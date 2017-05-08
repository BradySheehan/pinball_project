from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.directbase import DirectStart
import os
import errno


class LandingScreen():

    def __init__(self, button_enabled):
        self.button_enabled = button_enabled
        self.finished_entering = False
        self.file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'highscores/highscores.dat')
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
        #see http://stackoverflow.com/questions/10978869/safely-create-a-file-if-and-only-if-it-does-not-exist-with-python
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            self.file = os.open(self.file_name, flags)
        except OSError as e:
            if e.errno == errno.EEXIST:  # Failed as the file already exists.
                pass
            else:  # Something unexpected went wrong so reraise the exception.
                raise
        else:  # No exception, so the file must have been created successfully.
            with os.fdopen(self.file, 'w') as file_obj:
                # Using `os.fdopen` converts the handle to an object that acts like a
                # regular Python file object, and the `with` context manager means the
                # file will be automatically closed when we're done with it.
                self.file = file_obj

    def accept_username_input(self):
        self.un = [] #initialize username array
        for x in range(0, 5):
            self.un.insert(x,65)

    def enter_username(self):
        if self.cursor_position > 4:
            self.username = ''
            for x in range(0, 5):
                self.username = self.username + chr(self.un[x])
            #now we need to write it to the database
            #including the tab, then when we write the score, we will write a new line at the end of the score
            self.finished()
            return True
        else:
            #cannot go to next slot if you didn't select a letter
            self.cursor_position = self.cursor_position + 1
        return False

    def finished(self):
        #how we communicate inside Game that the username
        #has been entered completel
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
        self.update_score(self.username, score)

    def update_score(self, username, score):
        #maintain ordering of the list so that the highest
        #score is at the top of the file
        # self.file.close()
        updated_score = False
        found_username = False
        with open(self.file_name,'r+') as f:
            print f
            self.data = f.readlines()
            print self.data
        for i, d in enumerate(self.data):
            dsplit = d.split()
            if len(dsplit) > 0:
                if dsplit[0] == username:
                    found_username = True
                    print "found username"
                    print dsplit[0]
                    print str(score)
                    print int(dsplit[1])
                    if int(dsplit[1]) < int(score):
                        #new entry is 
                        print "updated = true"
                        updated_score = True
                        self.data[i] = username + ' ' + str(score)

        if found_username is False:
            print "did not find username"
            #add data to end of data list
            self.data.append(username + ' ' + str(score))
            self.data = sorted(self.data, key = lambda x: int(x.split()[1]), reverse=True)
            #then sort the data and write tthe file
            with open(self.file_name, 'w') as file:
                for item in self.data:
                    item = item.strip()
                    if item != '' and item != '\n':
                        file.write("%s \n" % item)

        if updated_score:
            print "updated score"
            self.data = sorted(self.data, key = lambda x: int(x.split()[1]), reverse=True)
            #now write the data back out to the list
            with open(self.file_name, 'w') as file:
                for item in self.data:
                    item = item.strip()
                    if item != '' and item != '\n':
                        file.write("%s\n" % item)

    def display_high_scores(self):
        with open(self.file_name,'r+') as f:
            data = f.readlines()
            #now we want to loop over the top 5 scores and add them to an
            #object we can print to the screen
        text = 'Username\tScore\n\n'
        for i, d in enumerate(data):
            if i > 5:
                break
            else:
                item = d.strip().split()
                if len(item) > 0:
                    text = text + item[0] + "\t" + item[1] + "\n"

        if self.button_enabled:
            position = (0,1.65,0)
        else:
            position = (1,0.9)
        self.high_score_text = OnscreenText(
            text=text,
            pos=position,
            scale=0.065,
            mayChange=False,
            fg=(255,255,255,255),
            bg=(0,0,0,1))

if __name__ == '__main__':
    ls = LandingScreen(False)
    ls.display()
    ls.update_score('AAAAA', 65)
    base.run()