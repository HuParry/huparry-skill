"""Check project conventions and optionally compile exact interactive sources."""
import argparse
import os
from pathlib import Path
import re
import subprocess

def without_comments(text):
    tokens=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/')
    return tokens.sub(lambda m: ' ' if m[0].startswith(('//','/*')) else m[0],text)

def check(path,interactor=False):
    code=without_comments(Path(path).read_text(encoding='utf-8-sig'));errors=[]
    if re.search(r'\bsync_with_stdio\s*\(\s*(?:false|0)\s*\)',code):
        errors.append('Keep default stream synchronization; do not call sync_with_stdio(false/0).')
    if re.search(r'\b(?:cin|cout)\s*\.\s*tie\s*\(\s*(?:nullptr|NULL|0)\s*\)',code):
        errors.append('Keep default stream ties for this project.')
    if interactor:
        if not re.search(r'^\s*#\s*include\s*"testlib\.h"',code,re.M):
            errors.append('Use #include "testlib.h" supplied by Hydro, without renaming the header.')
        if not re.search(r'\bregisterInteraction\s*\(',code):
            errors.append('Initialize testlib with registerInteraction(argc, argv).')
        if re.search(r'\bcin\s*(?:>>|\.)|\b(?:scanf|gets|getchar)\s*\(|\bgetline\s*\(\s*(?:std::)?cin\b',code):
            errors.append('Read contestant commands through ouf, not cin/scanf/another stdin reader.')
    return errors

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--interactor',required=True);ap.add_argument('--solution',action='append',default=[])
    ap.add_argument('--testlib-dir',help='Compile exact input sources using this directory/testlib.h')
    ap.add_argument('--compiler',default='g++')
    ap.add_argument('--build-dir',help='Required with --testlib-dir; outputs stay outside the import package')
    a=ap.parse_args();errors=[]
    for path,role in [(a.interactor,True)]+[(p,False) for p in a.solution]:
        try:messages=check(path,role)
        except (OSError,UnicodeError) as e:messages=[str(e)]
        errors.extend(f'{path}: {message}' for message in messages)
    for message in errors:print(message)
    if errors:return 1
    if a.testlib_dir:
        if not a.build_dir:ap.error('--build-dir is required with --testlib-dir')
        headers=Path(a.testlib_dir).resolve()
        if not (headers/'testlib.h').is_file():ap.error('The standard testlib.h is missing from --testlib-dir')
        out=Path(a.build_dir).resolve();out.mkdir(parents=True,exist_ok=True)
        sources=[('interactor',a.interactor)]+[(f'solution-{i}',p) for i,p in enumerate(a.solution,1)]
        try:
            for name,path in sources:
                target=out/(name+('.exe' if os.name=='nt' else ''))
                subprocess.run([a.compiler,'-std=c++17','-O2','-Wall','-Wextra',str(Path(path).resolve()),'-I',str(headers),'-o',str(target)],check=True)
        except (OSError,subprocess.CalledProcessError) as e:
            print(f'COMPILE FAILED: {e}');return 1
        print(f'Compiled {len(sources)} exact source files successfully; live-test the resulting programs next.')
    else:print('Source convention checks passed; no compilation was requested. Compile and live-test separately.')
    return 0

if __name__=='__main__':raise SystemExit(main())
