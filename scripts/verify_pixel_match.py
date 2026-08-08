#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageChops, ImageEnhance

def ink_mask(img, threshold=235):
    a=np.asarray(ImageOps.grayscale(img))
    return a < threshold

def dilate1(mask):
    out=np.zeros_like(mask,dtype=bool)
    h,w=mask.shape
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            ys=slice(max(0,dy), min(h,h+dy))
            xs=slice(max(0,dx), min(w,w+dx))
            yd=slice(max(0,-dy), min(h,h-dy))
            xd=slice(max(0,-dx), min(w,w-dx))
            out[yd,xd] |= mask[ys,xs]
    return out

def ratio(a,b_dilated):
    denom=int(a.sum())
    return float((a & b_dilated).sum()/denom) if denom else 1.0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source'); ap.add_argument('rendered')
    ap.add_argument('--threshold',type=int,default=235)
    ap.add_argument('--src-min',type=float,default=0.0)
    ap.add_argument('--render-min',type=float,default=0.0)
    ap.add_argument('--outdir',default='qa_out')
    args=ap.parse_args()
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    s=Image.open(args.source).convert('RGB'); r=Image.open(args.rendered).convert('RGB')
    if s.size != r.size:
        raise SystemExit(f'SIZE_MISMATCH source={s.size} rendered={r.size}')
    sm=ink_mask(s,args.threshold); rm=ink_mask(r,args.threshold)
    sr=ratio(sm,dilate1(rm)); rs=ratio(rm,dilate1(sm))
    exact=float(np.mean(np.all(np.asarray(s)==np.asarray(r),axis=2)))
    report={
        'size': list(s.size),
        'source_ink_match_1px': sr,
        'render_ink_match_1px': rs,
        'exact_rgb_pixel_ratio': exact,
        'threshold': args.threshold,
    }
    (out/'pixel_match_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'pixel_match_report.txt').write_text('\n'.join(f'{k}: {v}' for k,v in report.items()),encoding='utf-8')
    side=Image.new('RGB',(s.width*2,s.height),'white'); side.paste(s,(0,0)); side.paste(r,(s.width,0)); side.save(out/'side_by_side.png')
    diff=ImageChops.difference(s,r)
    diff=ImageEnhance.Contrast(diff).enhance(4)
    diff=diff.resize((diff.width*4,diff.height*4),Image.Resampling.NEAREST)
    diff.save(out/'diff_x4.png')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if sr < args.src_min or rs < args.render_min:
        raise SystemExit(2)

if __name__=='__main__': main()
