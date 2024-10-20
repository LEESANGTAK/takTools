import os
import tempfile
import telnetlib
import threading
from maya import cmds, mel


HOST = "localhost"
BLENDER_PORT = 30301


def sendSelectedObjectsToBlender():
    meshes = cmds.filterExpand(cmds.ls(sl=True), sm=12)
    cmds.select(meshes, r=True)

    export_path = os.path.join(tempfile.gettempdir(), 'mayaExported.fbx')
    mel.eval('FBXExport -f "{}" -s'.format(export_path.replace('\\', '/')))

    tn = telnetlib.Telnet(HOST, BLENDER_PORT)
    tn.write(b"import_fbx " + export_path.encode('ascii') + b"\n")
    tn.close()

    removeFileDeffered(export_path)


def removeFileDeffered(filePath, delay_minutes=1):
    delay_seconds = delay_minutes * 60
    timer = threading.Timer(delay_seconds, remove_file, [filePath])
    timer.start()


def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except PermissionError:
        print(f"Permission denied: unable to delete '{file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
