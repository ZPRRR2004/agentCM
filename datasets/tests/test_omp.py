"""Check source fidelity and tool-result alignment of the public trace adapter."""
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('omp', Path(__file__).resolve().parents[1] / 'adapters/omp.py')
omp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(omp)


class OMPTests(unittest.TestCase):
    def trace(self, rows):
        return omp.convert_trace('\n'.join(json.dumps(r) for r in rows).encode(),
                                 'task-a', 'Original task instruction', 'trace.jsonl')

    def test_exact_text_and_tool_ids_survive_without_duplicate_results(self):
        user = {'type':'message_end','message':{'role':'user','content':[{'type':'text','text':'Harness + task'}]}}
        agent = {'type':'message_end','message':{'role':'assistant','content':[
            {'type':'thinking','thinking':'Read the\nexact text'},
            {'type':'toolCall','id':'a','name':'read','arguments':{'path':'x'}},
            {'type':'toolCall','id':'b','name':'bash','arguments':{'command':'cat x'}}]}}
        def result(identity, text):
            return {'type':'message_end','message':{'role':'toolResult','toolCallId':identity,
                                                  'content':[{'type':'text','text':text}]}}
        rows = [user, agent,
                {'type':'tool_execution_end','toolCallId':'a','result':{'content':[{'type':'text','text':'duplicate'}]}},
                result('b','second\n\t  '), result('a','first\n'),
                {'type':'raw_output','text':json.dumps({'type':'agent_end','messages':[user,agent]})},
                {'type':'auto_compaction_end','skipped':True}]
        data = self.trace(rows)
        self.assertEqual(data['metadata']['initial_prompt'], 'Harness + task')
        self.assertEqual(data['query']['text'], 'Original task instruction')
        self.assertEqual(len(data['events']), 2)
        self.assertEqual(data['events'][0]['thought'], 'Read the\nexact text')
        self.assertEqual([c['observation']['raw'] for c in data['events'][0]['tool_calls']], ['first\n','second\n\t  '])
        self.assertEqual([c['observation']['source_line'] for c in data['events'][0]['tool_calls']], [5,4])
        self.assertEqual(data['events'][1]['context_event'], 'auto_compaction_end')

    def test_interrupted_tool_fallback_and_source_overflow_are_explicit(self):
        data = self.trace([
            {'type':'message_end','message':{'role':'assistant','content':[{'type':'toolCall','id':'a','name':'bash','arguments':{}}]}},
            {'type':'tool_execution_end','toolCallId':'a','isError':True,'result':{'content':[{'type':'text','text':'timeout'}]}},
            {'type':'trace_filter_summary','overflowEvents':2}])
        observation = data['events'][0]['tool_calls'][0]['observation']
        self.assertEqual(observation['raw'], 'timeout')
        self.assertTrue(observation['is_error'])
        self.assertEqual(observation['source_type'], 'tool_execution_end')
        self.assertEqual(data['metadata']['flags'][0]['events'], 2)

    def test_unmatched_tool_result_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no matching call'):
            self.trace([{'type':'message_end','message':{'role':'toolResult','toolCallId':'unknown','content':[]}}])

    def test_full_dataset_conversion_preserves_utf8_and_lf(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination, tasks = root / 'public', root / 'tasks'
            source = destination / 'source'
            entries = []
            for index in range(89):
                task_id = f'task-{index:02d}'
                instruction = f'处理第 {index} 项任务 🚀\n'
                official = tasks / task_id / 'instruction.md'
                official.parent.mkdir(parents=True)
                official.write_bytes(instruction.encode('utf-8'))
                runs = ['xhigh'] + ([f'xhigh-rerun-{index}'] if index < 2 else [])
                for run in runs:
                    task = source / run / 'traces' / task_id
                    trace = task / 'agent/omp-test/omp.jsonl'
                    trace.parent.mkdir(parents=True)
                    row = {'type': 'message_end', 'message': {'role': 'assistant',
                           'content': [{'type': 'text', 'text': '检查输入并继续执行 🚀'}]}}
                    files = {task / 'instruction.txt': instruction,
                             task / 'result.json': json.dumps({'pass': True, 'scored': True,
                                                              'detail': '验证成功 🚀'}, ensure_ascii=False),
                             trace: json.dumps(row, ensure_ascii=False) + '\n'}
                    for path, text in files.items():
                        data = text.encode('utf-8')
                        path.write_bytes(data)
                        entries.append({'path': path.relative_to(source).as_posix(),
                                        'sha256': hashlib.sha256(data).hexdigest()})
            manifest = {'repository': 'https://example.com/traces', 'revision': 'a' * 40,
                        'description': '完整轨迹 🚀', 'files': entries}
            (destination / 'source-manifest.json').write_bytes(
                json.dumps(manifest, ensure_ascii=False).encode('utf-8'))
            report = omp.convert_dataset(destination, tasks)
            self.assertEqual((report['task_count'], report['trajectory_count'], report['event_count']),
                             (89, 91, 91))
            self.assertEqual(report['instruction_mismatches'], [])
            raw = (destination / 'normalized/xhigh__task-00.json').read_bytes()
            data = json.loads(raw.decode('utf-8'))
            self.assertEqual(data['query']['text'], '处理第 0 项任务 🚀\n')
            self.assertEqual(data['events'][0]['thought'], '检查输入并继续执行 🚀')
            self.assertEqual(data['metadata']['result']['detail'], '验证成功 🚀')
            self.assertNotIn(b'\r\n', raw)
            summary = (destination / 'normalization-manifest.json').read_bytes()
            self.assertEqual(json.loads(summary.decode('utf-8'))['trajectory_count'], 91)
            self.assertNotIn(b'\r\n', summary)


if __name__ == '__main__':
    unittest.main()
