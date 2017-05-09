from direct.directbase import DirectStart
from direct.directtools.DirectGeometry import LineNodePath
from panda3d.core import *
from panda3d.ode import *


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
 
# Load the smiley and frowney models
smiley = loader.loadModel("smiley.egg")
smiley.reparentTo(render)
smiley.setPos(0, 0, 2)
frowney = loader.loadModel("frowney.egg")
frowney.reparentTo(render)
frowney.setPos(-7.5, 0, -0.5)
 
# Setup our physics world
world = OdeWorld()
world.setGravity(0, 0, -9.81)
 
# Setup the body for the smiley
smileyBody = OdeBody(world)
M = OdeMass()
M.setSphere(5000, 1.0)
smileyBody.setMass(M)
smileyBody.setPosition(smiley.getPos(render))
smileyBody.setQuaternion(smiley.getQuat(render))
 
# Now, the body for the frowney
frowneyBody = OdeBody(world)
M = OdeMass()
M.setSphere(5000, 1.0)
frowneyBody.setMass(M)
frowneyBody.setPosition(frowney.getPos(render))
frowneyBody.setQuaternion(frowney.getQuat(render))
 
# Create the joints
smileyJoint = OdeBallJoint(world)
# smileyJoint.attach(smileyBody, smileyBody) # Attach it to the environment
smileyJoint.setAnchor(0, 0, 0)
frowneyJoint = OdeBallJoint(world)
frowneyJoint.attach(smileyBody, frowneyBody)
frowneyJoint.setAnchor(-5, 0, -5)


space1 = OdeSimpleSpace()
space1.setAutoCollideWorld(world)
contactgroup = OdeJointGroup()
space1.setAutoCollideJointGroup(contactgroup)
 
table_egg = loader.loadModel(
            "models/table2.egg")
plane1 = table_egg.find("**/Plane.001")
plane1.reparentTo(render)
plane1.flattenLight()
plane = OdePlaneGeom(space1, 0, 0, 1, 0)
 
# Set the camera position
base.disableMouse()
base.camera.setPos(0, 0, 10)
base.camera.lookAt(0, 0, 0)
 
# We are going to be drawing some lines between the anchor points and the joints
lines = LineNodePath(parent = render, thickness = 3.0, colorVec = Vec4(1, 0, 0, 1))
def drawLines():
  # Draws lines between the smiley and frowney.
  lines.reset()
  lines.drawLines([((frowney.getX(), frowney.getY(), frowney.getZ()),
                    (smiley.getX(), smiley.getY(), smiley.getZ())),
                   ((smiley.getX(), smiley.getY(), smiley.getZ()),
                    (0, 0, 0))])
  lines.create()
 
# The task for our simulation
def simulationTask(task):
  # Step the simulation and set the new positions
  space1.autoCollide()
  world.quickStep(globalClock.getDt())
  # frowney.setPosQuat(render, frowneyBody.getPosition(), Quat(frowneyBody.getQuaternion()))
  frowneyBody.setPosition(frowney.getPos())
  smiley.setPosQuat(render, smileyBody.getPosition(), Quat(smileyBody.getQuaternion()))
  drawLines()
  # base.camera.lookAt(smiley.getPos())
  print smiley.getPos()
  contactgroup.empty() 
  return task.cont
 
drawLines()
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
 
run()