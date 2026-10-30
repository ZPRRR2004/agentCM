"""Predicate experiments and reviews backed by a separate dataset catalog."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from urllib.parse import urlparse

from .datasets import CATALOG, DatasetCatalog, content_hash
from .trajectory_selection import trajectory_summary
from . import splitting, preprocessing
from .common import (DISCOVERY, PROMPTS, ROOT, PROMPT_FILES, PromptManager,
                     load_windows, now, read, text_field, write)
from . import predicate_inputs
from .prompt_upgrade import upgrade_node_contract
from src.trajectory_nodes import build_nodes, window_nodes


def definition_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Workspace:
    def __init__(self, data_dir, discovery=DISCOVERY, catalog_path=CATALOG):
        self.data = Path(data_dir).resolve()
        self.discovery = Path(discovery).resolve()
        self.data.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.processes = {}
        self.closing = False
        self.catalog = DatasetCatalog(catalog_path)
        if not (self.data / 'tasks.json').exists():
            tasks = []
            todo = ROOT.parents[1] / 'TODO.md'
            for line in todo.read_text(encoding='utf-8').splitlines() if todo.exists() else []:
                match = re.match(r'- \[([ x])\] (.*)', line)
                if match:
                    title = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', match[2])
                    tasks.append({'id': uuid.uuid4().hex[:12], 'title': title,
                                  'status': 'done' if match[1] == 'x' else 'backlog',
                                  'notes': '', 'experiment_id': '', 'updated_at': now()})
            write(self.data / 'tasks.json', tasks)
        upgrade_node_contract(self.data, self.source_prompts())

    def source_prompts(self):
        return {name: (PROMPTS / name).read_text(encoding='utf-8') for name in PROMPT_FILES}

    def datasets(self):
        return self.catalog.describe()

    def dataset_tasks(self, dataset):
        return self.catalog.tasks(dataset)

    def dataset_task(self, dataset, identity):
        return self.catalog.task(dataset, identity)

    def records(self, dataset):
        return self.catalog.records(dataset)

    def trajectories(self, dataset):
        return [trajectory_summary(r) for r in self.records(dataset)]

    def trajectory(self, dataset, identity):
        record = next((r for r in self.records(dataset) if r.trajectory_id == identity), None)
        if record is None:
            raise ValueError('找不到这条轨迹')
        return {'trajectory': record.data, 'id': record.trajectory_id, 'sha256': record.sha256,
                'nodes': build_nodes(record.trajectory_id, record.data['events'])}

    def paths(self, identity, *, include_deleted=False):
        if not isinstance(identity, str) or not re.fullmatch(r'[a-f0-9]{12}', identity):
            raise ValueError('实验标识无效')
        root = self.data / 'experiments' / identity
        if not (root / 'experiment.json').is_file():
            raise ValueError('找不到实验')
        if not include_deleted and (root / 'deleted.json').is_file():
            raise ValueError('实验已移至回收站，可在实验管理中恢复')
        return root, root / 'output'

    def experiment(self, identity, detail=False):
        root, output = self.paths(identity)
        state = read(output / 'execution_state.json', {})
        meta = read(root / 'experiment.json', {})
        registry = read(output / 'predicate_registry.json', [])
        kind = meta.get('kind', 'predicate')
        total = meta['trajectory_count'] if kind in ('split', 'preprocess') else meta['window_count']
        live = self.processes.get(identity)
        alive = live is not None and live.poll() is None
        pending = read(root / 'pending_feedback.json')
        status = state.get('status', 'draft')
        if alive:
            status = 'waiting' if pending and not (root / 'feedback.json').exists() else 'running'
        elif status != 'completed':
            status = read(root / 'lifecycle.json', {}).get('status', 'draft')
            if status in ('running', 'waiting'):
                status = 'interrupted'
        batches = []
        for f in sorted((output / 'batches').glob('*/batch_metadata.json')):
            b = read(f)
            batches.append({'index': b['batch_index'], 'end': b['end_window'],
                            'before': b.get('registry_size', 0),
                            'after': b.get('registry_size_after_feedback', b.get('registry_size', 0)),
                            'feedback': b.get('feedback_completed', False)})
        result = {**meta, 'id': identity, 'title': meta['title'],
                  'kind': kind, 'schema': {'split': 'split-experiment/v1', 'preprocess': 'preprocess-experiment/v1'}.get(kind, meta.get('predicate_schema_version', state.get('predicate_schema_version', 'predicate-definition/v1'))),
                  'status': status, 'completed': state.get('completed_trajectories' if kind in ('split', 'preprocess') else 'completed_windows', 0),
                  'total': total, 'registry_count': len(registry), 'batches': batches,
                  'stage': state.get('next_stage', ''), 'batch': state.get('current_batch_index', 1),
                  'dataset_id': meta['dataset_id'],
                  'pending': pending if alive else None,
                  'unit': '轨迹' if kind in ('split', 'preprocess') else '窗口',
                  'statistics': read(output / 'statistics.json', {}),
                  'produced_windows': state.get('window_count', 0)}
        if detail:
            reviews = read(self.data / 'reviews.json', {}).get(identity, {})
            for definition in registry:
                review = reviews.get(definition['name'])
                if review:
                    review['stale'] = review['definition_hash'] != definition_hash(definition)
            result.update(registry=registry, reviews=reviews, state=state)
            result['lifecycle'] = read(root / 'lifecycle.json', {})
            result['execution'] = read(root / 'execution.json', {})
            logfile = root / 'worker.log'
            if logfile.exists():
                with logfile.open('rb') as stream:
                    stream.seek(max(0, logfile.stat().st_size - 18000))
                    log = stream.read().decode('utf-8', errors='replace')
                key = self.settings(secret=True).get('api_key', '')
                result['log'] = log.replace(key, '[REDACTED]') if key else log
            if kind == 'preprocess':
                result['trajectories'] = preprocessing.list_trajectories(root)
                result['selection'] = read(root / 'selection.json') if meta.get('selection_policy') else None
                result['windows'] = []
            else:
                result['windows'] = self.window_list(result['dataset_id'], identity)
        return result

    def experiments(self):
        local = sorted((self.data / 'experiments').glob('*/experiment.json'),
                       key=lambda x: x.stat().st_mtime, reverse=True)
        ids = [p.parent.name for p in local if not (p.parent / 'deleted.json').is_file()]
        return [self.experiment(identity) for identity in ids]

    def _window_records(self, dataset, experiment=None):
        if not experiment:
            raise ValueError('请先选择切分实验的输出窗口')
        root, output = self.paths(experiment)
        meta = read(root / 'experiment.json')
        directory = output / 'windows' if meta.get('kind') == 'split' else root / 'inputs'
        records = load_windows(directory) if any(directory.glob('*.json')) else []
        return records, output

    def window_list(self, dataset=None, experiment=None):
        records, output = self._window_records(dataset, experiment)
        return [{'id': r.run_name, 'filename': r.path.name, 'trajectory_id': r.trajectory_id,
                 'window_id': r.window_id, 'index': r.window_index,
                 'title': r.data['user_query']['title'], 'events': len(r.data['core']['events']),
                 'status': read(output / 'runs' / r.run_name / 'metadata.json', {}).get('status', 'ready')
                 if output else 'ready'} for r in records]

    def window(self, dataset, window_id, experiment=None):
        records, output = self._window_records(dataset, experiment)
        record = next((r for r in records if r.run_name == window_id), None)
        if not record:
            raise ValueError('找不到这个窗口')
        result = {'window': record.data, 'sha256': record.sha256, 'stages': {}}
        root, _ = self.paths(experiment)
        meta = read(root / 'experiment.json')
        if meta.get('node_schema_version'):
            result['nodes'] = read(root / 'nodes' / (record.run_name + '.json'))
            result['node_source'] = 'snapshot'
        elif meta.get('kind') == 'split':
            result['nodes'] = window_nodes(record.data)
            result['node_source'] = 'preview'
        else:
            result['node_source'] = 'legacy_events'
        if output:
            for stage in ('discovery', 'comparison', 'review'):
                call = read(output / 'runs' / record.run_name / (stage + '_response.json'), {})
                if call:
                    result['stages'][stage] = call.get('parsed_response', call.get('parsed', {}))
            result['metadata'] = read(output / 'runs' / record.run_name / 'metadata.json', {})
        return result

    def evidence(self, identity, name):
        root, output = self.paths(identity)
        records = load_windows(root / 'inputs')
        found = []
        for record in records:
            directory = output / 'runs' / record.run_name
            stages = []
            for stage in ('discovery', 'comparison', 'review'):
                call = read(directory / (stage + '_response.json'), {})
                parsed = call.get('parsed_response', call.get('parsed', {}))
                if contains_name(parsed, name):
                    stages.append(stage)
            if stages:
                found.append({'id': record.run_name, 'title': record.data['user_query']['title'],
                              'window_id': record.window_id, 'stages': stages})
        return found

    def prompts(self):
        values = read(self.data / 'prompts.json')
        digest = hashlib.sha256(__import__('json').dumps(values, sort_keys=True).encode()).hexdigest()
        return {'files': values, 'hash': digest, 'source': self.source_prompts()}

    def settings(self, secret=False):
        values = {'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-flash'),
                  'base_url': os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                  'api_key': os.getenv('DEEPSEEK_API_KEY', '')}
        # Read module .env in isolation so settings never mutate the server environment.
        for path in [self.discovery / 'src/.env']:
            if path.is_file():
                for line in path.read_text(encoding='utf-8-sig').splitlines():
                    key, sep, val = line.strip().removeprefix('export ').partition('=')
                    mapping = {'DEEPSEEK_API_KEY': 'api_key', 'DEEPSEEK_MODEL': 'model',
                               'DEEPSEEK_BASE_URL': 'base_url'}
                    if sep and key.strip() in mapping and not os.getenv(key.strip()):
                        values[mapping[key.strip()]] = val.strip().strip('\"\'')
        values.update(read(self.data / 'settings.json', {}))
        return values if secret else values | {
            'key_configured': bool(values['api_key'].strip())}

    def save_settings(self, body):
        values = self.settings(secret=True)
        model = text_field(body, 'model', values['model'], 200)
        url = text_field(body, 'base_url', values['base_url'], 2000).rstrip('/')
        parsed = urlparse(url)
        if not model or parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('请填写模型名称和有效的 HTTP(S) API 地址')
        key = text_field(body, 'api_key', '', 4000)
        values.update(model=model, base_url=url)
        if key:
            values['api_key'] = key
        if body.get('clear_key'):
            values['api_key'] = ''
        write(self.data / 'settings.json', values, private=True)
        return self.settings()

    def create(self, body):
        kind = body.get('kind', 'predicate')
        if kind == 'preprocess':
            return preprocessing.create(self, body)
        if kind == 'split':
            return splitting.create(self, body)
        if kind != 'predicate':
            raise ValueError('实验类型无效')
        source_id = text_field(body, 'source_experiment_id', limit=100)
        if not source_id:
            raise ValueError('请先完成一次切分实验，再选择其结果')
        source = self.experiment(source_id)
        if source['kind'] != 'split' or source['status'] != 'completed':
            raise ValueError('请选择已完成的切分实验')
        dataset = source['dataset_id']
        if body.get('dataset_id', dataset) != dataset:
            raise ValueError('数据集与切分实验不匹配')
        _, source_output = self.paths(source_id)
        records = load_windows(source_output / 'windows')
        if content_hash(records) != source['statistics']['output_hash']:
            raise ValueError('切分产物发生变化，请重新运行切分实验')
        selected = body.get('trajectory_ids', [])
        if not isinstance(selected, list) or not all(isinstance(s, str) for s in selected):
            raise ValueError('任务选择无效')
        if selected:
            if set(selected) - {r.trajectory_id for r in records}:
                raise ValueError('任务不属于当前数据集')
            records = [r for r in records if r.trajectory_id in selected]
        if 'window_ids' in body:
            window_ids = body['window_ids']
            if not isinstance(window_ids, list) or not window_ids:
                raise ValueError('请至少选择一个窗口')
            if not all(isinstance(value, str) for value in window_ids) or len(set(window_ids)) != len(window_ids):
                raise ValueError('窗口选择无效')
            selected_windows = set(window_ids)
            if selected_windows - {r.run_name for r in records}:
                raise ValueError('窗口不属于所选的切分结果或任务')
            records = [r for r in records if r.run_name in selected_windows]
        limit = integer(body, 'window_limit', len(records), 1, len(records))
        batch = integer(body, 'batch_size', 10, 1, 1000)
        retries = integer(body, 'max_retries', 3, 0, 10)
        title = text_field(body, 'title', limit=200)
        if not title:
            raise ValueError('请填写实验名称')
        records = records[:limit]
        identity = uuid.uuid4().hex[:12]
        root = self.data / 'experiments' / identity
        settings = self.settings()
        prompts = self.prompts()
        PromptManager(PROMPTS, root / 'output').validate(prompts['files'])
        (root / 'inputs').mkdir(parents=True)
        for r in records:
            shutil.copyfile(r.path, root / 'inputs' / r.path.name)
        node_meta = predicate_inputs.snapshot(root, records)
        for name, content in prompts['files'].items():
            p = root / 'prompts' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
        write(root / 'experiment.json', {
            'id': identity, 'kind': 'predicate', 'title': title, 'question': text_field(body, 'question'),
            'dataset_id': dataset, 'dataset_name': source['dataset_name'],
            'source_experiment_id': source_id, 'source_title': source['title'],
            'source_output_hash': source['statistics']['output_hash'],
            'split_config': source['config'], 'input_hash': content_hash(records),
            'trajectory_ids': sorted({r.trajectory_id for r in records}),
            'window_ids': [r.run_name for r in records],
            'window_count': len(records), 'created_at': now(),
            **node_meta,
            'prompt_hash': prompts['hash'], 'model': settings['model'], 'base_url': settings['base_url'],
            'config': {'human_feedback_interval': batch, 'feedback_mode': 'registry_feedback',
                       'max_llm_retries': retries}})
        write(root / 'lifecycle.json', {'status': 'draft', 'updated_at': now()})
        return self.experiment(identity, detail=True)

    def start(self, identity):
        root, output = self.paths(identity)
        old = self.processes.get(identity)
        if old is not None and old.poll() is None:
            raise ValueError('实验已经在运行')
        if read(output / 'execution_state.json', {}).get('status') == 'completed':
            raise ValueError('实验已完成；可新建实验进行对比')
        settings = self.settings(secret=True)
        meta = read(root / 'experiment.json')
        if meta.get('kind', 'predicate') == 'predicate':
            predicate_inputs.verify(root, meta)
        if meta.get('kind') == 'split' and (meta.get('input_state') == 'awaiting_input' or not meta['trajectory_count']):
            raise ValueError('请先接入执行轨迹，再开始切分')
        needs_model = meta.get('kind', 'predicate') == 'predicate' or (meta.get('kind') == 'split' and splitting.uses_model(meta['config']))
        if needs_model and not settings['api_key'].strip():
            raise ValueError('请先在模型设置中填写 API Key')
        env = dict(os.environ, DEEPSEEK_API_KEY=settings['api_key'],
                   DEEPSEEK_MODEL=meta['model'], DEEPSEEK_BASE_URL=meta['base_url'],
                   PYTHONUNBUFFERED='1', PYTHONUTF8='1')
        pending = read(root / 'pending_feedback.json', {})
        submitted = read(root / 'feedback.json', {})
        if not pending or pending.get('token') != submitted.get('token'):
            for name in ('pending_feedback.json', 'feedback.json'):
                (root / name).unlink(missing_ok=True)
        if output.exists() and any(output.iterdir()) and not (output / 'execution_state.json').exists():
            archive = root / 'initialization_attempts' / uuid.uuid4().hex
            archive.parent.mkdir(exist_ok=True)
            output.rename(archive)
        write(root / 'lifecycle.json', {'status': 'running', 'started_at': now()})
        with (root / 'worker.log').open('ab') as log:
            process = subprocess.Popen([sys.executable, '-m', 'workbench.worker', str(root)],
                                       cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       start_new_session=True)
        self.processes[identity] = process
        threading.Thread(target=self._monitor, args=(identity, root, process), daemon=True).start()
        return self.experiment(identity)

    def _monitor(self, identity, root, process):
        code = process.wait()
        with self.lock:
            if self.processes.get(identity) is not process:
                return
            lifecycle = read(root / 'lifecycle.json', {})
            if lifecycle.get('status') == 'running':
                state = read(root / 'output/execution_state.json', {})
                write(root / 'lifecycle.json', {'status': 'completed' if state.get('status') == 'completed'
                                              else 'failed', 'exit_code': code, 'updated_at': now()})

    def stop(self, identity):
        root, _ = self.paths(identity)
        process = self.processes.get(identity)
        if process is None or process.poll() is not None:
            raise ValueError('实验当前没有运行中的进程')
        write(root / 'lifecycle.json', {'status': 'stopped', 'updated_at': now()})
        process.terminate()
        process.wait(timeout=10)
        return self.experiment(identity)

    def feedback(self, identity, body):
        root, _ = self.paths(identity)
        process = self.processes.get(identity)
        pending = read(root / 'pending_feedback.json')
        if process is None or process.poll() is not None or not pending:
            raise ValueError('这个实验当前没有等待反馈的批次')
        if body.get('token') != pending['token'] or (root / 'feedback.json').exists():
            raise ValueError('此批次已提交或状态已变化，请刷新')
        feedback = text_field(body, 'feedback', limit=50000)
        if any(line.strip() == 'END' for line in feedback.splitlines()):
            raise ValueError('反馈正文中请避免使用独占一行的 END')
        payload = {'token': pending['token'], 'text': feedback, 'submitted_at': now()}
        write(root / 'feedback_submissions' / (pending['token'] + '.json'), payload)
        write(root / 'feedback.json', payload)
        return {'ok': True}

    def review(self, identity, body):
        data = self.experiment(identity, detail=True)
        name = text_field(body, 'name', limit=500)
        if name not in {x['name'] for x in data['registry']}:
            raise ValueError('定义不在当前 Registry 中')
        decision = body.get('decision')
        if decision not in ('keep', 'revise', 'merge', 'delete', 'pending'):
            raise ValueError('审核结论无效')
        reviews = read(self.data / 'reviews.json', {})
        previous = reviews.get(identity, {}).get(name)
        if previous:
            write(self.data / 'review_history' / identity / (uuid.uuid4().hex + '.json'),
                  {'name': name, **previous})
        reviews.setdefault(identity, {})[name] = {
            'decision': decision, 'notes': text_field(body, 'notes'), 'updated_at': now(),
            'definition_hash': definition_hash(next(x for x in data['registry'] if x['name'] == name)),
            'stale': False}
        write(self.data / 'reviews.json', reviews)
        return reviews[identity][name]

    def batch(self, identity, index):
        _, output = self.paths(identity)
        if type(index) is not int or not 1 <= index <= 100000:
            raise ValueError('批次编号无效')
        directory = output / 'batches' / f'batch_{index:04d}'
        if not directory.is_dir():
            raise ValueError('找不到批次')
        feedback_path = directory / 'human_feedback.txt'
        packet_path = directory / 'review_packet.md'
        return {'metadata': read(directory / 'batch_metadata.json', {}),
                'feedback': feedback_path.read_text(encoding='utf-8') if feedback_path.exists() else '',
                'packet': packet_path.read_text(encoding='utf-8') if packet_path.exists() else '',
                'plan': read(directory / 'registry_revision_plan.json', {})}

    def task(self, body):
        tasks = read(self.data / 'tasks.json', [])
        identity = body.get('id')
        old = next((t for t in tasks if t['id'] == identity), None)
        if identity and not old:
            raise ValueError('找不到任务')
        if body.get('delete'):
            tasks.remove(old)
        else:
            title = text_field(body, 'title', (old or {}).get('title', ''), 1000)
            status = body.get('status', (old or {}).get('status', 'backlog'))
            if not title or status not in ('backlog', 'doing', 'review', 'done'):
                raise ValueError('请填写任务名称并选择有效状态')
            experiment = text_field(body, 'experiment_id', (old or {}).get('experiment_id', ''), 100)
            if experiment:
                self.paths(experiment, include_deleted=experiment == (old or {}).get('experiment_id'))
            item = {'id': identity or uuid.uuid4().hex[:12], 'title': title, 'status': status,
                    'notes': text_field(body, 'notes', (old or {}).get('notes', '')),
                    'experiment_id': experiment, 'updated_at': now()}
            if old:
                tasks[tasks.index(old)] = item
            else:
                tasks.insert(0, item)
        write(self.data / 'tasks.json', tasks)
        return tasks

    def shutdown(self):
        for identity, process in list(self.processes.items()):
            if process.poll() is None:
                self.stop(identity)


def contains_name(value, name):
    if isinstance(value, dict):
        return any((k in ('name', 'candidate_name', 'matched_existing_name', 'original_name') and v == name)
                   or contains_name(v, name) for k, v in value.items())
    if isinstance(value, list):
        return any(contains_name(v, name) for v in value)
    return False


def integer(body, key, default, low, high):
    value = body.get(key, default)
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{key} 必须是 {low}–{high} 范围内的整数')
    return value
