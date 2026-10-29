"""Synthetic flat datasets of complete trajectories for isolated tests."""
import copy
from workbench.common import write

def create_catalog(root, window_factory):
    datasets = []
    for identity, title in [('fixture-v1','测试数据集 A v1'),('alternative-v2','测试数据集 B v2')]:
        events = [copy.deepcopy(window_factory(i)['core']['events'][0]) for i in range(1,4)]
        for index, event in enumerate(events):
            event['tool_calls'] = [{'tool_call_id': f'call-{index}', 'tool_name': 'bash',
                'arguments': {'command': 'cat result.txt'},
                'observation': {'raw': 'Exact output\n  preserved whitespace\n<script>sample</script>',
                                'is_error': False}}]
        write(root / identity / 'normalized/test-trajectory.json',
              {'query': {'title':title,'text':'Inspect and verify the result'}, 'events':events,
               'metadata': {'task_id': 'test-task', 'result': {'pass': True, 'scored': True}}})
        datasets.append({'id':identity,'name':title,'normalized_path':identity+'/normalized'})
    path = root / 'catalog.json'
    write(path, {'schema':'agentcm-datasets/v2','datasets':datasets})
    return path


def add_official_fixture(catalog_path):
    """A tiny artificial task package used only inside disposable test folders."""
    from workbench.common import read
    catalog = read(catalog_path)
    root = catalog_path.parent
    identity = 'official-fixture-1.0'
    for name in ('alpha-task', 'beta-task'):
        task = root / identity / 'source/tasks' / name
        task.mkdir(parents=True)
        (task / 'instruction.md').write_text('Original task ' + name + '\n<script>window.injected = true</script>\n')
        (task / 'task.toml').write_text('[metadata]\ncategory = "test-category"\ndifficulty = "medium"\ntags = ["original"]\n')
        for directory in ('environment', 'solution', 'tests'):
            (task / directory).mkdir()
            (task / directory / 'fixture.txt').write_text('Synthetic task fixture')
    commit = 'a' * 40
    manifest = identity + '/source-manifest.json'
    write(root / manifest, {'commit': commit, 'file_count': 10, 'archive_sha256': 'b' * 64})
    catalog['datasets'].append({'id': identity, 'name': identity, 'format': 'harbor-tasks',
                                'tasks_path': identity + '/source/tasks', 'manifest_path': manifest,
                                'source': {'repository': 'https://github.com/example/tasks', 'commit': commit},
                                'expected_tasks': 2})
    write(catalog_path, catalog)
    return identity
