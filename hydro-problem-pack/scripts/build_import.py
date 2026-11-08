"""Build a Hydro import ZIP from one numeric problem folder (stdlib only).

This checks the file allowlist, UTF-8 text, Hydro file:// assets and ZIP integrity.
It deliberately does not parse YAML or validate the judge's semantics.
"""
import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote
import zipfile

IMAGE_EXTENSIONS={'.png','.jpg','.jpeg','.gif','.webp','.svg','.avif'}

def check_statement_images(statement, present):
    # Hydro uses file://<attachment-name>, not an OS file URI. Keep case exact.
    references=[]
    for raw in re.findall(r'''file://[^\s<>()[\]"']*''',statement,flags=re.I):
        name=unquote(re.split(r'[?#]',raw[7:],maxsplit=1)[0])
        if not name or name.startswith('/') or ':' in name or '\\' in name or any(x in ('','..','.') for x in name.split('/')):
            raise ValueError(f'Unsafe Hydro attachment reference: {raw}')
        rel='additional_file/'+name
        if rel not in present:
            raise ValueError(f'Missing attachment or filename case mismatch: {raw}; expected {rel}')
        references.append(rel)
    # Ordinary inline image syntax: reject machine paths / relative image paths.
    # More complex Markdown reference definitions still need manual review.
    inline=re.findall(r'!\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)\n]+))',statement)
    urls=[a or b for a,b in inline]
    urls+=re.findall(r'''<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["']''',statement,flags=re.I)
    external=[]
    for url in urls:
        if url.lower().startswith('file://'):continue
        if url.lower().startswith(('http://','https://','data:')) or url.startswith('//'):
            external.append(url.split(':',1)[0] if url.lower().startswith('data:') else url)
        else:raise ValueError(f'Use a Hydro file:// attachment reference for local image: {url}')
    return sorted(set(references)),external

def build(root, output, sources=(), expected_inputs=50):
    root=Path(root)
    if root.is_symlink():raise ValueError('Problem root must not be a symbolic link')
    root=root.resolve();output=Path(output).resolve()
    if not root.is_dir() or not re.fullmatch(r'[0-9]+',root.name):
        raise ValueError('Root must be an existing numeric problem folder, e.g. hydro/1')
    if output.is_relative_to(root):raise ValueError('Output ZIP must be outside the problem folder')
    allowed={'problem.yaml','problem_zh.md','testdata/config.yaml'}
    for raw in sources:
        raw=raw.replace('\\','/')
        if not raw or raw.startswith('/') or ':' in raw or any(x in ('','..','.') for x in raw.split('/')):
            raise ValueError(f'Unsafe judge-source path: {raw}')
        if Path(raw).suffix.lower() not in ('.cpp','.cc','.c','.cxx','.h','.hpp','.py','.rs','.java'):
            raise ValueError(f'Unexpected judge-source extension: {raw}')
        allowed.add('testdata/'+raw)
    files=[];present=set();inputs=answers=images=0
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError(f'Symbolic link is not allowed: {p}')
        if not p.is_file():continue
        rel=p.relative_to(root).as_posix()
        if rel in allowed:pass
        elif re.fullmatch(r'testdata/[^/.][^/]*\.(in|out|ans)',rel):
            if rel.endswith('.in'):inputs+=1
            else:answers+=1
        elif rel.startswith('additional_file/') and p.suffix.lower() in IMAGE_EXTENSIONS:
            if not p.stat().st_size:raise ValueError(f'Empty image attachment: {rel}')
            images+=1
        else:
            raise ValueError(f'Unexpected file {rel}; move author material outside the import root, or explicitly include a required judge source')
        if rel in ('problem.yaml','problem_zh.md','testdata/config.yaml'):
            if not p.read_text(encoding='utf-8-sig').strip():raise ValueError(f'Empty text file: {rel}')
        present.add(rel);files.append(p)
    missing=allowed-present
    if missing:raise ValueError('Missing files: '+', '.join(sorted(missing)))
    if not inputs or not answers:raise ValueError('Need input and answer files; shared answer files are allowed')
    if inputs != expected_inputs:
        raise ValueError(f'Expected {expected_inputs} input files, found {inputs}; user default is 50 test cases')
    image_refs,external_images=check_statement_images((root/'problem_zh.md').read_text(encoding='utf-8-sig'),present)
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:z.write(p,root.name+'/'+p.relative_to(root).as_posix())
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC check failed')
        names=z.namelist()
        if any(not name.startswith(root.name+'/') or '..' in name.split('/') for name in names):
            raise ValueError('Archive path verification failed')
    return {'files':len(files),'input_files':inputs,'answer_files':answers,
            'image_files':images,'referenced_attachments':image_refs,
            'external_images_needing_review':external_images,
            'bytes':output.stat().st_size,'output':str(output),
            'scope':'Structural packaging only; YAML references, score and judging behavior must be checked separately.'}

def main():
    import json
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--judge-source',action='append',default=[])
    ap.add_argument('--expected-inputs',type=int,default=50,help='Default is the user\'s 50-case convention; override only for an explicitly different request')
    a=ap.parse_args()
    try:result=build(a.root,a.output,a.judge_source,a.expected_inputs)
    except (ValueError,OSError,UnicodeError,zipfile.BadZipFile) as e:
        print('ERROR:',e,file=sys.stderr);return 1
    print(json.dumps(result,ensure_ascii=True,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
