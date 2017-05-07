from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.directbase import DirectStart
import os

class LandingScreen():

    def __init__(self, button_enabled):
        self.button_enabled = button_enabled
        self.finished_entering = False
        self.start_text = "Welcome to PINBall!\nBy D. Ramsey and B. Sheehan.\nEnter your username:"
        self.cursor_position = 0 #highlight the letter of interst when we print the text (maybe make it a zero)
        self.initialize_highscore_list()
        self.accept_username_input()

    def display(self):
        self.finished_entering = False
        self.cursor_position = 0
        #every time the landing screen appears, play the song
        os.system('sudo mpg123 -q audio/intro_song1.mp3 &')
        self.image_object = OnscreenImage(
            image = 'models/metal_texture_small2.jpg',
            pos = (0, 0, 0),
            scale=(0.75,0.3,0.4),
            hpr=(0,0,0))

        self.username = ''
        for x in range(0, 5):
            self.username = self.username + chr(self.un[x])

        self.text_object = OnscreenText(
            text=self.start_text + '\n' + self.username,
            pos=(0, 0),
            scale=0.1,
            mayChange=True,
            fg=(192,192,192,192),
            bg=(0,0,0,0),
            shadow=(0,0,0,1))

    def update_display(self):
        #loop over the username array and convert each number to the corresponding chracger,
        #concatenate them, and add them to the onscreen text to be displayed
        self.username = ''
        for x in range(0, 5):
            self.username = self.username + chr(self.un[x])
        self.text = self.start_text + "\n" + self.username
        self.text_object.setText(self.text)

    def remove_display(self):
        self.text_object.destroy()
        self.image_object.destroy()
        self.accept_username_input()

    def initialize_highscore_list(self):
        self.file = open('highscores/highscores.dat', 'w+')
        dir_path = os.path.dirname(os.path.realpath(__file__))
        size = os.stat(os.path.join(dir_path, 'highscores/highscores.dat')).st_size
        if size == 0:
            #write the header to the file (not that we really need it,
            #but so that it is easier to visualize later)
            self.file.write("USERNAME \t SCORE\n")


    def accept_username_input(self):
        self.un = [] #initialize username array
        for x in range(0, 5):
            self.un.insert(x,65)

        # for x in range(65, 91):
        #     print chr(x)
        #right flipper increment, left flipper decrement

        #"cursor" needs to default on the first spot of the username
        #blanks are allowed... default of the string is all blanks
        #numers are not allowed
        # if side_button_pressed():
        #     increment_letter_choice
        #     refresh_text_display
        # if launch_button_pressed():
        #     if end_of_block:
        #         write_username_to_db and make sure we can add score to the file later
        #         delete_landing_screen
        #     else:
        #         save_letter_to_variable
        #         move_cursor_to_next_slot
        #         refresh_text_display

    def enter_username(self):
        if self.cursor_position > 4:
            self.username = ''
            for x in range(0, 4):
                self.username = self.username + chr(self.un[x])
            #now we need to write it to the database
            #including the tab, then when we write the score, we will write a new line at the end of the score
            self.file.write(self.username + '\t')
            # self.file.close()
            # print "returning true"
            self.finished()
            return True
        else:
            #cannot go to next slot if you didn't select a letter
            self.cursor_position = self.cursor_position + 1
        return False

    def finished(self):
        self.finished_entering = True
        return self.username

    def left_down_decrement(self):
        #left down
        #decrement
        if self.cursor_position <= 4:
            if self.un[self.cursor_position] > 65:
                self.un[self.cursor_position] = self.un[self.cursor_position] - 1
                self.update_display()

    def right_down_increment(self):
        #right down
        #increment
        if self.cursor_position <= 4:
            if self.un[self.cursor_position] < 90:
                self.un[self.cursor_position] = self.un[self.cursor_position] + 1
                self.update_display()

    def write_final_score(self, score):
        self.file.write(str(score) + '\n')


if __name__ == '__main__':
    ls = LandingScreen(False)
    ls.display()
    base.run()