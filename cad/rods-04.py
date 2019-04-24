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
#from cqparts_fastners.bolts import Bolt
from cqparts.display import display


CAD_ENV = {'BAR_SEPERATION':40,
           'Z_STEPPER_AXIS_OFFSET': 43}

class H3Part(cqparts.Part):
    def __init__(self,  env = None):
        super(H3Part, self).__init__()
        if env is None:
            self.env = CAD_ENV
        else:
            self.env = env


class H3Assembly(cqparts.Assembly):
    def __init__(self,  env = None):
        super(H3Assembly, self).__init__()
        if env is None:
            self.env = CAD_ENV
        else:
            self.env = env


class ThreadedRod(H3Part):
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


class SideConstruct(H3Part):

    # default appearance
    _render = render_props(color=(250, 50, 90))
    motor_offset = 38

    def __init__(self, env = None):
        super(SideConstruct, self).__init__(env)
        # Parameters
        self.seperation = self.env['BAR_SEPERATION']

    def make(self):
        plate = cadquery.Workplane("XY").transformed(offset=(-.25, 0, 0)).box(0.5, self.seperation+2, 2)\
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
        return Mate(self, CoordSystem(
            origin=(0, -self.seperation/2, 0),
            xDir=(1, 0, 0), normal=(0, 1, 0),
        ))

    @property
    def mate_motor(self):
        return Mate(self, CoordSystem(
            origin=(self.motor_offset, 0, 0),
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


class Stepper_28BYJ_48(H3Part):
    """
    This is a standard 28BYJ-48 stepper motor schematic to show positioning
    """

    # default appearance
    _render = render_props(color=(0, 250, 90))

    # Parameters
    motor_od = PositiveFloat(28, doc="Motor diameter")
    motor_length = PositiveFloat(19.5, doc="Motor length")
    shaft_od = PositiveFloat(5, doc="Shaft diameter")
    shaft_length = PositiveFloat(9, doc="Shaft length")

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
        w = 3.5  # Width of tab
        l = 35.0 / 2  # hole centre to hole centre distance
        t = 0.85  # Thickness of tab
        hw = 2  # tab hole size
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
        w = 3.0 / 2  # distance of flat tab
        l = 4.0 / 2  # distance along flat tab
        c = 0.5  # Curved end
        r = workplane.transformed(offset=(8.5, 0, self.motor_length)) \
            .lineTo(w, 0).lineTo(w, l).threePointArc((0, l+c), (-w, l)) \
            .lineTo(-w, -l).threePointArc((0, -l - c), (w, -l)).lineTo(w, 0) \
            .close() \
            .extrude(self.shaft_length)
        #r = workplane.transformed(offset=(8.5, 0, 0)).circle((self.shaft_od)/2).\
        #                           extrude(self.shaft_length+self.motor_length)
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


class Stepper_Holder(H3Part):
    """
    This is a holder for astandard 28BYJ-48 stepper motor
    It is built using the bottom of the base plate as a reference.
    TODO Bug fix It seems as though faces selection is taking the first face to generate models
    """

    # default appearance
    _render = render_props(color=(20, 20, 150))

    # Parameters
    body_length = PositiveFloat(61, doc="Body length")
    motor_od = 28.5
    rod_cover_width = 15
    motor_offset = 35 #42.5  # distance of shaft from end of mounting block

    def base_plate(self, workplane):
        sep = self.env['BAR_SEPERATION']
        r = workplane.transformed(offset=(0, 0, 1)).box(self.body_length, sep, 2)
        return r

    def rod_block(self, workplane, offset):
        """Block to cover rods which will be used as building block"""
        z = (self.rod_cover_width/2.0)-1  # adjust for depth of base plate
        r = workplane.transformed(offset=(0, offset, z)).box(self.body_length,
                                                             self.rod_cover_width, self.rod_cover_width)
        return r

    def mounting_block(self, workplane, offset):
        """mounting block for motor tabs"""
        o = -self.body_length/2.0 + self.motor_offset
        h = 12  # height of mounting block
        z = self.rod_cover_width + (h/2.0) - 1 # adjust for depth of base plate TODO error?
        r = workplane.transformed(offset=(o, offset, z)).box(self.rod_cover_width*2, self.rod_cover_width, h)
        return r

    def test_block(self, workplane):
        r = workplane.box(1, 1, 1)
        return r

    def make(self):
        # Outside face
        sep = self.env['BAR_SEPERATION']
        axis_offset = self.env['Z_STEPPER_AXIS_OFFSET']
        r = self.base_plate(cadquery.Workplane("XY"))
        r = r.union(self.rod_block(r.faces("<Z"), sep/2.0))
        r = r.union(self.rod_block(r.faces("<Z"), -sep/2.0))
        r = r.union(self.mounting_block(r.faces("<Z"), sep/2.0))
        r = r.union(self.mounting_block(r.faces(">Z"), -sep/2.0))
        # add holes for bars
        r = r.faces("<X").workplane(centerOption='CenterOfBoundBox').transformed(offset=(0, 0, 0)).\
            rect(sep, 0, forConstruction=True).vertices().hole(8.5)
        # cut out to fit motor
        o = (-self.body_length/2.0 ) + self.motor_offset
        r = r.faces("<Z").workplane(centerOption='CenterOfBoundBox').transformed(offset=(o, 0, 0)).\
            hole(self.motor_od)
        # add some holes for mounting nut inserts to hold motor in
        r = r.faces("<Z").workplane(centerOption='CenterOfBoundBox').transformed(offset=(o, 0, 0)).\
            rect(0, 36, forConstruction=True).vertices().hole(4 - 0.20)   # Add some interference for threads to melt into
        # add some holes for mounting or zip ties
        x = self.body_length - 6*2
        y = sep -  self.rod_cover_width - 3.5*2
        #  Not sure why adjusting offset
        r = r.faces("<Z").workplane(centerOption='CenterOfBoundBox').transformed(offset=(0, 0, 0)).\
            rect(x, y, forConstruction=True).vertices().hole(4)
#         #r = r.faces(">X").workplane().lineTo(0, self.env['BAR_SEPERATION'],  forConstruction=True).vertices().hole(11)
        return r

    # Construct mating points for two axes
    @property
    def mate_centre(self):
        return Mate(self, CoordSystem(
            origin=(-self.body_length/2, -self.env['BAR_SEPERATION']/2, 0),
            xDir=(1, 0, 0), normal=(0, 0, 1),
        ))


# ------------------- Rotator Assembly -------------------

class RotatorAssembly(H3Assembly):

    motor_offset = 35 # 61-15

    def make_components(self):
        base = SideConstruct()
        holder = Stepper_Holder()
        # Adjust dimensions
        base.motor_offset = self.motor_offset
        holder.motor_offset = self.motor_offset
        return {
            'base': base,
            'front_bar': ThreadedRod(),
            'back_bar': ThreadedRod(),
            'motor': Stepper_28BYJ_48(),
            'holder': holder,
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
    # r = RotatorAssembly()
    # r = Stepper_28BYJ_48()
    r = Stepper_Holder()
    display(r)
