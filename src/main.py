for_pi = True

if for_pi is False:
	pass
#Change resolution 
	# from panda3d.core import loadPrcFileData

	# loadPrcFileData("", "win-size 1024 768")
	# #make full screen
	# loadPrcFileData("", "fullscreen t")

from game import Game

if __name__ == '__main__':
	game = Game(for_pi)
	game.start()