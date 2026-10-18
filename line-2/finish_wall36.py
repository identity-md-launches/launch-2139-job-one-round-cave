"""Retain generated pigment only on unused rock, then create the required preview."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

spec = importlib.util.spec_from_file_location('png36', 'gathering/finish_wall.py')
png = importlib.util.module_from_spec(spec)
spec.loader.exec_module(png)
old = Path('artifacts/line-2/wall-v15.png')
out = Path('artifacts/line-2/wall-v16.png')
w, h, ancestor = png.read_png(old)
dw, dh, draft = png.read_png(out)
assert (w, h) == (dw, dh) == (1254, 1254)
assert hashlib.sha256(old.read_bytes()).hexdigest() == '8716d19560c0ce3a40baef2c907c3421865ab2791971230967024ef1e6b9f41b'
final = ancestor[:]
rect = (340, 905, 90, 95)
for y in range(rect[1], rect[1] + rect[3]):
    for x in range(rect[0], rect[0] + rect[2]):
        i = (y*w+x)*3
        r, g, b = draft[i:i+3]
        chalk = any((x-cx)**2+(y-cy)**2 < 10**2 for cx, cy in ((378,943),(409,974)))
        curve = 380 < x < 409 and 940 < y < 976
        ellipse = ((x-384)/32)**2 + ((y-953)/37)**2
        alpha = 0
        if chalk and r > 145 and g > 130 and b > 100 and r-g < 55:
            alpha = .87
        elif curve and r < 85 and g < 65 and b < 55:
            alpha = .83
        elif .68 < ellipse < 1.4 and r > 1.65*g and r > 2*b and g < 105:
            alpha = .85
        if alpha:
            for c in range(3):
                final[i+c] = round(ancestor[i+c]*(1-alpha) + draft[i+c]*alpha)
changed = [i for i in range(w*h) if ancestor[3*i:3*i+3] != final[3*i:3*i+3]]
assert len(changed) > 300
assert all(rect[0] <= i%w < rect[0]+rect[2] and rect[1] <= i//w < rect[1]+rect[3] for i in changed)
digest = png.write_png(out,w,h,final)
wall = Path('artifacts/line-2/wall.png')
wall.unlink()
wall.symlink_to('wall-v16.png')
rgba = bytearray()
for y in range(512):
    ya,yb=y*h//512,(y+1)*h//512
    for x in range(512):
        xa,xb=x*w//512,(x+1)*w//512
        n=(yb-ya)*(xb-xa)
        for c in range(3):
            rgba.append(round(sum(final[(sy*w+sx)*3+c] for sy in range(ya,yb) for sx in range(xa,xb))/n))
        rgba.append(255)
subprocess.run(['node','-e',"const fs=require('fs');const enc=require('./line-3/tools/corpus-change-receipt/vendor/jpeg-js/lib/encoder.js');const r=enc({data:fs.readFileSync(0),width:512,height:512},78);if(r.data.length>100000)throw Error('preview too large');fs.writeFileSync('dist/line-2/36.jpg',r.data);"],input=rgba,check=True)
review = {'round':36,'ancestorSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'wallSha256':digest,
          'dimensions':[w,h],'format':'PNG','channels':'RGB','newMarkRectangle':list(rect),
          'changedPixels':len(changed),'changedPixelsOutsideRectangle':0,
          'method':'Built-in imagegen edit of inherited wall; selected only new chalk, charcoal and ochre pigment within bare-rock rectangle; all other pixels copied from ancestor.',
          'visualReview':'Two chalk dots with a curved charcoal link and broken ochre arc. Existing Pepe, two five-digit hands, ancestor pigment, rock, light, crystals and framing preserved. No added hands, letters or numbers.',
          'unmetVisualRequirements':[], 'preview':{'path':'dist/line-2/36.jpg','format':'JPEG','dimensions':[512,512],'bytes':Path('dist/line-2/36.jpg').stat().st_size}}
Path('line-2/REVIEW-36.json').write_text(json.dumps(review,indent=2)+'\n')
record={'name':'The Proof Revisited','image':'https://api.imd.fun/artifacts/'+digest,'attributes':[
{'trait_type':'Cave','value':'Crystal'}, {'trait_type':'Wall','value':'Line 2'}, {'trait_type':'Number','value':36},
{'trait_type':'Left behind','value':'Receipt Audit'},
{'trait_type':'Meaning','value':'Two linked chalk dots return a saved claim to its proven source.'},
{'trait_type':'One thing','value':'Verify Ethereum account and storage proofs against trusted state roots'}]}
assert not Path('dist/line-2/36.json').exists()
Path('dist/line-2/36.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(review,indent=2))
