from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults, Camera
set_port(3939)

import build123d as bd
print_rect = bd.Rectangle(140,140)#.move(loc=bd.Location((140/2,140/2)))
printer_volume = bd.extrude(print_rect, amount=140)


def ring_line(thickness:float=5, height:float=10, radius:float=10, start:float=0, straight_inner:bool=False) -> bd.Line:
    rad = radius + start
    with bd.BuildLine() as _line:
        l = bd.Line((start,0), (start+thickness,0))
        u = bd.Line((start,height),(start+thickness,height))
        if straight_inner:
            bd.Line(l@0, u@0)
        else:
            bd.RadiusArc(l@0, u@0, -(rad))
        
        bd.RadiusArc(l@1, u@1, -(rad+thickness))
    return _line.line

def ring_sketch(rings:int=4,thickness:float=5,height:float=10, radius:float=10,clearance:float=0.6) -> bd.Sketch:
    with bd.BuildSketch(mode=bd.Mode.PRIVATE) as _sketch:
        for i in range(rings):
            bd.add(ring_line(thickness=thickness, height=height, radius=radius, start=i*(thickness+clearance), straight_inner=i==0))
            bd.make_face()
    
    return _sketch


def gyro(rings:int=4, ring_thickness:float=5, height:float=10, start_radius:float=10, clearance:float=0.4,) -> bd.Part:
    with bd.BuildPart() as _part:
        bd.add(ring_sketch(rings=rings, thickness=ring_thickness, height=height, radius=start_radius, clearance=clearance))
        bd.revolve(axis=bd.Axis.Y)
        with bd.Locations(_part.faces().sort_by(bd.Axis.Y)[0]):
            bd.Hole(start_radius/4)
    return _part

part = gyro(rings=4, clearance=0.6, start_radius=5)
show(
    part,
    reset_camera=Camera.KEEP
)
part.part.export_stl("pip-gyroscope/gyro.stl")
part.part.export_step("pip-gyroscope/gyro.step")