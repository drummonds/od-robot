#!/usr/bin/env python

# The code here should be representative of that in:
#   https://cqparts.github.io/cqparts/doc/tutorials/assembly.html

# ------------------- Wheel -------------------

import cadquery
import cqparts
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

# Across model constants that don't fit easily into parameter objects
# Position of motor
MOTOR_HEIGHT = 13.7
MOTOR_X = -47


class Wheel(cqparts.Part):
    """
    This is a model wheel which is designed to:
    - fit on a spintronics 3mm axle
    - Have a 216 standard o ring on it
    - Have a grub screw axis in which a 3mm brass insert can be put to screw it
    onto the axle.
    """
    # Parameters
    o_ring_id = PositiveFloat(30, doc="O-ring tyre internal diameter")
    o_ring_thickness = PositiveFloat(2.8, doc="O-ring tyre thickness")
    lip_d = PositiveFloat(0.8, doc="Lip size on wheel to retain O-ring")
    lip_thickness = PositiveFloat(0.8, doc="lip thickness")
    # 4+1+1
    grip_thickness = PositiveFloat(7, doc="grub screw holder thickness")
    # 3 + 2 * (6 + 2), shafter, plus insert length plus clearance
    grip_od = PositiveFloat(14, doc="")
    shaft_od = PositiveFloat(3 + 0.4, doc="")  # give a bit of clearance
    insert_od = PositiveFloat(4, doc="")

    # default appearance
    _render = render_props(template='wood_dark')

    def make(self):
        # Outside face
        r = cadquery.Workplane("front").circle(
            (self.o_ring_id+self.lip_d)/2).extrude(self.lip_thickness)
        r = r.faces(">Z").circle((self.o_ring_id)/2).extrude(self.o_ring_thickness)
        r = r.faces(">Z").circle((self.o_ring_id+self.lip_d)/2).extrude(self.lip_thickness)
        r = r.faces(">Z").box(self.grip_od, self.grip_od-9, self.grip_thickness, centered=(True, True, False))
        r = r.faces(">Z[-2]").circle(self.grip_od/2).extrude(self.grip_thickness)
        r = r.faces(">Z").workplane().hole(self.shaft_od)
        # Try and add insert holes
        #r = r.faces(">Z").workplane().transformed(offset=cq.Vector(0, -1.5, 1.0),rotate=cq.Vector(60, 0, 0)) \
        #     .rect(1.5,1.5,forConstruction=True).vertices().hole(0.25)
        r = r.faces(">X").workplane()\
             .hole(self.insert_od)
        return r

    def get_cutout(self, clearance=0):
        # A cylinder with a equal clearance on every face
        return cadquery.Workplane('XY', origin=(0, 0, -clearance)) \
            .circle((self.diameter / 2) + clearance) \
            .extrude(self.width + (2 * clearance))

    @property
    def width_midline_inside(self):
        """Distance from smooth inside wheel surface to midline"""
        return (self.lip_thickness
                + self.o_ring_thickness /2)

    @property
    def width_midline_outside(self):
        """Distance from grub screw axle grip to midline"""
        return (self.width_midline_inside
                + self.grip_thickness)
    @property
    def width(self):
        """How much axle is required to extend out from the inside of the
        wheel to the outside in order for the wheel to fit nicely."""
        return self.width_midline_inside + self.width_midline_outside

    @property
    def diameter(self):
        """Diamter of wheel (O-ring."""
        return self.o_ring_id + 2 * self.o_ring_thickness

    @property
    def mate_axle(self):
        plane = self.local_obj.faces(">Z").workplane().plane
        return Mate(self, CoordSystem.from_plane(plane))


class GearWheel(cqparts.Part):
    """
    This is a model gear wheel from Spintronics
    """
    # Parameters
    gear_od = PositiveFloat(22, doc="O-ring tyre internal diameter")
    gear_thickness = PositiveFloat(1.5, doc="O-ring tyre thickness")
    spacer_od = PositiveFloat(6, doc="Spacer diameter")  # give a bit of clearance
    spacer_thickness = PositiveFloat(10, doc="Space thickness/length")

    # default appearance
    _render = render_props(template='wood_dark')

    def make(self):
        # Outside face
        r = cadquery.Workplane("front").circle(
            self.spacer_od/2).extrude(self.spacer_thickness)
        r = r.faces("<Z") \
            .transformed(offset=(0, 0,
                                 (-self.gear_thickness + self.spacer_thickness)/2)) \
            .circle((self.gear_od)/2).extrude(self.gear_thickness)
        return r

    def get_cutout(self, clearance=1):
        # A cylinder with a equal clearance on every face
        return cadquery.Workplane('XY', origin=(0, 0, -clearance)) \
            .circle((self.diameter / 2) + clearance) \
            .extrude(self.gear_thickness + (2 * clearance))

    @property
    def width(self):
        """How much axle is required to extend out from the inside of the
        wheel to the outside in order for the wheel to fit nicely."""
        return self.spacer_thickness

    @property
    def diameter(self):
        """Diameter of gear"""
        return self.gear_od

    @property
    def mate_centre(self):
        """Assumes rotating around Z axis"""
        return Mate(self, CoordSystem(
            origin=(0, 0, +self.width / 2),
#            xDir=(1, 0, 0), normal=(0, -1, 0),
        ))


    # default appearance
    _render = render_props(color=(240,240,240))  # Light grey


class Motor(cqparts.Part):
    """
    This is a standard DC motor with a worm gear
    """
    # Parameters
    motor_od = PositiveFloat(24.1, doc="Motor diameter")
    motor_length = PositiveFloat(30.5, doc="Motor length")
    shaft_od = PositiveFloat(2, doc="Shaft diameter")
    shaft_length = PositiveFloat(6.5, doc="Shaft length")
    # Modelling worm drive as a cylinder
    gear_od = PositiveFloat(6, doc="Gear diameter")
    gear_length = PositiveFloat(10, doc="Gear length")

    # default appearance
    _render = render_props(color=(200, 200, 0))  # dark yellow

    def make(self):
        # Outside face
        r = cadquery.Workplane("YZ").circle(
            (self.motor_od)/2).extrude(self.motor_length)
        r = r.faces(">X").circle((self.shaft_od)/2).extrude(self.shaft_length)
        r = r.faces(">X").circle((self.gear_od)/2).extrude(self.gear_length)
        return r

    def get_cutout(self, clearance=1):
        # Outside face
        r = cadquery.Workplane("YZ").circle(clearance + (self.motor_od/2)).extrude(self.motor_length)
        return r

# ------------------- Axle -------------------


class Axle(cqparts.Part):
    # Parameters
    length = PositiveFloat(50, doc="axle length")
    diameter = PositiveFloat(3, doc="axle diameter")

    # default appearance
    _render = render_props(color=(50, 50, 90))  # dark grey

    def make(self):
        axle = cadquery.Workplane('ZX', origin=(0, -self.length/2, 0)) \
            .circle(self.diameter / 2).extrude(self.length)
        return axle

    # wheel mates, assuming they rotate around z-axis
    @property
    def mate_left(self):
        return Mate(self, CoordSystem(
            origin=(0, -self.length / 2, 0),
            xDir=(1, 0, 0), normal=(0, -1, 0),
        ))

    @property
    def mate_right(self):
        return Mate(self, CoordSystem(
            origin=(0, self.length / 2, 0),
            xDir=(1, 0, 0), normal=(0, 1, 0),
        ))

    @property
    def mate_centre(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, 0),
            xDir=(1, 0, 0), normal=(0, 1, 0),
        ))

    def get_cutout(self, clearance=0.5):
        return cadquery.Workplane('ZX', origin=(0, -self.length/2 - clearance, 0)) \
            .circle((self.diameter / 2) + clearance) \
            .extrude(self.length + (2 * clearance))


# ------------------- Chassis -------------------

class Chassis(cqparts.Part):
    """This should:
    - Hold the motor
    - hold the Axle
    - provide couplings front and back
    - provide mounts for the battery
    - provide mounts for a power switch"""
    # Parameters
    width = PositiveFloat(50, doc="chassis width")
    base_x = PositiveFloat(100, doc="base x length")
    base_y = PositiveFloat(20, doc="base y width")
    base_z = PositiveFloat(3, doc="base z thickness")

    bendy = Float(3, doc="width of bits that need to bend")
    motor_y = Float(20, doc="motor y length")
    motor_x = Float(30.5, doc="motor x diameter")
    axle_x = PositiveFloat(bendy.default + motor_x.default + 13.6,
                           doc="axle X displacement from offset")
    axle_d = PositiveFloat(3, doc="axle diameter")
    axle_r = PositiveFloat(axle_d.default / 2, doc="axle radius")
    axle_z = PositiveFloat(26, doc="axle z displacement from base")
    axle_gap = PositiveFloat(1.1, doc="Axle amount of click")

    side_thickness = PositiveFloat(3, doc="Width of axle supporting plates")

    clamp_bolt_size = PositiveFloat(3, doc="Diameter of clamping bolt")

    _render = render_props(template='wood_light')

    def side_wall(self, z1):
        # Define the points that the polyline will be drawn to/thru
        points = [
            (0, self.base_z),
            (self.bendy + self.motor_x, self.base_z),
            (self.bendy + self.motor_x, self.base_z + self.motor_y),
            (self.bendy + self.motor_x - self.bendy, self.base_z + self.motor_y),
            (self.bendy + self.motor_x - self.bendy, self.base_z + self.motor_y + self.bendy),
            (self.bendy + self.motor_x + self.bendy, self.base_z + self.motor_y + self.bendy),
            (self.axle_x - self.axle_gap, self.axle_z + self.axle_r + self.bendy ),
            (self.axle_x - self.axle_gap, self.axle_z + self.axle_r),
            (self.axle_x - self.axle_r, self.axle_z + self.axle_r ),
            (self.axle_x - self.axle_r + self.axle_gap, self.axle_z  - self.axle_r),
            (self.axle_x + self.axle_r, self.axle_z - self.axle_r ),
            (self.axle_x + self.axle_r, self.axle_z + self.axle_r ),
            (self.axle_x + self.axle_r, self.axle_z + self.axle_r + self.bendy ),
            (self.axle_x + self.axle_r + self.bendy, self.axle_z + self.axle_r + self.bendy ),
            (self.axle_x + self.axle_r + self.bendy, 0)
        ]
        r = cadquery.Workplane("front") \
            .transformed(offset=(-self.base_x/2, z1, 0), rotate=(90, 0, 0),) \
            .polyline(points).close() \
            .extrude(self.side_thickness)
        # locate at axle position
        r = r.transformed(offset=(self.axle_x, self.axle_z,
                                  self.side_thickness))
        r = r.transformed(offset=(0, 0, 0)).hole(self.axle_d + 0.5,
                                                 depth=self.side_thickness+2)
        return r

    def rear_axle_holder(self, z1):
        # Define the points that the polyline will be drawn to/thru
        axle_x = 10  # TODO link to back axle position
        axle_x_mid = axle_x / 2
        x1 = 0
        x2 = axle_x_mid - self.axle_gap#
        x3 = axle_x_mid - self.axle_r + self.axle_gap
        x4 = axle_x_mid + self.axle_r
        x5 = axle_x
        y1 = 0
        y2 = self.axle_z + self.axle_r + self.bendy # highest
        points = [
            (x1, y2),
            (x2, y2),
            (x2, self.axle_z + self.axle_r ),
            (x3, self.axle_z  - self.axle_r),
            (x4, self.axle_z - self.axle_r ),
            (x4, self.axle_z + self.axle_r ),
            (x4, self.axle_z + self.axle_r + self.bendy ),
            (x5, y2),
            (x5, y1),
            # (0, 0)  # Done on closure
        ]
        r = cadquery.Workplane("front") \
            .transformed(offset=(-82, z1, 0), rotate=(90, 0, 0),) \
            .polyline(points).close() \
            .extrude(self.side_thickness*1.5)
        # locate at axle position
        r = r.transformed(offset=(axle_x_mid, self.axle_z,
                                  self.side_thickness*1.5))
        r = r.transformed(offset=(0, 0, 0)).hole(self.axle_d + 0.5,
                                                 depth=self.side_thickness+2)
        return r

    def motor_clip(self, z1, is_left=True):
        """Define a clip that will go over the motor and hold it
        from wiggling and secure."""
        length_x = 10
        x_offset = -37
        x1 = 0
        x2 = length_x / 2
        x3 = length_x
        y1 = 0
        y2 = self.motor_y + 14  # highest
        points = [
            (x1, y2),
            (x3, y2),
            (x3, y1),
            # (0, 0)  # Done on closure
        ]
        r = cadquery.Workplane("front") \
            .transformed(offset=(x_offset, z1, 0), rotate=(90, 0, 0),) \
            .polyline(points).close() \
            .extrude(self.side_thickness)
        # Add some boxes to wrap around
        # # easier to model than extruding in the X direction
        for w, l, o in ((2, 29.6, -3.6), (2, 26, 0),
                        (1.2, 22, 0), (1.2, 18, 0),
                        (1.2, 16, 0), (1.2, 13, 0), (1.0, 11, 0), (1, 8, 0),):
            if is_left:
                r = r.faces(">Y")
            else:
                r = r.faces("<Y")
            r = r.workplane().transformed(offset=(0, o, w/2)).box(length_x, l, w)
            # locate at axle position
        r = r.transformed(offset=(x2-length_x/2, self.axle_z - 8,
                                  self.side_thickness-1))
        # The zero offset made a difference so keep
        # Adding a hole to
        r = r.transformed(offset=(0, 0, 0))\
                .hole(self.clamp_bolt_size + 0.5, depth=20)
                # .box(2, 1, 1)
        return r

    def make(self):
        r = cadquery.Workplane("front")\
            .transformed(offset=(-40, 0, 0),) \
            .box(self.base_x, self.base_y, self.base_z)
        # Add some holes to add battery boxes and trailers
        r = r.faces("<Z").workplane() \
            .rect(self.base_x-8, self.base_y-8, forConstruction=True).\
            vertices().hole(3.5)
        r = r.faces("<Z").workplane() \
            .rect(self.base_x-60, self.base_y-10, forConstruction=True).\
            vertices().hole(3.5)
        r = r.union(self.side_wall(-self.base_y/2+self.side_thickness))
        r = r.union(self.side_wall(+self.base_y/2))
        r = r.union(self.rear_axle_holder(-self.base_y/2+3+self.side_thickness))
        r = r.union(self.rear_axle_holder(+self.base_y/2-3))
        r = r.union(self.motor_clip(-self.base_y/2+3+self.side_thickness, is_left = False))
        r = r.union(self.motor_clip(+self.base_y/2-3, is_left = True))
        m = Motor()
        m1 = m.make()
        r1 = cadquery.Workplane("front").transformed(offset=(30, 30, 30))
        r = r.cut(m.make().translate((MOTOR_X, 0, MOTOR_HEIGHT)))
        return r



# ------------------- Wheel Assembly -------------------


class WheeledAxle(cqparts.Assembly):
    axle_diam = PositiveFloat(3, doc="axle diameter")
    axle_track = PositiveFloat(25, doc="distance between wheel tread midlines")
    wheel_clearance = PositiveFloat(3, doc="distance between wheel and chassis")

    def make_components(self):
        wheel_l = Wheel()
        wheel_r = Wheel()
        axle_length = self.axle_track + wheel_l.width + wheel_r.width
        return {
            'axle': Axle(length=axle_length, diameter=self.axle_diam),
            'left_wheel': wheel_l,
            'right_wheel': wheel_r,
        }

    def make_constraints(self):
        return [
            Fixed(self.components['axle'].mate_origin, CoordSystem()),
            Coincident(
                self.components['left_wheel'].mate_axle,
                self.components['axle'].mate_left
            ),
            Coincident(
                self.components['right_wheel'].mate_axle,
                self.components['axle'].mate_right
            ),
        ]

    def apply_cutout(self, part):
        # Cut wheel & axle from given part
        axle = self.components['axle']
        left_wheel = self.components['left_wheel']
        right_wheel = self.components['right_wheel']
        local_obj = part.local_obj
        local_obj = local_obj \
            .cut((axle.world_coords - part.world_coords) + axle.get_cutout()) \
            .cut((left_wheel.world_coords - part.world_coords) + left_wheel.get_cutout(self.wheel_clearance)) \
            .cut((right_wheel.world_coords - part.world_coords) + right_wheel.get_cutout(self.wheel_clearance))
        part.local_obj = local_obj

# ------------------- GearedWheel Assembly -------------------


class GearedWheeledAxle(WheeledAxle):
    """This is a normal wheeled axle with a demo gear drive in the middle.
    The gear wheel is assumed to be in the middle with spacers each side"""
    gear_od = PositiveFloat(22, "Outside diameter of gear wheel")
    gear_width = PositiveFloat(1.5, "Gear wheel width")
    spare_od = PositiveFloat(6, "Spare outside diameter")
    spacer_width = PositiveFloat(10, "spacer width")

    def make_components(self):
        gear = GearWheel()
        r = super(GearedWheeledAxle, self).make_components()
        r['gear_wheel'] = gear
        return r

    def make_constraints(self):
        result = super(GearedWheeledAxle, self).make_constraints()
        result.append(
            Coincident(
                self.components['gear_wheel'].mate_centre,
                self.components['axle'].mate_centre
            ))
        return result



# ------------------- Train Assembly -------------------

class Train(cqparts.Assembly):
    # Parameters
    wheelbase_offset = Float(-3, "Position of front axis")
    wheelbase = PositiveFloat(65, "distance between front and rear axles")
    axle_track = PositiveFloat(26.6, "distance between tread midlines")

    def make_components(self):
        self.chassis = Chassis(width=self.axle_track)
        return {
            'chassis': self.chassis,
            'front_axle': GearedWheeledAxle(
                axle_track=self.axle_track,
            ),
            'rear_axle': WheeledAxle(
                axle_track=self.axle_track,
            ),
           'motor': Motor(),
        }

    def make_constraints(self):
        axle_z = 10
        return [
            Fixed(self.components['chassis'].mate_origin),
            Coincident(
                self.components['front_axle'].mate_origin,
                Mate(self.components['chassis'],
                     CoordSystem((self.wheelbase_offset, 0, self.chassis.axle_z))),
            ),
            Coincident(
                self.components['rear_axle'].mate_origin,
                Mate(self.components['chassis'],
                     CoordSystem((self.wheelbase_offset-
                                  self.wheelbase, 0, self.chassis.axle_z))),
            ),
            Coincident(
                self.components['motor'].mate_origin,
                Mate(self.components['chassis'], CoordSystem((MOTOR_X, 0, MOTOR_HEIGHT))),
            ),
        ]

    def make_alterations(self):
        # cut out wheel wells
        chassis = self.components['chassis']
        self.components['front_axle'].apply_cutout(chassis)
        self.components['rear_axle'].apply_cutout(chassis)


# -------------------- New Start ----------------------
from cqparts_fasteners.male import MaleFastenerPart
from cqparts.display import display


class ThreadedRod(cqparts.Part):
    """
    This is a length of threadedrod (without thread)
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


# ------------------- Train Assembly -------------------

class TopAssembly(cqparts.Assembly):
    # Parameters
    rod_offset = Float(-10, "Difference between ros")

    def make_components(self):
        return {
            'front_rod': ThreadedRod(),
            'rear_rod': ThreadedRod(),
        }

    # def make_constraints(self):
    #     return [
    #         Fixed(self.components['front_rod'].mate_origin, CoordSystem()),
    #         Coincident(
    #             self.components['rear_rod'].mate_origin,
    #             Mate(self.components['front_rod'],
    #                  CoordSystem((self.rod_offset, 0, 0))),
    #         ),
    #     ]




# ------------------- Display Result -------------------
# Could also export to another format
if __name__ != 'TestEngineWholeModel':
    # not run as a module, so display result
    # m = Train()
    #m = Chassis()
    # m = WheeledAxle()
    # m = Axle()
    # m = Wheel()
    # m = Motor()
    #m = ThreadedRod()
    m = TopAssembly()
    display(m)
