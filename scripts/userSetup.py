import subprocess
import maya.cmds as cmds


cmds.undoInfo(state=True, infinity=True)
cmds.optionVar(iv=("undoIsInfinite", 1))

cmds.optionVar(iv=("isIncrementalSaveEnabled", 0))
cmds.evalDeferred("cmds.keyTangent(e=True, g=True, itt='linear')", lowestPriority=True)
cmds.evalDeferred("cmds.keyTangent(e=True, g=True, ott='linear')", lowestPriority=True)


def _find_port_owner_pids(port):
    pids = []
    try:
        res = subprocess.run(
            ['netstat', '-ano', '-p', 'TCP'],
            capture_output=True,
            text=True,
            timeout=3,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        suffix = ':{}'.format(port)
        for line in res.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[1].endswith(suffix) and parts[3].upper() == 'LISTENING':
                if parts[4] not in pids:
                    pids.append(parts[4])
    except Exception:
        pass
    return pids


def _open_command_ports():
    port_groups = (
        ('mel', (20200, 20210, 20220, 20230)),
        ('python', (20201, 20211, 20221, 20231)),
    )
    fallback_notices = []
    failed_messages = []

    for source_type, candidate_ports in port_groups:
        base_port = candidate_ports[0]
        base_owner_pids = []
        opened_port = None

        for port in candidate_ports:
            try:
                cmds.commandPort(n=':{}'.format(port), sourceType=source_type)
                opened_port = port
                break
            except Exception as exc:
                pids = _find_port_owner_pids(port)
                if port == base_port:
                    base_owner_pids = pids
                    owner_info = ' (점유 PID: {})'.format(', '.join(pids)) if pids else ''
                    cmds.warning('commandPort :{} ({}) 오픈 실패{}: {}'.format(port, source_type, owner_info, exc))

        if opened_port is None:
            failed_messages.append(':{} (PID {})'.format(base_port, ', '.join(base_owner_pids) if base_owner_pids else '?'))
        elif opened_port != base_port:
            owner_info = ' (PID {})'.format(', '.join(base_owner_pids)) if base_owner_pids else ''
            msg = '[takTools] 기본 포트(:{}) 점유{}로 인해 대체 commandPort(:{})를 열었습니다.'.format(
                base_port, owner_info, opened_port
            )
            cmds.warning(msg)
            fallback_notices.append(':{}->:{}'.format(base_port, opened_port))

    if not cmds.about(batch=True):
        if failed_messages:
            notice = (
                'TakTools commandPort 오픈 실패: {}. '
                '백그라운드 좀비 maya.exe가 포트를 점유 중일 수 있습니다.'
            ).format(', '.join(failed_messages))
            cmds.evalDeferred(
                lambda m=notice: cmds.inViewMessage(amg=m, pos='topCenter', fade=True, fadeStayTime=8000),
                lowestPriority=True,
            )
        elif fallback_notices:
            notice = (
                'TakTools 기본 포트 점유로 대체 commandPort({})를 열었습니다.'
            ).format(', '.join(fallback_notices))
            cmds.evalDeferred(
                lambda m=notice: cmds.inViewMessage(amg=m, pos='topCenter', fade=True, fadeStayTime=6000),
                lowestPriority=True,
            )


_open_command_ports()


cmds.evalDeferred("import takTools.takToolsMenu as takToolsMenu;takToolsMenu.showMenu()", lowestPriority=True)
cmds.evalDeferred("from takTools import tak_tools;tak_tools.UI()", lowestPriority=True)
cmds.evalDeferred("from takTools.common import errorFix_look", lowestPriority=True)
