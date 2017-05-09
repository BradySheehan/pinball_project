# from direct.showbase.DirectObject import DirectObject
# from direct.showbase.ShowBase import ShowBase
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

    def setup_camera(self):
        print "setup camera"
        base.camera.setPos(9, 0, 15)
        base.camera.lookAt(0, 0, 0)

    def setup_light(self):
        print "setup light"
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
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(.5, .5, 1, 1))
        # ambientNP = egg.attachNewNode(ambient)
        # egg.setLight(ambientNP)

    def setup_ode_world_params(self):
        print "setup ode world params"
        self.world = OdeWorld()
        # gravity needs to be adjusted (to simulate table being tilted)
        self.world.setGravity(0, 0, -9.81)
        self.world.initSurfaceTable(1)
        self.world.setSurfaceEntry(
            0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
        self.space1 = OdeSimpleSpace()
        self.space1.setAutoCollideWorld(self.world)
        self.contactgroup = OdeJointGroup()
        self.space1.setAutoCollideJointGroup(self.contactgroup)

    def load_models(self):
        print "load models"
        self.ball_egg = loader.loadModel("models/table_collide_no_culling.egg")
        self.ball = self.ball_egg.find("**/Sphere")
        self.ball.reparentTo(render)
        self.ball.setPos(0, 0, 0.12)
        self.ball_mass = OdeMass()
        self.ball_mass.setSphere(50, 0.1)
        self.ball_body = OdeBody(self.world)
        self.ball_body.setMass(self.ball_mass)
        self.ball_body.setPosition(self.ball.getPos(render))
        self.ball_body.setQuaternion(self.ball.getQuat(render))
        self.ball_geom = OdeSphereGeom(self.space1, 0.1)
        self.ball_geom.setBody(self.ball_body)

        self.table_egg = loader.loadModel(
            "models/visible_table_inner_wall.egg")
        self.import_table(self.table_egg)

    def add_plane_to_physics(self, params1, params2, params3, params4):
        # Returns a handle to the OdePlaneGeom object with the specified
        # parameters
        plane = OdePlaneGeom(self.space1, params1, params2, params3, params4)
        return plane

    def add_wall_to_physics(self, dimx, dimy, dimz, locx, locy, locz):
        # Returns a handle to the OdeBoxGeom object with the specified
        # parameters
        box = OdeBoxGeom(self.space1, dimx, dimy, dimz)
        box.setPosition(locx, locy, locz)
        return box

    def setup_table_physics(self):
        print "\t \t setup table physics"
        self.ground_plane = self.add_plane_to_physics(0, 0, 1, 0)
        self.wall_west = self.add_wall_to_physics(10, 0.1, 2, 0, -3, 1)
        self.wall_east = self.add_wall_to_physics(10, 0.1, 2, 0, 3, 1)
        self.wall_north = self.add_wall_to_physics(0.1, 6, 2, -5, 0, 1)
        self.wall_south = self.add_wall_to_physics(1, 5, 2, 5, 0, 1)
        self.bumper_wall = self.add_wall_to_physics(
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

    def simulationTask(self, task):
        self.space1.autoCollide()  # Setup the contact joints
        # Step the simulation and set the new positions
        self.world.quickStep(globalClock.getDt())
        self.ball.setPosQuat(
            render, self.ball_body.getPosition(), Quat(
                self.ball_body.getQuaternion()))
        self.ball_body.setForce(-1, -1, 0)
        self.contactgroup.empty()  # Clear the contact joints
        return task.cont

    def launch_ball(self):
        taskMgr.doMethodLater(
            1,
            self.simulationTask,
            'Physics Simulation')


class Game():

    def __init__(self):
        self.max_balls = 5
        self.balls_used = 0
        self.score = 0
        self.table = Table()

    def start(self):
        self.reset_score()
        self.table.launch_ball()
        base.disableMouse()
        base.accept("escape", sys.exit)  # Escape quits
        base.run()

    def reset_score(self):
        self.balls_used = 0
        self.score = 0

if __name__ == '__main__':
    game = Game()
    game.start()
