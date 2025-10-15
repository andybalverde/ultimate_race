from pathlib import Path
from panda3d.core import Filename

ROOT  = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"

TRACK = MEDIA / "tracks" / "usa" / "cartoon_race_track_spielberg.glb"
TESLA = MEDIA / "tesla_model_s_plaid_2023.glb"

def p3(path: Path) -> str:
    return Filename.from_os_specific(str(path)).get_fullpath()
