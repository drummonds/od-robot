#!/usr/bin/env python

# The code here should be representative of that in:
#   https://cqparts.github.io/cqparts/doc/tutorials/assembly.html

# ------------------- Wheel -------------------

import cadquery
import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props, display
from cqparts.constraint import Mate, Fixed, Coincident
from cqparts.utils.geometry import CoordSystem

# -------------------- New Start ----------------------
from cqparts_fasteners.male import MaleFastenerPart
#from cqparts_fastners.bolts import Bolt
from cqparts.display import display


class ThreadedRod(cqparts.Part):
    """
    This is a length of threaded rod (without thread)
    """
    # Parameters
    rod_od = PositiveFloat(8, doc="Rod diameter")
    rod_length = PositiveFloat(200, doc="Rod length")

    # default appearance
    _render = render_props(color=(200, 200, 200))  # dark grey

    def make(self):
        # Outside face
        r = cadquery.Workplane("YZ").circle(
            (self.rod_od)/2).extrude(self.rod_length)
        # r = r.faces(">X").circle((self.gear_od)/2).extrude(self.gear_length)
        return r

    # Construct mating points
    @property
    def mate_start(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, 0),
            # xDir=(1, 0, 0), normal=(0, -1, 0),
        ))

# ------------------- Side construction -------------------
# This is some construction geometry to hold the two bars on for constructing
# the rotator holder


class SideConstruct(cqparts.Part):
    # Parameters
    seperation = PositiveFloat(40, doc="bar seperation")

    # default appearance
    _render = render_props(color=(250, 50, 90))

    def make(self):
        plate = cadquery.Workplane("XY").box(2, self.seperation+2, 0.5)\
                 .faces(">X").workplane() \
                 .pushPoints([(self.seperation/2, 0), (-self.seperation/2, 0)]) \
                 .hole(0.125)
        return plate

    # Construct mating points for two axes
    @property
    def mate_left(self):
        return Mate(self, CoordSystem(
            origin=(0, self.seperation/2, 0),
            xDir=(1, 0, 0), normal=(0, -1, 0),
        ))

    @property
    def mate_right(self):
        print('Mating right')
        return Mate(self, CoordSystem(
            origin=(0, -self.seperation/2, 0),
            xDir=(1, 0, 0), normal=(0, 1, 0),
        ))

    @property
    def mate_motor(self):
        return Mate(self, CoordSystem(
            origin=(40, 0, 0),
            xDir=(1, 0, 0), normal=(0, 1, 0),
        ))

# ------------------- Stepper Motor 28BYJ-48 -------------------
# This is a model of the stepper motor to help with modelling


class Stepper_28BYJ_48(cqparts.Part):
    """
    This is a standard 28BYJ-48 stepper motor schematic to show positioning
    """

    # default appearance
    _render = render_props(color=(0, 250, 90))

    # Parameters
    motor_od = PositiveFloat(28, doc="Motor diameter")
    motor_length = PositiveFloat(19.5, doc="Motor length")
    shaft_od = PositiveFloat(5, doc="Shaft diameter")
    shaft_length = PositiveFloat(10, doc="Shaft length")

    def motor(self, workplane):
        r = workplane.circle(
            (self.motor_od)/2).extrude(self.motor_length)
        return r

    def wiring_block(self, workplane):
        r = workplane.transformed(offset=((-self.motor_od/2) +0.45, 0, 11)).box(4.5, 14.5, 17)
        return r


    def wires(self, workplane):
        r = workplane.transformed(offset=((-self.motor_od/2) -3.6, 0, self.motor_length/2)).box(4, 6.5, self.motor_length)
        return r


    def mounting_block(self, workplane):
        """This is the two little tabs each side used for mounting the motor"""
        w = 3.5
        l = 19
        t = 0.85
        hw = 2
        r = workplane.transformed(offset=(0, 0, self.motor_length-t)) \
            .lineTo(w, 0).lineTo(w, l).threePointArc((0, l+4), (-w, l)) \
            .lineTo(-w, -l).threePointArc((0, -l - 4), (w, -l)).lineTo(w, 0) \
            .close() \
            .center(0, l).circle(hw) \
            .center(0, -l*2).circle(hw) \
            .extrude(t)
        # new work center is ( 0.0, 1.5).
        return r


    def shaft(self, workplane):
        r = workplane.transformed(offset=(8.5, 0, 0)).circle((self.shaft_od)/2).\
                                  extrude(self.shaft_length+self.motor_length)
        return r

    def make(self):
        # Outside face
        r = self.motor(cadquery.Workplane("YZ"))
        r = r.union(self.shaft(r.faces(">X")))  # Actually seems to ignore and always picks "X" face
        r = r.union(self.wiring_block(r.faces(">X")))
        r = r.union(self.wires(r.faces(">X")))
        r = r.union(self.mounting_block(r.faces(">X")))
        return r

    def get_cutout(self, clearance=1):
        # Outside face
        r = cadquery.Workplane("YZ").circle(clearance + (self.motor_od/2)).extrude(self.motor_length)
        return r

    # Construct mating points for two axes
    @property
    def mate_centre(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, 0),
            xDir=(1, 0, 0), normal=(0, -1, 0),
        ))


# ------------------- Rotator Assembly -------------------

class RotatorAssembly(cqparts.Assembly):

    def make_components(self):
        return {
            'base': SideConstruct(),
            'front_bar': ThreadedRod(),
            'back_bar': ThreadedRod(),
            'motor': Stepper_28BYJ_48(),
        }

    def make_constraints(self):
        return [
            Fixed(self.components['base'].mate_origin, CoordSystem()),
            Coincident(
                self.components['front_bar'].mate_start,
                self.components['base'].mate_left
            ),
            Coincident(
                self.components['back_bar'].mate_start,
                self.components['base'].mate_right
            ),
            Coincident(
                self.components['motor'].mate_centre,
                self.components['base'].mate_motor
            ),
        ]

        # ------------------- Display Result -------------------
# Could also export to another format
if __name__ != 'TestEngineWholeModel':
    # r = ThreadedRod()
    # r = SideConstruct()
    # r = RotatorAssembly()
    r = Stepper_28BYJ_48()
    display(r)
