#!/usr/bin/env python

# Microswitches with models on how to mount them

import cadquery
import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props, display
from cqparts.constraint import Mate, Fixed, Coincident
from cqparts.utils.geometry import CoordSystem

# -------------------- New Start ----------------------
from cqparts_fasteners.male import MaleFastenerPart

# from cqparts_fastners.bolts import Bolt
from cqparts.display import display


from rods_04 import ThreadedRod
from stepper import Stepper_28BYJ_48, StepperGear
from z_riser import ZRiser, ZRiserHolder

from nuts_bolts import Bolt


class M2RollerSwitch(cqparts.Part):

    _render = render_props(template="cyan", alpha=0.4)
    y_bolt_offset = 4
    thickness = 5.7

    def make(self):
        points = [
            (0, 6.35),
            (12.82, 6.35),
            (12.82, 0),
            (4.6, 0),
            (4.2, -0.5),
            (4.0, -0.5),
            (3.6, 0),
            (2, 0),
        ]
        r = (
            cadquery.Workplane("front")
            .transformed(offset=(0, 0, 0), rotate=(0, 0, 0))
            .polyline(points)
            .lineTo(2, -0.3)
            .lineTo(15, -4.6)
            .lineTo(15, -6.5)
            .threePointArc((12.5, -9), (10, -6.5))
            .lineTo(10, -3.5)
            .lineTo(0, 0)
            .close()
            .extrude(self.thickness)
        )
        yo = self.y_bolt_offset
        r = r.faces(">Z").workplane().transformed(offset=(2.3, yo, 0)).hole(2.1)
        r = r.faces(">Z").workplane().transformed(offset=(-4.7, yo, 0)).hole(2.1)
        return r

    # Construct mating points
    @property
    def mate_bolt_left(self):
        """Left bolt hole mate position (on top of microswitch for bolt to go through"""
        return Mate(
            self,
            CoordSystem(
                origin=(3, self.y_bolt_offset + 1.0, self.thickness / 2.0),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )

    @property
    def mate_bolt_right(self):
        """Right bolt hole mate position (on top of microswitch for bolt to go through"""
        return Mate(
            self,
            CoordSystem(
                origin=(10, self.y_bolt_offset + 1.0, self.thickness / 2.0),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )


class M2RollerSwitchAssembly(cqparts.Assembly):
    """This is the microswitch with bolts.
    It is designed for an M" x 12 mm bolt with the nut burried 2mm"""

    # default appearance
    _render = render_props(template="blue", alpha=0.2)

    def __init__(
        self,
        show_cutout=False
    ):
        super(M2RollerSwitchAssembly, self).__init__()
        self.show_cutout = show_cutout


    def make_components(self):
        bolt1 = Bolt(size="M2", length=14, embedded_length=3, show_cutout=self.show_cutout)
        bolt2 = Bolt(size="M2", length=14, embedded_length=3, show_cutout=self.show_cutout)
        # bolt1._render = render_props(template="cyan", alpha=0.5)
        # bolt2._render=render_props(template="magenta", alpha=0.5)
        parts = {"switch": M2RollerSwitch(), "bolt1": bolt1, "bolt2": bolt2}
        return parts

    def make_constraints(self):
        constraints = [
            Fixed(self.components["switch"].mate_origin, CoordSystem((0, 0, 0))),
            Coincident(
                self.components["bolt1"].mate_head_end(),
                self.components["switch"].mate_bolt_right,
            ),
            # Fixed(self.components["bolt1"].mate_origin, CoordSystem((0,0,0))),
            Coincident(
                self.components["bolt2"].mate_head_end(),
                self.components["switch"].mate_bolt_left,
            ),
            # Fixed(self.components["bolt2"].mate_origin, CoordSystem((10,10,10))),
            # Coincident(
            #     self.components["bolt2"].mate_head_end(),
            #     self.components["switch"].mate_bolt_right,
            # ),
        ]
        return constraints

    # def get_cutout(self, clearance=0.3):
    #     r = self.cutout.make()
    #     r = r.union(self.thread.make())
    #     return r
    #
    # def apply_cutout(self, part):
    #     part.local_obj = part.local_obj.cut(
    #         (self.world_coords - part.world_coords) + self.get_cutout()
    #     )
    def apply_cutout(self, part):
        # Cut wheel & axle from given part
        bolt1 = self.components['bolt1']
        bolt2 = self.components['bolt2']
        local_obj = part.local_obj
        local_obj = local_obj \
            .cut((bolt1.world_coords - part.world_coords) + bolt1.get_cutout()) \
            .cut((bolt2.world_coords - part.world_coords) + bolt2.get_cutout())
        part.local_obj = local_obj


class MicroswitchHolder(cqparts.Part):
    """This is the holder for the testing microswitches, aim to mount both top and bottom"""

    _render = render_props(template="red", alpha=0.2)

    def make(self):
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(0, 0, 0))
            .rect(40, 20, centered=False)
            .extrude(20)
        )
        return r


class MicroswitchDisplay(cqparts.Assembly):
    """This is a test aseembly of a holder and microswitches
    switch 1 is just as it comes, switch two will be mated to a vertical wall and the nut inserts cutout"""

    # default appearance
    _render = render_props(template="green", alpha=0.2)

    def make_components(self):
        parts = {
            "base": MicroswitchHolder(),
            "switch1": M2RollerSwitchAssembly(show_cutout=True),
            "switch2": M2RollerSwitchAssembly(),
        }
        return parts

    def make_constraints(self):
        constraints = [
            Fixed(self.components["base"].mate_origin, CoordSystem()),
            Fixed(self.components["switch1"].mate_origin, CoordSystem((0, -30, 0))),
            Fixed(
                self.components["switch2"].mate_origin,
                CoordSystem((0, 15, 0), xDir=(0, 0, 1), normal=(-1, 0, 0)).rotated((90, 0, 0)),)
            # Fixed(  # Space out nuts
            #     self.components["switch2"].mate_origin,
            #     CoordSystem((0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0)),
            # ),
        ]
        return constraints

    def make_alterations(self):
        # Making the mounting holes for the microswitch
        holder = self.components["base"]
        self.components['switch2'].apply_cutout(holder)


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ == "__cq_freecad_module__":
    # r = M2RollerSwitch()
    # r = MicroswitchHolder()
    r = MicroswitchDisplay()
    display(r)
