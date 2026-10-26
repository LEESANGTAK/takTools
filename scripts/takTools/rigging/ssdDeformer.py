# encoding: utf-8
"""
Author: Sangtak Lee / takTools
Description: Smooth Skin Decomposition (SSD) Deformer Baker
Bakes complex deformers (Delta Mush, BlendShape, Wrap, Wire, Lattice, etc.)
into a pure SkinCluster with optimized joint weights via constrained least squares.
"""

from __future__ import print_function, division
import time
import math
import contextlib
import numpy as np
import scipy.optimize

from maya import cmds, mel
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

WIN_NAME = 'ssdDeformerWin'

REMOVABLE_DEFORMER_TYPES = [
    'blendShape',
    'deltaMush',
    'wrap',
    'wire',
    'lattice',
    'cluster',
    'nonLinear',
    'tension',
    'softMod',
    'shrinkWrap',
    'morph',
    'cMuscleSystem',
    'sculpt'
]

PRESERVED_DEFORMER_TYPES = [
    'skinCluster',
    'tweak'
]


@contextlib.contextmanager
def undoChunk(chunkName='ssdDeformerBake'):
    """Context manager to group scene modifications into a single undo block."""
    cmds.undoInfo(openChunk=True, chunkName=chunkName)
    try:
        yield
    finally:
        cmds.undoInfo(closeChunk=True)


@contextlib.contextmanager
def preserveJointStates(joints):
    """Context manager that saves joint transformations and restores them on exit."""
    saved_states = {}
    for j in joints:
        if cmds.objExists(j):
            saved_states[j] = {
                't': cmds.getAttr('{}.translate'.format(j))[0],
                'r': cmds.getAttr('{}.rotate'.format(j))[0],
                'ro': cmds.getAttr('{}.rotateOrder'.format(j))
            }
    try:
        yield
    finally:
        for j, state in saved_states.items():
            if cmds.objExists(j):
                try:
                    cmds.setAttr('{}.rotate'.format(j), *state['r'])
                    cmds.setAttr('{}.translate'.format(j), *state['t'])
                except Exception as e:
                    print("Warning: Failed to restore state for {}: {}".format(j, e))


def getMeshDagPath(meshName):
    """Get MDagPath for given mesh transform or shape node."""
    sel = om.MSelectionList()
    sel.add(meshName)
    dag = sel.getDagPath(0)
    if dag.apiType() == om.MFn.kTransform:
        dag.extendToShape()
    return dag


def getMeshWorldPoints(meshDagPath):
    """Return vertex positions in world space as an (N, 3) float64 numpy array."""
    meshFn = om.MFnMesh(meshDagPath)
    points = meshFn.getPoints(om.MSpace.kWorld)
    num_points = len(points)
    arr = np.empty((num_points, 3), dtype=np.float64)
    for i in range(num_points):
        p = points[i]
        arr[i, 0] = p.x
        arr[i, 1] = p.y
        arr[i, 2] = p.z
    return arr


def getJointWorldMatrices(joints):
    """Return a list of 4x4 row-major numpy transformation matrices for joints in world space."""
    matrices = []
    sel = om.MSelectionList()
    for j in joints:
        sel.clear()
        sel.add(j)
        dag = sel.getDagPath(0)
        m = dag.inclusiveMatrix()
        # Row-major 4x4 array (Maya convention: v_world = v_local @ M)
        matrices.append(np.array(list(m), dtype=np.float64).reshape((4, 4)))
    return matrices


def findRelatedSkinCluster(mesh):
    """Find skinCluster associated with mesh or return None."""
    sc = mel.eval('findRelatedSkinCluster "{}"'.format(mesh))
    if sc and cmds.objExists(sc):
        return sc
    hist = cmds.listHistory(mesh, pdo=True) or []
    scs = cmds.ls(hist, type='skinCluster')
    return scs[0] if scs else None


def findMeshDeformers(mesh):
    """Return a list of non-skinCluster deformer nodes currently driving the mesh."""
    hist = cmds.listHistory(mesh, pdo=True) or []
    deformers = []
    sc = findRelatedSkinCluster(mesh)
    for node in hist:
        if node == sc or cmds.nodeType(node) in PRESERVED_DEFORMER_TYPES:
            continue
        nodeType = cmds.nodeType(node)
        if nodeType in REMOVABLE_DEFORMER_TYPES or 'deform' in nodeType.lower():
            if node not in deformers:
                deformers.append(node)
    return deformers


def parseTargetInputs(mesh=None, influences=None):
    """Parse and validate mesh and influence joints.
    
    If mesh is None, uses first selected mesh.
    If influences is None, uses skinCluster influences, or selected joints.
    """
    selected = cmds.ls(sl=True) or []

    # 1. Resolve target mesh
    if not mesh:
        mesh_candidates = []
        for item in selected:
            shapes = cmds.listRelatives(item, s=True, type='mesh', ni=True) or []
            if shapes or cmds.nodeType(item) == 'mesh':
                mesh_candidates.append(item)
        if not mesh_candidates:
            raise RuntimeError("No target mesh specified and no polygon mesh selected.")
        mesh = mesh_candidates[0]

    # Verify mesh exists and is valid
    if not cmds.objExists(mesh):
        raise RuntimeError("Target mesh '{}' does not exist.".format(mesh))
    shapes = cmds.listRelatives(mesh, s=True, type='mesh', ni=True) or []
    if not shapes and cmds.nodeType(mesh) != 'mesh':
        raise RuntimeError("Object '{}' is not a polygon mesh.".format(mesh))

    # 2. Resolve influences
    if influences is None or len(influences) == 0:
        selected_joints = cmds.ls(selected, type='joint')
        if selected_joints:
            influences = selected_joints
        else:
            sc = findRelatedSkinCluster(mesh)
            if sc:
                influences = cmds.skinCluster(sc, query=True, influence=True) or []
            if not influences:
                raise RuntimeError(
                    "No influence joints found for mesh '{}'. "
                    "Please specify influences or bind a preliminary skinCluster.".format(mesh)
                )

    # Filter valid existing joints
    valid_influences = [j for j in influences if cmds.objExists(j) and cmds.nodeType(j) == 'joint']
    if not valid_influences:
        raise RuntimeError("None of the specified influences are valid joint nodes.")

    return mesh, valid_influences


def generateArticulationPoses(joints, angles=(30.0, 45.0, 60.0), includeCombinations=True, includeChains=True):
    """Generate a diverse set of rotational poses to thoroughly sample joint articulation."""
    poses = []
    # 1. Rest pose (Zero rotation)
    poses.append({j: (0.0, 0.0, 0.0) for j in joints})

    # 2. Single axis sweeps for every joint
    for j in joints:
        for ang in angles:
            for sign in [1.0, -1.0]:
                val = ang * sign
                # Pitch (X)
                p_x = {k: (0.0, 0.0, 0.0) for k in joints}
                p_x[j] = (val, 0.0, 0.0)
                poses.append(p_x)

                # Yaw (Y)
                p_y = {k: (0.0, 0.0, 0.0) for k in joints}
                p_y[j] = (0.0, val, 0.0)
                poses.append(p_y)

                # Roll (Z)
                p_z = {k: (0.0, 0.0, 0.0) for k in joints}
                p_z[j] = (0.0, 0.0, val)
                poses.append(p_z)

    # 3. Multi-axis diagonal combinations
    if includeCombinations:
        diag_angle = 35.0
        for j in joints:
            for s1, s2 in [(1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0)]:
                p_xy = {k: (0.0, 0.0, 0.0) for k in joints}
                p_xy[j] = (diag_angle * s1, diag_angle * s2, 0.0)
                poses.append(p_xy)

                p_xz = {k: (0.0, 0.0, 0.0) for k in joints}
                p_xz[j] = (diag_angle * s1, 0.0, diag_angle * s2)
                poses.append(p_xz)

    # 4. Joint chain synchronized bend poses
    if includeChains and len(joints) > 1:
        chain_angles = [25.0, 45.0]
        for ang in chain_angles:
            for sign in [1.0, -1.0]:
                val = ang * sign
                p_chain_x = {j: (val, 0.0, 0.0) for j in joints}
                poses.append(p_chain_x)
                p_chain_z = {j: (0.0, 0.0, val) for j in joints}
                poses.append(p_chain_z)
                p_wave = {j: (val, 0.0, val * 0.5) for j in joints}
                poses.append(p_wave)

    return poses


def sampleDeformationData(mesh, joints, poses=None, useTimeline=False, startFrame=None, endFrame=None, step=1, progressCallback=None):
    """Sample deformed mesh vertex positions and joint matrices across poses."""
    meshDag = getMeshDagPath(mesh)
    J = len(joints)

    V0 = getMeshWorldPoints(meshDag)
    N = len(V0)
    rest_matrices = getJointWorldMatrices(joints)

    recorded_targets = []
    recorded_M = []

    if useTimeline:
        if startFrame is None:
            startFrame = int(cmds.playbackOptions(q=True, min=True))
        if endFrame is None:
            endFrame = int(cmds.playbackOptions(q=True, max=True))
        frames = list(range(int(startFrame), int(endFrame) + 1, max(1, int(step))))
        total_steps = len(frames)

        curr_time = cmds.currentTime(q=True)
        try:
            for idx, frame in enumerate(frames):
                if progressCallback and not progressCallback(idx, total_steps, "Sampling frame {}/{}".format(frame, endFrame)):
                    raise RuntimeError("SSD sampling cancelled by user.")
                cmds.currentTime(frame, update=True)
                cmds.dgeval(mesh)
                recorded_targets.append(getMeshWorldPoints(meshDag))
                recorded_M.append(getJointWorldMatrices(joints))
        finally:
            cmds.currentTime(curr_time, update=True)
    else:
        if poses is None:
            poses = generateArticulationPoses(joints)
        total_steps = len(poses)

        with preserveJointStates(joints):
            for idx, pose in enumerate(poses):
                if progressCallback and not progressCallback(idx, total_steps, "Sampling articulation pose {}/{}".format(idx + 1, total_steps)):
                    raise RuntimeError("SSD sampling cancelled by user.")

                for j, (rx, ry, rz) in pose.items():
                    cmds.setAttr('{}.rotate'.format(j), rx, ry, rz)
                cmds.dgeval(mesh)

                recorded_targets.append(getMeshWorldPoints(meshDag))
                recorded_M.append(getJointWorldMatrices(joints))

    F = len(recorded_targets)
    targets_np = np.array(recorded_targets, dtype=np.float64)
    joint_M_np = np.array(recorded_M, dtype=np.float64)

    return V0, targets_np, joint_M_np, rest_matrices


def solveSmoothSkinDecomposition(V0, targets, joint_M, rest_matrices, maxInfluences=4, maxCandidates=16, ridgeReg=1e-3, sumPenalty=100.0, progressCallback=None):
    """Solve constrained least squares (NNLS) with ridge regularization and distance priors."""
    F, N, _ = targets.shape
    J = len(rest_matrices)

    B_inv = [np.linalg.inv(rest_matrices[j]) for j in range(J)]
    joint_rest_positions = np.array([rest_matrices[j][3, :3] for j in range(J)], dtype=np.float64)

    # Vectorized computation of predicted positions
    V0_h = np.hstack([V0, np.ones((N, 1), dtype=np.float64)])  # (N, 4)
    P = np.empty((F, J, N, 3), dtype=np.float64)

    for f in range(F):
        for j in range(J):
            T_jf = B_inv[j] @ joint_M[f, j]
            P_jf_h = V0_h @ T_jf
            P[f, j] = P_jf_h[:, :3]

    weights = np.zeros((N, J), dtype=np.float64)
    sqrt_ridge = np.sqrt(max(1e-9, ridgeReg))
    filterCandidates = (J > maxCandidates and maxCandidates >= maxInfluences)

    for i in range(N):
        if progressCallback and (i % 200 == 0 or i == N - 1):
            if not progressCallback(i, N, "Solving skin weights for vertex {}/{}...".format(i + 1, N)):
                raise RuntimeError("SSD optimization cancelled by user.")

        v_pos = V0[i]
        dists = np.linalg.norm(joint_rest_positions - v_pos, axis=1)

        if filterCandidates:
            cand_indices = np.argsort(dists)[:maxCandidates]
        else:
            cand_indices = np.arange(J)

        c_count = len(cand_indices)
        cand_dists = dists[cand_indices]
        inv_dists = 1.0 / np.maximum(cand_dists, 0.05)**2
        w0 = inv_dists / np.sum(inv_dists)

        A_blocks = []
        b_blocks = []
        for f in range(F):
            A_f = P[f, cand_indices, i, :].T
            A_blocks.append(A_f)
            b_blocks.append(targets[f, i])

        A = np.vstack(A_blocks)
        b = np.concatenate(b_blocks)

        A_aug = np.vstack([
            A,
            np.full((1, c_count), sumPenalty),
            np.eye(c_count) * sqrt_ridge
        ])
        b_aug = np.concatenate([
            b,
            [sumPenalty],
            w0 * sqrt_ridge
        ])

        w_cand, _ = scipy.optimize.nnls(A_aug, b_aug)
        w_sum = np.sum(w_cand)
        if w_sum > 1e-6:
            w_cand = w_cand / w_sum
        else:
            w_cand = w0

        if c_count > maxInfluences:
            top_k_indices = np.argsort(w_cand)[-maxInfluences:]
            pruned_w = np.zeros(c_count, dtype=np.float64)
            pruned_w[top_k_indices] = w_cand[top_k_indices]
            p_sum = np.sum(pruned_w)
            if p_sum > 1e-6:
                w_cand = pruned_w / p_sum

        weights[i, cand_indices] = w_cand

    return weights


def applySkinWeightsToMesh(mesh, joints, weights, maxInfluences=4, deleteOtherDeformers=True, disableOtherDeformers=False):
    """Assign computed SSD weights to SkinCluster and clean up other deformers."""
    meshDag = getMeshDagPath(mesh)
    N, J = weights.shape

    # 1. Obtain or create skinCluster
    sc = findRelatedSkinCluster(mesh)
    if not sc:
        sc = cmds.skinCluster(
            joints,
            mesh,
            toSelectedBones=True,
            maximumInfluences=maxInfluences,
            normalizeWeights=1,
            name='{}_skinCluster'.format(mesh)
        )[0]
    else:
        existing_infs = cmds.skinCluster(sc, q=True, influence=True) or []
        for j in joints:
            if j not in existing_infs:
                cmds.skinCluster(sc, edit=True, addInfluence=j, weight=0.0)

    # 2. Deformer cleanup (BlendShape, DeltaMush, Wire, Wrap, etc.)
    removed_deformers = []
    other_deformers = findMeshDeformers(mesh)
    if deleteOtherDeformers:
        for df in other_deformers:
            try:
                cmds.delete(df)
                removed_deformers.append(df)
            except Exception as e:
                print("Notice: Could not delete deformer {}: {}".format(df, e))
    elif disableOtherDeformers:
        for df in other_deformers:
            if cmds.attributeQuery('envelope', node=df, exists=True):
                try:
                    cmds.setAttr('{}.envelope'.format(df), 0.0)
                    removed_deformers.append(df + " (disabled)")
                except Exception:
                    pass

    # 3. Apply weights via OpenMaya 2.0 MFnSkinCluster
    sel = om.MSelectionList()
    sel.add(sc)
    skinObj = sel.getDependNode(0)
    skinFn = oma.MFnSkinCluster(skinObj)

    compFn = om.MFnSingleIndexedComponent()
    comp = compFn.create(om.MFn.kMeshVertComponent)
    compFn.setCompleteData(N)

    infDagPaths = skinFn.influenceObjects()
    infNameMap = {}
    for idx, dag in enumerate(infDagPaths):
        infNameMap[dag.partialPathName()] = idx
        infNameMap[dag.fullPathName()] = idx

    num_sc_infs = len(infDagPaths)
    full_weights = np.zeros((N, num_sc_infs), dtype=np.float64)

    for our_idx, j in enumerate(joints):
        j_short = j.split('|')[-1]
        sc_idx = infNameMap.get(j, infNameMap.get(j_short, None))
        if sc_idx is not None:
            full_weights[:, sc_idx] = weights[:, our_idx]

    infIndices = om.MIntArray(range(num_sc_infs))
    flat_weights = om.MDoubleArray(full_weights.flatten().tolist())
    skinFn.setWeights(meshDag, comp, infIndices, flat_weights, False)

    cmds.setAttr('{}.normalizeWeights'.format(sc), 1)
    return sc, removed_deformers


def bakeSSD(
    mesh=None,
    influences=None,
    maxInfluences=4,
    angles=(30.0, 45.0, 60.0),
    includeCombinations=True,
    includeChains=True,
    useTimeline=False,
    startFrame=None,
    endFrame=None,
    step=1,
    deleteOtherDeformers=True,
    disableOtherDeformers=False,
    maxCandidates=16,
    ridgeReg=1e-3,
    sumPenalty=100.0,
    showProgress=True
):
    """Bake complex deformers on mesh into a pure SkinCluster using Smooth Skin Decomposition.
    
    Args:
        mesh (str, optional): Target mesh transform or shape. Defaults to current selection.
        influences (list of str, optional): Influence joints. Defaults to existing skinCluster joints.
        maxInfluences (int): Maximum influences allowed per vertex (default: 4).
        angles (tuple of float): Rotation angles for articulation (default: 30, 45, 60).
        includeCombinations (bool): Include multi-axis combined poses (default: True).
        includeChains (bool): Include synchronized chain bend poses (default: True).
        useTimeline (bool): Sample from scene timeline animation instead of auto articulation.
        startFrame (int, optional): Timeline start frame.
        endFrame (int, optional): Timeline end frame.
        step (int): Frame increment for timeline sampling.
        deleteOtherDeformers (bool): Delete other deformers (Delta Mush, BlendShape, etc.) after baking.
        disableOtherDeformers (bool): Set envelope=0 on other deformers instead of deleting.
        maxCandidates (int): Closeness candidate joints filter for speed & spatial locality.
        ridgeReg (float): Ridge regularization parameter to ensure non-singularity.
        sumPenalty (float): Penalty weight for partition of unity sum(w) = 1.
        showProgress (bool): Display Maya progress window dialog.
    
    Returns:
        dict: Result summary with skinCluster name, error metrics, and removed deformers.
    """
    startTime = time.time()

    mesh, influences = parseTargetInputs(mesh=mesh, influences=influences)
    print("=" * 60)
    print("[takTools SSD] Starting Smooth Skin Decomposition Baker...")
    print("  Target Mesh:        {}".format(mesh))
    print("  Influences ({}):    {}".format(len(influences), influences[:5] + (['...'] if len(influences) > 5 else [])))
    print("  Max Influences:     {}".format(maxInfluences))
    print("  Deformer Cleanup:   {}".format("Delete" if deleteOtherDeformers else ("Disable" if disableOtherDeformers else "None")))
    print("=" * 60)

    progressActive = False
    if showProgress and not cmds.about(batch=True):
        try:
            cmds.progressWindow(
                title='takTools SSD Baker',
                status='Preparing articulation poses...',
                progress=0,
                min=0,
                max=100,
                isInterruptable=True
            )
            progressActive = True
        except Exception:
            progressActive = False

    def progressCallback(current, total, statusText):
        if progressActive:
            if cmds.progressWindow(q=True, isCancelled=True):
                cmds.progressWindow(endProgress=True)
                return False
            percent = int((float(current) / float(max(1, total))) * 100)
            cmds.progressWindow(edit=True, progress=percent, status=statusText)
        return True

    try:
        with undoChunk('ssdDeformerBake'):
            if not useTimeline:
                poses = generateArticulationPoses(
                    influences,
                    angles=angles,
                    includeCombinations=includeCombinations,
                    includeChains=includeChains
                )
            else:
                poses = None

            V0, targets, joint_M, rest_matrices = sampleDeformationData(
                mesh=mesh,
                joints=influences,
                poses=poses,
                useTimeline=useTimeline,
                startFrame=startFrame,
                endFrame=endFrame,
                step=step,
                progressCallback=progressCallback
            )

            N = len(V0)
            F = len(targets)
            print("[takTools SSD] Recorded {} poses for {} vertices.".format(F, N))

            weights = solveSmoothSkinDecomposition(
                V0=V0,
                targets=targets,
                joint_M=joint_M,
                rest_matrices=rest_matrices,
                maxInfluences=maxInfluences,
                maxCandidates=maxCandidates,
                ridgeReg=ridgeReg,
                sumPenalty=sumPenalty,
                progressCallback=progressCallback
            )

            if progressActive:
                cmds.progressWindow(edit=True, progress=95, status="Applying SkinCluster weights and cleaning deformers...")

            skinClusterNode, removed_deformers = applySkinWeightsToMesh(
                mesh=mesh,
                joints=influences,
                weights=weights,
                maxInfluences=maxInfluences,
                deleteOtherDeformers=deleteOtherDeformers,
                disableOtherDeformers=disableOtherDeformers
            )

    finally:
        if progressActive:
            try:
                cmds.progressWindow(endProgress=True)
            except Exception:
                pass

    elapsed = time.time() - startTime
    print("-" * 60)
    print("[takTools SSD] Complete in {:.2f}s!".format(elapsed))
    print("  SkinCluster:       {}".format(skinClusterNode))
    print("  Cleaned Deformers: {}".format(removed_deformers if removed_deformers else "None"))
    print("=" * 60)

    summary = {
        'mesh': mesh,
        'skinCluster': skinClusterNode,
        'influences': influences,
        'numVertices': N,
        'numPoses': F,
        'removedDeformers': removed_deformers,
        'elapsedTime': elapsed
    }
    return summary


# ---------------------------------------------------------------------------
# Maya GUI Dialog
# ---------------------------------------------------------------------------

def showUI(parent=None):
    """Show the Smooth Skin Decomposition (SSD) GUI dialog."""
    if cmds.window(WIN_NAME, exists=True):
        cmds.deleteUI(WIN_NAME)

    kwargs = {'title': 'SSD (Smooth Skin Decomposition)', 'tlb': True}
    if parent and cmds.window(parent, exists=True):
        kwargs['p'] = parent

    cmds.window(WIN_NAME, **kwargs)

    mainCol = cmds.columnLayout(adj=True, rs=6)

    # 1. Target Mesh & Influences Section
    cmds.frameLayout(label='Targets', p=mainCol, cll=False)
    cmds.columnLayout(adj=True, rs=4)

    # Mesh row
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 220, 50), adj=2)
    cmds.text(label='Mesh:')
    cmds.textField('ssdMeshTxtFld', text='', placeholderText='Select polygon mesh...')
    cmds.button(label='<<<', c=lambda x: _loadSelectedMesh(), ann='Load selected mesh')
    cmds.setParent('..')

    # Influences row
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 220, 50), adj=2)
    cmds.text(label='Influences:')
    cmds.textField('ssdInfsTxtFld', text='', placeholderText='Auto from SkinCluster or joints...')
    cmds.button(label='<<<', c=lambda x: _loadSelectedInfluences(), ann='Load selected joints or skin influences')
    cmds.setParent('..')

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(150, 150))
    cmds.button(label='Auto Detect Infs', c=lambda x: _autoDetectInfluences(), ann='Auto detect influences from mesh skinCluster')
    cmds.text('ssdInfCountTxt', label='0 influences')
    cmds.setParent('..')

    cmds.setParent('..')  # End Targets frame

    # 2. Settings Section
    cmds.frameLayout(label='Settings', p=mainCol, cll=False)
    cmds.columnLayout(adj=True, rs=4)

    # Articulation Angles
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(130, 200), adj=2)
    cmds.text(label='Angles (deg):')
    cmds.textField('ssdAnglesTxtFld', text='30, 45, 60')
    cmds.setParent('..')

    # Max Influences Option Menu
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(130, 200), adj=2)
    cmds.text(label='Max Influences:')
    cmds.optionMenu('ssdMaxInfsOptMenu')
    cmds.menuItem(label='2')
    cmds.menuItem(label='4')
    cmds.menuItem(label='8')
    cmds.menuItem(label='12')
    cmds.optionMenu('ssdMaxInfsOptMenu', e=True, v='4')
    cmds.setParent('..')

    # Checkboxes
    cmds.checkBox('ssdDiagCheckBox', label='Multi-axis Diagonal Poses', v=True)
    cmds.checkBox('ssdChainsCheckBox', label='Synchronized Chain Bend Poses', v=True)
    cmds.checkBox('ssdDeleteDeformersCheckBox', label='Delete other deformers after baking', v=True)

    cmds.setParent('..')  # End Settings frame

    # 3. Action Buttons
    cmds.separator(h=8, style='none', p=mainCol)
    cmds.button(
        label='Decompose Skin (Bake SSD)',
        h=36,
        bgc=[0.2, 0.45, 0.65],
        c=lambda x: _runBakeFromUI(),
        p=mainCol,
        ann='Run SSD decomposition and replace deformers with SkinCluster'
    )

    cmds.showWindow(WIN_NAME)
    cmds.window(WIN_NAME, e=True, w=340, h=320)

    # Automatically initialize with current selection
    _initFromSelection()


def _initFromSelection():
    selected = cmds.ls(sl=True) or []
    for item in selected:
        shapes = cmds.listRelatives(item, s=True, type='mesh', ni=True) or []
        if shapes or cmds.nodeType(item) == 'mesh':
            cmds.textField('ssdMeshTxtFld', e=True, text=item)
            _autoDetectInfluences()
            break


def _loadSelectedMesh():
    selected = cmds.ls(sl=True) or []
    for item in selected:
        shapes = cmds.listRelatives(item, s=True, type='mesh', ni=True) or []
        if shapes or cmds.nodeType(item) == 'mesh':
            cmds.textField('ssdMeshTxtFld', e=True, text=item)
            _autoDetectInfluences()
            return
    cmds.warning("Please select a polygon mesh.")


def _loadSelectedInfluences():
    selected = cmds.ls(sl=True, type='joint') or []
    if selected:
        cmds.textField('ssdInfsTxtFld', e=True, text=', '.join(selected))
        cmds.text('ssdInfCountTxt', e=True, label='{} influences'.format(len(selected)))
    else:
        cmds.warning("No joints selected.")


def _autoDetectInfluences():
    meshName = cmds.textField('ssdMeshTxtFld', q=True, text=True).strip()
    if not meshName or not cmds.objExists(meshName):
        return
    sc = findRelatedSkinCluster(meshName)
    if sc:
        infs = cmds.skinCluster(sc, q=True, influence=True) or []
        cmds.textField('ssdInfsTxtFld', e=True, text=', '.join(infs))
        cmds.text('ssdInfCountTxt', e=True, label='{} influences'.format(len(infs)))
    else:
        cmds.text('ssdInfCountTxt', e=True, label='No skinCluster')


def _runBakeFromUI():
    meshName = cmds.textField('ssdMeshTxtFld', q=True, text=True).strip()
    if not meshName:
        cmds.warning("Please specify a target mesh.")
        return

    infText = cmds.textField('ssdInfsTxtFld', q=True, text=True).strip()
    infs = [j.strip() for j in infText.split(',') if j.strip()] if infText else None

    # Parse angles
    anglesText = cmds.textField('ssdAnglesTxtFld', q=True, text=True).strip()
    try:
        angles = tuple([float(a.strip()) for a in anglesText.split(',') if a.strip()])
    except ValueError:
        angles = (30.0, 45.0, 60.0)

    maxInf = int(cmds.optionMenu('ssdMaxInfsOptMenu', q=True, v=True))
    includeDiag = cmds.checkBox('ssdDiagCheckBox', q=True, v=True)
    includeChains = cmds.checkBox('ssdChainsCheckBox', q=True, v=True)
    deleteDeformers = cmds.checkBox('ssdDeleteDeformersCheckBox', q=True, v=True)

    try:
        res = bakeSSD(
            mesh=meshName,
            influences=infs,
            maxInfluences=maxInf,
            angles=angles,
            includeCombinations=includeDiag,
            includeChains=includeChains,
            deleteOtherDeformers=deleteDeformers
        )
        msg = "SSD Baker successfully completed in {:.2f}s!\nSkinCluster: {}\nRemoved deformers: {}".format(
            res['elapsedTime'],
            res['skinCluster'],
            res['removedDeformers'] if res['removedDeformers'] else "None"
        )
        cmds.confirmDialog(title='SSD Complete', message=msg, button=['OK'])
    except Exception as e:
        cmds.confirmDialog(title='SSD Error', message=str(e), button=['OK'], icon='critical')
