import typing
from pathlib import Path, PurePath

import esprima
import escodegen
from esprima.nodes import Script
from libzip.Archive import Archive
from libzip.enums import OpenFlags
from libzip.Source import Source

from .constants import appConstraintsInternalPath, omniJaLinuxPath
from .json import json
from .patcher import patchAppConstants

# pylint:disable=too-few-public-methods

__all__ = ("PatchingPipeline", "DEFAULT_PRESET")

thisDir = Path(__file__).absolute().parent
presetFile = thisDir / "preset.json"
DEFAULT_PRESET = json.loads(presetFile.read_text())


class InternalPaths:
	__slots__ = ("appConstraints",)

	def __init__(self, appConstraints: PurePath = appConstraintsInternalPath) -> None:
		self.appConstraints = appConstraints


class Paths:
	__slots__ = ("root", "internal")

	def __init__(self, root: Path, internal: InternalPaths = None) -> None:
		self.root = root
		if internal is None:
			internal = InternalPaths()

		self.internal = internal


class PathsPair:
	__slots__ = ("root", "internal")

	def __init__(self, root: Path, internal: PurePath) -> None:
		self.root = root
		self.internal = internal


class DestinationBackend:
	__slots__ = ()

	def getFileText(self, pp: PathsPair) -> str:
		raise NotImplementedError

	def writeBack(self, pp: PathsPair, source: str) -> None:
		raise NotImplementedError

	@classmethod
	def make(cls, patchee: Paths) -> "DestinationBackend":
		if patchee.root.is_dir():
			return DirDestinationBackend()
		return ArchiveDestinationBackend()


class DirDestinationBackend(DestinationBackend):
	__slots__ = ()

	def getFileText(self, pp: PathsPair) -> str:
		return (pp.root / pp.internal).read_text()

	def writeBack(self, pp: PathsPair, source: str) -> None:
		(pp.root / pp.internal).write_text(source)


class ArchiveDestinationBackend(DestinationBackend):
	__slots__ = ()

	def getFileText(self, pp: PathsPair) -> str:
		with Archive(pp.root, OpenFlags.read_only | OpenFlags.check) as a:
			f = a[pp.internal]
			appConstsText = bytes(f.stat.originalSize)
			with f as of:
				of.read(appConstsText)
			return appConstsText.decode("utf-8")

	def writeBack(self, pp: PathsPair, source: str) -> None:
		with Archive(pp.root, OpenFlags.read_write | OpenFlags.check) as a:
			f = a[pp.internal]
			s = Source.make(source.encode("utf-8"))
			f.replace(s)


class ParsedAST:
	__slots__ = ("ast", "pp")

	def __init__(self, pp: PathsPair) -> None:
		self.pp = pp
		self.ast = None

	def load(self, destinationBackend: DestinationBackend) -> None:
		source = destinationBackend.getFileText(self.pp)
		self.ast = self.parse(source)

	def dump(self, destinationBackend: DestinationBackend) -> None:
		res = self.serialize(esprima.toDict(self.ast))
		destinationBackend.writeBack(self.pp, res)

	def parse(self, source):
		raise NotImplementedError

	def serialize(self, source):
		raise NotImplementedError


class JSParsedAST(ParsedAST):
	__slots__ = ()

	def parse(self, source: str) -> Script:
		return esprima.parse(source, {"comment": True})

	def serialize(self, source: typing.Dict) -> str:
		return escodegen.generate(esprima.toDict(self.ast))


class PatchingPipeline:
	__slots__ = ("preset", "patchee", "destinationBackend", "appConsts", "unpatchedProps")

	appConstraintsInternalPath = appConstraintsInternalPath

	def __init__(self, preset: typing.Dict[str, bool], patchee: typing.Union[Paths, Path], destinationBackend: typing.Optional[DestinationBackend] = None) -> None:
		self.preset = preset
		if not isinstance(patchee, Paths):
			patchee = Paths(patchee)

		self.patchee = patchee
		if destinationBackend is None:
			destinationBackend = DestinationBackend.make(patchee)
		self.destinationBackend = destinationBackend
		self.appConsts = JSParsedAST(PathsPair(patchee.root, patchee.internal.appConstraints))
		self.unpatchedProps = None

	def __call__(self) -> typing.Dict[typing.Any, typing.Any]:
		self.load()
		self.patch()
		self.dump()
		return self.unpatchedProps

	def load(self) -> None:
		self.appConsts.load(self.destinationBackend)

	def patch(self) -> None:
		self.unpatchedProps = patchAppConstants(self.appConsts.ast, self.preset)

	def dump(self) -> None:
		self.appConsts.dump(self.destinationBackend)
