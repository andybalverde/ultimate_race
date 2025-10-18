from pathlib import Path
from panda3d.core import loadPrcFile, loadPrcFileData, Filename, ClockObject
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld

from engine.inputmap import InputMap
from engine.camera import ChaseCamera
from game.player import Player

class App(ShowBase):
    def __init__(self):
        # PRC setup
        prc = Filename.from_os_specific(str(Path("config/panda.prc").resolve()))
        loadPrcFile(prc)
        loadPrcFileData("", "default-near 0.5\n")

        super().__init__()
        self.disableMouse()
        self.render.setShaderAuto()

        self.clock = ClockObject.getGlobalClock()

        # Physics world placeholder (for later 5-ray + colliders)
        self.bworld = BulletWorld()
        self.bworld.setGravity((0, 0, -9.81))

        # Input + player
        self.input = InputMap(self)
        self.player = Player(self, self.input)

        # Camera
        self.camera_sys = ChaseCamera(self, self.player.car)

        # main loop hook
        self.taskMgr.add(self._update, "engine_update")

    def _update(self, task):
        dt = min(self.clock.getDt(), 1/30)
        self.camera_sys.apply_inputs(self.input, dt)
        self.camera_sys.update(dt)
        self.bworld.doPhysics(dt, 4, dt / 4.0)
        return task.cont
