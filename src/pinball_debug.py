from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom, OdeTriMeshGeom, OdeTriMeshData
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
ball_NP.setPos(0,0, 0.01)
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

#extract the cube from the egg file
# /src/models/box_in_edit_mode_with_wall.egg
egg2 = loader.loadModel("models/visible_table_inner_wall.egg")
plane1 = egg2.find("**/Plane.001")
plane1.reparentTo(render)
plane2 = egg2.find("**/Plane.002")
plane2.reparentTo(render)
plane3 = egg2.find("**/Plane.003")
plane3.reparentTo(render)
plane4 = egg2.find("**/Plane.004")
plane4.reparentTo(render)
plane5 = egg2.find("**/Plane.005")
plane5.reparentTo(render)

inner_wall = egg2.find("**/Cube")
inner_wall.reparentTo(render)
# egg3 = loader.loadModel("models/box_in_edit_mode_with_wall.egg")
# plane6 = egg3.find("**/Plane.006")
# plane6.reparentTo(render)



def add_plane_to_physics(planeNP, space, params1, params2, params3, params4):
    plane = OdePlaneGeom(space, params1, params2, params3, params4)
    pos = planeNP.getPos(render)
    plane.setCollideBits(BitMask32(0x00000002))
    plane.setCategoryBits(BitMask32(0x00000001))
    plane.setCollideBits(BitMask32(0x00000001))
    plane.setCategoryBits(BitMask32(0x00000002))
    return plane

def add_wall_to_physics(space, dimx, dimy, dimz, locx, locy, locz):
    box = OdeBoxGeom(space, dimx, dimy, dimz)
    box.setPosition(locx, locy, locz)
    box.setCollideBits(BitMask32(0x00000002))
    box.setCategoryBits(BitMask32(0x00000001))
    box.setCollideBits(BitMask32(0x00000001))
    box.setCategoryBits(BitMask32(0x00000002))
    return box

ground_plane = add_plane_to_physics(plane1, space1, 0, 0, 1, 0)
wall_west = add_wall_to_physics(space1, 10, 0.1, 2, 0, -3, 1)
wall_east = add_wall_to_physics(space1, 10, 0.1, 2, 0, 3, 1)
wall_north = add_wall_to_physics(space1, 0.1, 5, 2, -5, 0, 1)
wall_south = add_wall_to_physics(space1, 1, 5, 2, 5, 0, 1)
bumper_wall = add_wall_to_physics(space1, 3.5, 0.2, 0.5, 3.25, 2.6, 0.25)

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
    base.camera.setPos(9, 0, 15)
    # base.camera.setPos(18, 0, 15)
    # base.camera.setPos(0,-10,0)
    base.camera.lookAt(0, 0, 0)

def simulationTask(task):
    space1.autoCollide()  # Setup the contact joints
    # Step the simulation and set the new positions
    world.quickStep(globalClock.getDt())
    ball_NP.setPosQuat(render, ball_body.getPosition(), Quat(ball_body.getQuaternion()))
    sphere.setPos(ball_body.getPosition())
    # ball_body.set_force(0,176.689,-1000)
    # ball_body.set_force(0,0, -100)
    ball_body.setForce(1, 1, 0)
    # ball_body.setForce(1, 1, 0)
    contactgroup1.empty()  # Clear the contact joints
    return task.cont

set_camera()
set_light()
base.accept("escape", sys.exit)  # Escape quit
# Wait a split second, then start the simulation
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
# box = wireGeom().generate ('box', extents=((7.332, 10.744, 0.676)))
# box.setPos(cube.getPos(render))
# box.setHpr (cube.getHpr(render))
# box.reparentTo( render )

base.run()
