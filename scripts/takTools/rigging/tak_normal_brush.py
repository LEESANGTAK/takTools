import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

try:
    from PySide6.QtGui import QCursor
except ImportError:
    try:
        from PySide2.QtGui import QCursor
    except ImportError:
        QCursor = None


class NormalAverageBrush(object):
    def __init__(self):
        # 모듈 전역 및 Maya __main__ 네임스페이스에 최신 인스턴스 등록
        global brush_instance
        brush_instance = self
        try:
            import __main__
            __main__.brush_instance = self
        except Exception:
            pass

        self.ctx_name = "normalAverageBrushContext"
        self.mel_proc_name = "NormalAverageBrushCallback"
        self.mel_init_proc_name = "NormalAverageBrushInitCallback"
        self.mel_finalize_proc_name = "NormalAverageBrushFinalizeCallback"

        # 스트로크 마우스 추적 및 방향 캐시 변수
        self.last_cursor_pos = None
        self.current_drag_vector = None

        self.setup_mel_procedures()
        self.setup_context()

    def setup_mel_procedures(self):
        """ Artisan이 던져주는 인자를 받아 파이썬으로 토스해주는 징검다리 MEL 프로시저 """
        import maya.mel as mel

        mel_code = f"""
        global proc string {self.mel_init_proc_name}(string $surfaceName) {{
            python("import takTools.rigging.tak_normal_brush as tnb; tnb.brush_instance.on_stroke_init('" + $surfaceName + "') if hasattr(tnb, 'brush_instance') and hasattr(tnb.brush_instance, 'on_stroke_init') else None");
            return "";
        }}

        global proc {self.mel_finalize_proc_name}(int $slot) {{
            python("import takTools.rigging.tak_normal_brush as tnb; tnb.brush_instance.on_stroke_finalize() if hasattr(tnb, 'brush_instance') and hasattr(tnb.brush_instance, 'on_stroke_finalize') else None");
        }}

        global proc {self.mel_proc_name}(int $slot, int $index, float $value) {{
            python("import takTools.rigging.tak_normal_brush as tnb; tnb.brush_instance.apply_normal_to_vertex(" + $index + ", " + $value + ") if hasattr(tnb, 'brush_instance') else None");
        }}
        """
        mel.eval(mel_code)

    def setup_context(self):
        # 기존 동일한 이름의 컨텍스트가 있다면 삭제
        if cmds.artUserPaintCtx(self.ctx_name, exists=True):
            cmds.deleteUI(self.ctx_name)

        # Artisan User Paint Context 생성
        cmds.artUserPaintCtx(self.ctx_name,
                             image1="polyNormal.png",
                             whichTool="userPaint",
                             initializeCmd=self.mel_init_proc_name,
                             finalizeCmd=self.mel_finalize_proc_name,
                             setValueCommand=self.mel_proc_name,
                             getValueCommand="",
                             toolCleanupCmd=self.get_cleanup_cmd()
                             )

    def get_cleanup_cmd(self):
        return 'python("print(\'Brush tool closed.\')")'

    def on_stroke_init(self, surface_name=""):
        """ 스트로크 시작 시 마우스 커서 위치 및 방향 벡터 초기화 """
        if QCursor:
            self.last_cursor_pos = QCursor.pos()
        else:
            self.last_cursor_pos = None
        self.current_drag_vector = None

    def on_stroke_finalize(self):
        """ 스트로크 종료 시 캐시 초기화 """
        self.last_cursor_pos = None
        self.current_drag_vector = None

    def calculate_drag_vector(self, dx, dy, mesh_name):
        """ 뷰포트 마우스 드래그(dx, dy)를 메시 오브젝트 로컬 공간의 방향 벡터로 변환 """
        try:
            view = omui.M3dView.active3dView()
            cam_dag = view.getCamera()
            cam_matrix = cam_dag.inclusiveMatrix()

            # 카메라의 Right(+X), Up(+Y) 벡터
            cam_right = om.MVector(cam_matrix[0], cam_matrix[1], cam_matrix[2]).normal()
            cam_up = om.MVector(cam_matrix[4], cam_matrix[5], cam_matrix[6]).normal()

            # 화면 2D 드래그를 뷰포트 카메라 기준 월드 3D 벡터로 변환 (스크린 Y축은 아래 방향이 +이므로 -dy)
            world_dir = (cam_right * dx) + (cam_up * (-dy))
            if world_dir.length() < 1e-4:
                return None
            world_dir.normalize()

            # 월드 방향 벡터를 메시 오브젝트 로컬 좌표계로 변환
            sel = om.MSelectionList()
            sel.add(mesh_name)
            mesh_dag = sel.getDagPath(0)
            inv_matrix = mesh_dag.inclusiveMatrixInverse()

            local_dir = (world_dir * inv_matrix).normal()
            return local_dir
        except Exception:
            return None

    def apply_normal_to_vertex(self, vertex_index, brush_value):
        """ 조합 키(Modifiers) 상태에 따라 각기 다른 노말 제어 연산을 수행하는 핵심 함수 """
        selection = cmds.ls(sl=True)
        if not selection:
            return

        # 순수 메시 이름 추출
        mesh_name = selection[0]
        if "." in mesh_name:
            mesh_name = mesh_name.split(".")[0]

        vtx = f"{mesh_name}.vtx[{vertex_index}]"

        try:
            # 1. 키보드 수정자(Modifier Key) 상태 체크 (Shift=1, Ctrl=4)
            modifiers = cmds.getModifiers()
            is_shift_pressed = (modifiers & 1) == 1
            is_ctrl_pressed = (modifiers & 4) == 4

            target_vector = om.MVector(0, 0, 0)

            if is_shift_pressed:
                # =============================================================
                # [Shift 누름] 주변 버텍스들의 평균 노말 계산 (Smooth 모드)
                # =============================================================
                connected_edges = cmds.polyListComponentConversion(vtx, toEdge=True)
                neighbor_vertices = cmds.polyListComponentConversion(connected_edges, toVertex=True)
                neighbor_vertices = cmds.ls(neighbor_vertices, flatten=True)

                if vtx in neighbor_vertices:
                    neighbor_vertices.remove(vtx)

                if not neighbor_vertices:
                    return

                sum_x, sum_y, sum_z = 0.0, 0.0, 0.0
                count = 0

                for n_vtx in neighbor_vertices:
                    normals = cmds.polyNormalPerVertex(n_vtx, query=True, normalXYZ=True)
                    if normals:
                        vtx_num_elements = len(normals) // 3
                        vtx_sum_x = sum(normals[i] for i in range(0, len(normals), 3)) / vtx_num_elements
                        vtx_sum_y = sum(normals[i] for i in range(1, len(normals), 3)) / vtx_num_elements
                        vtx_sum_z = sum(normals[i] for i in range(2, len(normals), 3)) / vtx_num_elements

                        sum_x += vtx_sum_x
                        sum_y += vtx_sum_y
                        sum_z += vtx_sum_z
                        count += 1

                if count == 0:
                    return

                target_vector = om.MVector(sum_x / count, sum_y / count, sum_z / count).normal()

            elif is_ctrl_pressed:
                # =============================================================
                # [Ctrl 누름] 연결된 페이스들의 수직 노말 평균 계산 (Face Normal 수직 정렬)
                # =============================================================
                connected_faces = cmds.polyListComponentConversion(vtx, toFace=True)
                connected_faces = cmds.ls(connected_faces, flatten=True)

                if not connected_faces:
                    return

                f_sum_x, f_sum_y, f_sum_z = 0.0, 0.0, 0.0
                f_count = 0

                for face in connected_faces:
                    f_normals = cmds.polyInfo(face, faceNormals=True)
                    if f_normals:
                        parts = f_normals[0].split()
                        f_sum_x += float(parts[-3])
                        f_sum_y += float(parts[-2])
                        f_sum_z += float(parts[-1])
                        f_count += 1

                if f_count == 0:
                    return

                target_vector = om.MVector(f_sum_x / f_count, f_sum_y / f_count, f_sum_z / f_count).normal()

            else:
                # =============================================================
                # [그냥 드래그] 마우스 뷰포트 드래그(스트로크) 방향으로 노말 기울이기 (Comb 모드)
                # =============================================================
                if QCursor:
                    curr_pos = QCursor.pos()
                    if self.last_cursor_pos is None:
                        self.last_cursor_pos = curr_pos

                    dx = curr_pos.x() - self.last_cursor_pos.x()
                    dy = curr_pos.y() - self.last_cursor_pos.y()
                    dist_sq = dx * dx + dy * dy

                    # 마우스가 2픽셀 이상 움직였을 때 드래그 방향 갱신 (스트로크 내 버텍스 공유)
                    if dist_sq >= 4:
                        new_dir = self.calculate_drag_vector(dx, dy, mesh_name)
                        if new_dir:
                            self.current_drag_vector = new_dir
                            self.last_cursor_pos = curr_pos

                if not self.current_drag_vector:
                    return

                target_vector = om.MVector(self.current_drag_vector)

                # 노말이 면 안쪽으로 파고들어 뒤집히는(Flipped) 현상 방지
                connected_faces = cmds.polyListComponentConversion(vtx, toFace=True)
                connected_faces = cmds.ls(connected_faces, flatten=True)
                if connected_faces:
                    f_sum_x, f_sum_y, f_sum_z = 0.0, 0.0, 0.0
                    f_count = 0
                    for face in connected_faces:
                        f_normals = cmds.polyInfo(face, faceNormals=True)
                        if f_normals:
                            parts = f_normals[0].split()
                            f_sum_x += float(parts[-3])
                            f_sum_y += float(parts[-2])
                            f_sum_z += float(parts[-1])
                            f_count += 1

                    if f_count > 0:
                        face_normal = om.MVector(f_sum_x / f_count, f_sum_y / f_count, f_sum_z / f_count).normal()
                        dot = target_vector * face_normal
                        # 페이스 노말과의 내적이 너무 낮으면(면 안쪽으로 향하면) 표면 바깥쪽으로 최소 0.1 보정
                        if dot < 0.1:
                            target_vector = (target_vector - face_normal * dot) + face_normal * 0.1
                            target_vector.normalize()

            # 2. 브러시 압력 및 설정 강도(brush_value)를 기준으로 선형 보간(Lerp) 연산
            current_normals = cmds.polyNormalPerVertex(vtx, query=True, normalXYZ=True)
            if current_normals:
                curr_x = sum(current_normals[i] for i in range(0, len(current_normals), 3)) / (len(current_normals) // 3)
                curr_y = sum(current_normals[i] for i in range(1, len(current_normals), 3)) / (len(current_normals) // 3)
                curr_z = sum(current_normals[i] for i in range(2, len(current_normals), 3)) / (len(current_normals) // 3)
                curr_vector = om.MVector(curr_x, curr_y, curr_z).normal()

                # 현재 노말에서 타겟 방향 벡터로 브러시 세기만큼 점진적으로 회전 및 변형
                final_vector = (curr_vector * (1.0 - brush_value)) + (target_vector * brush_value)
                final_vector.normalize()

                # 3. 최종 연산된 노말 방향을 버텍스에 할당
                cmds.polyNormalPerVertex(vtx, xyz=(final_vector.x, final_vector.y, final_vector.z))

        except Exception as e:
            pass

    def run(self):
        cmds.setToolTo(self.ctx_name)


def run_brush():
    global brush_instance
    brush_instance = NormalAverageBrush()
    brush_instance.run()
