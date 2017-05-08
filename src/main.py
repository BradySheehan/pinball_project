from panda3d.core import loadPrcFileData
#Change resolution 
loadPrcFileData("", "win-size 1024 768")
#make full screen
loadPrcFileData("", "fullscreen t")

from game import Game
from pandac.PandaModules import PStatCollector

if __name__ == '__main__':
	# PStatClient.connect()
	game = Game()
	game.start()