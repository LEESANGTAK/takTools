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

        # 뷰포트 카메라 방향 벡터 캐시
        self.cam_right = None
        self.cam_up = None

        # OpenMaya 2.0 고속 가속 캐시
        self.cached_mesh_name = None
        self.mesh_dag = None
        self.fn_mesh = None
        self.mesh_inv_matrix = None
        self.neighbors_map = None          # {vtx_idx: tuple(connected_vtx_ids)}
        self.faces_map = None              # {vtx_idx: tuple(connected_face_ids)}
        self.face_normals_cache = None     # [MVector(face_0_normal), ...]

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
        return 'python("print(\'Normal Brush tool closed.\')")'

    def setup_mesh_cache(self, mesh_name):
        """ 메시의 DAG, MFnMesh, 토폴로지 연결 정보를 구축 및 캐싱 """
        if not cmds.objExists(mesh_name):
            return False

        try:
            sel = om.MSelectionList()
            sel.add(mesh_name)
            dag = sel.getDagPath(0)
            dag.extendToShape()

            self.mesh_dag = dag
            self.fn_mesh = om.MFnMesh(dag)
            self.mesh_inv_matrix = dag.inclusiveMatrixInverse()

            # 메시가 바뀌었거나 캐시가 없을 때만 토폴로지 맵 1회 생성 (초고속 O(1) 룩업 보장)
            if self.cached_mesh_name != mesh_name or self.neighbors_map is None:
                num_vtx = self.fn_mesh.numVertices
                it_vtx = om.MItMeshVertex(dag)
                neighbors_map = [None] * num_vtx
                faces_map = [None] * num_vtx

                while not it_vtx.isDone():
                    idx = it_vtx.index()
                    neighbors_map[idx] = tuple(it_vtx.getConnectedVertices())
                    faces_map[idx] = tuple(it_vtx.getConnectedFaces())
                    it_vtx.next()

                self.neighbors_map = neighbors_map
                self.faces_map = faces_map

                # 페이스 노말 캐시 (기하학적 페이스 노말은 불변이므로 캐싱)
                num_faces = self.fn_mesh.numPolygons
                self.face_normals_cache = [
                    self.fn_mesh.getPolygonNormal(f_i, om.MSpace.kObject).normal()
                    for f_i in range(num_faces)
                ]
                self.cached_mesh_name = mesh_name

            return True
        except Exception:
            return False

    def on_stroke_init(self, surface_name=""):
        """ 스트로크 시작 시 마우스 위치, 카메라 방향, 메시 캐시 초기화 """
        if QCursor:
            self.last_cursor_pos = QCursor.pos()
        else:
            self.last_cursor_pos = None
        self.current_drag_vector = None

        # 활성 뷰포트 카메라의 Right / Up 벡터 캡처
        try:
            view = omui.M3dView.active3dView()
            cam_dag = view.getCamera()
            cam_matrix = cam_dag.inclusiveMatrix()
            self.cam_right = om.MVector(cam_matrix[0], cam_matrix[1], cam_matrix[2]).normal()
            self.cam_up = om.MVector(cam_matrix[4], cam_matrix[5], cam_matrix[6]).normal()
        except Exception:
            self.cam_right = om.MVector(1, 0, 0)
            self.cam_up = om.MVector(0, 1, 0)

        # 타겟 메시 캐시 선행 설정
        target_mesh = None
        if surface_name and cmds.objExists(surface_name):
            target_mesh = surface_name.split(".")[0]
        else:
            selection = cmds.ls(sl=True)
            if selection:
                target_mesh = selection[0].split(".")[0]

        if target_mesh:
            self.setup_mesh_cache(target_mesh)

    def on_stroke_finalize(self):
        """ 스트로크 종료 시 캐시 정리 및 뷰포트 갱신 """
        self.last_cursor_pos = None
        self.current_drag_vector = None
        if self.fn_mesh:
            try:
                self.fn_mesh.updateSurface()
            except Exception:
                pass

    def calculate_drag_vector(self, dx, dy):
        """ 캐싱된 카메라와 메시 역행렬을 이용해 초고속으로 메시 로컬 드래그 방향 벡터 계산 """
        if not self.cam_right or not self.cam_up or not self.mesh_inv_matrix:
            return None

        # 화면 2D 드래그를 뷰포트 월드 3D 벡터로 변환 (스크린 Y축은 아래 방향이 +이므로 -dy)
        world_dir = (self.cam_right * dx) + (self.cam_up * (-dy))
        if world_dir.length() < 1e-4:
            return None
        world_dir.normalize()

        # 월드 방향 벡터를 메시 오브젝트 로컬 좌표계로 변환
        local_dir = (world_dir * self.mesh_inv_matrix).normal()
        return local_dir

    def get_vertex_normal(self, vertex_index):
        """ 버텍스에 편집/고정된 커스텀 노말을 고속 조회 """
        fcs = self.faces_map[vertex_index]
        if fcs:
            return self.fn_mesh.getFaceVertexNormal(fcs[0], vertex_index, om.MSpace.kObject).normal()
        return self.fn_mesh.getVertexNormal(vertex_index, om.MSpace.kObject).normal()

    def apply_normal_to_vertex(self, vertex_index, brush_value):
        """ OpenMaya 2.0 기반 초고속 노말 연산 및 적용 """
        try:
            # 캐시 유효성 검사 및 보정
            if not self.fn_mesh or not self.neighbors_map:
                selection = cmds.ls(sl=True)
                if not selection:
                    return
                mesh_name = selection[0].split(".")[0]
                if not self.setup_mesh_cache(mesh_name):
                    return

            if vertex_index >= len(self.neighbors_map):
                return

            # 1. 키보드 수정자(Modifier Key) 상태 체크 (Shift=1, Ctrl=4)
            modifiers = cmds.getModifiers()
            is_shift_pressed = (modifiers & 1) == 1
            is_ctrl_pressed = (modifiers & 4) == 4

            target_vector = om.MVector(0, 0, 0)

            if is_shift_pressed:
                # =============================================================
                # [Shift 누름] 주변 버텍스들의 평균 노말 계산 (Smooth 모드)
                # =============================================================
                nbrs = self.neighbors_map[vertex_index]
                if not nbrs:
                    return

                sum_norm = om.MVector(0, 0, 0)
                for n_idx in nbrs:
                    sum_norm += self.get_vertex_normal(n_idx)

                if sum_norm.length() < 1e-5:
                    return

                target_vector = sum_norm.normal()

            elif is_ctrl_pressed:
                # =============================================================
                # [Ctrl 누름] 연결된 페이스들의 수직 노말 평균 계산 (Face Normal 수직 정렬)
                # =============================================================
                fcs = self.faces_map[vertex_index]
                if not fcs:
                    return

                sum_face = om.MVector(0, 0, 0)
                for f_idx in fcs:
                    sum_face += self.face_normals_cache[f_idx]

                if sum_face.length() < 1e-5:
                    return

                target_vector = sum_face.normal()

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
                        new_dir = self.calculate_drag_vector(dx, dy)
                        if new_dir:
                            self.current_drag_vector = new_dir
                            self.last_cursor_pos = curr_pos

                if not self.current_drag_vector:
                    return

                target_vector = om.MVector(self.current_drag_vector)

                # 노말이 면 안쪽으로 파고들어 뒤집히는(Flipped) 현상 방지
                fcs = self.faces_map[vertex_index]
                if fcs:
                    sum_face = om.MVector(0, 0, 0)
                    for f_idx in fcs:
                        sum_face += self.face_normals_cache[f_idx]

                    if sum_face.length() > 1e-5:
                        face_norm = sum_face.normal()
                        dot = target_vector * face_norm
                        # 페이스 노말과의 내적이 너무 낮으면(면 안쪽으로 향하면) 표면 바깥쪽으로 최소 0.1 보정
                        if dot < 0.1:
                            target_vector = (target_vector - face_norm * dot) + face_norm * 0.1
                            target_vector.normalize()

            # 2. 브러시 압력 및 설정 강도(brush_value) 기준으로 선형 보간(Lerp) 연산
            curr_vector = self.get_vertex_normal(vertex_index)

            # 현재 노말에서 타겟 방향 벡터로 브러시 세기만큼 점진적으로 회전 및 변형
            final_vector = (curr_vector * (1.0 - brush_value)) + (target_vector * brush_value)
            final_vector.normalize()

            # 3. OpenMaya MFnMesh를 통해 버텍스 노말을 C++ 메모리 레벨에서 즉시 적용
            self.fn_mesh.setVertexNormal(final_vector, vertex_index, om.MSpace.kObject)

        except Exception:
            pass

    def run(self):
        cmds.setToolTo(self.ctx_name)


def run_brush():
    global brush_instance
    brush_instance = NormalAverageBrush()
    brush_instance.run()
