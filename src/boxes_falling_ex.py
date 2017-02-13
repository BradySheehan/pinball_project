from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
import sys
from panda3d.core import loadPrcFileData
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdePlaneGeom
from panda3d.core import BitMask32, CardMaker, Vec4, Quat
from random import randint, random
# Change resolution
loadPrcFileData("", "win-size 1024 768")
# make full screen 
loadPrcFileData("", "fullscreen t")

class World(DirectObject):

    def __init__(self):
        self.accept("escape", sys.exit)

w = World()

base = ShowBase()

# Setup our physics world

world = OdeWorld()
world.setGravity(0, 0, -9.81)

# The surface table is needed for autoCollide
world.initSurfaceTable(1)
world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
# world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)

# Create a space and add a contactgroup to it to add the contact joints
space = OdeSimpleSpace()
space.setAutoCollideWorld(world)
contactgroup = OdeJointGroup()
space.setAutoCollideJointGroup(contactgroup)

# Load the box
box = loader.loadModel("models/cube.egg")

# cube = loader.loadModel("models/test_green2.egg")

# # make the table visible
# cube.setPos(1,1,1)
# cube.reparentTo(render)


# Make sure its center is at 0, 0, 0 like OdeBoxGeom
box.setPos(-.5, -.5, -.5)
# box.flattenLight() # Apply transform
# box.setTextureOff()

# Add a random amount of boxes
boxes = []
for i in range(randint(15, 30)):
    # Setup the geometry
    boxNP = box.copyTo(render)
    boxNP.setPos(randint(-10, 10), randint(-10, 10), 10 + random())
    boxNP.setColor(random(), random(), random(), 1)
    boxNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45))
    # Create the body and set the mass
    boxBody = OdeBody(world)
    M = OdeMass()
    M.setBox(50, 1, 1, 1)
    boxBody.setMass(M)
    boxBody.setPosition(boxNP.getPos(render))
    boxBody.setQuaternion(boxNP.getQuat(render))
    # Create a BoxGeom
    boxGeom = OdeBoxGeom(space, 1, 1, 1)
    boxGeom.setCollideBits(BitMask32(0x00000002))
    boxGeom.setCategoryBits(BitMask32(0x00000001))
    boxGeom.setBody(boxBody)
    boxes.append((boxNP, boxBody))

# Add a plane to collide with
cm = CardMaker("ground")
cm.setFrame(-20, 20, -20, 20)
ground = render.attachNewNode(cm.generate())
ground.setPos(0, 0, 0)
ground.lookAt(0, 0, -1)
groundGeom = OdePlaneGeom(space, Vec4(0, 0, 1, 0))
groundGeom.setCollideBits(BitMask32(0x00000001))
groundGeom.setCategoryBits(BitMask32(0x00000002))

# Set the camera position
base.disableMouse()
base.camera.setPos(40, 40, 20)
base.camera.lookAt(0, 0, 0)

# The task for our simulation
def simulationTask(task):
    space.autoCollide() # Setup the contact joints
    # Step the simulation and set the new positions
    world.quickStep(globalClock.getDt())
    for np, body in boxes:
        np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
    contactgroup.empty() # Clear the contact joints
    return task.cont


# # Create Ambient Light
# ambientLight = AmbientLight('ambientLight')
# ambientLight.setColor(Vec4(0.1, 0.1, 0.1, 1))
# ambientLightNP = render.attachNewNode(ambientLight)
# render.setLight(ambientLightNP)

# # Directional light 01
# directionalLight = DirectionalLight('directionalLight')
# directionalLight.setColor(Vec4(0.8, 0.2, 0.2, 1))
# directionalLightNP = render.attachNewNode(directionalLight)
# # This light is facing backwards, towards the camera.
# directionalLightNP.setHpr(180, -20, 0)
# render.setLight(directionalLightNP)

# # Directional light 02
# directionalLight = DirectionalLight('directionalLight')
# directionalLight.setColor(Vec4(0.2, 0.2, 0.8, 1))
# directionalLightNP = render.attachNewNode(directionalLight)
# # This light is facing forwards, away from the camera.
# directionalLightNP.setHpr(0, -20, 0)
# render.setLight(directionalLightNP)

# # Now attach a green light only to object x.
# ambient = AmbientLight('ambient')
# ambient.setColor(Vec4(1, 1, 1, 1))
# ambientNP = cube.attachNewNode(ambient)

# cube.setLightOff() 
# cube.setLight(ambientNP)

# Wait a split second, then start the simulation  
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")

base.run()