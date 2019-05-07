#!/usr/bin/env python

# Z riser assembly, this is a rack which is designed to mount with a gear and stepper motor
# There is also a holder to enclose the assembly

import cadquery
import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props, display
from cqparts.constraint import Mate, Fixed, Coincident
from cqparts.utils.geometry import CoordSystem

# from cqparts_fastners.bolts import Bolt
from cqparts.display import display


class ZRiser(cqparts.Part):
    """This is the vertical geared rack that lifts the head up and down"""

    _render = render_props(template="blue", alpha=0.4)

    width = 5.2
    depth = 6.7
    length = 120

    def riser_rod(self, clearance=0):
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(0, 0, 6))
            .rect(self.depth + clearance, self.width + clearance)
            .extrude(self.length)
        )
        return r

    def riser_foot(self):
        """The foot has a holder to bolt on a gripper/appendage and also extends out to act as a stop
        to a microswitch on the actuator"""
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(-6, 0, 0))
            .rect(31, self.width)
            .extrude(7)
        )
        r = r.faces("<Y").workplane().transformed(offset=(0, 0, 0)).hole(3.3)
        r = r.faces("<Y").workplane().transformed(offset=(10, 0, 0)).hole(3.3)
        return r

    def make(self):
        r = self.riser_rod()
        r = r.union(self.riser_foot())
        # r = r.union(self.riser_foot(r.faces("<Z").workplane(centerOption="CenterOfBoundBox")))
        # r = r.workplane("<Z").offset(10, 10).box(6.7, 20, 5.2)
        return r

    def get_cutout(self, clearance=0.3):
        r = self.riser_rod(clearance=clearance)
        return r

    def apply_cutout(self, part):
        part.local_obj = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.get_cutout()
        )

    @property
    def mate_holder_demo(self):
        """This should mount the riser in a demo position on the holder"""
        return Mate(self, CoordSystem((0, 0, self.length / 3.0), (1, 0, 0), (0, 0, 1)))


class ZRiserHolder(cqparts.Part):
    """This is the holder for a Z riser It will need to be integrated into a support structure"""

    _render = render_props(template="pink", alpha=0.2)
    wall = 4
    length = 45
    surround_length = (
        10
    )  # Length of surround around riser at each end to keep it caged in

    def __init__(self, riser):
        super(ZRiserHolder, self).__init__()
        self.riser_width = riser.width
        self.riser_depth = riser.depth

    def riser_channel(self, wall=4):
        w = self.wall
        d = self.riser_depth
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(-w / 2, 0, 0))
            .rect(self.riser_depth + w, self.riser_width + w * 2)
            .extrude(self.length)
        )
        return r

    def riser_surround(self, z_offset=0):
        """The foot has a holder to bolt on a gripper/appendage and also extends out to act as a stop
        to a microswitch on the actuator"""
        w = self.wall
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=((self.riser_depth + w) / 2.0, 0, z_offset))
            .rect(w, self.riser_width + w * 2)
            .extrude(self.surround_length)
        )
        return r

    def surround_bevel(self, z_offset=0):
        """This is a bevel so that the top riser surround can be printed with a 45 degree
        chamfer without suport"""
        w = self.wall
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(self.riser_depth / 2.0, 0, z_offset-w))
            .rect(0.2, self.riser_width + w * 2)
            .workplane(offset=w).center(w/2.0,0)
            .rect(w, self.riser_width + w * 2)
            .loft(combine=True)
        )
        return r

    def make(self):
        r = self.riser_channel()
        r = r.union(self.riser_surround())
        r = r.union(self.riser_surround(z_offset=self.length - self.surround_length))
        r = r.union(self.surround_bevel(z_offset=self.length - self.surround_length))
        # r = r.union(self.riser_foot(r.faces("<Z").workplane(centerOption="CenterOfBoundBox")))
        # r = r.workplane("<Z").offset(10, 10).box(6.7, 20, 5.2)
        return r

    def get_cutout(self, clearance=0.3):
        r = self.riser_rod(clearance=clearance)
        return r

    def apply_cutout(self, part):
        part.local_obj = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.get_cutout()
        )


class ZRiserAssembly(cqparts.Assembly):
    """Z riser assembly (both riser and holder)"""

    # default appearance
    _render = render_props(template="green", alpha=0.2)

    def make_components(self):
        riser = ZRiser()
        return {"riser": riser, "riser_holder": ZRiserHolder(riser)}

    def make_constraints(self):
        return [
            Fixed(self.components["riser_holder"].mate_origin, CoordSystem()),
            Coincident(  # mount
                self.components["riser"].mate_holder_demo,
                self.components["riser_holder"].mate_origin,
            ),
        ]

    def make_alterations(self):
        """cut out channel for riser"""
        holder = self.components["riser_holder"]
        self.components["riser"].apply_cutout(holder)


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ == "__cq_freecad_module__":
    # r = ZRiser()
    # riser = ZRiser()
    # r = ZRiserHolder(riser)
    r = ZRiserAssembly()
    display(r)
