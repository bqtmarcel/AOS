"""Erzeugt die App-Symbole: „AOS“ in Chrom, im O das rote Red-Tigers-T (img/t.png).
Aufruf: python3 tools/make-icons.py  (aus dem Repo-Hauptordner)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import math
FONT='/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
S=1024

def bg():
    im=Image.new('RGB',(S,S),(0,0,0)); px=im.load()
    for y in range(S):
        for x in range(S):
            d=math.hypot(x-S/2,y-S*0.48)/(S*0.62); k=max(0.0,1-d)**1.6
            line=0.92 if (y//6)%2 else 1.0
            px[x,y]=(int((10+80*k)*line),int((6+4*k)*line),int((8+4*k)*line))
    return im

def chrome(h):
    stops=[(0,(255,255,255)),(.40,(227,231,236)),(.52,(127,134,146)),(.70,(201,206,214)),(1,(245,247,249))]
    g=Image.new('RGB',(1,h))
    for y in range(h):
        t=y/(h-1)
        for (a,ca),(b,cb) in zip(stops,stops[1:]):
            if a<=t<=b: f=(t-a)/(b-a); g.putpixel((0,y),tuple(int(ca[i]+(cb[i]-ca[i])*f) for i in range(3))); break
    return g

def build(scale):
    """scale: Anteil der Breite, die der Schriftzug einnimmt (maskable kleiner)."""
    im=bg().convert('RGBA')
    font=ImageFont.truetype(FONT,400)
    cap=font.getbbox('A')[3]-font.getbbox('A')[1]
    wA=font.getlength('A'); wS=font.getlength('S'); oD=cap*1.02; gap=cap*0.10
    total=wA+gap+oD+gap+wS; f=S*scale/total
    font=ImageFont.truetype(FONT,int(400*f)); cap*=f; wA*=f; wS*=f; oD*=f; gap*=f
    top=font.getbbox('A')[1]; y0=(S-cap)/2; x=(S-(wA+gap+oD+gap+wS))/2
    mask=Image.new('L',(S,S),0); d=ImageDraw.Draw(mask)
    d.text((x,y0-top),'A',font=font,fill=255)
    cx=x+wA+gap+oD/2; cy=y0+cap/2; r=oD/2; th=cap*0.17
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=255); d.ellipse([cx-r+th,cy-r+th,cx+r-th,cy+r-th],fill=0)
    d.text((x+wA+gap+oD+gap,y0-top),'S',font=font,fill=255)
    # Schatten + Chrom
    sh=Image.new('RGBA',(S,S),(0,0,0,0)); sh.putalpha(mask.filter(ImageFilter.GaussianBlur(6)).point(lambda v:int(v*.7)))
    im.alpha_composite(sh,(0,4))
    g=chrome(int(cap)).resize((S,int(cap))); fill=Image.new('RGB',(S,S),(245,247,249)); fill.paste(g,(0,int(y0)))
    layer=fill.convert('RGBA'); layer.putalpha(mask); im.alpha_composite(layer)
    # rotes T im O mit Glühen
    t=Image.open('img/t.png').convert('RGBA'); inner=(r-th)*2; tw=int(inner*0.84)
    t=t.resize((tw,int(tw*t.height/t.width)),Image.LANCZOS)
    glow=Image.new('RGBA',(S,S),(0,0,0,0)); ga=Image.new('L',(S,S),0)
    ga.paste(t.getchannel('A'),(int(cx-t.width/2),int(cy-t.height/2))); ga=ga.filter(ImageFilter.GaussianBlur(int(cap*0.08)))
    glow=Image.new('RGBA',(S,S),(246,1,0,0)); glow.putalpha(ga.point(lambda v:int(v*.85))); im.alpha_composite(glow)
    im.alpha_composite(t,(int(cx-t.width/2),int(cy-t.height/2)))
    return im.convert('RGB')

full=build(0.80); safe=build(0.62)
full.resize((512,512),Image.LANCZOS).save('icon-512.png')
full.resize((192,192),Image.LANCZOS).save('icon-192.png')
full.resize((180,180),Image.LANCZOS).save('apple-touch-icon.png')
safe.resize((512,512),Image.LANCZOS).save('icon-maskable-512.png')
print('ok')
