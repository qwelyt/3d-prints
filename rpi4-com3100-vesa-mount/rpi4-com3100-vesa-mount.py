from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults, Camera
set_port(3939)

import build123d as bd
print_rect = bd.Rectangle(140,140)#.move(loc=bd.Location((140/2,140/2)))
printer_volume = bd.extrude(print_rect, amount=140)

def base():
    with bd.BuildSketch() as _sketch:
        bd.Rectangle(130, 130)
        with bd.GridLocations(200,200,2,1):
            bd.Circle(radius=60, mode=bd.Mode.SUBTRACT)
        with bd.GridLocations(200,200,1,2):
            bd.Circle(radius=60, mode=bd.Mode.SUBTRACT)

        bd.fillet(_sketch.vertices(), radius=5)

        with bd.GridLocations(100, 100, 2,2):
            bd.Circle(radius=2, mode=bd.Mode.SUBTRACT)
        
    return _sketch

def mount():
    with bd.BuildPart() as _part:
        bd.add(base())
        bd.extrude(amount=5)
        bd.fillet(_part.edges().filter_by(bd.GeomType.CIRCLE, reverse=True), radius=1)
        bd.chamfer(_part.faces().sort_by(bd.Axis.Z).last.edges().filter_by(bd.GeomType.CIRCLE), 2,1)

        with bd.BuildSketch(bd.Plane(_part.faces().sort_by(bd.Axis.Z).last)):
            with bd.Locations((0,-(56/2)-3.5), (0,(56/2)+3.5)):
                bd.Rectangle(88, 4)
            
        holder = bd.extrude(amount=8)

        with bd.BuildSketch(bd.Plane(holder.faces().sort_by(bd.Axis.Y)[6])):
            with bd.Locations((-88/2+50/2+7,1.59)):
                bd.Rectangle(50,1.5)
        top_hold = bd.extrude(amount=2)
        bd.fillet(top_hold.edges(), radius=0.5)
        with bd.BuildSketch(bd.Plane(top_hold.faces().sort_by(bd.Axis.X)[0])):
            with bd.Locations((0.5,-1)):
                bd.RegularPolygon(radius=1.5, side_count=3, rotation=70)
        bd.extrude(amount=-90,mode=bd.Mode.SUBTRACT)

        with bd.BuildSketch(bd.Plane(holder.faces().sort_by(bd.Axis.Y)[5])):
            with bd.Locations((-88/2+50/2+7,-1.59)):
                bd.Rectangle(50,1.5)
        hook = bd.extrude(amount=5)

        with bd.BuildSketch(bd.Plane(holder.faces().sort_by(bd.Axis.X)[1])):
            with bd.Locations((-2.2,-2)):
                bd.RegularPolygon(radius=6,side_count=3,rotation=-20)
        bd.extrude(amount=-90,mode=bd.Mode.SUBTRACT)

        bd.fillet(holder.edges(), radius=0.9)
        bd.fillet(hook.edges(), radius=0.5)

    
    return _part

part = mount()
show(
    part
    # , part.wires().filter_by(bd.GeomType.CIRCLE, reverse=True)[1].vertices()
    , bd.Box(88,56, 25).located(bd.Location((0,0,(25/2)+6)))
    , print_rect
    , reset_camera=Camera.KEEP
)

# part.part.export_step(__file__.replace(".py", ".step"))
# part.part.export_stl(__file__.replace(".py", ".stl"))