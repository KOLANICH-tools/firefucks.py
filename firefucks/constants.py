from pathlib import Path, PurePath

__all__ = ("omniJaLinuxPath", "appConstraintsInternalPath")

omniJaLinuxPath = Path("/usr/lib/firefox/omni.ja")
appConstraintsInternalPath = PurePath("modules/AppConstants.jsm")
