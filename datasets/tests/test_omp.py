"""Check source fidelity and tool-result alignment of the public trace adapter."""
import importlib.util
import json
from pathlib import Path
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


if __name__ == '__main__':
    unittest.main()
