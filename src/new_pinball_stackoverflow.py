
from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom
from panda3d.core import BitMask32, CardMaker, Vec4, Quat
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Light, AmbientLight, DirectionalLight, LMatrix3f
import sys
world = OdeWorld()
world.setGravity(0, 0, -9.81)

# The surface table is needed for autoCollide
world.initSurfaceTable(1)
world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
# what properties should the floor have versus the walls?

# Create a space and add a contactgroup to it to add the contact joints
space1 = OdeSimpleSpace()
space1.setAutoCollideWorld(world)
contactgroup1 = OdeJointGroup()
space1.setAutoCollideJointGroup(contactgroup1)

#load the egg file created in Blender
egg = loader.loadModel("models/table_collide_no_culling.egg")

#Extract the Sphere 
ball = egg.find("**/Sphere")
ball_NP = ball.copyTo(render)
ball_NP.setPos(0, 0, 0.45)
#Setup the sphere's physics
mass = OdeMass()
mass.setSphere(50, 0.1)
ball_body = OdeBody(world)
ball_body.setMass(mass)
ball_body.setPosition(ball_NP.getPos(render))
ball_body.setQuaternion(ball_NP.getQuat(render))
ball_geom = OdeSphereGeom(space1, 0.1)
ball_geom.setCollideBits(BitMask32(0x00000002))
ball_geom.setCategoryBits(BitMask32(0x00000001))
ball_geom.setBody(ball_body)

#extract the cube from the egg file
cube = egg.find("**/Cube")
cube.reparentTo(render)  # make this stuff visible

#ALLEGED PROBLEM SECTION
#attempt to create physics for the cube
cube_geom = OdeBoxGeom(space1, 7.332, 10.744, 0.676)
cube_geom.setCollideBits(BitMask32(0x00000002))
cube_geom.setCategoryBits(BitMask32(0x00000001))
# cube_geom.setPosition(cube.getPos(render))
# cube_geom.setQuaternion(cube.getQuat(render))
cube_geom.setCollideBits(BitMask32(0x00000001))
cube_geom.setCategoryBits(BitMask32(0x00000002))

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
    egg.setLight(ambientNP)

def set_camera():
    # Set the camera position
    base.disableMouse()
    base.camera.setPos(0, 9, 20)
    base.camera.lookAt(0, 0, 0)


def simulationTask(task):
    space1.autoCollide()  # Setup the contact joints
    # Step the simulation and set the new positions
    world.quickStep(globalClock.getDt())
    ball_NP.setPosQuat(render, ball_body.getPosition(),
                       Quat(ball_body.getQuaternion()))
    ball_body.setForce(1, -1, -1)
    contactgroup1.empty()  # Clear the contact joints
    return task.cont

set_camera()
set_light()
base.accept("escape", sys.exit)  # Escape quit
# Wait a split second, then start the simulation
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
base.run()
