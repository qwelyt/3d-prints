from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults, Camera
set_port(3939)

import build123d as bd

printer_volume = bd.extrude(bd.Rectangle(140,140).move(loc=bd.Location((140/2,140/2))), amount=140)
constraint_lines = [
    bd.Line((0-15,0),(120-17-15,140)),
    bd.Line((0,0),(120-17,140)),
    bd.Line((12,0),(112,140)), 
    bd.Line((17,0),(120,140)),
    bd.Line((17+15,0),(120+15,140)), 
    bd.Line((0,130),(130,0)), 
    bd.Line((0,150),(150,0)), 
    bd.Line((0,15),(140,15)),
    bd.Line((0,26),(140,26)),
    bd.Line((125,0),(125,140)),
    bd.Line((0,40),(140,40)),
    bd.Line((5,0),(5,140)),
    bd.Line((8,0),(8,140)),
    bd.Line((135,0),(135,140)),
    bd.Line((0,135),(140,135)),
    bd.Line((0,5),(140,5)),
    bd.Line((0,130),(140,130)),
]
# %%
def constraint_point(a:bd.Line,b:bd.Line)->bd.Vector:
    _a = constraint_lines[a]
    _b = constraint_lines[b]
    val = _a.edge().intersections(bd.Plane.XY, _b.edge())
    # print(val)
    return val[0]

def cpoint(p:(int,int)) -> bd.Vector:
    return constraint_point(p[0],p[1])

def cline(a:(int,int),b:(int,int))->bd.Line:
    return bd.Line(cpoint(a),cpoint(b))

def shape():
    with bd.BuildLine() as _line:
        cline((0,10),(1,10))
        frontHook = cline((0,10),(0,8))
        innerLine = cline((1,10), (1,8))
        innerArc = bd.JernArc(innerLine@1, innerLine%1, 6.85, 180)
        restLine = bd.Line(innerArc@1, cpoint((3,16)))
        upperArc = bd.JernArc(restLine@1, restLine%1, 12.4, -140)
        # upperArc = bd.RadiusArc(restLine@1, cpoint((13,16)), 14)
        bd.Line(upperArc@1, cpoint((7,13)))
        bd.RadiusArc(cpoint((7,13)), cpoint((9,15)), 10)
        bottomLine = cline((9,15),(2,15))
        # bd.RadiusArc(frontHook@1, bottomLine@1, 10, False)
        #frontArc = bd.JernArc(bottomLine@1, bottomLine%1, 13.4,-115)
        #bd.Line(frontHook@1, frontArc@1)
        bd.RadiusArc(bottomLine@1, frontHook@1, 14.7)


        # bd.ThreePointArc(cpoint((1,8)),cpoint((2,7)),cpoint((3,8)))
        # bd.JernArc(cpoint((1,8)),cpoint((1,8)),-7,180)
    return _line.line

def shape_old():
    pts = [
        (5,25),
        (20,40),
        (35,40),
        (20,25)
    ]
    with bd.BuildLine() as line:
        hook = bd.Polyline(
            (5,25),
            (20,40),
            (35,40),
            (20,25)
        )
        innerArc = bd.JernArc(hook@1, hook%1, 7, 180)
        rest = bd.Line((innerArc@1),(125,125))
        upperArc = bd.JernArc(rest@1, rest%1, 7, -130)
        frontLowerArc = bd.ThreePointArc(
            (hook @ 0),
            (5,15),
            (20,5)
        )
        backLowerArc = bd.ThreePointArc(
            (120,5),
            (130,10),
            (135,20),
        )
        bd.Line((frontLowerArc@1),(backLowerArc@0))
        bd.Line((upperArc@1),(backLowerArc@1))
        
    return line.line

def cut_outs() -> list[bd.Sketch]:
    ret = []
    with bd.BuildSketch() as a:
        with bd.BuildLine():
            bd.Polyline(
                cpoint((4,5)),
                cpoint((4,7)),
                cpoint((5,7)),
                close=True
                )
        bd.make_face()
        bd.fillet(a.vertices(),2)
    ret.append(a)
    with bd.BuildSketch() as b:
        with bd.BuildLine():
            bd.Polyline(
                cpoint((4,6)),
                cpoint((4,9)),
                cpoint((6,9)),
                close=True
                )
        bd.make_face()
        bd.fillet(b.vertices(),2)
    ret.append(b)

    return ret

def sketch():
    with bd.BuildSketch() as sketch:
        bd.add(shape())
        bd.make_face()
        for t in cut_outs():
            bd.add(t, mode=bd.Mode.SUBTRACT)
        # print(sketch.max_fillet(sketch.vertices))
    return sketch

def stand():
    with bd.BuildPart() as part:
        bd.add(sketch())
        bd.extrude(amount=10)
        
    return part


part = stand()
show(
    part,
    # cut_outs(),
    # shape(),
    # constraint_lines,
    printer_volume, 
    reset_camera=Camera.KEEP
)
part.part.export_stl("stand.stl")
part.part.export_step("stand.step")
# %%