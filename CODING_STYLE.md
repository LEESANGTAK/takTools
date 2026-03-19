# takTools 코딩 스타일 가이드

## 파일 명명 규칙

### 현재 상태 (레거시)
프로젝트에 여러 명명 패턴이 혼재합니다. 기존 파일은 호환성을 위해 이름을 유지합니다.

| 패턴 | 예시 | 비고 |
|------|------|------|
| `tak_` 접두사 + camelCase | `tak_cleanUpModel.py` | 자체 작성 모듈 |
| camelCase | `hairTools.py` | 자체 작성 유틸리티 |
| 외부 라이브러리 원본명 | `bSkinSaver.py` | 변경하지 않음 |

### 새 파일 작성 시 규칙
- **snake_case** 사용 (PEP 8): `skin_utils.py`, `display_tools.py`
- `tak_` 접두사 **사용하지 않음** (패키지가 이미 `takTools`)
- 외부 라이브러리는 원본 이름 유지

### 클래스/함수 명명
- 클래스: **PascalCase** → `SkinWeights`, `Controller`
- 함수: **camelCase** (레거시 호환) 또는 **snake_case** (신규)
- 상수: **UPPER_SNAKE_CASE** → `MODULE_NAME`, `DEFAULT_ICONS_DIR`

## 패키지 구조 규칙

```
scripts/takTools/
├── common/    # UI 포함 가능한 고수준 도구
├── utils/     # UI 없는 순수 유틸리티 함수
├── animation/ # 애니메이션 도메인 도구
├── modeling/  # 모델링 도메인 도구
├── rigging/   # 리깅 도메인 도구
├── fx/        # FX 도메인 도구
├── pipeline/  # 파이프라인 도구
└── widgets/   # 커스텀 Qt 위젯
```

## import 규칙
- `from imp import reload` → `from importlib import reload` (Python 3.4+)
- 새 코드에서 분리된 모듈 직접 import 권장:
  ```python
  # 권장
  from takTools.common.tak_skin import addInfCopySkin
  # 레거시 호환 (동작하지만 비권장)
  from takTools.common.tak_misc import addInfCopySkin
  ```
