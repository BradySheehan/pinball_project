from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Material, LRotationf, NodePath
from panda3d.core import LVector3, BitMask32
from panda3d.core import loadPrcFileData
from panda3d.core import Vec4, Quat, Light, AmbientLight, DirectionalLight
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdePlaneGeom
import sys


# Change resolution
loadPrcFileData("", "win-size 1024 768")
# make full screen
loadPrcFileData("", "fullscreen t")

# class World(DirectObject):

#     def __init__(self):
#         self.accept("escape", sys.exit)

# w = World()


class Pinball(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		self.accept("escape", sys.exit)  # Escape quits


		# Disable default mouse-based camera control.  This is a method on the
		# ShowBase class from which we inherit.
		self.disableMouse()
		camera.setPosHpr(0, 0, 25, 0, -90, 0)  # Place the camera

		# Load the maze and place it in the scene
		self.table = loader.loadModel("models/table_collide_no_culling.egg")
		print self.table
		#self.table.ls()
		self.table.reparentTo(render)

		self.walls = self.table.find("**/Cube.001")
		print self.walls

		self.walls.node().setIntoCollideMask(BitMask32.bit(0))

		self.walls.show()

		self.ball = self.table.find("**/Sphere")
		print self.ball

		self.ball2 = loader.loadModel("models/ball")
		# Load the ball and attach it to the scene
		# It is on a root dummy node so that we can rotate the ball itself without
		# rotating the ray that will be attached to it
		self.ballRoot = render.attachNewNode("ballRoot")
		self.ball = loader.loadModel("models/ball")
		self.ball.reparentTo(self.ballRoot)

		# Find the collison sphere for the ball which was created in the egg file
		# Notice that it has a from collision mask of bit 0, and an into collison
		# mask of no bits. This means that the ball can only cause collisions, not
		# be collided into
		self.ballSphere = self.ball.find("**/ball")
		self.ballSphere.node().setFromCollideMask(BitMask32.bit(0))
		self.ballSphere.node().setIntoCollideMask(BitMask32.allOff())

		self.setup_gravity_world()

		self.set_light()


	def setup_gravity_world(self):

		world = OdeWorld()
		#world.setGravity(0, 0, -9.81)
		world.setGravity(0, -9.81, 0)
		# The surface table is needed for autoCollide
		world.initSurfaceTable(1)
		world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
		# world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)

		# Create a space and add a contactgroup to it to add the contact joints
		space = OdeSimpleSpace()
		space.setAutoCollideWorld(world)
		contactgroup = OdeJointGroup()
		space.setAutoCollideJointGroup(contactgroup)

		body = OdeBody(world)
		M = OdeMass()
		M.setSphere(7874, 1.0)
		body.setMass(M)
		body.setPosition(self.ball.getPos(render))
		body.setQuaternion(self.ball.getQuat(render))

		


	def set_light(self):
		# Create Ambient Light
		ambientLight = AmbientLight('ambientLight')
		ambientLight.setColor(Vec4(0.0, 0.0, 0.0, 1))
		ambientLightNP = render.attachNewNode(ambientLight)
		render.setLight(ambientLightNP)

		# Directional light 01
		directionalLight = DirectionalLight('directionalLight')
		directionalLight.setColor(Vec4(1.0, 0.0, 0.0, 1))
		directionalLightNP = render.attachNewNode(directionalLight)
		# This light is facing backwards, towards the camera.
		directionalLightNP.setHpr(180, -20, 0)
		render.setLight(directionalLightNP)

		# Directional light 02
		directionalLight = DirectionalLight('directionalLight')
		directionalLight.setColor(Vec4(0.0, 1.0, 0.0, 1))
		directionalLightNP = render.attachNewNode(directionalLight)
		# This light is facing forwards, away from the camera.
		directionalLightNP.setHpr(0, -20, 0)
		render.setLight(directionalLightNP)

		# Now attach a green light only to object x.
		ambient = AmbientLight('ambient')
		ambient.setColor(Vec4(.5, .5, 1, 1))
		ambientNP = self.table.attachNewNode(ambient)

		#box.setLightOff()
		self.table.setLight(ambientNP)
demo = Pinball()
demo.run()