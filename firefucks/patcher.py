import typing

import esprima
from esprima.nodes import CallExpression, Literal, ObjectExpression, Script, StaticMemberExpression

from .json import json


def isPropParent(cand: StaticMemberExpression, pathComp: str) -> bool:
	if pathComp == "this":

		def objPred0(o):
			return o.type == "ThisExpression"

	else:

		def objPred0(o):
			return o.type == "Identifier" and o.name == pathComp

	return cand.type == "MemberExpression" and objPred0(cand.object)


def isPropChild(cand: StaticMemberExpression, pathComp: str) -> bool:
	p = cand.property
	return p.type == "Identifier" and p.name == pathComp


def isProp2(cand: StaticMemberExpression, pathComp0: str, pathComp1: str) -> bool:
	return isPropParent(cand, pathComp0) and isPropChild(cand, pathComp1)


def findThisAssignmentPropInProgram(progNode: Script, propsToFind: set, op: str = "=") -> typing.Dict[str, CallExpression]:
	assert progNode.type == "Program"
	res = {}
	for assignmentExprCand1 in progNode.body:
		if assignmentExprCand1 and assignmentExprCand1.type == "ExpressionStatement":
			assignmentExprCand = assignmentExprCand1.expression
			if assignmentExprCand and assignmentExprCand.type == "AssignmentExpression" and assignmentExprCand.operator == op:
				lhs = assignmentExprCand.left
				if isPropParent(lhs, "this"):
					p = lhs.property
					if p.type == "Identifier" and p.name in propsToFind:
						res[p.name] = assignmentExprCand.right
	return res


def literal2ast(v: bool) -> Literal:
	return esprima.parse(json.dumps(v)).body[0].expression


def patchDictExpr(dictExpr: ObjectExpression, patch: dict) -> typing.Dict[typing.Any, typing.Any]:
	patch = type(patch)(patch)
	for cand in dictExpr.properties:
		if cand.key.type == "Identifier" and cand.key.name in patch:
			try:
				replacementVal = patch[cand.key.name]
			except KeyError:
				continue
			else:
				targetP = cand
				targetP.value = literal2ast(replacementVal)
				del patch[cand.key.name]
				if not patch:
					break
	return patch


def patchAppConstants(res: Script, patch: typing.Dict[str, bool]) -> typing.Dict[typing.Any, typing.Any]:
	appConstantsExpr = findThisAssignmentPropInProgram(res, {"AppConstants"})["AppConstants"]
	if isProp2(appConstantsExpr.callee, "Object", "freeze"):
		aS = appConstantsExpr.arguments
		if aS:
			appConstantsExpr = aS[0]  # unfrozen expression

	if appConstantsExpr.type == "ObjectExpression":
		return patchDictExpr(appConstantsExpr, patch)

	raise ValueError("this.AppConstants is assigned with wrong thing:", appConstantsExpr)
