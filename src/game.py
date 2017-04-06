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
        self.max_balls = 1
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
        # self.table.ball.setPos(-3.2, -0.3426, 0.6)
        # self.ball.setPos(0,0,0.1)
        # self.ball.setPos(0,0,2.12)
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
            self.start_trigger_miss_task,
            'trigger_miss_task')

    def start_gravity_task(self):
        taskMgr.add(self.table.gravity_task, 'gravity_task')

    def remove_gravity_task(self):
        taskMgr.remove('gravity_task')

    def trigger_miss_event(self, entry):
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
            print 'collision has happened'
            self.remove_gravity_task()
            self.lose_ball()

    def start_trigger_miss_task(self, task):
        print "start trigger miss task"
        self.table.space1.setCollisionEvent("trigger_miss")
        base.accept("trigger_miss", self.trigger_miss_event)

    def lose_ball(self):
        self.balls_used = self.balls_used + 1
        if self.balls_used >= self.max_balls:
            self.scoreboard.displayLostGame(self.score, self.balls_used)
            base.acceptOnce('enter', self.restart)
            return()
        self.scoreboard.updateDisplay(self.score, self.balls_used)