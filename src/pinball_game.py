# from direct.showbase.DirectObject import DirectObject
# from direct.showbase.ShowBase import ShowBase
from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom, OdeTriMeshGeom, OdeTriMeshData
from panda3d.core import BitMask32, Vec4, Quat
from panda3d.core import Light, AmbientLight, DirectionalLight, LMatrix3f
import sys

# we should create a table class
# with two functions setup_graphics and setup_physics with the affiliated suppport functions

class Table():
	#class that sets up the graphics and physics

	def __init__(self):
		# ShowBase.__init__(self)
		# self.accept("escape", sys.exit)  # Escape quits
		self.setup_ode_world_params()
		self.setup_camera()
		self.setup_light()
		self.load_models()

	def place_ball(self):
		self.ball.set_pos(4.3,2.85, 0.12)
		self.ball_body.setPosition(self.ball.getPos(render))

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
		self.world.setGravity(0, 0, -9.81) #gravity needs to be adjusted (to simulate table being tilted)
		self.world.initSurfaceTable(1)
		self.world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
		self.space = OdeSimpleSpace()
		self.space.setAutoCollideWorld(self.world)
		self.contactgroup = OdeJointGroup()
		self.space.setAutoCollideJointGroup(self.contactgroup)

	def load_models(self):
		print "load models"
		self.ball_egg = loader.loadModel("models/table_collide_no_culling.egg")
		self.ball_temp = self.ball_egg.find("**/Sphere")
		self.ball = self.ball_temp.copyTo(render)
		self.ball.setPos(4.3,2.85, 0.12)
		# self.ball = self.import_ball(self.ball_egg)
		self.setup_ball_physics(50, 0.1)

		# #extract bumper
		# egg_trigger = loader.loadModel("models/bumper2.egg")
		# egg_trigger2= loader.loadModel("models/bumper2.egg")
		# trigger = egg_trigger.find("**/Cube")
		# trigger2 = egg_trigger2.find("**/Cube")
		# trigger.setPos(3,.75, 5)
		# trigger2.setPos(3,-.75, 5)
		# trigger.setHpr(90,0,0)
		# trigger2.setHpr(-90,0,0)
		# # trigger.reparentTo(render)
		# # trigger2.reparentTo(render)

		self.table_egg = loader.loadModel("models/visible_table_inner_wall.egg")
		self.import_table(self.table_egg)
		self.setup_table_physics()

	def import_ball(self, ball_egg):
		sphere = ball_egg.find("**/Sphere")
		return sphere.copyTo(render)	

	def add_plane_to_physics(self, params1, params2, params3, params4):
		#Returns a handle to the OdePlaneGeom object with the specified parameters
	    plane = OdePlaneGeom(self.space, params1, params2, params3, params4)
	    plane.setCollideBits(BitMask32(0x00000002))
	    plane.setCategoryBits(BitMask32(0x00000001))
	    plane.setCollideBits(BitMask32(0x00000001))
	    plane.setCategoryBits(BitMask32(0x00000002))
	    return plane

	def add_wall_to_physics(self, dimx, dimy, dimz, locx, locy, locz):
	    #Returns a handle to the OdeBoxGeom object with the specified parameters
	    box = OdeBoxGeom(self.space, dimx, dimy, dimz)
	    box.setPosition(locx, locy, locz)
	    box.setCollideBits(BitMask32(0x00000002))
	    box.setCategoryBits(BitMask32(0x00000001))
	    box.setCollideBits(BitMask32(0x00000001))
	    box.setCategoryBits(BitMask32(0x00000002))
	    return box

	def setup_table_physics(self):
		print "setup table physics"
		self.ground_plane = self.add_plane_to_physics(0, 0, 1, 0)
		self.wall_west = self.add_wall_to_physics( 10, 0.1, 2, 0, -3, 1)
		self.wall_east = self.add_wall_to_physics(10, 0.1, 2, 0, 3, 1)
		self.wall_north = self.add_wall_to_physics(0.1, 6, 2, -5, 0, 1)
		self.wall_south = self.add_wall_to_physics(1, 5, 2, 5, 0, 1)
		self.bumper_wall = self.add_wall_to_physics(3.5, 0.2, 0.5, 3.25, 2.6, 0.25)

	def import_table(self, table_egg):
		plane1 = table_egg.find("**/Plane.001")
		plane1.reparentTo(render)
		plane2 = table_egg.find("**/Plane.002")
		plane2.reparentTo(render)
		plane3 = table_egg.find("**/Plane.003")
		plane3.reparentTo(render)
		plane4 = table_egg.find("**/Plane.004")
		plane4.reparentTo(render)
		plane5 = table_egg.find("**/Plane.005")
		plane5.reparentTo(render)

		inner_wall = table_egg.find("**/Cube")
		inner_wall.reparentTo(render)



	def setup_ball_physics(self, radius, mass):
		self.ball_mass = OdeMass()
		self.ball_mass.setSphere(mass, radius)
		self.ball_body = OdeBody(self.world)
		self.ball_body.setMass(self.ball_mass)
		self.ball_body.setPosition(self.ball.getPos(render))
		self.ball_body.setQuaternion(self.ball.getQuat(render))
		self.ball_geom = OdeSphereGeom(self.space, radius)
		self.ball_geom.setCollideBits(BitMask32(0x00000002))
		self.ball_geom.setCategoryBits(BitMask32(0x00000001))
		self.ball_geom.setBody(self.ball_body)
		

	def simulationTask(self,task):
	    self.space.autoCollide()  # Setup the contact joints
	    # Step the simulation and set the new positions
	    self.world.quickStep(globalClock.getDt())
	    self.ball.setPosQuat(render, self.ball_body.getPosition(), Quat(self.ball_body.getQuaternion()))
	    # sphere.setPos(ball_body.getPosition())
	    # ball_body.set_force(0,176.689,-1000)
	    # ball_body.set_force(0,0, -100)
	    #self.ball_body.setForce(-1, 0, 0)
	    self.ball_body.setForce(-1, -1, 0)
	    # ball_body.setForce(1, 1, 0)
	    self.contactgroup.empty()  # Clear the contact joints
	    return task.cont

# class Game(ShowBase):
class Game():

	def __init__(self):
		# ShowBase.__init__(self)
		self.max_balls = 5
		self.balls_used = 0
		self.score = 0
		base.accept("escape", sys.exit)  # Escape quits
		self.table = Table()

	def start(self):
		# self.table.run()
		# self.reset_score()
		# self.table.place_ball()
		self.launch_ball()


	def reset_score(self):
		self.balls_used = 0
		self.score = 0

	def launch_ball(self):
		# pass
		taskMgr.doMethodLater(2.5, self.table.simulationTask, 'Physics Simulation')
		# taskMgr.remove('Physics Simulation')


if __name__ == '__main__':
	game = Game()
	game.start()
	# base = ShowBase()
	base.disableMouse()
	base.run()