"""
Undoable Maya API 2.0 command for fast bulk mesh vertex updates.

Used by takTools.utils.sym_mesh to apply MFnMesh.setPoints() in milliseconds
while preserving full Maya Undo/Redo support.
"""

import sys
import uuid
from maya.api import OpenMaya as om


def maya_useNewAPI():
    """Declare OpenMaya 2.0 API usage to Maya."""
    pass


CMD_NAME = "symMeshSetPoints"


def get_payload_store():
    """Return process-wide transient store shared with takTools.utils.sym_mesh."""
    store = getattr(sys, "_sym_mesh_payloads", None)
    if store is None:
        store = {}
        sys._sym_mesh_payloads = store
    return store


def register_payload(points, space=om.MSpace.kObject):
    """Store vertex points payload and return a unique token key."""
    key = uuid.uuid4().hex
    get_payload_store()[key] = (points, space)
    return key


def clear_payload(key):
    """Remove unused payload if command invocation failed before doIt."""
    get_payload_store().pop(key, None)


class SymMeshSetPointsCmd(om.MPxCommand):
    """Undoable command that applies bulk MFnMesh.setPoints."""

    def __init__(self):
        super(SymMeshSetPointsCmd, self).__init__()
        self._dag_path = None
        self._space = om.MSpace.kObject
        self._old_points = None
        self._new_points = None

    def isUndoable(self):
        return True

    def doIt(self, args):
        if len(args) < 2:
            raise RuntimeError("Usage: symMeshSetPoints <mesh> <payloadKey>")

        mesh_name = args.asString(0)
        key = args.asString(1)

        payload = get_payload_store().pop(key, None)
        if payload is None:
            raise RuntimeError("No pending vertex payload found for key: {}".format(key))

        new_points, space = payload

        sel_list = om.MSelectionList()
        sel_list.add(mesh_name)
        dag_path = sel_list.getDagPath(0)
        dag_path.extendToShape()

        fn_mesh = om.MFnMesh(dag_path)
        self._dag_path = dag_path
        self._space = space
        self._old_points = fn_mesh.getPoints(space)
        self._new_points = new_points

        self.redoIt()

    def redoIt(self):
        if self._dag_path is None or self._new_points is None:
            return
        fn_mesh = om.MFnMesh(self._dag_path)
        fn_mesh.setPoints(self._new_points, self._space)

    def undoIt(self):
        if self._dag_path is None or self._old_points is None:
            return
        fn_mesh = om.MFnMesh(self._dag_path)
        fn_mesh.setPoints(self._old_points, self._space)


def _cmd_creator():
    return SymMeshSetPointsCmd()


def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin, "takTools", "1.0", "Any")
    plugin_fn.registerCommand(CMD_NAME, _cmd_creator)


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    plugin_fn.deregisterCommand(CMD_NAME)
