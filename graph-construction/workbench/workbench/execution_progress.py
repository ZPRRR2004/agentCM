"""Persist worker progress separately from resumable algorithm outputs."""
import os
import uuid
from datetime import datetime
from pathlib import Path

from .common import now, write


STAGES = {
    'discovery': '发现候选谓词',
    'comparison': '与已有谓词比较',
    'review': '模型审核谓词',
    'registry_revision': '根据你的反馈修改谓词库',
    'registry_read': '读取 Predicate Registry',
    'embedding_inputs': '构造 Embedding 输入',
    'embedding_api': '调用 Embedding API',
    'embedding_save': '保存 Embedding',
    'embedding_field_inputs': '构造四字段 Embedding 输入',
    'embedding_field_save': '保存字段向量',
    'embedding_concat': '生成平方根加权拼接向量并整体归一化',
    'clustering': '执行各元数组聚类',
    'cluster_statistics': '计算 Cluster 统计',
    'clustering_save': '保存聚类结果',
    'cluster_abstraction': 'LLM Predicate Abstraction',
    'cluster_abstraction_save': '保存抽象 Registry 与成员映射',
}


class ExecutionProgress:
    def __init__(self, root):
        self.root = Path(root)
        self.current = {'run_id': uuid.uuid4().hex, 'run_started_at': now()}

    def __call__(self, event, **fields):
        stage = STAGES.get(fields.get('stage'), fields.get('stage', ''))
        message = fields.pop('message', '')
        if event == 'model_wait':
            message = f'{stage}：已发送请求，等待模型返回（第 {fields["attempt"]}/{fields["attempt_limit"]} 次尝试）'
        elif event == 'model_received':
            message = f'{stage}：已收到模型返回，正在检查结果格式'
        elif event == 'model_done':
            message = f'{stage}：结果检查通过，用时 {fields["duration_seconds"]:.1f} 秒'
        elif event == 'model_error':
            message = f'{stage}：{fields.pop("error")}。' + ('即将重试' if fields.pop('will_retry') else '本阶段停止')
        keys = [os.environ.get(name, '') for name in ('DEEPSEEK_API_KEY', 'AGENTCM_EMBEDDING_API_KEY')]
        def safe(value):
            if isinstance(value, str):
                for key in keys:
                    if key:
                        value = value.replace(key, '[REDACTED]')
            return value
        fields = {k: safe(v) for k, v in fields.items()}
        self.current.update(fields, event=event, message=safe(message), updated_at=now())
        write(self.root / 'execution.json', self.current)
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f'[{timestamp}] {self.current["message"]}', flush=True)
