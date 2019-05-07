#!/usr/bin/env python

# Nuts and bolts as well as traps for them

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


class Nut(cqparts.Part):

    _render = render_props(template="silver", alpha=0.3)

    def __init__(self, size="M3", clearance=0.3):
        """Thanks https://www.fairburyfastener.com/xdims_metric_nuts.htm"""
        super(Nut, self).__init__()
        size = size.upper()
        self.size_name = size
        if size == "M2":
            self.thread = 2.0
            self.od = 4.32 + clearance
            self.thickness = 1.6 + clearance
        elif size == "M3":
            self.thread = 3.0
            self.od = 6.01 + clearance
            self.thickness = 2.4 + clearance
        elif size == "M4":
            self.thread = 4.0
            self.od = 7.66 + clearance
            self.thickness = 3.2 + clearance
        elif size == "M5":
            self.thread = 5.0
            self.od = 8.79 + clearance
            self.thickness = 4.7 + clearance
        elif size == "M6":
            self.thread = 6.0
            self.od = 11.05 + clearance
            self.thickness = 5.2 + clearance
        elif size == "M8":
            self.thread = 8.0
            self.od = 14.4 + clearance
            self.thickness = 6.8 + clearance
        else:
            raise Exception("unknown Metric nut size {}".format(size))

    @property
    def face_width(self):
        return self.od * 0.8660  # (OD * sin(60))

    def make(self):
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(0, 0, 0), rotate=(0, 0, 30))
            .polygon(6, self.od)
            .extrude(self.thickness)
        )
        r = r.faces(">Z").hole(self.thread)
        return r

    # Construct mating points origin is the inside of the nut
    @property
    def mate_nutend(self):
        """Mating other side of nut"""
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.thickness),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )

    def get_cutout(self, clearance=0.1):
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(0, 0, 0), rotate=(0, 0, 30))
            .polygon(6, self.od + clearance)
            .extrude(self.thickness)
        )
        return r

    def apply_cutout(self, part):
        part.local_obj = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.get_cutout()
        )


class Head(Nut):
    """Identical to a nut but has a different colour"""

    _render = render_props(template="aluminium", alpha=0.2)

    def make(self):
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(0, 0, 0), rotate=(0, 0, 30))
            .polygon(6, self.od)
            .extrude(self.thickness)
        )
        return r


class Thread(cqparts.Part):

    _render = render_props(template="gray", alpha=0.3)

    def __init__(self, size="M3", clearance=0.3, length=10):
        """Thanks https://www.fairburyfastener.com/xdims_metric_nuts.htm"""
        super(Thread, self).__init__()
        size = size.upper()
        self.size_name = size
        self.length = length
        if size == "M2":
            self.od = 2.0 + clearance
        elif size == "M3":
            self.od = 3.0 + clearance
        elif size == "M4":
            self.od = 4.0 + clearance
        elif size == "M5":
            self.od = 5.0 + clearance
        elif size == "M6":
            self.od = 6.0 + clearance
        elif size == "M8":
            self.od = 8.0 + clearance
        else:
            raise Exception("unknown Metric nut size {}".format(size))

    def make(self):
        r = cadquery.Workplane("XY").circle(self.od / 2.0).extrude(self.length)
        return r

    # Construct mating points
    def mate_along(self, distance=0, rotation=(0,0,0)):
        """Mating along rod, zero is the start of the thread"""
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, distance),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ).rotated(rotation),
        )

    def mate_thread_end(self, rotation=(0,0,0)):
        """Mating at head end"""
        return self.mate_along(distance = self.length, rotation=rotation)

    def mate_thread_start(self, rotation=(0,0,0)):
        """Mating at head end"""
        return self.mate_along(distance = 0, rotation=rotation)


class NutCutout(cqparts.Part):
    """This is a slot which allows a captive nut to be inserted into a solid block"""
    def __init__(self, nut=None, length=10, backspace=0.3):
        """Thanks https://www.fairburyfastener.com/xdims_metric_nuts.htm"""
        super(NutCutout, self).__init__()
        self.nut = nut
        self.length = length
        self.backspace = backspace

    def make_cutout(self, workplane):
        # Calculate where to start in Y
        y = (self.length / 2.0) + self.backspace + (self.nut.od / 4)
        y2 = y + ((self.nut.od / 2.0) - (self.nut.od / 4))
        x = (self.backspace / 2.0) + (self.nut.face_width / 2.0)
        points = [(x, 0), (x, y), (0, y2), (-x, y), (-x, -y), (x, -y), (x, 0)]
        r = workplane.polyline(points).close().extrude(self.nut.thickness)
        return r

    def make(self):
        # Make with a function so that can reuse for actual cutting out
        r = self.make_cutout(
            cadquery.Workplane("front").transformed(
                offset=(0, -self.length / 2.0, 0), rotate=(0, 0, 0)
            )
        )
        return r

    #    .transformed(offset=(-self.base_x / 2, z1, 0), rotate=(90, 0, 0), ) \
    # \
    # Construct mating points
    def mate_along(self, distance=0):
        """Mating along bolt from thread tip"""
        return Mate(
            self,
            CoordSystem(
                origin=(distance, 0, 0),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )


class Bolt(cqparts.Assembly):
    """Bolt can also model threaded nut for insertion into a solid object
    this models a
    - head
    - thread of length
    - nut which is bolted on somewhere on the thread
    """

    # default appearance
    _render = render_props(template="blue", alpha=0.2)

    def __init__(
        self,
        size="M3",
        clearance=0.3,
        length=10,  # This is the total length of the thread never mind how much is embedded
        embedded_length=0,  # This is the amount that pokes through the nut
        cutout_length=10,
        show_cutout=False,
        use_nut_cutout=True,  # This is the cutout for the nut
        show_nut=True,
        show_head=True,
    ):
        super(Bolt, self).__init__()
        self.size = size
        self.clearance = clearance
        self.length = length
        self.embedded_length = embedded_length
        self.cutout_length = cutout_length
        self.show_cutout = show_cutout
        self.use_nut_cutout = use_nut_cutout
        self.show_nut = show_nut
        self.show_head = show_head
        self.nut = Nut(size=self.size)
        self.nut._render = self._render
        self.head = Head(size=self.size)
        self.head._render = self._render

    def make_components(self):
        l = self.length
        thread = Thread(
            size=self.size, clearance=0, length=l
        )  # Model thread with zero clearance
        self.thread = Thread(
            size=self.size, clearance=self.clearance, length=l
        )  # Cutout thread with clearance
        thread._render = self._render
        self.cutout = cutout = NutCutout(self.nut, length=self.cutout_length)
        parts = {"thread": thread}
        if self.show_nut:
            parts["nut"] = self.nut
            if self.show_cutout:
                parts["cutout"] = cutout
        if self.show_head:
            parts["head"] = self.head
        return parts

    def make_constraints(self):
        constraints = [Fixed(self.components["thread"].mate_origin, CoordSystem())]
        if self.show_nut:
            constraints.append(
                Coincident(
                    self.components["nut"].mate_origin,
                    self.components["thread"].mate_along(self.embedded_length),
                )
            )
            if self.show_cutout:
                constraints.append(
                    Coincident(
                        self.components["cutout"].mate_origin,
                        self.components["nut"].mate_origin,
                    )
                )
        if self.show_head:
            constraints.append(
                Coincident(
                    self.components["head"].mate_origin,
                    self.components["thread"].mate_thread_end(),
                )
            )
        return constraints

    # Construct mating points
    def mate_along(self, distance=0, rotation=(0,0,0)):
        """Mating along rod, 0 is the start of thread, """
        return Mate(self, CoordSystem(origin=(0, 0, distance)).rotated(rotation))

    def mate_head_end(self, rotation=(0,0,0)):
        """Mating at the outside end of the head eg for embedding into a block"""
        return self.mate_along(distance= -self.nut.thickness, rotation = rotation)

    def mate_thread_head(self, rotation=(0, 0, 0)):
        """Mating at the end of thread next to the head, ie bolting something down"""
        return self.mate_along(distance=0, rotation = rotation)

    def mate_thread_end(self, rotation=(0, 0, 0)):
        """Mating at thread end"""
        return self.mate_along(distance=self.length, rotation = rotation)

    def get_cutout(self, clearance=0.3):
        # Cutout space for nut
        r = self.cutout.make_cutout(
            cadquery.Workplane("front").transformed(
                offset=(0, -self.cutout_length / 2.0, self.embedded_length),
                rotate=(0, 0, 0),
            )
        )
        # Todo maybe a neater way to use self.thread.make() but need to offset by embedded_length
        r = (
            r.faces("<Z")
            .workplane()
            .transformed(offset=(0, -self.cutout_length / 2.0, self.embedded_length))
            .circle(self.thread.od / 2.0)
            .extrude(-self.thread.length)
        )
        return r

    def apply_cutout(self, part):
        local_obj = part.local_obj
        local_obj = local_obj.cut(
            (self.world_coords - part.world_coords) + self.get_cutout()
        )
        if self.show_nut:  # Cutout space for nut
            local_obj = local_obj.cut(
                (self.nut.world_coords - part.world_coords) + self.nut.get_cutout()
            )
        if self.show_head:  # Cutout space for head
            local_obj = local_obj.cut(
                (self.head.world_coords - part.world_coords) + self.head.get_cutout()
            )
        part.local_obj = local_obj



class NutInsertTool(cqparts.Part):
    """This is a tool in push nuts into  holes"""

    _render = render_props(template="yellow")

    def __init__(self, size="M3", clearance=-0.2, length=10):
        """Thanks https://www.fairburyfastener.com/xdims_metric_nuts.htm"""
        super(NutInsertTool, self).__init__()
        self.length = length
        self.size = size
        self.clearance = clearance

    def make(self):
        nut = Nut(size=self.size, clearance=self.clearance)
        # Calculate where to start in Y
        y = (self.length / 2.0) + (nut.od / 4)
        y2 = y - ((nut.od / 2.0) - (nut.od / 4))
        x = nut.face_width / 2.0
        points = [(x, 0), (x, y), (0, y2), (-x, y), (-x, -y), (x, -y), (x, 0)]
        r = (
            cadquery.Workplane("front")
            .transformed(offset=(0, -self.length / 2.0, 0), rotate=(0, 0, 0))
            .polyline(points)
            .close()
            .extrude(nut.thickness)
        )
        r = r.union(
            cadquery.Workplane("front")
            .transformed(offset=(0, -self.length, 0), rotate=(0, 0, 0))
            .circle(4)
            .extrude(nut.thickness)
        )
        r = (
            r.faces("front")
            .workplane()
            .transformed(offset=(0, 5 - self.length / 2.0 - (nut.od / 3), 0))
            .hole(3)
        )  # Formula not quite right (centre of gravity?)
        return r
        # locate at axle position


class BoltHolder(cqparts.Part):
    """This is the holder for the testing Bolts"""

    _render = render_props(template="red", alpha=0.2)
    width = 28
    height = 20

    def make(self):
        r = (
            cadquery.Workplane("XY")
            .transformed(offset=(-10, 0, 0))
            .rect(6 * 20 + 10, self.width, centered=False)
            .extrude(self.height)
        )
        return r

    def mate_nut_top(self, nth=0):
        """Mating along top face"""
        return Mate(
            self,
            CoordSystem(
                origin=(nth * 20, self.width / 2, self.height),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )

    def mate_nut_bottom(self, nth=0):
        """Mating along top face"""
        return Mate(
            self,
            CoordSystem(
                origin=(nth * 20, self.width / 2, 0),
                # xDir=(1, 0, 0), normal=(0, -1, 0),
            ),
        )


class NutDisplay(cqparts.Assembly):
    """Z Axis stepper motor assembly"""

    # default appearance
    _render = render_props(template="green", alpha=0.2)
    tests = ["M2", "M3", "M4", "M5", "M6", "M8"]

    def nut_name(self, size):
        return "Nut_" + size

    def thread_name(self, size):
        return "Thread_" + size

    def min_bolt_name(self, size):
        "Essential just a thread"
        return "MinBolt_" + size

    def bolt_name(self, size):
        return "Bolt_" + size

    def embedded_bolt_name(self, size):
        return "Embed_Bolt_" + size

    def insert_bolt_name(self, size):
        return "Insert_Bolt_" + size

    def tool_name(self, size):
        return "Tool_" + size

    def nut_on_top_name(self, size):
        return "NutOnTop_" + size

    def bolt_on_bottom_name(self, size):
        return "BoltOnBottom_" + size

    def make_components(self):
        parts = {"base": BoltHolder(), "base2": BoltHolder(), "base3": BoltHolder()}
        for size in self.tests:
            parts[self.nut_name(size)] = Nut(size=size)
            parts[self.nut_on_top_name(size)] = Nut(size=size)
            parts[self.thread_name(size)] = Thread(size=size)
            parts[self.min_bolt_name(size)] = Bolt(
                size=size, show_nut=False, show_head=False
            )
            parts[self.bolt_name(size)] = Bolt(size=size, length=12)
            parts[self.bolt_on_bottom_name(size)] = Bolt(size=size, length=20, cutout_length=15, embedded_length=10)
            parts[self.insert_bolt_name(size)] = Bolt(
                size=size, length=16, embedded_length=2, cutout_length=15
            )
            parts[self.tool_name(size)] = NutInsertTool(size=size, length=70)
            # Embedded nut variations
            if size == "M8":
                parts[self.embedded_bolt_name(size)] = Bolt(
                    size=size, length=12, embedded_length=3, show_cutout=True
                )
            elif size == "M6":
                parts[self.embedded_bolt_name(size)] = Bolt(
                    size=size,
                    length=12,
                    embedded_length=3,
                    show_cutout=True,
                    show_head=False,
                )
            elif size == "M5":
                parts[self.embedded_bolt_name(size)] = Bolt(
                    size=size,
                    length=12,
                    embedded_length=3,
                    show_cutout=True,
                    show_head=False,
                    show_nut=False,
                )

            elif size == "M4":
                parts[self.embedded_bolt_name(size)] = Bolt(
                    size=size,
                    length=12,
                    embedded_length=3,
                    show_cutout=True,
                    show_head=True,
                    show_nut=False,
                )
            else:
                parts[self.embedded_bolt_name(size)] = Bolt(
                    size=size, length=12, embedded_length=3
                )
        return parts

    def make_constraints(self):
        base2 = self.components["base2"]
        base3 = self.components["base3"]
        constraints = [
            Fixed(self.components["base"].mate_origin, CoordSystem((0, 107, 0))),
            Fixed(
                base2.mate_origin, CoordSystem((0, 147, 0))
            ),  # Embed nuts in top and make sure cutout
            Fixed(
                base3.mate_origin, CoordSystem((0, 180, 0))
            ),  # Embed nuts in top and make sure cutout
            # works
        ]
        for i, size in enumerate(self.tests):
            bolt_b = self.components[self.bolt_on_bottom_name(size)]
            constraints += [
                Fixed(  # Space out nuts
                    self.components[self.nut_name(size)].mate_origin,
                    CoordSystem((i * 20, 0, 0)),
                ),
                Fixed(
                    self.components[self.thread_name(size)].mate_origin,
                    CoordSystem((i * 20, 15, 0)),
                ),
                Fixed(
                    self.components[self.min_bolt_name(size)].mate_origin,
                    CoordSystem((i * 20, 40, 0)),
                ),
                Fixed(
                    self.components[self.bolt_name(size)].mate_origin,
                    CoordSystem((i * 20, 65, 0)),
                ),
                Fixed(
                    self.components[self.embedded_bolt_name(size)].mate_origin,
                    CoordSystem((i * 20, 95, 0)),
                ),
                Fixed(
                    self.components[self.insert_bolt_name(size)].mate_origin,
                    CoordSystem((i * 20, 120, 10)),
                ),
                Fixed(
                    self.components[self.tool_name(size)].mate_origin,
                    CoordSystem((i * 20, -10, 0)),
                ),
                Coincident(
                    self.components[self.nut_on_top_name(size)].mate_nutend,
                    base2.mate_nut_top(i),
                ),
                Coincident(
                        bolt_b.mate_head_end(rotation=(180,0,0)),
                    base3.mate_nut_bottom(i),
                ),
            ]
        return constraints

    def make_alterations(self):
        # Cutout the inserted nuts
        base = self.components["base"]
        base2 = self.components["base2"]
        base3 = self.components["base3"]
        for i, size in enumerate(self.tests):
            self.components[self.insert_bolt_name(size)].apply_cutout(base)
            self.components[self.nut_on_top_name(size)].apply_cutout(base2)
            self.components[self.bolt_on_bottom_name(size)].apply_cutout(base3)


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ == "__cq_freecad_module__":
    # r = Nut()
    # r = Head()
    # r = Bolt()
    # r = Bolt(size = 'M3', embedded_length=3)
    # r = Bolt(size = 'M3', embedded_length=3, show_cutout=True)
    r = NutDisplay()
    display(r)
