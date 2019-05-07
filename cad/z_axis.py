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


from rods_04 import ThreadedRod
from stepper import Stepper_28BYJ_48, StepperGear
from z_riser import ZRiser, ZRiserHolder
from nuts_bolts import Nut, Bolt
from microswitches import M2RollerSwitchAssembly


class ZMMotorHolder(cqparts.Part):
    """This is the holder for the motor, the nut trap, wiring loom etc.  The back left corner will be 0,0
    so it is being built on -y and X Z.  """

    _render = render_props(template="red", alpha=0.2)

    height = 22  # Height of main support block
    wall = 4
    nut_width = 6.5
    riser_width = 6.8
    width = wall + nut_width + wall  # main support block

    def motor_support(self):
        """Motor support bracket"""
        h = self.wall + self.nut_width + 4
        w = self.width-2
        x_start = 15
        offset = 0
        r = (
            cadquery.Workplane("XY")
            .transformed(
                offset=(x_start, -w, 0)
            )
            .rect(h, w, centered=False)
            .extrude(self.height+24)
        )
        return r

    def microswitch_support(self):
        """Motor support brackets"""
        h = 8
        w = 25
        offset = 0
        r = (
            cadquery.Workplane("XY")
            .transformed(
                offset=(0, -w, 0)
            )
            .rect(h, w, centered=False)
            .extrude(self.height)
        )
        return r

    def make(self):
        r = (
            cadquery.Workplane("XY")
            .transformed(
                offset=(0, -self.width, 0)
            )
            .rect(50, self.width, centered=False)
            .extrude(self.height)
        )
        r = r.union(self.motor_support())
        r = r.union(self.microswitch_support())
        return r

    @property
    def mate_bolt(self):
        """This should mate to the end of the M8 support rod, from the internal origin at the back base"""
        return Mate(
            self,
            CoordSystem(
                origin=(15, -10.5, self.height / 2), xDir=(0, 1, 0), normal=(0, 0, -1)
            ).rotated((90, -90, 0)),
        )

    @property
    def mate_motor(self):
        """This should mount the motor"""
        return Mate(
            self,
            CoordSystem((33.7, 8.5, 25), (0, 0, 1), (-1, 0, 0)).rotated((-120, 0, 90)),
        )

    @property
    def mate_away(self):
        """This should mount the object away from where its meant to be so that you can examine details of the exploded design"""
        return Mate(
            self,
            CoordSystem((-250, 0, 0)),
        )

class ZAxis(cqparts.Assembly):
    """Z Axis stepper motor assembly"""

    # default appearance
    _render = render_props(template="green", alpha=0.2)

    def make_components(self):
        gear = StepperGear(
            tooth_count=20, effective_radius=8.6, width=3.5, tooth_height=1.6
        )
        gear.gear_od = 8
        riser = ZRiser()
        return {
            "bolt": Bolt(size="M8", length=40, show_cutout=True),
            "holder": ZMMotorHolder(),
            "motor": Stepper_28BYJ_48(),
            "riser": riser,
            "riser_holder": ZRiserHolder(riser),
            "gear": gear,
            "switch": M2RollerSwitchAssembly(),
        }

    def make_constraints(self):
        return [
            Fixed(
                self.components["holder"].mate_origin,
                CoordSystem((0, 0, 0), (1, 0, 0), (0, 0, 1)),
            ),
            Coincident(
                self.components["bolt"].mate_along(
                    0),
                # self.components["holder"].mate_origin,  # Put nut at end
                self.components["holder"].mate_bolt,
            ),
            # Fixed(  # Test  bolt
            #     self.components["bolt"].mate_origin,
            #     CoordSystem((20, 30, 0), (0, 0, 1), (1, 0, 0)).rotated((0, 0, 0)),
            # ),
            Coincident(  # Move motor
                self.components["motor"].mate_origin,
                self.components["holder"].mate_motor,
            ),
            Coincident(
                self.components["gear"].mate_shaft, self.components["motor"].mate_gear
            ),
            Fixed(  # Move riser
                self.components["riser_holder"].mate_origin,
                CoordSystem((7.5+14.7/2.0, -18.4, 0), (-1, 0, 0), (0, 0, 1)).rotated((0, 0, 180)),
            ),
            Coincident(  # mount
                self.components["riser"].mate_holder_demo,
                self.components["riser_holder"].mate_origin,
            ),
            Fixed(
                self.components["switch"].mate_origin,
                CoordSystem((0, -7, 3), xDir=(0, 0, 1), normal=(-1, 0, 0)).rotated((90, 0, 0)), )
        ]

    def make_alterations(self):
        """Apply all the cutouts"""
        # Cutout the motor
        holder = self.components["holder"]
        self.components["motor"].apply_cutout(holder)
        self.components["motor"].apply_cutout(self.components["riser_holder"])
        self.components["bolt"].apply_cutout(holder)
        # cutout the riser
        riser = self.components["riser"]
        riser.apply_cutout(self.components["riser_holder"])
        riser.apply_cutout(holder)
        # Add mounting holes for microswitch
        self.components['switch'].apply_cutout(holder)



# ------------------- Display Result -------------------
# Could also export to another format
if __name__ == "__cq_freecad_module__":
    # r = Nut()
    # r = ThreadedRod()
    # r = ZMMotorHolder()
    r = ZAxis()
    display(r)
