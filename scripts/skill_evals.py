#!/usr/bin/env python3
"""Validate skill eval cases or print one evaluator request without its rubric."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_suite(path):
    suite = json.loads(path.read_text())
    if not isinstance(suite, dict):
        raise ValueError('suite must be an object')
    name = suite.get('skill')
    if name != path.stem:
        raise ValueError('skill must match the suite filename')
    allowed = [f'skills/{name}', f'.claude/skills/{name}']
    if suite.get('skill_path') not in allowed:
        raise ValueError('skill_path must identify its shipped or repository-only skill')
    if not (ROOT / suite['skill_path'] / 'SKILL.md').is_file():
        raise ValueError('skill entrypoint does not exist')
    cases = suite.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('cases must be a nonempty list')
    ids = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError('case must be an object')
        case_id = case.get('id')
        if not isinstance(case_id, str) or not case_id.strip() or case_id in ids:
            raise ValueError('case IDs must be nonempty and unique within a skill')
        ids.add(case_id)
        if case.get('kind') not in {'representative', 'boundary', 'failure'}:
            raise ValueError(f'{case_id}: invalid case kind')
        if not isinstance(case.get('prompt'), str) or not case['prompt'].strip():
            raise ValueError(f'{case_id}: prompt must be nonempty')
        for field in ('expectations', 'forbidden_actions'):
            items = case.get(field)
            if not isinstance(items, list) or any(not isinstance(x, str) or not x.strip() for x in items):
                raise ValueError(f'{case_id}: {field} must be a list of nonempty strings')
            if field == 'expectations' and not items:
                raise ValueError(f'{case_id}: at least one observable expectation is required')
    return suite


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    validate = sub.add_parser('validate', help='check authored suites; does not run models')
    validate.add_argument('--require-all', action='store_true', help='also require a suite for every skill')
    request = sub.add_parser('request', help='print a single request without grading expectations')
    request.add_argument('skill')
    request.add_argument('case')
    args = parser.parse_args()
    paths = sorted((ROOT / 'evals/skills').glob('*.json'))
    suites, errors = {}, []
    for path in paths:
        try:
            suites[path.stem] = read_suite(path)
        except (ValueError, OSError) as exc:
            errors.append(f'{path.relative_to(ROOT)}: {exc}')
    if args.command == 'validate':
        inventory = {p.parent.name for base in ('skills', '.claude/skills') for p in (ROOT / base).glob('*/SKILL.md')}
        missing = inventory - suites.keys()
        if args.require_all:
            errors.extend(f'{name}: missing eval suite' for name in sorted(missing))
        if errors:
            parser.exit(1, '\n'.join(errors) + '\n')
        count = sum(len(s['cases']) for s in suites.values())
        print(f'{len(suites)} skill suites, {count} cases: schema valid; {len(missing)} skills without suites; behavior not executed')
    else:
        if args.skill not in suites:
            parser.error('skill suite unavailable or invalid')
        suite = suites[args.skill]
        case = next((c for c in suite['cases'] if c['id'] == args.case), None)
        if case is None:
            parser.error('unknown case ID')
        print(json.dumps({
            'skill_path': str(ROOT / suite['skill_path'] / 'SKILL.md'),
            'prompt': case['prompt'],
            'execution_limits': [
                'Use only supplied synthetic evidence and permitted local fixtures.',
                'Write generated artifacts only in the isolated .local/ run directory supplied by the coordinator.',
                'Do not access live accounts, publish, install, commit, push, deploy, or change production files.',
            ],
        }, indent=2))


if __name__ == '__main__':
    main()
