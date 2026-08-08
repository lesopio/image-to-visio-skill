#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path

def run(cmd):
    print('+',' '.join(map(str,cmd)))
    subprocess.run(cmd,check=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('vsdx')
    ap.add_argument('--page',type=int,default=2)
    ap.add_argument('--dpi',type=int,default=100)
    ap.add_argument('--outdir',default='qa_out')
    ap.add_argument('--src-min',type=float,default=0.0)
    ap.add_argument('--render-min',type=float,default=0.0)
    args=ap.parse_args()
    out=Path(args.outdir).resolve(); out.mkdir(parents=True,exist_ok=True)
    here=Path(__file__).resolve().parent
    run([sys.executable,str(here/'preflight_vsdx.py'),args.vsdx,'--editable-page',str(args.page)])
    soffice=shutil.which('soffice') or shutil.which('libreoffice')
    if not soffice: raise SystemExit('LibreOffice/soffice not found')
    pdftoppm=shutil.which('pdftoppm')
    if not pdftoppm: raise SystemExit('pdftoppm not found')
    run([soffice,'--headless','--convert-to','pdf','--outdir',str(out),str(Path(args.vsdx).resolve())])
    pdf=out/(Path(args.vsdx).stem+'.pdf')
    if not pdf.exists(): raise SystemExit(f'PDF not produced: {pdf}')
    prefix=out/'rendered_page'
    run([pdftoppm,'-f',str(args.page),'-singlefile','-r',str(args.dpi),'-png',str(pdf),str(prefix)])
    rendered=Path(str(prefix)+'.png')
    run([sys.executable,str(here/'verify_pixel_match.py'),args.source,str(rendered),'--src-min',str(args.src_min),'--render-min',str(args.render_min),'--outdir',str(out)])
    print('QA complete:',out)

if __name__=='__main__': main()
