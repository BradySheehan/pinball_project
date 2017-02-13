from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Material, LRotationf, NodePath
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import TextNode
from panda3d.core import LVector3, BitMask32
from panda3d.core import loadPrcFileData
from direct.gui.OnscreenText import OnscreenText
from direct.interval.MetaInterval import Sequence, Parallel
from direct.interval.LerpInterval import LerpFunc
from direct.interval.FunctionInterval import Func, Wait
from direct.task.Task import Task
import sys
from direct.showbase.DirectObject import DirectObject

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
		self.table.ls()
		self.table.reparentTo(render)

		self.walls = self.table.find("**/Cube.001")
		print self.walls

		self.walls.node().setIntoCollideMask(BitMask32.bit(0))

		self.walls.show()

demo = Pinball()
demo.run()