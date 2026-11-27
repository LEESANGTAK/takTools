"""Maya commandPort(:20201) 원격 Python 실행 및 로그 조회 헬퍼 모듈.

CLI 사용 예시:
    python maya_remote.py -c "import maya.cmds as cmds; print(cmds.ls(sl=True))"
    python maya_remote.py -f my_script.py
    python maya_remote.py --logs 8000
    @'
    import maya.cmds as cmds
    print(cmds.about(version=True))
    '@ | python maya_remote.py
"""

import argparse
import base64
import json
import socket
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 20201
DEFAULT_CANDIDATE_PORTS = (20201, 20211, 20221, 20231)
PROBE_TIMEOUT = 1.5
DEFAULT_TIMEOUT = 30.0

_RUNNER_TEMPLATE = """
import ast, base64, io, json, sys, traceback
_code = base64.b64decode({b64_user!r}).decode('utf-8')
_out, _err = io.StringIO(), io.StringIO()
_old_out, _old_err = sys.stdout, sys.stderr
sys.stdout, sys.stderr = _out, _err
_ok = True
_res = None
_tb = None
try:
    _tree = ast.parse(_code, '<maya_remote>', 'exec')
    if _tree.body and isinstance(_tree.body[-1], ast.Expr):
        _last = ast.Expression(_tree.body.pop().value)
        ast.fix_missing_locations(_tree)
        ast.fix_missing_locations(_last)
        if _tree.body:
            exec(compile(_tree, '<maya_remote>', 'exec'), globals())
        _val = eval(compile(_last, '<maya_remote>', 'eval'), globals())
        if _val is not None:
            _res = repr(_val)
    else:
        exec(compile(_tree, '<maya_remote>', 'exec'), globals())
except Exception:
    _ok = False
    _tb = traceback.format_exc()
finally:
    sys.stdout, sys.stderr = _old_out, _old_err
_MAYA_REMOTE_RES_ = json.dumps(
    {{"ok": _ok, "stdout": _out.getvalue(), "stderr": _err.getvalue(), "result": _res, "error": _tb}},
    ensure_ascii=False,
)
"""


def _probe_port(host, port, timeout=PROBE_TIMEOUT):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.sendall(b"1+1")
            data = sock.recv(1024)
            return bool(data)
    except OSError:
        return False


def _resolve_port(host, port, probe_timeout=PROBE_TIMEOUT):
    if port is not None and port != DEFAULT_PORT:
        return port
    ports_to_try = (DEFAULT_PORT,) + tuple(p for p in DEFAULT_CANDIDATE_PORTS if p != DEFAULT_PORT)
    for candidate in ports_to_try:
        if _probe_port(host, candidate, timeout=probe_timeout):
            return candidate
    return DEFAULT_PORT


def _send_expression(expr, host=DEFAULT_HOST, port=None, timeout=DEFAULT_TIMEOUT):
    resolved_port = _resolve_port(host, port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((host, resolved_port))
        sock.sendall(expr.encode("utf-8"))
        chunks = []
        while True:
            try:
                data = sock.recv(65536)
                if not data:
                    break
                chunks.append(data)
                if b"\x00" in data:
                    break
            except socket.timeout:
                break
    return b"".join(chunks).decode("utf-8", errors="replace").rstrip("\x00\r\n")


def execute_python(code, host=DEFAULT_HOST, port=None, timeout=DEFAULT_TIMEOUT):
    """Maya 세션에서 다중 라인 Python 코드를 실행하고 출력/반환값/에러를 딕셔너리로 반환한다."""
    b64_user = base64.b64encode(code.encode("utf-8")).decode("ascii")
    runner_code = _RUNNER_TEMPLATE.format(b64_user=b64_user)
    b64_runner = base64.b64encode(runner_code.encode("utf-8")).decode("ascii")
    expr = (
        f"(__import__('builtins').exec(compile(__import__('base64').b64decode('{b64_runner}')"
        f".decode('utf-8'), '<maya_remote>', 'exec'), globals()), globals().pop('_MAYA_REMOTE_RES_', ''))[1]"
    )
    raw = _send_expression(expr, host=host, port=port, timeout=timeout)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "stdout": "", "stderr": "", "result": None, "error": f"Raw response: {raw}"}


def get_script_editor_log(max_chars=15000, host=DEFAULT_HOST, port=None, timeout=DEFAULT_TIMEOUT):
    """Maya Script Editor(cmdScrollFieldReporter)의 최근 로그 텍스트를 반환한다."""
    code = f"""
import maya.cmds as cmds
reporters = cmds.lsUI(type='cmdScrollFieldReporter') or []
out = []
for r in reporters:
    txt = cmds.cmdScrollFieldReporter(r, q=True, text=True) or ''
    out.append(f'=== {{r}} (len={{len(txt)}}) ===\\n' + txt[-{int(max_chars)}:])
print('\\n'.join(out))
"""
    res = execute_python(code, host=host, port=port, timeout=timeout)
    if not res["ok"]:
        raise RuntimeError(res["error"])
    return res["stdout"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Execute Python code or fetch logs from a running Maya session.")
    parser.add_argument("-c", "--code", help="Inline Python code to execute in Maya.")
    parser.add_argument("-f", "--file", help="Path to a Python script file to execute in Maya.")
    parser.add_argument(
        "--logs",
        nargs="?",
        const=15000,
        type=int,
        help="Fetch recent Maya Script Editor logs (optional max characters, default: 15000).",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Maya host (default: {DEFAULT_HOST}).")
    parser.add_argument("-p", "--port", type=int, default=None, help=f"Maya commandPort (default: auto-probe starting at {DEFAULT_PORT}).")
    parser.add_argument("-t", "--timeout", type=float, default=DEFAULT_TIMEOUT, help="Socket timeout in seconds.")
    parser.add_argument("--json", action="store_true", help="Print full result as JSON.")

    args = parser.parse_args()

    if args.logs is not None:
        print(get_script_editor_log(max_chars=args.logs, host=args.host, port=args.port, timeout=args.timeout), end="")
        return

    if args.code is not None:
        code = args.code
    elif args.file is not None:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    elif not sys.stdin.isatty():
        code = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    res = execute_python(code, host=args.host, port=args.port, timeout=args.timeout)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res["ok"] else 1)

    if res["stdout"]:
        print(res["stdout"], end="" if res["stdout"].endswith("\n") else "\n")
    if res["stderr"]:
        print(res["stderr"], file=sys.stderr, end="" if res["stderr"].endswith("\n") else "\n")
    if res["result"] is not None:
        print(res["result"])
    if not res["ok"] and res["error"]:
        print(res["error"], file=sys.stderr, end="" if res["error"].endswith("\n") else "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
