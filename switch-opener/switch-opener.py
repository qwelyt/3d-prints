# %%
from ocp_vscode import (
    show,
    show_object,
    reset_show,
    set_port,
    set_defaults,
    get_defaults,
    Camera,
)

set_port(3939)
set_defaults(reset_camera=Camera.KEEP)

import build123d as bd


keycap_opener_orig = bd.import_stl("KeyCap_Opener.stl")
keycap_opener_right = keycap_opener_orig.moved(bd.Location((20, 0, 2)))
keycap_opener_back = keycap_opener_orig.moved(bd.Location((0, 20, 2)))


mkswestl = bd.import_stl("mkswe.stl")


# %%
def sketch_from_wires(wires):
    with bd.BuildSketch() as skt:
        for w in wires:
            with bd.BuildLine():
                bd.add(w)
            bd.make_face()

    return skt.sketch


def mkswe_sthlm_logo(
    logo_size=None,
    base_thickness=20,
    ring_thickness=30,
    caps_thickness=10,
    caps_taper=30,
    caps_base_thickness=None,
):
    def logo_2d(logo_size):
        mks = bd.import_svg("mkswe_sthlm.svg")
        keys = mks[0:7] + mks[25:]
        towerMain = mks[24:25]
        arch = mks[23:24]
        towerDetails = mks[7:23]

        bad14 = sketch_from_wires([mks[14]])
        ls14bb = bad14.bounding_box()
        with bd.BuildSketch() as cutter:
            with bd.Locations(bd.Location(ls14bb.center())):
                bd.Rectangle(ls14bb.size.X, ls14bb.size.Y)
            bd.add(bad14, mode=bd.Mode.SUBTRACT)
        with bd.BuildSketch() as expected_face:
            with bd.Locations(bd.Location(ls14bb.center())):
                bd.Rectangle(ls14bb.size.X, ls14bb.size.Y)
            bd.add(cutter.sketch, mode=bd.Mode.SUBTRACT)

        towerDetails[14] = expected_face.sketch.wire()
        towerDetails.append(mks[21])

        with bd.BuildSketch() as cut_tower:
            bd.add(sketch_from_wires(towerMain))
            bd.add(sketch_from_wires(towerDetails), mode=bd.Mode.SUBTRACT)

        with bd.BuildSketch() as ring_skt:
            bd.add(sketch_from_wires(arch))

        with bd.BuildSketch() as keys_skt:
            for k in keys:
                with bd.BuildLine():
                    bd.add(k)
                bd.make_face()

        # Move to 0,0 (ish)
        bb = cut_tower.sketch.bounding_box()
        mv_x = (bb.min.X + bb.max.X) / 2
        mv_y = (bb.min.Y + bb.max.Y) / 2

        tower = cut_tower.sketch.translate((mv_x * -1, mv_y * -1, 0))
        caps = keys_skt.sketch.translate((mv_x * -1, mv_y * -1, 0))
        ring = ring_skt.sketch.translate((mv_x * -1, mv_y * -1, 0))

        if logo_size is None:
            return (tower, ring, caps)
        else:
            biggest_dim = max(
                max(tower.bounding_box().size.to_tuple()),
                max(ring.bounding_box().size.to_tuple()),
                max(caps.bounding_box().size.to_tuple()),
            )
            scale_factor = logo_size / biggest_dim
            return (
                tower.scale(scale_factor),
                ring.scale(scale_factor),
                caps.scale(scale_factor),
            )

    _2d = logo_2d(logo_size)

    with bd.BuildPart() as base:
        bd.add(_2d[0])
        bd.extrude(amount=base_thickness)

    with bd.BuildPart() as ring:
        bd.add(_2d[1])
        bd.extrude(amount=ring_thickness)

    def extrude_caps(faces, thickness, taper):
        cap_fix = []
        for k in faces:
            with bd.BuildPart() as cf:
                with bd.BuildSketch():
                    bd.add(k)
                bd.extrude(amount=thickness, taper=taper)
            if cf.part.bounding_box().center().Z < 0:
                mcf = cf.part.mirror(bd.Plane.XY)
                cap_fix.append(mcf)
            else:
                cap_fix.append(cf)
        return cap_fix

    extruded_caps = extrude_caps(_2d[2].faces(), caps_thickness, caps_taper)
    with bd.BuildPart() as caps:
        if caps_base_thickness:
            bd.add(extrude_caps(_2d[2].faces(), caps_base_thickness, 0))
            with bd.Locations(bd.Location((0, 0, caps_base_thickness))):
                bd.add(extruded_caps)
        else:
            bd.add(extruded_caps)

    return (base.part, ring.part, caps.part, _2d)


# %%

msl = mkswe_sthlm_logo(
    logo_size=20,
    base_thickness=1.5,
    ring_thickness=2.3,
    caps_thickness=0.5,
    caps_taper=10,
    caps_base_thickness=1.7,
)
show(msl)

# %%


def opener(text_thickness=1):
    z_faces = lambda p: p.faces().sort_by(bd.Axis.Z)
    with bd.BuildPart() as prt:

        # Lower box
        with bd.BuildSketch():
            bd.Rectangle(18, 18)
        bd.extrude(amount=15)

        # Fix nice rounded corners
        bd.fillet(prt.edges().filter_by(bd.Axis.Z), 2)
        bd.fillet(z_faces(prt)[0].edges(), 2)

        # Fix box for small pegs
        first_top = prt.faces().sort_by(bd.Axis.Z)[-1]
        with bd.BuildSketch(first_top):
            bd.Rectangle(14.5, 15)
        bd.extrude(amount=4.5)
        bd.chamfer(z_faces(prt)[-1].edges(), 1.7)

        # Larger pegs, 0.5mm higher than the small pegs
        with bd.BuildSketch(first_top):
            bd.Rectangle(8, 18)
        bd.extrude(amount=5)

        top = z_faces(prt)[-1]
        bd.chamfer(top.edges().filter_by(bd.Axis.X), 1.7)

        left = prt.faces().sort_by(bd.Axis.X)[0]
        front = prt.faces().sort_by(bd.Axis.Y)[0]

        # Main cut in the center where the switch goes
        with bd.BuildSketch(top):
            bd.Rectangle(15, 7.2)
            bd.Rectangle(10.8, 14)
        bd.extrude(amount=-16, mode=bd.Mode.SUBTRACT)

        # Cut the corners at the top
        with bd.BuildSketch(top):
            with bd.GridLocations(13, 15.3, 2, 2):
                bd.Rectangle(8, 4)
        bd.extrude(amount=-6, mode=bd.Mode.SUBTRACT)

        # Notch in the larger pegs that grip the bottom housing
        with bd.BuildSketch(left):
            with bd.Locations(bd.Location((0, -9.55, 0))):
                with bd.GridLocations(13.2, 1, 2, 1):
                    bd.Circle(1 / 1.5)
        bd.extrude(amount=-20, mode=bd.Mode.SUBTRACT)

        # Bottom hole
        bd.Hole(2.5)

        # Things are nicer when a bit rounded, no?
        bd.fillet(
            prt.edges().filter_by_position(bd.Axis.Z, 13, 20),
            0.1,
        )
        bd.fillet(
            prt.edges()
            .filter_by_position(bd.Axis.Z, -10, 13)
            .filter_by(bd.Axis.Z, reverse=True),
            0.5,
        )

        # Time to brand this opener!
        with bd.BuildSketch(front):
            bd.Text(
                "Stockholm",
                font_size=2.3,
                font_style=bd.FontStyle.BOLD,
                align=(bd.Align.CENTER, bd.Align.MIN),
            )
            with bd.Locations(bd.Location((0, -0.3, 0))):
                bd.Text(
                    "Meetup 8",
                    font_size=2.3,
                    font_style=bd.FontStyle.BOLD,
                    align=(bd.Align.CENTER, bd.Align.MAX),
                )
            with bd.Locations(bd.Location((0, -5, 0))):
                bd.Text(
                    "2024-02-24",
                    font_size=2,
                    font_style=bd.FontStyle.BOLD,
                    align=(bd.Align.CENTER, bd.Align.MAX),
                )
        bd.extrude(amount=text_thickness)

    return prt.part


# svg = __file__.replace("switch-opener.py", "atom.svg")
# print(svg)
# t = bd.import_svg(svg)
part = opener()  # .move(bd.Location((0, 0, -2)))
# %%
show(
    part,
    keycap_opener_back,
    keycap_opener_right,
)
# %%
# logo = mkswe_sthlm_logo(base_tickness=30)
logo = mkswe_sthlm_logo(
    logo_size=15,
    base_thickness=1.7,
    ring_thickness=2,
    caps_thickness=0.3,
    caps_taper=30,
    caps_base_thickness=1.8,
)
slogo = logo[0] + logo[1] + logo[2]
rslogo = (
    slogo.rotate(bd.Axis.X, 90).rotate(bd.Axis.Z, 180).move(bd.Location((0, 8, 10)))
)
# %%

show(
    part,
    rslogo,
)

# %%
with bd.BuildPart() as mkswe_opener:
    bd.add(part)
    bd.add(rslogo)

show(mkswe_opener)
mkswe_opener.part.export_step(__file__.replace(".py", "_mkswe_sthlm_8.step"))
mkswe_opener.part.export_stl(__file__.replace(".py", "_mkswe_sthlm_8.stl"))
# %%
atom = bd.import_svg("atom.svg")
print(type(atom))
print(atom)
with bd.BuildPart() as msp:
    with bd.BuildSketch():
        bd.add(atom.wires())
        bd.add(atom.faces())
    bd.extrude(amount=1)
show(msp, atom.wires(), atom.faces())
# %%
mks = bd.import_svg("mkswe_sthlm.svg")
print(mks)
print(len(mks))
# 23+24 is the big piece, cut all other shapes out of that?
# %%
ls = []
for i, w in enumerate(mks):
    with bd.BuildSketch() as skt:
        with bd.BuildLine():
            bd.add(w)
        bd.make_face()
    skt.label = str(i)
    ls.append(skt)
show(ls)
# %%
print(ls[14].sketch.bounding_box())
print(ls[14].sketch.location)
print(ls[14].sketch.faces()[0].location)

ls14bb = ls[14].sketch.bounding_box()
with bd.BuildSketch() as cutter:
    with bd.Locations(bd.Location(ls14bb.center())):
        bd.Rectangle(ls14bb.size.X, ls14bb.size.Y)
    bd.add(ls[14].sketch, mode=bd.Mode.SUBTRACT)
with bd.BuildSketch() as expected_face:
    with bd.Locations(bd.Location(ls14bb.center())):
        bd.Rectangle(ls14bb.size.X, ls14bb.size.Y)
    bd.add(cutter.sketch, mode=bd.Mode.SUBTRACT)
show(cutter, ls[14], expected_face)
print(expected_face)
print(expected_face.sketch)
print(expected_face.sketch.wire())

# %%
keys = mks[0:7] + mks[25:]
archTower = mks[23:25]
towerDetails = mks[7:23]
towerDetails[14] = expected_face.sketch.wire()
towerDetails.append(mks[21])


def sketch_from_wires(wires):
    with bd.BuildSketch() as skt:
        for w in wires:
            with bd.BuildLine():
                bd.add(w)
            bd.make_face()

    return skt.sketch


keys_skt = sketch_from_wires(keys)
archTower_skt = sketch_from_wires(archTower)
towerDetails_skt = sketch_from_wires(towerDetails)

with bd.BuildSketch() as sss:
    bd.add(archTower_skt)
    bd.add(towerDetails_skt, mode=bd.Mode.SUBTRACT)

show(
    mks,
    keys,
    archTower,
    towerDetails,
    keys_skt,
    archTower_skt,
    towerDetails_skt,
    sss,
)

# %%
keys_p = []
for k in keys:
    with bd.BuildPart() as ppp:
        with bd.BuildSketch():
            with bd.BuildLine():
                bd.add(k)
            bd.make_face()
        bd.extrude(amount=10, dir=bd.Axis.Z.direction, taper=30)
    if ppp.part.bounding_box().center().Z < 0:
        np = ppp.part.mirror(bd.Plane.XY)
        keys_p.append(np)
    else:
        keys_p.append(ppp.part)

show(
    keys_p,
)
# %%
with bd.BuildPart() as base:
    with bd.BuildSketch():
        bd.add(sss)
    bd.extrude(amount=10)

with bd.BuildPart() as button:
    for k in keys_p:
        bd.add(k)

with bd.BuildPart() as logo:
    bd.add(base.part)
    bd.add(button.part.move(bd.Location((0, 0, 10))))
show(
    # keys_p,
    # sss,
    base,
    button.part.move(bd.Location((0, 0, 10))),
    logo,
)
logo.part.export_step(__file__.replace(".py", "_mkswelogo.step"))
logo.part.export_stl(__file__.replace(".py", "_mkswelogo.stl"))
# %%
p = mks[0:23]
q = mks[25:40]
smaller = p + q
with bd.BuildSketch() as details:
    for w in smaller:
        with bd.BuildLine():
            bd.add(w)
        bd.make_face()
with bd.BuildSketch() as bigger:
    for w in mks[23:25]:
        with bd.BuildLine():
            bd.add(w)
        bd.make_face()

with bd.BuildPart() as pp:
    bd.add(bigger.sketch)
    bd.extrude(amount=10)
    bd.add(details.sketch)
    bd.extrude(amount=12)

show(details, bigger, pp)

# pp.part.export_step(__file__.replace(".py", "_mkswelogo.step"))
# pp.part.export_stl(__file__.replace(".py", "_mkswelogo.stl"))
# %%
sub = mks[0:24]

with bd.BuildPart() as mksp:
    with bd.BuildSketch() as mkss:
        for i, w in enumerate(sub):
            with bd.BuildLine():
                bd.add(w)
            bd.make_face()
    bd.extrude(amount=30)

# with bd.BuildPart() as mksp:
#     for w in sub:
#         try:
#             print(w)
#             with bd.BuildLine():
#                 bd.add(w)
#             with bd.BuildSketch():
#                 bd.Rectangle(9,9)
#             bd.sweep()
#         except:
#             print("Did badly")
show(mks, mkss, mksp)
# %%
with bd.BuildPart() as ppp:
    bd.Box(10, 20, 30)
    with bd.BuildSketch(ppp.faces().sort_by(bd.Axis.X)[0]):
        bd.Text(
            "Meetup9", font_size=8, align=(bd.Align.CENTER, bd.Align.MIN), rotation=-90
        )
        bd.Text(
            "2024-02-24",
            font_size=8,
            align=(bd.Align.CENTER, bd.Align.MAX),
            rotation=-90,
        )
    bd.extrude(amount=2)

show(ppp)
