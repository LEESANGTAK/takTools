"""
Fast symmetry mapping and mesh mirror/flip/revert/blendshape operations
powered by Maya OpenMaya API 2.0 and NumPy.

Supports Maya Transfer-Attributes-style sample spaces:
- World
- Local
- UV
- Topology (seeded by center seam edge(s), with optional fallback for detached shells)
"""

from collections import deque
from dataclasses import dataclass, field
import itertools
import os
import sys
import time
import uuid

import numpy as np
from maya import cmds
from maya.api import OpenMaya as om

try:
    from scipy.spatial import cKDTree as _SciPyKDTree
except ImportError:
    _SciPyKDTree = None


SAMPLE_WORLD = "world"
SAMPLE_LOCAL = "local"
SAMPLE_UV = "uv"
SAMPLE_TOPOLOGY = "topology"

VALID_SAMPLE_SPACES = (SAMPLE_WORLD, SAMPLE_LOCAL, SAMPLE_UV, SAMPLE_TOPOLOGY)

AXIS_X = 0
AXIS_Y = 1
AXIS_Z = 2
AXIS_NAMES = {AXIS_X: "X", AXIS_Y: "Y", AXIS_Z: "Z"}

ORIGIN_ZERO = "origin"
ORIGIN_PIVOT = "pivot"
ORIGIN_BBOX = "bbox"

_PLUGIN_NAME = "symMeshCmd.py"
_PLUGIN_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "plug-ins", _PLUGIN_NAME)
).replace("\\", "/")


@dataclass
class SymmetryData:
    """Cached symmetry correspondence table for a base mesh."""

    base_mesh: str
    base_shape: str
    num_verts: int
    sample_space: str
    axis: int
    origin_mode: str
    base_mid: float
    tolerance: float
    sym_table: np.ndarray
    side_table: np.ndarray
    uv_set: str = ""
    uv_axis: int = 0
    uv_center: float = 0.5
    seed_edges: list = field(default_factory=list)
    elapsed_ms: float = 0.0
    notes: str = ""

    @property
    def pos_indices(self):
        return np.flatnonzero(self.side_table == 1).astype(np.int32)

    @property
    def neg_indices(self):
        return np.flatnonzero(self.side_table == -1).astype(np.int32)

    @property
    def center_indices(self):
        return np.flatnonzero(self.side_table == 0).astype(np.int32)

    @property
    def unmatched_indices(self):
        return np.flatnonzero(self.sym_table == -1).astype(np.int32)

    @property
    def paired_count(self):
        return int(np.count_nonzero((self.sym_table >= 0) & (self.side_table != 0))) // 2

    @property
    def center_count(self):
        return int(np.count_nonzero(self.side_table == 0))

    @property
    def unmatched_count(self):
        return int(np.count_nonzero(self.sym_table == -1))

    @property
    def is_symmetrical(self):
        return self.unmatched_count == 0


# ---------------------------------------------------------------------------
# Maya Mesh & Selection Helpers
# ---------------------------------------------------------------------------

def get_mesh_dag_paths(mesh_name):
    """Return (transform_dag_path, shape_dag_path) for a mesh transform or shape."""
    if not cmds.objExists(mesh_name):
        raise ValueError("Mesh does not exist: {}".format(mesh_name))

    sel = om.MSelectionList()
    sel.add(mesh_name)
    dag = sel.getDagPath(0)

    if dag.apiType() == om.MFn.kMesh:
        shape_dag = om.MDagPath(dag)
        transform_dag = om.MDagPath(dag)
        transform_dag.pop()
        return transform_dag, shape_dag

    transform_dag = om.MDagPath(dag)
    shape_dag = om.MDagPath(dag)
    num_shapes = shape_dag.numberOfShapesDirectlyBelow()
    for i in range(num_shapes):
        cand = om.MDagPath(dag)
        cand.extendToShape(i)
        if cand.apiType() == om.MFn.kMesh:
            fn_dag = om.MFnDagNode(cand)
            if not fn_dag.isIntermediateObject:
                return transform_dag, cand

    raise ValueError("No non-intermediate polygon mesh shape found on: {}".format(mesh_name))


def get_transform_name(mesh_name):
    """Return partial transform name for a mesh or shape."""
    transform_dag, _ = get_mesh_dag_paths(mesh_name)
    return transform_dag.partialPathName()


def get_mesh_points_np(mesh_name, space=om.MSpace.kObject):
    """Read all vertex positions as an (N, 3) float64 numpy array."""
    _, shape_dag = get_mesh_dag_paths(mesh_name)
    fn_mesh = om.MFnMesh(shape_dag)
    pts = fn_mesh.getPoints(space)
    if len(pts) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    return np.asarray(pts, dtype=np.float64)[:, :3].copy()


def _ensure_set_points_plugin():
    """Load the symMeshCmd undoable command plugin if available."""
    if cmds.pluginInfo("symMeshCmd", q=True, loaded=True):
        return True
    if os.path.isfile(_PLUGIN_PATH):
        try:
            cmds.loadPlugin(_PLUGIN_PATH, quiet=True)
            return True
        except Exception:
            return False
    try:
        cmds.loadPlugin("symMeshCmd", quiet=True)
        return True
    except Exception:
        return False


def _register_plugin_payload(points, space):
    store = getattr(sys, "_sym_mesh_payloads", None)
    if store is None:
        store = {}
        sys._sym_mesh_payloads = store
    key = uuid.uuid4().hex
    store[key] = (points, space)
    return key


def _clear_plugin_payload(key):
    store = getattr(sys, "_sym_mesh_payloads", None)
    if store is not None:
        store.pop(key, None)


def set_mesh_points_np(mesh_name, points_np, space=om.MSpace.kObject, undoable=True):
    """Write an (N, 3) numpy array back to the mesh, undoable by default."""
    _, shape_dag = get_mesh_dag_paths(mesh_name)
    fn_mesh = om.MFnMesh(shape_dag)
    num_verts = fn_mesh.numVertices
    if points_np.shape != (num_verts, 3):
        raise ValueError(
            "Expected points shape ({}, 3), got {}".format(num_verts, points_np.shape)
        )

    # MFnMesh.setPoints in kWorld can fail or skip DG updates on some Maya versions when transformed;
    # converting world points into object space guarantees reliable updates.
    write_pts = points_np
    write_space = om.MSpace.kObject
    if space == om.MSpace.kWorld:
        inv_mat = np.array(shape_dag.inclusiveMatrixInverse(), dtype=np.float64).reshape(4, 4)
        ones = np.ones((num_verts, 1), dtype=np.float64)
        hom = np.hstack((points_np, ones))
        write_pts = (hom @ inv_mat)[:, :3]

    if not undoable:
        mp_arr = om.MPointArray(write_pts.tolist())
        fn_mesh.setPoints(mp_arr, write_space)
        return

    if _ensure_set_points_plugin() and hasattr(cmds, "symMeshSetPoints"):
        mp_arr = om.MPointArray(write_pts.tolist())
        key = _register_plugin_payload(mp_arr, write_space)
        try:
            cmds.symMeshSetPoints(shape_dag.fullPathName(), key)
            return
        except Exception:
            _clear_plugin_payload(key)

    # Pure-cmds undoable fallback when plugin cannot be loaded.
    shape_name = shape_dag.fullPathName()
    has_history = bool(cmds.listConnections("{}.inMesh".format(shape_name), s=True, d=False))
    if not has_history:
        cmds.setAttr("{}.vt[0:{}]".format(shape_name, num_verts - 1), *write_pts.ravel().tolist())
    else:
        old_pts = get_mesh_points_np(shape_name, space=om.MSpace.kObject)
        existing_pnts = np.asarray(
            cmds.getAttr("{}.pnts[0:{}]".format(shape_name, num_verts - 1)), dtype=np.float64
        )
        new_pnts = existing_pnts + (write_pts - old_pts)
        cmds.setAttr("{}.pnts[0:{}]".format(shape_name, num_verts - 1), *new_pnts.ravel().tolist())


def get_mirror_mid(mesh_name, axis, sample_space, origin_mode, points_np=None):
    """Compute the mirror plane coordinate along `axis` in the active evaluation space."""
    if origin_mode == ORIGIN_ZERO:
        return 0.0

    if origin_mode == ORIGIN_BBOX:
        if points_np is None:
            space = om.MSpace.kWorld if sample_space == SAMPLE_WORLD else om.MSpace.kObject
            points_np = get_mesh_points_np(mesh_name, space=space)
        if len(points_np) == 0:
            return 0.0
        return float(0.5 * (points_np[:, axis].min() + points_np[:, axis].max()))

    # ORIGIN_PIVOT
    transform_name = get_transform_name(mesh_name)
    if sample_space == SAMPLE_WORLD:
        piv = cmds.xform(transform_name, q=True, ws=True, rp=True)
    else:
        piv = cmds.xform(transform_name, q=True, os=True, rp=True)
    return float(piv[axis])


def get_uv_sets(mesh_name):
    """Return list of UV set names on the mesh."""
    _, shape_dag = get_mesh_dag_paths(mesh_name)
    fn_mesh = om.MFnMesh(shape_dag)
    return list(fn_mesh.getUVSetNames() or [])


def get_current_uv_set(mesh_name):
    """Return active UV set name on the mesh."""
    _, shape_dag = get_mesh_dag_paths(mesh_name)
    fn_mesh = om.MFnMesh(shape_dag)
    return fn_mesh.currentUVSetName()


def resolve_selection():
    """Inspect active Maya selection.

    Returns:
        tuple: (mesh_transform_name_or_None, selected_vertex_indices_np_or_None, error_msg_or_None)
        If whole mesh transform/shape is selected, indices is None.
        If components (vertices, edges, faces) on a single mesh are selected, indices is an int32 array.
    """
    sel = cmds.ls(sl=True, fl=False) or []
    if not sel:
        return None, None, "Nothing selected."

    meshes = cmds.filterExpand(sel, sm=12) or []
    if len(meshes) > 1:
        return None, None, "Select only one polygon object."
    if len(meshes) == 1:
        return get_transform_name(meshes[0]), None, None

    # Component mode
    hilited = cmds.ls(hilite=True) or []
    mesh_hilited = []
    for node in hilited:
        try:
            mesh_hilited.append(get_transform_name(node))
        except ValueError:
            pass
    mesh_hilited = list(dict.fromkeys(mesh_hilited))

    if len(mesh_hilited) == 0:
        # Components might have been selected without hilite list if selected directly by script
        objs = list(dict.fromkeys(cmds.ls(sel, objectsOnly=True) or []))
        for obj in objs:
            try:
                mesh_hilited.append(get_transform_name(obj))
            except ValueError:
                pass
        mesh_hilited = list(dict.fromkeys(mesh_hilited))

    if len(mesh_hilited) != 1:
        return None, None, "Select components on a single polygon mesh."

    target_mesh = mesh_hilited[0]
    verts = cmds.filterExpand(sel, sm=31) or []
    other_comps = cmds.filterExpand(sel, sm=(32, 34, 35)) or []
    if other_comps:
        converted = cmds.polyListComponentConversion(other_comps, toVertex=True) or []
        verts.extend(converted)

    if not verts:
        return target_mesh, None, None

    # Use MSelectionList to extract vertex indices quickly without slow `ls -fl` on 50k verts
    sel_list = om.MSelectionList()
    for v in verts:
        sel_list.add(v)

    idx_list = []
    for i in range(sel_list.length()):
        _, comp = sel_list.getComponent(i)
        if not comp.isNull() and comp.apiType() == om.MFn.kMeshVertComponent:
            fn_comp = om.MFnSingleIndexedComponent(comp)
            idx_list.extend(fn_comp.getElements())

    if not idx_list:
        return target_mesh, None, None

    indices = np.unique(np.asarray(idx_list, dtype=np.int32))
    return target_mesh, indices, None


def extract_selected_edge_indices(mesh_name=None):
    """Return sorted list of selected edge indices on `mesh_name` (or active selection's mesh)."""
    edges = cmds.filterExpand(cmds.ls(sl=True) or [], sm=32) or []
    if not edges:
        return [], "Select one or more center edges on the mesh."

    sel_list = om.MSelectionList()
    for e in edges:
        sel_list.add(e)

    target_shape = None
    if mesh_name:
        _, target_shape_dag = get_mesh_dag_paths(mesh_name)
        target_shape = target_shape_dag.fullPathName()

    edge_ids = []
    detected_mesh = None
    for i in range(sel_list.length()):
        dag, comp = sel_list.getComponent(i)
        dag.extendToShape()
        if target_shape and dag.fullPathName() != target_shape:
            continue
        if detected_mesh is None:
            detected_mesh = get_transform_name(dag.fullPathName())
        if not comp.isNull() and comp.apiType() == om.MFn.kMeshEdgeComponent:
            fn_comp = om.MFnSingleIndexedComponent(comp)
            edge_ids.extend(fn_comp.getElements())

    if not edge_ids:
        return [], "No edges matched on target mesh."
    return sorted(set(int(e) for e in edge_ids)), None


def indices_to_component_list(mesh_name, indices, component_type="vtx"):
    """Convert integer vertex/edge indices into Maya component strings."""
    if len(indices) == 0:
        return []
    return ["{}.{}[{}]".format(mesh_name, component_type, int(i)) for i in indices]


def select_vertex_indices(mesh_name, indices):
    """Select vertex indices in Maya efficiently via OpenMaya MSelectionList."""
    transform_name = get_transform_name(mesh_name)
    if len(indices) == 0:
        cmds.select(transform_name, r=True)
        return

    _, shape_dag = get_mesh_dag_paths(transform_name)
    comp = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
    om.MFnSingleIndexedComponent(comp).addElements(om.MIntArray([int(i) for i in indices]))

    sel = om.MSelectionList()
    sel.add((shape_dag, comp))
    cmds.selectMode(component=True)
    cmds.selectType(vertex=True)
    om.MGlobal.setActiveSelectionList(sel)


# ---------------------------------------------------------------------------
# Fast 1-to-1 Spatial Point Matching (SciPy cKDTree or Pure-NumPy Hash)
# ---------------------------------------------------------------------------

def match_points_1to1(query_pts, target_pts, tol):
    """Match each query point to its nearest unique target point within `tol`.

    Args:
        query_pts: (M, D) float64 array.
        target_pts: (K, D) float64 array.
        tol: maximum Euclidean distance threshold.

    Returns:
        tuple: (matched_target_indices_for_query, distances)
            matched_target_indices_for_query is int32 array of length M (-1 if unmatched).
    """
    m = len(query_pts)
    k = len(target_pts)
    result = np.full(m, -1, dtype=np.int32)
    result_dists = np.full(m, np.inf, dtype=np.float64)

    if m == 0 or k == 0 or tol < 0.0:
        return result, result_dists

    tol = float(tol)
    if _SciPyKDTree is not None:
        return _match_with_kdtree(query_pts, target_pts, tol)
    return _match_with_numpy_spatial(query_pts, target_pts, tol)


def _assign_greedy_1to1(candidates, m, k):
    """Sort candidate (dist, qi, ti) tuples and greedily assign unique 1-to-1 matches."""
    result = np.full(m, -1, dtype=np.int32)
    result_dists = np.full(m, np.inf, dtype=np.float64)
    if not candidates:
        return result, result_dists

    candidates.sort(key=lambda item: item[0])
    used_q = np.zeros(m, dtype=bool)
    used_t = np.zeros(k, dtype=bool)
    for dist, qi, ti in candidates:
        if not used_q[qi] and not used_t[ti]:
            used_q[qi] = True
            used_t[ti] = True
            result[qi] = ti
            result_dists[qi] = dist
    return result, result_dists


def _match_with_kdtree(query_pts, target_pts, tol):
    m = len(query_pts)
    k = len(target_pts)
    tree = _SciPyKDTree(target_pts)
    k_nn = min(4, k)
    dists, indices = tree.query(query_pts, k=k_nn, distance_upper_bound=tol + 1e-12)
    if k_nn == 1:
        dists = dists[:, None]
        indices = indices[:, None]

    # Fast path: if all valid k=0 hits are unique (normal symmetrical mesh), avoid Python loop sorting
    first_idx = indices[:, 0]
    first_dist = dists[:, 0]
    valid_mask = first_idx < k
    valid_targets = first_idx[valid_mask]
    if valid_targets.size == 0:
        return np.full(m, -1, dtype=np.int32), np.full(m, np.inf, dtype=np.float64)

    _, counts = np.unique(valid_targets, return_counts=True)
    if np.all(counts == 1):
        result = np.full(m, -1, dtype=np.int32)
        result_dists = np.full(m, np.inf, dtype=np.float64)
        result[valid_mask] = valid_targets.astype(np.int32)
        result_dists[valid_mask] = first_dist[valid_mask]
        return result, result_dists

    # Collision path: greedy 1-to-1 assignment across k-nearest candidates
    candidates = []
    for qi in range(m):
        for r in range(k_nn):
            ti = int(indices[qi, r])
            if ti >= k:
                break
            candidates.append((float(dists[qi, r]), qi, ti))
    return _assign_greedy_1to1(candidates, m, k)


def _match_with_numpy_spatial(query_pts, target_pts, tol):
    m, dim = query_pts.shape
    k = len(target_pts)

    # Small matrix fast path
    if m * k <= 250000:
        diff = query_pts[:, None, :] - target_pts[None, :, :]
        dist_sq = np.sum(diff * diff, axis=2)
        tol_sq = (tol + 1e-12) ** 2
        q_idx, t_idx = np.nonzero(dist_sq <= tol_sq)
        if len(q_idx) == 0:
            return np.full(m, -1, dtype=np.int32), np.full(m, np.inf, dtype=np.float64)
        dists = np.sqrt(dist_sq[q_idx, t_idx])
        candidates = list(zip(dists.tolist(), q_idx.tolist(), t_idx.tolist()))
        return _assign_greedy_1to1(candidates, m, k)

    # Decide between spatial grid hash (tight tol) and 1D sorted binary search (wide tol)
    ptp = np.ptp(target_pts, axis=0)
    cell = max(tol, 1e-6)
    max_cells_est = float(np.max(ptp)) / cell if cell > 0 else 1e9
    if max_cells_est < 6.0:
        return _match_sorted_axis(query_pts, target_pts, tol)

    return _match_grid_hash(query_pts, target_pts, tol, cell, dim)


def _match_grid_hash(query_pts, target_pts, tol, cell, dim):
    m = len(query_pts)
    k = len(target_pts)
    tol_sq = (tol + 1e-12) ** 2

    t_coords = np.floor(target_pts / cell).astype(np.int64)
    grid = {}
    for ti, key in enumerate(map(tuple, t_coords.tolist())):
        bucket = grid.get(key)
        if bucket is None:
            grid[key] = [ti]
        else:
            bucket.append(ti)

    q_coords = np.floor(query_pts / cell).astype(np.int64).tolist()
    offsets = list(itertools.product((-1, 0, 1), repeat=dim))

    candidates = []
    for qi, base_cell in enumerate(q_coords):
        q_pt = query_pts[qi]
        cands = []
        if dim == 3:
            bx, by, bz = base_cell
            for dx, dy, dz in offsets:
                bucket = grid.get((bx + dx, by + dy, bz + dz))
                if bucket is not None:
                    cands.extend(bucket)
        else:
            bx, by = base_cell
            for dx, dy in offsets:
                bucket = grid.get((bx + dx, by + dy))
                if bucket is not None:
                    cands.extend(bucket)

        if not cands:
            continue

        cand_arr = np.asarray(cands, dtype=np.int32)
        diff = target_pts[cand_arr] - q_pt
        d_sq = np.sum(diff * diff, axis=1)
        valid = d_sq <= tol_sq
        if not np.any(valid):
            continue
        for ti, ds in zip(cand_arr[valid].tolist(), np.sqrt(d_sq[valid]).tolist()):
            candidates.append((ds, qi, ti))

    return _assign_greedy_1to1(candidates, m, k)


def _match_sorted_axis(query_pts, target_pts, tol):
    m = len(query_pts)
    k = len(target_pts)
    tol_sq = (tol + 1e-12) ** 2

    sort_axis = int(np.argmax(np.ptp(target_pts, axis=0)))
    order = np.argsort(target_pts[:, sort_axis])
    t_sorted = target_pts[order]
    t_axis_vals = t_sorted[:, sort_axis]

    lo_indices = np.searchsorted(t_axis_vals, query_pts[:, sort_axis] - tol - 1e-12, side="left")
    hi_indices = np.searchsorted(t_axis_vals, query_pts[:, sort_axis] + tol + 1e-12, side="right")

    candidates = []
    for qi in range(m):
        lo = int(lo_indices[qi])
        hi = int(hi_indices[qi])
        if lo >= hi:
            continue
        diff = t_sorted[lo:hi] - query_pts[qi]
        d_sq = np.sum(diff * diff, axis=1)
        valid = d_sq <= tol_sq
        if not np.any(valid):
            continue
        matched_t = order[lo:hi][valid]
        for ti, ds in zip(matched_t.tolist(), np.sqrt(d_sq[valid]).tolist()):
            candidates.append((ds, qi, ti))

    return _assign_greedy_1to1(candidates, m, k)


# ---------------------------------------------------------------------------
# Symmetry Table Builders (World, Local, UV, Topology)
# ---------------------------------------------------------------------------

def build_symmetry_data(
    base_mesh,
    sample_space=SAMPLE_LOCAL,
    axis=AXIS_X,
    origin_mode=ORIGIN_PIVOT,
    tolerance=0.001,
    uv_set="",
    uv_axis=0,
    uv_center=0.5,
    uv_auto_center=False,
    uv_tolerance=0.001,
    seed_edges=None,
    fallback_unreached=SAMPLE_LOCAL,
):
    """Build a cached SymmetryData mapping for `base_mesh` using the chosen sample space."""
    t0 = time.perf_counter()
    transform_dag, shape_dag = get_mesh_dag_paths(base_mesh)
    transform_name = transform_dag.partialPathName()
    shape_name = shape_dag.fullPathName()
    fn_mesh = om.MFnMesh(shape_dag)
    num_verts = fn_mesh.numVertices

    if sample_space not in VALID_SAMPLE_SPACES:
        raise ValueError("Invalid sample space: {}".format(sample_space))

    if sample_space in (SAMPLE_WORLD, SAMPLE_LOCAL):
        sym_table, side_table, base_mid, notes = _build_spatial_symmetry(
            transform_name, sample_space, axis, origin_mode, tolerance
        )
        used_uv_set = uv_set
        used_uv_center = uv_center
        used_seeds = []
    elif sample_space == SAMPLE_UV:
        sym_table, side_table, base_mid, used_uv_set, used_uv_center, notes = _build_uv_symmetry(
            transform_name,
            axis,
            origin_mode,
            uv_set,
            uv_axis,
            uv_center,
            uv_auto_center,
            uv_tolerance,
            tolerance,
        )
        used_seeds = []
    else:  # SAMPLE_TOPOLOGY
        sym_table, side_table, base_mid, used_seeds, notes = _build_topology_symmetry(
            transform_name,
            axis,
            origin_mode,
            tolerance,
            seed_edges,
            fallback_unreached,
            uv_set,
            uv_axis,
            uv_center,
            uv_auto_center,
            uv_tolerance,
        )
        used_uv_set = uv_set
        used_uv_center = uv_center

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return SymmetryData(
        base_mesh=transform_name,
        base_shape=shape_name,
        num_verts=num_verts,
        sample_space=sample_space,
        axis=axis,
        origin_mode=origin_mode,
        base_mid=base_mid,
        tolerance=tolerance,
        sym_table=sym_table,
        side_table=side_table,
        uv_set=used_uv_set,
        uv_axis=uv_axis,
        uv_center=used_uv_center,
        seed_edges=used_seeds,
        elapsed_ms=elapsed_ms,
        notes=notes,
    )


def _build_spatial_symmetry(mesh_name, sample_space, axis, origin_mode, tol):
    space = om.MSpace.kWorld if sample_space == SAMPLE_WORLD else om.MSpace.kObject
    pts = get_mesh_points_np(mesh_name, space=space)
    num_verts = len(pts)
    mid = get_mirror_mid(mesh_name, axis, sample_space, origin_mode, points_np=pts)

    sym_table = np.full(num_verts, -1, dtype=np.int32)
    side_table = np.full(num_verts, -2, dtype=np.int8)

    offsets = pts[:, axis] - mid
    center_mask = np.abs(offsets) < tol
    pos_mask = offsets >= tol
    neg_mask = offsets <= -tol

    center_idx = np.flatnonzero(center_mask).astype(np.int32)
    sym_table[center_idx] = center_idx
    side_table[center_idx] = 0

    pos_idx = np.flatnonzero(pos_mask).astype(np.int32)
    neg_idx = np.flatnonzero(neg_mask).astype(np.int32)

    mirrored_pos = pts[pos_idx].copy()
    mirrored_pos[:, axis] = 2.0 * mid - mirrored_pos[:, axis]

    matched_neg_rel, _ = match_points_1to1(mirrored_pos, pts[neg_idx], tol)
    valid = matched_neg_rel >= 0
    matched_pos = pos_idx[valid]
    matched_neg = neg_idx[matched_neg_rel[valid]]

    sym_table[matched_pos] = matched_neg
    sym_table[matched_neg] = matched_pos
    side_table[matched_pos] = 1
    side_table[matched_neg] = -1

    return sym_table, side_table, mid, ""


def _build_uv_symmetry(
    mesh_name,
    axis,
    origin_mode,
    uv_set,
    uv_axis,
    uv_center,
    uv_auto_center,
    uv_tol,
    spatial_tol,
):
    _, shape_dag = get_mesh_dag_paths(mesh_name)
    fn_mesh = om.MFnMesh(shape_dag)
    num_verts = fn_mesh.numVertices

    uv_sets = list(fn_mesh.getUVSetNames() or [])
    if not uv_sets:
        raise ValueError("Mesh '{}' has no UV sets.".format(mesh_name))
    if not uv_set or uv_set not in uv_sets:
        uv_set = fn_mesh.currentUVSetName()
        if uv_set not in uv_sets:
            uv_set = uv_sets[0]

    u_vals, v_vals = fn_mesh.getUVs(uv_set)
    if len(u_vals) == 0:
        raise ValueError("UV set '{}' on '{}' is empty.".format(uv_set, mesh_name))

    uv_counts, uv_ids = fn_mesh.getAssignedUVs(uv_set)
    poly_counts, poly_verts = fn_mesh.getVertices()

    # Build deduplicated UV coordinates per vertex
    vert_uvs = [[] for _ in range(num_verts)]
    v_cursor = 0
    uv_cursor = 0
    for f_idx, v_count in enumerate(poly_counts):
        u_count = uv_counts[f_idx]
        if u_count == v_count:
            for k in range(v_count):
                vid = int(poly_verts[v_cursor + k])
                uid = int(uv_ids[uv_cursor + k])
                uv_pt = (float(u_vals[uid]), float(v_vals[uid]))
                existing = vert_uvs[vid]
                if not any(abs(uv_pt[0] - ex[0]) < 1e-6 and abs(uv_pt[1] - ex[1]) < 1e-6 for ex in existing):
                    existing.append(uv_pt)
        v_cursor += v_count
        uv_cursor += u_count

    pts_3d = get_mesh_points_np(mesh_name, space=om.MSpace.kObject)
    mid_3d = get_mirror_mid(mesh_name, axis, SAMPLE_LOCAL, origin_mode, points_np=pts_3d)

    all_uv_coords = []
    entry_vert_ids = []
    for vid, uvs in enumerate(vert_uvs):
        for uv_pt in uvs:
            all_uv_coords.append(uv_pt)
            entry_vert_ids.append(vid)

    if not all_uv_coords:
        raise ValueError("No assigned UVs found in UV set '{}' on '{}'.".format(uv_set, mesh_name))

    uv_arr = np.asarray(all_uv_coords, dtype=np.float64)
    entry_vids = np.asarray(entry_vert_ids, dtype=np.int32)

    if uv_auto_center:
        used_uv_center = float(0.5 * (uv_arr[:, uv_axis].min() + uv_arr[:, uv_axis].max()))
    else:
        used_uv_center = float(uv_center)

    mirrored_uv = uv_arr.copy()
    mirrored_uv[:, uv_axis] = 2.0 * used_uv_center - mirrored_uv[:, uv_axis]

    # Collect all UV candidates within uv_tol for each entry using fast range query
    pair_candidates = _find_uv_candidate_pairs(uv_arr, mirrored_uv, entry_vids, pts_3d, mid_3d, axis, uv_tol)

    sym_table = np.full(num_verts, -1, dtype=np.int32)
    side_table = np.full(num_verts, -2, dtype=np.int8)

    # First identify self-mirroring center vertices (either on UV center line or split symmetrically across seam)
    # Only promote self-match if vertex is not clearly paired to a different vertex at a closer 3D mirror distance
    best_self_uv_dist = {}
    best_other_by_v = {}
    for uv_d, dist3d, v1, v2 in pair_candidates:
        if v1 == v2:
            prev = best_self_uv_dist.get(v1)
            if prev is None or uv_d < prev:
                best_self_uv_dist[v1] = uv_d
        else:
            prev = best_other_by_v.get(v1)
            if prev is None or (round(uv_d, 6), dist3d) < prev:
                best_other_by_v[v1] = (round(uv_d, 6), dist3d)

    center_verts = []
    for vid, self_uv_d in best_self_uv_dist.items():
        other = best_other_by_v.get(vid)
        if other is None:
            center_verts.append(vid)
        else:
            # Disambiguate stacked center UVs vs true center seam
            self_3d_offset = abs(float(pts_3d[vid, axis] - mid_3d))
            if self_uv_d + 1e-6 < other[0] or self_3d_offset <= other[1]:
                center_verts.append(vid)

    for vid in center_verts:
        sym_table[vid] = vid
        side_table[vid] = 0

    # Greedy 1-to-1 assignment for distinct vertex pairs
    distinct_cands = []
    for uv_d, dist3d, v1, v2 in pair_candidates:
        if v1 == v2 or sym_table[v1] != -1 or sym_table[v2] != -1:
            continue
        distinct_cands.append((round(uv_d, 6), dist3d, v1, v2))

    distinct_cands.sort(key=lambda item: (item[0], item[1]))
    for _, _, v1, v2 in distinct_cands:
        if sym_table[v1] != -1 or sym_table[v2] != -1:
            continue
        sym_table[v1] = v2
        sym_table[v2] = v1
        if pts_3d[v1, axis] >= pts_3d[v2, axis]:
            side_table[v1] = 1
            side_table[v2] = -1
        else:
            side_table[v1] = -1
            side_table[v2] = 1

    notes = "UV Set '{}', {}={:.4f}".format(uv_set, "U" if uv_axis == 0 else "V", used_uv_center)
    return sym_table, side_table, mid_3d, uv_set, used_uv_center, notes


def _find_uv_candidate_pairs(uv_arr, mirrored_uv, entry_vids, pts_3d, mid_3d, axis, uv_tol):
    """Find candidate (uv_dist, dist3d_mirrored, vid_a, vid_b) tuples within `uv_tol`."""
    n = len(uv_arr)
    results = []

    if _SciPyKDTree is not None:
        tree = _SciPyKDTree(uv_arr)
        # query_ball_tree handles stacked/seam UVs accurately in C++
        q_tree = _SciPyKDTree(mirrored_uv)
        hits = q_tree.query_ball_tree(tree, r=uv_tol + 1e-12)
        for qi, hit_list in enumerate(hits):
            if not hit_list:
                continue
            v1 = int(entry_vids[qi])
            p1_mir = pts_3d[v1].copy()
            p1_mir[axis] = 2.0 * mid_3d - p1_mir[axis]
            mq = mirrored_uv[qi]
            for ti in hit_list:
                v2 = int(entry_vids[ti])
                du = uv_arr[ti, 0] - mq[0]
                dv = uv_arr[ti, 1] - mq[1]
                uv_d = float((du * du + dv * dv) ** 0.5)
                d3 = float(np.linalg.norm(pts_3d[v2] - p1_mir))
                results.append((uv_d, d3, v1, v2))
        return results

    # Pure-numpy 2D grid hash fallback
    cell = max(float(uv_tol), 1e-5)
    tol_sq = (uv_tol + 1e-12) ** 2
    t_coords = np.floor(uv_arr / cell).astype(np.int64)
    grid = {}
    for ti, key in enumerate(map(tuple, t_coords.tolist())):
        bucket = grid.get(key)
        if bucket is None:
            grid[key] = [ti]
        else:
            bucket.append(ti)

    q_coords = np.floor(mirrored_uv / cell).astype(np.int64).tolist()
    offsets = list(itertools.product((-1, 0, 1), repeat=2))
    for qi, (bx, by) in enumerate(q_coords):
        cands = []
        for dx, dy in offsets:
            bucket = grid.get((bx + dx, by + dy))
            if bucket is not None:
                cands.extend(bucket)
        if not cands:
            continue
        cand_arr = np.asarray(cands, dtype=np.int32)
        diff = uv_arr[cand_arr] - mirrored_uv[qi]
        d_sq = np.sum(diff * diff, axis=1)
        valid = d_sq <= tol_sq
        if not np.any(valid):
            continue
        v1 = int(entry_vids[qi])
        p1_mir = pts_3d[v1].copy()
        p1_mir[axis] = 2.0 * mid_3d - p1_mir[axis]
        for ti, ds in zip(cand_arr[valid].tolist(), np.sqrt(d_sq[valid]).tolist()):
            v2 = int(entry_vids[ti])
            d3 = float(np.linalg.norm(pts_3d[v2] - p1_mir))
            results.append((ds, d3, v1, v2))
    return results


def _build_topology_mesh_graph(fn_mesh):
    """Extract face vertex loops and undirected edge -> adjacent faces map."""
    poly_counts, poly_verts = fn_mesh.getVertices()
    face_verts = []
    edge_to_faces = {}
    cursor = 0
    for f_idx, count in enumerate(poly_counts):
        loop = [int(poly_verts[cursor + k]) for k in range(count)]
        face_verts.append(loop)
        for k in range(count):
            a = loop[k]
            b = loop[(k + 1) % count]
            ekey = (a, b) if a < b else (b, a)
            flist = edge_to_faces.get(ekey)
            if flist is None:
                edge_to_faces[ekey] = [f_idx]
            else:
                flist.append(f_idx)
        cursor += count
    return face_verts, edge_to_faces


def _auto_detect_center_edges(fn_mesh, face_verts, edge_to_faces, pts, axis, mid, tol):
    """Find one valid center seam edge per connected shell near the symmetry plane."""
    num_edges = fn_mesh.numEdges
    num_faces = len(face_verts)

    # Precompute face centroids along symmetry axis
    face_cent_axis = np.zeros(num_faces, dtype=np.float64)
    for f_idx, loop in enumerate(face_verts):
        face_cent_axis[f_idx] = float(np.mean(pts[loop, axis]))

    # Build connected shells via face adjacency
    face_shell = np.full(num_faces, -1, dtype=np.int32)
    shell_id = 0
    for start_f in range(num_faces):
        if face_shell[start_f] != -1:
            continue
        q = deque([start_f])
        face_shell[start_f] = shell_id
        while q:
            cf = q.popleft()
            loop = face_verts[cf]
            cnt = len(loop)
            for k in range(cnt):
                a, b = loop[k], loop[(k + 1) % cnt]
                ekey = (a, b) if a < b else (b, a)
                for nf in edge_to_faces.get(ekey, ()):
                    if face_shell[nf] == -1:
                        face_shell[nf] = shell_id
                        q.append(nf)
        shell_id += 1

    best_per_shell = {}
    for e_idx in range(num_edges):
        va, vb = fn_mesh.getEdgeVertices(e_idx)
        off_a = abs(float(pts[va, axis] - mid))
        off_b = abs(float(pts[vb, axis] - mid))
        if off_a >= tol or off_b >= tol:
            continue
        ekey = (va, vb) if va < vb else (vb, va)
        adj = edge_to_faces.get(ekey, [])
        if len(adj) != 2:
            continue
        f1, f2 = adj[0], adj[1]
        if len(face_verts[f1]) != len(face_verts[f2]):
            continue
        d1 = face_cent_axis[f1] - mid
        d2 = face_cent_axis[f2] - mid
        if d1 * d2 >= 0.0:
            continue
        sh = int(face_shell[f1])
        score = off_a + off_b
        prev = best_per_shell.get(sh)
        if prev is None or score < prev[0]:
            best_per_shell[sh] = (score, e_idx)

    return [item[1] for item in best_per_shell.values()]


def _run_topology_bfs(face_verts, edge_to_faces, initial_queue, sym_table, side_table, visited_faces):
    """Propagate symmetry pairs across manifold face-edge-vertex topology via BFS."""
    queue = deque(initial_queue)
    while queue:
        f_pos, f_neg, a_pos, b_pos, a_neg, b_neg = queue.popleft()
        if f_pos in visited_faces or f_neg in visited_faces:
            continue

        vp = face_verts[f_pos]
        vn = face_verts[f_neg]
        k = len(vp)
        if k != len(vn):
            continue

        try:
            ip = vp.index(a_pos)
            in_ = vn.index(a_neg)
        except ValueError:
            continue

        if vp[(ip + 1) % k] == b_pos:
            dp = 1
        elif vp[(ip - 1) % k] == b_pos:
            dp = -1
        else:
            continue

        if vn[(in_ + 1) % k] == b_neg:
            dn = 1
        elif vn[(in_ - 1) % k] == b_neg:
            dn = -1
        else:
            continue

        seq_p = [vp[(ip + t * dp) % k] for t in range(k)]
        seq_n = [vn[(in_ + t * dn) % k] for t in range(k)]

        # Check compatibility with previously assigned vertices before committing
        conflict = False
        for u, v in zip(seq_p, seq_n):
            su = int(sym_table[u])
            sv = int(sym_table[v])
            if (su != -1 and su != v) or (sv != -1 and sv != u):
                conflict = True
                break
        if conflict:
            continue

        visited_faces.add(f_pos)
        visited_faces.add(f_neg)

        for u, v in zip(seq_p, seq_n):
            if u == v:
                sym_table[u] = u
                side_table[u] = 0
            else:
                sym_table[u] = v
                sym_table[v] = u
                side_table[u] = 1
                side_table[v] = -1

        for t in range(k):
            p1, p2 = seq_p[t], seq_p[(t + 1) % k]
            q1, q2 = seq_n[t], seq_n[(t + 1) % k]
            ep = (p1, p2) if p1 < p2 else (p2, p1)
            en = (q1, q2) if q1 < q2 else (q2, q1)
            if ep == en:
                # Reached another center seam edge; do not cross over to opposite side.
                continue

            adj_p = edge_to_faces.get(ep, ())
            adj_n = edge_to_faces.get(en, ())
            if len(adj_p) != 2 or len(adj_n) != 2:
                continue

            fp_next = adj_p[1] if adj_p[0] == f_pos else adj_p[0]
            fn_next = adj_n[1] if adj_n[0] == f_neg else adj_n[0]
            if fp_next == fn_next:
                continue
            if fp_next not in visited_faces and fn_next not in visited_faces:
                queue.append((fp_next, fn_next, p1, p2, q1, q2))


def _build_topology_symmetry(
    mesh_name,
    axis,
    origin_mode,
    tol,
    seed_edges,
    fallback_unreached,
    uv_set,
    uv_axis,
    uv_center,
    uv_auto_center,
    uv_tol,
):
    _, shape_dag = get_mesh_dag_paths(mesh_name)
    fn_mesh = om.MFnMesh(shape_dag)
    num_verts = fn_mesh.numVertices
    num_edges = fn_mesh.numEdges

    pts = get_mesh_points_np(mesh_name, space=om.MSpace.kObject)
    mid = get_mirror_mid(mesh_name, axis, SAMPLE_LOCAL, origin_mode, points_np=pts)

    face_verts, edge_to_faces = _build_topology_mesh_graph(fn_mesh)

    parsed_seeds = []
    if seed_edges:
        for item in seed_edges:
            if isinstance(item, int):
                if 0 <= item < num_edges:
                    parsed_seeds.append(item)
            elif isinstance(item, str):
                s = item.strip()
                if s.isdigit():
                    eid = int(s)
                    if 0 <= eid < num_edges:
                        parsed_seeds.append(eid)
                elif ".e[" in s:
                    sel_tmp = om.MSelectionList()
                    try:
                        sel_tmp.add(s)
                        _, comp = sel_tmp.getComponent(0)
                        if not comp.isNull() and comp.apiType() == om.MFn.kMeshEdgeComponent:
                            parsed_seeds.extend(int(e) for e in om.MFnSingleIndexedComponent(comp).getElements())
                    except Exception:
                        pass
        parsed_seeds = sorted(set(parsed_seeds))

    if not parsed_seeds:
        parsed_seeds = _auto_detect_center_edges(fn_mesh, face_verts, edge_to_faces, pts, axis, mid, tol)

    if not parsed_seeds and fallback_unreached == "none":
        raise ValueError(
            "Topology mode requires center seam edge(s). Select center edge(s) and load them."
        )

    sym_table = np.full(num_verts, -1, dtype=np.int32)
    side_table = np.full(num_verts, -2, dtype=np.int8)
    visited_faces = set()
    initial_queue = []

    for e_idx in parsed_seeds:
        va, vb = fn_mesh.getEdgeVertices(e_idx)
        ekey = (va, vb) if va < vb else (vb, va)
        adj = edge_to_faces.get(ekey, [])
        if len(adj) != 2:
            continue
        f1, f2 = adj[0], adj[1]
        c1 = float(np.mean(pts[face_verts[f1], axis]))
        c2 = float(np.mean(pts[face_verts[f2], axis]))
        if c1 >= c2:
            f_pos, f_neg = f1, f2
        else:
            f_pos, f_neg = f2, f1

        sym_table[va] = va
        sym_table[vb] = vb
        side_table[va] = 0
        side_table[vb] = 0
        initial_queue.append((f_pos, f_neg, va, vb, va, vb))

    _run_topology_bfs(face_verts, edge_to_faces, initial_queue, sym_table, side_table, visited_faces)

    # Optional fallback for disconnected shells without center edges (e.g. eyeballs, teeth)
    fallback_count = 0
    if fallback_unreached and fallback_unreached != "none":
        unmatched = np.flatnonzero(sym_table == -1)
        if len(unmatched) > 0:
            if fallback_unreached == SAMPLE_UV:
                fb_sym, fb_side, _, _, _, _ = _build_uv_symmetry(
                    mesh_name, axis, origin_mode, uv_set, uv_axis, uv_center, uv_auto_center, uv_tol, tol
                )
            elif fallback_unreached in (SAMPLE_WORLD, SAMPLE_LOCAL):
                fb_sym, fb_side, _, _ = _build_spatial_symmetry(
                    mesh_name, fallback_unreached, axis, origin_mode, tol
                )
            else:
                fb_sym = None
                fb_side = None

            if fb_sym is not None:
                # Try seeding unvisited symmetrical face pairs topologically first using a fallback-matched edge
                unmatched_set = set(unmatched.tolist())
                fb_queue = []
                for ekey, adj in edge_to_faces.items():
                    if len(adj) != 2:
                        continue
                    a, b = ekey
                    if a not in unmatched_set or b not in unmatched_set:
                        continue
                    ma, mb = int(fb_sym[a]), int(fb_sym[b])
                    if ma < 0 or mb < 0 or ma == a or mb == b:
                        continue
                    mkey = (ma, mb) if ma < mb else (mb, ma)
                    madj = edge_to_faces.get(mkey, [])
                    if len(madj) != 2:
                        continue
                    # Pick corresponding faces by fallback matching their remaining vertices
                    for f_a in adj:
                        if f_a in visited_faces:
                            continue
                        va_loop = face_verts[f_a]
                        mapped_loop = {int(fb_sym[v]) for v in va_loop}
                        if -1 in mapped_loop:
                            continue
                        for f_b in madj:
                            if f_b in visited_faces or f_b == f_a:
                                continue
                            if set(face_verts[f_b]) == mapped_loop:
                                if np.mean(pts[va_loop, axis]) >= np.mean(pts[face_verts[f_b], axis]):
                                    fb_queue.append((f_a, f_b, a, b, ma, mb))
                                else:
                                    fb_queue.append((f_b, f_a, ma, mb, a, b))
                                break

                if fb_queue:
                    _run_topology_bfs(face_verts, edge_to_faces, fb_queue, sym_table, side_table, visited_faces)

                # Fill any remaining isolated vertices directly from fallback table
                still_unmatched = np.flatnonzero(sym_table == -1)
                for vid in still_unmatched.tolist():
                    partner = int(fb_sym[vid])
                    if partner < 0:
                        continue
                    if partner == vid:
                        sym_table[vid] = vid
                        side_table[vid] = 0
                        fallback_count += 1
                    elif sym_table[partner] == -1:
                        sym_table[vid] = partner
                        sym_table[partner] = vid
                        side_table[vid] = fb_side[vid]
                        side_table[partner] = fb_side[partner]
                        fallback_count += 2

    notes = "Seeds: {} edge(s)".format(len(parsed_seeds))
    if fallback_count > 0:
        notes += ", fallback matched {} vert(s)".format(fallback_count)
    return sym_table, side_table, mid, parsed_seeds, notes


# ---------------------------------------------------------------------------
# High-Level Mesh Operations (Check, Mirror, Flip, Revert, Blendshape Ops)
# ---------------------------------------------------------------------------

def check_symmetry(
    mesh_name,
    sample_space=SAMPLE_LOCAL,
    axis=AXIS_X,
    origin_mode=ORIGIN_PIVOT,
    tolerance=0.001,
    uv_set="",
    uv_axis=0,
    uv_center=0.5,
    uv_auto_center=False,
    uv_tolerance=0.001,
    seed_edges=None,
    fallback_unreached=SAMPLE_LOCAL,
):
    """Return asymmetric vertex indices for `mesh_name`."""
    sym_data = build_symmetry_data(
        mesh_name,
        sample_space=sample_space,
        axis=axis,
        origin_mode=origin_mode,
        tolerance=tolerance,
        uv_set=uv_set,
        uv_axis=uv_axis,
        uv_center=uv_center,
        uv_auto_center=uv_auto_center,
        uv_tolerance=uv_tolerance,
        seed_edges=seed_edges,
        fallback_unreached=fallback_unreached,
    )
    return sym_data.unmatched_indices, sym_data


def mirror_selection(sym_data, vert_indices):
    """Return mirrored vertex indices corresponding to `vert_indices`."""
    vert_indices = np.asarray(vert_indices, dtype=np.int32)
    valid_mask = (vert_indices >= 0) & (vert_indices < sym_data.num_verts)
    vert_indices = vert_indices[valid_mask]
    mapped = sym_data.sym_table[vert_indices]
    out = np.where(mapped >= 0, mapped, vert_indices)
    return np.unique(out).astype(np.int32)


def get_moved_verts(target_mesh, base_mesh, tolerance=0.001):
    """Return indices of vertices on `target_mesh` that differ from `base_mesh` in object space."""
    trg_pts = get_mesh_points_np(target_mesh, space=om.MSpace.kObject)
    base_pts = get_mesh_points_np(base_mesh, space=om.MSpace.kObject)
    if trg_pts.shape != base_pts.shape:
        raise ValueError(
            "Vertex count mismatch between '{}' ({}) and '{}' ({}).".format(
                target_mesh, len(trg_pts), base_mesh, len(base_pts)
            )
        )
    diff = np.abs(trg_pts - base_pts)
    moved_mask = np.any(diff > tolerance, axis=1)
    return np.flatnonzero(moved_mask).astype(np.int32)


def mirror_vertices(
    target_mesh,
    sym_data,
    vert_indices=None,
    neg_to_pos=False,
    origin_mode=None,
    undoable=True,
):
    """Mirror vertex positions across the symmetry plane on `target_mesh`."""
    space = om.MSpace.kWorld if sym_data.sample_space == SAMPLE_WORLD else om.MSpace.kObject
    pts = get_mesh_points_np(target_mesh, space=space)
    if len(pts) != sym_data.num_verts:
        raise ValueError(
            "Vertex count mismatch: target '{}' has {}, base '{}' has {}.".format(
                target_mesh, len(pts), sym_data.base_mesh, sym_data.num_verts
            )
        )

    use_origin = origin_mode if origin_mode is not None else sym_data.origin_mode
    mid = get_mirror_mid(target_mesh, sym_data.axis, sym_data.sample_space, use_origin, points_np=pts)
    src_side = -1 if neg_to_pos else 1

    if vert_indices is None:
        src_verts = np.flatnonzero(sym_data.side_table == src_side)
        ctr_verts = sym_data.center_indices
    else:
        sel = np.asarray(vert_indices, dtype=np.int32)
        sel = sel[(sel >= 0) & (sel < sym_data.num_verts)]
        src_verts = sel[sym_data.side_table[sel] == src_side]
        ctr_verts = sel[sym_data.side_table[sel] == 0]

    dst_verts = sym_data.sym_table[src_verts]
    valid = dst_verts >= 0
    src_verts = src_verts[valid]
    dst_verts = dst_verts[valid]

    if len(src_verts) > 0:
        mirrored = pts[src_verts].copy()
        mirrored[:, sym_data.axis] = 2.0 * mid - mirrored[:, sym_data.axis]
        pts[dst_verts] = mirrored

    if len(ctr_verts) > 0:
        pts[ctr_verts, sym_data.axis] = mid

    set_mesh_points_np(target_mesh, pts, space=space, undoable=undoable)


def flip_vertices(
    target_mesh,
    sym_data,
    vert_indices=None,
    origin_mode=None,
    undoable=True,
):
    """Flip symmetrical vertex pairs and center vertices across the symmetry plane."""
    space = om.MSpace.kWorld if sym_data.sample_space == SAMPLE_WORLD else om.MSpace.kObject
    pts = get_mesh_points_np(target_mesh, space=space)
    if len(pts) != sym_data.num_verts:
        raise ValueError(
            "Vertex count mismatch: target '{}' has {}, base '{}' has {}.".format(
                target_mesh, len(pts), sym_data.base_mesh, sym_data.num_verts
            )
        )

    use_origin = origin_mode if origin_mode is not None else sym_data.origin_mode
    mid = get_mirror_mid(target_mesh, sym_data.axis, sym_data.sample_space, use_origin, points_np=pts)

    if vert_indices is None:
        u = sym_data.pos_indices
        v = sym_data.sym_table[u]
        ctr_verts = sym_data.center_indices
    else:
        sel = np.asarray(vert_indices, dtype=np.int32)
        sel = sel[(sel >= 0) & (sel < sym_data.num_verts)]
        ctr_verts = np.unique(sel[sym_data.side_table[sel] == 0])

        paired_sel = sel[(sym_data.sym_table[sel] >= 0) & (sym_data.side_table[sel] != 0)]
        if len(paired_sel) > 0:
            partners = sym_data.sym_table[paired_sel]
            # Normalize each pair as (pos_side_vert, neg_side_vert) and deduplicate
            # so selecting both sides never swaps a pair twice.
            u_raw = np.where(sym_data.side_table[paired_sel] == 1, paired_sel, partners)
            u = np.unique(u_raw).astype(np.int32)
            v = sym_data.sym_table[u]
        else:
            u = np.zeros(0, dtype=np.int32)
            v = np.zeros(0, dtype=np.int32)

    if len(u) > 0:
        pts_u = pts[u].copy()
        pts_v = pts[v].copy()
        pts_u[:, sym_data.axis] = 2.0 * mid - pts_u[:, sym_data.axis]
        pts_v[:, sym_data.axis] = 2.0 * mid - pts_v[:, sym_data.axis]
        pts[v] = pts_u
        pts[u] = pts_v

    if len(ctr_verts) > 0:
        pts[ctr_verts, sym_data.axis] = 2.0 * mid - pts[ctr_verts, sym_data.axis]

    set_mesh_points_np(target_mesh, pts, space=space, undoable=undoable)


def revert_vertices(
    target_mesh,
    base_mesh,
    bias=1.0,
    vert_indices=None,
    orig_points=None,
    base_points=None,
    undoable=True,
):
    """Blend `target_mesh` vertex positions toward `base_mesh` by `bias` (1.0 = 100% base)."""
    pts = orig_points.copy() if orig_points is not None else get_mesh_points_np(target_mesh, om.MSpace.kObject)
    b_pts = base_points if base_points is not None else get_mesh_points_np(base_mesh, om.MSpace.kObject)
    if pts.shape != b_pts.shape:
        raise ValueError(
            "Vertex count mismatch between '{}' ({}) and '{}' ({}).".format(
                target_mesh, len(pts), base_mesh, len(b_pts)
            )
        )

    bias = float(bias)
    if vert_indices is None:
        pts = pts + bias * (b_pts - pts)
    else:
        sel = np.asarray(vert_indices, dtype=np.int32)
        sel = sel[(sel >= 0) & (sel < len(pts))]
        if len(sel) > 0:
            pts[sel] = pts[sel] + bias * (b_pts[sel] - pts[sel])

    set_mesh_points_np(target_mesh, pts, space=om.MSpace.kObject, undoable=undoable)


def blendshape_operation(
    base_mesh,
    source_mesh,
    target_mesh,
    sym_data,
    operation,
    mirror=False,
    use_target_as_base=False,
    undoable=True,
):
    """Apply Copy / Add / Subtract (with optional Mirror) from `source_mesh` to `target_mesh`.

    Args:
        operation: "copy", "add", or "subtract".
        mirror: if True, mirror positions/deltas across `sym_data`.
        use_target_as_base: if True, delta is computed as (source - target) instead of (source - base).
    """
    base_pts = get_mesh_points_np(base_mesh, om.MSpace.kObject)
    src_pts = get_mesh_points_np(source_mesh, om.MSpace.kObject)
    trg_pts = get_mesh_points_np(target_mesh, om.MSpace.kObject)

    n = sym_data.num_verts
    if len(base_pts) != n or len(src_pts) != n or len(trg_pts) != n:
        raise ValueError("All meshes (Base, Source, Target) must have matching vertex counts.")

    ref_pts = trg_pts if use_target_as_base else base_pts
    delta = src_pts - ref_pts
    out_pts = trg_pts.copy()

    if not mirror:
        if operation == "copy":
            out_pts = src_pts.copy()
        elif operation == "add":
            out_pts = trg_pts + delta
        elif operation == "subtract":
            out_pts = trg_pts - delta
        else:
            raise ValueError("Unknown operation: {}".format(operation))
    else:
        axis = sym_data.axis
        valid_mask = sym_data.sym_table >= 0
        valid_idx = np.flatnonzero(valid_mask)
        sym_idx = sym_data.sym_table[valid_idx]

        if operation == "copy":
            mid = get_mirror_mid(target_mesh, axis, SAMPLE_LOCAL, sym_data.origin_mode, points_np=trg_pts)
            mirrored_src = src_pts[sym_idx].copy()
            mirrored_src[:, axis] = 2.0 * mid - mirrored_src[:, axis]
            out_pts[valid_idx] = mirrored_src
        elif operation in ("add", "subtract"):
            mirrored_delta = delta[sym_idx].copy()
            mirrored_delta[:, axis] *= -1.0
            if operation == "add":
                out_pts[valid_idx] = trg_pts[valid_idx] + mirrored_delta
            else:
                out_pts[valid_idx] = trg_pts[valid_idx] - mirrored_delta
        else:
            raise ValueError("Unknown operation: {}".format(operation))

    set_mesh_points_np(target_mesh, out_pts, space=om.MSpace.kObject, undoable=undoable)


def restore_symmetry(
    mesh_name,
    vert_indices=None,
    axis=AXIS_X,
    origin_mode=ORIGIN_PIVOT,
    start_tol=1e-6,
    end_tol=1.0,
    iterations=200,
    neg_to_pos=False,
    undoable=True,
):
    """Iteratively symmetrize vertices using increasing search radii (fast vectorized abSymmetrizeVerts)."""
    if start_tol > end_tol:
        raise ValueError("Start radius must be less than or equal to end radius.")

    pts = get_mesh_points_np(mesh_name, om.MSpace.kObject)
    num_verts = len(pts)
    mid = get_mirror_mid(mesh_name, axis, SAMPLE_LOCAL, origin_mode, points_np=pts)

    if vert_indices is None:
        work_idx = np.arange(num_verts, dtype=np.int32)
    else:
        work_idx = np.unique(np.asarray(vert_indices, dtype=np.int32))
        work_idx = work_idx[(work_idx >= 0) & (work_idx < num_verts)]

    offsets = pts[work_idx, axis] - mid
    center_mask = np.abs(offsets) <= start_tol
    if np.any(center_mask):
        pts[work_idx[center_mask], axis] = mid

    pos_idx = work_idx[offsets > start_tol]
    neg_idx = work_idx[offsets < -start_tol]

    src_pool = neg_idx if neg_to_pos else pos_idx
    dst_pool = pos_idx if neg_to_pos else neg_idx

    matched_count = 0
    iters = max(int(iterations), 2)
    for it in range(iters):
        if len(src_pool) == 0 or len(dst_pool) == 0:
            break
        t = float(it) / float(iters - 1)
        tol = float(end_tol) * (t * t) + float(start_tol)

        mirrored_src = pts[src_pool].copy()
        mirrored_src[:, axis] = 2.0 * mid - mirrored_src[:, axis]

        matched_dst_rel, _ = match_points_1to1(mirrored_src, pts[dst_pool], tol)
        hit_mask = matched_dst_rel >= 0
        if np.any(hit_mask):
            hit_src = src_pool[hit_mask]
            hit_dst = dst_pool[matched_dst_rel[hit_mask]]
            pts[hit_dst] = mirrored_src[hit_mask]
            matched_count += len(hit_src)

            src_pool = src_pool[~hit_mask]
            dst_keep = np.ones(len(dst_pool), dtype=bool)
            dst_keep[matched_dst_rel[hit_mask]] = False
            dst_pool = dst_pool[dst_keep]

    set_mesh_points_np(mesh_name, pts, space=om.MSpace.kObject, undoable=undoable)
    return matched_count
