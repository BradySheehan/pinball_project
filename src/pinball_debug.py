from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom
from panda3d.core import BitMask32, Vec4, Quat
from panda3d.core import Light, AmbientLight, DirectionalLight, LMatrix3f
from visualizeGeoms import wireGeom
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
print ball.getName()
print type(ball)

ball_NP = ball.copyTo(render)
# ball_NP.setPos(0, 0, 0.45)
ball_NP.setPos(0,0, 0.35)
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

sphere = wireGeom().generate ('sphere', radius=0.1)
sphere.setPos (ball_NP.getPos(render))
sphere.reparentTo(render)
# sphere.setHpr (0, 0, 0)

#extract the cube from the egg file
egg2 = loader.loadModel("models/box_in_edit_mode.egg")
plane1 = egg2.find("**/Plane.001")
print "plane1", plane1, type(plane1)
plane1.reparentTo(render)
plane2 = egg2.find("**/Plane.002")
print "plane2", plane2, type(plane2)
plane2.reparentTo(render)
plane3 = egg2.find("**/Plane.003")
print "plane3", plane3, type(plane3)
plane3.reparentTo(render)
plane4 = egg2.find("**/Plane.004")
print "plane4", plane4, type(plane4)
plane4.reparentTo(render)
plane5 = egg2.find("**/Plane.005")
print "plane5", plane5, type(plane5)
plane5.reparentTo(render)

def add_plane_to_physics(planeNP, space, params1, params2, params3, params4):
    #create the plane
    #set the position
    #set the collide/category bits
    plane = OdePlaneGeom(space, params1, params2, params3, params4)
    pos = planeNP.getPos(render)

    plane.setCollideBits(BitMask32(0x00000002))
    plane.setCategoryBits(BitMask32(0x00000001))
    print plane, type(plane)
    print planeNP.getPos(render), type(planeNP.getPos(render))
    print planeNP.getQuat(render), type(planeNP.getQuat(render))
    plane.setPosition(pos[0], pos[1], pos[2])
    # plane.setQuaternion(planeNP.getQuat(render))
    return plane

ground_plane = add_plane_to_physics(plane1, space1, 0, 0, 1, 0)

# cube = egg.find("**/Cube")
# print cube.getName()
# print type(cube)
# cube.reparentTo(render)  # make this stuff visible

# cube_geom = OdeBoxGeom(space1, (10, 6, 2))
# cube_geom.setCollideBits(BitMask32(0x00000002))
# cube_geom.setCategoryBits(BitMask32(0x00000001))
# cube_geom.setPosition(cube.getPos(render))
# cube_geom.setQuaternion(cube.getQuat(render))

def set_light():
    # Create Ambient Light
    ambientLight = AmbientLight('ambientLight')
    ambientLight.setColor(Vec4(0.0, 0.0, 0.0, 1))
    ambientLightNP = render.attachNewNode(ambientLight)
    render.setLight(ambientLightNP)
    # Directional light 01
    directionalLight = DirectionalLight('directionalLight')
    directionalLight.setColor(Vec4(1.0, 1.0, 1.0, 1))
    directionalLightNP = render.attachNewNode(directionalLight)
    # This light is facing backwards, towards the camera.
    directionalLightNP.setHpr(180, -20, 0)
    render.setLight(directionalLightNP)
    # Directional light 02
    directionalLight = DirectionalLight('directionalLight')
    directionalLight.setColor(Vec4(0.0, 1.0, 1.0, 1))
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
    # base.camera.setPos(20, 7, 4)
    # base.camera.setPos(10, 9, 20)
    base.camera.setPos(18, -10, 15)
    base.camera.lookAt(0, 0, 0)

def simulationTask(task):
    space1.autoCollide()  # Setup the contact joints
    # Step the simulation and set the new positions
    world.quickStep(globalClock.getDt())
    ball_NP.setPosQuat(render, ball_body.getPosition(),
                       Quat(ball_body.getQuaternion()))
    sphere.setPos (ball_body.getPosition())
    # ball_body.set_force(0,176.689,-1000)
    # ball_body.set_force(0,0, -100)
    # ball_body.setForce(0, 1, -1)
    # ball_body.setForce(1, 1, 0)
    contactgroup1.empty()  # Clear the contact joints
    return task.cont

set_camera()
set_light()
base.accept("escape", sys.exit)  # Escape quit
# Wait a split second, then start the simulation
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
box = wireGeom().generate ('box', extents=((7.332, 10.744, 0.676)))
box.setPos(cube.getPos(render))
box.setHpr (cube.getHpr(render))
box.reparentTo( render )

base.run()
