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
# ball_NP.setPos(0, 0, 0.1)
ball_NP.setPos(4.3,2.85, 0.12)
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



#------example -----
# in order to rotate around a point other than center I need to render a node and then 
# attach the bumper to that node. Then I rotate the first node. 

# newNode = render2d.attachNewNode('newNode')
# sprite.reparentTo(newNode)
# sprite.setPos(1, 0, 0) # or whatever you want the rotate pivot to be
# newNode.setR(rotation)
#-------------------
#extract bumper
egg_bumper = loader.loadModel("models/bumper3.egg")
egg_bumper2= loader.loadModel("models/bumper3.egg")
pivot_left = render.attachNewNode("pivot")

bumper = egg_bumper.find("**/Cube")
bumper2 = egg_bumper2.find("**/Cube")

bumper.setPos(4,.6, .25)
bumper.setHpr(110,0,0)

#(, down, )
bumper2.setPos(0.18,0.4, 0)
bumper2.setH(-110)

pivot_left.setPos(4.12,-1.0, .25)
# pivot_left.setH(-110)


bumper.reparentTo(render)
bumper2.reparentTo(pivot_left)



#-------bumper hit code ---------
hit_bumper2 = False
h = 0
x = 0.0
y =  0.0
z = 0.0

def test_bump_x():
    global x
    x += .1
    bumper2.setPos(x,-y,z)
def test_bump_y():
    global y
    y -= .1
    bumper2.setPos(x,-y,z)
def test_bump_z():
    global z
    z += .1
    bumper2.setPos(x,-y,z)

def move_left_bumper():
    global hit_bumper2
    hit_bumper2 = True


base.accept('a', move_left_bumper)
base.accept('x', test_bump_x)
base.accept('y', test_bump_y)
base.accept('z', test_bump_z)
#-------end bumper hit code ---------


def add_plane_to_physics(planeNP, space, params1, params2, params3, params4):
    plane = OdePlaneGeom(space, params1, params2, params3, params4)
    # plane.setCollideBits(BitMask32(0x00000002))
    # plane.setCategoryBits(BitMask32(0x00000001))
    # plane.setCollideBits(BitMask32(0x00000001))
    # plane.setCategoryBits(BitMask32(0x00000002))
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
wall_north = add_wall_to_physics(space1, 0.1, 6, 2, -5, 0, 1)
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
    # ambientNP = egg.attachNewNode(ambient)
    # egg.setLight(ambientNP)

def set_camera():
    # Set the camera position
    
    # base.camera.setPos(20, 7, 4)
    # base.camera.setPos(10, 9, 20)
    base.camera.setPos(9, 0, 15)
    # base.camera.setPos(18, 0, 15)
    # base.camera.setPos(0,-10,0)
    base.camera.lookAt(0, 0, 0)
    base.disableMouse()

def simulationTask(task):
    space1.autoCollide()  # Setup the contact joints
    # Step the simulation and set the new positions
    world.quickStep(globalClock.getDt())
    ball_NP.setPosQuat(render, ball_body.getPosition(), Quat(ball_body.getQuaternion()))
    sphere.setPos(ball_body.getPosition())
    # ball_body.set_force(0,176.689,-1000)
    # ball_body.set_force(0,0, -100)
    ball_body.setForce(-1, -1, 0)

    # ball_body.setForce(1, 1, 0)

    #----------- handeling update for flippers -------------------------------
    # do I want to rotate the bumper by maually chaging the hpr or do I want 
    # to apply a force to the bumper and some how have it stuck around a screw
    global h
    global hit_bumper2

    if (h < 90) and hit_bumper2 :
        h = h + 1

    # global x
    # global y
    # global z
    

    pivot_left.setPos(4.12,-1.0, .25)
    pivot_left.setH(h)

    contactgroup1.empty()  # Clear the contact joints
    return task.cont

set_camera()
set_light()
base.accept("escape", sys.exit)  # Escape quit
# Wait a split second, then start the simulation
# taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
# box = wireGeom().generate ('box', extents=((7.332, 10.744, 0.676)))
# box.setPos(cube.getPos(render))
# box.setHpr (cube.getHpr(render))
# box.reparentTo( render )
taskMgr.doMethodLater(1.5, simulationTask, "Physics Simulation")

base.run()






