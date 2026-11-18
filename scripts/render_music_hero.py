"""Sir Davi profile hero: music-led editorial, with systems in the construction.

Original programmatic art, never a screenshot or substituted owner logo.
An abstract multitrack music session expresses the same timing, automation,
modularity and iteration principles used in interactive systems design.
No literal audio-to-code wires, fake technical dashboards or private assets.
"""
from __future__ import annotations
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"assets"
SIZE=(1600,470)
PI=math.pi
FONTS={
    "display": ["C:/Windows/Fonts/georgiab.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
    "head": ["C:/Windows/Fonts/seguisb.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "body": ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "mono": ["C:/Windows/Fonts/consola.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
}
INK=(245,240,235)
MUTED=(199,189,197)
COPPER=(222,153,113)
MAUVE=(172,138,183)
COOL=(119,190,188)
LEFT_MAX=625
VISUAL_START=680

def font(kind,size):
    for name in FONTS[kind]:
        if Path(name).is_file():
            return ImageFont.truetype(name,size)
    return ImageFont.load_default()

def signal_samples(phase:float)->tuple[float,...]:
    """Deterministic synthetic layered audio; never represented as a real song."""
    values=[]
    for i in range(480):
        beat=i/480
        envelope=(0.18+0.82*abs(math.sin(PI*(beat*3.7+0.13)))**1.4)
        carrier=(0.49*math.sin(i*0.58+phase)
                 +0.26*math.sin(i*1.23+phase*0.64)
                 +0.17*math.sin(i*2.03+phase*0.32))
        values.append(max(-1.0,min(1.0,envelope*carrier)))
    return tuple(values)

def automation_curve()->tuple[float,...]:
    """Smooth envelope derived from keyframed control points, not a route."""
    keys=((0.,0.16),(.19,.40),(.39,.27),(.61,.77),(.79,.62),(1.,.85))
    result=[]
    for i in range(301):
        t=i/300
        for a,b in zip(keys,keys[1:]):
            if a[0]<=t<=b[0]:
                u=(t-a[0])/(b[0]-a[0])
                u=u*u*(3-2*u)
                result.append(a[1]*(1-u)+b[1]*u)
                break
    return tuple(result)

def backdrop():
    # Sparse background grading. No faux app window, or heavy sci-fi grid.
    w,h=SIZE
    im=Image.new("RGB",SIZE,(14,14,19))
    px=im.load()
    for y in range(h):
        for x in range(w):
            g=max(0.,1.-math.hypot((x-1210)/970,(y-240)/520))
            left=max(0.,1.-math.hypot((x-170)/930,(y+130)/760))
            px[x,y]=(int(14+13*g+4*left),int(14+8*g+3*left),int(19+16*g+7*left))
    return im.convert("RGBA")

def draw_arrangement(layer):
    """Timeline ruler and muted notes imply signal structure, not fake UI."""
    d=ImageDraw.Draw(layer)
    left,right=VISUAL_START,1552
    # Editorial header and underline.
    d.text((left+3,54),"SOUND    /    STRUCTURE    /    RESPONSE",
           font=font("mono",18),fill=(213,198,205,225))
    d.line((left,90,right,90),fill=(202,179,184,95),width=1)
    d.line((left,427,right,427),fill=(202,179,184,65),width=1)
    for k in range(21):
        x=left+k*43
        c=(148,130,149,40) if k%4 else (166,139,151,85)
        d.line((x,112,x,418),fill=c,width=1)
        if k%4==0:
            d.text((x+5,96),f"{(k//4+1):02d}",font=font("mono",11),
                   fill=(170,160,170,135))
    for y in (139,227,313,416):
        d.line((left,y,right,y),fill=(168,147,157,48),width=1)
    d.text((left+5,125),"WAVE",font=font("mono",13),fill=(209,169,151,215))
    d.text((left+5,236),"ARRANGE",font=font("mono",13),fill=(182,161,198,210))
    d.text((left+5,333),"AUTOMATE",font=font("mono",13),fill=(153,200,195,210))
    # Multitrack regions. Deterministic and visually subordinate to the signal.
    x0=left+96
    track_colors=((191,141,171),(127,158,174),(178,127,134))
    for lane in range(3):
        for i in range(16):
            if (i+2*lane)%5==0:continue
            start=x0+i*46+((i*3+lane*7)%9)
            end=min(right-14,start+19+(i*7+lane*11)%27)
            y=254+lane*18+((i+lane)%2)*3
            d.rounded_rectangle((start,y,end,y+7),radius=3,
                fill=(*track_colors[lane],130 if lane else 177))
    # A short boundary marker says this is a designed graphic, not live measurements.
    d.text((left+6,443),"COMPOSITION  /  PROCESS  /  INTERACTION",
           font=font("mono",14),fill=(177,168,178,195))

def draw_signal(layer,phase=0.):
    """Waveform visualization held inside its own musical lane."""
    d=ImageDraw.Draw(layer)
    values=signal_samples(phase)
    left,right=780,1522
    center=183
    n=len(values)
    # Underlay showing signal envelope; not a cable or connector.
    d.line((left,center,right,center),fill=(188,154,147,91),width=1)
    for i,signal in enumerate(values):
        x=left+(right-left)*i/(n-1)
        amp=7+46*abs(signal)
        d.line((x,center-amp,x,center+amp),
            fill=(231,165,127,218 if i%3 else 237),width=2)
    d.line((left,center-62,right,center-62),fill=(180,139,134,30),width=1)
    d.line((left,center+62,right,center+62),fill=(180,139,134,30),width=1)

def draw_automation(layer,phase=0.):
    """Independent keyframed automation, visibly part of the same session grid."""
    d=ImageDraw.Draw(layer)
    env=automation_curve()
    left,right=780,1522
    curve=[]
    for i,val in enumerate(env):
        x=left+(right-left)*i/(len(env)-1)
        y=401-48*val+1.1*math.sin(phase+i*.024)
        curve.append((round(x),round(y)))
    d.line(curve,fill=(*COOL,226),width=3,joint="curve")
    # A few keyframe anchors, like a producer's automation pass.
    for ratio in (.0,.19,.39,.61,.79,1.):
        j=int(round(ratio*300))
        x,y=curve[j]
        d.ellipse((x-4,y-4,x+4,y+4),fill=(17,27,31,255),
                  outline=(*COOL,235),width=2)

def typography(layer):
    """Music credentials and creative identity lead; no fabricated logo."""
    d=ImageDraw.Draw(layer)
    d.text((82,49),"RECORDING ARTIST    /    MUSIC PRODUCER",
           font=font("mono",18),fill=(221,206,216,240))
    d.text((78,101),"Sir Davi",font=font("display",101),fill=(*INK,255))
    d.text((84,244),"Music, media & systems.",font=font("head",32),
           fill=(239,225,232,250))
    d.text((86,299),"Built through sound, structure",font=font("body",22),
           fill=(201,188,201,243))
    d.text((86,330),"and experimentation.",font=font("body",22),
           fill=(201,188,201,243))
    d.line((86,379,409,379),fill=(196,153,133,103),width=1)
    d.text((87,390),"\u201cI code sometimes\u2026\u201d",font=font("body",18),
           fill=(170,155,178,216))

# Reuse a cached background so frames remain reproducible and inexpensive.
_BACKGROUND=None
def frame(phase=0.):
    global _BACKGROUND
    if _BACKGROUND is None:_BACKGROUND=backdrop()
    canvas=_BACKGROUND.copy()
    visuals=Image.new("RGBA",SIZE,(0,0,0,0))
    draw_arrangement(visuals)
    draw_signal(visuals,phase)
    draw_automation(visuals,phase)
    canvas.alpha_composite(visuals)
    typography(canvas)
    return canvas

def compose():
    ASSETS.mkdir(parents=True,exist_ok=True)
    png=ASSETS/"hero-music-systems.png"
    frame(0).convert("RGB").save(png,format="PNG",optimize=True)
    frames=[]
    for k in range(18):
        phase=2*PI*k/18
        frames.append(frame(phase).convert("RGB").quantize(
            colors=96,method=Image.Quantize.FASTOCTREE))
    gif=ASSETS/"hero-music-systems.gif"
    frames[0].save(gif,save_all=True,append_images=frames[1:],
                   duration=140,loop=1,optimize=True,disposal=2)
    print("EDITORIAL_BANNER_PNG_BYTES",png.stat().st_size)
    print("EDITORIAL_BANNER_GIF_BYTES",gif.stat().st_size)

if __name__=="__main__":
    compose()