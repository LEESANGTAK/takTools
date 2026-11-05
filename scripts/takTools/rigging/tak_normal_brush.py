import maya.cmds as cmds
import maya.api.OpenMaya as om

class NormalAverageBrush(object):
    def __init__(self):
        self.ctx_name = "normalAverageBrushContext"
        self.mel_proc_name = "NormalAverageBrushCallback"
        self.setup_mel_procedure()
        self.setup_context()

    def setup_mel_procedure(self):
        """Artisan이 던져주는 인자를 받아 파이썬으로 토스해주는 징검다리 MEL 프로시저"""
        mel_code = f"""
        global proc {self.mel_proc_name}(int $slot, int $index, float $value) {{
            python("brush_instance.apply_normal_to_vertex(" + $index + ", " + $value + ")");
        }}
        """
        import maya.mel as mel
        mel.eval(mel_code)

    def setup_context(self):
        # 기존 동일한 이름의 컨텍스트가 있다면 삭제
        if cmds.artUserPaintCtx(self.ctx_name, exists=True):
            cmds.deleteUI(self.ctx_name)

        # Artisan User Paint Context 생성
        cmds.artUserPaintCtx(self.ctx_name,
                             image1="polyNormal.png",
                             whichTool="userPaint",
                             initializeCmd=self.get_initialize_cmd(),
                             finalizeCmd=self.get_finalize_cmd(),
                             setValueCommand=self.mel_proc_name,
                             getValueCommand="",
                             toolCleanupCmd=self.get_cleanup_cmd()
                             )

    def get_initialize_cmd(self):
        return 'python("import maya.cmds as cmds;\\nimport maya.api.OpenMaya as om")'

    def get_finalize_cmd(self):
        return 'python("print(\'Normal brush stroke finished.\')")'

    def get_cleanup_cmd(self):
        return 'python("print(\'Brush tool closed.\')")'

    def apply_normal_to_vertex(self, vertex_index, brush_value):
        """ 브러시 영역 내에 들어온 버텍스마다 실행되는 핵심 연산 함수 """
        selection = cmds.ls(sl=True)
        if not selection:
            return

        # 순수 메시 이름 추출
        mesh_name = selection[0]
        if "." in mesh_name:
            mesh_name = mesh_name.split(".")[0]

        vtx = f"{mesh_name}.vtx[{vertex_index}]"

        try:
            # 1. 키보드 Shift 상태 체크 (Shift를 누르면 1, 안 누르면 0)
            modifiers = cmds.getModifiers()
            is_shift_pressed = (modifiers & 1) == 1

            target_vector = om.MVector(0, 0, 0)

            if is_shift_pressed:
                # [Shift 누름] 주변 버텍스(Neighbors)의 평균 노말 계산
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

            else:
                # [일반 브러시질] 연결된 페이스(Face)들의 노말 평균 계산 (Face Normal 수직 정렬)
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

            # 2. 브러시 압력(가중치)을 고려하여 기존 노말과 보간 계산
            current_normals = cmds.polyNormalPerVertex(vtx, query=True, normalXYZ=True)
            if current_normals:
                curr_x = sum(current_normals[i] for i in range(0, len(current_normals), 3)) / (len(current_normals) // 3)
                curr_y = sum(current_normals[i] for i in range(1, len(current_normals), 3)) / (len(current_normals) // 3)
                curr_z = sum(current_normals[i] for i in range(2, len(current_normals), 3)) / (len(current_normals) // 3)
                curr_vector = om.MVector(curr_x, curr_y, curr_z).normal()

                final_vector = (curr_vector * (1.0 - brush_value)) + (target_vector * brush_value)
                final_vector.normalize()

                # 3. 최종 노말 적용
                cmds.polyNormalPerVertex(vtx, xyz=(final_vector.x, final_vector.y, final_vector.z))

        except Exception as e:
            pass

    def run(self):
        cmds.setToolTo(self.ctx_name)

def run_brush():
    global brush_instance
    brush_instance = NormalAverageBrush()
    brush_instance.run()
