"""
SymMesh - Fast OpenMaya / NumPy Mesh Symmetry Tool

Maya Transfer-Attributes-style symmetry sampling (World, Local, UV, Topology)
with separated Symmetry Setup (Build Symmetry Data) and Operations (Mirror/Flip/Revert) tabs.
"""

from maya import cmds
from maya import OpenMayaUI as omui
from maya.api import OpenMaya as om
import numpy as np

from ..utils import sym_mesh as symUtil

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtWidgets, QtGui, QtCore
    from shiboken import wrapInstance
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance
else:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance


WINDOW_OBJECT_NAME = "symMeshWin"
WINDOW_TITLE = "SymMesh"
LANGUAGE_OPTION_VAR = "symMeshLanguage"

_ORIGIN_VALUES = (symUtil.ORIGIN_PIVOT, symUtil.ORIGIN_ZERO, symUtil.ORIGIN_BBOX)
_FALLBACK_VALUES = (symUtil.SAMPLE_LOCAL, symUtil.SAMPLE_WORLD, symUtil.SAMPLE_UV, "none")


_TR = {
    "en": {
        "win_title": "SymMesh",
        "menu_ops": "Operations",
        "menu_tools": "Tools",
        "menu_lang": "Language",
        "lang_en": "English",
        "lang_ko": "한국어 (Korean)",
        # Tabs
        "tab_setup": "1. Symmetry Setup",
        "tab_ops": "2. Operations",
        # Operations menu
        "op_copy": "Copy A to B",
        "op_copy_tt": "Copy vertex positions from mesh A to mesh B (select A then B).",
        "op_add": "Add A to B",
        "op_add_tt": "Add (A - Base) delta onto mesh B (select A then B).",
        "op_sub": "Subtract A from B",
        "op_sub_tt": "Subtract (A - Base) delta from mesh B (select A then B).",
        "op_mir_copy": "Copy Mirror A to B",
        "op_mir_copy_tt": "Mirror mesh A across symmetry map and copy to mesh B.",
        "op_mir_add": "Add Mirror A to B",
        "op_mir_add_tt": "Mirror (A - Base) delta and add onto mesh B.",
        "op_mir_sub": "Subtract Mirror A from B",
        "op_mir_sub_tt": "Mirror (A - Base) delta and subtract from mesh B.",
        "op_b_add": "Add A to B (Use B as Base)",
        "op_b_add_tt": "Add (A - B) delta onto B (select A then B).",
        "op_b_sub": "Subtract A from B (Use B as Base)",
        "op_b_sub_tt": "Subtract (A - B) delta from B (select A then B).",
        "op_b_mir_add": "Add Mirror A to B (Use B as Base)",
        "op_b_mir_add_tt": "Mirror (A - B) delta and add onto B.",
        "op_b_mir_sub": "Subtract Mirror A from B (Use B as Base)",
        "op_b_mir_sub_tt": "Mirror (A - B) delta and subtract from B.",
        # Tools menu
        "tool_sel_mirror": "Selection Mirror",
        "tool_sel_mirror_tt": "Select the symmetrical counterpart vertices for the current vertex selection.",
        "tool_sel_moved": "Select Moved Verts",
        "tool_sel_moved_tt": "Select vertices on the target mesh whose positions differ from the base mesh beyond Tolerance.",
        "tool_restore": "Attempt To Restore Symmetry...",
        "tool_restore_tt": "Iteratively match and symmetrize vertices on an almost-symmetrical mesh.",
        "tool_sel_asym": "Select Unmatched / Asymmetric Verts",
        "tool_sel_asym_tt": "Select vertices on the base mesh that have no symmetrical partner.",
        "tool_sel_ctr": "Select Center Seam Verts",
        "tool_sel_ctr_tt": "Select vertices on the base mesh lying on the symmetry center seam.",
        "tool_clear_cache": "Clear Symmetry Data",
        "tool_clear_cache_tt": "Clear the built symmetry mapping table and base mesh.",
        # Tab 1: Step 1 Base Mesh
        "grp_base": "1. Base Mesh",
        "btn_load_base": "Load Selected",
        "btn_load_base_tt": "Set the currently selected polygon mesh as the Base Mesh.",
        "btn_clear": "Clear",
        "btn_clear_tt": "Clear the Base Mesh and reset built symmetry data.",
        "base_ph": "<Enter or Load Base Mesh>",
        "base_field_tt": "Base mesh name used to build the symmetry vertex mapping.",
        # Tab 1: Step 2 Sample Space
        "grp_sample": "2. Sample Space (Transfer Attributes Style)",
        "ss_world": "World",
        "ss_world_tt": "Match symmetrical vertices using world-space 3D coordinates.",
        "ss_local": "Local",
        "ss_local_tt": "Match symmetrical vertices using object/local-space 3D coordinates (ignores world transforms).",
        "ss_uv": "UV",
        "ss_uv_tt": "Match symmetrical vertices in UV space (works even when 3D geometry is posed or sculpted asymmetrically).",
        "ss_topo": "Topology",
        "ss_topo_tt": "Match symmetrical vertices by mesh edge/face topology from center edge(s), independent of 3D vertex positions.",
        "lbl_axis": "Symmetry Axis:",
        "axis_x": "YZ (X)",
        "axis_y": "XZ (Y)",
        "axis_z": "XY (Z)",
        "axis_tt": "Plane across which vertices are mirrored or flipped.",
        "lbl_origin": "Mirror Origin:",
        "origin_items": ("Pivot", "Origin (0)", "Bounding Box"),
        "origin_tt": "Reference position for the symmetry plane: object Pivot, coordinate Origin (0), or Bounding Box center.",
        "lbl_tol": "Tolerance:",
        "tol_tt": "Search distance tolerance for spatial matching, center detection, and Select Moved Verts.",
        # UV options
        "lbl_uv_set": "UV Set:",
        "uv_set_tt": "UV set name used for UV-space symmetry matching.",
        "btn_refresh": "Refresh",
        "btn_refresh_tt": "Reload available UV sets from the Base Mesh or selected mesh.",
        "lbl_uv_axis": "UV Mirror Axis:",
        "uv_u": "U",
        "uv_v": "V",
        "uv_axis_tt": "Axis in UV space (U or V) across which UV coordinates are mirrored.",
        "lbl_uv_center": "UV Center:",
        "uv_center_tt": "Coordinate on the UV mirror axis where the symmetry line lies (default 0.5).",
        "chk_uv_auto": "Auto (BBox)",
        "chk_uv_auto_tt": "Automatically compute UV mirror center from the UV bounding box.",
        "lbl_uv_tol": "UV Tolerance:",
        "uv_tol_tt": "Maximum distance in UV space to consider two UVs symmetrical.",
        # Topology options
        "lbl_seed_edges": "Center Edge(s):",
        "seed_edges_ph": "Auto-detect, or load center edge(s)",
        "seed_edges_tt": "Edge index or indices on the symmetry seam used as BFS starting seeds. Leave blank to auto-detect.",
        "btn_load_sel": "Load Sel",
        "btn_load_sel_tt": "Load currently selected mesh edge(s) as center seam seed(s).",
        "btn_clear_edges_tt": "Clear loaded center edge(s) and revert to auto-detection.",
        "lbl_detached": "Detached Shells:",
        "fallback_items": ("Auto (Local Space)", "Auto (World Space)", "Auto (UV Space)", "None (Topology Only)"),
        "fallback_tt": "How to match disconnected mesh shells that have no center edge (e.g., eyeballs, teeth).",
        # Tab 1: Step 3 Build Symmetry Data
        "grp_build": "3. Build Symmetry Data",
        "btn_build_sym": "Build Symmetry Data",
        "btn_build_sym_tt": "Generate and cache left/right vertex symmetry mapping from the Base Mesh and Sample Space.",
        "status_empty": "1) Load Base Mesh  ->  2) Choose Sample Space  ->  3) Click 'Build Symmetry Data'.",
        "status_base_ready": "Base Mesh '{mesh}' ready. Choose Sample Space and click 'Build Symmetry Data'.",
        "status_sym": "Success | {pairs} pairs, {ctr} center ({ms:.1f} ms)",
        "status_asym": "Partial match: {unm} unmatched vert(s), {pairs} pairs ({ms:.1f} ms).",
        "status_err": "Failed: {err}",
        "hint_try_spatial": "Tip: If the mesh is asymmetrically sculpted or posed, try 'Topology' (with a center edge) or 'UV' Sample Space.",
        "hint_try_uv": "Tip: Check UV Set / UV Center / UV Tolerance, or try 'Topology' or 'Local' Sample Space.",
        "hint_try_topo": "Tip: Select center seam edge(s) and click 'Load Sel', or try 'UV' / 'Local' Sample Space.",
        "btn_sel_unmatched": "Select Unmatched",
        "btn_sel_unmatched_tt": "Select vertices on the base mesh that could not be paired.",
        "btn_goto_ops": "Go to Operations ->",
        "btn_goto_ops_tt": "Switch to the Operations tab to Mirror, Flip, or Revert meshes.",
        # Tab 2: Operations Summary Banner
        "ops_banner_none": "No Symmetry Data built yet. Build it in '1. Symmetry Setup' tab first.",
        "ops_banner_ok": "Active Base: {mesh}  [{space}]  |  {pairs} pairs, {ctr} center",
        "ops_banner_asym": "Active Base: {mesh}  [{space}]  |  {pairs} pairs ({unm} unmatched)",
        # Tab 2: Mirror & Flip Group
        "grp_mf": "Mirror & Flip",
        "chk_neg_to_pos": "Operate -{axis} to +{axis}",
        "chk_neg_to_pos_tt": "When checked, mirror from -{axis} to +{axis}. When unchecked, mirror from +{axis} to -{axis}.",
        "btn_mirror": "Mirror Selected",
        "btn_mirror_tt": "Copy vertex positions from the source side to the opposite side across the symmetry plane (whole mesh if object selected).",
        "btn_flip": "Flip Selected",
        "btn_flip_tt": "Swap symmetrical vertex pairs across the symmetry plane (whole mesh if object selected).",
        # Tab 2: Revert Group
        "grp_rev": "Revert to Base",
        "btn_revert": "Revert Selected to Base",
        "btn_revert_tt": "Revert selected vertices (or whole mesh) 100% to the base mesh. Right-click for percentage presets and alternate base options.",
        "rev_base_orig": "Revert Base: Original",
        "rev_base_alt": "Revert Base: {name}",
        "rev_slider_tt": "Drag to interactively blend selected vertices toward the revert base.",
        "rev_spin_tt": "Exact percentage (0% = current shape, 100% = base shape) to revert.",
        "btn_commit": "Commit",
        "btn_commit_tt": "Reset slider cache and keep the current mesh positions as the new starting state.",
        "chk_overshoot": "Overshoot (-50% ~ 150%)",
        "chk_overshoot_tt": "Allow negative or >100% revert values to push beyond the base or original shape.",
        # Context menu
        "ctx_using_orig": "Using Original Base",
        "ctx_using_alt": "Using {name} as Base",
        "ctx_use_sel_base": "Use Selected as Revert Base",
        "ctx_use_orig_base": "Use Original Base",
        "ctx_sel_moved_alt": "Select Moved from Revert Base",
        # Restore Symmetry Dialog
        "rst_title": "Attempt To Restore Symmetry",
        "rst_iter": "Iterations:",
        "rst_iter_tt": "Number of progressive radius steps between Start Radius and End Radius.",
        "rst_start": "Start Radius:",
        "rst_start_tt": "Initial tight search tolerance for nearly symmetrical vertices.",
        "rst_end": "End Radius:",
        "rst_end_tt": "Maximum search radius reached at the final iteration.",
        "rst_btn": "Symmetrize Selected / Mesh",
        "rst_btn_tt": "Progressively match and snap vertices to restore spatial symmetry.",
    },
    "ko": {
        "win_title": "SymMesh",
        "menu_ops": "연산 (Operations)",
        "menu_tools": "도구 (Tools)",
        "menu_lang": "언어 (Language)",
        "lang_en": "English",
        "lang_ko": "한국어",
        # Tabs
        "tab_setup": "1. 대칭 데이터 생성",
        "tab_ops": "2. 미러 / 플립 작업",
        # Operations menu
        "op_copy": "A를 B로 복사 (Copy A to B)",
        "op_copy_tt": "A 메시의 버텍스 위치를 B 메시로 복사합니다 (A 선택 후 B 선택).",
        "op_add": "A를 B에 더하기 (Add A to B)",
        "op_add_tt": "(A - Base) 변형량을 B 메시에 더합니다 (A 선택 후 B 선택).",
        "op_sub": "B에서 A 빼기 (Subtract A from B)",
        "op_sub_tt": "(A - Base) 변형량을 B 메시에서 뺍니다 (A 선택 후 B 선택).",
        "op_mir_copy": "A를 좌우 반전해 B로 복사",
        "op_mir_copy_tt": "대칭 테이블을 기준으로 A를 반전하여 B 메시에 복사합니다.",
        "op_mir_add": "A를 좌우 반전해 B에 더하기",
        "op_mir_add_tt": "(A - Base) 변형량을 좌우 반전하여 B 메시에 더합니다.",
        "op_mir_sub": "A를 좌우 반전해 B에서 빼기",
        "op_mir_sub_tt": "(A - Base) 변형량을 좌우 반전하여 B 메시에서 뺍니다.",
        "op_b_add": "A를 B에 더하기 (B를 Base로 사용)",
        "op_b_add_tt": "(A - B) 변형량을 B 메시에 더합니다 (A 선택 후 B 선택).",
        "op_b_sub": "B에서 A 빼기 (B를 Base로 사용)",
        "op_b_sub_tt": "(A - B) 변형량을 B 메시에서 뺍니다 (A 선택 후 B 선택).",
        "op_b_mir_add": "A를 좌우 반전해 B에 더하기 (B를 Base로 사용)",
        "op_b_mir_add_tt": "(A - B) 변형량을 좌우 반전하여 B 메시에 더합니다.",
        "op_b_mir_sub": "A를 좌우 반전해 B에서 빼기 (B를 Base로 사용)",
        "op_b_mir_sub_tt": "(A - B) 변형량을 좌우 반전하여 B 메시에서 뺍니다.",
        # Tools menu
        "tool_sel_mirror": "대칭 선택 (Selection Mirror)",
        "tool_sel_mirror_tt": "현재 선택한 버텍스들의 반대편 대칭 버텍스를 선택합니다.",
        "tool_sel_moved": "이동된 버텍스 선택 (Select Moved)",
        "tool_sel_moved_tt": "Base 메시 대비 허용 오차 이상 이동한 버텍스들을 선택합니다.",
        "tool_restore": "대칭 복원 시도 (Restore Symmetry)...",
        "tool_restore_tt": "반경을 점진적으로 넓혀가며 거의 대칭인 메시의 정점 대칭을 복원합니다.",
        "tool_sel_asym": "미매칭 / 비대칭 버텍스 선택",
        "tool_sel_asym_tt": "Base 메시에서 대칭 짝을 찾지 못한 버텍스들을 선택합니다.",
        "tool_sel_ctr": "중앙 심(Center Seam) 버텍스 선택",
        "tool_sel_ctr_tt": "Base 메시의 대칭 중심선에 위치한 버텍스들을 선택합니다.",
        "tool_clear_cache": "대칭 데이터 초기화",
        "tool_clear_cache_tt": "생성된 대칭 매핑 테이블과 Base 메시를 초기화합니다.",
        # Tab 1: Step 1 Base Mesh
        "grp_base": "1. Base 메시 입력",
        "btn_load_base": "선택 로드",
        "btn_load_base_tt": "현재 선택한 폴리곤 메시를 Base 메시로 입력합니다.",
        "btn_clear": "초기화",
        "btn_clear_tt": "입력된 Base 메시와 대칭 데이터를 초기화합니다.",
        "base_ph": "<Base 메시 이름 입력 또는 선택 로드>",
        "base_field_tt": "좌우 대칭 버텍스 매핑 데이터를 생성할 기준 Base 메시입니다.",
        # Tab 1: Step 2 Sample Space
        "grp_sample": "2. 샘플 스페이스 선택 (Transfer Attributes 방식)",
        "ss_world": "World",
        "ss_world_tt": "월드 좌표(World Space) 3D 위치를 기준으로 대칭 버텍스를 매칭합니다.",
        "ss_local": "Local",
        "ss_local_tt": "오브젝트 로컬 좌표(Local Space)를 기준으로 매칭합니다 (월드 이동/회전 무시).",
        "ss_uv": "UV",
        "ss_uv_tt": "UV 좌표를 기준으로 매칭합니다 (포즈나 형태가 비대칭이어도 UV가 대칭이면 작동).",
        "ss_topo": "Topology",
        "ss_topo_tt": "중앙 엣지로부터 페이스/엣지 연결 구조(Topology)를 따라 매칭합니다 (Base가 비대칭이어도 작동).",
        "lbl_axis": "대칭 축:",
        "axis_x": "YZ (X)",
        "axis_y": "XZ (Y)",
        "axis_z": "XY (Z)",
        "axis_tt": "미러 및 플립 연산의 기준이 되는 대칭 평면 축입니다.",
        "lbl_origin": "미러 원점:",
        "origin_items": ("피벗 (Pivot)", "원점 (0)", "바운딩 박스 중앙"),
        "origin_tt": "대칭 평면의 위치 기준: 오브젝트 피벗, 좌표 원점(0), 또는 바운딩 박스 중심.",
        "lbl_tol": "허용 오차:",
        "tol_tt": "공간 매칭, 중심선 판별 및 Select Moved Verts에 사용되는 거리 허용 오차입니다.",
        # UV options
        "lbl_uv_set": "UV 셋:",
        "uv_set_tt": "UV 기반 대칭 매칭에 사용할 UV Set 이름입니다.",
        "btn_refresh": "새로고침",
        "btn_refresh_tt": "Base 또는 선택한 메시에서 UV Set 목록을 다시 불러옵니다.",
        "lbl_uv_axis": "UV 미러 축:",
        "uv_u": "U",
        "uv_v": "V",
        "uv_axis_tt": "UV 공간에서 좌우 반전 기준으로 사용할 축(U 또는 V)입니다.",
        "lbl_uv_center": "UV 중심:",
        "uv_center_tt": "UV 미러 축 위의 대칭 중심 좌표입니다 (기본값 0.5).",
        "chk_uv_auto": "자동 (BBox)",
        "chk_uv_auto_tt": "UV 바운딩 박스의 중앙을 자동으로 UV 대칭 중심으로 계산합니다.",
        "lbl_uv_tol": "UV 오차:",
        "uv_tol_tt": "UV 공간에서 두 UV를 대칭으로 간주할 최대 거리입니다.",
        # Topology options
        "lbl_seed_edges": "중앙 엣지:",
        "seed_edges_ph": "자동 감지, 또는 중앙 엣지 선택 후 로드",
        "seed_edges_tt": "토폴로지 BFS 탐색 시작점으로 사용할 대칭 중심선 엣지 인덱스입니다. 비워두면 자동 감지합니다.",
        "btn_load_sel": "선택 로드",
        "btn_load_sel_tt": "현재 뷰포트에서 선택한 중앙 엣지(들)를 시드로 입력합니다.",
        "btn_clear_edges_tt": "입력된 중앙 엣지를 지우고 자동 감지로 되돌립니다.",
        "lbl_detached": "분리된 쉘:",
        "fallback_items": ("자동 (Local Space)", "자동 (World Space)", "자동 (UV Space)", "사용 안 함 (Topology만)"),
        "fallback_tt": "눈동자/치아처럼 중앙 엣지가 없는 분리된 메시 쉘을 매칭할 보조 방식입니다.",
        # Tab 1: Step 3 Build Symmetry Data
        "grp_build": "3. 대칭 데이터 생성",
        "btn_build_sym": "Build Symmetry Data (대칭 데이터 생성)",
        "btn_build_sym_tt": "입력된 Base 메시와 선택한 Sample Space를 바탕으로 좌우 대칭 버텍스 매핑 데이터를 생성합니다.",
        "status_empty": "1) Base 메시 입력  →  2) Sample Space 선택  →  3) 'Build Symmetry Data' 실행",
        "status_base_ready": "Base 메시 '{mesh}' 입력됨. Sample Space를 선택한 뒤 'Build Symmetry Data'를 누르세요.",
        "status_sym": "생성 완료 | {pairs}쌍, 중앙 {ctr}개 ({ms:.1f} ms)",
        "status_asym": "부분 매칭: 미매칭 {unm}개 | {pairs}쌍 ({ms:.1f} ms)",
        "status_err": "생성 실패: {err}",
        "hint_try_spatial": "제안: Base 메시가 기하학적으로 비대칭이라면 'Topology'(중앙 엣지 지정) 또는 'UV' Sample Space로 다시 시도해 보세요.",
        "hint_try_uv": "제안: UV Set / UV 중심 / UV 오차를 확인하거나 'Topology' 또는 'Local' Sample Space로 시도해 보세요.",
        "hint_try_topo": "제안: 메시의 중앙 엣지를 선택해 '선택 로드'를 누르거나, 'UV' / 'Local' Sample Space로 시도해 보세요.",
        "btn_sel_unmatched": "미매칭 선택",
        "btn_sel_unmatched_tt": "Base 메시에서 대칭 짝을 찾지 못한 버텍스들을 선택합니다.",
        "btn_goto_ops": "작업 탭으로 이동 →",
        "btn_goto_ops_tt": "Mirror / Flip / Revert 작업을 수행하는 두 번째 탭으로 이동합니다.",
        # Tab 2: Operations Summary Banner
        "ops_banner_none": "생성된 대칭 데이터가 없습니다. 먼저 '1. 대칭 데이터 생성' 탭에서 데이터를 생성하세요.",
        "ops_banner_ok": "활성 Base: {mesh}  [{space}]  |  {pairs}쌍, 중앙 {ctr}개",
        "ops_banner_asym": "활성 Base: {mesh}  [{space}]  |  {pairs}쌍 (미매칭 {unm}개)",
        # Tab 2: Mirror & Flip Group
        "grp_mf": "미러 및 플립",
        "chk_neg_to_pos": "-{axis} → +{axis} 방향으로 적용",
        "chk_neg_to_pos_tt": "체크 시 -{axis}에서 +{axis}로 미러합니다. 해제 시 +{axis}에서 -{axis}로 미러합니다.",
        "btn_mirror": "선택 미러 (Mirror)",
        "btn_mirror_tt": "소스 방향의 버텍스 위치를 반대편으로 대칭 복사합니다 (오브젝트 선택 시 전체 적용).",
        "btn_flip": "선택 플립 (Flip)",
        "btn_flip_tt": "선택한 대칭 버텍스 쌍의 위치를 서로 맞바꿉니다 (오브젝트 선택 시 전체 적용).",
        # Tab 2: Revert Group
        "grp_rev": "Base로 되돌리기 (Revert)",
        "btn_revert": "선택 버텍스 Base로 복원",
        "btn_revert_tt": "선택한 버텍스(또는 전체 메시)를 Base 메시 위치로 100% 되돌립니다. 우클릭 시 퍼센트 프리셋과 대체 Base 메뉴가 열립니다.",
        "rev_base_orig": "복원 기준 Base: 원본 Base",
        "rev_base_alt": "복원 기준 Base: {name}",
        "rev_slider_tt": "드래그하여 선택한 버텍스를 Base 형태로 실시간 블렌드합니다.",
        "rev_spin_tt": "복원 비율을 퍼센트로 직접 입력합니다 (0% = 현재 형태, 100% = Base 형태).",
        "btn_commit": "확정",
        "btn_commit_tt": "슬라이더 캐시를 초기화하고 현재 메시 상태를 새로운 기준점으로 확정합니다.",
        "chk_overshoot": "오버슈트 허용 (-50% ~ 150%)",
        "chk_overshoot_tt": "0~100% 범위를 넘어 반대 방향(-50%)이나 Base 너머(150%)까지 과장 블렌드합니다.",
        # Context menu
        "ctx_using_orig": "원본 Base 사용 중",
        "ctx_using_alt": "{name} 을(를) Base로 사용 중",
        "ctx_use_sel_base": "선택한 메시를 복원 Base로 사용",
        "ctx_use_orig_base": "원본 Base로 되돌리기",
        "ctx_sel_moved_alt": "복원 Base 대비 이동된 버텍스 선택",
        # Restore Symmetry Dialog
        "rst_title": "대칭 복원 시도",
        "rst_iter": "반복 횟수:",
        "rst_iter_tt": "시작 반경에서 종료 반경까지 탐색 허용 오차를 단계별로 증가시킬 횟수입니다.",
        "rst_start": "시작 반경:",
        "rst_start_tt": "거의 대칭인 버텍스부터 매칭하기 위한 초기 허용 오차입니다.",
        "rst_end": "종료 반경:",
        "rst_end_tt": "마지막 반복 단계에서 도달할 최대 탐색 반경입니다.",
        "rst_btn": "선택 버텍스 / 메시 대칭화",
        "rst_btn_tt": "반경을 점진적으로 넓혀가며 대응 버텍스를 찾아 대칭 위치로 스냅합니다.",
    },
}


def get_saved_language():
    """Return persisted UI language ('en' or 'ko') from Maya optionVar."""
    if cmds.optionVar(exists=LANGUAGE_OPTION_VAR):
        val = cmds.optionVar(q=LANGUAGE_OPTION_VAR)
        if val in _TR:
            return val
    return "en"


def save_language(lang):
    """Persist UI language preference in Maya optionVar."""
    if lang in _TR:
        cmds.optionVar(sv=(LANGUAGE_OPTION_VAR, lang))


def _get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is None:
        return None
    return wrapInstance(int(ptr), QtWidgets.QWidget)


def _add_menu_action(menu, label, callback, checkable=False):
    action = menu.addAction(label)
    action.setCheckable(checkable)
    action.triggered.connect(callback)
    return action


def _configure_button(btn, min_height=None):
    """Ensure button text is never clipped across languages or Maya DPI scales."""
    btn.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
    if min_height is not None:
        btn.setMinimumHeight(min_height)
    btn.setStyleSheet("QPushButton { padding: 4px 10px; }")


class RestoreSymmetryDialog(QtWidgets.QDialog):
    """Sub-dialog for iterative spatial symmetry restoration."""

    def __init__(self, parent, get_settings_fn, lang="en"):
        super(RestoreSymmetryDialog, self).__init__(parent)
        self._get_settings_fn = get_settings_fn
        self._lang = lang if lang in _TR else "en"
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(320)

        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.iter_lbl = QtWidgets.QLabel()
        self.iter_spin = QtWidgets.QSpinBox()
        self.iter_spin.setRange(10, 2000)
        self.iter_spin.setValue(200)

        self.start_lbl = QtWidgets.QLabel()
        self.start_rad_spin = QtWidgets.QDoubleSpinBox()
        self.start_rad_spin.setDecimals(6)
        self.start_rad_spin.setRange(0.000001, 10.0)
        self.start_rad_spin.setSingleStep(0.0001)
        self.start_rad_spin.setValue(0.000001)

        self.end_lbl = QtWidgets.QLabel()
        self.end_rad_spin = QtWidgets.QDoubleSpinBox()
        self.end_rad_spin.setDecimals(4)
        self.end_rad_spin.setRange(0.0001, 1000.0)
        self.end_rad_spin.setSingleStep(0.05)
        self.end_rad_spin.setValue(1.0)

        layout.addRow(self.iter_lbl, self.iter_spin)
        layout.addRow(self.start_lbl, self.start_rad_spin)
        layout.addRow(self.end_lbl, self.end_rad_spin)

        self.apply_btn = QtWidgets.QPushButton()
        _configure_button(self.apply_btn, min_height=28)
        self.apply_btn.clicked.connect(self._on_apply)
        layout.addRow(self.apply_btn)

        self.retranslate(self._lang)

    def retranslate(self, lang):
        self._lang = lang if lang in _TR else "en"
        t = _TR[self._lang]
        self.setWindowTitle(t["rst_title"])
        self.iter_lbl.setText(t["rst_iter"])
        self.iter_spin.setToolTip(t["rst_iter_tt"])
        self.start_lbl.setText(t["rst_start"])
        self.start_rad_spin.setToolTip(t["rst_start_tt"])
        self.end_lbl.setText(t["rst_end"])
        self.end_rad_spin.setToolTip(t["rst_end_tt"])
        self.apply_btn.setText(t["rst_btn"])
        self.apply_btn.setToolTip(t["rst_btn_tt"])
        self.adjustSize()

    def _on_apply(self):
        mesh_name, vert_indices, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select a mesh or vertices.")
            return

        settings = self._get_settings_fn()
        try:
            count = symUtil.restore_symmetry(
                mesh_name,
                vert_indices=vert_indices,
                axis=settings["axis"],
                origin_mode=settings["origin_mode"],
                start_tol=self.start_rad_spin.value(),
                end_tol=self.end_rad_spin.value(),
                iterations=self.iter_spin.value(),
                neg_to_pos=settings["neg_to_pos"],
                undoable=True,
            )
            cmds.inViewMessage(
                amg="Symmetrized <hl>{}</hl> vertex pair(s).".format(count),
                pos="botCenter",
                fade=True,
            )
        except Exception as exc:
            cmds.warning(str(exc))


class SymMeshUI(QtWidgets.QDialog):
    """Transfer-Attributes-inspired fast symmetry tool UI with Setup & Operations tabs."""

    _instance = None

    def __init__(self, parent=None):
        if parent is None:
            parent = _get_maya_main_window()
        super(SymMeshUI, self).__init__(parent)

        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setMinimumWidth(440)

        self._lang = get_saved_language()
        self._sym_data = None
        self._build_error_msg = ""
        self._build_error_space = ""
        self._alt_base_mesh = ""
        self._seed_edges = []

        # Interactive revert slider cache
        self._rev_mesh = ""
        self._rev_indices = None
        self._rev_orig_pts = None
        self._rev_base_pts = None
        self._rev_dragging = False
        self._syncing_revert = False

        self._restore_dialog = None

        self._build_ui()
        self._connect_signals()
        self._retranslate_ui()
        self._update_sample_space_visibility()
        self._update_base_dependent_ui()

    @classmethod
    def show_ui(cls):
        existing = None
        maya_win = _get_maya_main_window()
        if maya_win is not None:
            existing = maya_win.findChild(QtWidgets.QDialog, WINDOW_OBJECT_NAME)
        if existing is not None:
            existing.close()
            existing.deleteLater()

        cls._instance = cls(parent=maya_win)
        cls._instance.show()
        cls._instance.raise_()
        cls._instance.activateWindow()
        return cls._instance

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(6, 4, 6, 6)
        root_layout.setSpacing(6)

        # Menu Bar
        self.menu_bar = QtWidgets.QMenuBar(self)
        root_layout.setMenuBar(self.menu_bar)
        self._build_menus()

        # Tab Widget
        self.tab_widget = QtWidgets.QTabWidget()
        root_layout.addWidget(self.tab_widget, 1)

        self.setup_tab = QtWidgets.QWidget()
        self.ops_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.setup_tab, "")
        self.tab_widget.addTab(self.ops_tab, "")

        self._build_setup_tab()
        self._build_operations_tab()

    def _build_setup_tab(self):
        setup_layout = QtWidgets.QVBoxLayout(self.setup_tab)
        setup_layout.setContentsMargins(6, 8, 6, 6)
        setup_layout.setSpacing(8)

        # Step 1: Base Mesh
        self.base_grp = QtWidgets.QGroupBox()
        base_layout = QtWidgets.QVBoxLayout(self.base_grp)
        base_layout.setContentsMargins(8, 8, 8, 8)
        base_layout.setSpacing(5)

        base_row = QtWidgets.QHBoxLayout()
        self.base_field = QtWidgets.QLineEdit()
        self.load_base_btn = QtWidgets.QPushButton()
        _configure_button(self.load_base_btn)
        self.clear_base_btn = QtWidgets.QPushButton()
        _configure_button(self.clear_base_btn)
        base_row.addWidget(self.base_field, 1)
        base_row.addWidget(self.load_base_btn)
        base_row.addWidget(self.clear_base_btn)
        base_layout.addLayout(base_row)
        setup_layout.addWidget(self.base_grp)

        # Step 2: Sample Space (Maya Transfer Attributes UX)
        self.sample_grp = QtWidgets.QGroupBox()
        sample_layout = QtWidgets.QVBoxLayout(self.sample_grp)
        sample_layout.setContentsMargins(8, 8, 8, 8)
        sample_layout.setSpacing(6)

        ss_row = QtWidgets.QHBoxLayout()
        ss_row.setSpacing(10)
        self.ss_group = QtWidgets.QButtonGroup(self)
        self.ss_world_rb = QtWidgets.QRadioButton()
        self.ss_local_rb = QtWidgets.QRadioButton()
        self.ss_uv_rb = QtWidgets.QRadioButton()
        self.ss_topo_rb = QtWidgets.QRadioButton()
        self.ss_local_rb.setChecked(True)

        for idx, rb in enumerate((self.ss_world_rb, self.ss_local_rb, self.ss_uv_rb, self.ss_topo_rb)):
            self.ss_group.addButton(rb, idx)
            ss_row.addWidget(rb)
        ss_row.addStretch(1)
        sample_layout.addLayout(ss_row)

        common_form = QtWidgets.QFormLayout()
        common_form.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        common_form.setContentsMargins(0, 2, 0, 0)
        common_form.setSpacing(5)

        axis_row = QtWidgets.QHBoxLayout()
        self.axis_group = QtWidgets.QButtonGroup(self)
        self.axis_x_rb = QtWidgets.QRadioButton()
        self.axis_y_rb = QtWidgets.QRadioButton()
        self.axis_z_rb = QtWidgets.QRadioButton()
        self.axis_x_rb.setChecked(True)
        for idx, rb in enumerate((self.axis_x_rb, self.axis_y_rb, self.axis_z_rb)):
            self.axis_group.addButton(rb, idx)
            axis_row.addWidget(rb)
        axis_row.addStretch(1)
        self.axis_lbl = QtWidgets.QLabel()
        common_form.addRow(self.axis_lbl, axis_row)

        self.origin_lbl = QtWidgets.QLabel()
        self.origin_combo = QtWidgets.QComboBox()
        for value in _ORIGIN_VALUES:
            self.origin_combo.addItem("", value)
        common_form.addRow(self.origin_lbl, self.origin_combo)

        self.tol_lbl = QtWidgets.QLabel()
        self.tol_spin = QtWidgets.QDoubleSpinBox()
        self.tol_spin.setDecimals(6)
        self.tol_spin.setRange(0.0, 10.0)
        self.tol_spin.setSingleStep(0.001)
        self.tol_spin.setValue(0.001)
        common_form.addRow(self.tol_lbl, self.tol_spin)

        sample_layout.addLayout(common_form)

        # Contextual UV options
        self.uv_widget = QtWidgets.QWidget()
        uv_form = QtWidgets.QFormLayout(self.uv_widget)
        uv_form.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        uv_form.setContentsMargins(0, 4, 0, 0)
        uv_form.setSpacing(5)

        self.uv_set_lbl = QtWidgets.QLabel()
        uv_set_row = QtWidgets.QHBoxLayout()
        self.uv_set_combo = QtWidgets.QComboBox()
        self.uv_set_combo.setEditable(True)
        self.uv_set_combo.setEditText("map1")
        self.uv_refresh_btn = QtWidgets.QPushButton()
        _configure_button(self.uv_refresh_btn)
        uv_set_row.addWidget(self.uv_set_combo, 1)
        uv_set_row.addWidget(self.uv_refresh_btn)
        uv_form.addRow(self.uv_set_lbl, uv_set_row)

        self.uv_axis_lbl = QtWidgets.QLabel()
        uv_axis_row = QtWidgets.QHBoxLayout()
        self.uv_axis_group = QtWidgets.QButtonGroup(self)
        self.uv_u_rb = QtWidgets.QRadioButton()
        self.uv_v_rb = QtWidgets.QRadioButton()
        self.uv_u_rb.setChecked(True)
        self.uv_axis_group.addButton(self.uv_u_rb, 0)
        self.uv_axis_group.addButton(self.uv_v_rb, 1)
        uv_axis_row.addWidget(self.uv_u_rb)
        uv_axis_row.addWidget(self.uv_v_rb)
        uv_axis_row.addStretch(1)
        uv_form.addRow(self.uv_axis_lbl, uv_axis_row)

        self.uv_center_lbl = QtWidgets.QLabel()
        uv_center_row = QtWidgets.QHBoxLayout()
        self.uv_center_spin = QtWidgets.QDoubleSpinBox()
        self.uv_center_spin.setDecimals(4)
        self.uv_center_spin.setRange(-100.0, 100.0)
        self.uv_center_spin.setSingleStep(0.5)
        self.uv_center_spin.setValue(0.5)
        self.uv_auto_center_chk = QtWidgets.QCheckBox()
        uv_center_row.addWidget(self.uv_center_spin, 1)
        uv_center_row.addWidget(self.uv_auto_center_chk)
        uv_form.addRow(self.uv_center_lbl, uv_center_row)

        self.uv_tol_lbl = QtWidgets.QLabel()
        self.uv_tol_spin = QtWidgets.QDoubleSpinBox()
        self.uv_tol_spin.setDecimals(5)
        self.uv_tol_spin.setRange(0.00001, 1.0)
        self.uv_tol_spin.setSingleStep(0.001)
        self.uv_tol_spin.setValue(0.001)
        uv_form.addRow(self.uv_tol_lbl, self.uv_tol_spin)

        sample_layout.addWidget(self.uv_widget)

        # Contextual Topology options
        self.topo_widget = QtWidgets.QWidget()
        topo_form = QtWidgets.QFormLayout(self.topo_widget)
        topo_form.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        topo_form.setContentsMargins(0, 4, 0, 0)
        topo_form.setSpacing(5)

        self.seed_edges_lbl = QtWidgets.QLabel()
        edge_row = QtWidgets.QHBoxLayout()
        self.seed_edges_edit = QtWidgets.QLineEdit()
        self.load_edges_btn = QtWidgets.QPushButton()
        _configure_button(self.load_edges_btn)
        self.clear_edges_btn = QtWidgets.QPushButton("X")
        _configure_button(self.clear_edges_btn)
        edge_row.addWidget(self.seed_edges_edit, 1)
        edge_row.addWidget(self.load_edges_btn)
        edge_row.addWidget(self.clear_edges_btn)
        topo_form.addRow(self.seed_edges_lbl, edge_row)

        self.fallback_lbl = QtWidgets.QLabel()
        self.fallback_combo = QtWidgets.QComboBox()
        for value in _FALLBACK_VALUES:
            self.fallback_combo.addItem("", value)
        topo_form.addRow(self.fallback_lbl, self.fallback_combo)

        sample_layout.addWidget(self.topo_widget)
        setup_layout.addWidget(self.sample_grp)

        # Step 3: Build Symmetry Data
        self.build_grp = QtWidgets.QGroupBox()
        build_layout = QtWidgets.QVBoxLayout(self.build_grp)
        build_layout.setContentsMargins(8, 8, 8, 8)
        build_layout.setSpacing(6)

        self.build_sym_btn = QtWidgets.QPushButton()
        _configure_button(self.build_sym_btn, min_height=32)
        build_layout.addWidget(self.build_sym_btn)

        self.base_status_lbl = QtWidgets.QLabel()
        self.base_status_lbl.setWordWrap(True)
        build_layout.addWidget(self.base_status_lbl)

        self.build_feedback_lbl = QtWidgets.QLabel()
        self.build_feedback_lbl.setWordWrap(True)
        self.build_feedback_lbl.setStyleSheet("color: #79c0ff; font-size: 11px;")
        self.build_feedback_lbl.setVisible(False)
        build_layout.addWidget(self.build_feedback_lbl)

        action_row = QtWidgets.QHBoxLayout()
        self.sel_asym_btn = QtWidgets.QPushButton()
        _configure_button(self.sel_asym_btn)
        self.sel_asym_btn.setVisible(False)
        self.goto_ops_btn = QtWidgets.QPushButton()
        _configure_button(self.goto_ops_btn)
        self.goto_ops_btn.setVisible(False)
        action_row.addWidget(self.sel_asym_btn)
        action_row.addStretch(1)
        action_row.addWidget(self.goto_ops_btn)
        build_layout.addLayout(action_row)

        setup_layout.addWidget(self.build_grp)
        setup_layout.addStretch(1)

    def _build_operations_tab(self):
        ops_layout = QtWidgets.QVBoxLayout(self.ops_tab)
        ops_layout.setContentsMargins(6, 8, 6, 6)
        ops_layout.setSpacing(8)

        # Active Base Banner
        self.ops_banner_lbl = QtWidgets.QLabel()
        self.ops_banner_lbl.setWordWrap(True)
        self.ops_banner_lbl.setStyleSheet(
            "QLabel { background-color: #2b2b2b; border: 1px solid #444; border-radius: 4px; padding: 6px; }"
        )
        ops_layout.addWidget(self.ops_banner_lbl)

        # Mirror & Flip Group
        self.deform_grp = QtWidgets.QGroupBox()
        deform_layout = QtWidgets.QVBoxLayout(self.deform_grp)
        deform_layout.setContentsMargins(8, 8, 8, 8)
        deform_layout.setSpacing(6)

        self.neg_to_pos_chk = QtWidgets.QCheckBox()
        deform_layout.addWidget(self.neg_to_pos_chk)

        mf_row = QtWidgets.QHBoxLayout()
        self.mirror_btn = QtWidgets.QPushButton()
        _configure_button(self.mirror_btn, min_height=30)
        self.flip_btn = QtWidgets.QPushButton()
        _configure_button(self.flip_btn, min_height=30)
        mf_row.addWidget(self.mirror_btn, 1)
        mf_row.addWidget(self.flip_btn, 1)
        deform_layout.addLayout(mf_row)

        ops_layout.addWidget(self.deform_grp)

        # Revert to Base Group
        self.rev_grp = QtWidgets.QGroupBox()
        rev_layout = QtWidgets.QVBoxLayout(self.rev_grp)
        rev_layout.setContentsMargins(8, 8, 8, 8)
        rev_layout.setSpacing(5)

        self.revert_btn = QtWidgets.QPushButton()
        _configure_button(self.revert_btn, min_height=26)
        self.revert_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        rev_layout.addWidget(self.revert_btn)

        self.alt_base_lbl = QtWidgets.QLabel()
        self.alt_base_lbl.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        rev_layout.addWidget(self.alt_base_lbl)

        slider_row = QtWidgets.QHBoxLayout()
        self.revert_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.revert_slider.setRange(0, 1000)
        self.revert_slider.setValue(0)
        self.revert_spin = QtWidgets.QDoubleSpinBox()
        self.revert_spin.setRange(0.0, 100.0)
        self.revert_spin.setDecimals(1)
        self.revert_spin.setSuffix("%")
        self.revert_spin.setMinimumWidth(74)
        self.commit_rev_btn = QtWidgets.QPushButton()
        _configure_button(self.commit_rev_btn)
        slider_row.addWidget(self.revert_slider, 1)
        slider_row.addWidget(self.revert_spin)
        slider_row.addWidget(self.commit_rev_btn)
        rev_layout.addLayout(slider_row)

        self.overshoot_chk = QtWidgets.QCheckBox()
        rev_layout.addWidget(self.overshoot_chk)

        ops_layout.addWidget(self.rev_grp)
        ops_layout.addStretch(1)

    def _build_menus(self):
        self.ops_menu = self.menu_bar.addMenu("")
        self.ops_menu.setToolTipsVisible(True)
        self.op_copy_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("copy", False, False))
        self.op_add_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("add", False, False))
        self.op_sub_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("subtract", False, False))
        self.ops_menu.addSeparator()
        self.op_mir_copy_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("copy", True, False))
        self.op_mir_add_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("add", True, False))
        self.op_mir_sub_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("subtract", True, False))
        self.ops_menu.addSeparator()
        self.op_b_add_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("add", False, True))
        self.op_b_sub_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("subtract", False, True))
        self.ops_menu.addSeparator()
        self.op_b_mir_add_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("add", True, True))
        self.op_b_mir_sub_act = _add_menu_action(self.ops_menu, "", lambda: self._run_blend_op("subtract", True, True))

        self._ops_actions = [
            self.op_copy_act,
            self.op_add_act,
            self.op_sub_act,
            self.op_mir_copy_act,
            self.op_mir_add_act,
            self.op_mir_sub_act,
            self.op_b_add_act,
            self.op_b_sub_act,
            self.op_b_mir_add_act,
            self.op_b_mir_sub_act,
        ]

        self.tools_menu = self.menu_bar.addMenu("")
        self.tools_menu.setToolTipsVisible(True)
        self.sel_mirror_act = _add_menu_action(self.tools_menu, "", self._on_selection_mirror)
        self.sel_moved_act = _add_menu_action(self.tools_menu, "", self._on_select_moved)
        self.tools_menu.addSeparator()
        self.tool_restore_act = _add_menu_action(self.tools_menu, "", self._open_restore_symmetry)
        self.tools_menu.addSeparator()
        self.sel_asym_action = _add_menu_action(self.tools_menu, "", self._select_unmatched)
        self.sel_ctr_action = _add_menu_action(self.tools_menu, "", self._select_center)
        self.tools_menu.addSeparator()
        self.tool_clear_cache_act = _add_menu_action(self.tools_menu, "", self._clear_base)

        self.lang_menu = self.menu_bar.addMenu("")
        self.lang_en_act = _add_menu_action(self.lang_menu, "", lambda: self.set_language("en"), checkable=True)
        self.lang_ko_act = _add_menu_action(self.lang_menu, "", lambda: self.set_language("ko"), checkable=True)

    # ------------------------------------------------------------------
    # Localization & Tooltips
    # ------------------------------------------------------------------

    def set_language(self, lang):
        """Switch UI language ('en' or 'ko') and persist preference."""
        if lang not in _TR:
            return
        self._lang = lang
        save_language(lang)
        self._retranslate_ui()
        if self._restore_dialog is not None:
            try:
                self._restore_dialog.retranslate(lang)
            except Exception:
                pass
        self.adjustSize()

    def _retranslate_ui(self):
        t = _TR[self._lang]
        self.setWindowTitle(t["win_title"])

        # Tabs
        self.tab_widget.setTabText(0, t["tab_setup"])
        self.tab_widget.setTabText(1, t["tab_ops"])

        # Menus
        self.ops_menu.setTitle(t["menu_ops"])
        self.tools_menu.setTitle(t["menu_tools"])
        self.lang_menu.setTitle(t["menu_lang"])
        self.lang_en_act.setText(t["lang_en"])
        self.lang_ko_act.setText(t["lang_ko"])
        self.lang_en_act.setChecked(self._lang == "en")
        self.lang_ko_act.setChecked(self._lang == "ko")

        op_map = (
            (self.op_copy_act, "op_copy", "op_copy_tt"),
            (self.op_add_act, "op_add", "op_add_tt"),
            (self.op_sub_act, "op_sub", "op_sub_tt"),
            (self.op_mir_copy_act, "op_mir_copy", "op_mir_copy_tt"),
            (self.op_mir_add_act, "op_mir_add", "op_mir_add_tt"),
            (self.op_mir_sub_act, "op_mir_sub", "op_mir_sub_tt"),
            (self.op_b_add_act, "op_b_add", "op_b_add_tt"),
            (self.op_b_sub_act, "op_b_sub", "op_b_sub_tt"),
            (self.op_b_mir_add_act, "op_b_mir_add", "op_b_mir_add_tt"),
            (self.op_b_mir_sub_act, "op_b_mir_sub", "op_b_mir_sub_tt"),
            (self.sel_mirror_act, "tool_sel_mirror", "tool_sel_mirror_tt"),
            (self.sel_moved_act, "tool_sel_moved", "tool_sel_moved_tt"),
            (self.tool_restore_act, "tool_restore", "tool_restore_tt"),
            (self.sel_asym_action, "tool_sel_asym", "tool_sel_asym_tt"),
            (self.sel_ctr_action, "tool_sel_ctr", "tool_sel_ctr_tt"),
            (self.tool_clear_cache_act, "tool_clear_cache", "tool_clear_cache_tt"),
        )
        for act, lbl_k, tt_k in op_map:
            act.setText(t[lbl_k])
            act.setToolTip(t[tt_k])

        # Step 1: Base Mesh
        self.base_grp.setTitle(t["grp_base"])
        self.load_base_btn.setText(t["btn_load_base"])
        self.load_base_btn.setToolTip(t["btn_load_base_tt"])
        self.clear_base_btn.setText(t["btn_clear"])
        self.clear_base_btn.setToolTip(t["btn_clear_tt"])
        self.base_field.setPlaceholderText(t["base_ph"])
        self.base_field.setToolTip(t["base_field_tt"])

        # Step 2: Sample Space
        self.sample_grp.setTitle(t["grp_sample"])
        self.ss_world_rb.setText(t["ss_world"])
        self.ss_world_rb.setToolTip(t["ss_world_tt"])
        self.ss_local_rb.setText(t["ss_local"])
        self.ss_local_rb.setToolTip(t["ss_local_tt"])
        self.ss_uv_rb.setText(t["ss_uv"])
        self.ss_uv_rb.setToolTip(t["ss_uv_tt"])
        self.ss_topo_rb.setText(t["ss_topo"])
        self.ss_topo_rb.setToolTip(t["ss_topo_tt"])

        self.axis_lbl.setText(t["lbl_axis"])
        self.axis_x_rb.setText(t["axis_x"])
        self.axis_y_rb.setText(t["axis_y"])
        self.axis_z_rb.setText(t["axis_z"])
        for rb in (self.axis_x_rb, self.axis_y_rb, self.axis_z_rb):
            rb.setToolTip(t["axis_tt"])

        self.origin_lbl.setText(t["lbl_origin"])
        for idx, text in enumerate(t["origin_items"]):
            self.origin_combo.setItemText(idx, text)
        self.origin_combo.setToolTip(t["origin_tt"])

        self.tol_lbl.setText(t["lbl_tol"])
        self.tol_spin.setToolTip(t["tol_tt"])

        # UV options
        self.uv_set_lbl.setText(t["lbl_uv_set"])
        self.uv_set_combo.setToolTip(t["uv_set_tt"])
        self.uv_refresh_btn.setText(t["btn_refresh"])
        self.uv_refresh_btn.setToolTip(t["btn_refresh_tt"])
        self.uv_axis_lbl.setText(t["lbl_uv_axis"])
        self.uv_u_rb.setText(t["uv_u"])
        self.uv_v_rb.setText(t["uv_v"])
        self.uv_u_rb.setToolTip(t["uv_axis_tt"])
        self.uv_v_rb.setToolTip(t["uv_axis_tt"])
        self.uv_center_lbl.setText(t["lbl_uv_center"])
        self.uv_center_spin.setToolTip(t["uv_center_tt"])
        self.uv_auto_center_chk.setText(t["chk_uv_auto"])
        self.uv_auto_center_chk.setToolTip(t["chk_uv_auto_tt"])
        self.uv_tol_lbl.setText(t["lbl_uv_tol"])
        self.uv_tol_spin.setToolTip(t["uv_tol_tt"])

        # Topology options
        self.seed_edges_lbl.setText(t["lbl_seed_edges"])
        self.seed_edges_edit.setPlaceholderText(t["seed_edges_ph"])
        self.seed_edges_edit.setToolTip(t["seed_edges_tt"])
        self.load_edges_btn.setText(t["btn_load_sel"])
        self.load_edges_btn.setToolTip(t["btn_load_sel_tt"])
        self.clear_edges_btn.setToolTip(t["btn_clear_edges_tt"])
        self.fallback_lbl.setText(t["lbl_detached"])
        for idx, text in enumerate(t["fallback_items"]):
            self.fallback_combo.setItemText(idx, text)
        self.fallback_combo.setToolTip(t["fallback_tt"])

        # Step 3: Build Symmetry Data
        self.build_grp.setTitle(t["grp_build"])
        self.build_sym_btn.setText(t["btn_build_sym"])
        self.build_sym_btn.setToolTip(t["btn_build_sym_tt"])
        self.sel_asym_btn.setText(t["btn_sel_unmatched"])
        self.sel_asym_btn.setToolTip(t["btn_sel_unmatched_tt"])
        self.goto_ops_btn.setText(t["btn_goto_ops"])
        self.goto_ops_btn.setToolTip(t["btn_goto_ops_tt"])
        self._refresh_status_label()

        # Tab 2: Mirror & Flip
        self.deform_grp.setTitle(t["grp_mf"])
        self._update_axis_direction_text()
        self.mirror_btn.setText(t["btn_mirror"])
        self.mirror_btn.setToolTip(t["btn_mirror_tt"])
        self.flip_btn.setText(t["btn_flip"])
        self.flip_btn.setToolTip(t["btn_flip_tt"])

        # Tab 2: Revert
        self.rev_grp.setTitle(t["grp_rev"])
        self.revert_btn.setText(t["btn_revert"])
        self.revert_btn.setToolTip(t["btn_revert_tt"])
        self._refresh_alt_base_label()
        self.revert_slider.setToolTip(t["rev_slider_tt"])
        self.revert_spin.setToolTip(t["rev_spin_tt"])
        self.commit_rev_btn.setText(t["btn_commit"])
        self.commit_rev_btn.setToolTip(t["btn_commit_tt"])
        self.overshoot_chk.setText(t["chk_overshoot"])
        self.overshoot_chk.setToolTip(t["chk_overshoot_tt"])

    def _update_axis_direction_text(self):
        t = _TR[self._lang]
        axis_name = symUtil.AXIS_NAMES[self._get_axis()]
        self.neg_to_pos_chk.setText(t["chk_neg_to_pos"].format(axis=axis_name))
        self.neg_to_pos_chk.setToolTip(t["chk_neg_to_pos_tt"].format(axis=axis_name))

    def _get_sample_space_hint(self, sample_space):
        t = _TR[self._lang]
        if sample_space in (symUtil.SAMPLE_WORLD, symUtil.SAMPLE_LOCAL):
            return t["hint_try_spatial"]
        if sample_space == symUtil.SAMPLE_UV:
            return t["hint_try_uv"]
        return t["hint_try_topo"]

    def _refresh_status_label(self):
        t = _TR[self._lang]
        base_text = self.base_field.text().strip()

        if self._build_error_msg:
            self.base_status_lbl.setStyleSheet("color: #f85149;")
            self.base_status_lbl.setText(t["status_err"].format(err=self._build_error_msg))
            self.build_feedback_lbl.setText(self._get_sample_space_hint(self._build_error_space))
            self.build_feedback_lbl.setVisible(True)
            self.sel_asym_btn.setVisible(False)
            self.goto_ops_btn.setVisible(False)
            self.ops_banner_lbl.setText(t["ops_banner_none"])
            self.ops_banner_lbl.setStyleSheet(
                "QLabel { background-color: #2b2b2b; border: 1px solid #444; border-radius: 4px; padding: 6px; color: #aaaaaa; }"
            )
            return

        if self._sym_data is None:
            self.base_status_lbl.setStyleSheet("")
            if base_text:
                self.base_status_lbl.setText(t["status_base_ready"].format(mesh=base_text))
            else:
                self.base_status_lbl.setText(t["status_empty"])
            self.build_feedback_lbl.setVisible(False)
            self.sel_asym_btn.setVisible(False)
            self.goto_ops_btn.setVisible(False)
            self.ops_banner_lbl.setText(t["ops_banner_none"])
            self.ops_banner_lbl.setStyleSheet(
                "QLabel { background-color: #2b2b2b; border: 1px solid #444; border-radius: 4px; padding: 6px; color: #aaaaaa; }"
            )
            return

        if self._sym_data.is_symmetrical:
            msg = t["status_sym"].format(
                pairs=self._sym_data.paired_count,
                ctr=self._sym_data.center_count,
                ms=self._sym_data.elapsed_ms,
            )
            self.base_status_lbl.setStyleSheet("color: #7ee787;")
            self.build_feedback_lbl.setVisible(False)
            self.sel_asym_btn.setVisible(False)
            self.ops_banner_lbl.setText(
                t["ops_banner_ok"].format(
                    mesh=self._sym_data.base_mesh,
                    space=self._sym_data.sample_space.upper(),
                    pairs=self._sym_data.paired_count,
                    ctr=self._sym_data.center_count,
                )
            )
            self.ops_banner_lbl.setStyleSheet(
                "QLabel { background-color: #1f2d24; border: 1px solid #3c6e47; border-radius: 4px; padding: 6px; color: #7ee787; }"
            )
        else:
            msg = t["status_asym"].format(
                unm=self._sym_data.unmatched_count,
                pairs=self._sym_data.paired_count,
                ms=self._sym_data.elapsed_ms,
            )
            self.base_status_lbl.setStyleSheet("color: #ffa657;")
            self.build_feedback_lbl.setText(self._get_sample_space_hint(self._sym_data.sample_space))
            self.build_feedback_lbl.setVisible(True)
            self.sel_asym_btn.setVisible(True)
            self.ops_banner_lbl.setText(
                t["ops_banner_asym"].format(
                    mesh=self._sym_data.base_mesh,
                    space=self._sym_data.sample_space.upper(),
                    pairs=self._sym_data.paired_count,
                    unm=self._sym_data.unmatched_count,
                )
            )
            self.ops_banner_lbl.setStyleSheet(
                "QLabel { background-color: #2f261b; border: 1px solid #7c5828; border-radius: 4px; padding: 6px; color: #ffa657; }"
            )

        if self._sym_data.notes:
            msg += "\n[{}] {}".format(self._sym_data.sample_space.upper(), self._sym_data.notes)
        self.base_status_lbl.setText(msg)
        self.goto_ops_btn.setVisible(self._sym_data.paired_count > 0 or self._sym_data.center_count > 0)

    def _refresh_alt_base_label(self):
        t = _TR[self._lang]
        if self._alt_base_mesh:
            self.alt_base_lbl.setText(t["rev_base_alt"].format(name=self._alt_base_mesh))
        else:
            self.alt_base_lbl.setText(t["rev_base_orig"])

    # ------------------------------------------------------------------
    # Signal Wiring & State Helpers
    # ------------------------------------------------------------------

    def _connect_signals(self):
        self.load_base_btn.clicked.connect(self._on_load_base_mesh)
        self.clear_base_btn.clicked.connect(self._clear_base)
        self.base_field.textChanged.connect(self._on_base_text_changed)

        self.ss_group.buttonClicked.connect(self._on_sample_space_changed)
        self.axis_group.buttonClicked.connect(self._on_axis_changed)
        self.uv_auto_center_chk.toggled.connect(lambda checked: self.uv_center_spin.setEnabled(not checked))
        self.uv_refresh_btn.clicked.connect(self._refresh_uv_sets)

        self.load_edges_btn.clicked.connect(self._load_selected_seed_edges)
        self.clear_edges_btn.clicked.connect(self._clear_seed_edges)

        self.build_sym_btn.clicked.connect(self._on_build_symmetry_data)
        self.sel_asym_btn.clicked.connect(self._select_unmatched)
        self.goto_ops_btn.clicked.connect(lambda: self.tab_widget.setCurrentWidget(self.ops_tab))

        self.mirror_btn.clicked.connect(self._on_mirror_selected)
        self.flip_btn.clicked.connect(self._on_flip_selected)

        self.revert_btn.clicked.connect(lambda: self._on_revert_bias(1.0))
        self.revert_btn.customContextMenuRequested.connect(self._show_revert_context_menu)
        self.overshoot_chk.toggled.connect(self._on_overshoot_toggled)
        self.revert_slider.sliderPressed.connect(self._on_revert_drag_start)
        self.revert_slider.valueChanged.connect(self._on_revert_slider_changed)
        self.revert_slider.sliderReleased.connect(self._on_revert_drag_end)
        self.revert_spin.editingFinished.connect(self._on_revert_spin_committed)
        self.commit_rev_btn.clicked.connect(self._commit_revert_cache)

    def _get_sample_space(self):
        idx = self.ss_group.checkedId()
        return (
            symUtil.SAMPLE_WORLD,
            symUtil.SAMPLE_LOCAL,
            symUtil.SAMPLE_UV,
            symUtil.SAMPLE_TOPOLOGY,
        )[idx]

    def _get_axis(self):
        return self.axis_group.checkedId()

    def _get_settings(self):
        return {
            "sample_space": self._get_sample_space(),
            "axis": self._get_axis(),
            "origin_mode": self.origin_combo.currentData(),
            "tolerance": float(self.tol_spin.value()),
            "uv_set": self.uv_set_combo.currentText().strip(),
            "uv_axis": self.uv_axis_group.checkedId(),
            "uv_center": float(self.uv_center_spin.value()),
            "uv_auto_center": self.uv_auto_center_chk.isChecked(),
            "uv_tolerance": float(self.uv_tol_spin.value()),
            "seed_edges": self._parse_seed_edges(),
            "fallback_unreached": self.fallback_combo.currentData(),
            "neg_to_pos": self.neg_to_pos_chk.isChecked(),
        }

    def _parse_seed_edges(self):
        text = self.seed_edges_edit.text().strip()
        if not text:
            return []
        tokens = [tok.strip() for tok in text.replace(",", " ").split() if tok.strip()]
        parsed = []
        for tok in tokens:
            if tok.isdigit():
                parsed.append(int(tok))
            else:
                parsed.append(tok)
        return parsed

    def _on_base_text_changed(self, text):
        if self._sym_data is None and not self._build_error_msg:
            self._refresh_status_label()

    def _on_sample_space_changed(self, *args):
        self._update_sample_space_visibility()

    def _update_sample_space_visibility(self):
        ss = self._get_sample_space()
        self.uv_widget.setVisible(ss == symUtil.SAMPLE_UV)
        self.topo_widget.setVisible(ss == symUtil.SAMPLE_TOPOLOGY)
        self.adjustSize()

    def _on_axis_changed(self, *args):
        self._update_axis_direction_text()
        if self._sym_data is not None and self._sym_data.axis != self._get_axis():
            self._invalidate_symmetry_data()

    def _update_base_dependent_ui(self):
        has_base = self._sym_data is not None and cmds.objExists(self._sym_data.base_mesh)
        for widget in (
            self.mirror_btn,
            self.flip_btn,
            self.revert_btn,
            self.revert_slider,
            self.revert_spin,
            self.commit_rev_btn,
        ):
            widget.setEnabled(has_base)

        for action in self._ops_actions:
            action.setEnabled(has_base)
        self.sel_mirror_act.setEnabled(has_base)
        self.sel_moved_act.setEnabled(has_base)
        self.sel_asym_action.setEnabled(has_base)
        self.sel_ctr_action.setEnabled(has_base)

    # ------------------------------------------------------------------
    # Step 1 & Step 2 Helpers (Base Load, UV Sets, Seed Edges)
    # ------------------------------------------------------------------

    def _on_load_base_mesh(self):
        mesh_name, _, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select one polygon mesh.")
            return

        self.base_field.setText(mesh_name)
        self._invalidate_symmetry_data()
        self._populate_uv_sets_for_mesh(mesh_name)

    def _populate_uv_sets_for_mesh(self, mesh_name):
        try:
            uv_sets = symUtil.get_uv_sets(mesh_name)
            current_uv = symUtil.get_current_uv_set(mesh_name)
        except Exception:
            return
        if not uv_sets:
            return
        prev = self.uv_set_combo.currentText()
        self.uv_set_combo.clear()
        self.uv_set_combo.addItems(uv_sets)
        if prev in uv_sets:
            self.uv_set_combo.setCurrentText(prev)
        elif current_uv in uv_sets:
            self.uv_set_combo.setCurrentText(current_uv)

    def _refresh_uv_sets(self):
        target = self.base_field.text().strip()
        if not target or not cmds.objExists(target):
            mesh_name, _, err = symUtil.resolve_selection()
            target = mesh_name if not err and mesh_name else ""

        if not target:
            cmds.warning("Enter/load a Base Mesh or select a mesh to query UV sets.")
            return
        self._populate_uv_sets_for_mesh(target)

    def _load_selected_seed_edges(self):
        base_hint = self.base_field.text().strip() or None
        if base_hint and not cmds.objExists(base_hint):
            base_hint = None
        edge_ids, err = symUtil.extract_selected_edge_indices(mesh_name=base_hint)
        if err:
            cmds.warning(err)
            return
        self._seed_edges = edge_ids
        self.seed_edges_edit.setText(", ".join(str(e) for e in edge_ids))

    def _clear_seed_edges(self):
        self._seed_edges = []
        self.seed_edges_edit.clear()

    # ------------------------------------------------------------------
    # Step 3: Build Symmetry Data
    # ------------------------------------------------------------------

    def _on_build_symmetry_data(self):
        mesh_name = self.base_field.text().strip()
        if not mesh_name:
            sel_mesh, _, err = symUtil.resolve_selection()
            if not err and sel_mesh:
                mesh_name = sel_mesh
                self.base_field.setText(mesh_name)
            else:
                self._sym_data = None
                self._build_error_msg = err or "No Base Mesh specified."
                self._build_error_space = self._get_sample_space()
                self._refresh_status_label()
                self._update_base_dependent_ui()
                cmds.warning(self._build_error_msg)
                return

        if not cmds.objExists(mesh_name):
            self._sym_data = None
            self._build_error_msg = "Mesh does not exist: {}".format(mesh_name)
            self._build_error_space = self._get_sample_space()
            self._refresh_status_label()
            self._update_base_dependent_ui()
            cmds.warning(self._build_error_msg)
            return

        settings = self._get_settings()
        if settings["sample_space"] == symUtil.SAMPLE_UV:
            self._populate_uv_sets_for_mesh(mesh_name)
            settings["uv_set"] = self.uv_set_combo.currentText().strip()

        try:
            sym_data = symUtil.build_symmetry_data(
                mesh_name,
                sample_space=settings["sample_space"],
                axis=settings["axis"],
                origin_mode=settings["origin_mode"],
                tolerance=settings["tolerance"],
                uv_set=settings["uv_set"],
                uv_axis=settings["uv_axis"],
                uv_center=settings["uv_center"],
                uv_auto_center=settings["uv_auto_center"],
                uv_tolerance=settings["uv_tolerance"],
                seed_edges=settings["seed_edges"],
                fallback_unreached=settings["fallback_unreached"],
            )
        except Exception as exc:
            self._sym_data = None
            self._build_error_msg = str(exc)
            self._build_error_space = settings["sample_space"]
            self._refresh_status_label()
            self._update_base_dependent_ui()
            cmds.warning(str(exc))
            return

        self._build_error_msg = ""
        self._build_error_space = ""
        self._sym_data = sym_data
        self._alt_base_mesh = ""
        self._commit_revert_cache()
        self.base_field.setText(sym_data.base_mesh)
        self._refresh_alt_base_label()

        if sym_data.sample_space == symUtil.SAMPLE_TOPOLOGY and sym_data.seed_edges and not self.seed_edges_edit.text().strip():
            self.seed_edges_edit.setText(", ".join(str(e) for e in sym_data.seed_edges))

        if not sym_data.is_symmetrical:
            cmds.warning(
                "Base geometry '{}' has {} unmatched vertices under '{}' space. {}".format(
                    sym_data.base_mesh,
                    sym_data.unmatched_count,
                    sym_data.sample_space,
                    self._get_sample_space_hint(sym_data.sample_space),
                )
            )
        self._refresh_status_label()
        self._update_base_dependent_ui()
        self.adjustSize()

    def _invalidate_symmetry_data(self):
        self._sym_data = None
        self._build_error_msg = ""
        self._build_error_space = ""
        self._alt_base_mesh = ""
        self._commit_revert_cache()
        self._refresh_alt_base_label()
        self._refresh_status_label()
        self._update_base_dependent_ui()

    def _clear_base(self):
        self.base_field.clear()
        self._invalidate_symmetry_data()

    def _select_unmatched(self):
        if self._sym_data is None or not cmds.objExists(self._sym_data.base_mesh):
            return
        unmatched = self._sym_data.unmatched_indices
        if len(unmatched) == 0:
            cmds.inViewMessage(amg="No unmatched vertices.", pos="botCenter", fade=True)
            return
        symUtil.select_vertex_indices(self._sym_data.base_mesh, unmatched)

    def _select_center(self):
        if self._sym_data is None or not cmds.objExists(self._sym_data.base_mesh):
            return
        symUtil.select_vertex_indices(self._sym_data.base_mesh, self._sym_data.center_indices)

    # ------------------------------------------------------------------
    # Selection, Mirror & Flip Actions
    # ------------------------------------------------------------------

    def _on_selection_mirror(self):
        if self._sym_data is None:
            return
        mesh_name, vert_indices, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select vertices on a mesh.")
            return
        if vert_indices is None or len(vert_indices) == 0:
            cmds.warning("Select vertices to mirror selection.")
            return
        mirrored_indices = symUtil.mirror_selection(self._sym_data, vert_indices)
        symUtil.select_vertex_indices(mesh_name, mirrored_indices)

    def _on_select_moved(self, use_alt_base=False):
        if self._sym_data is None:
            return
        mesh_name, _, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select a target mesh.")
            return

        ref_base = self._get_revert_base_mesh() if use_alt_base else self._sym_data.base_mesh
        if not cmds.objExists(ref_base):
            cmds.warning("Base mesh does not exist: {}".format(ref_base))
            return

        try:
            moved = symUtil.get_moved_verts(mesh_name, ref_base, tolerance=self.tol_spin.value())
            symUtil.select_vertex_indices(mesh_name, moved)
            print("{} moved vert(s)".format(len(moved)))
        except Exception as exc:
            cmds.warning(str(exc))

    def _on_mirror_selected(self):
        if self._sym_data is None:
            return
        mesh_name, vert_indices, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select a mesh or vertices.")
            return

        try:
            symUtil.mirror_vertices(
                mesh_name,
                self._sym_data,
                vert_indices=vert_indices,
                neg_to_pos=self.neg_to_pos_chk.isChecked(),
                origin_mode=self.origin_combo.currentData(),
                undoable=True,
            )
        except Exception as exc:
            cmds.warning(str(exc))

    def _on_flip_selected(self):
        if self._sym_data is None:
            return
        mesh_name, vert_indices, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select a mesh or vertices.")
            return

        try:
            symUtil.flip_vertices(
                mesh_name,
                self._sym_data,
                vert_indices=vert_indices,
                origin_mode=self.origin_combo.currentData(),
                undoable=True,
            )
        except Exception as exc:
            cmds.warning(str(exc))

    # ------------------------------------------------------------------
    # Revert to Base Actions (Button, Context Menu, Interactive Slider)
    # ------------------------------------------------------------------

    def _get_revert_base_mesh(self):
        if self._alt_base_mesh and cmds.objExists(self._alt_base_mesh):
            return self._alt_base_mesh
        return self._sym_data.base_mesh if self._sym_data else ""

    def _on_revert_bias(self, bias):
        if self._sym_data is None:
            return
        mesh_name, vert_indices, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select a mesh or vertices.")
            return

        ref_base = self._get_revert_base_mesh()
        try:
            symUtil.revert_vertices(
                mesh_name,
                ref_base,
                bias=bias,
                vert_indices=vert_indices,
                undoable=True,
            )
        except Exception as exc:
            cmds.warning(str(exc))

    def _show_revert_context_menu(self, pos):
        t = _TR[self._lang]
        menu = QtWidgets.QMenu(self.revert_btn)
        presets_1 = (1, 2, 3, 4, 5)
        presets_2 = (10, 20, 30, 40, 50, 60, 70, 80, 90)

        for pct in presets_1:
            _add_menu_action(menu, "{}%".format(pct), lambda _=False, b=pct / 100.0: self._on_revert_bias(b))
        menu.addSeparator()
        for pct in presets_2:
            _add_menu_action(menu, "{}%".format(pct), lambda _=False, b=pct / 100.0: self._on_revert_bias(b))

        menu.addSeparator()
        cur_lbl = t["ctx_using_alt"].format(name=self._alt_base_mesh) if self._alt_base_mesh else t["ctx_using_orig"]
        info_act = menu.addAction(cur_lbl)
        info_act.setEnabled(False)
        menu.addSeparator()

        _add_menu_action(menu, t["ctx_use_sel_base"], lambda: self._set_alternate_base(True))
        orig_act = _add_menu_action(menu, t["ctx_use_orig_base"], lambda: self._set_alternate_base(False))
        orig_act.setEnabled(bool(self._alt_base_mesh))
        moved_alt_act = _add_menu_action(
            menu, t["ctx_sel_moved_alt"], lambda: self._on_select_moved(use_alt_base=True)
        )
        moved_alt_act.setEnabled(bool(self._alt_base_mesh))

        menu.exec_(self.revert_btn.mapToGlobal(pos))

    def _set_alternate_base(self, use_selected):
        if not use_selected:
            self._alt_base_mesh = ""
            self._commit_revert_cache()
            self._refresh_alt_base_label()
            return

        if self._sym_data is None:
            return
        mesh_name, _, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning("Select one polygon mesh to use as alternate revert base.")
            return

        pts = symUtil.get_mesh_points_np(mesh_name, om.MSpace.kObject)
        if len(pts) != self._sym_data.num_verts:
            cmds.warning("Alternate base mesh vertex count does not match original base mesh.")
            return

        self._alt_base_mesh = mesh_name
        self._commit_revert_cache()
        self._refresh_alt_base_label()

    def _on_overshoot_toggled(self, checked):
        self._syncing_revert = True
        try:
            if checked:
                self.revert_slider.setRange(-500, 1500)
                self.revert_spin.setRange(-50.0, 150.0)
            else:
                self.revert_slider.setRange(0, 1000)
                self.revert_spin.setRange(0.0, 100.0)
                val = max(0.0, min(100.0, self.revert_spin.value()))
                self.revert_spin.setValue(val)
                self.revert_slider.setValue(int(round(val * 10.0)))
        finally:
            self._syncing_revert = False

    def _prepare_revert_cache(self):
        mesh_name, vert_indices, err = symUtil.resolve_selection()
        if err or not mesh_name:
            cmds.warning(err or "Select a mesh or vertices.")
            return False

        ref_base = self._get_revert_base_mesh()
        if not cmds.objExists(ref_base):
            return False

        same_target = (
            self._rev_mesh == mesh_name
            and self._rev_orig_pts is not None
            and self._rev_base_pts is not None
            and (
                (vert_indices is None and self._rev_indices is None)
                or (
                    vert_indices is not None
                    and self._rev_indices is not None
                    and np.array_equal(vert_indices, self._rev_indices)
                )
            )
        )
        if same_target:
            return True

        orig_pts = symUtil.get_mesh_points_np(mesh_name, om.MSpace.kObject)
        base_pts = symUtil.get_mesh_points_np(ref_base, om.MSpace.kObject)
        if orig_pts.shape != base_pts.shape:
            cmds.warning("Vertex count mismatch with base mesh.")
            return False

        self._rev_mesh = mesh_name
        self._rev_indices = vert_indices.copy() if vert_indices is not None else None
        self._rev_orig_pts = orig_pts
        self._rev_base_pts = base_pts
        return True

    def _commit_revert_cache(self):
        self._rev_mesh = ""
        self._rev_indices = None
        self._rev_orig_pts = None
        self._rev_base_pts = None
        self._syncing_revert = True
        try:
            self.revert_slider.setValue(0)
            self.revert_spin.setValue(0.0)
        finally:
            self._syncing_revert = False

    def _on_revert_drag_start(self):
        self._rev_dragging = True
        if not self._prepare_revert_cache():
            self._rev_dragging = False

    def _on_revert_slider_changed(self, slider_val):
        if self._syncing_revert:
            return
        pct = slider_val / 10.0
        self._syncing_revert = True
        try:
            self.revert_spin.setValue(pct)
        finally:
            self._syncing_revert = False

        if not self._rev_dragging:
            if not self._prepare_revert_cache():
                return

        if self._rev_orig_pts is None:
            return

        symUtil.revert_vertices(
            self._rev_mesh,
            self._get_revert_base_mesh(),
            bias=pct / 100.0,
            vert_indices=self._rev_indices,
            orig_points=self._rev_orig_pts,
            base_points=self._rev_base_pts,
            undoable=False,
        )

    def _on_revert_drag_end(self):
        if not self._rev_dragging:
            return
        self._rev_dragging = False
        if self._rev_orig_pts is None or not self._rev_mesh:
            return

        bias = self.revert_slider.value() / 1000.0
        symUtil.set_mesh_points_np(self._rev_mesh, self._rev_orig_pts, space=om.MSpace.kObject, undoable=False)
        symUtil.revert_vertices(
            self._rev_mesh,
            self._get_revert_base_mesh(),
            bias=bias,
            vert_indices=self._rev_indices,
            orig_points=self._rev_orig_pts,
            base_points=self._rev_base_pts,
            undoable=True,
        )

    def _on_revert_spin_committed(self):
        if self._syncing_revert:
            return
        pct = self.revert_spin.value()
        self._syncing_revert = True
        try:
            self.revert_slider.setValue(int(round(pct * 10.0)))
        finally:
            self._syncing_revert = False

        if not self._prepare_revert_cache():
            return
        symUtil.set_mesh_points_np(self._rev_mesh, self._rev_orig_pts, space=om.MSpace.kObject, undoable=False)
        symUtil.revert_vertices(
            self._rev_mesh,
            self._get_revert_base_mesh(),
            bias=pct / 100.0,
            vert_indices=self._rev_indices,
            orig_points=self._rev_orig_pts,
            base_points=self._rev_base_pts,
            undoable=True,
        )

    # ------------------------------------------------------------------
    # Blendshape Operations & Tools Menu
    # ------------------------------------------------------------------

    def _run_blend_op(self, operation, mirror, use_target_as_base):
        if self._sym_data is None:
            cmds.warning("Build symmetry data first.")
            return

        sel = cmds.ls(sl=True) or []
        if len(sel) != 2:
            cmds.warning("Select two mesh objects: source (A) then target (B).")
            return

        try:
            src = symUtil.get_transform_name(sel[0])
            trg = symUtil.get_transform_name(sel[1])
        except ValueError as exc:
            cmds.warning(str(exc))
            return

        if src == self._sym_data.base_mesh or trg == self._sym_data.base_mesh:
            cmds.warning("Base mesh cannot be used as source or target. Use Revert instead.")
            return

        try:
            symUtil.blendshape_operation(
                self._sym_data.base_mesh,
                src,
                trg,
                self._sym_data,
                operation=operation,
                mirror=mirror,
                use_target_as_base=use_target_as_base,
                undoable=True,
            )
        except Exception as exc:
            cmds.warning(str(exc))

    def _open_restore_symmetry(self):
        if self._restore_dialog is not None:
            try:
                self._restore_dialog.close()
                self._restore_dialog.deleteLater()
            except Exception:
                pass
        self._restore_dialog = RestoreSymmetryDialog(self, self._get_settings, lang=self._lang)
        self._restore_dialog.show()


def show_ui():
    """Launch or focus the SymMesh window."""
    return SymMeshUI.show_ui()


def UI():
    """Alias matching takTools convention."""
    return show_ui()
