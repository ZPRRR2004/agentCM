"""Preprocess trajectories, split them into windows, then build predicates."""
import os
import re
import argparse
from datetime import datetime
from pathlib import Path

from src.discover_predicates.main import main as process_discover_predicates
from src.preprocess import Client, load, normalize, save
from src.split.main import load_config as load_split_config
from src.split.main import process_directory as process_split_directory
from src.split.summary_generator import SummaryGenerator


ROOT = Path(__file__).resolve().parent


def load_env(path):
    """Load src/.env without overwriting existing environment variables."""
    if not path.is_file():
        return
    for number, raw in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        key, separator, value = line.partition('=')
        key, value = key.strip(), value.strip()
        if not separator or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key):
            raise ValueError(f'{path.name}:{number}: expected KEY=VALUE')
        if value.startswith(('"', "'")):
            quote = value[0]
            end = value.find(quote, 1)
            if end < 0 or (value[end + 1:].strip() and not value[end + 1:].strip().startswith('#')):
                raise ValueError(f'{path.name}:{number}: invalid quoted value')
            value = value[1:end]
        else:
            value = re.split(r'\s+#', value, maxsplit=1)[0].rstrip()
        os.environ.setdefault(key, value)


def create_run_directory(runs_root):
    """Reserve today's next sequence number without overwriting an old run."""
    runs_root.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime('%m-%d')
    prefix = date + '_'
    numbers = [int(path.name[len(prefix):]) for path in runs_root.iterdir()
               if path.name.startswith(prefix) and path.name[len(prefix):].isdigit()]
    sequence = max(numbers, default=0) + 1
    while True:
        directory = runs_root / f'{date}_{sequence}'
        try:
            directory.mkdir()
            return directory
        except FileExistsError:
            sequence += 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', required=True, type=Path,
                        help='Agent run directory containing */agent/trajectory.json')
    args = parser.parse_args(argv)
    try:
        load_env(ROOT / 'src' / '.env')
    except (OSError, ValueError) as error:
        print(f'Configuration error: {error}')
        return 1

    input_root = args.input_dir.resolve()
    inputs = sorted(input_root.glob('*/agent/trajectory.json'))
    inputs = [path for path in inputs if path.is_file()]
    if not inputs:
        print(f'No inputs found: {input_root}/*/agent/trajectory.json')
        return 1
    if not os.environ.get('DEEPSEEK_API_KEY', '').strip():
        print('Set DEEPSEEK_API_KEY in src/.env or the environment before running.')
        return 1
    try:
        split_config = load_split_config(ROOT / 'src' / 'split' / 'config.yaml')
    except (OSError, ValueError) as error:
        print(f'Split configuration error: {error}')
        return 1

    run_directory = create_run_directory(ROOT / 'runs')
    processed = run_directory / 'processed_trajectory'
    processed.mkdir()
    model = os.environ.get('DEEPSEEK_MODEL') or 'deepseek-flash'
    base_url = os.environ.get('DEEPSEEK_BASE_URL') or 'https://api.deepseek.com'
    client = Client(run_directory, model=model, base_url=base_url)
    summary = {'total': len(inputs), 'succeeded': 0, 'failed': 0, 'cases': []}
    print(f'Run directory: {run_directory}')

    for index, input_path in enumerate(inputs, 1):
        case_name = input_path.parent.parent.name
        source_trajectory = Path(os.path.relpath(input_path, ROOT)).as_posix()
        destination = processed / f'trajectory{index}.json'
        record = {'case': case_name, 'input': source_trajectory}
        print(f'[{index}/{len(inputs)}] {case_name}')
        try:
            trace, source = load(input_path)
            result = normalize(trace, source, client)
            result['metadata'] = {'source_trajectory': source_trajectory}
            save(destination, result)
        except Exception as error:
            # Keep processing the other cases; exclude credentials from diagnostics.
            detail = client.redactor.hide(str(error))
            record.update(status='failed', error=detail)
            summary['failed'] += 1
            print(f'Failed: {detail}')
        else:
            record.update(status='succeeded', output=destination.relative_to(run_directory).as_posix())
            summary['succeeded'] += 1
        summary['cases'].append(record)
        save(run_directory / 'summary.json', summary)

    split_output = run_directory / 'split_windows'
    split_output.mkdir()
    print(f'Splitting processed trajectories into: {split_output}')
    try:
        summary_generator = SummaryGenerator(
            run_directory,
            model=model,
            base_url=base_url,
        )
        window_count, empty_count, split_failed = process_split_directory(
            processed, split_output, split_config, summary_generator)
        summary['split'] = {
            'output': split_output.relative_to(run_directory).as_posix(),
            'windows': window_count,
            'empty_trajectories': empty_count,
            'failed': split_failed,
        }
    except Exception as error:
        detail = client.redactor.hide(str(error))
        split_failed = 1
        summary['split'] = {
            'output': split_output.relative_to(run_directory).as_posix(),
            'windows': 0,
            'empty_trajectories': 0,
            'failed': split_failed,
            'error': detail,
        }
        print(f'Split stage failed: {detail}')
    save(run_directory / 'summary.json', summary)

    discover_predicates_output = run_directory / 'discover_predicates'
    summary['discover_predicates'] = {
        'output': discover_predicates_output.relative_to(run_directory).as_posix(),
        'status': 'running',
        'exit_code': None,
    }
    save(run_directory / 'summary.json', summary)
    print(f'Building predicates from split windows into: {discover_predicates_output}')
    try:
        discover_predicates_exit_code = process_discover_predicates([
            '--input-dir', str(split_output),
            '--output-dir', str(discover_predicates_output),
            '--config', str(ROOT / 'src' / 'discover_predicates' / 'config.yaml'),
        ])
    except Exception as error:
        detail = client.redactor.hide(str(error))
        discover_predicates_exit_code = 1
        summary['discover_predicates'].update(
            status='failed', exit_code=discover_predicates_exit_code, error=detail)
        print(f'Predicate Discovery stage failed: {detail}')
    else:
        summary['discover_predicates'].update(
            status='succeeded' if discover_predicates_exit_code == 0 else 'failed',
            exit_code=discover_predicates_exit_code)
    save(run_directory / 'summary.json', summary)

    print(f'Preprocess: {summary["succeeded"]} succeeded, {summary["failed"]} failed.')
    print(f'Split: {summary["split"]["windows"]} windows, '
          f'{summary["split"]["failed"]} failures.')
    print(f'Predicate Discovery: {summary["discover_predicates"]["status"]} '
          f'(exit code {summary["discover_predicates"]["exit_code"]}).')
    print(f'Processed trajectories: {processed}')
    print(f'Split windows: {split_output}')
    print(f'Predicate Discovery output: {discover_predicates_output}')
    return 1 if (summary['failed'] or split_failed or
                 discover_predicates_exit_code != 0) else 0


if __name__ == '__main__':
    raise SystemExit(main())
