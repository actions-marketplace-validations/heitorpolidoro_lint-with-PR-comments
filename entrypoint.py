#!/bin/python
import os
import re
from subprocess import Popen, PIPE
from github import Github

# os.system("""
# set -x
# apk add --update --no-cache git github-cli
# echo "$PERSONAL_ACCESS_TOKEN" | gh auth login --with-token
# gh repo clone heitorpolidoro/polidoro-argument
# cd polidoro-argument
# git checkout lint
# """)
# os.chdir('polidoro-argument')
print('::group::Flake8')
flake_cmd = 'flake8 --show-source ' + os.environ['INPUT_FLAKE_PARAMETERS']
print(flake_cmd)
proc = Popen(flake_cmd, shell=True, text=True, stdout=PIPE, stderr=PIPE)
outs, errs = proc.communicate()
print(outs)
splitted_outs = outs.split('\n')
lines_with_errors = {}
for errors_index in range(0, len(splitted_outs), 3):
    if splitted_outs[errors_index]:
        info = re.search(r'(?P<path>.*?):(?P<line>\d*):\d*: *(?P<error>.*)', splitted_outs[errors_index]).groupdict()
        lwe = lines_with_errors.get(info['line'], {})
        lwe['errors'] = lwe.get('errors', []) + [info['error']]
        lwe['code'] = splitted_outs[errors_index + 1].strip()
        lines_with_errors[info['line']] = lwe

gh = Github(os.environ['INPUT_GITHUB_TOKEN'])
repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
pr = repo.get_pulls(head=os.environ['GITHUB_REF'])[0]
commit = list(pr.get_commits())[-1]
comments = pr.get_review_comments()
for file in pr.get_files():
    for diff_index, diff_code in enumerate(file.patch.split('\n')):
        if diff_code[0] == '+':
            for lwe in lines_with_errors.values():
                if lwe['code'] == diff_code[1:].strip():
                    print(diff_index, lwe['errors'])
                    pr.create_review_comment('\n'.join(lwe['errors']), commit, file.filename, diff_index)
    print('::endgroup::')

