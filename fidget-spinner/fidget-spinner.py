
from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults, Camera
set_port(3939)

import build123d as bd
print_rect = bd.Rectangle(140,140)#.move(loc=bd.Location((140/2,140/2)))
printer_volume = bd.extrude(print_rect, amount=140)


def shape(hole_diameter:float=22, bridge_thickness:float=3) -> bd.Sketch:
    hole_r=hole_diameter/2
    r = hole_r*1.3
    polar_r = hole_diameter+bridge_thickness
    with bd.BuildSketch() as _sketch:
        center = bd.Circle(r)
        locs = bd.PolarLocations(radius=polar_r, count=3).locations
        for loc in locs:
            o = bd.Circle(r).move(loc)
            bd.make_hull(center.edges()+o.edges())
        bd.fillet(_sketch.vertices(), radius=r)
        with bd.PolarLocations(radius=polar_r, count=3):
            bd.Circle(hole_r, mode=bd.Mode.SUBTRACT)
        bd.Circle(hole_r, mode=bd.Mode.SUBTRACT)
    return _sketch

def spinner(height:float=7, hole_diameter:float=22, brigde_thickness:float=3):
    with bd.BuildPart() as _part:
        bd.add(shape(hole_diameter=hole_diameter, bridge_thickness=brigde_thickness))
        bd.extrude(amount=height)
        edges = _part.edges().filter_by(bd.GeomType.CIRCLE,reverse=True).filter_by(bd.Axis.Z, reverse=True)
        edges += _part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.SortBy.RADIUS)[8:]
        print(len(edges))
        print(edges[0].length)
        bd.fillet(edges, radius=2)
        # for edge in edges:
        #     locs = edge.distribute_locations(6, positions_only=True)
        #     with bd.LocationList(locs):
        #         bd.Hole(radius=1)


        # bd.fillet(_part.edges().filter_by(bd.GeomType.CIRCLE, reverse=True), radius=1)
    return _part


part = spinner(height=7, hole_diameter=22.3, brigde_thickness=3)
show(
    part
    , reset_camera=Camera.KEEP
    )
part.part.export_stl("fidget-spinner/fidget-spinner.stl")
part.part.export_step("fidget-spinner/fidget-spinner.step")