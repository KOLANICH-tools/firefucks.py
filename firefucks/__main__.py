import argparse
from pathlib import Path

from . import DEFAULT_PRESET, PatchingPipeline
from .constants import omniJaLinuxPath


def main() -> None:
	p = argparse.ArgumentParser(prog=None, usage=None, description="A patcher to make Firefox into allowing unsigned addons.", exit_on_error=False)
	p.add_argument(dest="path", metavar="<omni.ja contents path>", default="./omni.ja", type=Path, help="The path to `" + str(omniJaLinuxPath) + "` archive or unpacked dir")
	args = p.parse_args()
	pl = PatchingPipeline(DEFAULT_PRESET, args.path)
	unpatched = pl()
	print("unpatched", unpatched)


if __name__ == "__main__":
	main()
