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
        plate = cadquery.Workplane("XY").box(self.seperation+2, 2, 0.5)\
                 .faces(">Y").workplane() \
                 .pushPoints([(0, self.seperation/2), (0, -self.seperation/2)]) \
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


# ------------------- Rotator Assembly -------------------


class RotatorAssembly(cqparts.Assembly):

    def make_components(self):
        bar_f = ThreadedRod()
        bar_b = ThreadedRod()
        return {
            'base': SideConstruct(),
            'front_bar': bar_f,
            'back_bar': bar_b,
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
        ]


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ != 'TestEngineWholeModel':
    # r = ThreadedRod()
    # r = SideConstruct()
    r = RotatorAssembly()
    display(r)
