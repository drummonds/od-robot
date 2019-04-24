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


BAR_SEPERATION = 40

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
    seperation = BAR_SEPERATION  # PositiveFloat(40, doc="bar seperation")

    # default appearance
    _render = render_props(color=(250, 50, 90))

    def make(self):
        plate = cadquery.Workplane("XY").transformed(offset=(-1, 0, 0)).box(2, self.seperation+2, 0.5)\
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
            origin=(38, 0, 0),
            xDir=(0, 0, 1), normal=(-1, 0, 0),
        ))

    @property
    def mate_holder(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, 0),
            # xDir=(1, 0, 0), normal=(0, 0, 1),
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

# ------------------- Stepper holder -------------------
# This is a model of a holder for the stepper motor


class Stepper_Holder(cqparts.Part):
    """
    This is a holder for astandard 28BYJ-48 stepper motor
    """

    # default appearance
    _render = render_props(color=(20, 20, 150))

    # Parameters
    body_length = PositiveFloat(61, doc="Body length")
    motor_od = 28.5

    def rod_block(self, workplane, offset):
        r = workplane.transformed(offset=(offset, 0, 0)).box(15, 15, self.body_length)
        return r

    def base_plate(self, workplane):
        r = workplane.transformed(offset=(-BAR_SEPERATION/2, -6.5, 0)).box(BAR_SEPERATION, 2, self.body_length)
        return r

    def mounting_block(self, workplane, offset):
        r = workplane.transformed(offset=(offset, 13.5, 10)).box(15, 12, 30)
        return r

    def make(self):
        # Outside face
        r = self.rod_block(cadquery.Workplane("YZ"), 0)
        r = r.union(self.rod_block(r.faces(">X"), -BAR_SEPERATION))
        r = r.union(self.mounting_block(r.faces(">X"), -20+BAR_SEPERATION/2))
        r = r.union(self.mounting_block(r.faces(">X"), -BAR_SEPERATION))
        r = r.union(self.base_plate(r.faces(">X")))
        # add holes for bars
        r = r.faces(">X").workplane().transformed(offset=(0, 0.625, 0)).\
            rect(BAR_SEPERATION, 0, forConstruction=True).vertices().hole(8.5)
        # cut out to fit motor
        r = r.faces(">Z").workplane().transformed(offset=(-2, 0, 0)).\
            hole(self.motor_od)
        # add some holes for mounting nut inserts to hold motor in
        r = r.faces("<Z").workplane().transformed(offset=(9.5, 0, 0)).\
            rect(0, 36, forConstruction=True).vertices().hole(3)
        # add some holes for mounting or zip ties
        r = r.faces("<Z").workplane().transformed(offset=(-10, 0, 0)).\
            rect(10, 20, forConstruction=True).vertices().hole(3)
        #r = r.faces(">X").workplane().lineTo(0, BAR_SEPERATION,  forConstruction=True).vertices().hole(11)
        return r

    # Construct mating points for two axes
    @property
    def mate_centre(self):
        return Mate(self, CoordSystem(
            origin=(-self.body_length/2, -BAR_SEPERATION/2, 0),
            xDir=(1, 0, 0), normal=(0, 0, 1),
        ))


# ------------------- Rotator Assembly -------------------

class RotatorAssembly(cqparts.Assembly):

    def make_components(self):
        return {
            'base': SideConstruct(),
            'front_bar': ThreadedRod(),
            'back_bar': ThreadedRod(),
            'motor': Stepper_28BYJ_48(),
            'holder': Stepper_Holder(),
        }

    def make_constraints(self):
        return [
            Fixed(self.components['base'].mate_origin, CoordSystem()),
            Coincident(
                self.components['front_bar'].mate_origin,
                self.components['base'].mate_left
            ),
            Coincident(
                self.components['back_bar'].mate_origin,
                self.components['base'].mate_right
            ),
            Coincident(
                self.components['motor'].mate_centre,
                self.components['base'].mate_motor
            ),
            Coincident(
                self.components['holder'].mate_centre,
                self.components['base'].mate_holder
            ),
        ]

        # ------------------- Display Result -------------------
# Could also export to another format
if __name__ != 'TestEngineWholeModel':
    # r = ThreadedRod()
    # r = SideConstruct()
    r = RotatorAssembly()
    # r = Stepper_28BYJ_48()
    # r = Stepper_Holder()
    display(r)
