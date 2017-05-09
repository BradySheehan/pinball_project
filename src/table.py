from direct.directbase import DirectStart
from direct.directtools.DirectGeometry import LineNodePath
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup, OdeHingeJoint, OdeBallJoint, OdeUtil
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom, OdeCylinderGeom
from panda3d.core import BitMask32, Vec4, Quat, VBase3, Vec3
from panda3d.core import Light, AmbientLight, DirectionalLight
import sys
import os
sys.path.append('../scripts/')
from visualizeGeoms_copy import wireGeom


class Table():
    # class that sets up the graphics and physics

    def __init__(self, button_enabled):
        if button_enabled:
            from RPi import GPIO
            global GPIO
        self.quat_right = Quat(0.0, 0.0, 0.0, 0.0)
        v = VBase3(27.0, 0.0, 0.0)
        self.quat_right.setHpr(v)
        self.quat_left = Quat(0.0, 0.0, 0.0, 0.0)
        v2 = VBase3(-27.0, 0.0, 0.0)
        self.quat_left.setHpr(v2)
        self.button_enabled = button_enabled
        self.setup_ode_world_params()
        self.setup_camera()
        self.setup_light()
        self.load_models()
        self.not_first_time = False
        # rotation angle for flippers
        self.h_left = 0
        self.h_right = 0
        # accelleration for flippers
        self.accell_flippers = .005
        # velocity for flippers
        self.velocity_left = 1
        self.velocity_right = 1
        # flags used for flipper movement
        self.left_flipper_up = False
        self.right_flipper_up = False
        # amount of force applied to ball when a flipper hits it
        self.force_applied_to_ball_left = 0.1;
        self.force_applied_to_ball_right = 0.1;
        self.force_increase_rate = 1.0;
        #frame rate
        self.simTimeStep = 1.0/35
        self.ball_not_sinking = True
        #force applied on ball launch
        self.launch_force = 0.0
        self.can_launch = True
        self.metroid_door = loader.loadMusic("audio/Metroid_Door.wav")

    def move_left_flipper(self):
        self.left_flipper_up = True

    def stop_left_flipper(self):
        self.left_flipper_up = False

    def move_right_flipper(self):
        self.right_flipper_up = True

    def stop_right_flipper(self):
        self.right_flipper_up = False

    # def destroy(self):
    #     self.ignoreAll()

    def setup_camera(self):
        # print "setup camera"
        base.camera.setPos(10, 0, 15)
        base.camera.lookAt(0, 0, 0)

    def setup_light(self):
        # print "setup light"
        # set light in panda3d from blender
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor(Vec4(0.0, 0.0, 0.0, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)
        directionalLight = DirectionalLight('directionalLight')
        directionalLight.setColor(Vec4(.85, .85, .85, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(180, -20, 0)
        render.setLight(directionalLightNP)
        directionalLight = DirectionalLight('directionalLight')
        directionalLight.setColor(Vec4(.85, .85, .85, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(0, -20, 0)
        render.setLight(directionalLightNP)


    def setup_ode_world_params(self):
        # print "setup ode world params"
        self.world = OdeWorld()
        # gravity needs to be adjusted (to simulate table being tilted)
        # self.world.setGravity(4.5, 0, -10)
        self.world.setGravity(1.0, 0, -10)
        self.world.initSurfaceTable(3)  # we need to figure out what this does
        self.world.setSurfaceEntry(
            0,
            0,
            150,
            0.0,
            9.1,
            0.0,
            0.0000,
            0.0,
            0.002)  # and what this does

        self.world.setSurfaceEntry(
            0, #surface ID
            1, #surface ID
            50,  #Friction (mu)
            0.1,  # bounce
            0.0,  # bounce velocity (minimum velocity a body must have before it bounces)
            0.0,
            0.0000,
            1.0, #slip
            0.00) #damping

        # for ball hitting the bumpers
        self.world.setSurfaceEntry(
            0, #surface ID
            2, #surface ID
            50,  #Friction (mu)
            .5,  # bounce
            0.0,  # bounce velocity (minimum velocity a body must have before it bounces)
            0.0,
            0.0000,
            0.0, #slip
            0.00) #damping

        self.space1 = OdeSimpleSpace()
        self.space1.setAutoCollideWorld(self.world)
        self.contactgroup = OdeJointGroup()
        self.space1.setAutoCollideJointGroup(self.contactgroup)

    def load_models(self):
        # print "load models"
        # self.ball_egg = loader.loadModel("models/table_collide_no_culling.egg")
        self.table_egg = loader.loadModel(
            "models/table_mods.egg")
        self.ball = self.import_ball(self.table_egg)
        self.setup_ball_physics(0.1, 0.1)

        self.import_table(self.table_egg)
        self.setup_table_physics()
        self.import_innards(self.table_egg)
        self.import_flippers(self.table_egg)
        self.import_ramp(self.table_egg)

    def add_plane_to_physics(self, params1, params2, params3, params4):
        # Returns a handle to the OdePlaneGeom object with the specified
        # parameters, used in setup_table_physics
        plane = OdePlaneGeom(self.space1, params1, params2, params3, params4)
        return plane

    def add_wall_to_physics(self, dimx, dimy, dimz, locx, locy, locz):
        # Returns a handle to the OdeBoxGeom object with the specified
        # parameters, used in setup_table_physics
        box = OdeBoxGeom(self.space1, dimx, dimy, dimz)
        box.setPosition(locx, locy, locz)
        return box

    def add_innard_cube_to_physics(self, innardNP, dimx, dimy, dimz):
        innard = OdeBoxGeom(self.space1, dimx, dimy, dimz)
        innard.setPosition(innardNP.getPos())
        innard.setQuaternion(innardNP.getQuat())
        return innard

    def add_innard_cylinder_to_physics(self, innardNP, radius, length):
        innard = OdeCylinderGeom(self.space1, radius, length)
        innard.setPosition(innardNP.getPos())
        innard.setQuaternion(innardNP.getQuat())
        return innard

    def add_flipper_to_physics(self, flipperNP, num):
        flipper_mass = OdeMass()
        flipper_mass.setBox(50, .23, .720, .338)
        flipper_body = OdeBody(self.world)
        flipper_body.setMass(flipper_mass)
        flipper_body.setPosition(flipperNP.getPos())
        if num == 2 :
            flipper_body.setQuaternion(self.quat_left)
        else :
            flipper_body.setQuaternion(self.quat_right)
        flipper = OdeBoxGeom(self.space1, .23, .720, .338)
        self.space1.setSurfaceType(flipper, 1)
        flipper.setBody(flipper_body)

        return flipper_body


    def setup_table_physics(self):
        # print "\t \t setup table physics"
        self.ground_plane = self.add_plane_to_physics(0, 0, 1, 0)
        self.space1.setSurfaceType(self.ground_plane,0)
        self.wall_west = self.add_wall_to_physics(10, 0.1, 2.5, 0, -3, 1)
        self.wall_east = self.add_wall_to_physics(10, 0.1, 2.5, 0, 3, 1)
        self.wall_north = self.add_wall_to_physics(0.1, 6, 2.5, -5, 0, 1)
        self.wall_south = self.add_wall_to_physics(0.5, 6, 2.5, 5, 0, 1)
        self.launch_wall = self.add_wall_to_physics(
            6.5, 0.2, 0.5, 1.75, 2.6, 0.25)

    def import_table(self, table_egg):
        # print "\t import table egg"
        plane1 = table_egg.find("**/Plane.001")
        plane1.reparentTo(render)
        plane1.flattenStrong()
        plane2 = table_egg.find("**/Plane.002")
        plane2.reparentTo(render)
        plane2.flattenStrong()
        plane3 = table_egg.find("**/Plane.003")
        plane3.reparentTo(render)
        plane3.flattenStrong()
        plane4 = table_egg.find("**/Plane.004")
        plane4.reparentTo(render)
        plane4.flattenStrong()
        plane5 = table_egg.find("**/Plane.005")
        plane5.reparentTo(render)
        plane5.flattenStrong()

        inner_wall = table_egg.find("**/Cube")
        inner_wall.reparentTo(render)
        inner_wall.flattenStrong()

        roof_for_launch_wall = table_egg.find("**/Cube.032")
        roof_for_launch_wall.reparentTo(render)
        roof_for_launch_wall.flattenStrong()
        self.door = table_egg.find("**/Cube.033")
        self.door_holder = self.door

    def import_innards(self, table_egg):
        flipper_r_wall = table_egg.find("**/Cube.002")
        flipper_r_wall_geom = self.add_innard_cube_to_physics(
            flipper_r_wall, 1.5, 0.05, 0.5)
        flipper_r_wall.reparentTo(render)
        flipper_r_wall.flattenStrong()

        flipper_l_wall = table_egg.find("**/Cube.001")
        flipper_l_wall_geom = self.add_innard_cube_to_physics(
            flipper_l_wall, 1.5, 0.05, 0.5)
        flipper_l_wall.reparentTo(render)
        flipper_l_wall.flattenStrong()

        l_bumper_wall = table_egg.find("**/Cube.003")
        l_bumper_wall_geom = self.add_innard_cube_to_physics(
            l_bumper_wall, 1.5, 0.2, 0.5)
        l_bumper_wall.reparentTo(render)
        l_bumper_wall.flattenStrong()

        r_bumper_wall = table_egg.find("**/Cube.004")
        r_bumper_wall_geom = self.add_innard_cube_to_physics(
            r_bumper_wall, 1.5, 0.15, 0.5)
        # test = wireGeom().generate('box', extents=(1.5, 0.15, 0.5))
        # test.setPos(r_bumper_wall.getPos())
        # test.reparentTo(render)
        r_bumper_wall.reparentTo(render)
        r_bumper_wall.flattenStrong()

        rb_bumper = table_egg.find("**/Cylinder")
        #left triangle bottom of table
        self.setup_physics_rb_bumper(rb_bumper)

        rb_bumper.reparentTo(render)
        rb_bumper.flattenStrong()

        lb_bumper = table_egg.find("**/Cylinder.001")
        #right triangle bottom of table
        self.setup_physics_lb_bumper(lb_bumper)
        lb_bumper.reparentTo(render)
        lb_bumper.flattenStrong()

        #bumper rings
        lb_bumper_ring = table_egg.find("**/Cylinder.011")
        lb_bumper_ring.reparentTo(render)
        lb_bumper_ring.flattenStrong()

        rb_bumper_ring = table_egg.find("**/Cylinder.013")
        rb_bumper_ring.reparentTo(render)
        rb_bumper_ring.flattenStrong()

        tall_bumper_ring1 = table_egg.find("**/Cylinder.014")
        tall_bumper_ring1.reparentTo(render)
        tall_bumper_ring1.flattenStrong()

        tall_bumper_ring2 = table_egg.find("**/Cylinder.015")
        tall_bumper_ring2.reparentTo(render)
        tall_bumper_ring2.flattenStrong()

        tall_bumper_ring3 = table_egg.find("**/Cylinder.016")
        tall_bumper_ring3.reparentTo(render)
        tall_bumper_ring3.flattenStrong()

        #tall bumper left
        tall_round_bumper_left = table_egg.find("**/Cylinder.021")
        self.tall_round_bumper_geom_left = self.add_innard_cylinder_to_physics(tall_round_bumper_left, float(0.35/2), 1)
        self.space1.setSurfaceType(self.tall_round_bumper_geom_left,2)
        tall_round_bumper_left.reparentTo(render)
        tall_round_bumper_left.flattenStrong()

        tall_bumper_ring1_left = table_egg.find("**/Cylinder.018")
        tall_bumper_ring1_left.reparentTo(render)
        tall_bumper_ring1_left.flattenStrong()

        tall_bumper_ring2_left = table_egg.find("**/Cylinder.019")
        tall_bumper_ring2_left.reparentTo(render)
        tall_bumper_ring2_left.flattenStrong()

        tall_bumper_ring3_left = table_egg.find("**/Cylinder.020")
        tall_bumper_ring3_left.reparentTo(render)
        tall_bumper_ring3_left.flattenStrong()

        #wide round bumper
        wide_round_bumper_left = table_egg.find("**/Cylinder.017")
        self.wide_round_bumper_geom_left = self.add_innard_cylinder_to_physics(wide_round_bumper_left, .5, .25)
        self.space1.setSurfaceType(self.wide_round_bumper_geom_left,2)
        wide_round_bumper_left.reparentTo(render)
        wide_round_bumper_left.flattenStrong()

        #tesla coils kinda
        tesla_tall = table_egg.find("**/Cylinder.022")
        self.tesla_tall_geom = self.add_innard_cylinder_to_physics(tesla_tall, .2, 1)
        self.space1.setSurfaceType(self.tesla_tall_geom,2)
        tesla_tall.reparentTo(render)
        tesla_tall.flattenStrong()

        tesla_tall_top = table_egg.find("**/Cylinder.023")
        tesla_tall_top.reparentTo(render)
        tesla_tall_top.flattenStrong()

        tesla_middle = table_egg.find("**/Cylinder.025")
        self.tesla_middle_geom = self.add_innard_cylinder_to_physics(tesla_middle, .2, 1)
        self.space1.setSurfaceType(self.tesla_middle_geom,2)
        tesla_middle.reparentTo(render)
        tesla_middle.flattenStrong()

        tesla_tall_middle = table_egg.find("**/Cylinder.024")
        tesla_tall_middle.reparentTo(render)
        tesla_tall_middle.flattenStrong()

        tesla_short = table_egg.find("**/Cylinder.026")
        self.tesla_short_geom = self.add_innard_cylinder_to_physics(tesla_short, .2, 1)
        self.space1.setSurfaceType(self.tesla_short_geom,2)
        tesla_short.reparentTo(render)
        tesla_short.flattenStrong()

        tesla_tall_short = table_egg.find("**/Cylinder.027")
        tesla_tall_short.reparentTo(render)
        tesla_tall_short.flattenStrong()

        angled_launch_wall = table_egg.find("**/Cube.005")

        angled_launch_wall_geom = self.add_innard_cube_to_physics(
            angled_launch_wall, 1.0, 0.1, 0.5)
        angled_launch_wall.reparentTo(render)
        angled_launch_wall.flattenStrong()

        # input pink bumpers Cylinder.002 and Cylinder.003
        round_bumper_left = table_egg.find("**/Cylinder.002")
        self.round_bumper_left_geom = self.add_innard_cylinder_to_physics(
            round_bumper_left, float(0.5/2), 0.5)
        self.space1.setSurfaceType(self.round_bumper_left_geom,2)
        round_bumper_left.reparentTo(render)
        round_bumper_left.flattenStrong()
        round_bumper_right = table_egg.find("**/Cylinder.003")
        self.round_bumper_right_geom = self.add_innard_cylinder_to_physics(
            round_bumper_right, float(0.5/2), 0.5)
        self.space1.setSurfaceType(self.round_bumper_right_geom,2)
        round_bumper_right.reparentTo(render)
        round_bumper_right.flattenStrong()

        #tall green bumper
        angled_wall_bumper = table_egg.find("**/Cylinder.004")
        self.tall_round_bumper_geom = self.add_innard_cylinder_to_physics(angled_wall_bumper, float(0.35/2), 1)
        self.space1.setSurfaceType(self.tall_round_bumper_geom,2)
        angled_wall_bumper.reparentTo(render)
        angled_wall_bumper.flattenStrong()

        angled_launch_wall2 = table_egg.find("**/Cube.006")

        angled_launch_wall_geom2 = self.add_innard_cube_to_physics(
            angled_launch_wall2, 1.0, 0.1, 0.5)
        angled_launch_wall2.reparentTo(render)
        angled_launch_wall2.flattenStrong()

        angled_launch_wall3 = table_egg.find("**/Cube.007")
        angled_launch_wall_geom3 = self.add_innard_cube_to_physics(
            angled_launch_wall3, 1.0, 0.1, 0.5)
        angled_launch_wall3.reparentTo(render)
        angled_launch_wall3.flattenStrong()

        angled_launch_wall4 = table_egg.find("**/Cube.008")

        angled_launch_wall_geom4 = self.add_innard_cube_to_physics(
            angled_launch_wall4, 1.0, 0.1, 0.5)
        angled_launch_wall4.reparentTo(render)
        angled_launch_wall4.flattenStrong()

        angled_launch_wall5 = table_egg.find("**/Cube.009")

        angled_launch_wall_geom5 = self.add_innard_cube_to_physics(
            angled_launch_wall5, 1.0, 0.1, 0.5)
        angled_launch_wall5.reparentTo(render)
        angled_launch_wall5.flattenStrong()

        # cubes 17 - 21 are the upper half of the angled wall, load those now
        upper_wall1 = table_egg.find("**/Cube.017")
        upper_wall1_geom = self.add_innard_cube_to_physics(
            upper_wall1, 1.0, 0.1, 0.5)
        upper_wall1.reparentTo(render)
        upper_wall1.flattenStrong()

        upper_wall2 = table_egg.find("**/Cube.018")
        upper_wall2_geom = self.add_innard_cube_to_physics(
            upper_wall2, 1.0, 0.1, 0.5)
        upper_wall2.reparentTo(render)
        upper_wall2.flattenStrong()

        upper_wall3 = table_egg.find("**/Cube.019")
        upper_wall3_geom = self.add_innard_cube_to_physics(
            upper_wall3, 1.0, 0.1, 0.5)
        upper_wall3.reparentTo(render)
        upper_wall3.flattenStrong()

        upper_wall4 = table_egg.find("**/Cube.020")
        upper_wall4_geom = self.add_innard_cube_to_physics(
            upper_wall4, 1.0, 0.1, 0.5)
        upper_wall4.reparentTo(render)
        upper_wall4.flattenStrong()


        upper_wall5 = table_egg.find("**/Cube.021")
        upper_wall5_geom = self.add_innard_cube_to_physics(
            upper_wall5, 1.0, 0.1, 0.5)
        upper_wall5.reparentTo(render)
        upper_wall5.flattenStrong()

        #22 - 27 are more parts of the angled launch wall
        lower_wall1 = table_egg.find("**/Cube.022")
        lower_wall1_geom = self.add_innard_cube_to_physics(
            lower_wall1, 1.0, 0.1, 0.5)
        lower_wall1.reparentTo(render)
        lower_wall1.flattenStrong()

        upper_wall6 = table_egg.find("**/Cube.023")
        upper_wall6_geom = self.add_innard_cube_to_physics(
            upper_wall6, 1.0, 0.1, 0.5)
        upper_wall6.reparentTo(render)
        upper_wall6.flattenStrong()

        lower_wall2 = table_egg.find("**/Cube.024")
        lower_wall2_geom = self.add_innard_cube_to_physics(
            lower_wall2, 1.0, 0.1, 0.5)
        lower_wall2.reparentTo(render)
        lower_wall2.flattenStrong()

        upper_wall7 = table_egg.find("**/Cube.025")
        upper_wall7_geom = self.add_innard_cube_to_physics(
            upper_wall7, 1.0, 0.1, 0.5)
        upper_wall7.reparentTo(render)
        upper_wall7.flattenStrong()

        lower_wall3 = table_egg.find("**/Cube.026")
        lower_wall3_geom = self.add_innard_cube_to_physics(
            lower_wall3, 1.0, 0.1, 0.5)
        lower_wall3.reparentTo(render)
        lower_wall3.flattenStrong()

        upper_wall8 = table_egg.find("**/Cube.027")
        upper_wall8_geom = self.add_innard_cube_to_physics(
            upper_wall8, 1.0, 0.1, 0.5)
        upper_wall8.reparentTo(render)
        upper_wall8.flattenStrong()


        # lower_wall4 = table_egg.find("**/Cube.012")
        # lower_wall4_geom = self.add_innard_cube_to_physics(
        #     lower_wall4, 1.0, 0.1, 0.5)
        # lower_wall4.reparentTo(render)
        # lower_wall4.flattenStrong()

        lower_wall6 = table_egg.find("**/Cylinder.012")
        lower_wall6.reparentTo(render)
        lower_wall6.flattenStrong()
        #need to add this to physics
        upper_wall_triangle = self.add_wall_to_physics(
            1.0, 0.01, 0.5, -0.0, -2.7, 0.25)
        self.upper_wall_triangle = self.launch_wall_helper(
            upper_wall_triangle, 35, 1, 0.1, 0.5)

        lower_wall_triangle = self.add_wall_to_physics(
            0.9, 0.01, 0.5, 0.7, -2.71, 0.25)
        self.lower_wall_triangle = self.launch_wall_helper(
            lower_wall_triangle, -35, 0.9, 0.1, 0.5)

        upper_np = table_egg.find("**/Cylinder.007")
        lower_np = table_egg.find("**/Cylinder.008")
        self.import_launch_wall_bumper(upper_np, lower_np)

        self.plunger = lower_np = table_egg.find("**/Cube.012")
        # the ode geom should stay static, just there to stop the ball from falling
        self.plunger_geom = self.add_innard_cube_to_physics(
            self.plunger, .25, 0.25, 0.25)
        self.plunger.reparentTo(render)

    def import_launch_wall_bumper(self, upper_np, lower_np):
        wall1 = self.add_wall_to_physics(1.1, 0.05, 0.5, -1, 2.25, 0.25)
        self.upper_launch_wall = self.launch_wall_helper(wall1, -26, 1.1, 0.05, 0.5)

        wall2 = self.add_wall_to_physics(0.75, 0.05, 0.5, 0.35, 2.15, 0.25)
        self.lower_launch_wall= self.launch_wall_helper(wall2, 70, 0.75, 0.05, 0.5)


        wall3 = self.add_wall_to_physics(0.65, 0.05, 0.5, -0.1, 1.9, 0.25)
        wall3 = self.launch_wall_helper(wall3, -15, 0.65, 0.05, 0.5)

        upper_np.reparentTo(render)
        upper_np.flattenStrong()
        lower_np.reparentTo(render)
        lower_np.flattenStrong()

    def launch_wall_helper(self, geom, rotation, dimx, dimy, dimz):
        quat = Quat(0.0, 0.0, 0.0, 0.0)
        v = VBase3(rotation, 0.0, 0.0)
        quat.setHpr(v)
        geom.setQuaternion(quat)
        # box_wall1 = wireGeom().generate('box', extents=(dimx, dimy, dimz))
        # box_wall1.setPos(geom.getPosition())
        # box_wall1.setQuat(geom.getQuaternion())
        # box_wall1.reparentTo(render)
        return geom

    def import_flippers(self, table_egg):
        # ---- Right Flipper ----
        self.pivot_right = render.attachNewNode("pivot_right")  # pivot point
        self.flipper = table_egg.find("**/Cube.010")
        self.pivot_right.setPos(4.29, 0.56, .09)
        self.flipper_body_right = self.add_flipper_to_physics(self.flipper, 1)

        # flip_wire = wireGeom().generate('box', extents=((.25, .720, .338)))
        # flip_wire.setPos(self.flipper_body_right.getPosition())
        # flip_wire.setHpr(
        #     Quat(self.flipper_body_right.getQuaternion()).getHpr())
        # flip_wire.wrtReparentTo(self.pivot_right)

        self.flipper.wrtReparentTo(self.pivot_right)

        # ---- Left Flipper ----
        self.pivot_left = render.attachNewNode("pivot_left")
        self.flipper2 = table_egg.find("**/Cube.011")
        self.pivot_left.setPos(4.29, -1.06, .09) #was -1.0
        self.flipper_body_left = self.add_flipper_to_physics(self.flipper2, 2)

        # flip_wire2 = wireGeom().generate('box', extents=((.25, .720, .338)))
        # flip_wire2.setPos(self.flipper_body_left.getPosition())
        # flip_wire2.setHpr(Quat(self.flipper_body_left.getQuaternion()).getHpr())
        # flip_wire2.wrtReparentTo(self.pivot_left)
        self.flipper2.wrtReparentTo(self.pivot_left)

    def import_ramp(self, table_egg):
        ramp_bottom = table_egg.find("**/Cube.013")
        ramp_bottom_geom = self.add_innard_cube_to_physics(
            ramp_bottom, 2.0, .5, .01)
        ramp_bottom.reparentTo(render)

        ramp_wall_left = table_egg.find("**/Cube.014")
        ramp_wall_left_geom = self.add_innard_cube_to_physics(
            ramp_wall_left, 2.081, .01, .5)
        ramp_wall_left.reparentTo(render)

        ramp_wall_right = table_egg.find("**/Cube.015")
        ramp_wall_right_geom = self.add_innard_cube_to_physics(
            ramp_wall_right, 2.081, .01, .5)
        ramp_wall_right.reparentTo(render)

        pipe = table_egg.find("**/Cylinder.005")
        self.pipe_geom = self.add_innard_cylinder_to_physics(pipe, .3715, .5)
        pipe.reparentTo(render)

        # dont add to physics, purley cosmetic
        pipe_rim = table_egg.find("**/Cylinder.006")
        pipe_rim.reparentTo(render)

        # dont render, just want the OdeGeom
        ball_stopper = table_egg.find("**/Cube.028")
        self.ball_stopper_geom = self.add_innard_cube_to_physics(ball_stopper, .1, .5, .35)

        #importing side pipe where ball will shoot out
        pipe_left_wall = table_egg.find("**/Cylinder.009")
        pipe_left_wall.reparentTo(render)
        #side pipe rim, no physics
        pipe_rim_left_wall = table_egg.find("**/Cylinder.010")
        pipe_rim_left_wall.reparentTo(render)
        # invisible wall in front of pipe
        pipe_cover_left = table_egg.find("**/Cube.031")
        self.pipe_cover_left_geom = self.add_innard_cube_to_physics(
            pipe_cover_left, .5, .01, .5)

        #walls arround pipe
        pipe_wall_bottom_left = table_egg.find("**/Cube.029")
        pipe_wall_bottom_left_geom = self.add_innard_cube_to_physics(
            pipe_wall_bottom_left, .5, .01, .5)
        pipe_wall_bottom_left.reparentTo(render)

        pipe_wall_top_left = table_egg.find("**/Cube.030")
        pipe_wall_top_left_geom = self.add_innard_cube_to_physics(
            pipe_wall_top_left, .5, .01, .5)
        pipe_wall_top_left.reparentTo(render)



    def setup_physics_lb_bumper(self, node_path):
        #tl stands for trigger left
        self.tl_l_wall = self.add_wall_to_physics(0.5, 0.05, 0.5, 2.5, -1.95, 0.25)
        # boxNodepath = wireGeom().generate('box', extents=(0.5, 0.05, 0.5))
        # boxNodepath.setPos(2.5,-1.95, 0.25)
        # boxNodepath.reparentTo(render)

        self.tl_rb_wall = self.add_wall_to_physics(0.635 , 0.05, 0.5, 2.45, -1.70, .25)
        quat = Quat(0.0, 0.0, 0.0, 0.0)
        v = VBase3(55.0, 0.0, 0.0)
        quat.setHpr(v)
        self.tl_rb_wall.setQuaternion(quat)
        # boxNodepath1 = wireGeom().generate('box', extents=(0.635, 0.05, 0.5))
        # boxNodepath1.setPos(2.45, -1.70, .25)
        # boxNodepath1.setHpr(55, 0, 0)
        # boxNodepath1.reparentTo(render)


        self.tl_rt_wall = self.add_wall_to_physics(0.6, 0.05, 0.5, 2.79, -1.75, .25)
        quat2 = Quat(0.0, 0.0, 0.0, 0.0)
        v2 = VBase3(125, 0, 0)
        quat2.setHpr(v2)
        self.tl_rt_wall.setQuaternion(quat2)
        # boxNodepath2 = wireGeom().generate('box', extents=(0.6, 0.05, 0.5))
        # boxNodepath2.setPos(2.79, -1.75, .25)
        # boxNodepath2.setHpr(125, 0, 0)
        # boxNodepath2.reparentTo(render)

    def setup_physics_rb_bumper(self, node_path):
        #tr stands for triangle right
        self.tr_r_wall = self.add_wall_to_physics(0.75, 0.05, 0.5, 2.6, 1.45, 0.25)
        self.tr_lb_wall = self.add_wall_to_physics(0.5, 0.05, 0.5, 2.4, 1.2, 0.25)
        quat = Quat(0.0, 0.0, 0.0, 0.0)
        v = VBase3(-55.0, 0.0, 0.0)
        quat.setHpr(v)
        self.tr_lb_wall.setQuaternion(quat)
        self.tr_rt_wall = self.add_wall_to_physics(0.6, 0.05, 0.5, 2.75, 1.2, 0.25)
        quat2 = Quat(0.0, 0.0, 0.0, 0.0)
        v2 = VBase3(-125, 0, 0)
        quat2.setHpr(v2)
        self.tr_rt_wall.setQuaternion(quat2)

        # boxNodepath1 = wireGeom().generate('box', extents=(0.6, 0.05, 0.5))
        # boxNodepath1.setPos(2.4, 1.2, 0.25)
        # boxNodepath1.setHpr(-55, 0, 0)
        # boxNodepath1.reparentTo(render)

        # boxNodepath2 = wireGeom().generate('box', extents=(0.6, 0.05, 0.5))
        # boxNodepath2.setPos(2.75, 1.2, 0.25)
        # boxNodepath2.setHpr(-125, 0, 0)
        # boxNodepath2.reparentTo(render)

    def close_launcher(self):
        self.metroid_door.play()
        if self.not_first_time == False:
            self.door_geom = self.add_innard_cube_to_physics(self.door, 1.1, 0.01, 0.5)
            self.not_first_time = True
        else:
            self.door_geom.enable()
        self.door.reparentTo(render)

    def open_launcher(self):
        if self.not_first_time == True:
             self.door_geom.disable()
        self.door.detachNode()
        self.door = self.door_holder

    def import_ball(self, ball_egg):
        # print "\t import ball egg"
        sphere = ball_egg.find("**/Sphere")
        sphere.reparentTo(render)
        return sphere

    def setup_ball_physics(self, radius, mass):
        # print "\t \t setup ball physics"
        ball_mass = OdeMass()
        ball_mass.setSphere(25, 0.1)
        self.ball_body = OdeBody(self.world)
        self.ball_body.setMass(ball_mass)
        self.ball_body.setPosition(self.ball.getPos(render))
        self.ball_body.setQuaternion(self.ball.getQuat(render))
        ball_geom = OdeSphereGeom(self.space1, 0.1)
        self.space1.setSurfaceType(ball_geom, 0)
        ball_geom.setBody(self.ball_body)

    def launch_ball_task(self, task):
        # self.space1.autoCollide()  # Setup the contact joints
        # Step the simulation and set the new positions
        # self.world.quickStep(globalClock.getDt())
        self.ball.setPosQuat(
            render, self.ball_body.getPosition(), Quat(
                self.ball_body.getQuaternion()))
        # self.ball_body.setForce(1.4, 1.1, 0)
        self.ball_body.setForce(-self.launch_force, 0.0, 0)
        self.contactgroup.empty()  # Clear the contact joints
        return task.cont

    def release_plunger_task(self,task):
        # code for moving plunger back to starting point
        if self.plunger.getX() > 3.923:
            self.plunger.setX(self.plunger.getX() - .25)
            return task.cont
        else:
            self.plunger.setX(3.923)
            taskMgr.doMethodLater(
            0,
            self.launch_ball_task,
            'launch_ball')
            taskMgr.remove('build_launch_force')
            taskMgr.remove('release_plunger')
            return task.done

    def gravity_task(self, task):
        # these two lines set up the ball cam for testing
        # base.camera.setPos(self.ball_body.getPosition())
        # base.camera.lookAt(4.12, 0.6, .09)

        self.space1.autoCollide()  # Setup the contact joints
        # Step the simulation and set the new positions
        self.world.quickStep(globalClock.getDt())
        # self.world.quickStep(self.simTimeStep)

        if self.ball_not_sinking :
            self.ball.setPosQuat(
                render, self.ball_body.getPosition(), Quat(
                    self.ball_body.getQuaternion()))
        else:
            self.start_ball_sink_task()
        #the ball gets passed the launcher wall, close the launch opening

        pos = self.ball_body.getPosition()
        if pos[0] < -2.5 and pos[1] < 2:
            messenger.send("close_launcher")

        if self.button_enabled:
            if GPIO.input(21) == False:
                messenger.send("left_down")
            else :
                messenger.send("left_up")
            if GPIO.input(12) == False:
                messenger.send("right_down")
            else  :
                messenger.send("right_up")

        if (self.left_flipper_up == False) and (self.h_left > 0):
            self.move_left_flipper_down()
        elif self.left_flipper_up and (self.h_left < 70):
            self.move_left_flipper_up()
        else:
            self.velocity_left = 1
            self.force_applied_to_ball_left = 0.1;

        if (self.right_flipper_up == False) and (self.h_right < 0):
            self.move_right_flipper_down()
        elif self.right_flipper_up and (self.h_right > -70):
            self.move_right_flipper_up()
        else:
            self.velocity_right = 1
            self.force_applied_to_ball_right = 0.1;

        self.contactgroup.empty()  # Clear the contact joints
        return task.cont

    def stop_launch_ball_task(self, task):
        taskMgr.remove('launch_ball')
        self.launch_force = 0.0
        self.can_launch = True

    def build_launch_force_task(self, task):
        if self.launch_force < 3.0:
            self.launch_force += .025;
            self.plunger.setX(self.plunger.getX() + 0.025)
            return task.cont
        else:
            return task.done

    def apply_force_to_ball(self, flipper):
        if flipper == 0 and self.right_flipper_up:
            #the ball must be y less than 0.6 and x greater than 4 
            if self.ball_body.getPosition()[0] > 4 and self.ball_body.getPosition()[1] < 0.6:
                self.ball_body.setForce(-self.force_applied_to_ball_right,0,0)
                # print self.force_applied_to_ball_right

        if flipper == 1 and self.left_flipper_up:
            #the ball must be y greater than -1.0 and x greater than 4 
            if self.ball_body.getPosition()[0] > 4 and self.ball_body.getPosition()[1] > -1.0:
                self.ball_body.setForce(-self.force_applied_to_ball_left,0,0)
                # print self.force_applied_to_ball_left

    def start_ball_sink_task(self):
        if  self.ball.getZ()  >= .25:
            self.ball.setZ(self.ball.getZ() - .05)
            self.ball_body.setPosition(self.ball.getPos())
        else:
            # shoot the ball out in a random place
            self.pipe_cover_left_geom.disable()
            self.ball.setPos(-1.24, -2.89, .1)
            self.ball_body.setPosition(self.ball.getPos())
            self.ball_body.setForce(.05, 1.0, 0)
            self.ball_not_sinking = True
            taskMgr.doMethodLater(
                1,
                self.enable_pipe_cover,
                'enable_pipe_cover')

    def enable_pipe_cover(self, task):
        self.pipe_cover_left_geom.enable()


    def move_left_flipper_up(self):
        if self.velocity_left <= 2.5:
            self.velocity_left += self.accell_flippers
        else:
            self.velocity_left = 2.5

        if self.force_increase_rate < 13.0:
            self.force_applied_to_ball_left += self.force_increase_rate

        self.h_left += 8 * self.velocity_left
        self.pivot_left.setH(self.h_left)

        self.flipper_body_left.setQuaternion(
            self.quat_left)
        self.flipper_body_left.setPosition(self.flipper2.getPos(base.render))

    def move_left_flipper_down(self):
        if self.velocity_left <= 2.5:
            self.velocity_left += self.accell_flippers
        else:
            self.velocity_left = 2.5

        #if flippers are moving down then restart force applied to ball
        self.force_applied_to_ball_left = 0.1;

        self.h_left -= 8 * self.velocity_left
        self.pivot_left.setH(self.h_left)
        self.flipper_body_left.setQuaternion(
            self.quat_left)
        self.flipper_body_left.setPosition(self.flipper2.getPos(base.render))

    def move_right_flipper_up(self):
        if self.velocity_right <= 2.5:
            self.velocity_right += self.accell_flippers
        else:
            self.velocity_right = 2.5

        if self.force_increase_rate < 13.0:
            self.force_applied_to_ball_right += self.force_increase_rate

        self.h_right -= 8 * self.velocity_right
        self.pivot_right.setH(self.h_right)

        self.flipper_body_right.setQuaternion(
            self.quat_right)
        self.flipper_body_right.setPosition(self.flipper.getPos(base.render))

    def move_right_flipper_down(self):
        if self.velocity_right <= 2.5:
            self.velocity_right += self.accell_flippers
        else:
            self.velocity_right = 2.5

        #if flippers are moving down then restart force applied to ball
        self.force_applied_to_ball_right = 0.1;

        self.h_right += 8 * self.velocity_right
        self.pivot_right.setH(self.h_right)

        self.flipper_body_right.setQuaternion(self.quat_right)
        self.flipper_body_right.setPosition(self.flipper.getPos(base.render))
