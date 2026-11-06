"""Snapshot-based predicate embedding and independent clustering by arity.

New experiments abstract each finished cluster through the existing chat client.
Source registries remain unchanged. Numerical imports stay inside the worker.
"""
import copy
import hashlib
import json
import math
import os
import re
import tempfile
import time
import uuid
import warnings
from collections import Counter
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .common import _windows_io, now, read, text_field, write
from src.discover_predicates.validator import validate_registry


SCHEMA = 'predicate-clustering/v1'
INPUT_TEMPLATE = 'predicate-embedding-input/v1'
FIELD_INPUT_TEMPLATE = 'predicate-embedding-fields/v1'
FIELD_CACHE_SCHEMA = 'predicate-field-embedding-cache/v1'
FIELD_ORDER = ('definition', 'parameters', 'assertion', 'exclusion')
DEFAULT_FIELD_WEIGHTS = {'definition': 0.5, 'parameters': 0.3,
                         'assertion': 0.1, 'exclusion': 0.1}
DEFAULT_BATCH_SIZE = 10
DEFAULT_MAX_RETRIES = 3
MAX_REQUEST_BYTES = 2_000_000  # Same limit as the workbench HTTP API.
ARITY_NAMES = {1: 'Unary', 2: 'Binary', 3: 'Ternary', 4: 'Quaternary'}


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Embedding API 地址发生重定向，请在模型设置中直接填写最终地址')


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def arity_label(arity):
    return f'{ARITY_NAMES.get(arity, str(arity) + "-ary")}（{arity} 元）'


def parse_registry(value):
    # Only an array or an unambiguous, single-key envelope is a registry.
    if isinstance(value, dict) and set(value) in ({'predicates'}, {'registry'}):
        value = next(iter(value.values()))
    validate_registry(value)
    if not value:
        raise ValueError('Predicate Registry 不能为空')
    return copy.deepcopy(value)


def arity_counts(registry):
    counts = Counter(len(p['parameters']) for p in registry)
    return {str(k): counts[k] for k in sorted(counts)}


def embedding_text(predicate):
    parameters = '\n'.join(
        f'{i}. {parameter["type"]}: {parameter["description"]}'
        for i, parameter in enumerate(predicate['parameters'], 1))
    return f'Definition: {predicate["definition"]}\n\nParameters:\n{parameters}'


def embedding_field_texts(predicate):
    parameters = '\n'.join(f'{i}. {p["type"]}: {p["description"]}'
                           for i, p in enumerate(predicate['parameters'], 1))
    assertion = '\n'.join(f'{i}. {text}' for i, text in
                          enumerate(predicate['assertion_conditions'], 1))
    exclusion = '\n'.join(f'{i}. {text}' for i, text in
                          enumerate(predicate['exclusion_conditions'], 1))
    return {'definition': 'Definition:\n' + predicate['definition'],
            'parameters': 'Ordered Parameters:\n' + parameters,
            'assertion': 'Assertion Conditions:\n' + assertion,
            'exclusion': 'Exclusion Conditions:\n' + exclusion if exclusion else None}


def validate_field_weights(weights):
    if not isinstance(weights, dict) or set(weights) != set(FIELD_ORDER):
        raise ValueError('必须配置 Definition、Parameters、Assertion、Exclusion 四个字段权重')
    for field in FIELD_ORDER:
        weight = weights[field]
        if type(weight) not in (int, float) or not 0 <= weight <= 1 or not math.isfinite(weight):
            raise ValueError(f'{field} 权重必须是 0–1 之间的有限非负数')
    if not math.isclose(math.fsum(weights.values()), 1, rel_tol=0, abs_tol=1e-9):
        raise ValueError('四个字段权重之和必须等于 1（100%）')
    return {field: float(weights[field]) for field in FIELD_ORDER}


def validate_embedding_representation(value):
    if not isinstance(value, dict):
        raise ValueError('Embedding 表示配置必须是对象')
    mode = value.get('mode')
    if mode == 'single_text':
        result = {'mode': mode, 'version': 'single-text/v1'}
    elif mode == 'fieldwise_concat':
        result = {'mode': mode, 'version': 'fieldwise-concat/v1',
                  'fields': list(FIELD_ORDER), 'weights': validate_field_weights(value.get('weights')),
                  'normalization': 'l2_per_field_then_l2_final', 'weight_application': 'sqrt',
                  'empty_field_policy': 'zero_block_keep_weights'}
    else:
        raise ValueError('Embedding 表示方式必须是 single_text 或 fieldwise_concat')
    if set(value) - set(result):
        raise ValueError('Embedding 表示配置包含不支持的字段')
    if any(value[key] != result[key] for key in value if key != 'weights'):
        raise ValueError('Embedding 表示版本、字段顺序或归一化策略不受支持')
    return result


def representation_config(config):
    # Missing strategy is the original contract. Do not insert it into old snapshots.
    if 'embedding_representation' not in config:
        return {'mode': 'single_text', 'version': 'single-text/v1'}
    return validate_embedding_representation(config['embedding_representation'])


def validate_effective_fields(registry, representation):
    if representation['mode'] != 'fieldwise_concat':
        return
    for index, predicate in enumerate(registry):
        texts = embedding_field_texts(predicate)
        if not any(texts[field] is not None and representation['weights'][field] > 0
                   for field in FIELD_ORDER):
            raise ValueError(f'Predicate {index + 1}（{predicate["name"]}）所有有效字段权重均为零，'
                             '无法构造非零拼接向量；请调整权重后新建实验')


def base_url(value):
    if not isinstance(value, str) or len(value) > 2000:
        raise ValueError('请填写有效的 Embedding API Base URL')
    value = value.strip().rstrip('/')
    parsed = urlparse(value)
    try:
        parsed.port
    except ValueError:
        raise ValueError('Embedding API 地址端口无效') from None
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname or
            parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('Embedding API 地址必须是无凭据、查询参数的 HTTP(S) 地址')
    path = parsed.path.rstrip('/')
    if not path or path.endswith('/compatible-mode'):
        path += '/v1'
    return urlunparse(parsed._replace(path=path))


def positive_integer(value, label, low=1, high=None):
    if type(value) is not int or value < low or (high is not None and value > high):
        raise ValueError(f'{label} 必须是 {low}' + (f'–{high}' if high is not None else ' 以上') + '的整数')
    return value


def embedding_config(settings, representation=None):
    model = text_field(settings, 'embedding_model', 'qwen3.7-text-embedding', 200)
    if not model:
        raise ValueError('请在模型设置中填写 Embedding 模型名称')
    dimensions = settings.get('embedding_dimensions')
    if dimensions is not None:
        positive_integer(dimensions, 'Embedding 输出维度')
    return {'model': model, 'base_url': base_url(settings.get('embedding_base_url', '')),
            'dimensions': dimensions, 'input_template': FIELD_INPUT_TEMPLATE
            if representation and representation['mode'] == 'fieldwise_concat' else INPUT_TEMPLATE,
            'batch_size': DEFAULT_BATCH_SIZE, 'max_retries': DEFAULT_MAX_RETRIES,
            'timeout_seconds': 120}


def validate_config(value, counts):
    if not isinstance(value, dict):
        raise ValueError('请填写聚类配置')
    algorithm = value.get('algorithm', 'agglomerative')
    if algorithm not in ('agglomerative', 'kmeans'):
        raise ValueError('聚类算法必须是 agglomerative 或 kmeans')
    targets = value.get('clusters_by_arity')
    if not isinstance(targets, dict) or set(targets) != set(counts):
        raise ValueError('各元数组的目标类数必须与 Registry 的非空元数组完全对应')
    for arity, count in counts.items():
        positive_integer(targets[arity], f'{arity} 元目标类数', 1, count)
    total = positive_integer(value.get('target_clusters'), '目标总类数',
                             len(counts), sum(counts.values()))
    if total != sum(targets.values()):
        raise ValueError('各元数组目标类数之和必须等于目标总类数')
    result = {'algorithm': algorithm, 'target_clusters': total,
              'clusters_by_arity': dict(targets)}
    if algorithm == 'agglomerative':
        linkage = value.get('linkage', 'average')
        if linkage not in ('average', 'complete'):
            raise ValueError('Cosine 聚类仅支持 average / complete linkage')
        result.update(metric='cosine', linkage=linkage)
    else:
        result.update(metric='euclidean',
                      n_init=positive_integer(value.get('n_init', 20), 'n_init', 1, 1000),
                      random_state=positive_integer(value.get('random_state', 42),
                                                    'random_state', 0, 2**32 - 1))
    if value.get('metric', result['metric']) != result['metric']:
        raise ValueError('聚类算法与距离配置不匹配')
    if 'embedding_representation' in value:
        result['embedding_representation'] = validate_embedding_representation(value['embedding_representation'])
    return result


def source_registry(workspace, body):
    mode = body.get('source_type')
    if mode == 'experiment':
        identity = text_field(body, 'source_experiment_id', limit=100)
        source = workspace.experiment(identity)
        if source['kind'] != 'predicate' or source['status'] != 'completed':
            raise ValueError('请选择已完成的谓词发现实验')
        _, output = workspace.paths(identity)
        registry = parse_registry(read(output / 'predicate_registry.json'))
        origin = {'type': 'experiment', 'experiment_id': identity,
                  'title': source['title'], 'dataset_id': source.get('dataset_id'),
                  'dataset_name': source.get('dataset_name', '')}
    elif mode == 'upload':
        value = body.get('registry')
        if len(json.dumps(value, ensure_ascii=False).encode('utf-8')) > MAX_REQUEST_BYTES:
            raise ValueError('Registry JSON 超出工作台 2 MB 请求限制')
        registry = parse_registry(value)
        filename = text_field(body, 'filename', 'predicate_registry.json', 500)
        filename = re.split(r'[/\\]', filename)[-1] or 'predicate_registry.json'
        origin = {'type': 'upload', 'filename': filename, 'title': filename,
                  'dataset_id': None, 'dataset_name': '本地 JSON'}
    else:
        raise ValueError('请选择已有谓词实验或上传本地 Registry JSON')
    return registry, origin


def preview(workspace, body):
    registry, source = source_registry(workspace, body)
    return {'source': source, 'predicate_count': len(registry),
            'arity_counts': arity_counts(registry), 'input_hash': digest(registry),
            'validation': 'predicate-definition/v2 校验通过',
            'empty_exclusion_count': sum(not p['exclusion_conditions'] for p in registry),
            'summary': [{'name': p['name'], 'definition': p['definition']}
                        for p in registry[:3]]}


def snapshot_hash(meta):
    fields = {key: meta[key] for key in ('input_hash', 'embedding', 'config')}
    if 'abstraction' in meta:
        fields['abstraction'] = meta['abstraction']
    return digest(fields)


def create(workspace, body):
    title = text_field(body, 'title', limit=200)
    if not title:
        raise ValueError('请填写实验名称')
    question = text_field(body, 'question')
    registry, source = source_registry(workspace, body)
    input_hash = digest(registry)
    if body.get('input_hash') and body['input_hash'] != input_hash:
        raise ValueError('来源 Registry 已变化，请重新读取并配置类数')
    counts = arity_counts(registry)
    requested_config = copy.deepcopy(body.get('config'))
    if not isinstance(requested_config, dict):
        raise ValueError('请填写聚类配置')
    requested_config.setdefault('embedding_representation', {
        'mode': 'fieldwise_concat', 'weights': dict(DEFAULT_FIELD_WEIGHTS)})
    config = validate_config(requested_config, counts)
    representation = representation_config(config)
    validate_effective_fields(registry, representation)
    settings = workspace.settings(secret=True)
    embedding = embedding_config(settings, representation)
    identity = uuid.uuid4().hex[:12]
    root = workspace.data / 'experiments' / identity
    from .predicate_abstraction import snapshot as abstraction_snapshot
    abstraction = abstraction_snapshot(settings, root)
    meta = {'id': identity, 'kind': 'clustering', 'schema': SCHEMA,
            'title': title, 'question': question, 'created_at': now(),
            'dataset_id': source['dataset_id'], 'dataset_name': source['dataset_name'],
            'source': source, 'source_title': source['title'],
            'source_experiment_id': source.get('experiment_id'),
            'input_hash': input_hash, 'predicate_count': len(registry),
            'arity_counts': counts, 'embedding': embedding, 'config': config,
            'abstraction': abstraction,
            'model': embedding['model'], 'base_url': embedding['base_url']}
    meta['snapshot_hash'] = snapshot_hash(meta)
    write(root / 'inputs/predicate_registry.json', registry)
    write(root / 'experiment.json', meta)
    write(root / 'lifecycle.json', {'status': 'draft', 'updated_at': now()})
    return workspace.experiment(identity, detail=True)


def verify_inputs(root, meta):
    registry = parse_registry(read(root / 'inputs/predicate_registry.json'))
    if meta.get('schema') != SCHEMA or digest(registry) != meta['input_hash']:
        raise ValueError('聚类输入快照或格式版本发生变化，拒绝运行')
    counts = arity_counts(registry)
    if counts != meta['arity_counts'] or len(registry) != meta['predicate_count']:
        raise ValueError('聚类输入的谓词数量或元数分布与快照不一致')
    if validate_config(meta['config'], counts) != meta['config']:
        raise ValueError('聚类配置快照无效')
    representation = representation_config(meta['config'])
    validate_effective_fields(registry, representation)
    embedding = meta['embedding']
    expected = embedding_config({
        'embedding_model': embedding['model'], 'embedding_base_url': embedding['base_url'],
        'embedding_dimensions': embedding['dimensions']}, representation)
    if embedding != expected or snapshot_hash(meta) != meta['snapshot_hash']:
        raise ValueError('Embedding 或聚类配置快照发生变化，拒绝复用缓存')
    if 'abstraction' in meta:
        from .predicate_abstraction import load_snapshot
        load_snapshot(root, meta['abstraction'])
    return registry


def _vectors(values, count, dimensions=None, *, normalized=False):
    import numpy as np
    if (not isinstance(values, list) or len(values) != count or
            any(not isinstance(v, list) or not v or any(
                type(x) not in (int, float) for x in v) for v in values)):
        raise ValueError('Embedding 返回的向量数量或数值格式无效')
    lengths = {len(v) for v in values}
    if len(lengths) != 1 or (dimensions is not None and lengths != {dimensions}):
        raise ValueError('Embedding 返回维度不一致，或与配置/已有批次维度不匹配')
    try:
        matrix = np.asarray(values, dtype=np.float64)
    except (OverflowError, TypeError, ValueError):
        raise ValueError('Embedding 向量包含无法处理的数值') from None
    if not np.isfinite(matrix).all():
        raise ValueError('Embedding 向量包含 NaN 或 Infinity')
    # Scale before the norm to avoid overflow/underflow on finite API values.
    scales = np.max(np.abs(matrix), axis=1)
    if np.any(scales == 0):
        raise ValueError('Embedding 返回零范数向量')
    scaled = matrix / scales[:, None]
    norms = np.linalg.norm(scaled, axis=1)
    if normalized:
        if not np.allclose(scales * norms, 1, rtol=0, atol=1e-8):
            raise ValueError('Embedding 缓存向量未通过 L2 归一化校验')
        return matrix
    return scaled / norms[:, None]


def _api_error(error):
    """Classify provider errors without persisting an echoed request or secret."""
    message = {401: '鉴权失败，请检查 Embedding API Key',
               403: '无访问权限，请检查 Embedding API Key 和工作空间',
               404: '服务或模型不存在，请检查冻结的 Base URL 和模型名称',
               400: '请求无效，请检查模型、输入长度及 dimensions 支持情况',
               422: '参数无效，请检查模型与 dimensions 支持情况'}.get(error.code, '请求被拒绝')
    if error.code in (400, 404, 422):
        try:
            detail = json.loads(error.read(65536))
            detail = detail.get('error', detail) if isinstance(detail, dict) else {}
            text = ' '.join(str(detail.get(k, '')) for k in ('code', 'message')).lower()
            if 'model' in text and any(word in text for word in ('not exist', 'not found', 'notfound', 'invalid model', 'not supported')):
                message = 'Embedding 模型不存在、未开通或不受该地址支持，请核对冻结的模型与服务地址'
            elif 'dimension' in text:
                message = 'Embedding 输出维度不受服务或模型支持，请在模型设置中调整维度并新建实验'
            elif any(word in text for word in ('api key', 'apikey', 'api_key', 'invalidkey')):
                message = '鉴权失败，请检查 Embedding API Key 和工作空间'
        except (ValueError, AttributeError, OSError):
            pass
    return f'Embedding API HTTP {error.code}：{message}'


def _request_embeddings(texts, config, key, progress):
    payload = {'model': config['model'], 'input': texts, 'encoding_format': 'float'}
    if config['dimensions'] is not None:
        payload['dimensions'] = config['dimensions']
    endpoint = config['base_url']
    if not endpoint.endswith('/embeddings'):
        endpoint += '/embeddings'
    request = Request(endpoint,
                      data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                      headers={'Authorization': 'Bearer ' + key,
                               'Content-Type': 'application/json'})
    for attempt in range(config['max_retries'] + 1):
        progress('embedding_request', stage='embedding_api',
                 message=f'调用 Embedding API（第 {attempt + 1}/{config["max_retries"] + 1} 次尝试）')
        delay = min(2**attempt, 8)
        try:
            with build_opener(_NoRedirect()).open(request, timeout=config['timeout_seconds']) as response:
                raw = response.read(64_000_001)
            if len(raw) > 64_000_000:
                raise ValueError('Embedding API 响应超过 64 MB，无法处理')
            try:
                value = json.loads(raw)
            except (ValueError, UnicodeError) as from_error:
                raise ValueError('Embedding API 返回了无效 JSON') from from_error
            data = value.get('data') if isinstance(value, dict) else None
            if not isinstance(data, list) or len(data) != len(texts):
                raise ValueError('Embedding API 返回的向量数量不匹配')
            ordered = [None] * len(texts)
            seen = set()
            for item in data:
                index = item.get('index') if isinstance(item, dict) else None
                if type(index) is not int or not 0 <= index < len(texts) or index in seen:
                    raise ValueError('Embedding API 返回的 index 缺失、重复或越界')
                seen.add(index)
                ordered[index] = item.get('embedding')
            return _vectors(ordered, len(texts), config['dimensions'])
        except HTTPError as exc:
            status = exc.code
            retry = status in (408, 409, 429) or 500 <= status < 600
            if not retry:
                message = _api_error(exc)
                exc.close()
                raise ValueError(message) from None
            error = f'Embedding API HTTP {status}，限流或服务暂时不可用'
            try:
                retry_after = float(exc.headers.get('Retry-After', '0'))
                if math.isfinite(retry_after):
                    delay = max(delay, min(30, retry_after))
            except (ValueError, TypeError):
                pass
            exc.close()
        except (URLError, TimeoutError, OSError, HTTPException):
            error = 'Embedding API 网络连接失败或超时，请检查服务地址和网络'
        if attempt == config['max_retries']:
            raise ValueError(error + '；有限次数重试已用尽') from None
        progress('embedding_retry', stage='embedding_api', message=error + f'，{delay:g} 秒后重试')
        time.sleep(delay)


def _save_array(path, value):
    import numpy as np
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            np.save(stream, value, allow_pickle=False)
        _windows_io(lambda: os.replace(temporary, path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _single_text_embedding_matrix(root, registry, meta, state, checkpoint, progress):
    import numpy as np
    config = meta['embedding']
    checkpoint('embedding_inputs')
    texts = [embedding_text(p) for p in registry]
    records = [{'index': i, 'predicate_name': p['name'], 'arity': len(p['parameters']),
                'text': text, 'text_hash': digest(text)}
               for i, (p, text) in enumerate(zip(registry, texts))]
    write(root / 'output/embedding_texts.json', {
        'schema': INPUT_TEMPLATE, 'input_hash': meta['input_hash'], 'items': records})
    progress('embedding_inputs', stage='embedding_inputs',
             message=f'已按统一模板构造 {len(texts)} 段 Embedding 文本')
    matrices = []
    dimensions = config['dimensions']
    key = os.environ.get('AGENTCM_EMBEDDING_API_KEY', '').strip()
    for start in range(0, len(texts), config['batch_size']):
        checkpoint('embedding_api')
        end = min(len(texts), start + config['batch_size'])
        binding = {'embedding': config, 'text_hashes': [r['text_hash'] for r in records[start:end]]}
        cache_key = digest(binding)
        path = root / 'output/embedding_batches' / f'{start:06d}-{cache_key[:16]}.json'
        cached = read(path)
        progress('embedding_batch', stage='embedding_api', embedding_start=start,
                 embedding_end=end, embedding_total=len(texts),
                 message=f'已生成 {start} / {len(texts)} 个 Embedding')
        if cached is not None:
            if (cached.get('cache_key') != cache_key or cached.get('binding') != binding or
                    cached.get('indices') != list(range(start, end)) or
                    digest(cached.get('vectors')) != cached.get('vectors_hash')):
                raise ValueError('Embedding 批次缓存校验失败，拒绝错误复用')
            matrix = _vectors(cached['vectors'], end - start, dimensions, normalized=True)
        else:
            if not key:
                raise ValueError('请在模型设置中填写 Embedding API Key')
            matrix = _request_embeddings(texts[start:end], config, key, progress)
            if dimensions is not None and matrix.shape[1] != dimensions:
                raise ValueError('Embedding 返回维度与已保存批次不一致')
            checkpoint('embedding_save')
            progress('embedding_save', stage='embedding_save', message=f'保存第 {start + 1}–{end} 个 Embedding')
            vectors = matrix.tolist()
            write(path, {'cache_key': cache_key, 'binding': binding,
                         'indices': list(range(start, end)), 'vectors_hash': digest(vectors),
                         'vectors': vectors})
        dimensions = matrix.shape[1]
        matrices.append(matrix)
        state.update(completed_embeddings=end, completed_predicates=end, dimensions=dimensions)
        checkpoint('embedding_api')
        progress('embedding_batch_done', stage='embedding_api', completed=end,
                 message=f'已生成 {end} / {len(texts)} 个 Embedding' + ('（复用已保存批次）' if cached else ''))
    matrix = np.vstack(matrices)
    checkpoint('embedding_save')
    progress('embedding_save', stage='embedding_save', message='保存归一化向量与稳定索引')
    _save_array(root / 'output/embeddings.npy', matrix)
    write(root / 'output/embedding_index.json', {
        'schema': 'predicate-embedding-index/v1', 'embedding': config,
        'input_hash': meta['input_hash'], 'dimensions': dimensions,
        'vectors_hash': digest(matrix.tolist()),
        'items': [{k: v for k, v in item.items() if k != 'text'} for item in records]})
    return matrix


def build_weighted_concat(field_vectors, weights, field_presence):
    """Keep the four configured weights; missing/inactive blocks stay zero."""
    import numpy as np
    weights = validate_field_weights(weights)
    if set(field_vectors) != set(FIELD_ORDER) or set(field_presence) != set(FIELD_ORDER):
        raise ValueError('四字段向量及存在性掩码不完整')
    shape = np.asarray(field_vectors['definition']).shape
    if len(shape) != 2 or min(shape) < 1:
        raise ValueError('字段向量必须是非空的 [Predicate 数量, 单字段维度] 矩阵')
    n, d = shape
    parts = []
    for field in FIELD_ORDER:
        vectors = np.asarray(field_vectors[field], dtype=np.float64)
        present = np.asarray(field_presence[field], dtype=bool)
        if vectors.shape != (n, d) or present.shape != (n,):
            raise ValueError(f'{field} 字段向量维度或存在性标记不一致')
        if not np.isfinite(vectors).all():
            raise ValueError(f'{field} 字段向量包含非有限值')
        block = np.zeros((n, d), dtype=np.float64)
        if weights[field] > 0 and np.any(present):
            active = _vectors(vectors[present].tolist(), int(present.sum()), d, normalized=True)
            block[present] = math.sqrt(weights[field]) * active
        parts.append(block)
    raw = np.concatenate(parts, axis=1)
    if np.any(np.max(np.abs(raw), axis=1) == 0):
        raise ValueError('Predicate 的所有有效字段权重均为零，无法归一化全零拼接向量')
    # The same stable L2 routine now normalizes each complete 4d concatenation.
    # No per-predicate reweighting and no change to the frozen weights.
    return _vectors(raw.tolist(), n, len(FIELD_ORDER) * d)


def field_cache_binding(config, field, text_hash):
    # Weight, algorithm, quotas, retries and API key do not identify an embedding.
    return {'model': config['model'], 'base_url': config['base_url'],
            'dimensions': config['dimensions'], 'field': field,
            'template_version': FIELD_INPUT_TEMPLATE, 'text_hash': text_hash}


def load_cached_field_embedding(path, binding, dimensions):
    import numpy as np
    try:
        value = read(path)
        if value is None:
            return None
        if (not isinstance(value, dict) or value.get('schema') != FIELD_CACHE_SCHEMA or
                value.get('cache_key') != digest(binding) or value.get('binding') != binding or
                digest(value.get('vector')) != value.get('vector_hash')):
            raise ValueError('身份或向量 Hash 不匹配')
        matrix = _vectors([value['vector']], 1, dimensions, normalized=True)
        if type(value.get('dimensions')) is not int or value['dimensions'] != matrix.shape[1]:
            raise ValueError('缓存记录维度无效')
        return np.asarray(matrix[0], dtype=np.float64)
    except (ValueError, KeyError, TypeError, OverflowError) as exc:
        raise ValueError(f'{binding["field"]} 字段缓存校验失败：{exc}') from None


def save_cached_field_embedding(path, binding, vector):
    # Each key has its own atomic JSON document. Concurrent writers never expose
    # partial data; read back the published value before freezing a local copy.
    if not path.is_file():
        values = vector.tolist()
        write(path, {'schema': FIELD_CACHE_SCHEMA, 'cache_key': digest(binding),
                     'binding': binding, 'dimensions': len(values),
                     'vector': values, 'vector_hash': digest(values)})
    return load_cached_field_embedding(path, binding, len(vector))


def _field_embedding_matrix(root, registry, meta, state, checkpoint, progress):
    import numpy as np
    config = meta['embedding']
    representation = representation_config(meta['config'])
    weights = representation['weights']
    n = len(registry)
    records, aliases = [], {}
    checkpoint('embedding_field_inputs')
    for index, predicate in enumerate(registry):
        fields = {}
        texts = embedding_field_texts(predicate)
        for field in FIELD_ORDER:
            text = texts[field]
            present = text is not None
            text_hash = digest(text) if present else None
            active = present and weights[field] > 0
            binding = field_cache_binding(config, field, text_hash) if present else None
            cache_key = digest(binding) if binding else None
            fields[field] = {'text': text, 'text_hash': text_hash, 'present': present,
                             'active': active, 'cache_key': cache_key}
            if active:
                aliases.setdefault(cache_key, {'binding': binding, 'text': text, 'members': []})[
                    'members'].append((index, field))
        records.append({'index': index, 'predicate_name': predicate['name'],
                        'arity': len(predicate['parameters']), 'fields': fields})
    write(root / 'output/embedding_texts.json', {
        'schema': FIELD_INPUT_TEMPLATE, 'input_hash': meta['input_hash'], 'items': records})
    total_vectors = sum(len(item['members']) for item in aliases.values())
    required = [sum(record['fields'][f]['active'] for f in FIELD_ORDER) for record in records]
    if any(count == 0 for count in required):
        raise ValueError('Predicate 的所有有效字段权重均为零，无法构造拼接向量')
    state.update(completed_embedding_vectors=0, total_embedding_vectors=total_vectors,
                 completed_predicates=0, total_predicates=n, current_embedding_field=None,
                 completed_embeddings=0)
    dimensions = config['dimensions']
    field_vectors = {}
    completed = [0] * n
    completed_keys = set()
    local = root / 'output/embedding_batches/fieldwise-v1'
    shared = root.parents[1] / 'embedding_cache/predicate-fields-v1'

    def report(event, stage, message):
        checkpoint(stage)
        progress(event, stage=stage, message=message,
                 completed_embedding_vectors=state['completed_embedding_vectors'],
                 total_embedding_vectors=total_vectors, completed_predicates=state['completed_predicates'],
                 total_predicates=n, current_embedding_field=state['current_embedding_field'])

    def resolve(cache_key, vector):
        nonlocal dimensions
        if cache_key in completed_keys:
            return
        if dimensions is not None and len(vector) != dimensions:
            raise ValueError('不同字段、批次或缓存的 Embedding 返回维度不一致')
        dimensions = len(vector)
        if not field_vectors:
            field_vectors.update({f: np.zeros((n, dimensions), dtype=np.float64) for f in FIELD_ORDER})
        for index, field in aliases[cache_key]['members']:
            field_vectors[field][index] = vector
            completed[index] += 1
            if completed[index] == required[index]:
                state['completed_predicates'] += 1
            state['completed_embedding_vectors'] += 1
        completed_keys.add(cache_key)
        state.update(field_dimensions=dimensions, completed_embeddings=state['completed_embedding_vectors'])

    report('embedding_field_inputs', 'embedding_field_inputs',
           f'已构造四字段输入：{n} 个 Predicate，需要 {total_vectors} 条有效字段向量')
    missing = []
    for cache_key, item in aliases.items():
        state['current_embedding_field'] = item['binding']['field']
        path = local / (cache_key + '.json')
        vector = load_cached_field_embedding(path, item['binding'], dimensions)
        if vector is None:
            vector = load_cached_field_embedding(shared / cache_key[:2] / (cache_key + '.json'),
                                                  item['binding'], dimensions)
            if vector is not None:
                vector = save_cached_field_embedding(path, item['binding'], vector)
        if vector is None:
            missing.append(cache_key)
        else:
            resolve(cache_key, vector)
            report('embedding_cache_hit', 'embedding_api',
                   f'复用 {item["binding"]["field"]} 字段缓存 · '
                   f'{state["completed_embedding_vectors"]}/{total_vectors} 条字段向量 · '
                   f'{state["completed_predicates"]}/{n} 个 Predicate')
    key = os.environ.get('AGENTCM_EMBEDDING_API_KEY', '').strip()
    for start in range(0, len(missing), config['batch_size']):
        batch = missing[start:start + config['batch_size']]
        state['current_embedding_field'] = ', '.join(
            field for field in FIELD_ORDER if any(aliases[k]['binding']['field'] == field for k in batch))
        report('embedding_field_request', 'embedding_api',
               f'字段 Embedding：{state["completed_embedding_vectors"]}/{total_vectors} · '
               f'当前字段：{state["current_embedding_field"]}')
        if not key:
            raise ValueError('请在模型设置中填写 Embedding API Key')
        try:
            matrix = _request_embeddings([aliases[k]['text'] for k in batch], config, key, progress)
            if dimensions is not None and matrix.shape[1] != dimensions:
                raise ValueError('返回维度与其他字段或已保存缓存不匹配')
        except ValueError as exc:
            locations = ', '.join(f'{aliases[k]["members"][0][0] + 1}/{aliases[k]["binding"]["field"]}'
                                  for k in batch)
            raise ValueError(f'字段 Embedding 批次（Predicate 索引/字段：{locations}）失败：{exc}') from None
        checkpoint('embedding_field_save')
        for cache_key, vector in zip(batch, matrix):
            item = aliases[cache_key]
            published = save_cached_field_embedding(shared / cache_key[:2] / (cache_key + '.json'),
                                                     item['binding'], vector)
            frozen = save_cached_field_embedding(local / (cache_key + '.json'), item['binding'], published)
            resolve(cache_key, frozen)
            report('embedding_field_saved', 'embedding_field_save',
                   f'已保存字段向量 {state["completed_embedding_vectors"]}/{total_vectors} · '
                   f'已完成 {state["completed_predicates"]}/{n} 个 Predicate')
    if state['completed_embedding_vectors'] != total_vectors or state['completed_predicates'] != n:
        raise ValueError('字段 Embedding 覆盖不完整，拒绝拼接')
    field_presence = {field: np.asarray([r['fields'][field]['present'] for r in records], dtype=bool)
                      for field in FIELD_ORDER}
    representation_info = {**representation, 'field_dimensions': dimensions,
                           'final_dimensions': len(FIELD_ORDER) * dimensions}
    items = [{**{k: v for k, v in row.items() if k != 'fields'},
              'fields': {field: {**{k: v for k, v in row['fields'][field].items() if k != 'text'},
                                 'embedded': row['fields'][field]['active']} for field in FIELD_ORDER}}
             for row in records]
    checkpoint('embedding_field_save')
    for field in FIELD_ORDER:
        _save_array(root / 'output/field_embeddings' / (field + '.npy'), field_vectors[field])
    write(root / 'output/field_embeddings/metadata.json', {
        'schema': 'predicate-field-embeddings/v1', 'cache_schema': FIELD_CACHE_SCHEMA,
        'input_hash': meta['input_hash'], 'snapshot_hash': meta['snapshot_hash'],
        'embedding_representation': representation_info, 'items': items,
        'vector_hashes': {f: digest(field_vectors[f].tolist()) for f in FIELD_ORDER}})
    report('embedding_concat', 'embedding_concat', '按冻结权重的平方根加权，固定四字段拼接，并执行整体 L2 归一化')
    matrix = build_weighted_concat(field_vectors, weights, field_presence)
    _save_array(root / 'output/embeddings.npy', matrix)
    write(root / 'output/embedding_index.json', {
        'schema': 'predicate-embedding-index/v2', 'embedding': config,
        'input_hash': meta['input_hash'], 'snapshot_hash': meta['snapshot_hash'],
        'input_template': FIELD_INPUT_TEMPLATE, 'embedding_representation': representation_info,
        'field_dimensions': dimensions, 'dimensions': matrix.shape[1],
        'vectors_hash': digest(matrix.tolist()), 'items': items})
    state.update(dimensions=matrix.shape[1], final_dimensions=matrix.shape[1], current_embedding_field=None)
    report('embedding_concat_done', 'embedding_concat',
           f'已保存最终归一化拼接矩阵：{n} × {matrix.shape[1]}，每字段 {dimensions} 维')
    return matrix


def _embedding_matrix(root, registry, meta, state, checkpoint, progress):
    if representation_config(meta['config'])['mode'] == 'fieldwise_concat':
        return _field_embedding_matrix(root, registry, meta, state, checkpoint, progress)
    return _single_text_embedding_matrix(root, registry, meta, state, checkpoint, progress)


def _cluster_indices(matrix, indices, k, config):
    if k == len(indices):
        return [[index] for index in indices]
    if k == 1:
        return [indices]
    from sklearn.cluster import AgglomerativeClustering, KMeans
    from sklearn.exceptions import ConvergenceWarning
    values = matrix[indices]
    if config['algorithm'] == 'agglomerative':
        labels = AgglomerativeClustering(n_clusters=k, metric='cosine',
                                        linkage=config['linkage']).fit_predict(values)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', ConvergenceWarning)
            labels = KMeans(n_clusters=k, n_init=config['n_init'],
                            random_state=config['random_state']).fit_predict(values)
    if len(set(labels.tolist())) != k:
        raise ValueError('算法未得到指定类数；相同向量可能使 K-Means 产生空簇。'
                         '请新建实验调整类数或使用 Agglomerative；本次不会自动减少类数')
    return [[index for index, label in zip(indices, labels) if label == group]
            for group in sorted(set(labels.tolist()))]


def _describe_cluster(indices, registry, similarities):
    import numpy as np
    indices = sorted(indices)
    pair_matrix = similarities[np.ix_(indices, indices)]
    means = (pair_matrix.sum(axis=1) - 1) / max(1, len(indices) - 1)
    medoid_local = int(np.flatnonzero(np.isclose(means, means.max(), rtol=0, atol=1e-12))[0])
    medoid = indices[medoid_local]
    pairs = np.triu_indices(len(indices), k=1)
    values = pair_matrix[pairs]
    minimum_pair = None
    if len(values):
        worst = int(np.argmin(values))
        minimum_pair = {'predicates': [registry[indices[pairs[0][worst]]]['name'],
                                        registry[indices[pairs[1][worst]]]['name']],
                        'similarity': float(values[worst])}
    return {'arity': len(registry[medoid]['parameters']), 'size': len(indices),
            'representative': registry[medoid]['name'], 'medoid_index': medoid,
            'mean_similarity': float(values.mean()) if len(values) else None,
            'min_similarity': float(values.min()) if len(values) else None,
            'minimum_pair': minimum_pair, 'member_indices': indices,
            'members': [registry[i] for i in indices],
            'member_similarities': {registry[i]['name']: float(similarities[i, medoid]) for i in indices},
            'similarity_matrix': pair_matrix.tolist()}


def _statistics(groups, counts, config):
    distribution = Counter(group['size'] for group in groups)
    pair_count = sum(group['size'] * (group['size'] - 1) // 2 for group in groups)
    mean = (sum(group['mean_similarity'] * (group['size'] * (group['size'] - 1) // 2)
                for group in groups if group['size'] > 1) / pair_count if pair_count else None)
    return {'predicate_count': sum(counts.values()), 'target_clusters': config['target_clusters'],
            'actual_clusters': len(groups), 'singleton_count': distribution.get(1, 0),
            'arity_counts': counts,
            'cluster_size_distribution': {str(k): distribution[k] for k in sorted(distribution)},
            'pairwise_similarity': {'pair_count': pair_count, 'mean': mean,
                                    'min': min((g['min_similarity'] for g in groups if g['size'] > 1), default=None)},
            'arities': [{'arity': int(a), 'predicate_count': count,
                         'target_clusters': config['clusters_by_arity'][a],
                         'actual_clusters': sum(g['arity'] == int(a) for g in groups),
                         'singleton_count': sum(g['arity'] == int(a) and g['size'] == 1 for g in groups)}
                        for a, count in counts.items()]}


def run(root, progress, llm_client=None):
    meta = read(root / 'experiment.json')
    progress('registry_read', stage='registry_read', message='读取并核验 Predicate Registry 输入快照')
    registry = verify_inputs(root, meta)
    state_path = root / 'output/execution_state.json'
    state = read(state_path, {})
    if state and (state.get('snapshot_hash') != meta['snapshot_hash'] or state.get('kind') != 'clustering'):
        raise ValueError('执行状态与聚类输入或配置不一致，拒绝恢复')
    state.update(kind='clustering', snapshot_hash=meta['snapshot_hash'],
                 status='running', completed_groups=0, group_total=len(meta['arity_counts']))
    if 'abstraction' in meta:
        if llm_client is None:
            raise ValueError('新建聚类实验需要抽象 Chat 模型客户端')
        state.update(clustering_completed=False, completed_clusters=0,
                     completed_abstraction_clusters=0, generated_predicates=0,
                     abstraction_total_clusters=meta['config']['target_clusters'],
                     current_abstraction_cluster=None, abstraction_run_id=None)

    def checkpoint(stage):
        state.update(next_stage=stage, updated_at=now())
        write(state_path, state)

    checkpoint('registry_read')
    try:
        import numpy as np
        matrix = _embedding_matrix(root, registry, meta, state, checkpoint, progress)
        checkpoint('cluster_statistics')
        progress('similarities', stage='cluster_statistics', message='计算原始归一化 Embedding 空间中的 Cosine Similarity')
        similarities = np.clip(matrix @ matrix.T, -1, 1)
        np.fill_diagonal(similarities, 1)
        _save_array(root / 'output/similarity_matrix.npy', similarities)
        groups = []
        config = meta['config']
        for group_number, (arity, count) in enumerate(meta['arity_counts'].items(), 1):
            k = config['clusters_by_arity'][arity]
            indices = [i for i, p in enumerate(registry) if len(p['parameters']) == int(arity)]
            progress('clustering_group', stage='clustering', arity=int(arity),
                     completed_groups=group_number - 1, group_total=len(meta['arity_counts']),
                     message=f'正在处理 {arity_label(int(arity))} · {count} 个 Predicate → {k} 类'
                             f'；已完成 {group_number - 1}/{len(meta["arity_counts"])} 个元数组')
            checkpoint('clustering')
            binding = digest({'snapshot': meta['snapshot_hash'], 'arity': arity,
                              'vectors': matrix[indices].tolist()})
            path = root / 'output/clustering_groups' / f'arity-{arity}.json'
            cached = read(path)
            if cached and cached.get('binding') == binding:
                partitions = cached['partitions']
                flattened = [i for partition in partitions for i in partition]
                if (len(partitions) != k or any(not part for part in partitions) or
                        any(type(i) is not int for i in flattened) or
                        sorted(flattened) != indices or digest(partitions) != cached.get('partitions_hash')):
                    raise ValueError('已保存的元数组聚类结果校验失败')
            else:
                partitions = _cluster_indices(matrix, indices, k, config)
                write(path, {'binding': binding, 'partitions': partitions,
                             'partitions_hash': digest(partitions)})
            progress('cluster_statistics', stage='cluster_statistics', message=f'计算 {arity_label(int(arity))} 的簇内统计与 Medoid')
            checkpoint('cluster_statistics')
            descriptions = [_describe_cluster(part, registry, similarities) for part in partitions]
            descriptions.sort(key=lambda group: group['medoid_index'])
            prefix = ARITY_NAMES.get(int(arity), f'arity-{arity}').lower()
            for number, group in enumerate(descriptions, 1):
                group['cluster_id'] = f'{prefix}-{number:03d}'
            groups.extend(descriptions)
            state['completed_groups'] = group_number
            if 'abstraction' in meta:
                state['completed_clusters'] = len(groups)
            checkpoint('clustering')
            progress('clustering_group_done', stage='clustering', completed_groups=group_number,
                     message=f'已完成 {group_number}/{len(meta["arity_counts"])} 个元数组')
        covered = sorted(index for group in groups for index in group['member_indices'])
        if len(groups) != config['target_clusters'] or covered != list(range(len(registry))):
            raise ValueError('聚类结果未满足目标类数或成员覆盖约束')
        progress('clustering_save', stage='clustering_save', message='保存完整聚类定义、相似度、统计与 Predicate-Cluster 映射')
        checkpoint('clustering_save')
        statistics = _statistics(groups, meta['arity_counts'], config)
        statistics['embedding_dimensions'] = matrix.shape[1]
        representation_info = None
        if 'embedding_representation' in config:
            representation_info = representation_config(config)
            field_dimensions = matrix.shape[1] // len(FIELD_ORDER) if representation_info['mode'] == 'fieldwise_concat' else matrix.shape[1]
            representation_info.update(field_dimensions=field_dimensions, final_dimensions=matrix.shape[1])
            statistics.update(embedding_representation=representation_info,
                              field_dimensions=field_dimensions, final_dimensions=matrix.shape[1])
        result = {'schema': SCHEMA, 'experiment_id': meta['id'], 'source': meta['source'],
                  'input_hash': meta['input_hash'], 'snapshot_hash': meta['snapshot_hash'],
                  'embedding': meta['embedding'], 'embedding_dimensions': matrix.shape[1],
                  'input_template': meta['embedding']['input_template'], **config, 'similarity_metric': 'cosine',
                  'actual_clusters': len(groups), 'predicate_count': len(registry),
                  'statistics': statistics, 'groups': groups}
        if representation_info is not None:
            result['embedding_representation'] = representation_info
        mapping = sorted(({'predicate_name': member['name'], 'arity': group['arity'],
                           'cluster_id': group['cluster_id'], 'registry_index': index}
                          for group in groups for index, member in zip(group['member_indices'], group['members'])),
                         key=lambda item: item['registry_index'])
        write(root / 'output/clusters.json', result)
        write(root / 'output/predicate_cluster_mapping.json',
              [{k: v for k, v in item.items() if k != 'registry_index'} for item in mapping])
        write(root / 'output/statistics.json', statistics)
        if 'abstraction' in meta:
            from .predicate_abstraction import abstract_clusters, load_snapshot
            state.update(clustering_completed=True, completed_clusters=len(groups),
                         actual_clusters=len(groups), completed_predicates=len(registry))
            checkpoint('cluster_abstraction')

            def abstraction_progress(event, **fields):
                state.update({key: value for key, value in fields.items()
                              if key not in ('stage', 'message')})
                checkpoint(fields['stage'])
                progress(event, **fields)

            abstract_clusters(groups, llm_client, load_snapshot(root, meta['abstraction']),
                              root / 'output', abstraction_progress)
        state.update(status='completed', actual_clusters=len(groups), completed_predicates=len(registry))
        checkpoint('completed')
        return result
    except ImportError:
        state['status'] = 'failed'
        checkpoint(state['next_stage'])
        raise ValueError('聚类依赖未安装，请使用工作台运行的 Python 安装 graph-construction/workbench/requirements.txt') from None
    except Exception:
        state['status'] = 'failed'
        checkpoint(state['next_stage'])
        raise


def export(workspace, identity, mapping=False):
    root, output = workspace.paths(identity)
    if read(root / 'experiment.json').get('kind') != 'clustering':
        raise ValueError('请选择谓词聚类实验')
    state = read(output / 'execution_state.json', {})
    if state.get('status') != 'completed' and not state.get('clustering_completed'):
        raise ValueError('聚类计算完成后才能导出聚类结果')
    return read(output / ('predicate_cluster_mapping.json' if mapping else 'clusters.json'))


def field_pair(workspace, identity, left, right):
    """Read saved field vectors for a pair; this endpoint never calls a provider."""
    root, output = workspace.paths(identity)
    meta = read(root / 'experiment.json')
    if meta.get('kind') != 'clustering' or representation_config(meta['config'])['mode'] != 'fieldwise_concat':
        raise ValueError('字段相似度仅适用于多字段加权拼接实验')
    state = read(output / 'execution_state.json', {})
    if state.get('status') != 'completed' and not state.get('clustering_completed'):
        raise ValueError('请等待聚类计算完成后查看字段相似度')
    registry = verify_inputs(root, meta)
    positive_integer(left, '左侧 Predicate 索引', 0, len(registry) - 1)
    positive_integer(right, '右侧 Predicate 索引', 0, len(registry) - 1)
    metadata = read(output / 'field_embeddings/metadata.json', {})
    representation = representation_config(meta['config'])
    if (metadata.get('schema') != 'predicate-field-embeddings/v1' or
            metadata.get('input_hash') != meta['input_hash'] or
            metadata.get('snapshot_hash') != meta['snapshot_hash'] or
            len(metadata.get('items', [])) != len(registry)):
        raise ValueError('字段向量元数据与输入快照不匹配')
    try:
        import numpy as np
    except ImportError:
        raise ValueError('读取字段相似度需要在工作台 Python 环境中安装 NumPy') from None
    dimensions = metadata['embedding_representation']['field_dimensions']
    fields = {}
    for field in FIELD_ORDER:
        flags = [metadata['items'][i]['fields'][field] for i in (left, right)]
        if not all(flag['present'] for flag in flags):
            fields[field] = {'similarity': None, 'status': 'missing', 'weight': representation['weights'][field]}
        elif representation['weights'][field] == 0:
            fields[field] = {'similarity': None, 'status': 'zero_weight', 'weight': 0}
        else:
            values = np.load(output / 'field_embeddings' / (field + '.npy'), allow_pickle=False)
            if (values.shape != (len(registry), dimensions) or not all(flag['embedded'] for flag in flags) or
                    digest(values.tolist()) != metadata.get('vector_hashes', {}).get(field)):
                raise ValueError(f'{field} 字段向量的形状、有效性或 Hash 校验失败')
            pair = _vectors(values[[left, right]].tolist(), 2, dimensions, normalized=True)
            fields[field] = {'similarity': float(np.clip(pair[0] @ pair[1], -1, 1)),
                             'status': 'available', 'weight': representation['weights'][field]}
    return {'left_index': left, 'right_index': right, 'fields': fields}
