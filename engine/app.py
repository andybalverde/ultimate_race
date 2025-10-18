from pathlib import Path
from panda3d.core import loadPrcFile, loadPrcFileData, Filename, ClockObject, TextNode
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletWorld

from engine.inputmap import InputMap
from engine.camera import ChaseCamera
from engine.assets import TRACKS, p3
from constants import TRACK_DEFAULTS
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

        # Bullet world
        self.bworld = BulletWorld()
        self.bworld.setGravity((0, 0, -9.81))

        # State
        self._scene = None           # "menu" or "race"
        self._menu_idx = 0
        self._menu_nodes = []

        # Boot to the menu
        self._enter_menu()

    # ===================== MENU =====================
    def _enter_menu(self):
        self._scene = "menu"

        # Background preview image (centered)
        sel = TRACKS[self._menu_idx]
        self._menu_preview = OnscreenImage(image=p3(sel["img"]), pos=(0, 0, 0), scale=(1.2, 1, 0.68))
        self._menu_nodes.append(self._menu_preview)

        # Title
        self._menu_title = OnscreenText(
            text=sel["name"], pos=(0, 0.80), scale=0.08,
            fg=(1, 1, 1, 1), align=TextNode.ACenter, mayChange=True, shadow=(0, 0, 0, 0.8)
        )
        self._menu_nodes.append(self._menu_title)

        # Instructions
        self._menu_help = OnscreenText(
            text="← / →  choose circuit     Enter  start",
            pos=(0, -0.85), scale=0.05, fg=(1, 1, 1, 1),
            align=TextNode.ACenter, shadow=(0, 0, 0, 0.8)
        )
        self._menu_nodes.append(self._menu_help)

        # Key bindings just for the menu
        self.accept("arrow_left",  self._menu_prev)
        self.accept("arrow_right", self._menu_next)
        self.accept("enter",       self._menu_select)
        self.accept("return",      self._menu_select)

    def _menu_refresh(self):
        sel = TRACKS[self._menu_idx]
        self._menu_preview.setImage(p3(sel["img"]))
        self._menu_title.setText(sel["name"])

    def _menu_prev(self):
        self._menu_idx = (self._menu_idx - 1) % len(TRACKS)
        self._menu_refresh()

    def _menu_next(self):
        self._menu_idx = (self._menu_idx + 1) % len(TRACKS)
        self._menu_refresh()

    def _cleanup_menu(self):
        for n in self._menu_nodes:
            n.removeNode()
        self._menu_nodes.clear()
        self.ignore("arrow_left")
        self.ignore("arrow_right")
        self.ignore("enter")
        self.ignore("return")

    def _menu_select(self):
        self._cleanup_menu()
        self._enter_race(TRACKS[self._menu_idx])

    # ===================== RACE =====================
    def _enter_race(self, track_def):
        self._scene = "race"

        # Input + player
        self.input = InputMap(self)
        defaults = TRACK_DEFAULTS.get(track_def["id"], TRACK_DEFAULTS["usa_spielberg"])
        self.player = Player(self, self.input, track_def, defaults)

        # Camera
        self.camera_sys = ChaseCamera(self, self.player.car)

        # main loop hook
        if not hasattr(self, "_task_added"):
            self.taskMgr.add(self._update, "engine_update")
            self._task_added = True

    def _update(self, task):
        dt = min(self.clock.getDt(), 1/30)
        # Only when in race
        if self._scene == "race":
            self.camera_sys.apply_inputs(self.input, dt)
            self.camera_sys.update(dt)
            self.bworld.doPhysics(dt, 4, dt / 4.0)
        return task.cont
