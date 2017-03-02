from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom
from panda3d.core import BitMask32, CardMaker, Vec4, Quat
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Light, AmbientLight, DirectionalLight,LMatrix3f
import sys

from visualizeGeoms import wireGeom
# notes aboute ode:
# ODE consists of two effectively separate, though designed to 
# work together, systems - collision handling and rigid body 
# physics. The rigid body physics simply makes bodies move 
# acording to the rules of physics - Newtons equations 
# basically, whilst the collision detection system handles 
# when things collide. 

# onCollision is an event that is being called every time 
# two geoms collide, a geom being an object in the collision 
# detection system. The bodies are the associated objects in 
# the rigid body physics system, each controlling their 
# respective geoms. In other words the bodies make the geoms 
# move by applying the rules of physics, and the geoms tell 
# the bodies when they have collided, so the physics can 
# take into account the collision. (onCollision is not 
# 	involved in this however - that is all being handled 
# 	automatically by ODE.) 

# What this practically means is that these objects contain
#  different information - a geom is the shape of an object 
#  and its position and rotation; a body also contains 
#  position and rotation (not necessarily the same - there 
#  	can be an offset.), but also includes things like mass, 
#  moments of inertia, velocity and torque. If you want to
#   make an object move you do so by applying a force to 
#   the body, if you want to make it change shape you 
#   update (Well, replace.) the geom. Additionally a 
#   body can have multiple geoms, so you can construct 
#   a single physically moving object out of multiple 
#   chunks of geometry. Also you can have a geom that never 
#   moves, and hence doesn't have a body - this is used for 
#   level geometry. 


# basic idea: apply force to ode body to make an object move
# geom is the shape of an object and its position and rotation
# therefore, our walls should not need bodys, the walls only need geoms

# These are the steps needed to have your objects collide with each other:

# - Create an OdeSpace (explained below). Use setAutoCollideWorld(world) to let the OdeSpace know 
# in which world you want to collide things.
# - Create an OdeJointGroup() to hold the contact joints. Use space.setAutoCollideJointGroup 
# to let the space know in which OdeJointGroup you would like to store the contact joints.
# - Configure the surface table for the world.
# - Create ODE collision geometry for your bodies, e.g. OdeBoxGeom, OdePlaneGeom, etc. Be 
# sure to set collide and category bitmasks on it using the setCollideBits and setCategoryBits 
# methods. Assign it to your body using geom.setBody(body).
# - In your simulation loop, call space.autoCollide() before you call world.quickStep.
# - After using quickStep, you need to empty your OdeJointGroup using the empty() method.

# If you have multiple surfaces, you need to tell ODE 
# which surface belongs to which geometry. You can 
# assign surfaces to your geometry using
#  odeSpace.setSurfaceType(geometry, surfaceId)


# NOTE:
# 3. Whenever you move an object from one point to another
# in your scene (except when you put it into your scene 
# 	the first time), instead of using:

# object.setPos(newPos)
# You should use:

# object.setFluidPos(newPos)
# In general, setPos() means "put the object here, 
# directly" and setFluidPos() means "slide the 
# object here, testing for collisions along the 
# way". It is important to make a clear distinction
#  between these two calls, and make the appropriate
#   call for each situation.

world = OdeWorld()
world.setGravity(0, 0, -9.81)


# The surface table is needed for autoCollide
world.initSurfaceTable(1)
world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
#what properties should the floor have versus the walls?

# Create a space and add a contactgroup to it to add the contact joints
space1 = OdeSimpleSpace()
space1.setAutoCollideWorld(world)
contactgroup1 = OdeJointGroup()
space1.setAutoCollideJointGroup(contactgroup1)

egg = loader.loadModel("models/table_collide_no_culling.egg")

ball = egg.find("**/Sphere")
ball_NP = ball.copyTo(render)
ball_NP.setPos(0,0,0.1)

mass = OdeMass();
mass.setSphere(50, 0.1)
# ball_geom = OdeSphereGeom(space1, 0.5)
ball_body = OdeBody(world)
ball_body.setMass(mass)
ball_body.setPosition(ball_NP.getPos(render))
ball_body.setQuaternion(ball_NP.getQuat(render))

#now we need to create body's for each of these and set mass on them
#I think we also need to give the the ball a mass

ball_geom = OdeSphereGeom(space1, 0.1)
ball_geom.setCollideBits(BitMask32(0x00000002))
ball_geom.setCategoryBits(BitMask32(0x00000001))
ball_geom.setBody(ball_body)


inner_walls = egg.find("**/Cube")
inner_walls.reparentTo(render) #make this stuff visible

# inner_walls.setPos(0, 0, 0)
# inner_walls.lookAt(0, 0, 0) #Sets the hpr on this NodePath so that it rotates to face the indicated point in space.

#now assign the outer_walls to be collision solids with ode mechanics

outer_walls = egg.find("**/Cube.001")
# note : OdeBoxGeom (OdeSpace space, float lx, float ly, float lz)
#dimensions of inner box = (7.332, 10.744, 0.676)
#dimensions of outer box = (7.667, 12.235, 0.707)
walls = OdeBoxGeom(space1, 2.667, 2.235, 1.707)

# walls.setRotation(LMatrix3f(180))
walls.setCollideBits(BitMask32(0x00000001))
walls.setCategoryBits(BitMask32(0x00000002))

#somehow we need to position an odeplanegeom that aligns
#with where the blender file walls are

def set_light():
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
	ambientNP = egg.attachNewNode(ambient)
	#box.setLightOff()
	egg.setLight(ambientNP)

def set_camera():
	# Set the camera position
	base.disableMouse()
	base.camera.setPos(2, 2, 25)
	base.camera.lookAt(0, 0, 0.5)
	# camera.setPosHpr(0, 0, 25, 0, -90, 0)  # Place the camera

def simulationTask(task):
  space1.autoCollide() # Setup the contact joints
  # Step the simulation and set the new positions
  world.quickStep(globalClock.getDt())
  ball_NP.setPosQuat(render, ball_body.getPosition(), Quat(ball_body.getQuaternion()))
  # ball_body.setForce(1, -1, -1)
  contactgroup1.empty() # Clear the contact joints
  return task.cont

set_camera()
set_light()
base.accept("escape", sys.exit)  # Escape quit
boxNodepath = wireGeom().generate ('box', extents=(2.667, 2.235, 1.707))
# Wait a split second, then start the simulation  
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
base.run()
