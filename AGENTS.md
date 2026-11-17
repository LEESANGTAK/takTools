모든 대화 및 기획서, 일감, 보고서 등의 artifacts 문서는 한글을 사용해 주세요.

## Maya 실시간 연동 및 takTools 환경
- 사용자의 Maya는 시작 시 `D:\tools\maya\modules\takTools\scripts\userSetup.py`를 통해 항상 다음 `commandPort`가 자동으로 열려 있습니다:
  - Python 포트: `127.0.0.1:20201` (`sourceType='python'`)
  - MEL 포트: `127.0.0.1:20200` (`sourceType='mel'`)
- 현재 열려 있는 Maya 씬을 조회·조작하거나 Script Editor 로그를 확인할 때는 별도의 MCP나 추가 포트 없이 `D:\tools\maya\modules\takTools\scripts\takTools\utils\maya_remote.py` 헬퍼 스크립트를 사용하세요:
  - 인라인 Python 실행: `python "D:\tools\maya\modules\takTools\scripts\takTools\utils\maya_remote.py" -c "<python_code>"`
  - 다중 라인 Python 실행 (PowerShell stdin): `@' ... '@ | python "D:\tools\maya\modules\takTools\scripts\takTools\utils\maya_remote.py"`
  - 스크립트 파일 실행: `python "D:\tools\maya\modules\takTools\scripts\takTools\utils\maya_remote.py" -f "<script_path>"`
  - Script Editor 최근 로그 조회: `python "D:\tools\maya\modules\takTools\scripts\takTools\utils\maya_remote.py" --logs 15000`
- 사용자의 커스텀 Maya 툴 모듈 경로는 `D:\tools\maya\modules\takTools`이며, 코딩 규칙은 `D:\tools\maya\modules\takTools\CODING_STYLE.md`를 따릅니다.
