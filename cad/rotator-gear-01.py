#!/usr/bin/env python

# The code here should be representative of that in:
#   https://cqparts.github.io/cqparts/doc/tutorials/assembly.html

# ------------------- Wheel -------------------

import cadquery
import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props, display
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

# -------------------- New Start ----------------------
from cqparts_fasteners.male import MaleFastenerPart
from cqparts_gears.trapezoidal import TrapezoidalGear


class RotatorStepperGear(TrapezoidalGear):
    """
    This is a length of threaded rod (without thread)
    """
    # Parameters
    gear_od = PositiveFloat(8, doc="Gear diameter")
    gear_length = PositiveFloat(2, doc="Ger length")

    # default appearance
    _render = render_props(color=(200, 200, 200))  # dark grey

    def make(self):
        r = super(RotatorStepperGear, self).make()
        # # Outside face
        # r = cadquery.Workplane("XY").circle(
        #     (self.rod_od)/2).extrude(self.rod_length)
        # r = r.union(TrapezoidalGear())
        # # circle(
        # #     (self.rod_od)/2).extrude(self.rod_length)
        r = r.faces(">Z").circle((self.gear_od)/2).extrude(self.gear_length)
        # r = r.faces(">Z").polygon(6, 1.0).cutThruAll()
        # cut out shaft
        e = 0.03  # Margin of error
        w = e + 3.0 / 2  # distance of flat tab
        l = 4.0 / 2  # distance along flat tab (no error term as that is in the c term
        c = e + 0.5  # Curved end
        r = r.cut(cadquery.Workplane("XY").transformed(offset=(0, 0, -5)) \
            .lineTo(w, 0).lineTo(w, l).threePointArc((0, l + c), (-w, l)) \
            .lineTo(-w, -l).threePointArc((0, -l - c), (w, -l)).lineTo(w, 0) \
            .close() \
            .extrude(20))
            #.cutThruAll()
        # r = r.faces(">Z").transformed(offset=(0, 0, 0)) \
        #     .lineTo(w, 0).lineTo(w, l).threePointArc((0, l + c), (-w, l)) \
        #     .lineTo(-w, -l).threePointArc((0, -l - c), (w, -l)).lineTo(w, 0) \
        #     .close() \
        #     .cutThruAll()
            #.extrude(10)
        # r = workplane.transformed(offset=(8.5, 0, 0)).circle((self.shaft_od)/2).\
        #                           extrude(self.shaft_length+self.motor_length)
        return r


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ != 'TestEngineWholeModel':
    #m = ThreadedRod()
    # m = TrapezoidalGear()
    m = RotatorStepperGear(tooth_count=22, effective_radius=8.6, width=3.5, tooth_height=1.8)
    display(m)
