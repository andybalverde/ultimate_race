from pathlib import Path
from panda3d.core import Filename

# Project roots
ROOT  = Path(__file__).resolve().parents[1]  # .../engine → project root
MEDIA = ROOT / "media"

# Utility: Panda3D-friendly path
def p3(path: Path) -> str:
    return Filename.from_os_specific(str(path)).get_fullpath()

# ---- Track registry ----------------------------------------------------------
# Each entry defines:
#   id: stable key
#   name: UI title
#   img: preview jpg
#   model: circuit .glb
# Default spawn/scale live in constants.TRACK_DEFAULTS (so you can bake new values later)
TRACKS = [
    {
        "id": "usa_spielberg",
        "name": "USA — Spielberg",
        "img": MEDIA / "tracks" / "usa" / "usa.jpg",
        "model": MEDIA / "tracks" / "usa" / "cartoon_race_track_spielberg.glb",
    },
    {
        "id": "bahrain",
        "name": "Bahrain",
        "img": MEDIA / "tracks" / "bahrain" / "bahrain.jpg",
        "model": MEDIA / "tracks" / "bahrain" / "f1_bahrain_lowpoly_circuit.glb",
    },
    {
        "id": "bermudas",
        "name": "Bermudas",
        "img": MEDIA / "tracks" / "bermudas" / "bermudas.jpg",
        "model": MEDIA / "tracks" / "bermudas" / "free_fire_burmuda_map_the_circuit_3d_model.glb",
    },
    {
        "id": "scotland",
        "name": "Scotland",
        "img": MEDIA / "tracks" / "scotland" / "scotland.jpg",
        "model": MEDIA / "tracks" / "scotland" / "endurance_run.glb",
    },
]

# Car model (unchanged)
TESLA = MEDIA / "tesla_model_s_plaid_2023.glb"
