"""Contract and pipeline checks using deterministic responses, with no API calls."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.discover_predicates.main import main
from src.discover_predicates.prompt_loader import PromptManager
from src.discover_predicates.registry import apply_registry_revision
from src.discover_predicates.storage import Storage
from src.discover_predicates.validator import (
    PREDICATE_SCHEMA_VERSION, ValidationError, predicate_signature,
    validate_comparison, validate_predicate, validate_registry_revision_plan)
from src.discover_predicates.window_loader import load_windows


ROOT = Path(__file__).resolve().parents[1]


def predicate(name='USES', types=('action', 'observation')):
    return {
        'name': name,
        'definition': 'A supported assertion with explicitly ordered argument roles.',
        'parameters': [
            {'name': f'argument_{index}', 'type': kind,
             'description': f'The role at argument position {index}.'}
            for index, kind in enumerate(types)
        ],
        'assertion_conditions': ['The visible evidence establishes the assertion.'],
        'exclusion_conditions': ['A shared topic alone does not establish it.'],
    }


def window(index):
    event = {'event_id': f'event-{index}', 'source': 'agent',
             'thought': 'Inspect the evidence', 'tool_calls': []}
    return {
        'trajectory_id': 'test-trajectory', 'window_id': f'window_{index:04d}',
        'user_query': {'title': 'Test', 'text': 'Inspect and verify the result'},
        'previous_summary': '', 'future_summary': '',
        'overlap': {'event_ids': [], 'events': []},
        'core': {'event_ids': [event['event_id']], 'events': [event]},
        'metadata': {'window_index': index},
    }


def after(text, marker):
    return json.JSONDecoder().raw_decode(text.split(marker, 1)[1].lstrip())[0]


class Model:
    def __init__(self, fail_comparison=False):
        self.stages = []
        self.fail_comparison = fail_comparison

    def __call__(self, payload):
        system, user = [message['content'] for message in payload['messages']]
        if 'Perform Blind Predicate Discovery' in system:
            self.stages.append('discovery')
            nodes = after(user, '[CORE NODES]')
            number = int(nodes[0]['source']['event_id'].split('-')[-1])
            definitions = {
                1: [predicate('IS_PLAN', ('reasoning',)), predicate(),
                    predicate('SUPERSEDES', ('observation', 'observation', 'reasoning'))],
                2: [predicate(), predicate('DERIVES', ('reasoning', 'observation[]', 'reasoning'))],
                3: [],
            }[number]
            value = {'candidate_predicates': definitions}
        elif 'Compare candidate predicate definitions' in system:
            self.stages.append('comparison')
            if self.fail_comparison:
                self.fail_comparison = False
                raise RuntimeError('Injected interruption after discovery')
            candidates = after(user, 'Candidate predicates:')
            registry = after(user, 'Existing registry:')
            names = {item['name'] for item in registry}
            value = {'existing': [
                {'candidate_name': item['name'], 'matched_existing_name': item['name']}
                for item in candidates if item['name'] in names],
                'new': [item for item in candidates if item['name'] not in names],
                'uncertain': []}
        elif 'Review typed predicate definitions' in system:
            self.stages.append('review')
            comparison = after(user, 'Complete Comparison result:')
            revisions = []
            if comparison['existing']:
                revised = predicate()
                revised['assertion_conditions'].append('The use can be located in the action.')
                revisions = [{'original_name': 'USES', 'revised_predicate': revised}]
            value = {'accepted_predicates': comparison['new'],
                     'revised_existing_predicates': revisions}
        elif "Apply the human's feedback" in system:
            self.stages.append('registry_revision')
            registry = after(user, 'Current predicate registry:')
            revisions = []
            for item in registry:
                if item['name'] == 'USES':
                    revised = copy.deepcopy(item)
                    revised['name'] = 'USES_INFORMATION'
                    revisions.append({'original_name': item['name'], 'operation': 'REVISE',
                                      'revised_predicate': revised})
                else:
                    revisions.append({'original_name': item['name'], 'operation': 'KEEP'})
            value = {'revisions': revisions}
        else:
            raise AssertionError('Unexpected pipeline stage')
        return {'choices': [{'finish_reason': 'stop', 'message': {
            'content': json.dumps(value)}}]}


class PredicateContractTests(unittest.TestCase):
    def test_unary_binary_ternary_and_collection_signatures(self):
        for name, types in [('IS_PLAN', ('reasoning',)), ('USES', ('action', 'observation')),
                            ('SUPERSEDES', ('observation', 'observation', 'reasoning')),
                            ('DERIVES', ('reasoning', 'observation[]', 'reasoning'))]:
            value = predicate(name, types)
            self.assertIs(validate_predicate(value), value)
            self.assertTrue(predicate_signature(value).startswith(name + '('))
            self.assertEqual(len(value['parameters']), len(types))

    def test_legacy_edge_definitions_are_rejected(self):
        with self.assertRaises(ValidationError):
            validate_predicate({'name': 'USES', 'definition': 'Legacy edge',
                                'source_description': 'source', 'target_description': 'target'})

    def test_invalid_parameter_contracts_are_rejected(self):
        bad = []
        value = predicate(); value['parameters'] = []; bad.append(value)
        value = predicate(); value['parameters'][1]['name'] = 'argument_0'; bad.append(value)
        value = predicate(); value['parameters'][0]['type'] = 'unknown'; bad.append(value)
        value = predicate(); value['parameters'][0]['type'] = 'observation[][]'; bad.append(value)
        value = predicate(); value['parameters'][0]['type'] = []; bad.append(value)
        value = predicate(); value['assertion_conditions'] = []; bad.append(value)
        value = predicate(); value['exclusion_conditions'] = ['']; bad.append(value)
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_predicate(value)

    def test_comparison_cannot_mutate_a_candidate_signature(self):
        original = predicate()
        changed = copy.deepcopy(original)
        changed['parameters'].reverse()
        with self.assertRaisesRegex(ValidationError, '原样保留'):
            validate_comparison({'existing': [], 'new': [changed], 'uncertain': []},
                                [original], [])

    def test_merge_preserves_ordered_argument_types(self):
        registry = [predicate('USES'), predicate('CONSUMES')]
        plan = {'revisions': [
            {'original_name': 'CONSUMES', 'operation': 'MERGE', 'merge_into': 'USES'},
            {'original_name': 'USES', 'operation': 'KEEP'}]}
        self.assertEqual(apply_registry_revision(registry, plan), [registry[0]])
        for incompatible in [('action',), ('observation', 'action'),
                             ('action', 'observation', 'reasoning')]:
            registry[1] = predicate('CONSUMES', incompatible)
            with self.subTest(types=incompatible), self.assertRaisesRegex(ValidationError, '不兼容'):
                validate_registry_revision_plan(plan, registry)

    def test_existing_match_preserves_arity_and_ordered_types(self):
        comparison = {'existing': [{'candidate_name': 'CONSUMES',
                                    'matched_existing_name': 'USES'}],
                      'new': [], 'uncertain': []}
        validate_comparison(comparison, [predicate('CONSUMES')], [predicate()])
        for types in [('action',), ('observation', 'action'),
                      ('action', 'observation', 'reasoning')]:
            with self.subTest(types=types), self.assertRaisesRegex(ValidationError, '不兼容'):
                validate_comparison(comparison, [predicate('CONSUMES', types)], [predicate()])

    def test_review_card_contains_all_parameter_roles(self):
        value = predicate('SUPERSEDES', ('observation', 'observation', 'reasoning'))
        card = '\n'.join(Storage._predicate_markdown(value))
        self.assertIn(predicate_signature(value), card)
        self.assertIn('成立条件', card)
        self.assertIn('排除条件', card)


class PredicatePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.inputs = self.base / 'windows'; self.inputs.mkdir()
        self.output = self.base / 'output'
        self.config = self.base / 'config.yaml'
        self.config.write_text('human_feedback_interval: 2\nfeedback_mode: registry_feedback\nmax_llm_retries: 0\n')
        for index in range(1, 4):
            (self.inputs / f'window_{index}.json').write_text(json.dumps(window(index)))

    def run_pipeline(self, model, resume=False):
        answers = iter(['Clarify the USES predicate name.', 'END'])
        args = ['--input-dir', str(self.inputs), '--output-dir', str(self.output),
                '--config', str(self.config)] + (['--resume'] if resume else [])
        with contextlib.redirect_stdout(io.StringIO()):
            return main(args, transport=model, input_func=lambda _: next(answers))

    def test_discovery_comparison_review_feedback_and_completed_resume(self):
        model = Model()
        self.assertEqual(self.run_pipeline(model), 0)
        storage = Storage(self.output)
        state = storage.load_state()
        self.assertEqual(state['predicate_schema_version'], PREDICATE_SCHEMA_VERSION)
        self.assertEqual(state['status'], 'completed')
        registry = storage.load_registry()
        self.assertEqual({item['name'] for item in registry},
                         {'IS_PLAN', 'USES_INFORMATION', 'SUPERSEDES', 'DERIVES'})
        self.assertEqual(storage.reconstruct_registry(load_windows(self.inputs), 3, save=False), registry)
        self.assertEqual(model.stages.count('discovery'), 3)
        self.assertEqual(model.stages.count('registry_revision'), 1)
        self.assertTrue((self.output / 'predicate_registry.json').exists())
        self.assertFalse((self.output / 'edge_type_registry.json').exists())
        packet = (self.output / 'batches/batch_0001/review_packet.md').read_text()
        self.assertIn('observation[]', packet)
        before = list(model.stages)
        self.assertEqual(self.run_pipeline(model, resume=True), 0)
        self.assertEqual(before, model.stages)

    def test_resume_after_interrupted_comparison_reuses_discovery(self):
        model = Model(fail_comparison=True)
        self.assertEqual(self.run_pipeline(model), 1)
        self.assertEqual(Storage(self.output).load_state()['next_stage'], 'comparison')
        self.assertEqual(self.run_pipeline(model, resume=True), 0)
        self.assertEqual(model.stages.count('discovery'), 3)

    def test_legacy_resume_fails_without_rewriting_history(self):
        self.output.mkdir()
        state = self.output / 'execution_state.json'
        state.write_text('{"status":"completed"}')
        before = state.read_bytes()
        model = Model()
        self.assertEqual(self.run_pipeline(model, resume=True), 1)
        self.assertEqual(model.stages, [])
        self.assertEqual(state.read_bytes(), before)

    def test_saved_prompt_contract_matches_rendered_variables(self):
        manager = PromptManager(ROOT / 'src/discover_predicates/prompts', self.output)
        manager.validate(manager.load_from_disk())


if __name__ == '__main__':
    unittest.main()
