#!/usr/bin/env python3
import argparse, posixpath, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
VISIO_NS = 'http://schemas.microsoft.com/office/visio/2012/main'

REQUIRED = [
    '[Content_Types].xml', '_rels/.rels',
    'visio/document.xml', 'visio/_rels/document.xml.rels',
    'visio/pages/pages.xml', 'visio/pages/_rels/pages.xml.rels',
]

def resolve_target(rels_name, target):
    if target.startswith('/'):
        return target.lstrip('/')
    base = posixpath.dirname(posixpath.dirname(rels_name))
    return posixpath.normpath(posixpath.join(base, target))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('vsdx')
    ap.add_argument('--editable-page', type=int, default=2)
    ap.add_argument('--max-foreign-area', type=float, default=0.92)
    args=ap.parse_args()
    p=Path(args.vsdx)
    errors=[]; warnings=[]

    try:
        with zipfile.ZipFile(p) as z:
            bad=z.testzip()
            if bad: errors.append(f'ZIP CRC failure: {bad}')
            names=set(z.namelist())
            for r in REQUIRED:
                if r not in names: errors.append(f'Missing required part: {r}')
            # Parse all XML and relationships.
            for n in names:
                if n.endswith('.xml') or n.endswith('.rels'):
                    try: ET.fromstring(z.read(n))
                    except Exception as e: errors.append(f'Invalid XML {n}: {e}')
            # Validate internal relationships.
            for n in names:
                if not n.endswith('.rels'): continue
                try: root=ET.fromstring(z.read(n))
                except Exception: continue
                for rel in root.findall(f'{{{REL_NS}}}Relationship'):
                    if rel.get('TargetMode') == 'External': continue
                    target=resolve_target(n, rel.get('Target',''))
                    if target not in names:
                        errors.append(f'Broken relationship: {n} -> {target}')
            page=f'visio/pages/page{args.editable_page}.xml'
            if page not in names:
                errors.append(f'Editable page not found: {page}')
            else:
                root=ET.fromstring(z.read(page))
                ns={'v':VISIO_NS}
                # Detect page-sized Foreign shapes where geometry is explicit.
                def cell(shape, name):
                    c=shape.find(f"v:Cell[@N='{name}']",ns)
                    return float(c.get('V')) if c is not None and c.get('V') else None
                ps=root.find('v:PageSheet',ns)
                pw=ph=None
                if ps is not None:
                    for name in ('PageWidth','PageHeight'):
                        c=ps.find(f"v:Cell[@N='{name}']",ns)
                        if c is not None and c.get('V'):
                            if name=='PageWidth': pw=float(c.get('V'))
                            else: ph=float(c.get('V'))
                if pw and ph:
                    page_area=pw*ph
                    for s in root.findall('.//v:Shape',ns):
                        if s.find('v:ForeignData',ns) is None: continue
                        w,h=cell(s,'Width'),cell(s,'Height')
                        if w and h and (w*h/page_area) > args.max_foreign_area:
                            errors.append(f'Editable page contains near-full-page Foreign image: shape {s.get("ID")} area={(w*h/page_area):.3f}')
    except Exception as e:
        errors.append(f'Cannot open VSDX: {e}')

    if errors:
        print('FAIL')
        for e in errors: print('ERROR:',e)
        for w in warnings: print('WARN:',w)
        raise SystemExit(1)
    print('PASS')
    print(f'VSDX preflight OK: {p}')

if __name__=='__main__': main()
