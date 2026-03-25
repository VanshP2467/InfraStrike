from pathlib import Path

# Folder containing the infrastrike package (src/infrastrike)
BASE_DIR = Path(__file__).resolve().parent

def asset_path(*parts) -> Path:
    """
    Build an absolute path to an asset inside src/infrastrike/assets/.

    Example:
        asset_path("images", "start_bg.png")
    """
    return BASE_DIR.joinpath("assets", *parts)