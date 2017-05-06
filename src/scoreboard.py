from direct.gui.OnscreenText import OnscreenText
class Scoreboard():

    def __init__(self, score, max_balls, balls_used, button_enabled):
        self.max_balls = max_balls
        self.button_enabled = button_enabled
        self.lost_message = 'Your weak father should be ashamed of you! \n Your final score is '
        self.stats = 'Score: ' + str(score) + "\n Balls Available: " + str(self.max_balls - balls_used)

        if self.button_enabled:
            self.position = (0,2)
            self.button_text = ''
            self.lost_button_text = '\n \n Press launch to return to the start screen'
        else:
            self.position = (-1,0.9)
            self.button_text = '\n \n Space - launch ball \n a - toggle left flipper \n d - toggle right flipper \n ESC - quit'
            self.lost_button_text = "\n Press enter to play again \n ESC to quit"

        self.text = self.stats + self.button_text

        self.text_object = OnscreenText(
            text=self.text,
            pos=self.position,
            scale=0.065,
            mayChange=True,
            fg=(255,255,255,255),
            bg=(0,0,0,1))

    def updateDisplay(self, score, balls_used):
        self.stats = 'Score: ' + str(score) + "\n Balls Available: " + str(self.max_balls - balls_used)
        self.text = self.stats + self.button_text
        self.text_object.setText(self.text)

    def displayLostGame(self, score, balls_used):
        self.text = self.lost_message + self.lost_button_text + str(score)
        self.text_object.setText(self.text)