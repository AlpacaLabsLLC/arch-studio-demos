# Sheds (toilet building) generator, as used for runs 4 to 13 of the Rhino 9 + Claude session.
# Published copy of the run 13 script. Changes from the working file: place, utility and local-code
# names were replaced in names and comments ("Water meter", "Septic pit", "local code minimum").
# Geometry, dimensions and logic are unchanged. Identifiers such as pozo_x keep their original names.
# Needs Rhino 9 (RhinoCommon, Python 3). Each generate_*() returns (layer path, object name, Brep) tuples;
# it does not add anything to the document. See the README for a bake snippet.

# Toilet building generator (Arch Studio): one driver, the cube size C. Metres.
import math
import Rhino
import Rhino.Geometry as G
TOL = 0.001
STUD, CLAD, LINE, L = 0.140, 0.019, 0.012, 0.68
SHEATH, WRB, OC = 0.012, 0.001, 0.4064
SK = SHEATH + WRB
RAFT, BATTEN, THATCH, SLOPE = 0.140, 0.019, 0.25, 0.08
SPACING = 60.0
ROOF_S, ROOF_DP, ROOF_TH, ROOF_EAVE = .10, .140, .006, .15

def layout(C):
    T = STUD + SK + CLAD + LINE; O = C + 2 * T; h = O / 2; P = 1.5 * C; R = 0.75 * C; w = C / 2
    def cube(x, y, d, acc=False, off=0.0, label=""):
        return dict(c=(x, y), d=d, acc=acc, off=off, label=label)
    def route(role, ramp, steps): return dict(role=role, ramp=ramp, steps=steps)
    opts = {}
    # Run 4: basins moved per the designer's notes. Deck and spacing widened to 1.75C where the note needs room.
    Db = 1.75 * C; hD = Db / 2; Pc = 1.75 * C; ALC = .60; CD = .60; ALD = ALC + CD + .10
    def alcove(x0, x1, yw, s, n):
        # recess in the gap between two cubes: floor from the main deck, counter wall to wall, guard behind it
        yc = yw + s * (ALC + CD / 2); fy = yc + s * .23; yg = yw + s * (ALC + CD + .05)
        return dict(deck=(x0, x1, min(yw, yw + s * ALD), max(yw, yw + s * ALD)),
                    counter=(x0, x1, min(yw + s * ALC, yw + s * (ALC + CD)), max(yw + s * ALC, yw + s * (ALC + CD)), "wall"),
                    basins=[(x0 + (x1 - x0) * (i + .5) / n, yc, 0.0, x0 + (x1 - x0) * (i + .5) / n, fy) for i in range(n)],
                    guard=(x0 + .04, yg, x1 - .04, yg))
    # A: one-way along the row. One basin recessed in each of the 4 gaps, so every toilet has one beside it.
    Xe = 4 * P + h; F = -h - C; Xf = Xe + C + 1.5; yl = (F - h - .6) / 2
    alA = [alcove(i * P + h, (i + 1) * P - h, -h, 1, 1) for i in range(4)]
    opts["A"] = dict(
        cubes=[cube(i * P, 0, (0, -1), i == 0, 0.0, ["Accessible", "Women 1", "Women 2", "Men 1", "Men 2"][i]) for i in range(5)],
        decks=[(-h, Xf, F, -h)] + [a_["deck"] for a_ in alA],
        routes=[route("Entry", (-h, -h - w, -h, -1, "x"), (-h, F, -h - w, -1, "x")), route("Exit", (Xf, -h - w, -h, 1, "x"), (Xf, F, -h - w, 1, "x"))],
        guards=[(-h, F, Xf, F), (Xe, -h, Xf, -h)] + [a_["guard"] for a_ in alA],
        counters=[a_["counter"] for a_ in alA], basins=[b_ for a_ in alA for b_ in a_["basins"]],
        flow=[[(-h + .2, yl), (Xf - .2, yl)]], front=F, back=h, xmid=2 * P)
    # B: 2 + 2 across a deck widened to 1.75C, one line of 4 basins down the centre between the toilets.
    Rb = 1.25 * C; bay0 = P + h; bay1 = bay0 + Rb; y = hD + h; c0 = P / 2 - C / 2; xs = c0 - .5; xo = bay1 - w / 2; ln = .3 + R / 2
    opts["B"] = dict(
        cubes=[cube(0, -y, (0, 1), False, .4, "Women 1"), cube(P, -y, (0, 1), False, .4, "Women 2"),
               cube(0, y, (0, -1), False, .4, "Men 1"), cube(P, y, (0, -1), False, .4, "Men 2"),
               cube(bay1 + h, 0, (-1, 0), True, 0.0, "Accessible")],
        decks=[(-h, bay1, -hD, hD)],
        routes=[route("Entry", (-h, 0, w, -1, "x"), (-h, -w, 0, -1, "x")), route("Exit", (-hD, bay1 - w, bay1, -1, "y"), (-hD, bay1 - 2 * w, bay1 - w, -1, "y"))],
        guards=[(h, -hD, P - h, -hD), (h, hD, P - h, hD), (bay0, -hD, bay1 - 2 * w, -hD), (bay0, hD, bay1, hD),
                (-h, w, -h, hD - .04), (-h, -hD + .04, -h, -w), (bay1, h + .04, bay1, hD), (bay1, -hD, bay1, -h - .04)],
        counters=[(c0, c0 + C, -.3, .3)], basins=[(c0 + (i + .5) * C / 4, 0) for i in range(4)],
        flow=[[(-h + .2, .6), (xs, .6), (xs, -ln), (xo, -ln), (xo, -hD + .2)], [(xs, .6), (xs, ln), (xo, ln), (xo, -hD + .2)]],
        front=-(hD + O), back=hD + O, xmid=(bay1 + h) / 2)
    # C: columns opened to 1.75C so each gap takes 2 basins side by side, south for the women's side, north for the men's.
    x1 = Pc + h + R; x0 = -h - R; y0 = -h - R; y1 = P + h + R; mid = P / 2
    xw = x0 + R / 2; yS = y0 + .6 + (R - .6) / 2; yN = y1 - R / 2; xE = Pc + h + (R - .6) / 2
    alS = alcove(h, Pc - h, -h, 1, 2); alN = alcove(h, Pc - h, P + h, -1, 2)
    opts["C"] = dict(
        cubes=[cube(0, 0, (0, -1), False, 0, "Women 1"), cube(Pc, 0, (0, -1), False, 0, "Women 2"),
               cube(0, P, (0, 1), False, 0, "Men 1"), cube(Pc, P, (0, 1), False, 0, "Men 2"),
               cube(x1 + h, mid, (-1, 0), True, 0, "Accessible")],
        decks=[(x0, x1, y0, -h), (x0, x1, P + h, y1), (x0, -h, -h, P + h), (Pc + h, x1, -h, P + h), alS["deck"], alN["deck"]],
        routes=[route("Entry", (x0, mid, mid + w, -1, "x"), (x0, mid - w, mid, -1, "x")), route("Exit", (x1, y0, y0 + w, 1, "x"), (y0, x1 - w, x1, -1, "y"))],
        guards=[(x0, y0, x1 - w, y0), (x0, y1, x1, y1), (x0, y0, x0, mid - w), (x0, mid + w, x0, y1),
                (x1, y0 + w, x1, mid - h), (x1, mid + h, x1, y1),
                alS["guard"], alN["guard"], (-h, h, -h, P - h), (Pc + h, h, Pc + h, P - h)],
        counters=[alS["counter"], alN["counter"]], basins=alS["basins"] + alN["basins"],
        flow=[[(x0 + .2, mid), (xw, mid), (xw, yS), (x1 - .2, yS)], [(xw, mid), (xw, yN), (xE, yN), (xE, yS)]],
        front=y0, back=y1, xmid=(x1 + h) / 2)
    # D: pinwheel. Square basin island, 2 and 2, each basin turned to face out along its diagonal.
    a = C; sx0 = -a + O; sx1 = -a + P + O; sy1 = a + R; r0 = -a + O + .2; s0 = -a + .2; ax = .75 * a; ac = -a + P + h; q = C / 7.5
    radial = []
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        f = math.atan2(sy, sx); bx_, by_ = sx * q, sy * q
        radial.append((bx_, by_, f - math.pi / 2, bx_ - .23 * math.cos(f), by_ - .23 * math.sin(f)))
    opts["D"] = dict(
        cubes=[cube(-a + h, a + h, (0, -1), False, 0, "Men 1"), cube(a + h, a - h, (-1, 0), False, 0, "Men 2"),
               cube(a - h, -a - h, (0, 1), False, 0, "Women 1"), cube(-a - h, -a + h, (1, 0), False, 0, "Women 2"),
               cube(ac, sy1 + h, (0, -1), True, 0, "Accessible")],
        decks=[(-a, a, -a, a), (sx0, sx1, a, sy1)],
        routes=[route("Entry", (-a, r0, r0 + w, -1, "x"), (-a, -a + .2, -a + .2 + w, -1, "y")), route("Exit", (a, s0, s0 + w, 1, "x"), (sx1, a + .1, a + .1 + w, 1, "x"))],
        guards=[(-a, -a, -a + .2, -a), (-a + .2 + w, -a, a - O, -a), (-a, -a + O, -a, r0), (-a, r0 + w, -a, a), (a, s0 + w, a, a - O), (a, -a, a, s0),
                (sx1, a, sx1, a + .1), (sx1, a + .1 + w, sx1, sy1), (sx0, sy1, -a + P, sy1)],
        counters=[(-C / 4, C / 4, -C / 4, C / 4, "ped")], basins=radial,
        flow=[[(-a + .2, r0 + w / 2), (ax, r0 + w / 2), (ax, s0 + w / 2), (a - .2, s0 + w / 2)],
              [(-a + .2 + w / 2, -a + .2), (-a + .2 + w / 2, s0 + w / 2), (a - .2, s0 + w / 2)],
              [(ax, r0 + w / 2), (ax, a + .6), (ac, a + .6)], [(ac, a + .6), (sx1 - .2, a + .1 + w / 2)]],
        front=-a - O, back=sy1 + O, xmid=0.0)
    # Run 5: every door hinged next to the side wall so the leaf parks flat against it when open inward.
    for sp in opts.values():
        for cb in sp["cubes"]: cb["off"] = C / 2 - .55
    return dict(C=C, T=T, O=O, h=h, P=P, R=R, w=w, OH=C / 6, PLATE=L + C, opts=opts)

def uv(ax, u, v, z): return G.Point3d(u, v, z) if ax == "x" else G.Point3d(v, u, z)
def uvbox(ax, u0, u1, v0, v1, z0, z1): return box(u0, u1, v0, v1, z0, z1) if ax == "x" else box(v0, v1, u0, u1, z0, z1)

def P3(x, y, z): return G.Point3d(x, y, z)
def box(x0, x1, y0, y1, z0, z1):
    return G.Box(G.BoundingBox(P3(min(x0, x1), min(y0, y1), min(z0, z1)), P3(max(x0, x1), max(y0, y1), max(z0, z1)))).ToBrep()
def beam(p0, p1, b, d, up):
    v = p1 - p0; n = v.Length; v.Unitize(); y = G.Vector3d.CrossProduct(up, v); y.Unitize()
    return G.Box(G.Plane(p0, v, y), G.Interval(0, n), G.Interval(-b / 2, b / 2), G.Interval(-d / 2, d / 2)).ToBrep()
def cyl(p0, p1, r):
    v = p1 - p0; return G.Cylinder(G.Circle(G.Plane(p0, v), r), v.Length).ToBrep(True, True)
def cap(b):
    c = b.CapPlanarHoles(TOL)
    if c is None or not c.IsSolid: raise ValueError("cap failed")
    return c
def prism(pts, vec):
    pts = list(pts) + [pts[0]]
    c = cap(G.Surface.CreateExtrusion(G.Polyline(pts).ToNurbsCurve(), vec).ToBrep())
    if c.SolidOrientation == G.BrepSolidOrientation.Inward: c.Flip()
    return c
def disc(x, y, z0, z1, rx, ry):
    c = cap(G.Surface.CreateExtrusion(G.Ellipse(G.Plane(P3(x, y, z0), G.Vector3d.ZAxis), rx, ry).ToNurbsCurve(), G.Vector3d(0, 0, z1 - z0)).ToBrep())
    if c.SolidOrientation == G.BrepSolidOrientation.Inward: c.Flip()
    return c
def solid_extrude(crv, vec):
    c = cap(G.Surface.CreateExtrusion(crv, vec).ToBrep())
    if c.SolidOrientation == G.BrepSolidOrientation.Inward: c.Flip()
    return c
def arc_band(ri, ro, z0, y0, y1):
    outer = G.Arc(P3(ro, y0, z0), P3(0, y0, z0 + ro), P3(-ro, y0, z0)).ToNurbsCurve()
    inner = G.Arc(P3(-ri, y0, z0), P3(0, y0, z0 + ri), P3(ri, y0, z0)).ToNurbsCurve()
    parts = [outer, G.LineCurve(P3(-ro, y0, z0), P3(-ri, y0, z0)), inner, G.LineCurve(P3(ri, y0, z0), P3(ro, y0, z0))]
    j = G.Curve.JoinCurves(parts, TOL)
    if j is None or len(j) != 1 or not j[0].IsClosed: raise ValueError("arc band did not close")
    return solid_extrude(j[0], G.Vector3d(0, y1 - y0, 0))
def half_disc(r, z0, y0, t):
    j = G.Curve.JoinCurves([G.Arc(P3(r, y0, z0), P3(0, y0, z0 + r), P3(-r, y0, z0)).ToNurbsCurve(), G.LineCurve(P3(-r, y0, z0), P3(r, y0, z0))], TOL)
    if j is None or len(j) != 1 or not j[0].IsClosed: raise ValueError("half disc did not close")
    return solid_extrude(j[0], G.Vector3d(0, t, 0))
def tri(a, b, c): return G.Brep.CreateFromCornerPoints(a, b, c, TOL)
def quad(a, b, c, d): return G.Brep.CreateFromCornerPoints(a, b, c, d, TOL)
def steps_range(a, b, s):
    n = max(1, int(round((b - a) / s))); return [a + (b - a) * i / n for i in range(n + 1)]

def oc_range(a, b, s):
    # pulled from one corner on true centres, closing stud at the far end
    p = [a]
    while p[-1] + s < b - .06: p.append(p[-1] + s)
    if b - p[-1] > .02: p.append(b)
    return p

def clear1(v, keeps, half):
    for i in range(60):
        for c in (v + i * .02, v - i * .02):
            if all(abs(c - k) >= half + r + .02 for k, r in keeps): return c
    return v

def cube_items(g, cb):
    C, O, h = g["C"], g["O"], g["h"]; PL = g["PLATE"]; OH = g["OH"]; out = []
    add = lambda lay, name, geo, xf=None: out.append((lay, name, geo, xf))
    vs = C / 2 + LINE + STUD / 2; off = cb["off"]; RO = .47
    # toilet on the side away from the hinge, out of the door line; louvered grill vent above it, high in the rear wall
    acc = cb["acc"]; u0 = -C / 2 + (.45 if acc else .60); VW, VH = .40, .30; V1 = PL - .268; V0 = V1 - VH; hw = VW / 2; uv = -u0
    rin = C / 2 + LINE; Rf = rin + STUD; H = L + 2.04; RISE = 2 * vs * ROOF_S
    def hdr(a_, b_, z_, nm, rk_):
        # double 2x8 header with a spacer filling the 2x6 wall
        add("Wall framing::Headers", nm, box(a_, b_, vs + .032, vs + .07, z_, z_ + .184), rk_)
        add("Wall framing::Headers", nm, box(a_, b_, vs - .07, vs - .032, z_, z_ + .184), rk_)
        add("Wall framing::Headers", "Header spacer", box(a_, b_, vs - .032, vs + .032, z_, z_ + .184), rk_)
    for k in range(4):
        rk = G.Transform.Rotation(k * math.pi / 2, G.Point3d.Origin)
        door = k == 0; even = k % 2 == 0
        lo, hi = (-Rf, Rf) if even else (-rin, rin)
        ulo, uhi = (-rin, rin) if even else (-Rf, Rf)
        pieces = [(lo, off - RO + .019), (off + RO - .019, hi)] if door else [(lo, hi)]
        for a, b in pieces:
            add("Wall framing::Plates", "Bottom plate", box(a, b, vs - .07, vs + .07, L, L + .038), rk)
        dzt = RISE if k == 0 else 0.0
        rake = lambda u: PL + ((u if k == 1 else -u) + vs) * ROOF_S
        if k % 2:
            # raked side walls: plates follow the roof and butt the end walls
            add("Wall framing::Plates", "Top plate", beam(P3(lo, vs, rake(lo) - .057), P3(hi, vs, rake(hi) - .057), .14, .038, G.Vector3d.ZAxis), rk)
            add("Wall framing::Plates", "Double top plate lapped at corner", beam(P3(lo, vs, rake(lo) - .019), P3(hi, vs, rake(hi) - .019), .14, .038, G.Vector3d.ZAxis), rk)
        else:
            add("Wall framing::Plates", "Top plate", box(lo, hi, vs - .07, vs + .07, PL - .076 + dzt, PL - .038 + dzt), rk)
            add("Wall framing::Plates", "Double top plate lapped at corner", box(ulo, uhi, vs - .07, vs + .07, PL - .038 + dzt, PL + dzt), rk)
        z0, z1 = L + .038, PL - .076 + dzt
        zt = (lambda u: rake(u) - .078) if k % 2 else (lambda u: z1)
        us = oc_range(lo + .019, hi - .019, OC); wall_us = []
        for u in us:
            if door and off - RO - .10 < u < off + RO + .10: continue
            if k == 2 and abs(u - uv) < hw + .06: continue
            if even and abs(abs(u) - (rin + .019)) < .045 and abs(abs(u) - (Rf - .019)) > .001: continue
            add("Wall framing::Studs", "Stud", box(u - .019, u + .019, vs - .07, vs + .07, z0, zt(u)), rk); wall_us.append(u)
        if even:
            for s_ in (-1, 1):
                add("Wall framing::Studs", "Corner stud", box(s_ * (rin + .019) - .019, s_ * (rin + .019) + .019, vs - .07, vs + .07, z0, z1), rk)
                wall_us.append(s_ * (rin + .019))
                c0, c1 = sorted((s_ * (rin + .038), s_ * (Rf - .038)))
                for zc in (z0 + .30, (z0 + z1) / 2, z1 - .30):
                    add("Wall framing::Blocking", "Corner blocking", box(c0, c1, vs - .07, vs + .07, zc - .019, zc + .019), rk)
        if door:
            for s in (-1, 1):
                add("Wall framing::Studs", "King stud", box(off + s * (RO + .038) - .019, off + s * (RO + .038) + .019, vs - .07, vs + .07, z0, z1), rk)
                add("Wall framing::Studs", "Jack stud", box(off + s * RO - .019, off + s * RO + .019, vs - .07, vs + .07, z0, H), rk)
                wall_us += [off + s * (RO + .038), off + s * RO]
            hdr(off - RO - .019, off + RO + .019, H, "Door header 2x8", rk)
            if z1 - (H + .184) > .03:
                for u in us:
                    if off - RO + .06 < u < off + RO - .06:
                        add("Wall framing::Studs", "Cripple stud", box(u - .019, u + .019, vs - .07, vs + .07, H + .184, z1), rk)
        if k == 2:
            for s_ in (-1, 1):
                add("Wall framing::Studs", "Vent king stud", box(uv + s_ * (hw + .019) - .019, uv + s_ * (hw + .019) + .019, vs - .07, vs + .07, z0, z1), rk)
                wall_us.append(uv + s_ * (hw + .019))
            hdr(uv - hw, uv + hw, V1, "Vent header 2x8", rk)
            add("Wall framing::Headers", "Vent sill", box(uv - hw, uv + hw, vs - .07, vs + .07, V0 - .038, V0), rk)
            add("Wall framing::Studs", "Vent cripple stud", box(uv - .019, uv + .019, vs - .07, vs + .07, z0, V0 - .038), rk)
            wall_us.append(uv)
            dy0, dy1 = vs - .07, h
            add("Room vent", "Vent frame", box(uv - hw, uv - hw + .02, dy0, dy1, V0, V1), rk)
            add("Room vent", "Vent frame", box(uv + hw - .02, uv + hw, dy0, dy1, V0, V1), rk)
            add("Room vent", "Vent frame", box(uv - hw + .02, uv + hw - .02, dy0, dy1, V1 - .02, V1), rk)
            add("Room vent", "Vent frame", box(uv - hw + .02, uv + hw - .02, dy0, dy1, V0, V0 + .02), rk)
            tilt = G.Vector3d(0, .7071, .7071)
            for i_ in range(4):
                zl = V0 + .02 + (VH - .04) * (i_ + .5) / 4
                add("Room vent", "Vent louver", beam(P3(uv - hw + .02, (dy0 + dy1) / 2, zl), P3(uv + hw - .02, (dy0 + dy1) / 2, zl), .05, .008, tilt), rk)
            add("Flashing", "Vent head flashing", box(uv - hw, uv + hw, h, h + .03, V1 - .002, V1), rk)
        if acc and k in (1, 2):
            # solid backing between studs behind the grab bars
            zbk = L + .87; ss = sorted(set(round(x, 5) for x in wall_us))
            span = (-C / 2 + .30, -C / 2 + 1.37) if k == 1 else (-(u0 + .65), -(u0 - .30))
            for a_, b_ in zip(ss, ss[1:]):
                if b_ - a_ > .06 and b_ > span[0] and a_ < span[1]:
                    add("Wall framing::Blocking", "Grab bar backing", box(a_ + .019, b_ - .019, vs - .07, vs + .07, zbk - .07, zbk + .07), rk)
        def panel(lay, nm, t, v_, ch, zb):
            if door:
                pts = [P3(-ch, v_, zb), P3(off - RO, v_, zb), P3(off - RO, v_, L + 2.04), P3(off + RO, v_, L + 2.04), P3(off + RO, v_, zb), P3(ch, v_, zb), P3(ch, v_, PL + RISE), P3(-ch, v_, PL + RISE)]
            else:
                pts = [P3(-ch, v_, zb), P3(ch, v_, zb), P3(ch, v_, rake(ch) if k % 2 else PL), P3(-ch, v_, rake(-ch) if k % 2 else PL)]
            sk = prism(pts, G.Vector3d(0, t, 0))
            if k == 2 and t < .005:
                # too thin to boolean at model tolerance: four strips around the vent opening
                for a_, b_, c_, d_ in ((-ch, uv - hw, zb, PL), (uv + hw, ch, zb, PL), (uv - hw, uv + hw, zb, V0), (uv - hw, uv + hw, V1, PL)):
                    add(lay, nm, prism([P3(a_, v_, c_), P3(b_, v_, c_), P3(b_, v_, d_), P3(a_, v_, d_)], G.Vector3d(0, t, 0)), rk)
                return
            if k == 2:
                cut_ = G.Brep.CreateBooleanDifference(sk, box(uv - hw, uv + hw, v_ - .05, v_ + t + .05, V0, V1), TOL)
                if cut_ is None or len(cut_) != 1: raise ValueError("vent opening failed")
                sk = cut_[0]
            add(lay, nm, sk, rk)
        zs_ = L if door else L - .209
        panel("Wall sheathing", "Plywood sheathing 12 mm", SHEATH, Rf, Rf + SHEATH if even else Rf, zs_)
        panel("Weather barrier", "Weather-resistive barrier", WRB, Rf + SHEATH, Rf + SK if even else Rf + SHEATH, zs_)
        panel("Cladding", "Vertical board cladding", CLAD, Rf + SK, h if even else h - CLAD, L if door else L - .20)
    add("Flashing", "Door head flashing", box(off - RO, off + RO, h, h + .03, H - .002, H))
    add("Door thresholds", "Door threshold", box(off - RO + .019, off + RO - .019, Rf, h, L - .025, L))
    add("Doors", "Door leaf", box(off - .45, off + .45, vs - .0225, vs + .0225, L + .005, L + 2.0))
    add("Floor::Subfloor", "Subfloor", box(-Rf, Rf, -Rf, Rf, L - .025, L))
    keeps = [(u0, .055), (u0 + .19, .010)]
    risers = [(u0, -C / 2 + .54, .055), (u0 + .19, -C / 2 + .11, .010)]
    js = []
    # flush framing: joists hang between double girders so joists and girders share one underside, 18 in. or more above grade
    gv = [-(Rf - .038), 0.0, Rf - .038]; pv = [-(Rf - .15), 0.0, Rf - .15]
    segs = [(-Rf + .076, -.038), (.038, Rf - .076)]
    for u in oc_range(-Rf + .019, Rf - .019, OC):
        u = clear1(u, keeps, .019); js.append(u)
        for v0_, v1_ in segs:
            add("Floor framing::Joists", "Floor joist 2x8 PT", box(u - .019, u + .019, v0_, v1_, L - .209, L - .025))
            for h0_, h1_ in ((v0_, v0_ + .05), (v1_ - .05, v1_)):
                add("Connectors", "Joist hanger", box(u - .021, u + .021, h0_, h1_, L - .212, L - .209))
    js.sort()
    for v in gv:
        for p_ in (v - .038, v):
            add("Floor framing::Girders", "Girder ply 2x8 PT", box(-Rf, Rf, p_, p_ + .038, L - .209, L - .025))
    for v in (-(Rf - .038) / 2, (Rf - .038) / 2):
        for a_, b_ in zip(js, js[1:]):
            if b_ - a_ < .06: continue
            if any(a_ - r - .01 < x < b_ + r + .01 and abs(y - v) < .019 + r + .01 for x, y, r in risers): continue
            add("Floor framing::Blocking", "Solid blocking 2x8 PT", box(a_ + .019, b_ - .019, v - .019, v + .019, L - .209, L - .025))
    for j_, v in enumerate(pv):
        for u in pv:
            add("Piers", "Concrete pier", box(u - .15, u + .15, v - .15, v + .15, -.45, L - .247))
            add("Piers", "Sill plate PT", box(u - .15, u + .15, v - .15, v + .15, L - .247, L - .209))
            add("Connectors", "Anchor bolt 12 mm", cyl(P3(u, gv[j_], L - .347), P3(u, gv[j_], L - .036), .006))
    # toilet
    seat = L + (.455 if acc else .40); kind = "Accessible WC" if acc else "Standard WC"
    tv0 = -C / 2 + .02; tv1 = -C / 2 + .20; bv = tv1 + .34
    add(kind + "::Bowl", "Toilet bowl", disc(u0, bv, L, seat - .04, .19, .34))
    add(kind + "::Seat", "Toilet seat", disc(u0, bv, seat - .04, seat, .19, .34))
    add(kind + "::Tank", "Toilet tank", box(u0 - .225, u0 + .225, tv0, tv1, L, L + .76))
    if acc:
        wall = -C / 2 + .04; zb = L + .87; far = -C / 2 + .04
        side = cyl(P3(wall, -C / 2 + .30, zb), P3(wall, -C / 2 + 1.37, zb), .019)
        rear = cyl(P3(u0 - .30, far, zb), P3(u0 + .65, far, zb), .019)
        add("Grab bars", "Side grab bar", side); add("Grab bars", "Rear grab bar", rear)
        for p, q in [((wall, -C / 2 + .40), (-C / 2, -C / 2 + .40)), ((wall, -C / 2 + 1.27), (-C / 2, -C / 2 + 1.27)),
                     ((u0 - .22, far), (u0 - .22, -C / 2)), ((u0 + .55, far), (u0 + .55, -C / 2))]:
            add("Grab mounts", "Grab bar mount", cyl(P3(p[0], p[1], zb), P3(q[0], q[1], zb), .025))
    # roof: single slope, low at the rear wall, one layer of purlins on the raked side walls, metal sheet over
    ztop = lambda y: PL + (y + vs) * ROOF_S
    nr = G.Vector3d(0, -ROOF_S, 1); nr.Unitize(); cdp = ROOF_DP / nr.Z; X = h + ROOF_EAVE
    for y in (-vs, 0.0, vs):
        add("Roof framing::Purlins", "Purlin 2x6", beam(P3(-X, y, ztop(y) + cdp / 2), P3(X, y, ztop(y) + cdp / 2), .038, ROOF_DP, nr))
        for sx in (-1, 1):
            add("Connectors", "Purlin uplift tie", box(sx * vs - .02, sx * vs + .02, y + .019, y + .022, ztop(y) - .06, ztop(y) + .06))
    zs_ = lambda y: ztop(y) + cdp
    add("Roof sheet", "Metal roof sheet", prism([P3(-X, -X, zs_(-X)), P3(-X, X, zs_(X)), P3(-X, X, zs_(X) + ROOF_TH), P3(-X, -X, zs_(-X) + ROOF_TH)], G.Vector3d(2 * X, 0, 0)))
    return out, dict(wc=(u0, bv), cold=(u0 + .19, (tv0 + tv1) / 2))

def guard(items, x0, y0, x1, y1):
    n = max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0) / 1.2)))
    for i in range(n + 1):
        t = i / float(n); x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
        items.append(("Guards", "Guard post", box(x - .04, x + .04, y - .04, y + .04, L, L + .90)))
    for z, nm in ((L + .90, "Top rail"), (L + .45, "Mid rail")):
        items.append(("Guards", nm, beam(P3(x0, y0, z), P3(x1, y1, z), .05, .05, G.Vector3d.ZAxis)))

def deck_items(items, x0, x1, y0, y1, keeps=()):
    inside = [k for k in keeps if x0 <= k[0] <= x1 and y0 <= k[1] <= y1]
    items.append(("Deck", "Deck surface", box(x0, x1, y0, y1, L - .032, L)))
    alongy = (x1 - x0) >= (y1 - y0)
    a0, a1, b0, b1 = (x0, x1, y0, y1) if alongy else (y0, y1, x0, x1)
    ka = [((k[0] if alongy else k[1]), k[2]) for k in inside]; kb = [((k[1] if alongy else k[0]), k[2]) for k in inside]
    mid_ = b1 - b0 > 2.4
    rows = [b0 + .038, b1 - .038] + ([clear1((b0 + b1) / 2, kb, .038)] if mid_ else [])
    prow = [b0 + .15, b1 - .15] + ([rows[2]] if mid_ else [])
    rs = sorted(rows); bays = [(p + .038, q - .038) for p, q in zip(rs, rs[1:])]
    for s in oc_range(a0 + .019, a1 - .019, OC):
        s = clear1(s, ka, .019)
        for c0, c1 in bays:
            items.append(("Floor framing::Joists", "Deck joist 2x8 PT", box(s - .019, s + .019, c0, c1, L - .216, L - .032) if alongy else box(c0, c1, s - .019, s + .019, L - .216, L - .032)))
            for h0, h1 in ((c0, c0 + .05), (c1 - .05, c1)):
                items.append(("Connectors", "Joist hanger", box(s - .021, s + .021, h0, h1, L - .219, L - .216) if alongy else box(h0, h1, s - .021, s + .021, L - .219, L - .216)))
    for r, pr in zip(rows, prow):
        stations = []
        for s in steps_range(a0 + .2, a1 - .2, 2.4):
            free = lambda c: a0 + .15 <= c <= a1 - .15 and not [k for k in inside if abs((k[0] if alongy else k[1]) - c) < .15 + k[2] + .02 and abs((k[1] if alongy else k[0]) - pr) < .15 + k[2] + .02]
            s = next((c for i in range(120) for c in (s + i * .02, s - i * .02) if free(c)), s)
            stations.append(s)
            zs = [(-.45, L - .254, "Concrete pier"), (L - .254, L - .216, "Sill plate PT")]
            for z0_, z1_, nm in zs:
                items.append(("Piers", nm, box(s - .15, s + .15, pr - .15, pr + .15, z0_, z1_) if alongy else box(pr - .15, pr + .15, s - .15, s + .15, z0_, z1_)))
            px, py = (s, r) if alongy else (r, s)
            items.append(("Connectors", "Anchor bolt 12 mm", cyl(P3(px, py, L - .354), P3(px, py, L - .043), .006)))
        # two plies, each jointed only over a pier and staggered ply to ply
        stations = sorted(stations); MAXL = 4.8
        def pick(first_short, avoid):
            last, out = a0, []
            while a1 - last > MAXL:
                c_ = [c for c in stations[1:-1] if last + .5 < c <= last + MAXL]
                if not c_: break
                pref = [c for c in c_ if c not in avoid] or c_
                last = pref[0] if (first_short and not out) else pref[-1]; out.append(last)
            return out
        g1 = pick(False, []); gcuts = [pick(True, g1), g1]
        for ply, (p0, p1) in enumerate(((r - .038, r), (r, r + .038))):
            cuts = [a0] + gcuts[ply] + [a1]
            for c0, c1 in zip(cuts, cuts[1:]):
                items.append(("Floor framing::Girders", "Deck girder ply 2x8 PT", box(c0, c1, p0, p1, L - .216, L - .032) if alongy else box(p0, p1, c0, c1, L - .216, L - .032)))

def disc_r(x, y, z0, z1, rx, ry, rot):
    c = disc(0, 0, z0, z1, rx, ry)
    c.Transform(G.Transform.Multiply(G.Transform.Translation(x, y, 0), G.Transform.Rotation(rot, G.Point3d.Origin)))
    return c
def basin_parts(b, counters):
    if len(b) == 5: return b
    bx, by = b
    c = [k for k in counters if k[0] <= bx <= k[1] and k[2] <= by <= k[3]][0]
    fxa = bx - .23 if bx > (c[0] + c[1]) / 2 + 1e-6 else bx + .23
    return bx, by, 0.0, fxa, by + .08

def option_items(g, sp):
    C = g["C"]; items = []; fixtures = []
    for cb in sp["cubes"]:
        (cx, cy), (dx, dy) = cb["c"], cb["d"]
        rot = math.atan2(dy, dx) - math.pi / 2
        xf = G.Transform.Multiply(G.Transform.Translation(cx, cy, 0), G.Transform.Rotation(rot, G.Point3d.Origin))
        cub, fx = cube_items(g, cb)
        for lay, nm, geo, x in cub:
            if x is not None: geo.Transform(x)
            geo.Transform(xf); items.append((lay, nm, geo))
        p = P3(fx["wc"][0], fx["wc"][1], 0); p.Transform(xf)
        q = P3(fx["cold"][0], fx["cold"][1], 0); q.Transform(xf)
        fixtures.append(dict(drain=(p.X, p.Y), dia=.110, cold=(q.X, q.Y), top=L + .60, dtop=L, name="Toilet"))
    keeps = []
    for b_ in sp["basins"]:
        bx, by, rot, fa, fb = basin_parts(b_, sp["counters"])
        keeps += [(bx, by, .025), (fa, fb, .010)]
    for dk in sp["decks"]: deck_items(items, *dk, keeps)
    RUN = L / SLOPE; LD = 1.5; rise = L / 4.0
    for rt in sp["routes"]:
        role = rt["role"]; e, lo, hi, s, ax = rt["ramp"]
        wv = G.Vector3d(0, hi - lo, 0) if ax == "x" else G.Vector3d(hi - lo, 0, 0)
        n_ = math.hypot(SLOPE, 1.0); nu, nz = s * SLOPE / n_, 1.0 / n_
        ruz = lambda t, d: (e + s * RUN * t - nu * d, L * (1 - t) - nz * d)
        rp = lambda t, d, vv: uv(ax, ruz(t, d)[0], vv, ruz(t, d)[1])
        TF, TG = .5, .25
        # upper half framed in wood on a flush girder and posts, lower half a concrete slab where framing would reach grade
        items.append(("Ramp::" + role, role + " ramp deck", prism([rp(0, 0, lo), rp(TF, 0, lo), rp(TF, .032, lo), rp(0, .032, lo)], wv)))
        uf = e + s * RUN * TF; zf_ = L * (1 - TF)
        items.append(("Ramp::" + role, role + " ramp slab", prism([uv(ax, uf, lo, zf_), uv(ax, e + s * RUN, lo, 0), uv(ax, e + s * (RUN + LD), lo, 0), uv(ax, e + s * (RUN + LD), lo, -.15), uv(ax, e + s * RUN, lo, -.15), uv(ax, uf, lo, zf_ - .15)], wv)))
        ztop_ = ruz(TF, .216)[1] - .008
        items.append(("Piers", role + " ramp stem", uvbox(ax, min(uf, uf - s * .20), max(uf, uf - s * .20), lo, hi, -.45, ztop_)))
        ug = e + s * RUN * TG; zg1 = L * (1 - TG) - .036 - .004; zg0 = zg1 - .184
        for p0_, p1_ in ((ug - .038, ug), (ug, ug + .038)):
            items.append(("Floor framing::Girders", "Ramp girder ply 2x8 PT", uvbox(ax, p0_, p1_, lo, hi, zg0, zg1)))
        for vp in (lo + .15, hi - .15):
            items.append(("Piers", "Ramp post", uvbox(ax, ug - .075, ug + .075, vp - .075, vp + .075, -.45, zg0)))
        nv = G.Vector3d(nu, 0, nz) if ax == "x" else G.Vector3d(0, nu, nz)
        dt = .038 / RUN
        for vp in oc_range(lo + .019, hi - .019, OC):
            for t0_, t1_ in ((0.0, TG - dt), (TG + dt, TF)):
                items.append(("Floor framing::Joists", "Ramp joist 2x8 PT", beam(rp(t0_, .124, vp), rp(t1_, .124, vp), .038, .184, nv)))
        for vp in (lo + .03, hi - .03):
            items.append(("Guards", "Ramp handrail", beam(uv(ax, e, vp, L + .90), uv(ax, e + s * RUN, vp, .90), .05, .05, G.Vector3d.ZAxis)))
            for t in (0, .2, .4, .6, .8, 1.0):
                up = e + s * RUN * t; zr = L * (1 - t)
                items.append(("Guards", "Ramp post", uvbox(ax, up - .04, up + .04, vp - .04, vp + .04, zr, zr + .90)))
        e, lo, hi, s, ax = rt["steps"]
        for i in (1, 2, 3):
            items.append(("Steps::" + role, "Step tread", uvbox(ax, min(e + s * .3 * (4 - i), e + s * .3 * (3 - i)), max(e + s * .3 * (4 - i), e + s * .3 * (3 - i)), lo, hi, i * rise - .032, i * rise)))
        tv = .038; xv = G.Vector3d(0, tv, 0) if ax == "x" else G.Vector3d(tv, 0, 0)
        prof = [(0, 3 * rise - .032), (.3, 3 * rise - .032), (.3, 2 * rise - .032), (.6, 2 * rise - .032), (.6, rise - .032), (.9, rise - .032), (.9, 0), (.55, 0), (0, 3 * rise - .032 - .21)]
        for vp in steps_range(lo + .019, hi - .019, OC):
            items.append(("Steps::" + role, "Step stringer 2x12 PT", prism([uv(ax, e + s * a_, vp - .019, z_) for a_, z_ in prof], xv)))
        items.append(("Piers", "Step footing pad", uvbox(ax, min(e + s * .50, e + s * 1.0), max(e + s * .50, e + s * 1.0), lo, hi, -.10, 0)))
    for gd in sp["guards"]: guard(items, *gd)
    for c in sp["counters"]:
        items.append(("Basin counter", "Basin counter", box(c[0], c[1], c[2], c[3], L + .76, L + .80)))
        kind = c[4] if len(c) > 4 else ""
        if kind == "ped":
            mx, my = (c[0] + c[1]) / 2, (c[2] + c[3]) / 2
            items.append(("Basin counter", "Counter pedestal", box(mx - .09, mx + .09, my - .09, my + .09, L, L + .76)))
        elif c[1] - c[0] >= c[3] - c[2]:
            ins = .005 if kind == "wall" else .02
            for xa in (c[0] + ins, c[1] - ins - .03):
                items.append(("Basin counter", "Counter leg", box(xa, xa + .03, c[2] + .02, c[3] - .02, L, L + .76)))
        else:
            for ya in (c[2] + .02, c[3] - .07):
                items.append(("Basin counter", "Counter leg", box(c[0] + .02, c[1] - .02, ya, ya + .05, L, L + .76)))
    for b_ in sp["basins"]:
        bx, by, rot, fa, fb = basin_parts(b_, sp["counters"])
        items.append(("Basins", "Basin", disc_r(bx, by, L + .72, L + .83, .20, .17, rot)))
        items.append(("Faucets", "Faucet", cyl(P3(fa, fb, L + .80), P3(fa, fb, L + .98), .012)))
        fixtures.append(dict(drain=(bx, by), dia=.050, cold=(fa, fb), top=L + .80, dtop=L + .72, name="Basin"))
    # plumbing: buried below the piers, all by gravity to the chamber and the septic pit
    xm = sp["xmid"]; Bk, F = sp["back"], sp["front"]; Y0 = Bk + 1.2
    dmax = max(abs(f["drain"][0] - xm) + (Y0 - f["drain"][1]) for f in fixtures)
    ztop = -.55; zc = ztop - .02 * dmax
    zy = lambda y: zc + .02 * (Y0 - y)
    for f in fixtures:
        fx, fy = f["drain"]; zs = zy(fy) + .02 * abs(fx - xm); r = f["dia"] / 2
        items.append(("Drains", f["name"] + " drain riser", cyl(P3(fx, fy, f["dtop"]), P3(fx, fy, zs), r)))
        if abs(fx - xm) > .01:
            items.append(("Drains", f["name"] + " drain branch", cyl(P3(fx, fy, zs), P3(xm, fy, zy(fy)), r)))
    ymin = min(f["drain"][1] for f in fixtures)
    items.append(("Drains", "Collector", cyl(P3(xm, ymin, zy(ymin)), P3(xm, Y0, zc), .055)))
    items.append(("Inspection chamber", "Inspection chamber", box(xm - .40, xm + .40, Y0 - .40, Y0 + .40, zc - .30, 0)))
    pozo_y = Bk + 10.0; Ro = 1.40; Ri = 1.25; zf = -3.29
    main_end = pozo_y + .20; dist = main_end - (Y0 + .40)
    items.append(("Main drain", "Main drain to septic pit", cyl(P3(xm, Y0 + .40, zc), P3(xm, main_end, zc - .025 * dist), .055)))
    pc = P3(xm, pozo_y + Ro, 0)
    outer = cyl(P3(pc.X, pc.Y, zf), P3(pc.X, pc.Y, -.20), Ro); inner = cyl(P3(pc.X, pc.Y, zf + .20), P3(pc.X, pc.Y, -.10), Ri)
    shell = G.Brep.CreateBooleanDifference(outer, inner, TOL)
    if shell is None or len(shell) != 1: raise ValueError("pit shell failed")
    items.append(("Septic pit", "Septic pit shell", shell[0]))
    items.append(("Septic pit", "Septic pit cover slab", cyl(P3(pc.X, pc.Y, -.20), P3(pc.X, pc.Y, 0), Ro)))
    APEX = g["PLATE"] + (g["h"] + ROOF_EAVE + g["C"] / 2 + LINE + STUD / 2) * ROOF_S + ROOF_DP + ROOF_TH
    vy = Bk + .70
    items.append(("Vents", "Building vent stack", cyl(P3(xm, vy, zy(vy)), P3(xm, vy, APEX + .70), .0315)))
    items.append(("Vents", "Septic pit vent", cyl(P3(pc.X + .9, pc.Y, -.20), P3(pc.X + .9, pc.Y, 2.50), .0315)))
    xw = xm + .30; zw = -.48; ym = F - 10.0
    while any(abs(xw - f["drain"][0]) < f["dia"] / 2 + .0125 + .03 for f in fixtures): xw += .05
    items.append(("Water meter", "Water meter box", box(xw - .20, xw + .20, ym - .25, ym, -.30, 0)))
    ymax = max(f["cold"][1] for f in fixtures)
    items.append(("Cold water", "Cold water meter riser", cyl(P3(xw, ym - .05, zw), P3(xw, ym - .05, -.25), .0125)))
    items.append(("Cold water", "Cold water main", cyl(P3(xw, ym - .05, zw), P3(xw, ymax, zw), .0125)))
    for f in fixtures:
        fx, fy = f["cold"]
        if abs(fx - xw) > .01:
            items.append(("Cold water", "Cold water branch", cyl(P3(xw, fy, zw), P3(fx, fy, zw), .010)))
        items.append(("Cold water", "Cold water riser", cyl(P3(fx, fy, zw), P3(fx, fy, f["top"]), .010)))
    far = pozo_y + 2 * Ro + .5
    items.append(("Truck access", "Truck access strip", box(xm - 1.5, xm + 1.5, far, far + 6.0, -.02, 0)))
    return items

def generate(C):
    g = layout(C); res = []
    for n, (o, sp) in enumerate(sorted(g["opts"].items())):
        X = n * SPACING; move = G.Transform.Translation(X, -240.0, 0)
        for lay, name, geo in option_items(g, sp):
            geo.Transform(move)
            geo.SetUserString("as_layer", "Toilet Building Run 6::Option %s::%s" % (o, lay)); geo.SetUserString("as_name", name)
            res.append(geo)
    return res


# ---- Run 8, option F: option D with the fifth unit removed; 2 ramps and 2 steps in the side gaps. ----
CENTRE = (180.0, -360.0)
def layout_f(C):
    g = layout(C); sp = g["opts"]["D"]; a, O, w = C, g["O"], g["w"]
    assert sp["cubes"][4]["acc"] and not any(c["acc"] for c in sp["cubes"][:4])
    sp["cubes"] = sp["cubes"][:4]
    sp["decks"] = [(-a, a, -a, a)]
    r0 = -a + O + .2; s0 = -a + .2
    sp["routes"] = [dict(role="Entry", ramp=(-a, r0, r0 + w, -1, "x"), steps=(-a, s0, s0 + w, -1, "y")),
                    dict(role="Exit", ramp=(a, -r0 - w, -r0, 1, "x"), steps=(a, -s0 - w, -s0, 1, "y"))]
    g0 = [(-a, -a, s0, -a), (s0 + w, -a, a - O - .04, -a), (-a, -a + O + .04, -a, r0), (-a, r0 + w, -a, a)]
    sp["guards"] = g0 + [(-x0, -y0, -x1, -y1) for x0, y0, x1, y1 in g0]
    sp["back"] = a + O; sp["front"] = -a - O; sp["xmid"] = 0.0
    return g, sp
def generate_f(C=2.40):
    g, sp = layout_f(C); out = []; move = G.Transform.Translation(CENTRE[0], CENTRE[1], 0)
    for lay, name, geo in option_items(g, sp):
        geo.Transform(move); out.append(("Toilet Building Run 8::Option F::%s" % lay, name, geo))
    return out

def generate_g(C=2.40):
    g, sp = layout_f(C); out = []; move = G.Transform.Translation(180.0, -420.0, 0)
    for lay, name, geo in option_items(g, sp):
        geo.Transform(move); out.append(("Toilet Building Run 9::Option G::%s" % lay, name, geo))
    return out


# ---- Run 10, option H: compact 2 + 2 on a central hall, minimum rooms (local code minimum, 1.40 m2), one ramp. Metres. ----
RX, RY, HALL, MINH, FIN = 1.40, 1.00, 1.70, 2.20, .020   # room depth, room width, hall, legal height, floor finish allowance
LEAF, RO, PART, YN_EXT = .70, .37, .089, .56             # door leaf, half rough opening, 2x4 partition, deck past the rooms
def option_h_items():
    items = []; add = lambda lay, nm, geo: items.append((lay, nm, geo))
    S = ROOF_S; PL = L + MINH + FIN; H = L + 2.04; z0 = L + .038
    XH = HALL / 2; XS0 = XH + CLAD + SK; XS1 = XS0 + STUD; XHC = (XS0 + XS1) / 2
    XC0 = XS1 + LINE; XC1 = XC0 + RX; XO0 = XC1 + LINE; XO1 = XO0 + STUD; XOC = (XO0 + XO1) / 2; XE = XO1 + SK + CLAD
    YP = PART / 2; YC0 = YP + LINE; YC1 = YC0 + RY; YS0 = YC1 + LINE; YS1 = YS0 + STUD; YE = YS1 + SK + CLAD; YR = (YC0 + YC1) / 2
    YN = YE + YN_EXT; CY0 = YE + .06; CY1 = YN - .08
    zr = lambda x: PL + (XOC - x) * S
    PLH = zr(XHC)
    PY = YS1 - .15
    piers = [(sx * XHC, sy * PY) for sx in (1, -1) for sy in (1, -1)] + [(sx * XOC, y) for sx in (1, -1) for y in (PY, 0.0, -PY)]
    def hanger(lay_add, x0, x1, y):
        if any(abs((x0 + x1) / 2 - px) < .15 + (x1 - x0) / 2 and abs(y - py) < .171 for px, py in piers): return
        lay_add("Connectors", "Joist hanger", box(x0, x1, y - .021, y + .021, L - .212, L - .209))
    def bay(north):
        b = []; a = lambda lay, nm, geo: b.append((lay, nm, geo)); fx = []
        def xstud(xc, y, z_0, z_1, nm="Stud"): a("Wall framing::Studs", nm, box(xc - .07, xc + .07, y - .019, y + .019, z_0, z_1))
        def header(xc, y0, y1, z, nm):
            a("Wall framing::Headers", nm, box(xc + .032, xc + .07, y0, y1, z, z + .184))
            a("Wall framing::Headers", nm, box(xc - .07, xc - .032, y0, y1, z, z + .184))
            a("Wall framing::Headers", "Header spacer", box(xc - .032, xc + .032, y0, y1, z, z + .184))
        nail = [sg * (YP + .019) for sg in (1, -1)] + [sg * (YS0 - .019) for sg in (1, -1)]
        us = oc_range(-YS1 + .019, YS1 - .019, OC)
        # hall wall: the high side, two doors
        z1 = PLH - .076
        for a_, b_ in ((-YS1, -YR - RO), (-YR + RO, YR - RO), (YR + RO, YS1)):
            a("Wall framing::Plates", "Bottom plate", box(XHC - .07, XHC + .07, a_, b_, L, z0))
        a("Wall framing::Plates", "Top plate", box(XHC - .07, XHC + .07, -YS1, YS1, z1, PLH - .038))
        a("Wall framing::Plates", "Double top plate", box(XHC - .07, XHC + .07, -YS1, YS1, PLH - .038, PLH))
        for n_ in nail: xstud(XHC, n_, z0, z1, "Corner stud")
        for c in (YR, -YR):
            for e in (-1, 1):
                xstud(XHC, c + e * (RO + .019), z0, H, "Jack stud"); xstud(XHC, c + e * (RO + .057), z0, z1, "King stud")
            header(XHC, c - RO - .038, c + RO + .038, H, "Door header 2x8")
        for u in us:
            if any(abs(u - c) < RO + .08 for c in (YR, -YR)):
                if any(abs(u - c) < RO - .06 for c in (YR, -YR)) and z1 - (H + .184) > .03: xstud(XHC, u, H + .184, z1, "Cripple stud")
                continue
            if any(abs(u - n_) < .045 for n_ in nail): continue
            xstud(XHC, u, z0, z1)
        # outer wall: the low side, one high vent per room
        z1o = PL - .076; hw = .20; V1 = PL - .268; V0 = V1 - .30
        a("Wall framing::Plates", "Bottom plate", box(XOC - .07, XOC + .07, -YS1, YS1, L, z0))
        a("Wall framing::Plates", "Top plate", box(XOC - .07, XOC + .07, -YS1, YS1, z1o, PL - .038))
        a("Wall framing::Plates", "Double top plate", box(XOC - .07, XOC + .07, -YS1, YS1, PL - .038, PL))
        for n_ in nail: xstud(XOC, n_, z0, z1o, "Corner stud")
        for c in (YR, -YR):
            for e in (-1, 1): xstud(XOC, c + e * (hw + .019), z0, z1o, "Vent king stud")
            header(XOC, c - hw, c + hw, V1, "Vent header 2x8")
            a("Wall framing::Headers", "Vent sill", box(XOC - .07, XOC + .07, c - hw, c + hw, V0 - .038, V0))
            xstud(XOC, c, z0, V0 - .038, "Vent cripple stud")
            dx0, dx1 = XO0, XE; zl_ = V1 - .02
            a("Room vent", "Vent frame", box(dx0, dx1, c - hw, c - hw + .02, V0, V1))
            a("Room vent", "Vent frame", box(dx0, dx1, c + hw - .02, c + hw, V0, V1))
            a("Room vent", "Vent frame", box(dx0, dx1, c - hw + .02, c + hw - .02, zl_, V1))
            a("Room vent", "Vent frame", box(dx0, dx1, c - hw + .02, c + hw - .02, V0, V0 + .02))
            tilt = G.Vector3d(.7071, 0, .7071)
            for i_ in range(4):
                zl = V0 + .02 + (.30 - .04) * (i_ + .5) / 4
                a("Room vent", "Vent louver", beam(P3((dx0 + dx1) / 2, c - hw + .02, zl), P3((dx0 + dx1) / 2, c + hw - .02, zl), .05, .008, tilt))
            a("Flashing", "Vent head flashing", box(XE, XE + .03, c - hw, c + hw, V1 - .002, V1))
        for u in us:
            if any(abs(u - c) < hw + .06 for c in (YR, -YR)): continue
            if any(abs(u - n_) < .045 for n_ in nail): continue
            xstud(XOC, u, z0, z1o)
        # raked walls between hall and outer walls: two ends in 2x6, the partition in 2x4
        for yc, w, kind in ((YS1 - .07, STUD, "End"), (-YS1 + .07, STUD, "End"), (0.0, PART, "Partition")):
            a("Wall framing::Plates", "Bottom plate", box(XS1, XO0, yc - w / 2, yc + w / 2, L, z0))
            a("Wall framing::Plates", "Top plate", beam(P3(XS1, yc, zr(XS1) - .057), P3(XO0, yc, zr(XO0) - .057), w, .038, G.Vector3d.ZAxis))
            a("Wall framing::Plates", "Double top plate", beam(P3(XS1, yc, zr(XS1) - .019), P3(XO0, yc, zr(XO0) - .019), w, .038, G.Vector3d.ZAxis))
            for u in oc_range(XS1 + .019, XO0 - .019, OC):
                a("Wall framing::Studs", "Stud", box(u - .019, u + .019, yc - w / 2, yc + w / 2, z0, zr(u) - .078))
        # envelope
        def pan_x(lay, nm, xf, t, pts): return prism([P3(xf, y, z) for y, z in pts], G.Vector3d(t, 0, 0))
        def pan_y(yf, t, pts): return prism([P3(x, yf, z) for x, z in pts], G.Vector3d(0, t, 0))
        for lay, nm, xf, t, YL in (("Wall sheathing", "Plywood sheathing 12 mm", XS0 - SHEATH, SHEATH, YS1 + SHEATH), ("Weather barrier", "Weather-resistive barrier", XS0 - SK, WRB, YS1 + SK), ("Cladding", "Vertical board cladding", XH, CLAD, YE)):
            p = [(-YL, L)]
            for c in (-YR, YR): p += [(c - RO, L), (c - RO, H), (c + RO, H), (c + RO, L)]
            p += [(YL, L), (YL, PLH), (-YL, PLH)]
            a(lay, nm, pan_x(lay, nm, xf, t, p))
        for lay, nm, xf, t, YL, zb in (("Wall sheathing", "Plywood sheathing 12 mm", XO1, SHEATH, YS1 + SHEATH, L - .209), ("Weather barrier", "Weather-resistive barrier", XO1 + SHEATH, WRB, YS1 + SK, L - .209), ("Cladding", "Vertical board cladding", XO1 + SK, CLAD, YE, L - .20)):
            if t < .005:
                edges = [-YL, -YR - hw, -YR + hw, YR - hw, YR + hw, YL]
                for i_, (a_, b_) in enumerate(zip(edges, edges[1:])):
                    if i_ % 2 == 0: a(lay, nm, pan_x(lay, nm, xf, t, [(a_, zb), (b_, zb), (b_, PL), (a_, PL)]))
                    else:
                        a(lay, nm, pan_x(lay, nm, xf, t, [(a_, zb), (b_, zb), (b_, V0), (a_, V0)]))
                        a(lay, nm, pan_x(lay, nm, xf, t, [(a_, V1), (b_, V1), (b_, PL), (a_, PL)]))
                continue
            sk = pan_x(lay, nm, xf, t, [(-YL, zb), (YL, zb), (YL, PL), (-YL, PL)])
            for c in (YR, -YR):
                cut_ = G.Brep.CreateBooleanDifference(sk, box(xf - .05, xf + t + .05, c - hw, c + hw, V0, V1), TOL)
                if cut_ is None or len(cut_) != 1: raise ValueError("vent opening failed")
                sk = cut_[0]
            a(lay, nm, sk)
        for e in (1, -1):
            for lay, nm, off_, t, x0, x1, zb in (("Wall sheathing", "Plywood sheathing 12 mm", 0.0, SHEATH, XS0, XO1, L - .209), ("Weather barrier", "Weather-resistive barrier", SHEATH, WRB, XS0 - SHEATH, XO1 + SHEATH, L - .209), ("Cladding", "Vertical board cladding", SK, CLAD, XS0 - SK, XO1 + SK, L - .20)):
                yf = YS1 + off_ if e > 0 else -YS1 - off_ - t
                if e == north:
                    xn = XHC + .039
                    p = [(xn, zb), (x1, zb), (x1, zr(x1)), (x0, zr(x0)), (x0, L), (xn, L)]
                else:
                    p = [(x0, zb), (x1, zb), (x1, zr(x1)), (x0, zr(x0))]
                a(lay, nm, pan_y(yf, t, p))
        a("Floor::Subfloor", "Subfloor", box(XS0, XO1, -YS1, YS1, L - .025, L))
        # rooms
        for s in (1, -1):
            c = s * YR
            a("Door thresholds", "Door threshold", box(XH, XS0, c - RO, c + RO, L - .025, L))
            a("Flashing", "Door head flashing", box(XH - .03, XH, c - RO, c + RO, H - .002, H))
            a("Doors", "Door leaf", box(XH, XH + .045, c - LEAF / 2, c + LEAF / 2, L + .005, L + 2.0))
            hy = c - s * LEAF / 2; zs_ = L + .01; q = LEAF * .7071
            a("Door swing", "Door swing arc", G.Arc(P3(XH, c + s * LEAF / 2, zs_), P3(XH - q, hy + s * q, zs_), P3(XH - LEAF, hy, zs_)).ToNurbsCurve())
            tx1 = XC1 - .02; tx0 = XC1 - .20; bx = tx0 - .34
            seat = L + .40
            a("Standard WC::Bowl", "Toilet bowl", disc(bx, c, L, seat - .04, .34, .19))
            a("Standard WC::Seat", "Toilet seat", disc(bx, c, seat - .04, seat, .34, .19))
            a("Standard WC::Tank", "Toilet tank", box(tx0, tx1, c - .225, c + .225, L, L + .76))
            fdx = XC0 + .27
            a("Floor drains", "Floor drain grate", cyl(P3(fdx, c, L - .008), P3(fdx, c, L + .002), .06))
            fx.append(dict(drain=(bx, c), dia=.110, cold=((tx0 + tx1) / 2, c + s * .19), top=L + .60, dtop=L, name="Toilet", branch=True))
            fx.append(dict(drain=(fdx, c), dia=.050, cold=None, top=None, dtop=L - .004, name="Floor", branch=False))
        # roof: one slope, high at the hall, low at the outer wall
        nr = G.Vector3d(S, 0, 1); nr.Unitize(); cdp = ROOF_DP / nr.Z; YX = YE + ROOF_EAVE; X0 = XH - ROOF_EAVE; X1 = XE + ROOF_EAVE
        for x in (XHC, (XHC + XOC) / 2, XOC):
            a("Roof framing::Purlins", "Purlin 2x6", beam(P3(x, -YX, zr(x) + cdp / 2), P3(x, YX, zr(x) + cdp / 2), .038, ROOF_DP, nr))
            for y in (-(YS1 - .07), 0.0, YS1 - .07):
                a("Connectors", "Purlin uplift tie", box(x + .019, x + .022, y - .02, y + .02, zr(x) - .06, zr(x) + .06))
        zt = lambda x: zr(x) + cdp
        a("Roof sheet", "Metal roof sheet", prism([P3(X0, -YX, zt(X0)), P3(X1, -YX, zt(X1)), P3(X1, -YX, zt(X1) + ROOF_TH), P3(X0, -YX, zt(X0) + ROOF_TH)], G.Vector3d(0, 2 * YX, 0)))
        return b, fx
    fixtures = []
    for sx, north in ((1, 1), (-1, -1)):
        b, fx = bay(north)
        xf = G.Transform.Rotation(0.0 if sx > 0 else math.pi, G.Point3d.Origin)
        for lay, nm, geo in b:
            geo.Transform(xf); add(lay, nm, geo)
        for f in fx:
            f["drain"] = (sx * f["drain"][0], sx * f["drain"][1])
            if f["cold"]: f["cold"] = (sx * f["cold"][0], sx * f["cold"][1])
            fixtures.append(f)
    # basins across the north end of the hall
    by, fy_ = CY0 + .19, CY1 - .03
    add("Basin counter", "Basin counter", box(-XH, XH, CY0, CY1, L + .76, L + .80))
    for xa in (-HALL / 4 - .015, HALL / 4 - .015):   # in the gaps between basins, clear of the bowls
        add("Basin counter", "Counter leg", box(xa, xa + .03, CY0 + .02, CY1 - .02, L, L + .76))
    for i in range(4):
        bx = -XH + HALL * (i + .5) / 4
        add("Basins", "Basin", disc(bx, by, L + .72, L + .83, .19, .17))
        add("Faucets", "Faucet", cyl(P3(bx, fy_, L + .80), P3(bx, fy_, L + .98), .012))
        fixtures.append(dict(drain=(bx, by), dia=.050, cold=(bx, fy_), top=L + .80, dtop=L + .72, name="Basin", branch=True))
    hd = (0.0, -.20)
    add("Floor drains", "Floor drain grate", cyl(P3(hd[0], hd[1], L - .008), P3(hd[0], hd[1], L + .002), .06))
    fixtures.append(dict(drain=hd, dia=.050, cold=None, top=None, dtop=L - .004, name="Floor", branch=False))
    # floor: one girder line under each hall wall, carried past the rooms to take the basin end; one under each outer wall
    ky_bay = [(f["drain"][1], f["dia"] / 2) for f in fixtures if abs(f["drain"][0]) > XS0] + [(f["cold"][1], .010) for f in fixtures if f["cold"] and abs(f["cold"][0]) > XS0]
    ky_hall = [(f["drain"][1], f["dia"] / 2) for f in fixtures if abs(f["drain"][0]) < XH] + [(f["cold"][1], .010) for f in fixtures if f["cold"] and abs(f["cold"][0]) < XH]
    for sx in (1, -1):
        xs_ = sorted((sx * XHC, sx * XHC + .038)), sorted((sx * XHC - .038, sx * XHC))
        for x0_, x1_ in xs_:
            add("Floor framing::Girders", "Girder ply 2x8 PT", box(x0_, x1_, -YS1, YN, L - .209, L - .025))
        for p_ in (-.038, 0.0):
            x_ = sx * XOC + p_
            add("Floor framing::Girders", "Girder ply 2x8 PT", box(x_, x_ + .038, -YS1, YS1, L - .209, L - .025))
        a0, a1 = sorted((sx * (XHC + .038), sx * (XOC - .038)))
        for u in oc_range(-YS1 + .019, YS1 - .019, OC):
            u = clear1(u, ky_bay, .019)
            add("Floor framing::Joists", "Floor joist 2x8 PT", box(a0, a1, u - .019, u + .019, L - .209, L - .025))
            hanger(add, a0, a0 + .05, u); hanger(add, a1 - .05, a1, u)
    a0, a1 = -(XHC - .038), XHC - .038
    for u in oc_range(-YS1 + .019, YN - .019, OC):
        u = clear1(u, ky_hall, .019)
        add("Floor framing::Joists", "Deck joist 2x8 PT", box(a0, a1, u - .019, u + .019, L - .209, L - .025))
        hanger(add, a0, a0 + .05, u); hanger(add, a1 - .05, a1, u)
    add("Deck", "Deck surface", box(-XH, XH, -YE, YN, L - .025, L))
    for px, py in piers:
        add("Piers", "Concrete pier", box(px - .15, px + .15, py - .15, py + .15, -.45, L - .247))
        add("Piers", "Sill plate PT", box(px - .15, px + .15, py - .15, py + .15, L - .247, L - .209))
        bx_ = px - .019     # in the ply, not in the seam between plies
        add("Connectors", "Anchor bolt 12 mm", cyl(P3(bx_, py, L - .347), P3(bx_, py, L - .036), .006))
    # guards
    def grd(x0, y0, x1, y1, zb=L):
        n = max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0) / 1.2)))
        for i in range(n + 1):
            t = i / float(n); x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
            add("Guards", "Guard post", box(x - .04, x + .04, y - .04, y + .04, zb, L + .90))
        for z, nm in ((L + .90, "Top rail"), (L + .45, "Mid rail")):
            add("Guards", nm, beam(P3(x0, y0, z), P3(x1, y1, z), .05, .05, G.Vector3d.ZAxis))
    RW = 1.20
    for sx in (1, -1):
        grd(sx * (XH - .04), -YE + .04, sx * (RW / 2 + .06), -YE + .04)
        grd(sx * (XH + .04), YE + .04, sx * (XH + .04), YN - .04, L - .025)
    grd(-XH + .04, YN - .04, XH - .04, YN - .04)
    # ramp off the south end of the hall, wood upper half and slab lower half as run 6
    role = "Entry"; e, lo, hi, s = -YE, -RW / 2, RW / 2, -1
    RUN = L / SLOPE; LD = 1.5; TF, TG = .5, .25
    wv = G.Vector3d(hi - lo, 0, 0); n_ = math.hypot(SLOPE, 1.0); nu, nz = s * SLOPE / n_, 1.0 / n_
    ruz = lambda t, dd: (e + s * RUN * t - nu * dd, L * (1 - t) - nz * dd)
    rp = lambda t, dd, vv: P3(vv, ruz(t, dd)[0], ruz(t, dd)[1])
    add("Ramp::Entry", "Entry ramp deck", prism([rp(0, 0, lo), rp(TF, 0, lo), rp(TF, .032, lo), rp(0, .032, lo)], wv))
    uf = e + s * RUN * TF; zf_ = L * (1 - TF); q_ = lambda u_, z_: P3(lo, u_, z_)
    add("Ramp::Entry", "Entry ramp slab", prism([q_(uf, zf_), q_(e + s * RUN, 0), q_(e + s * (RUN + LD), 0), q_(e + s * (RUN + LD), -.15), q_(e + s * RUN, -.15), q_(uf, zf_ - .15)], wv))
    ztop_ = ruz(TF, .216)[1] - .008
    add("Piers", "Entry ramp stem", box(lo, hi, min(uf, uf - s * .20), max(uf, uf - s * .20), -.45, ztop_))
    ug = e + s * RUN * TG; zg1 = L * (1 - TG) - .036 - .004; zg0 = zg1 - .184
    for p0_, p1_ in ((ug - .038, ug), (ug, ug + .038)):
        add("Floor framing::Girders", "Ramp girder ply 2x8 PT", box(lo, hi, p0_, p1_, zg0, zg1))
    for vp in (lo + .15, hi - .15):
        add("Piers", "Ramp post", box(vp - .075, vp + .075, ug - .075, ug + .075, -.45, zg0))
    nv = G.Vector3d(0, nu, nz); dt = .038 / RUN
    for vp in oc_range(lo + .019, hi - .019, OC):
        for t0_, t1_ in ((0.0, TG - dt), (TG + dt, TF)):
            add("Floor framing::Joists", "Ramp joist 2x8 PT", beam(rp(t0_, .124, vp), rp(t1_, .124, vp), .038, .184, nv))
    for vp in (lo + .03, hi - .03):
        add("Guards", "Ramp handrail", beam(P3(vp, e, L + .90), P3(vp, e + s * RUN, .90), .05, .05, G.Vector3d.ZAxis))
        for t in (0, .2, .4, .6, .8, 1.0):
            up = e + s * RUN * t; zr_ = L * (1 - t)
            add("Guards", "Ramp post", box(vp - .04, vp + .04, up - .04, up + .04, zr_, zr_ + .90))
    # plumbing: buried below the piers, gravity to the chamber and the septic pit
    xm = 0.0; Bk, F = YN, -YE; Y0 = Bk + 1.2
    dmax = max(abs(f["drain"][0] - xm) + (Y0 - f["drain"][1]) for f in fixtures)
    zc = -.55 - .02 * dmax; zy = lambda y: zc + .02 * (Y0 - y)
    br = {}
    for f in fixtures:
        fx_, fy = f["drain"]; zs = zy(fy) + .02 * abs(fx_ - xm); r = f["dia"] / 2
        add("Drains", "Floor drain riser" if f["name"] == "Floor" else f["name"] + " drain riser", cyl(P3(fx_, fy, f["dtop"]), P3(fx_, fy, zs), r))
        if f["branch"] and abs(fx_ - xm) > .01:
            k = (round(fy, 4), fx_ > xm)
            if k not in br or abs(fx_) > abs(br[k][0]): br[k] = (fx_, fy, zs, r, f["name"])
    for fx_, fy, zs, r, nm in br.values():
        add("Drains", nm + " drain branch", cyl(P3(fx_, fy, zs), P3(xm, fy, zy(fy)), r))
    ymin = min(f["drain"][1] for f in fixtures)
    add("Drains", "Collector", cyl(P3(xm, ymin, zy(ymin)), P3(xm, Y0, zc), .055))
    add("Inspection chamber", "Inspection chamber", box(xm - .40, xm + .40, Y0 - .40, Y0 + .40, zc - .30, 0))
    pozo_y = Bk + 10.0; Ro = 1.40; Ri = 1.25; zf = -3.29; main_end = pozo_y + .20; dist = main_end - (Y0 + .40)
    add("Main drain", "Main drain to septic pit", cyl(P3(xm, Y0 + .40, zc), P3(xm, main_end, zc - .025 * dist), .055))
    pcx, pcy = xm, pozo_y + Ro
    shell = G.Brep.CreateBooleanDifference(cyl(P3(pcx, pcy, zf), P3(pcx, pcy, -.20), Ro), cyl(P3(pcx, pcy, zf + .20), P3(pcx, pcy, -.10), Ri), TOL)
    if shell is None or len(shell) != 1: raise ValueError("pit shell failed")
    add("Septic pit", "Septic pit shell", shell[0])
    add("Septic pit", "Septic pit cover slab", cyl(P3(pcx, pcy, -.20), P3(pcx, pcy, 0), Ro))
    APEX = zr(XH - ROOF_EAVE) + ROOF_DP * 1.005 + ROOF_TH; vy = Bk + .70
    add("Vents", "Building vent stack", cyl(P3(xm, vy, zy(vy)), P3(xm, vy, APEX + .70), .0315))
    add("Vents", "Septic pit vent", cyl(P3(pcx + .9, pcy, -.20), P3(pcx + .9, pcy, 2.50), .0315))
    colds = [f for f in fixtures if f["cold"]]
    drains_x = [(f["drain"][0], f["dia"]) for f in fixtures]
    xw = xm + .30; zw = -.48; ym = F - 10.0 - RUN - LD
    while any(abs(xw - x_) < dia / 2 + .0125 + .03 for x_, dia in drains_x): xw += .05
    add("Water meter", "Water meter box", box(xw - .20, xw + .20, ym - .25, ym, -.30, 0))
    ymax = max(f["cold"][1] for f in colds)
    add("Cold water", "Cold water meter riser", cyl(P3(xw, ym - .05, zw), P3(xw, ym - .05, -.25), .0125))
    add("Cold water", "Cold water main", cyl(P3(xw, ym - .05, zw), P3(xw, ymax, zw), .0125))
    cb = {}
    for f in colds:
        fx_, fy = f["cold"]
        add("Cold water", "Cold water riser", cyl(P3(fx_, fy, zw), P3(fx_, fy, f["top"]), .010))
        if abs(fx_ - xw) > .01:
            k = (round(fy, 4), fx_ > xw)
            if k not in cb or abs(fx_ - xw) > abs(cb[k][0] - xw): cb[k] = (fx_, fy)
    for fx_, fy in cb.values():
        add("Cold water", "Cold water branch", cyl(P3(xw, fy, zw), P3(fx_, fy, zw), .010))
    far = pozo_y + 2 * Ro + .5
    add("Truck access", "Truck access strip", box(xm - 1.5, xm + 1.5, far, far + 6.0, -.02, 0))
    return items

def generate_h():
    out = []; move = G.Transform.Translation(180.0, -480.0, 0)
    for lay, name, geo in option_h_items():
        geo.Transform(move); out.append(("Toilet Building Run 10::Option H::%s" % lay, name, geo))
    return out


# ---- Run 13, option J slab on grade: run 12 (option I) with the stalls on a concrete slab on grade, finished floor 150 mm above grade. ----
# No piers, floor framing, deck framing, long ramp or deck guards. Front deck becomes an at-grade concrete apron, 1.70 m wide, with a short
# 1:12 transition at the local -y (world east) end where r12 had its ramp. Drains run below the slab in trenches, by gravity to the chamber
# and the septic pit. Grade is z = 0. Built in the run 12 frame (door wall along y), then turned 90 degrees so the row runs along world x.
RX_I, RY_I, NROOM, DECK_W, RAMP_W = 1.50, 1.12, 4, 1.70, 1.20   # stall depth, stall width (user), apron width, (r12 ramp width, unused)
FL_J = .15                     # finished slab top above grade
SLAB_T, SUB_T = .10, .15       # slab thickness, compacted gravel sub-base under the slab
EDGE_W, EDGE_D = .30, .40      # thickened edge: width, depth from slab top
APRON_T, APRON_SUB = .10, .10  # apron and transition slab, gravel under them
THRESH, XFALL = .020, .02      # threshold lip at the doors, apron cross-fall away from the building
COVER = .40                    # minimum cover to the crown of the 110 mm drain outside the building (assumed)
FALL, MAIN_FALL = .02, .025    # collector fall, main drain fall (as r12)
PIPE_RI = .055 - .0032         # 110 x 3.2 PVC inside radius: invert = centreline - PIPE_RI
TR_W, TR_W50, BED = .40, .30, .10   # trench widths for 110 and 50 mm pipe, bedding below the pipe
def option_j_items():
    items = []; add = lambda lay, nm, geo: items.append((lay, nm, geo))
    L = FL_J
    S = ROOF_S; PL = L + MINH + FIN; H = L + 2.04; z0 = L + .038
    XH = 0.0; XS0 = XH + CLAD + SK; XS1 = XS0 + STUD; XHC = (XS0 + XS1) / 2
    XC0 = XS1 + LINE; XC1 = XC0 + RX_I; XO0 = XC1 + LINE; XO1 = XO0 + STUD; XOC = (XO0 + XO1) / 2; XE = XO1 + SK + CLAD
    PIT = RY_I + 2 * LINE + PART
    cs = [(i - (NROOM - 1) / 2.0) * PIT for i in range(NROOM)]
    parts = [(cs[i] + cs[i + 1]) / 2 for i in range(NROOM - 1)]
    YS0 = cs[-1] + RY_I / 2 + LINE; YS1 = YS0 + STUD; YE = YS1 + SK + CLAD
    XD = XH - DECK_W
    zr = lambda x: PL + (XOC - x) * S; PLH = zr(XHC)
    def xstud(xc, y, z_0, z_1, nm="Stud"): add("Wall framing::Studs", nm, box(xc - .07, xc + .07, y - .019, y + .019, z_0, z_1))
    def header(xc, y0, y1, z, nm):
        add("Wall framing::Headers", nm, box(xc + .032, xc + .07, y0, y1, z, z + .184))
        add("Wall framing::Headers", nm, box(xc - .07, xc - .032, y0, y1, z, z + .184))
        add("Wall framing::Headers", "Header spacer", box(xc - .032, xc + .032, y0, y1, z, z + .184))
    nail = [p + sg * (PART / 2 + .019) for p in parts for sg in (1, -1)] + [sg * (YS0 - .019) for sg in (1, -1)]
    us = oc_range(-YS1 + .019, YS1 - .019, OC)
    # door wall: the high side, one door per stall
    z1 = PLH - .076
    edges = [-YS1] + [v for c in cs for v in (c - RO, c + RO)] + [YS1]
    for a_, b_ in zip(edges[0::2], edges[1::2]):
        add("Wall framing::Plates", "Bottom plate", box(XHC - .07, XHC + .07, a_, b_, L, z0))
    add("Wall framing::Plates", "Top plate", box(XHC - .07, XHC + .07, -YS1, YS1, z1, PLH - .038))
    add("Wall framing::Plates", "Double top plate", box(XHC - .07, XHC + .07, -YS1, YS1, PLH - .038, PLH))
    for n_ in nail: xstud(XHC, n_, z0, z1, "Corner stud")
    for c in cs:
        for e in (-1, 1):
            xstud(XHC, c + e * (RO + .019), z0, H, "Jack stud"); xstud(XHC, c + e * (RO + .057), z0, z1, "King stud")
        header(XHC, c - RO - .038, c + RO + .038, H, "Door header 2x8")
    for u in us:
        if any(abs(u - c) < RO + .08 for c in cs):
            if any(abs(u - c) < RO - .06 for c in cs) and z1 - (H + .184) > .03: xstud(XHC, u, H + .184, z1, "Cripple stud")
            continue
        if any(abs(u - n_) < .045 for n_ in nail): continue
        xstud(XHC, u, z0, z1)
    # back wall: the low side, one high vent per stall
    z1o = PL - .076; hw = .20; V1 = PL - .268; V0 = V1 - .30
    add("Wall framing::Plates", "Bottom plate", box(XOC - .07, XOC + .07, -YS1, YS1, L, z0))
    add("Wall framing::Plates", "Top plate", box(XOC - .07, XOC + .07, -YS1, YS1, z1o, PL - .038))
    add("Wall framing::Plates", "Double top plate", box(XOC - .07, XOC + .07, -YS1, YS1, PL - .038, PL))
    for n_ in nail: xstud(XOC, n_, z0, z1o, "Corner stud")
    for c in cs:
        for e in (-1, 1): xstud(XOC, c + e * (hw + .019), z0, z1o, "Vent king stud")
        header(XOC, c - hw, c + hw, V1, "Vent header 2x8")
        add("Wall framing::Headers", "Vent sill", box(XOC - .07, XOC + .07, c - hw, c + hw, V0 - .038, V0))
        xstud(XOC, c, z0, V0 - .038, "Vent cripple stud")
        dx0, dx1 = XO0, XE
        add("Room vent", "Vent frame", box(dx0, dx1, c - hw, c - hw + .02, V0, V1))
        add("Room vent", "Vent frame", box(dx0, dx1, c + hw - .02, c + hw, V0, V1))
        add("Room vent", "Vent frame", box(dx0, dx1, c - hw + .02, c + hw - .02, V1 - .02, V1))
        add("Room vent", "Vent frame", box(dx0, dx1, c - hw + .02, c + hw - .02, V0, V0 + .02))
        tilt = G.Vector3d(.7071, 0, .7071)
        for i_ in range(4):
            zl = V0 + .02 + (.30 - .04) * (i_ + .5) / 4
            add("Room vent", "Vent louver", beam(P3((dx0 + dx1) / 2, c - hw + .02, zl), P3((dx0 + dx1) / 2, c + hw - .02, zl), .05, .008, tilt))
        add("Flashing", "Vent head flashing", box(XE, XE + .03, c - hw, c + hw, V1 - .002, V1))
    for u in us:
        if any(abs(u - c) < hw + .06 for c in cs): continue
        if any(abs(u - n_) < .045 for n_ in nail): continue
        xstud(XOC, u, z0, z1o)
    # raked walls: two ends in 2x6, three partitions in 2x4
    for yc, w in [(YS1 - .07, STUD), (-YS1 + .07, STUD)] + [(p, PART) for p in parts]:
        add("Wall framing::Plates", "Bottom plate", box(XS1, XO0, yc - w / 2, yc + w / 2, L, z0))
        add("Wall framing::Plates", "Top plate", beam(P3(XS1, yc, zr(XS1) - .057), P3(XO0, yc, zr(XO0) - .057), w, .038, G.Vector3d.ZAxis))
        add("Wall framing::Plates", "Double top plate", beam(P3(XS1, yc, zr(XS1) - .019), P3(XO0, yc, zr(XO0) - .019), w, .038, G.Vector3d.ZAxis))
        for u in oc_range(XS1 + .019, XO0 - .019, OC):
            add("Wall framing::Studs", "Stud", box(u - .019, u + .019, yc - w / 2, yc + w / 2, z0, zr(u) - .078))
    # envelope
    def pan_x(xf, t, pts): return prism([P3(xf, y, z) for y, z in pts], G.Vector3d(t, 0, 0))
    def pan_y(yf, t, pts): return prism([P3(x, yf, z) for x, z in pts], G.Vector3d(0, t, 0))
    for lay, nm, xf, t, YL in (("Wall sheathing", "Plywood sheathing 12 mm", XS0 - SHEATH, SHEATH, YS1 + SHEATH), ("Weather barrier", "Weather-resistive barrier", XS0 - SK, WRB, YS1 + SK), ("Cladding", "Vertical board cladding", XH, CLAD, YE)):
        p = [(-YL, L)]
        for c in cs: p += [(c - RO, L), (c - RO, H), (c + RO, H), (c + RO, L)]
        p += [(YL, L), (YL, PLH), (-YL, PLH)]
        add(lay, nm, pan_x(xf, t, p))
    # skins lap 25 mm down over the slab edge (r12 lapped the rim joist)
    for lay, nm, xf, t, YL, zb in (("Wall sheathing", "Plywood sheathing 12 mm", XO1, SHEATH, YS1 + SHEATH, L - .025), ("Weather barrier", "Weather-resistive barrier", XO1 + SHEATH, WRB, YS1 + SK, L - .025), ("Cladding", "Vertical board cladding", XO1 + SK, CLAD, YE, L - .025)):
        if t < .005:
            ed = [-YL] + [v for c in cs for v in (c - hw, c + hw)] + [YL]
            for i_, (a_, b_) in enumerate(zip(ed, ed[1:])):
                if i_ % 2 == 0: add(lay, nm, pan_x(xf, t, [(a_, zb), (b_, zb), (b_, PL), (a_, PL)]))
                else:
                    add(lay, nm, pan_x(xf, t, [(a_, zb), (b_, zb), (b_, V0), (a_, V0)]))
                    add(lay, nm, pan_x(xf, t, [(a_, V1), (b_, V1), (b_, PL), (a_, PL)]))
            continue
        sk = pan_x(xf, t, [(-YL, zb), (YL, zb), (YL, PL), (-YL, PL)])
        for c in cs:
            cut_ = G.Brep.CreateBooleanDifference(sk, box(xf - .05, xf + t + .05, c - hw, c + hw, V0, V1), TOL)
            if cut_ is None or len(cut_) != 1: raise ValueError("vent opening failed")
            sk = cut_[0]
        add(lay, nm, sk)
    for e in (1, -1):
        for lay, nm, off_, t, x0, x1, zb in (("Wall sheathing", "Plywood sheathing 12 mm", 0.0, SHEATH, XS0, XO1, L - .025), ("Weather barrier", "Weather-resistive barrier", SHEATH, WRB, XS0 - SHEATH, XO1 + SHEATH, L - .025), ("Cladding", "Vertical board cladding", SK, CLAD, XS0 - SK, XO1 + SK, L - .025)):
            yf = YS1 + off_ if e > 0 else -YS1 - off_ - t
            add(lay, nm, pan_y(yf, t, [(x0, zb), (x1, zb), (x1, zr(x1)), (x0, zr(x0))]))
    # slab on grade: 100 mm slab over the full framing footprint, 300 wide thickened edge 400 deep from the top, gravel sub-base inside the edge
    zsb = L - SLAB_T; zg = zsb - SUB_T; ze = L - EDGE_D
    add("Slab::Slab", "Slab on grade 100 mm", box(XS0, XO1, -YS1, YS1, zsb, L))
    ix0, ix1, iy = XS0 + EDGE_W, XO1 - EDGE_W, YS1 - EDGE_W
    for a_ in ((XS0, ix0, -YS1, YS1), (ix1, XO1, -YS1, YS1), (ix0, ix1, -YS1, -iy), (ix0, ix1, iy, YS1)):
        add("Slab::Thickened edge", "Slab thickened edge", box(a_[0], a_[1], a_[2], a_[3], ze, zsb))
    add("Sub-base", "Slab gravel sub-base", box(ix0, ix1, -iy, iy, zg, zsb))
    add("Excavation", "Slab sub-base excavation", box(ix0, ix1, -iy, iy, zg, 0))
    for a_ in ((XS0, ix0, -YS1, YS1), (ix1, XO1, -YS1, YS1), (ix0, ix1, -YS1, -iy), (ix0, ix1, iy, YS1)):
        add("Excavation", "Thickened edge excavation", box(a_[0], a_[1], a_[2], a_[3], ze, 0))
    # bottom plates of the outer walls bolted to the slab: 150 from each end, 1.20 m or less between
    def bolts(axis, k, a, b):
        n = max(1, int(math.ceil((b - a - .30) / 1.2))) if b - a > .60 else 0
        us_ = [(a + b) / 2] if n == 0 else [a + .15 + (b - a - .30) * i / float(n) for i in range(n + 1)]
        for u in us_:
            p0, p1 = (P3(k, u, L - .15), P3(k, u, L + .07)) if axis == "y" else (P3(u, k, L - .15), P3(u, k, L + .07))
            add("Connectors", "Anchor bolt 12 mm", cyl(p0, p1, .006))
    for a_, b_ in zip(edges[0::2], edges[1::2]): bolts("y", XHC, a_, b_)
    bolts("y", XOC, -YS1, YS1)
    for yc in (YS1 - .07, -YS1 + .07): bolts("x", yc, XS1, XO0)
    # stalls
    fixtures = []
    for c in cs:
        add("Door thresholds", "Door threshold", box(XH, XS0, c - RO, c + RO, L - THRESH, L))
        add("Flashing", "Door head flashing", box(XH - .03, XH, c - RO, c + RO, H - .002, H))
        add("Doors", "Door leaf", box(XH, XH + .045, c - LEAF / 2, c + LEAF / 2, L + .005, L + 2.0))
        hy = c - LEAF / 2; zs_ = L + .01; q = LEAF * .7071
        add("Door swing", "Door swing arc", G.Arc(P3(XH, c + LEAF / 2, zs_), P3(XH - q, hy + q, zs_), P3(XH - LEAF, hy, zs_)).ToNurbsCurve())
        tx1 = XC1 - .02; tx0 = XC1 - .20; bx = tx0 - .34; seat = L + .40
        add("Standard WC::Bowl", "Toilet bowl", disc(bx, c, L, seat - .04, .34, .19))
        add("Standard WC::Seat", "Toilet seat", disc(bx, c, seat - .04, seat, .34, .19))
        add("Standard WC::Tank", "Toilet tank", box(tx0, tx1, c - .225, c + .225, L, L + .76))
        fdx = XC0 + .27
        add("Floor drains", "Floor drain grate", cyl(P3(fdx, c, L - .008), P3(fdx, c, L + .002), .06))
        fixtures.append(dict(c=c, bx=bx, fdx=fdx, cold=((tx0 + tx1) / 2, c + .19)))
    # roof over the stalls, high at the deck
    nr = G.Vector3d(S, 0, 1); nr.Unitize(); cdp = ROOF_DP / nr.Z; YX = YE + ROOF_EAVE; X0r = XH - ROOF_EAVE; X1r = XE + ROOF_EAVE
    for x in (XHC, (XHC + XOC) / 2, XOC):
        add("Roof framing::Purlins", "Purlin 2x6", beam(P3(x, -YX, zr(x) + cdp / 2), P3(x, YX, zr(x) + cdp / 2), .038, ROOF_DP, nr))
        for y in [-(YS1 - .07), YS1 - .07] + parts:
            add("Connectors", "Purlin uplift tie", box(x + .019, x + .022, y - .02, y + .02, zr(x) - .06, zr(x) + .06))
    zt = lambda x: zr(x) + cdp
    add("Roof sheet", "Metal roof sheet", prism([P3(X0r, -YX, zt(X0r)), P3(X1r, -YX, zt(X1r)), P3(X1r, -YX, zt(X1r) + ROOF_TH), P3(X0r, -YX, zt(X0r) + ROOF_TH)], G.Vector3d(0, 2 * YX, 0)))
    # apron: at-grade concrete in front of the doors, butting the slab edge, 20 mm below the floor at the threshold, 2% fall away from the
    # building. Gravel under it; excavation only where the gravel goes below grade. No guards: the most it stands above grade is 130 mm.
    za0 = L - THRESH; za = lambda x: za0 - XFALL * (XS0 - x)
    def sec(y, top0, top1, t):
        # closed x-z section at y, across the apron, top falling from top0 at the slab edge to top1 at the outer edge, t thick
        return G.Polyline([P3(XS0, y, top0), P3(XD, y, top1), P3(XD, y, top1 - t), P3(XS0, y, top0 - t), P3(XS0, y, top0)]).ToNurbsCurve()
    def loft(c0, c1):
        lf = G.Brep.CreateFromLoft([c0, c1], G.Point3d.Unset, G.Point3d.Unset, G.LoftType.Straight, False)
        if not lf or len(lf) != 1: raise ValueError("loft failed")
        c = cap(lf[0])
        if c.SolidOrientation == G.BrepSolidOrientation.Inward: c.Flip()
        return c
    a0, a1 = za(XS0), za(XD)
    gb0, gb1 = a0 - APRON_T - APRON_SUB, a1 - APRON_T - APRON_SUB
    dig = lambda y: G.Polyline([P3(XS0, y, 0), P3(XD, y, 0), P3(XD, y, gb1), P3(XS0, y, gb0), P3(XS0, y, 0)]).ToNurbsCurve()
    add("Apron", "Concrete apron 100 mm", loft(sec(-YE, a0, a1, APRON_T), sec(YE, a0, a1, APRON_T)))
    add("Sub-base", "Apron gravel sub-base", loft(sec(-YE, a0 - APRON_T, a1 - APRON_T, APRON_SUB), sec(YE, a0 - APRON_T, a1 - APRON_T, APRON_SUB)))
    add("Excavation", "Apron excavation", loft(dig(-YE), dig(YE)))
    # 1:12 transition off the -y end, where r12 had its ramp: from the apron edge down to grade over TL
    TL = math.ceil(a0 * 12 / .05) * .05; ye1 = -YE - TL
    add("Apron", "Apron transition 1:12", loft(sec(-YE, a0, a1, APRON_T), sec(ye1, 0, 0, APRON_T)))
    add("Sub-base", "Apron gravel sub-base", loft(sec(-YE, a0 - APRON_T, a1 - APRON_T, APRON_SUB), sec(ye1, -APRON_T, -APRON_T, APRON_SUB)))
    add("Excavation", "Apron excavation", loft(dig(-YE), sec(ye1, 0, 0, APRON_T + APRON_SUB)))
    # drains: a collector in a trench under the slab, below the toilets, falling to the middle and out under the back wall's thickened
    # edge to the chamber and the septic pit. Depth set by COVER to the crown where the pipe leaves the slab (x = XO1); 2% back up from there.
    XB = fixtures[0]["bx"]; X0 = XE + 1.2; cmax = max(abs(f["c"]) for f in fixtures)
    zc = -COVER - .055 - FALL * (X0 - XO1); zp = lambda dist: zc + FALL * dist
    # r12 rule, for the comparison only
    zc12 = -.55 - .02 * (cmax + (X0 - XB) + (XB - fixtures[0]["fdx"]))
    for f in fixtures:
        c = f["c"]; dz = zp(abs(c) + X0 - XB); fz = zp(abs(c) + X0 - XB + XB - f["fdx"])
        add("Drains", "Toilet drain riser", cyl(P3(XB, c, L), P3(XB, c, dz), .055))
        add("Drains", "Floor drain riser", cyl(P3(f["fdx"], c, L - .004), P3(f["fdx"], c, fz), .025))
        add("Drains", "Floor drain branch", cyl(P3(f["fdx"], c, fz), P3(XB, c, dz), .025))
    for sg in (1, -1):
        add("Drains", "Collector", cyl(P3(XB, sg * cmax, zp(cmax + X0 - XB)), P3(XB, 0, zp(X0 - XB)), .055))
    add("Drains", "Collector", cyl(P3(XB, 0, zp(X0 - XB)), P3(X0, 0, zc), .055))
    add("Inspection chamber", "Inspection chamber", box(X0 - .40, X0 + .40, -.40, .40, zc - .30, 0))
    # pit: same working depth below the inlet as r12, so it moves by the same amount as the chamber
    pozo_x = XE + 10.0; Ro = 1.40; Ri = 1.25; zf = -3.29 + (zc - zc12); main_end = pozo_x + .20; dist = main_end - (X0 + .40)
    add("Main drain", "Main drain to septic pit", cyl(P3(X0 + .40, 0, zc), P3(main_end, 0, zc - MAIN_FALL * dist), .055))
    # excavation: trenches from the bottom of whatever is already dug (gravel under the slab, the thickened edge) or from grade, down to
    # BED below the pipe; chamber and pit dug 150 / 300 mm wider than the structure and 100 mm below it for a blinding layer
    def trench(nm, p0, p1, z0c, z1c, r, w, ztop):
        v = G.Vector3d(p1.X - p0.X, p1.Y - p0.Y, 0); n_ = G.Vector3d(-v.Y, v.X, 0); n_.Unitize(); n_ *= w / 2
        q = lambda p, z: P3(p.X - n_.X, p.Y - n_.Y, z)
        add("Excavation", nm, prism([q(p0, ztop), q(p1, ztop), q(p1, z1c - r - BED), q(p0, z0c - r - BED)], n_ * 2))
    d0 = lambda x: X0 - x   # path length to the chamber along the x-run
    xe0 = XO1 - EDGE_W
    for sg in (1, -1):
        y0_, y1_ = sg * (cmax + .20), sg * TR_W / 2
        trench("Drain trench", P3(XB, y0_, 0), P3(XB, y1_, 0), zp(abs(y0_) + d0(XB)), zp(abs(y1_) + d0(XB)), .055, TR_W, zg)
    for xa, xb, zt_ in ((XB - TR_W / 2, xe0, zg), (xe0, XO1, ze), (XO1, X0 - .55, 0.0)):
        trench("Drain trench", P3(xa, 0, 0), P3(xb, 0, 0), zp(d0(xa)), zp(d0(xb)), .055, TR_W, zt_)
    for f in fixtures:
        c = f["c"]; dz = zp(abs(c) + X0 - XB); fz = zp(abs(c) + X0 - XB + XB - f["fdx"])
        trench("Drain trench", P3(f["fdx"] - TR_W50 / 2, c, 0), P3(XB - TR_W / 2, c, 0), fz, dz, .025, TR_W50, zg)
    zm = lambda x: zc - MAIN_FALL * (x - (X0 + .40))
    trench("Drain trench", P3(X0 + .55, 0, 0), P3(pozo_x - .30, 0, 0), zm(X0 + .55), zm(pozo_x - .30), .055, TR_W, 0.0)
    add("Excavation", "Inspection chamber excavation", box(X0 - .55, X0 + .55, -.55, .55, zc - .40, 0))
    pcx, pcy = pozo_x + Ro, 0.0
    add("Excavation", "Septic pit excavation", cyl(P3(pcx, pcy, zf - .10), P3(pcx, pcy, 0), Ro + .30))
    levels = dict(FL=L, slab_t=SLAB_T, edge_bottom=ze, gravel_bottom=zg, apron_door=a0, apron_outer=a1, transition_len=TL,
                  wc1_cl=zp(cmax + X0 - XB), exit_cl=zp(X0 - XO1), chamber_cl=zc, pozo_in_cl=zc - MAIN_FALL * dist, pozo_floor=zf,
                  chamber_cl_r12=zc12, wc1_cl_r12=zc12 + .02 * (cmax + X0 - XB), exit_cl_r12=zc12 + .02 * (X0 - XO1),
                  pozo_in_cl_r12=zc12 - .025 * dist, pozo_floor_r12=-3.29, pipe_ri=PIPE_RI)
    LEVELS.clear(); LEVELS.update(levels)
    shell = G.Brep.CreateBooleanDifference(cyl(P3(pcx, pcy, zf), P3(pcx, pcy, -.20), Ro), cyl(P3(pcx, pcy, zf + .20), P3(pcx, pcy, -.10), Ri), TOL)
    if shell is None or len(shell) != 1: raise ValueError("pit shell failed")
    add("Septic pit", "Septic pit shell", shell[0])
    add("Septic pit", "Septic pit cover slab", cyl(P3(pcx, pcy, -.20), P3(pcx, pcy, 0), Ro))
    APEX = zr(XH - ROOF_EAVE) + ROOF_DP * 1.005 + ROOF_TH; vx = XE + .70
    add("Vents", "Building vent stack", cyl(P3(vx, 0, zp(X0 - vx)), P3(vx, 0, APEX + .70), .0315))
    add("Vents", "Septic pit vent", cyl(P3(pcx, pcy + .9, -.20), P3(pcx, pcy + .9, 2.50), .0315))
    # cold water: from the Water meter beyond the deck side, under the building, a branch along the tanks
    # 320 mm down: under the thickened edges (bottom -0.25) and above the collector crown where it crosses
    yw = .30; zw = -.32; mx = XD - 10.0; XCW = fixtures[0]["cold"][0]
    add("Water meter", "Water meter box", box(mx - .25, mx, yw - .20, yw + .20, -.30, 0))
    add("Cold water", "Cold water meter riser", cyl(P3(mx - .05, yw, zw), P3(mx - .05, yw, -.25), .0125))
    add("Cold water", "Cold water main", cyl(P3(mx - .05, yw, zw), P3(XCW, yw, zw), .0125))
    cy_ = [f["cold"][1] for f in fixtures]
    add("Cold water", "Cold water branch", cyl(P3(XCW, yw, zw), P3(XCW, max(cy_), zw), .010))
    add("Cold water", "Cold water branch", cyl(P3(XCW, yw, zw), P3(XCW, min(cy_), zw), .010))
    for y in cy_: add("Cold water", "Cold water riser", cyl(P3(XCW, y, zw), P3(XCW, y, L + .60), .010))
    far = pozo_x + 2 * Ro + .5
    add("Truck access", "Truck access strip", box(far, far + 6.0, -1.5, 1.5, -.02, 0))
    return items

LEVELS = {}
def generate_j():
    # same place as r12, so it replaces r12 in a copy of the r12 site
    out = []; xf = G.Transform.Multiply(G.Transform.Translation(180.0, -540.0, 0), G.Transform.Rotation(math.pi / 2, G.Point3d.Origin))
    for lay, name, geo in option_j_items():
        geo.Transform(xf); out.append(("Toilet Building Run 13::Option J::%s" % lay, name, geo))
    return out
