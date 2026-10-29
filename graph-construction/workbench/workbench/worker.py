"""One isolated process per experiment, using the existing discovery pipeline."""
import sys
import time
import uuid
from pathlib import Path

from .common import PromptManager, load_windows, manifest, now, read, write
from .execution_progress import ExecutionProgress
from src.discover_predicates.execution_manager import process_all_windows
from src.discover_predicates.llm_client import PredicateDiscoveryLLM
from src.discover_predicates.storage import Storage


class WebFeedback:
    def __init__(self, root, progress=None):
        self.root = Path(root)
        self.lines = []
        self.progress = progress or (lambda *args, **kwargs: None)

    def __call__(self, prompt=''):
        if not self.lines:
            state = read(self.root / 'output/execution_state.json')
            pending = read(self.root / 'pending_feedback.json', {})
            submitted = read(self.root / 'feedback.json', {})
            reuse = (pending.get('batch') == state['current_batch_index'] and
                     pending.get('token') and pending.get('token') == submitted.get('token'))
            token = pending['token'] if reuse else uuid.uuid4().hex
            write(self.root / 'pending_feedback.json', {
                'token': token, 'batch': state['current_batch_index'], 'created_at': now()})
            if not reuse:
                (self.root / 'feedback.json').unlink(missing_ok=True)
            self.progress('human_wait', stage='human_review',
                          message=f'第 {state["current_batch_index"]} 批已完成，等待你在网页提交审核意见')
            while True:
                response = read(self.root / 'feedback.json')
                if response and response.get('token') == token:
                    self.lines = response['text'].splitlines() + ['END']
                    self.progress('feedback_received', stage='registry_revision',
                                  message='收到你的审核意见，继续处理')
                    break
                time.sleep(0.25)
        return self.lines.pop(0)


def run(root, transport=None):
    root = Path(root)
    progress = ExecutionProgress(root)
    progress('started', stage='prepare', message='开始运行，正在读取实验输入与配置')
    try:
        result = _run(root, transport, progress)
    except Exception as exc:
        progress('failed', message=f'运行失败：{exc}')
        raise
    progress('completed', stage='completed', message='实验已完成，结果已保存')
    return result


def _run(root, transport, progress):
    meta = read(root / 'experiment.json')
    output = root / 'output'
    if meta.get('kind') == 'preprocess':
        from .preprocessing import run as preprocess_run
        return preprocess_run(root, progress=progress)
    if meta.get('kind') == 'split':
        from .splitting import run as split_run
        return split_run(root, transport=transport, progress=progress)
    from .predicate_inputs import verify
    records = verify(root, meta)
    llm = PredicateDiscoveryLLM(output, model=meta['model'], base_url=meta['base_url'],
                               max_retries=meta['config']['max_llm_retries'], transport=transport,
                               progress=progress)
    process_all_windows(records=records, manifest=manifest(records, root / 'inputs'),
                        config=meta['config'], prompt_manager=PromptManager(root / 'prompts', output),
                        llm_client=llm, storage=Storage(output),
                        resume=(output / 'execution_state.json').is_file(),
                        input_func=WebFeedback(root, progress), progress=progress)
    for name in ('pending_feedback.json', 'feedback.json'):
        (root / name).unlink(missing_ok=True)


if __name__ == '__main__':
    root = Path(sys.argv[1])
    try:
        run(root)
    except Exception as exc:
        import os
        key = os.environ.get('DEEPSEEK_API_KEY', '')
        error = str(exc).replace(key, '[REDACTED]') if key else str(exc)
        write(root / 'lifecycle.json', {'status': 'failed', 'error': error, 'updated_at': now()})
        print(error, flush=True)
        raise SystemExit(1)
