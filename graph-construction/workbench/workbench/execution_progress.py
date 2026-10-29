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
        key = os.environ.get('DEEPSEEK_API_KEY', '')
        def safe(value):
            if isinstance(value, str):
                return value.replace(key, '[REDACTED]') if key else value
            return value
        fields = {k: safe(v) for k, v in fields.items()}
        self.current.update(fields, event=event, message=safe(message), updated_at=now())
        write(self.root / 'execution.json', self.current)
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f'[{timestamp}] {self.current["message"]}', flush=True)
