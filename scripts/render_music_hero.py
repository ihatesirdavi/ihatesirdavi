"""A single music-to-systems visual composition for the Sir Davi GitHub hero.

All marks are rendered from original geometry. One continuous graphic carries
a synthetic audio signal into a signal-routing graph and a deterministic
three-body orbit. No screenshots, fake logos, or private project source.
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = (1600, 470)
PI = math.pi
PALETTE = {
    "bg": (13, 13, 17), "surface": (41, 40, 48),
    "ink": (245, 242, 238), "primary": (201, 189, 207),
    "secondary": (140, 116, 145), "accent": (184, 124, 85),
    "signal": (220, 161, 113), "route": (173, 140, 191),
    "orbit": (114, 199, 195)
}
FONTS = {
    "head": ["C:/Windows/Fonts/georgiab.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
    "body": ["C:/Windows/Fonts/seguisb.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "small": ["C:/Windows/Fonts/segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "mono": ["C:/Windows/Fonts/consola.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
}

def font(name: str, size: int):
    for path in FONTS[name]:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def signal_samples(phase: float) -> tuple[float, ...]:
    """Deterministic synthetic arrangement-shaped audio amplitude, not a recording."""
    values = []
    for i in range(360):
        beat = i / 360.0
        envelope = (0.30 + 0.70 * abs(math.sin(PI * beat * 5.0)) ** 2)
        harmonics = (
            .48 * math.sin(i * .39 + phase) +
            .30 * math.sin(i * .91 + phase * .67) +
            .15 * math.sin(i * 1.67 + phase * .29)
        )
        values.append(max(-1.0, min(1.0, harmonics * envelope)))
    return tuple(values)

def orbital_paths() -> tuple[tuple[tuple[float,float], ...], ...]:
    """Plummer-softened velocity-Verlet, same public educational figure-eight setup."""
    bodies = [
        [1., .97000436, -.24308753, .466203685, .43236573],
        [1., -.97000436, .24308753, .466203685, .43236573],
        [1., 0., 0., -.93240737, -.86473146],
    ]
    dt, soften = .006, .025
    paths = [[], [], []]
    def acceleration():
        a = [[0., 0.] for _ in bodies]
        for i in range(3):
            for j in range(i+1, 3):
                dx = bodies[j][1]-bodies[i][1]
                dy = bodies[j][2]-bodies[i][2]
                inverse = (dx*dx+dy*dy+soften*soften) ** -1.5
                a[i][0] += bodies[j][0]*dx*inverse
                a[i][1] += bodies[j][0]*dy*inverse
                a[j][0] -= bodies[i][0]*dx*inverse
                a[j][1] -= bodies[i][0]*dy*inverse
        return a
    for k in range(1800):
        if k % 8 == 0:
            for i, b in enumerate(bodies):
                paths[i].append((round(b[1], 6), round(b[2], 6)))
        a = acceleration()
        for i, b in enumerate(bodies):
            b[1] += b[3]*dt + .5*a[i][0]*dt*dt
            b[2] += b[4]*dt + .5*a[i][1]*dt*dt
        next_a = acceleration()
        for i, b in enumerate(bodies):
            b[3] += .5 * (a[i][0]+next_a[i][0])*dt
            b[4] += .5 * (a[i][1]+next_a[i][1])*dt
    return tuple(tuple(path) for path in paths)

def backdrop():
    im = Image.new("RGB", SIZE, PALETTE["bg"])
    pix = im.load()
    w, h = SIZE
    for y in range(h):
        for x in range(w):
            # Fine low-contrast grading, no fake space photograph.
            v = max(0., 1. - math.hypot((x-1250)/920, (y-255)/500))
            a = max(0., 1. - math.hypot((x-280)/1050, (y+150)/820))
            pix[x,y] = (int(13+14*v+5*a), int(13+6*v+4*a), int(17+19*v+8*a))
    return im.convert("RGBA")

def ink_line(draw, pts, fill, width=1, joint="curve"):
    draw.line([(int(x), int(y)) for x,y in pts], fill=fill, width=width, joint=joint)

def glow_dot(layer, x, y, color, radius=5):
    x,y=int(x),int(y)
    bloom=Image.new("RGBA",SIZE,(0,0,0,0))
    b=ImageDraw.Draw(bloom)
    for r, alpha in ((radius*4,9),(radius*3,18),(radius*2,38)):
        b.ellipse((x-r,y-r,x+r,y+r),fill=(*color,alpha))
    layer.alpha_composite(bloom)
    d=ImageDraw.Draw(layer)
    d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*color,230))
    d.ellipse((x-radius*.40,y-radius*.40,x+radius*.40,y+radius*.40),fill=(250,240,229,236))

def draw_signal_flow(layer, phase=0.):
    """Arrangement lanes morph into one waveform and later into the routing graph."""
    d=ImageDraw.Draw(layer)
    x0,x1=618,981
    # Muted beat and measure grid, rather than screenshot panels.
    for k in range(16):
        x=x0+k*24
        d.line((x,275,x,433),fill=(160,136,162,35 if k%4 else 70),width=1)
    for y in (296,335,375,412):
        d.line((x0,y,x1,y),fill=(132,119,139,38),width=1)
    # Piano-roll / arrangement blocks, logically tied to the waveform clock.
    for lane in range(3):
        for i in range(11):
            if (i*3+lane)%4 == 1: continue
            x=627+i*30+lane*4
            y=375+lane*17-(i%3)*4
            length=13+(i*7+lane*3)%20
            d.rounded_rectangle((x,y,x+length,y+5),radius=2,
              fill=(214,158+lane*7,134+lane*12,132+(i%3)*24))
    # A measured-looking waveform drawn explicitly from SYNTHETIC amplitudes.
    samples=signal_samples(phase)
    for i,v in enumerate(samples):
        x=629+i*.96
        fade=(1-min(1,abs(x-803)/210))*.5+.5
        amp=v*(15+35*fade)
        color=(232,167,128,int(158+90*fade))
        d.line((x,335-abs(amp),x,335+abs(amp)),fill=color,width=1)
    # Flow smoothly leaves the track view, leading into nodes with no rectangle seam.
    for strand in range(3):
        pts=[]
        for x in range(974,1101,3):
            u=(x-974)/126
            cy=335-34*u+9*math.sin(u*PI)
            amp=(1-u)**1.5*(3.5+strand*2.0)
            y=cy+amp*math.sin((x-974)/37+phase*.7+strand*.52)
            pts.append((x,y))
        ink_line(d,pts,(213,152+strand*5,144+strand*7,108+strand*23),2)
    return (1100, 301)

def curved_route(d, p1, p2, c1, c2, color, width=2):
    pts=[]
    for i in range(46):
        t=i/45;u=1-t
        x=u**3*p1[0]+3*u*u*t*c1[0]+3*u*t*t*c2[0]+t**3*p2[0]
        y=u**3*p1[1]+3*u*u*t*c1[1]+3*u*t*t*c2[1]+t**3*p2[1]
        pts.append((x,y))
    ink_line(d,pts,color,width)
    return pts

def draw_routing(layer):
    """Branching IO/processing graph is the same continuous signal, not a UI mock."""
    d=ImageDraw.Draw(layer)
    nodes=[(1114,301),(1200,228),(1200,349),(1320,280)]
    curved_route(d,(1098,301),nodes[0],(1102,301),(1108,301),(235,175,141,227),4)
    curved_route(d,nodes[0],nodes[1],(1146,262),(1163,230),(200,165,204,232),4)
    curved_route(d,nodes[0],nodes[2],(1147,338),(1165,348),(163,166,198,222),4)
    curved_route(d,nodes[1],nodes[3],(1254,207),(1284,253),(146,198,204,227),4)
    curved_route(d,nodes[2],nodes[3],(1255,369),(1286,296),(165,187,210,208),4)
    # One intentional handoff from the final route into the dynamic field.
    # The line stops before the calculated orbits instead of drawing over them.
    curved_route(d,nodes[3],(1381,271),(1342,279),(1362,272),(132,194,196,172),2)    # Tiny port markers convey routable edges without boxed cards.
    for i,(x,y) in enumerate(nodes):
        col=[(210,155,129),(173,140,191),(156,166,187),(116,193,191)][i]
        d.ellipse((x-10,y-10,x+10,y+10),fill=(19,21,30,243),outline=(*col,227),width=3)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*col,247))
        for angle in (0,PI):
            xx=x+16*math.cos(angle)
            yy=y+16*math.sin(angle)
            d.ellipse((xx-2,yy-2,xx+2,yy+2),fill=(*col,142))
    return nodes

def draw_orbits(layer, paths, phase=0.):
    """Real generated three-body trajectories blend into the route's last node."""
    d=ImageDraw.Draw(layer)
    cx,cy,scale=1486,265,86
    colors=[(220,163,119),(172,142,193),(113,199,193)]
    for i,path in enumerate(paths):
        xy=[(cx+x*scale,cy-y*scale) for x,y in path]
        ink_line(d,xy,(*colors[i],194),3)
        # Emphasize short local trajectories as an audio/physics signal continuation.
        j=int(phase/(2*PI)*len(xy))%len(xy)
        segment=[xy[(j+t)%len(xy)] for t in range(28)]
        ink_line(d,segment,(*colors[i],248),4)
    d.ellipse((cx-3,cy-3,cx+3,cy+3),outline=(185,171,195,100),width=1)
    for i,path in enumerate(paths):
        j=int(phase/(2*PI)*len(path))%len(path)
        x,y=path[j]
        glow_dot(layer,cx+x*scale,cy-y*scale,colors[i],3)
    # The trajectories themselves provide the orbital structure; an
    # extra oversized guide arc previously crossed the routing region.

def labels(layer):
    d=ImageDraw.Draw(layer)
    fm=font("mono",18)
    d.text((633,246),"01  /  ARRANGE",font=fm,fill=(221,176,146,239))
    d.text((1084,194),"02  /  ROUTE",font=fm,fill=(189,168,208,238))
    d.text((1369,92),"03  /  EVOLVE",font=fm,fill=(159,216,217,240))
    d.text((670,446),"AUDIO  /  MOTION  /  SYSTEMS",font=font("mono",15),
           fill=(178,169,186,219))

def typography(layer):
    d=ImageDraw.Draw(layer)
    # Text-only eyebrow: no invented mark masquerading as the owner's logo.
    d.text((84,45),"RECORDING ARTIST   /   MUSIC PRODUCER",
           font=font("mono",18),fill=(216,202,222,244))
    d.text((78,101),"Sir Davi",font=font("head",99),fill=(*PALETTE["ink"],255))
    d.text((83,239),"Music, media, and systems.",font=font("body",33),
           fill=(235,225,233,255))
    d.text((87,294),"Built through sound, structure",font=font("small",22),
           fill=(205,188,203,239))
    d.text((87,327),"and experimentation.",font=font("small",22),
           fill=(205,188,203,239))
    d.text((88,391),"\u201cI code sometimes\u2026\u201d",font=font("small",18),
           fill=(162,145,172,215))
    d.line((88,377,420,377),fill=(192,148,129,84),width=1)

def frame(phase=0.):
    canvas=backdrop()
    # The grid must be alpha-composited. Drawing translucent RGBA
    # directly onto the opaque base overwrites its alpha and produces
    # bright lines after RGB conversion.
    grid=Image.new("RGBA",SIZE,(0,0,0,0))
    gd=ImageDraw.Draw(grid)
    for x in range(605,1600,56):
        gd.line((x,0,x,469),fill=(143,123,151,19),width=1)
    for y in range(50,470,56):
        gd.line((600,y,1599,y),fill=(143,123,151,19),width=1)
    canvas.alpha_composite(grid)
    ink=Image.new("RGBA",SIZE,(0,0,0,0))
    draw_signal_flow(ink,phase)
    draw_routing(ink)
    draw_orbits(ink,orbital_paths_cached(),phase)
    labels(ink)
    canvas.alpha_composite(ink)
    typography(canvas)
    return canvas

_ORBITS=None
def orbital_paths_cached():
    global _ORBITS
    if _ORBITS is None:
        _ORBITS=orbital_paths()
    return _ORBITS

def compose():
    # Poster and animation share the exact same geometry.
    poster=frame(0).convert("RGB")
    png=ASSETS/"hero-music-systems.png"
    poster.save(png,format="PNG",optimize=True)
    frames=[]
    for k in range(18):
        phase=2*PI*k/18
        frames.append(frame(phase).convert("RGB").quantize(colors=96,method=Image.Quantize.FASTOCTREE))
    gif=ASSETS/"hero-music-systems.gif"
    frames[0].save(gif,save_all=True,append_images=frames[1:],duration=140,
                   loop=1,optimize=True,disposal=2)
    print(f"Integrated PNG={png.stat().st_size} bytes, GIF={gif.stat().st_size} bytes")
    print("Deterministic signal routing plus publicly documented educational dynamics.")

if __name__=="__main__":
    compose()