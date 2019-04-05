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
from cqparts_fastners.bolts import Bolt
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


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ != 'TestEngineWholeModel':
    #m = ThreadedRod()
    m = Bolt()
    display(m)
