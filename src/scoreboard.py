from direct.gui.OnscreenText import OnscreenText
class Scoreboard():

    def __init__(self, score, max_balls, balls_used):
        self.max_balls = max_balls
        self.text_object = OnscreenText(text='Your score is ' + str(score) + "\n Balls Available: " + str(
            max_balls - balls_used) + '\n \n Space - launch ball \n a - toggle left flipper \n d - toggle right flipper \n ESC - quit', pos=(0, 2), scale=0.065, mayChange=True, fg=(255,255,255,255), bg=(0,0,0,1))

    def updateDisplay(self, score, balls_used):
        self.text_object.destroy()
        self.text_object = OnscreenText(text='Your score is ' + str(score) + "\n Balls Available: " + str(
            self.max_balls - balls_used) + '\n \n Space - launch ball \n a - toggle left flipper \n d - toggle right flipper \n ESC - quit', pos=(0, 2), scale=0.065, mayChange=True, fg=(255,255,255,255), bg=(0,0,0,1))

    def displayLostGame(self, score, balls_used):
        self.text_object.destroy()
        self.text_object = OnscreenText(
            text='Your weak father should be ashamed of you! \n Your final score is ' +
            str(score) +
            "\n Press enter to play again \n ESC to quit",
            pos=(
                0,
                0),
            scale=0.1, mayChange=True, fg=(255,255,255,255), bg=(0,0,0,1))