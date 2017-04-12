from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdeSphereGeom, OdePlaneGeom
from panda3d.core import BitMask32, Vec4, Quat, VBase3
from panda3d.core import Light, AmbientLight, DirectionalLight
import sys

from table import Table
from scoreboard import Scoreboard

class Game():

    def __init__(self):
        base.disableMouse()
        base.accept("escape", sys.exit)  # Escape quits
        self.max_balls = 3
        self.balls_used = 0
        self.score = 0
        self.table = Table()

    def start(self):
        self.scoreboard = Scoreboard(
            self.score, self.max_balls, self.balls_used)
        self.place_ball()
        base.run()

    def restart(self):
        self.reset_score()
        self.scoreboard.text_object.destroy()
        self.scoreboard = Scoreboard(
            self.score, self.max_balls, self.balls_used)
        self.place_ball()

    def place_ball(self):
        self.table.ball.setPos(4.4, 2.85, 0.1)
        self.table.ball_body.setPosition(self.table.ball.getPos(render))
        self.table.ball_body.setQuaternion(self.table.ball.getQuat(render))
        base.acceptOnce('space', self.launch_ball)

    def reset_score(self):
        self.balls_used = 0
        self.score = 0

    def launch_ball(self):
        self.start_gravity_task()
        base.accept('a', self.table.move_left_flipper)
        base.accept('a-up', self.table.stop_left_flipper)

        base.accept('d', self.table.move_right_flipper)
        base.accept('d-up', self.table.stop_right_flipper)

        print "called"
        taskMgr.doMethodLater(
            0,
            self.table.launch_ball_task,
            'launch_ball')
        taskMgr.doMethodLater(
            1,
            self.table.stop_launch_ball_task,
            'stop_launch_ball')
        taskMgr.doMethodLater(
            0.5,
            self.start_bump_ball_task,
            'bump_ball_task')

    def start_gravity_task(self):
        taskMgr.add(self.table.gravity_task, 'gravity_task')

    def remove_gravity_task(self):
        taskMgr.remove('gravity_task')

    def bump_ball_event(self, entry):
        geom1 = entry.getGeom1()
        geom2 = entry.getGeom2()
        body1 = entry.getBody1()
        body2 = entry.getBody2()
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
            self.score = self.score + 10
            self.scoreboard.updateDisplay(self.score, self.balls_used)
        if self.bumped_round_bumper(geom1, geom2, body1, body2):
            self.score = self.score + 50
            self.scoreboard.updateDisplay(self.score, self.balls_used)
        if self.bumped_by_ball(geom1, geom2, body1, body2, self.table.pipe_geom):
            print 'ball has been bumped'
            self.score = self.score + 200
            self.scoreboard.updateDisplay(self.score, self.balls_used)
            if self.balls_used  > 0:
                self.balls_used = self.balls_used  - 1
                self.place_ball()

    def bumped_by_ball(self, geom1, geom2, body1, body2, geomOfInterest):
        if (
            (
                geom1 and geom1 == geomOfInterest ) and (
                (body1 and body1 == self.table.ball_body) or (
                body2 and body2 == self.table.ball_body))) or (
                    (geom2 and geom2 == geomOfInterest) and (
                        (body1 and body1 == self.table.ball_body) or (
                            body2 and body2 == self.table.ball_body))):
            return True
        return False

    def bumped_triangle_bumper(self, geom1, geom2, body1, body2):
        #if you bump the left pink triangle
        one = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.tl_l_wall)
        two = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.tl_rb_wall)
        three = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.tl_rt_wall)
        #if you bump the right pink triangle
        four = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.tr_r_wall)
        five = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.tr_lb_wall)
        six = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.tr_rt_wall)
        if one or two or three or four or five or six:
            return True
        else:
            return False

    def bumped_round_bumper(self, geom1, geom2, body1, body2):
        #if you bump the left pink triangle
        one = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.round_bumper_left_geom)
        two = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.round_bumper_right_geom)
        three = self.bumped_by_ball(geom1, geom2, body1, body2, self.table.tall_round_bumper_geom)
        if one or two or three:
            return True
        else:
            return False

    def start_bump_ball_task(self, task):
        print "start trigger miss task"
        self.table.space1.setCollisionEvent("bump_event")
        print self.table.space1.getCollisionEvent()
        base.accept("bump_event", self.bump_ball_event)

    def lose_ball(self):
        print "lost ball"
        self.balls_used = self.balls_used + 1
        if self.balls_used >= self.max_balls:
            self.scoreboard.displayLostGame(self.score, self.balls_used)
            base.acceptOnce('enter', self.restart)
            return()
        self.place_ball()
        self.scoreboard.updateDisplay(self.score, self.balls_used)