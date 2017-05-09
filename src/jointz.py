from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdePlaneGeom, OdeSphereGeom
from panda3d.core import BitMask32, CardMaker, Vec4, Quat, Light, AmbientLight, DirectionalLight
from random import randint, random


# Setup our physics world
world = OdeWorld()
world.setGravity(0, 0, -9.81)
 
# The surface table is needed for autoCollide
world.initSurfaceTable(1)
world.setSurfaceEntry(0, 0, 0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.00)
 
# Create a space and add a contactgroup to it to add the contact joints
space = OdeSimpleSpace()
space.setAutoCollideWorld(world)
contactgroup = OdeJointGroup()
space.setAutoCollideJointGroup(contactgroup)
 
table = loader.loadModel("models/table_collide_no_culling.egg")
box = table.find("**/Sphere")
#box.reparentTo(render)
# Load the box
#box = loader.loadModel("box")
# Make sure its center is at 0, 0, 0 like OdeBoxGeom
box.setPos(-.5, -.5, -.5)
#box.setScale()
box.flattenLight() # Apply transform
box.setTextureOff()

# Add a random amount of boxes
boxes = []
for i in range(1):
  # Setup the geometry
  boxNP = box.copyTo(render)
 # boxNP.setPos(randint(-10, 10), randint(-10, 10), 10 + random())
  boxNP.setPos(.5+i,.5,10)
  #boxNP.setColor(random(), random(), random(), 10)
  #boxNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45))
  # Create the body and set the mass
  boxBody = OdeBody(world)
  M = OdeMass()
  M.setSphere(100, .6)
  boxBody.setMass(M)
  boxBody.setPosition(boxNP.getPos(render))
  boxBody.setQuaternion(boxNP.getQuat(render))
  # Create a BoxGeom
  #boxGeom = OdeBoxGeom(space, 1, 1, 1)
  boxGeom = OdeSphereGeom(space, .6)
  boxGeom.setCollideBits(BitMask32(0x00000002))
  boxGeom.setCategoryBits(BitMask32(0x00000001))
  boxGeom.setBody(boxBody)
  boxes.append((boxNP, boxBody))


# Add a plane to collide with
cm = CardMaker("ground")
cm.setFrame(-20, 10, -20, 10)
ground = render.attachNewNode(cm.generate())
ground.setPos(0, 0, 0); ground.lookAt(0, 0, -1)

groundGeom = OdePlaneGeom(space, Vec4(0, 0, 1, 0))
groundGeom.setCollideBits(BitMask32(0x00000001))
groundGeom.setCategoryBits(BitMask32(0x00000002))


# Add a plane to collide with
# cm2 = CardMaker("left")
# cm2.setFrame(-10, 10, -10, 10)
# cm.setFrameFullscreenQuad()
# ground2 = render.attachNewNode(cm2.generate())
# ground2.setPos(-1, 1, 0); ground2.lookAt(0, 0, -1)
# groundGeom2 = OdePlaneGeom(space, Vec4(0, 0, 1, 0))
# groundGeom2.setCollideBits(BitMask32(0x00000001))
# groundGeom2.setCategoryBits(BitMask32(0x00000002))

# Set the camera position
base.disableMouse()
#base.camera.setPos(20, 20, 10)
base.camera.setPos(-30, -30, 30)
base.camera.lookAt(boxNP.getPos(render))

# Create Ambient Light
ambientLight = AmbientLight('ambientLight')
ambientLight.setColor(Vec4(0.0, 0.0, 0.0, 1))
ambientLightNP = render.attachNewNode(ambientLight)
render.setLight(ambientLightNP)

# Directional light 01
directionalLight = DirectionalLight('directionalLight')
directionalLight.setColor(Vec4(0.0, 0.0, 1.0, 1))
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
ambientNP = box.attachNewNode(ambient)

#box.setLightOff()
box.setLight(ambientNP)
# The task for our simulation
def simulationTask(task):
  space.autoCollide() # Setup the contact joints
  # Step the simulation and set the new positions
  world.quickStep(globalClock.getDt())
  for np, body in boxes:
    np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
    body.setForce(-1.0, 0 , 0)
    base.camera.lookAt(body.getPosition())
  contactgroup.empty() # Clear the contact joints
  return task.cont
 
# Wait a split second, then start the simulation  
taskMgr.doMethodLater(.5, simulationTask, "Physics Simulation")
 
run()