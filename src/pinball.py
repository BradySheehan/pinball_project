from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom
from panda3d.core import BitMask32, Vec4, Quat
from panda3d.core import Light, AmbientLight, DirectionalLight
import sys


class Table():
    # class that sets up the graphics and physics

    def __init__(self):
        self.setup_ode_world_params()
        self.setup_camera()
        self.setup_light()
        self.load_models()

        self.h_left = 0  # rotation for left flipper
        self.h_right = 0

        base.accept('a', self.move_left_flipper)
        base.accept('a-up', self.stop_left_flipper)

        base.accept('d', self.move_right_flipper)
        base.accept('d-up', self.stop_right_flipper)

    def move_left_flipper(self):
        taskMgr.doMethodLater(
            0,
            self.move_left_flipper_up,
            'move_left_flipper_up')

    def stop_left_flipper(self):
        taskMgr.remove('move_left_flipper_up')
        taskMgr.doMethodLater(
            0,
            self.move_left_flipper_down,
            'move_left_flipper_down')

    def move_right_flipper(self):
        taskMgr.doMethodLater(
            0,
            self.move_right_flipper_up,
            'move_right_flipper_up')

    def stop_right_flipper(self):
        taskMgr.remove('move_right_flipper_up')
        taskMgr.doMethodLater(
            0,
            self.move_right_flipper_down,
            'move_right_flipper_down')

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
        self.world.setGravity(0.25, 0, -4.5)
        self.world.initSurfaceTable(1)
        self.world.setSurfaceEntry(
            0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 1.0, 0.002)
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
            "models/visible_table_first_bumpers_attempt_color_launch_wall.egg")

        # extract bumper
        self.egg_flipper = loader.loadModel("models/bumper3.egg")
        self.egg_flipper2 = loader.loadModel("models/bumper3.egg")
        self.pivot_left = render.attachNewNode("pivot_left")
        self.pivot_right = render.attachNewNode("pivot_right")

        self.flipper = self.egg_flipper.find("**/Cube")
        self.flipper2 = self.egg_flipper2.find("**/Cube")

        self.flipper.setPos(0.18, -0.4, 0)
        self.flipper.setH(110)

        # I want this at 4.3, -.6, .25 about
        self.flipper2.setPos(0.18, 0.4, 0)
        self.flipper2.setH(-110)

        self.pivot_left.setPos(4.12, -1.0, .25)
        self.pivot_right.setPos(4.12, 0.6, .25)
        # pivot_left.setH(-110)

        self.flipper.reparentTo(self.pivot_right)
        self.flipper2.reparentTo(self.pivot_left)

        self.import_table(self.table_egg)
        self.setup_table_physics()
        self.import_innards(self.table_egg)

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
        print innardNP
        innard = OdeBoxGeom(self.space1, dimx, dimy, dimz)
        innard.setPosition(innardNP.getPos())
        innard.setQuaternion(innardNP.getQuat())
        return innard

    def setup_table_physics(self):
        print "\t \t setup table physics"
        self.ground_plane = self.add_plane_to_physics(0, 0, 1, 0)
        self.wall_west = self.add_wall_to_physics(10, 0.1, 2, 0, -3, 1)
        self.wall_east = self.add_wall_to_physics(10, 0.1, 2, 0, 3, 1)
        self.wall_north = self.add_wall_to_physics(0.1, 6, 2, -5, 0, 1)
        self.wall_south = self.add_wall_to_physics(0.5, 6, 2, 5, 0, 1)
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
        # print 'flipper_r_wall', flipper_r_wall.getPos(), ' ',
        # flipper_r_wall.getQuat()
        invisible_stopper_for_ball = self.add_wall_to_physics(0.1, 0.1, 1, 4.75, 2.80, 0.5)

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
        rb_bumper.reparentTo(render)
        rb_bumper.flattenLight()

        lb_bumper = table_egg.find("**/Cylinder.001")
        lb_bumper.reparentTo(render)
        lb_bumper.flattenLight()

        angled_launch_wall = table_egg.find("**/Cube.005")
        angled_launch_wall_geom = self.add_innard_cube_to_physics(
            angled_launch_wall, 1, 1, 1)
        angled_launch_wall.reparentTo(render)
        angled_launch_wall.flattenLight()

    def import_ball(self, ball_egg):
        print "\t import ball egg"
        sphere = ball_egg.find("**/Sphere")
        sphere.reparentTo(render)
        return sphere

    def setup_ball_physics(self, radius, mass):
        print "\t \t setup ball physics"
        ball_mass = OdeMass()
        ball_mass.setSphere(50, 0.1)
        self.ball_body = OdeBody(self.world)
        self.ball_body.setMass(ball_mass)
        self.ball_body.setPosition(self.ball.getPos(render))
        self.ball_body.setQuaternion(self.ball.getQuat(render))
        ball_geom = OdeSphereGeom(self.space1, 0.1)
        ball_geom.setBody(self.ball_body)

    def place_ball(self):
        self.ball.setPos(4.4, 2.85, 0.1)
        # self.ball.setPos(-4, -2.85, 0.1)
        # self.ball.setPos(0,0,0.1)
        # self.ball.setPos(0,0,2.12)
        self.ball_body.setPosition(self.ball.getPos(render))
        self.ball_body.setQuaternion(self.ball.getQuat(render))

    def launch_ball_task(self, task):
        self.space1.autoCollide()  # Setup the contact joints
        # Step the simulation and set the new positions
        self.world.quickStep(globalClock.getDt())
        self.ball.setPosQuat(
            render, self.ball_body.getPosition(), Quat(
                self.ball_body.getQuaternion()))
        # self.ball_body.setForce(1.4, 1.1, 0)
        self.ball_body.setForce(-2.5, 0, 0)
        self.contactgroup.empty()  # Clear the contact joints
        return task.cont

    def gravity_task(self, task):
        self.space1.autoCollide()  # Setup the contact joints
        # Step the simulation and set the new positions
        self.world.quickStep(globalClock.getDt())
        self.ball.setPosQuat(
            render, self.ball_body.getPosition(), Quat(
                self.ball_body.getQuaternion()))
        self.contactgroup.empty()  # Clear the contact joints
        return task.cont

    def stop_launch_ball_task(self, task):
        taskMgr.remove('launch_ball')

    def start_trigger_miss_task(self):
        self.space1.setCollisionEvent("trigger_miss")
        base.accept("trigger_miss", self.trigger_miss_event)

    def move_left_flipper_up(self, task):
        self.h_left = self.h_left + 5
        self.pivot_left.setPos(4.12, -1.0, .25)
        self.pivot_left.setH(self.h_left)
        if (self.h_left < 90):
            return task.cont

    def move_left_flipper_down(self, task):
        self.h_left = self.h_left - 5
        self.pivot_left.setPos(4.12, -1.0, .25)
        self.pivot_left.setH(self.h_left)
        if (self.h_left > 0):
            return task.cont

    def move_right_flipper_up(self, task):
        self.h_right = self.h_right - 5
        self.pivot_right.setPos(4.12, 0.6, .25)
        self.pivot_right.setH(self.h_right)
        if (self.h_right > -90):
            return task.cont

    def move_right_flipper_down(self, task):
        self.h_right = self.h_right + 5
        self.pivot_right.setPos(4.12, 0.6, .25)
        self.pivot_right.setH(self.h_right)
        if (self.h_right < 0):
            return task.cont

# Setup collision event
    def trigger_miss_event(self, entry):
        # print 'inside trigger miss event'
        geom1 = entry.getGeom1()
        geom2 = entry.getGeom2()
        body1 = entry.getBody1()
        body2 = entry.getBody2()
        if ( (geom1 and geom1 == self.wall_south) and ( (body1 and body1 == self.ball_body) or (body2 and body2 == self.ball_body) ) ) or ( (geom2 and geom2 == self.wall_south) and ( (body1 and body1 == self.ball_body) or (body2 and body2 == self.ball_body) ) ):
        # if (geom2 and geom2 == self.wall_south):
            #now the Game needs to be made aware of the ball being "lost" and
            #the ball needs to be placed back at the start position
            print 'collision has happened'
            self.place_ball()

class Game():

    def __init__(self):
        self.max_balls = 5
        self.balls_used = 0
        self.score = 0
        self.table = Table()

    def start(self):
        self.reset_score()
        self.table.place_ball()
        self.table.start_trigger_miss_task()
        self.start_gravity_task()
        # self.launch_ball()
        base.disableMouse()
        base.accept("escape", sys.exit)  # Escape quits
        # base.accept("ode-collision", onCollision)
        base.accept('space', self.launch_ball)
        base.run()

    def reset_score(self):
        self.balls_used = 0
        self.score = 0

    def launch_ball(self):
        print "called"
        taskMgr.doMethodLater(
            0,
            self.table.launch_ball_task,
            'launch_ball')
        taskMgr.doMethodLater(
            1,
            self.table.stop_launch_ball_task,
            'stop_launch_ball')

    def start_gravity_task(self):
        taskMgr.add(self.table.gravity_task, 'gravity_task')

if __name__ == '__main__':
    game = Game()
    game.start()