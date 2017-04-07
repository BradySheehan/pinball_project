from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom, OdeCylinderGeom
from panda3d.core import BitMask32, Vec4, Quat, VBase3
from panda3d.core import Light, AmbientLight, DirectionalLight
import sys

sys.path.append('../scripts/')
from visualizeGeoms_copy import wireGeom


class Table():
    # class that sets up the graphics and physics

    def __init__(self):
        self.setup_ode_world_params()
        self.setup_camera()
        self.setup_light()
        self.load_models()

        # rotation angle for flippers
        self.h_left = 0
        self.h_right = 0
        # accelleration for flippers
        self.accell_flippers = .1
        # velocity for flippers
        self.velocity_left = 1
        self.velocity_right = 1
        # flags used for flipper movement
        self.left_flipper_up = False
        self.right_flipper_up = False

    def move_left_flipper(self):
        self.left_flipper_up = True

    def stop_left_flipper(self):
        self.left_flipper_up = False

    def move_right_flipper(self):
        self.right_flipper_up = True

    def stop_right_flipper(self):
        self.right_flipper_up = False

    def setup_camera(self):
        print "setup camera"
        base.camera.setPos(10, 0, 15)
        base.camera.lookAt(0, 0, 0)

    def setup_light(self):
        print "setup light"
        # set light in panda3d from blender
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor(Vec4(0.0, 0.0, 0.0, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)
        directionalLight = DirectionalLight('directionalLight')
        directionalLight.setColor(Vec4(1.0, 1.0, 1.0, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(180, -20, 0)
        render.setLight(directionalLightNP)
        directionalLight = DirectionalLight('directionalLight')
        directionalLight.setColor(Vec4(0.0, 1.0, 1.0, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(0, -20, 0)
        render.setLight(directionalLightNP)

    def setup_ode_world_params(self):
        print "setup ode world params"
        self.world = OdeWorld()
        # gravity needs to be adjusted (to simulate table being tilted)
        self.world.setGravity(1, 0, -10)
        self.world.initSurfaceTable(1)  # we need to figure out what this does
        self.world.setSurfaceEntry(
            0,
            0,
            150,
            0.0,
            9.1,
            0.9,
            0.0000,
            1.0,
            0.002)  # and what this does
        self.space1 = OdeSimpleSpace()
        self.space1.setAutoCollideWorld(self.world)
        self.contactgroup = OdeJointGroup()
        self.space1.setAutoCollideJointGroup(self.contactgroup)

    def load_models(self):
        print "load models"
        self.ball_egg = loader.loadModel("models/table_collide_no_culling.egg")
        self.ball = self.import_ball(self.ball_egg)
        self.setup_ball_physics(0.1, 0.1)
        self.table_egg = loader.loadModel(
            "models/table2.egg")

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

    def add_flipper_to_physics(self, flipperNP):

        flipper_mass = OdeMass()
        flipper_mass.setBox(100, .398, .563, .300)
        flipper_body = OdeBody(self.world)
        flipper_body.setMass(flipper_mass)
        flipper_body.setPosition(flipperNP.getPos())
        flipper_body.setQuaternion(flipperNP.getQuat())
        flipper = OdeBoxGeom(self.space1, .398, .563, .300)
        flipper.setBody(flipper_body)

        return flipper_body

    def setup_table_physics(self):
        print "\t \t setup table physics"
        self.ground_plane = self.add_plane_to_physics(0, 0, 1, 0)
        self.wall_west = self.add_wall_to_physics(10, 0.1, 2.5, 0, -3, 1)
        self.wall_east = self.add_wall_to_physics(10, 0.1, 2.5, 0, 3, 1)
        self.wall_north = self.add_wall_to_physics(0.1, 6, 2.5, -5, 0, 1)
        self.wall_south = self.add_wall_to_physics(0.5, 6, 2.5, 5, 0, 1)
        self.launch_wall = self.add_wall_to_physics(
            3.5, 0.2, 0.5, 3.25, 2.6, 0.25)

    def import_table(self, table_egg):
        print "\t import table egg"
        plane1 = table_egg.find("**/Plane.001")
        plane1.reparentTo(render)
        plane1.flattenLight()
        plane2 = table_egg.find("**/Plane.002")
        plane2.reparentTo(render)
        plane2.flattenLight()
        plane3 = table_egg.find("**/Plane.003")
        plane3.reparentTo(render)
        plane3.flattenLight()
        plane4 = table_egg.find("**/Plane.004")
        plane4.reparentTo(render)
        plane4.flattenLight()
        plane5 = table_egg.find("**/Plane.005")
        plane5.reparentTo(render)
        plane5.flattenLight()

        inner_wall = table_egg.find("**/Cube")
        inner_wall.reparentTo(render)
        inner_wall.flattenLight()

    def import_innards(self, table_egg):
        flipper_r_wall = table_egg.find("**/Cube.002")
        flipper_r_wall_geom = self.add_innard_cube_to_physics(
            flipper_r_wall, 1.5, 0.05, 0.5)
        flipper_r_wall.reparentTo(render)
        flipper_r_wall.flattenLight()

        flipper_l_wall = table_egg.find("**/Cube.001")
        flipper_l_wall_geom = self.add_innard_cube_to_physics(
            flipper_l_wall, 1.5, 0.05, 0.5)
        flipper_l_wall.reparentTo(render)
        flipper_l_wall.flattenLight()

        l_bumper_wall = table_egg.find("**/Cube.003")
        l_bumper_wall_geom = self.add_innard_cube_to_physics(
            l_bumper_wall, 0.75, 0.2, 0.5)
        l_bumper_wall.reparentTo(render)
        l_bumper_wall.flattenLight()

        r_bumper_wall = table_egg.find("**/Cube.004")
        r_bumper_wall_geom = self.add_innard_cube_to_physics(
            r_bumper_wall, 0.75, 0.2, 0.5)
        r_bumper_wall.reparentTo(render)
        r_bumper_wall.flattenLight()

        rb_bumper = table_egg.find("**/Cylinder")

        self.setup_physics_rb_bumper(rb_bumper)

        boxNodepath2 = wireGeom().generate('box', extents=(0.75, 0.05, 0.5))
        boxNodepath2.setPos(2.6, 1.45, 0.25)
        boxNodepath2.setQuat(rb_bumper.getQuat())
        boxNodepath2.reparentTo(render)

        rb_bumper.reparentTo(render)
        rb_bumper.flattenLight()

        lb_bumper = table_egg.find("**/Cylinder.001")
        self.setup_physics_lb_bumper(lb_bumper)

        boxNodepath3 = wireGeom().generate('box', extents=(0.75, 0.05, 0.5))
        boxNodepath3.setPos(2.6, -1.95, 0.25)
        boxNodepath3.setQuat(lb_bumper.getQuat())
        boxNodepath3.reparentTo(render)

        lb_bumper.reparentTo(render)
        lb_bumper.flattenLight()

        angled_launch_wall = table_egg.find("**/Cube.005")
        boxNodepath = wireGeom().generate('box', extents=(1.0, 0.05, 0.5))
        boxNodepath.setPos(angled_launch_wall.getPos())
        boxNodepath.setQuat(angled_launch_wall.getQuat())
        boxNodepath.reparentTo(render)

        angled_launch_wall_geom = self.add_innard_cube_to_physics(
            angled_launch_wall, 1.0, 0.1, 0.5)
        angled_launch_wall.reparentTo(render)
        angled_launch_wall.flattenLight()

        # input pink bumpers Cylinder.002 and Cylinder.003
        round_bumper_left = table_egg.find("**/Cylinder.002")
        round_bumper_left_geom = self.add_innard_cylinder_to_physics(
            round_bumper_left, float(0.7432/2), 0.5)
        round_bumper_left.reparentTo(render)
        round_bumper_left.flattenLight()
        round_bumper_right = table_egg.find("**/Cylinder.003")
        round_bumper_left_geom = self.add_innard_cylinder_to_physics(
            round_bumper_right, float(0.7432/2), 0.5)
        round_bumper_right.reparentTo(render)
        round_bumper_right.flattenLight()

        #tall green bumper
        angled_wall_bumper = table_egg.find("**/Cylinder.004")
        self.angled_wall_bumper_geom = self.add_innard_cylinder_to_physics(angled_wall_bumper, float(0.7432/2), 1)
        angled_wall_bumper.reparentTo(render)
        angled_wall_bumper.flattenLight()

        angled_launch_wall2 = table_egg.find("**/Cube.006")
        boxNodepath2 = wireGeom().generate('box', extents=(1.0, 0.01, 0.5))
        boxNodepath2.setPos(angled_launch_wall2.getPos())
        boxNodepath2.setQuat(angled_launch_wall2.getQuat())
        boxNodepath2.reparentTo(render)

        angled_launch_wall_geom2 = self.add_innard_cube_to_physics(
            angled_launch_wall2, 1.0, 0.1, 0.5)
        angled_launch_wall2.reparentTo(render)
        angled_launch_wall2.flattenLight()

        angled_launch_wall3 = table_egg.find("**/Cube.007")
        boxNodepath3 = wireGeom().generate('box', extents=(1.0, 0.01, 0.5))
        boxNodepath3.setPos(angled_launch_wall3.getPos())
        boxNodepath3.setQuat(angled_launch_wall3.getQuat())
        boxNodepath3.reparentTo(render)

        angled_launch_wall_geom3 = self.add_innard_cube_to_physics(
            angled_launch_wall3, 1.0, 0.1, 0.5)
        angled_launch_wall3.reparentTo(render)
        angled_launch_wall3.flattenLight()

        angled_launch_wall4 = table_egg.find("**/Cube.008")
        boxNodepath4 = wireGeom().generate('box', extents=(1.0, 0.01, 0.5))
        boxNodepath4.setPos(angled_launch_wall4.getPos())
        boxNodepath4.setQuat(angled_launch_wall4.getQuat())
        boxNodepath4.reparentTo(render)

        angled_launch_wall_geom4 = self.add_innard_cube_to_physics(
            angled_launch_wall4, 1.0, 0.1, 0.5)
        angled_launch_wall4.reparentTo(render)
        angled_launch_wall4.flattenLight()

        angled_launch_wall5 = table_egg.find("**/Cube.009")
        boxNodepath5 = wireGeom().generate('box', extents=(1.0, 0.01, 0.5))
        boxNodepath5.setPos(angled_launch_wall5.getPos())
        boxNodepath5.setQuat(angled_launch_wall5.getQuat())
        boxNodepath5.reparentTo(render)

        angled_launch_wall_geom5 = self.add_innard_cube_to_physics(
            angled_launch_wall5, 1.0, 0.1, 0.5)
        angled_launch_wall5.reparentTo(render)
        angled_launch_wall5.flattenLight()

        # cubes 17 - 21 are the upper half of the angled wall, load those now
        upper_wall1 = table_egg.find("**/Cube.017")
        upper_wall1_geom = self.add_innard_cube_to_physics(
            upper_wall1, 1.0, 0.1, 0.5)
        upper_wall1.reparentTo(render)
        upper_wall1.flattenLight()

        upper_wall2 = table_egg.find("**/Cube.018")
        upper_wall2_geom = self.add_innard_cube_to_physics(
            upper_wall2, 1.0, 0.1, 0.5)
        upper_wall2.reparentTo(render)
        upper_wall2.flattenLight()

        upper_wall3 = table_egg.find("**/Cube.019")
        upper_wall3_geom = self.add_innard_cube_to_physics(
            upper_wall3, 1.0, 0.1, 0.5)
        upper_wall3.reparentTo(render)
        upper_wall3.flattenLight()

        upper_wall4 = table_egg.find("**/Cube.020")
        upper_wall4_geom = self.add_innard_cube_to_physics(
            upper_wall4, 1.0, 0.1, 0.5)
        upper_wall4.reparentTo(render)
        upper_wall4.flattenLight()


        upper_wall5 = table_egg.find("**/Cube.021")
        upper_wall5_geom = self.add_innard_cube_to_physics(
            upper_wall5, 1.0, 0.1, 0.5)
        upper_wall5.reparentTo(render)
        upper_wall5.flattenLight()

    def import_flippers(self, table_egg):
        # extract flipper
        self.pivot_right = render.attachNewNode("pivot_right")  # pivot point
        self.flipper = table_egg.find("**/Cube.010")
        # self.flipper.setPos(4.3,.2, .09)
        # self.flipper.setPos(0.18,-0.4, 0)
        # self.flipper.setH(110)
        self.pivot_right.setPos(4.12, 0.6, .09)
        self.flipper_body_right = self.add_flipper_to_physics(self.flipper)

        flip_wire = wireGeom().generate('box', extents=((.398, .563, .300)))
        flip_wire.setPos(self.flipper.getPos())
        flip_wire.setHpr(self.flipper.getHpr())
        flip_wire.wrtReparentTo(self.pivot_right)

        self.flipper.wrtReparentTo(self.pivot_right)

        self.pivot_left = render.attachNewNode("pivot_left")
        self.flipper2 = table_egg.find("**/Cube.011")
        # self.flipper2.setPos(4.3,-.6, .09)
        # self.flipper2.setPos(0.18,0.4, 0)
        # self.flipper2.setH(-110)
        self.pivot_left.setPos(4.12, -1.0, .09)
        self.flipper_body_left = self.add_flipper_to_physics(self.flipper2)

        flip_wire2 = wireGeom().generate('box', extents=((.398, .563, .300)))
        flip_wire2.setPos(self.flipper_body_left.getPosition())
        flip_wire2.setHpr(
            Quat(self.flipper_body_left.getQuaternion()).getHpr())
        flip_wire2.wrtReparentTo(self.pivot_left)
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
        pipe_geom = self.add_innard_cylinder_to_physics(pipe, .3715, .5)
        pipe.reparentTo(render)

        # dont add to physics, purley cosmetic
        pipe_rim = table_egg.find("**/Cylinder.006")
        pipe_rim.reparentTo(render)

    def setup_physics_lb_bumper(self, node_path):
        l_wall = self.add_wall_to_physics(0.5, 0.05, 0.5, 2.6, -1.95, 0.25)
        rb_wall = self.add_wall_to_physics(0.6, 0.05, 0.5, 2.375, -1.8, .25)
        quat = Quat(0.0, 0.0, 0.0, 0.0)
        v = VBase3(55.0, 0.0, 0.0)
        quat.setHpr(v)
        rb_wall.setQuaternion(quat)
        rt_wall = self.add_wall_to_physics(0.6, 0.05, 0.5, 2.79, -1.75, .25)
        quat2 = Quat(0.0, 0.0, 0.0, 0.0)
        v2 = VBase3(125, 0, 0)
        quat2.setHpr(v2)
        rt_wall.setQuaternion(quat2)

        boxNodepath1 = wireGeom().generate('box', extents=(0.5, 0.05, 0.5))
        boxNodepath1.setPos(2.375, -1.8, .25)
        boxNodepath1.setHpr(55, 0, 0)
        boxNodepath1.reparentTo(render)

        boxNodepath2 = wireGeom().generate('box', extents=(0.6, 0.05, 0.5))
        boxNodepath2.setPos(2.79, -1.75, .25)
        boxNodepath2.setHpr(125, 0, 0)
        boxNodepath2.reparentTo(render)

    def setup_physics_rb_bumper(self, node_path):
        r_wall = self.add_wall_to_physics(0.75, 0.05, 0.5, 2.6, 1.45, 0.25)
        lb_wall = self.add_wall_to_physics(0.5, 0.05, 0.5, 2.4, 1.2, 0.25)
        quat = Quat(0.0, 0.0, 0.0, 0.0)
        v = VBase3(-55.0, 0.0, 0.0)
        quat.setHpr(v)
        lb_wall.setQuaternion(quat)
        rt_wall = self.add_wall_to_physics(0.6, 0.05, 0.5, 2.75, 1.2, 0.25)
        quat2 = Quat(0.0, 0.0, 0.0, 0.0)
        v2 = VBase3(-125, 0, 0)
        quat2.setHpr(v2)
        rt_wall.setQuaternion(quat2)

        boxNodepath1 = wireGeom().generate('box', extents=(0.6, 0.05, 0.5))
        boxNodepath1.setPos(2.4, 1.2, 0.25)
        boxNodepath1.setHpr(-55, 0, 0)
        boxNodepath1.reparentTo(render)

        boxNodepath2 = wireGeom().generate('box', extents=(0.6, 0.05, 0.5))
        boxNodepath2.setPos(2.75, 1.2, 0.25)
        boxNodepath2.setHpr(-125, 0, 0)
        boxNodepath2.reparentTo(render)

    def import_ball(self, ball_egg):
        print "\t import ball egg"
        sphere = ball_egg.find("**/Sphere")
        sphere.reparentTo(render)
        return sphere

    def setup_ball_physics(self, radius, mass):
        print "\t \t setup ball physics"
        ball_mass = OdeMass()
        ball_mass.setSphere(25, 0.1)
        self.ball_body = OdeBody(self.world)
        self.ball_body.setMass(ball_mass)
        self.ball_body.setPosition(self.ball.getPos(render))
        self.ball_body.setQuaternion(self.ball.getQuat(render))
        ball_geom = OdeSphereGeom(self.space1, 0.1)
        ball_geom.setBody(self.ball_body)

    def launch_ball_task(self, task):
        self.space1.autoCollide()  # Setup the contact joints
        # Step the simulation and set the new positions
        self.world.quickStep(globalClock.getDt())
        self.ball.setPosQuat(
            render, self.ball_body.getPosition(), Quat(
                self.ball_body.getQuaternion()))
        # self.ball_body.setForce(1.4, 1.1, 0)
        self.ball_body.setForce(-3.0, -0.0, 0)
        self.contactgroup.empty()  # Clear the contact joints
        return task.cont

    def gravity_task(self, task):
        self.space1.autoCollide()  # Setup the contact joints
        # Step the simulation and set the new positions
        self.world.quickStep(globalClock.getDt())
        self.ball.setPosQuat(
            render, self.ball_body.getPosition(), Quat(
                self.ball_body.getQuaternion()))
        if (self.left_flipper_up == False) and (self.h_left > 0):
            self.move_left_flipper_down()
        elif self.left_flipper_up and (self.h_left < 70):
            self.move_left_flipper_up()
        else:
            self.velocity_left = 1

        if (self.right_flipper_up == False) and (self.h_right < 0):
            self.move_right_flipper_down()
        elif self.right_flipper_up and (self.h_right > -70):
            self.move_right_flipper_up()
        else:
            self.velocity_right = 1
        self.contactgroup.empty()  # Clear the contact joints
        return task.cont

    def stop_launch_ball_task(self, task):
        taskMgr.remove('launch_ball')

    def move_left_flipper_up(self):
        if self.velocity_left <= 2.5:
            self.velocity_left += self.accell_flippers
        else:
            self.velocity_left = 2.5

        self.h_left += 8 * self.velocity_left
        self.pivot_left.setH(self.h_left)

        self.flipper_body_left.setQuaternion(
            self.flipper2.getQuat(base.render))
        self.flipper_body_left.setPosition(self.flipper2.getPos(base.render))

    def move_left_flipper_down(self):
        if self.velocity_left <= 2.5:
            self.velocity_left += self.accell_flippers
        else:
            self.velocity_left = 2.5

        self.h_left -= 8 * self.velocity_left
        self.pivot_left.setH(self.h_left)
        self.flipper_body_left.setQuaternion(
            self.flipper2.getQuat(base.render))
        self.flipper_body_left.setPosition(self.flipper2.getPos(base.render))

    def move_right_flipper_up(self):
        if self.velocity_right <= 2.5:
            self.velocity_right += self.accell_flippers
        else:
            self.velocity_right = 2.5

        self.h_right -= 8 * self.velocity_right
        self.pivot_right.setH(self.h_right)

        self.flipper_body_right.setQuaternion(
            self.flipper.getQuat(base.render))
        self.flipper_body_right.setPosition(self.flipper.getPos(base.render))

    def move_right_flipper_down(self):
        if self.velocity_right <= 2.5:
            self.velocity_right += self.accell_flippers
        else:
            self.velocity_right = 2.5

        self.h_right += 8 * self.velocity_right
        self.pivot_right.setH(self.h_right)
        self.flipper_body_right.setQuaternion(self.flipper.getQuat(base.render))
        self.flipper_body_right.setPosition(self.flipper.getPos(base.render))