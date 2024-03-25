import argparse
import os
import re
import subprocess
import sys

import requests


def get_changed_files(
    repo: str, base_sha: str, head_sha: str, token: str
) -> set:
    changed_files = set()
    url = (
        f'https://api.github.com/repos/{repo}/compare/{base_sha}...{head_sha}'
    )
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers).json()
    for file in response.get('files', []):
        changed_files.add(file['filename'])
    return changed_files


def filter_files(files: set, pattern: str) -> set:
    regex = re.compile(pattern)
    return {file for file in files if regex.search(file)}


def main():
    parser = argparse.ArgumentParser(
        description='Detect changed files matching a given pattern.'
    )
    parser.add_argument(
        'pattern', type=str, help='Regex pattern to match files.'
    )
    args = parser.parse_args()

    pattern = args.pattern

    repo = os.getenv('GITHUB_REPOSITORY')
    head_sha = os.getenv('GITHUB_SHA')
    token = os.getenv('GITHUB_TOKEN')

    try:
        base_sha = (
            subprocess.check_output(['git', 'rev-parse', 'HEAD^'])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        print('Error obtaining base SHA. Falling back to HEAD.')
        base_sha = head_sha

    if not (repo and head_sha and token):
        print('Missing required environment variables.')
        sys.exit(1)

    changed_files = get_changed_files(repo, base_sha, head_sha, token)
    filtered_files = filter_files(changed_files, pattern)
    for file in sorted(filtered_files):
        print(file)


if __name__ == '__main__':
    main()
