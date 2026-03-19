# utils - 순수 유틸리티 함수

이 패키지에는 Maya API를 감싸는 **저수준 순수 유틸리티 함수**가 포함됩니다.
UI를 포함하지 않으며, 다른 모듈에서 import하여 재사용할 수 있도록 설계되었습니다.

## 모듈 구조

| 모듈 | 역할 |
|------|------|
| `joint.py` | 조인트 관련 유틸리티 |
| `mesh.py` | 메쉬 관련 유틸리티 |
| `skin.py` | 스킨클러스터 유틸리티 |
| `transform.py` | 트랜스폼 관련 유틸리티 |
| `curve.py` | 커브 관련 유틸리티 |
| `material.py` | 머터리얼 관련 유틸리티 |
| `name.py` | 네이밍 유틸리티 |
| `globalUtil.py` | 전역/씬 유틸리티 |
| `mathUtil.py` | 수학 유틸리티 |
| `qtUtil.py` | Qt UI 유틸리티 |
| `system.py` | 시스템/OS 유틸리티 |
| `display.py` | 디스플레이 유틸리티 |
| `blendshape.py` | 블렌드셰이프 유틸리티 |
| `cluster.py` | 클러스터 유틸리티 |
| `anim.py` | 애니메이션 유틸리티 |
| `camera.py` | 카메라 유틸리티 |
| `uv.py` | UV 유틸리티 |
| `vector.py` | 벡터 연산 유틸리티 |
| `matrix.py` | 매트릭스 연산 유틸리티 |
| `kdTree.py` | KD-Tree 공간 탐색 |
| `surface.py` | 서피스 유틸리티 |

## `common/` 패키지와의 차이점

- **`utils/`**: UI 없음, 순수 함수, Maya API 래핑, 저수준
- **`common/`**: UI 포함 가능, 복합 도구, 고수준
