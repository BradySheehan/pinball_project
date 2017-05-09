
from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom
from panda3d.core import BitMask32, CardMaker, Vec4, Quat
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Light, AmbientLight, DirectionalLight, LMatrix3f
from panda3d.core import GeomVertexData, GeomVertexWriter, GeomVertexFormat, Geom, GeomTriangles, GeomNode
#from visualizeGeoms import wireGeom
import sys

# CODE FOR ADDING AXIS

# #step 1) create GeomVertexData and add vertex information 
# format = GeomVertexFormat.getV3() 
# vdata = GeomVertexData("vertices", format, Geom.UHStatic) 
# vdata.setNumRows(4) 

# vertexWriter = GeomVertexWriter(vdata, "vertex") 
# vertexWriter.addData3f(0,0,0)
# vertexWriter.addData3f(1,0,0)
# vertexWriter.addData3f(1,0,1)
# vertexWriter.addData3f(0,0,1)

# #step 2) make primitives and assign vertices to them 
# tris=GeomTriangles(Geom.UHStatic) 

# #have to add vertices one by one since they are not in order 
# tris.addVertex(0) 
# tris.addVertex(1) 
# tris.addVertex(3) 

# #indicates that we have finished adding vertices for the first triangle. 
# tris.closePrimitive() 

# #since the coordinates are in order we can use this convenience function. 
# tris.addConsecutiveVertices(1,3) #add vertex 1, 2 and 3 
# tris.closePrimitive() 

# #step 3) make a Geom object to hold the primitives 
# squareGeom=Geom(vdata) 
# squareGeom.addPrimitive(tris) 

# #now put squareGeom in a GeomNode. You can now position your geometry in the scene graph. 
# squareGN=GeomNode("square")
# squareGN.addGeom(squareGeom)
# render.attachNewNode(squareGN)



#load the egg file created in Blender
egg = loader.loadModel("models/square4.egg")
cube = egg.find("**/square")
print type(cube)
cube.setPos(0,0,0)


cube.reparentTo(render)  # make this stuff visible

def set_camera():
    # Set the camera position
    base.disableMouse()
    base.camera.setPos(-5, -5, -5)
    # base.camera.setPos(2, 9, 20)
    base.camera.lookAt(0, 0, 0)

def set_light():
    # Create Ambient Light
    ambientLight = AmbientLight('ambientLight')
    ambientLight.setColor(Vec4(0.0, 0.0, 0.0, 1))
    ambientLightNP = render.attachNewNode(ambientLight)
    render.setLight(ambientLightNP)
    # Directional light 01
    directionalLight = DirectionalLight('directionalLight')
    directionalLight.setColor(Vec4(1.0, 0.0, 1.0, 1))
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

base.accept("escape", sys.exit)  # Escape quit

set_camera()
set_light()


base.run()
