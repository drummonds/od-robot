import cadquery
import cqparts
from cqparts.display import render_props, display
from cqparts.constraint import Mate, Fixed, Coincident
from cqparts.utils.geometry import CoordSystem


from support import ScrewHolder


class BarHolder(cqparts.Part):
    """
    This is a mount to hold a threaded screw.  With a spacer to make sure the selected
    screw goes the requested depth into the wood below.
    """

    length = 15
    wall = 4.0
    shaft_diameter = 8.3
    # default appearance
    _render = render_props(color=(200, 200, 200))  # dark grey

    def make(self):
        l = self.length
        radius = (self.shaft_diameter / 2.0) + self.wall
        r = cadquery.Workplane("XY").circle(radius).extrude(l)
        # add holes for rod
        r = r.faces(">Z").workplane().hole(self.shaft_diameter)
        return r

    def get_cutout(self, clearance=0.5):
        # A cylinder with a equal clearance on every face
        return (
            cadquery.Workplane("XY", origin=(0, 0, clearance + 10))
            .circle((self.shaft_diameter / 2.0) + clearance)
            .extrude(-self.length - (2 * clearance))
        )

    def apply_cutout(self, part):
        # Cut space for screw hole from part this is fitted into
        part.local_obj = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.get_cutout()
        )


class Beam(cqparts.Part):
    # default appearance
    _render = render_props(template="blue", alpha=0.5)
    length = 140
    height = 25
    width = 30
    thickness = 4

    def make(self):
        (L, H, W, t) = (self.length, self.height, self.width, self.thickness)
        pts = [
            (0, H / 2.0),
            (W / 2.0, H / 2.0),
            (W / 2.0, (H / 2.0 - t)),
            (t / 2.0, (H / 2.0 - t)),
            (t / 2.0, (t - H / 2.0)),
            (W / 2.0, (t - H / 2.0)),
            (W / 2.0, H / -2.0),
            (0, H / -2.0),
        ]
        r = cadquery.Workplane("front").polyline(pts).close().extrude(L)
        return r


class Base(cqparts.Part):
    """
    This is a test base to mount the hole onto
    Need to mount at three depths to test clearning on thin, drilling on large depth and
    stop drilling if too large
    """

    # default appearance
    _render = render_props(template="red", alpha=0.5)

    def make(self):
        r = cadquery.Workplane("XY").rect(25, 35).extrude(4)
        return r

    # Construct mating points
    @property
    def mate_one(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 6, 0),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )

    @property
    def mate_two(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, -11, 0),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )

    @property
    def mate_beam1(self):
        return Mate(
            self, CoordSystem(origin=(0, 17.5, 0), xDir=(0, -1, 0), normal=(0, 0, 1))
        )

    @property
    def mate_beam2(self):
        return Mate(
            self,
            CoordSystem(origin=(10, 17.5, 128), xDir=(0, -1, 0), normal=(-1, 0, 0)),
        )

    @property
    def mate_holder(self):
        return Mate(
            self,
            CoordSystem(origin=(-90, 17.5, 128), xDir=(1, 0, 0), normal=(0, -1, 0)),
        )


class TestBase(cqparts.Assembly):
    # default appearance
    _render = render_props(template="green", alpha=0.2)

    def make_components(self):
        beam2 = Beam()
        beam2.length = 105
        return {
            "base": Base(),
            "mount1": ScrewHolder(),
            "mount2": ScrewHolder(),
            "beam1": Beam(),
            "beam2": beam2,
            "holder": BarHolder(),
        }

    def make_constraints(self):
        return [
            Fixed(self.components["base"].mate_origin, CoordSystem()),
            Coincident(
                self.components["mount1"].mate_origin, self.components["base"].mate_one
            ),
            Coincident(
                self.components["mount2"].mate_origin, self.components["base"].mate_two
            ),
            Coincident(
                self.components["beam1"].mate_origin, self.components["base"].mate_beam1
            ),
            Coincident(
                self.components["beam2"].mate_origin, self.components["base"].mate_beam2
            ),
            Coincident(
                self.components["holder"].mate_origin, self.components["base"].mate_holder
            ),
        ]

    def make_alterations(self):
        # cut out wheel wells
        base = self.components["base"]
        self.components["mount1"].apply_cutout(base)
        self.components["mount2"].apply_cutout(base)
        beam = self.components["beam2"]
        self.components["holder"].apply_cutout(beam)


print("Name = {}".format(__name__))
# ------------------- Display Result -------------------
# Could also export to another format
if __name__ == "__cq_freecad_module__":
    # r = Beam()
    # r = BarHolder()
    r = TestBase()
    display(r)
