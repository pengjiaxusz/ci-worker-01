#!/usr/bin/env python3
"""Dynamically extract and execute build/test steps from target repo's .github/workflows/core.yml.
Keeps target repo's core.yml as the single source of truth without duplicating crate lists.
"""
import os, re, subprocess, sys

def parse_steps_for_job(yml_text: str, job_id: str):
    lines = yml_text.splitlines()
    in_job = False
    job_indent = None
    in_steps = False
    steps = []
    cur = None
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(' '))
        if not in_job:
            if re.match(rf'^\s{{2}}{re.escape(job_id)}:\s*$', line):
                in_job = True
                job_indent = indent
        else:
            if stripped and not stripped.startswith('#') and indent <= job_indent:
                break
            if re.match(r'^\s+steps:\s*$', line):
                in_steps = True
                i += 1
                continue
            if in_steps:
                m_name = re.match(r'^(\s+)-\s+name:\s*(.+)$', line)
                m_uses = re.match(r'^(\s+)-\s+uses:\s*(.+)$', line)
                if m_name:
                    cur = {'name': m_name.group(2).strip(), 'run': ''}
                    steps.append(cur)
                elif m_uses:
                    cur = None
                elif cur is not None:
                    m_run = re.match(r'^(\s+)run:\s*(.*)$', line)
                    if m_run:
                        run_indent = len(m_run.group(1))
                        val = m_run.group(2).strip()
                        if val in ('>-', '>', '|', '|-'):
                            block = []
                            i += 1
                            while i < len(lines):
                                bl = lines[i]
                                if bl.strip() == '':
                                    block.append('')
                                    i += 1
                                    continue
                                bindent = len(bl) - len(bl.lstrip(' '))
                                if bindent <= run_indent:
                                    break
                                block.append(bl.strip() if val.startswith('>') else bl[run_indent+2:])
                                i += 1
                            cur['run'] = (' '.join(block) if val.startswith('>') else '\n'.join(block)).strip()
                            continue
                        else:
                            cur['run'] = val
        i += 1
    return steps

def main():
    job_id = sys.argv[1]
    yml_path = os.path.join(os.getcwd(), '.github', 'workflows', 'core.yml')
    text = open(yml_path, 'r', encoding='utf-8').read()

    m_tc = re.search(r'CI_RUST_TOOLCHAIN:\s*(\S+)', text)
    if m_tc and 'CI_RUST_TOOLCHAIN' not in os.environ:
        os.environ['CI_RUST_TOOLCHAIN'] = m_tc.group(1)

    steps = parse_steps_for_job(text, job_id)
    ran = 0
    for s in steps:
        cmd = s.get('run', '').strip()
        if not cmd:
            continue
        if any(cmd.startswith(p) for p in ('cargo ', 'python3 ')):
            print(f"\n::group::{s['name']}", flush=True)
            print(f"$ {cmd}", flush=True)
            res = subprocess.run(cmd, shell=True)
            print("::endgroup::", flush=True)
            ran += 1
            if res.returncode != 0:
                sys.exit(res.returncode)
    if ran == 0:
        print(f"No executable steps found for job '{job_id}' in core.yml", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
