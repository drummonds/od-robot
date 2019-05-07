"""Repository for stepper motor and addons"""
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
from cqparts_gears.trapezoidal import TrapezoidalGear

# ------------------- Stepper Motor 28BYJ-48 -------------------
# This is a model of the stepper motor to help with modelling


class Stepper_28BYJ_48(cqparts.Part):
    """
    This is a standard 28BYJ-48 stepper motor schematic to show positioning and to use when creating
    supports.
    This is on an XY plane with the gear off centre pointing up
    """

    # default appearance
    # make motor transparent so can see block more clearly
    _render = render_props(template="green", alpha=0.2)

    # Parameters
    motor_od = PositiveFloat(28, doc="Motor diameter")
    motor_length = PositiveFloat(19.5, doc="Motor length")
    shaft_od = PositiveFloat(5, doc="Shaft diameter")
    shaft_length = PositiveFloat(9, doc="Shaft length")
    tab_thickness = (
        0.85
    )  # The tab is the mounting plate with holes in on the surface of the motor

    def motor(self, workplane):
        r = workplane.circle((self.motor_od) / 2).extrude(self.motor_length)
        return r

    def wiring_block(self, workplane):
        r = workplane.transformed(offset=((-self.motor_od / 2) + 0.45, 0, 11)).box(
            4.5, 14.5, 17
        )
        return r

    def wires(self, workplane):
        r = workplane.transformed(
            offset=((-self.motor_od / 2) - 3.6, 0, self.motor_length / 2)
        ).box(4, 6.5, self.motor_length)
        return r

    def mounting_block(self, workplane, z_clearance=0, xy_clearance=0):
        """This is the two little tabs each side used for mounting the motor"""
        w = 3.5  # Width of tab
        l = 35.0 / 2  # hole centre to hole centre distance
        t = self.tab_thickness
        hw = 2  # tab hole size
        w2 = w + xy_clearance
        r = (
            workplane.transformed(offset=(0, 0, self.motor_length - t))
            .lineTo(w2, 0)
            .lineTo(w2, l)
            .threePointArc((0, l + 4 + xy_clearance), (-w2, l))
            .lineTo(-w2, -l)
            .threePointArc((0, -l - 4 - xy_clearance), (w2, -l))
            .lineTo(w2, 0)
            .close()
        )
        if z_clearance < 0.01:
            r = r.center(0, l).circle(hw).center(0, -l * 2).circle(hw)
        r = r.extrude(t + z_clearance)
        # new work center is ( 0.0, 1.5).
        return r

    def shaft(self, workplane):
        w = 3.0 / 2  # distance of flat tab
        l = 4.0 / 2  # distance along flat tab
        c = 0.5  # Curved end
        r = (
            workplane.transformed(offset=(8.5, 0, self.motor_length))
            .lineTo(w, 0)
            .lineTo(w, l)
            .threePointArc((0, l + c), (-w, l))
            .lineTo(-w, -l)
            .threePointArc((0, -l - c), (w, -l))
            .lineTo(w, 0)
            .close()
            .extrude(self.shaft_length)
        )
        # r = workplane.transformed(offset=(8.5, 0, 0)).circle((self.shaft_od)/2).\
        #                           extrude(self.shaft_length+self.motor_length)
        return r

    def make(self):
        # Outside face
        r = self.motor(cadquery.Workplane("XY"))
        r = r.union(
            self.shaft(r.faces(">Z"))
        )  # Actually seems to ignore and always picks "X" face
        r = r.union(self.wiring_block(r.faces(">Z")))
        r = r.union(self.wires(r.faces(">Z")))
        r = r.union(self.mounting_block(r.faces(">Z")))
        return r

    def get_cutout(self, clearance=1):
        """clearance is edge clearance"""
        z_clearance = 30  # To allow inserting a motor from an open side
        # Outside face
        r = (
            cadquery.Workplane("XY")
            .circle(clearance + (self.motor_od / 2))
            .extrude(self.motor_length + z_clearance)
        )
        r = r.union(
            self.mounting_block(cadquery.Workplane("XY"), z_clearance=z_clearance,  xy_clearance=0.3)
        )
        # r = r.union(self.mounting_block(r.faces(">Z")))
        r = (
            r.faces("<Z")
            .transformed(offset=(-15, 0, 0), rotate=(0, 0, 0))
            .rect(9, 15)
            .extrude(30 + z_clearance)
        )  # wires
        #Now add cutouts for screws (3mm nut inserts)
        for x, y in ((15, -17.5), (0, 35)):
            r = (
                r.faces("<Z")
                # .workplane(centerOption="CenterOfBoundBox")
                .transformed(offset=(x, y, 0), rotate=(0, 0, 0))
                .circle(3.8 / 2)
                .extrude(30 + z_clearance)
            )
        return r

    def apply_cutout(self, part):
        """Apply this cutout"""
        part.local_obj = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.get_cutout()
        )

    # Construct mating points for two axes
    @property
    def mate_centre(self):
        """This is below the face plate and half way between the mounting bolts"""
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.motor_length - self.tab_thickness),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )

    @property
    def mate_gear(self):
        """This is at the centre and end of the drive shaft"""
        return Mate(
            self, CoordSystem(origin=(8.5, 0, 26.75), xDir=(1, 0, 1), normal=(0, 0, -1))
        )


# ------------------- Stepper holder -------------------
# This is a model of a holder for the stepper motor


class Stepper_Holder(cqparts.Part):
    """
    This is a simple holder for a standard 28BYJ-48 stepper motor.  It needs to be assembled.
    """

    # default appearance
    _render = render_props(color=(20, 20, 150))

    height = 30

    def make(self):
        # Outside face
        r = cadquery.Workplane("XY").rect(30, 55).extrude(self.height)
        return r

    # Construct mating points for two axes
    @property
    def mate_centre(self):
        """This is the top of the box"""
        embed_depth = (
            10
        )  # Make non zero to actually embed stepper into solid block and checkout cutouts
        return Mate(
            self,
            CoordSystem(
                origin=(10, 0, self.height - embed_depth),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )


class StepperGear(TrapezoidalGear):
    """
    This is a length of threaded rod (without thread)
    """

    # Parameters
    gear_od = PositiveFloat(8, doc="Gear diameter")
    gear_length = PositiveFloat(2, doc="Gear length")

    # default appearance
    _render = render_props(color=(200, 200, 200))  # dark grey

    def make(self):
        r = super(StepperGear, self).make()
        r = r.faces(">Z").circle((self.gear_od) / 2).extrude(self.gear_length)
        # cut out shaft
        e = 0.03  # Margin of error
        w = e + 3.0 / 2  # distance of flat tab
        l = 4.0 / 2  # distance along flat tab (no error term as that is in the c term
        c = e + 0.5  # Curved end
        r = r.cut(
            cadquery.Workplane("XY")
            .transformed(offset=(0, 0, -5))
            .lineTo(w, 0)
            .lineTo(w, l)
            .threePointArc((0, l + c), (-w, l))
            .lineTo(-w, -l)
            .threePointArc((0, -l - c), (w, -l))
            .lineTo(w, 0)
            .close()
            .extrude(20)
        )
        return r

    # Construct mating points for two axes
    @property
    def mate_shaft(self):
        """This is the top of the box"""
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
        )


# ------------------- Test Stepper Assembly -------------------


class TestStepperAssembly(cqparts.Assembly):
    def make_components(self):
        motor = Stepper_28BYJ_48()
        # make motor transparent so can see block more clearly
        # motor._render = render_props(template="green", alpha=0.2)
        return {
            "motor": motor,
            "holder": Stepper_Holder(),
            "gear": StepperGear(
                tooth_count=22, effective_radius=8.6, width=3.5, tooth_height=1.8
            ),
        }

    def make_constraints(self):
        return [
            Fixed(self.components["holder"].mate_origin, CoordSystem()),
            Coincident(
                self.components["motor"].mate_centre,
                self.components["holder"].mate_centre,
            ),
            Coincident(
                self.components["gear"].mate_shaft, self.components["motor"].mate_gear
            ),
        ]

    def make_alterations(self):
        """cut out space for stepper in holder"""
        holder = self.components["holder"]
        self.components["motor"].apply_cutout(holder)


# ------------------- Display Result -------------------
# Could also export to another format
if __name__ == "__cq_freecad_module__":
    r = TestStepperAssembly()
    display(r)
