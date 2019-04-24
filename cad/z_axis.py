#!/usr/bin/env python

# Building parts for an optical disc robot
# Starting to prototype general environment variables

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


from rods_04 import ThreadedRod, Stepper_28BYJ_48
from rotator_gear import RotatorStepperGear


class Nut(cqparts.Part):
    def make(self):
        r = cadquery.Workplane("YZ").polygon(6, 14.6).extrude(6.3)
        return r


class ZMMotorHolder(cqparts.Part):
    _render = render_props(template="green", alpha=0.2)

    def make(self):
        r = cadquery.Workplane("XY").rect(20, 40).extrude(10)
        return r


class ZRiser(cqparts.Part):
    """This is the vertical geared rack that lifts the head up and down"""

    _render = render_props(template="blue", alpha=0.4)

    def make(self):
        r = cadquery.Workplane("XY").rect(6.7, 5.2).extrude(120)
        #r = r.workplane("<Z").offset(10, 10).box(6.7, 20, 5.2)
        return r


class ZAxis(cqparts.Assembly):
    """Z Axis stepper motor assembly"""

    # default appearance
    _render = render_props(template="green", alpha=0.2)

    def make_components(self):
        gear = RotatorStepperGear(tooth_count=20, effective_radius=8.6, width=3.5, tooth_height=1.6)
        gear.gear_od = 8
        return {
            "base": ThreadedRod(),
            "nut": Nut(),
            "holder": ZMMotorHolder(),
            "motor": Stepper_28BYJ_48(),
            "riser": ZRiser(),
            "gear": gear,
        }

    def make_constraints(self):
        return [
            Fixed(self.components["base"].mate_origin, CoordSystem()),
            Coincident(
                self.components["nut"].mate_origin,
                self.components["base"].mate_along(0),  # Put nut at end
            ),
            Coincident(
                self.components["holder"].mate_origin,
                self.components["base"].mate_along(-2),
            ),
            Fixed(  # Move motor
                self.components["motor"].mate_origin,
                CoordSystem((20, -11, 25), (-1, 0, 0), (0, -1, 0)),
            ),
            Coincident(
                self.components["gear"].mate_origin,
                self.components["motor"].mate_gear,
            ),
            # Fixed(  # Move gear
            #     self.components["gear"].mate_origin,
            #     CoordSystem((10, 0, 40), (-1, 0, 0), (0, 0, 1)),
            # ),
            Fixed(  # Move riser
                self.components["riser"].mate_origin,
                CoordSystem((-6, 0, -50), (1, 0, 0), (0, 0, 1)),
            ),
        ]


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ == "__cq_freecad_module__":
    # r = Nut()
    # r = ThreadedRod()
    r = ZAxis()
    display(r)
