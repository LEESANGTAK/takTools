import maya.cmds as cmds
import maya.api.OpenMaya as om
import numpy as np
from scipy.optimize import nnls

# 스킨 클러스터 찾기
def get_skin_cluster(mesh):
    history = cmds.listHistory(mesh)
    skin_clusters = cmds.ls(history, type='skinCluster')
    return skin_clusters[0] if skin_clusters else None

# 버텍스의 월드 좌표 구하기
def get_vertex_world_position(mesh, index):
    pos = cmds.pointPosition(f"{mesh}.vtx[{index}]", w=True)
    return om.MVector(pos)

# 조인트 리스트 가져오기
def get_influencing_joints(skin_cluster):
    return cmds.skinCluster(skin_cluster, query=True, influence=True)

# 각 조인트의 worldMatrix 가져오기
def get_joint_world_matrices(joints):
    matrices = []
    for joint in joints:
        matrix = cmds.getAttr(f"{joint}.worldMatrix[0]")
        matrices.append(np.array(matrix).reshape(4, 4))
    return matrices

# 각 조인트의 bindPreMatrix 가져오기
def get_bind_pre_matrices(all_joints, selected_joints, skin_cluster):
    matrices = []

    mapping = get_joint_skinCluster_index_mapping(all_joints, skin_cluster)

    for joint in selected_joints:
        index = mapping[joint]
        mat_flat = cmds.getAttr(f"{skin_cluster}.bindPreMatrix[{index}]")
        matrices.append(np.array(mat_flat).reshape(4, 4))
    return matrices

def get_bind_matrix(all_joints, joint, skin_cluster):
    mapping = get_joint_skinCluster_index_mapping(all_joints, skin_cluster)

    index = mapping[joint]
    mat_flat = cmds.getAttr(f"{skin_cluster}.bindPreMatrix[{index}]")
    bindPreMatrix = np.array(mat_flat).reshape(4, 4)

    return np.linalg.inv(bindPreMatrix)

def get_joint_skinCluster_index_mapping(all_joints, skin_cluster):
    connections = []
    for joint in all_joints:
        connectedSkins = cmds.listConnections(joint, s=False, d=True, plugs=True, type='skinCluster')
        skinClstConnection = [conn for conn in connectedSkins if f"{skin_cluster}.matrix" in conn ]
        if skinClstConnection:
            connections.append((joint, skinClstConnection[0]))

    mapping = {}
    for joint, conn in connections:
        index = int(conn.split('[')[-1].split(']')[0])
        mapping[joint] = index

    return mapping

# 현재 포즈로부터 바인드 상태 위치 추정
def estimate_bind_position(skin_cluster, mesh, vtx_index):
    joints = get_influencing_joints(skin_cluster)
    weights = cmds.skinPercent(skin_cluster, f"{mesh}.vtx[{vtx_index}]", query=True, value=True)
    v_deformed = get_vertex_world_position(mesh, vtx_index)
    v_deformed = np.array([v_deformed.x, v_deformed.y, v_deformed.z, 1.0])

    weighted_matrix = np.zeros((4, 4))
    for joint, weight in zip(joints, weights):
        if weight < 1e-4:
            continue

        joint_matrix = cmds.getAttr(f"{joint}.worldMatrix[0]")
        joint_matrix = np.array(joint_matrix).reshape(4, 4)

        pre_matrix = cmds.getAttr(f"{joint}.bindPose")
        pre_matrix = np.array(pre_matrix).reshape(4, 4)
        pre_matrix = np.linalg.inv(pre_matrix)

        weighted_matrix += (pre_matrix @ joint_matrix) * weight

    try:
        inv_matrix = np.linalg.inv(weighted_matrix)
    except np.linalg.LinAlgError:
        om.MGlobal.displayError("Matrix inversion failed.")
        return None

    v_bind = v_deformed @ inv_matrix

    return om.MVector(v_bind[0], v_bind[1], v_bind[2])

def select_joints_for_vertex(joint_weights, all_joints, skin, skinMesh, vtx_index, max_influences=4):
    # 1차적으로 유의미한 weights 기반 선택
    selected_joints = [j for j, w in joint_weights if w > 0.001][:max_influences]

    # 부족하면 거리 기반으로 보충
    if len(selected_joints) < max_influences:
        used = set(selected_joints)
        v_pos = estimate_bind_position(skin, skinMesh, vtx_index)

        joint_distances = []
        for j in all_joints:
            if j in used:
                continue
            bind_matrix = get_bind_matrix(all_joints, j, skin)
            pos = bind_matrix[3, :3]
            dist = np.linalg.norm(np.array(pos) - np.array(v_pos))
            joint_distances.append((j, dist))

        joint_distances.sort(key=lambda x: x[1])
        for j, _ in joint_distances:
            selected_joints.append(j)
            if len(selected_joints) == max_influences:
                break

    return selected_joints

def get_all_vertex_positions(mesh):
    sel_list = om.MSelectionList()
    sel_list.add(mesh)
    dag_path = sel_list.getDagPath(0)
    mfn_mesh = om.MFnMesh(dag_path)
    world_matrix = dag_path.inclusiveMatrix()

    points = mfn_mesh.getPoints(space=om.MSpace.kObject)
    points_np = np.array([[p.x, p.y, p.z, 1.0] for p in points])  # Nx4

    world_matrix_np = np.array(world_matrix).reshape(4, 4).T  # column-major → row-major
    world_positions = points_np @ world_matrix_np  # Nx4
    return world_positions[:, :3]  # Nx3

def get_modified_vertex_indices(skinMesh, sculptMesh, threshold=1e-4):
    pos_a = get_all_vertex_positions(skinMesh)
    pos_b = get_all_vertex_positions(sculptMesh)

    deltas = np.linalg.norm(pos_a - pos_b, axis=1)
    modified_indices = np.where(deltas > threshold)[0].tolist()
    return modified_indices


# 최종 가중치 계산 및 적용
def apply_inverse_weights_limited(skinMesh, sculptMesh, vtx_index, max_influences=4):
    skin = get_skin_cluster(skinMesh)
    if not skin:
        om.MGlobal.displayError("Skin cluster not found.")
        return

    all_joints = get_influencing_joints(skin)
    all_weights = cmds.skinPercent(skin, f"{skinMesh}.vtx[{vtx_index}]", query=True, value=True)
    joint_weights = list(zip(all_joints, all_weights))

    selected_joints = select_joints_for_vertex(joint_weights, all_joints, skin, skinMesh, vtx_index, max_influences)

    if not selected_joints:
        om.MGlobal.displayError("No significant joint influences.")
        return

    joint_matrices = get_joint_world_matrices(selected_joints)
    bind_matrices = get_bind_pre_matrices(all_joints, selected_joints, skin)

    v_bind_vec = estimate_bind_position(skin, skinMesh, vtx_index)
    if v_bind_vec is None:
        return

    v_bind = np.array([v_bind_vec.x, v_bind_vec.y, v_bind_vec.z, 1.0])
    v_target_vec = get_vertex_world_position(sculptMesh, vtx_index)
    v_target = np.array([v_target_vec.x, v_target_vec.y, v_target_vec.z])

    A = []
    for j_mat, b_mat in zip(joint_matrices, bind_matrices):
        skin_matrix = b_mat @ j_mat
        transformed = v_bind @ skin_matrix
        A.append(transformed[:3])

    A = np.array(A).T  # shape: (3, N)

    try:
        weights, _ = nnls(A, v_target)
    except Exception as e:
        om.MGlobal.displayWarning(f"NNLS failed: {e}")
        return

    if np.sum(weights) > 0:
        weights /= np.sum(weights)

    transform_weights = list(zip(selected_joints, weights.tolist()))
    cmds.skinPercent(skin, f"{skinMesh}.vtx[{vtx_index}]", transformValue=transform_weights)


def apply_inverse_weights_all(skinMesh, sculptMesh):
    sculptedVtxIndices = get_modified_vertex_indices(skinMesh, sculptMesh, threshold=1e-4)
    for vtx_index in sculptedVtxIndices:
        apply_inverse_weights_limited(skinMesh, sculptMesh, vtx_index, max_influences=4)
