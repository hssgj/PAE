"""Collect a local PAE source inventory without reading sessions or credentials.

Run on the actual phone. No upload, checkout, pull, reset or process changes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

CODE_SUFFIXES = {'.py', '.sh', '.html', '.java', '.xml', '.gradle', '.toml'}
EXCLUDED_PARTS = {'data', 'models', 'pae_backups', 'exports', '__pycache__', '.git', '.gradle', 'build', '.venv'}
SECRET_PATTERNS = (
    re.compile(r'\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|gsk_[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|AIza[A-Za-z0-9_-]{20,})'),
    re.compile(r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----'),
    re.compile(r'(?im)^\s*(?:export\s+)?(?:[A-Z_]*(?:API_KEY|ACCESS_TOKEN|REFRESH_TOKEN|CLIENT_SECRET|PASSWORD|GITHUB_TOKEN))\s*=\s*[\"\']?[A-Za-z0-9_./+-]{12,}'),
)


def git_value(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 'UNKNOWN'


def collect(root: Path, output: Path, include_source: bool = False) -> dict:
    root = root.resolve()
    if not (root / 'prototype_v0').is_dir():
        raise ValueError('Expected a PAE checkout containing prototype_v0')
    if output.exists():
        raise FileExistsError('Output already exists; choose a new filename')
    candidates = list((root / 'prototype_v0').rglob('*'))
    candidates += list(root.glob('start-*.sh'))
    if (root / 'pae-android').is_dir():
        candidates += list((root / 'pae-android').rglob('*'))
    report = {
        'schema': 'pae-phone-inventory-v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'git_head': git_value(root, 'rev-parse', 'HEAD'),
        'branch': git_value(root, 'branch', '--show-current'),
        'tracked_changes': git_value(root, 'diff', '--name-status', 'HEAD'),
        'untracked_paths': git_value(root, 'ls-files', '--others', '--exclude-standard'),
        'files': [], 'excluded': [],
        'contains_sessions': False, 'contains_model_weights': False,
        'uploaded': False,
    }
    accepted = []
    for path in sorted(set(candidates)):
        relative = path.relative_to(root)
        if path.is_symlink():
            report['excluded'].append({'path':relative.as_posix(),'reason':'symlink'})
            continue
        if not path.is_file() or set(relative.parts) & EXCLUDED_PARTS:
            continue
        if path.suffix not in CODE_SUFFIXES or '.bak' in path.name:
            continue
        if not path.resolve().is_relative_to(root):
            raise ValueError('Source path escaped checkout')
        if path.stat().st_size > 1_000_000:
            report['excluded'].append({'path':relative.as_posix(),'reason':'over size limit'})
            continue
        data = path.read_bytes()
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            report['excluded'].append({'path':relative.as_posix(),'reason':'non-UTF8'})
            continue
        suspect = any(pattern.search(text) for pattern in SECRET_PATTERNS)
        report['files'].append({'path':relative.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source_included':include_source and not suspect})
        if suspect:
            report['excluded'].append({'path':relative.as_posix(),'reason':'possible embedded credential; source omitted'})
        elif include_source:
            accepted.append((relative.as_posix(), data))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('inventory.json', json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        for name, data in accepted:
            archive.writestr('source/' + name, data)
    output.chmod(0o600)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--include-source', action='store_true', help='Include allowed UTF-8 source after credential-pattern screening; review before sharing')
    args = parser.parse_args()
    output = args.output or args.root / 'exports' / ('phone-source-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.zip')
    report = collect(args.root, output, args.include_source)
    print(json.dumps({'output':str(output.resolve()),'source_files':len(report['files']),'omitted':len(report['excluded']),'uploaded':False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
