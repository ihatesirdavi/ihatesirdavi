"""Compose a GitHub profile hero from published, tested visual preview captures.

This is a deterministic Pillow composition of owner-controlled public source images,
not an AI-generated banner and NOT a reproduction of the unavailable original logo.
GIF animation runs for a finite count and rests on its final frame.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = (1600, 470)
PALETTE = {
    "bg":(13,13,17), "surface":(41,40,48),
    "ink":(245,242,238), "primary":(201,189,207),
    "secondary":(140,116,145), "accent":(184,124,85)
}
FONTS = {
    "head":[
        "C:/Windows/Fonts/georgiab.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "body":[
        "C:/Windows/Fonts/seguisb.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "small":[
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mono":[
        "C:/Windows/Fonts/consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
}
def font(name,size):
    for path in FONTS[name]:
        if Path(path).is_file():
            return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def rounded_preview(file, crop, size, name):
    source=Image.open(ASSETS / file).convert("RGB")
    tile=source.crop(crop).resize(size,Image.Resampling.LANCZOS)
    # Vignette the source, keeping the authentic rendered image center visible.
    shade=Image.new("RGBA",size,(12,12,18,0))
    sd=ImageDraw.Draw(shade)
    sd.rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=16,outline=(160,154,171,160),width=2)
    overlay=Image.new("RGBA",size,(0,0,0,0))
    od=ImageDraw.Draw(overlay)
    od.rounded_rectangle((0,0,size[0],43),radius=13,fill=(13,14,20,216))
    od.text((18,13),name,font=font("mono",17),fill=(223,225,227,255))
    tile=Image.alpha_composite(tile.convert("RGBA"),shade)
    tile=Image.alpha_composite(tile,overlay)
    mask=Image.new("L",size,0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=16,fill=255)
    tile.putalpha(mask)
    return tile

def backdrop():
    w,h=SIZE
    im=Image.new("RGB",SIZE,PALETTE["bg"])
    pixels=im.load()
    for y in range(h):
        for x in range(w):
            # Restrained plum light around the identity and soft violet at right.
            k1=max(0,1-math.hypot((x-580)/1120,(y+80)/610))
            k2=max(0,1-math.hypot((x-1460)/810,(y-170)/690))
            pixels[x,y]=(int(13+12*k1+10*k2),int(13+7*k1+7*k2),int(17+17*k1+18*k2))
    return im.convert("RGBA")

def base_frame():
    im=backdrop()
    d=ImageDraw.Draw(im)
    ink=PALETTE["ink"];soft=PALETTE["primary"];accent=PALETTE["accent"]
    # Three diagonal motifs from creator source-direction, geometry not a copied logo.
    for i in range(3):
        x=57+i*9
        d.line((x,82,x+26,49),fill=(192,158,138,140),width=3)
    d.text((110,46),"RECORDING ARTIST  /  MUSIC PRODUCER  /  CREATIVE TECHNOLOGIST",
           fill=(211,201,210),font=font("mono",20))
    d.text((85,99),"Sir Davi",fill=ink,font=font("head",111))
    d.text((91,241),"Music is where I learned",fill=soft,font=font("body",34))
    d.text((91,286),"to build systems.",fill=ink,font=font("body",41))
    d.text((94,346),"ARRANGEMENT  /  SIGNAL FLOW  /  TIMING  /  ITERATION",
           fill=(209,170,139),font=font("mono",19))
    d.text((92,388),"\u201cI code sometimes\u2026\u201d",fill=(173,156,176),font=font("small",20))
    # Source-backed real user-owned Chrome capture panels.
    tile1=rounded_preview("hero-source-signal.png",(0,420,1365,960),(600,178),"SIGNAL-001  /  VISUAL INTERACTION")
    tile2=rounded_preview("hero-source-dynamics.png",(0,490,1365,1030),(600,178),"DYNAMICS-002  /  PHYSICS")
    im.alpha_composite(tile1,(943,49))
    im.alpha_composite(tile2,(943,239))
    d=ImageDraw.Draw(im)
    d.line((906,51,906,409),fill=(160,127,158,100),width=2)
    # Studio sequencing lanes, subordinate to the actual visual work.
    for row in range(3):
        y=435+row*8
        d.line((90,y,845,y),fill=(76,68,83,190),width=1)
        for seg in range(13):
            x=98+seg*54
            if (row+seg)%4!=0:
                d.rounded_rectangle((x,y-2,x+24+(seg%3)*7,y+2),radius=2,
                    fill=(118+row*15,88+seg%4*5,111+row*8,160))
    return im

def compose():
    base=base_frame()
    # Keep PNG fully legible as reduced-motion / sharp fallback.
    poster=base.convert("RGB")
    png=ASSETS / "hero-music-systems.png"
    poster.save(png,format="PNG",optimize=True)
    # Add a finite motion trace in the low-priority bottom 16px strip only.
    frames=[]
    n=18
    for index in range(n):
        frame=base.copy()
        layer=Image.new("RGBA",SIZE,(0,0,0,0))
        draw=ImageDraw.Draw(layer)
        pts=[]
        for x in range(920,1555,5):
            phase=(x-920)/55-index*.55
            envelope=(0.25+0.75*abs(math.sin((x-920)/635*math.pi)))
            y=448+4.8*math.sin(phase)*envelope
            pts.append((x,int(y)))
        draw.line(pts,fill=(210,156,121,175),width=2)
        frame=Image.alpha_composite(frame,layer)
        frames.append(frame.convert("RGB").quantize(colors=96,method=Image.Quantize.FASTOCTREE))
    # 18*140ms, at most 2 total cycles, then the animation stops.
    gif=ASSETS / "hero-music-systems.gif"
    frames[0].save(gif,save_all=True,append_images=frames[1:],
        duration=140,loop=1,optimize=True,disposal=2)
    print(f"PNG {png.stat().st_size} bytes; GIF {gif.stat().st_size} bytes")
    print("Source captures were local, previously published Preview Lab images.")

if __name__ == "__main__":
    compose()