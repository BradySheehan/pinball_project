from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom
from panda3d.core import BitMask32, Vec4, Quat, VBase3
from panda3d.core import Light, AmbientLight, DirectionalLight
import sys
import os
# from table import Table
# from scoreboard import Scoreboard
# from landing_screen import LandingScreen


class Game():

    def __init__(self, button_enabled):
        from table import Table
        from landing_screen import LandingScreen
        base.disableMouse()
        base.setFrameRateMeter(True)
        base.accept("escape", sys.exit)  # Escape quits
        self.max_balls = 1
        self.balls_used = 0
        self.score = 0
        self.button_enabled = button_enabled
        self.landing_screen = LandingScreen(self.button_enabled)
        self.table = Table(self.button_enabled)
        if self.button_enabled:
            from RPi import GPIO
            global GPIO
        from panda3d.core import WindowProperties
        wp = WindowProperties()
        wp.setFullscreen(False)
        base.win.requestProperties(wp)
        self.jump_sound = loader.loadMusic("audio/jump.wav")
        self.intro_song = loader.loadMusic("audio/intro_song1.wav")
        self.power_up_ray = loader.loadMusic("audio/Power_Up_Ray.wav")
        self.electrical_sweep = loader.loadMusic("audio/Electrical_Sweep.wav")
        self.lasor_cannon = loader.loadMusic("audio/Laser_Cannon.wav")
        self.strong_punch = loader.loadMusic("audio/Strong_Punch.wav")

    def start(self):
        self.not_first_time = False
        self.intro_song.setLoopCount(0)
        self.intro_song.play()
        if self.button_enabled:
            self.start_button_handler()
        else: #setup accepts for the a, d, and enter keys to work with landing_screen
            base.accept('a', self.landing_screen.left_down_decrement)
            base.accept('d', self.landing_screen.right_down_increment)
            base.accept('enter', self.landing_screen.enter_username)
        self.landing_screen.display()
        taskMgr.doMethodLater(
            0,
            self.listen_for_input,
            'listen_for_input') #listens for input related to managing the landing screen controls
        base.run()
        #this might be wrong.. we don't want to place_ball() until
        #landing screen is finished. Make sure this works
        #additionally, we want the scoreboard to show the username of the current player

    def finish_start(self):
        from scoreboard import Scoreboard
        #this function will do everything that needs to happen after the user picks their username
        self.landing_screen.remove_display()
        self.landing_screen.display_high_scores()
        self.scoreboard = Scoreboard(
            self.score, self.max_balls, self.balls_used, self.button_enabled, self.landing_screen.username)
        self.enable_buttons(self.button_enabled)
        base.acceptOnce("close_launcher", self.table.close_launcher)
        self.place_ball()

        #I don't think we should take them to the landing screen if they lose,
        #give them the option to play again with the current username. this will take some work though

    def restart(self):
        self.reset_score()
        self.scoreboard.text_object.destroy()
        self.landing_screen.high_score_text.destroy()
        self.landing_screen.display()
        if self.button_enabled:
            self.start_button_handler()
        else: #setup accepts for the a, d, and enter keys to work with landing_screen
            base.accept('a', self.landing_screen.left_down_decrement)
            base.accept('d', self.landing_screen.right_down_increment)
            base.accept('enter', self.landing_screen.enter_username)
            taskMgr.doMethodLater(
                0,
                self.listen_for_input,
                'listen_for_input') #listens for input related to managing the landing screen controls

    def place_ball(self):
        self.table.ball.setPos(3.705, 2.85, 0.1)
        self.table.ball_body.setPosition(self.table.ball.getPos(render))
        self.table.ball_body.setQuaternion(self.table.ball.getQuat(render))
        if self.not_first_time:
            self.table.can_launch = False
            self.table.open_launcher()
        self.allow_launch()
        self.not_first_time = True

    def allow_launch(self):
        if self.button_enabled:
            base.acceptOnce("button_build_force", self.build_launch_force)
            base.acceptOnce("button_launch", self.launch_ball)
            taskMgr.doMethodLater(
                0,
                self.start_button_launch,
                'start_button_launch')
        else:
            base.acceptOnce('space', self.build_launch_force)
            base.acceptOnce('space-up', self.launch_ball)

    def reset_score(self):
        self.balls_used = 0
        self.score = 0

    def enable_buttons(self, on):
            if on :
                #make sure start_button_handler is called before this
                base.accept('left_down',self.table.move_left_flipper)
                base.accept('left_up',self.table.stop_left_flipper)
                base.accept('right_down',self.table.move_right_flipper)
                base.accept('right_up',self.table.stop_right_flipper)
            else:
                base.accept('a', self.table.move_left_flipper)
                base.accept('a-up', self.table.stop_left_flipper)

                base.accept('d', self.table.move_right_flipper)
                base.accept('d-up', self.table.stop_right_flipper)

    def start_button_handler(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP) #right button
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP) #left button
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) #launch button
        # pass

    def build_launch_force(self):
        self.power_up_ray.play()
        taskMgr.doMethodLater(
            0,
            self.table.build_launch_force_task,
            'build_launch_force')

    def launch_ball(self):
        # print 'gravity task is started'
        self.strong_punch.play()
        self.start_gravity_task()
        taskMgr.doMethodLater(
            0,
            self.table.release_plunger_task,
            'release_plunger')
        taskMgr.doMethodLater(
            1,
            self.table.stop_launch_ball_task,
            'stop_launch_ball')
        taskMgr.doMethodLater(
            0.5,
            self.start_bump_ball_task,
            'bump_ball_task')

    def start_gravity_task(self):
        taskMgr.doMethodLater(0, self.table.gravity_task, 'gravity_task')

    def remove_gravity_task(self):
        taskMgr.remove('gravity_task')

    def bump_ball_event(self, entry):
        geom1 = entry.getGeom1()
        geom2 = entry.getGeom2()
        body1 = entry.getBody1()
        body2 = entry.getBody2()
        self.table.apply_force_to_ball(self.bumped_by_flipper(geom1, geom2, body1, body2))
        if self.table.can_launch:
            if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.plunger_geom):
                self.table.can_launch = False
                # print 'here'
                # print 'gravity task is removed'
                self.remove_gravity_task()
                self.allow_launch()

        #below is a check for if the ball hits the back wall of the table
        if (
            (
                geom1 and geom1 == self.table.wall_south) and (
                (body1 and body1 == self.table.ball_body) or (
                body2 and body2 == self.table.ball_body))) or (
                    (geom2 and geom2 == self.table.wall_south) and (
                        (body1 and body1 == self.table.ball_body) or (
                            body2 and body2 == self.table.ball_body))):
            self.remove_gravity_task()
            self.lose_ball()

        if self.bumped_triangle_bumper(geom1, geom2, body1, body2):
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            self.jump_sound.play()
            self.score = self.score + 10
            self.scoreboard.updateDisplay(self.score, self.balls_used)

        if self.bumped_round_bumper(geom1, geom2, body1, body2):
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            self.jump_sound.play()
            self.score = self.score + 300
            self.scoreboard.updateDisplay(self.score, self.balls_used)

        if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.pipe_geom) and self.table.ball_not_sinking:
            self.score = self.score + 200
            self.scoreboard.updateDisplay(self.score, self.balls_used)
            self.jump_sound.play()
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            if self.table.ball.getZ() > .48 :
                self.table.ball_not_sinking = False
        # check for ball sink task
        if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.ball_stopper_geom) and self.table.ball_not_sinking:
            self.table.ball_not_sinking = False
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            self.lasor_cannon.play()
            self.scoreboard.updateDisplay(self.score, self.balls_used)

        if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.lower_wall_triangle):
            self.score = self.score + 100
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            self.jump_sound.play()
            self.scoreboard.updateDisplay(self.score, self.balls_used)

        if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.upper_wall_triangle):
            self.score = self.score + 100
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            self.jump_sound.play()
            self.scoreboard.updateDisplay(self.score, self.balls_used)

        if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.upper_launch_wall):
            self.score = self.score + 100
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            self.jump_sound.play()
            self.scoreboard.updateDisplay(self.score, self.balls_used)

        if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.lower_launch_wall):
            self.score = self.score + 100
            #os.system('sudo mpg123 -q audio/jump.mp3 &')
            self.jump_sound.play()
            self.scoreboard.updateDisplay(self.score, self.balls_used)

    def bumped_by_ball(self, geom1, geom2, body1, body2, geomOfInterest):
        if (
            (
                geom1 and geom1 == geomOfInterest) and (
                (body1 and body1 == self.table.ball_body) or (
                body2 and body2 == self.table.ball_body))) or (
                    (geom2 and geom2 == geomOfInterest) and (
                        (body1 and body1 == self.table.ball_body) or (
                            body2 and body2 == self.table.ball_body))):
            return True
        return False

    def bumped_by_ball2(self, body1, body2, bodyOfInterest):
        if  ((body2 and body2 == bodyOfInterest) and
                (body1 and body1 == self.table.ball_body)) or (
                    (body1 and body1 == bodyOfInterest) and
                            (body2 and body2 == self.table.ball_body)):
            return True
        return False

    def bumped_triangle_bumper(self, geom1, geom2, body1, body2):
        # if you bump the left pink triangle
        one = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.tl_l_wall)
        two = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.tl_rb_wall)
        three = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.tl_rt_wall)
        # if you bump the right pink triangle
        four = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.tr_r_wall)
        five = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.tr_lb_wall)
        six = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.tr_rt_wall)
        if one or two or three or four or five or six:
            return True
        else:
            return False

    def bumped_round_bumper(self, geom1, geom2, body1, body2):
        # if you bump the left pink triangle
        one = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.round_bumper_left_geom)
        two = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.round_bumper_right_geom)
        three = self.bumped_by_ball(
            geom1, geom2, body1, body2, self.table.tall_round_bumper_geom)
        if one or two or three:
            return True
        else:
            return False

    def bumped_by_flipper(self, geom1, geom2, body1, body2):
        one = self.bumped_by_ball2(body1, body2, self.table.flipper_body_right)
        two = self.bumped_by_ball2(body1, body2, self.table.flipper_body_left)
        if one:
            return 0
        if two:
            return 1

    #button down task
    def start_button_launch(self, task):
        if GPIO.input(25) == False:
            messenger.send("button_build_force")
            taskMgr.doMethodLater(0, self.wait_for_plunger_release, 'wait_for_plunger_release')
            taskMgr.remove('start_button_launch')
        return task.cont

    #button up task
    def wait_for_plunger_release(self,task):
        #checks for when the launch button is released
        if GPIO.input(25) == True:
            messenger.send("button_launch")
            taskMgr.remove('wait_for_plunger_release')
        return task.cont

    def start_bump_ball_task(self, task):
        # print "start trigger miss task"
        self.table.space1.setCollisionEvent("bump_event")
        # print self.table.space1.getCollisionEvent()
        base.accept("bump_event", self.bump_ball_event)

    def listen_for_enter(self, task):
        # import RPi.GPIO as GPIO
        if GPIO.input(25) == False:
            messenger.send("button_enter")
            taskMgr.remove('listen_for_enter')
        return task.cont

    def listen_for_input(self, task):
        #this task is meant to work with the landing_screen
        #it is how we communicate between the landing screen and the game class
        if self.button_enabled:
            if GPIO.input(21) == False:
                #left down decrement
                self.landing_screen.left_down_decrement()
            if GPIO.input(12) == False:
                #right down increment
                self.landing_screen.right_down_increment()
            if GPIO.input(25) == False:
                self.landing_screen.enter_username()

        if self.landing_screen.finished_entering:
            # print "removing task for landing screen"
            taskMgr.remove('listen_for_input')
            self.finish_start()
        return task.cont

    def lose_ball(self):
        # print "lost ball"
        self.balls_used = self.balls_used + 1
        if self.balls_used >= self.max_balls:
            #display lost game until someone hits launch button,
            #then take them to the landing screen.
            #then don't restart the game until they go through the landing_screen
            self.scoreboard.displayLostGame(self.score)
            self.landing_screen.write_final_score(self.score)
            if self.button_enabled:
                base.acceptOnce('button_enter', self.restart)
                taskMgr.doMethodLater(
                    0,
                    self.listen_for_enter,
                    'listen_for_enter')
            else:
                base.acceptOnce('enter', self.restart)
            return()
        self.place_ball()
        self.scoreboard.updateDisplay(self.score, self.balls_used)
