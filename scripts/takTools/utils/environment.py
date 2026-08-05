from maya import cmds
import re


def getFrameRange():
    return cmds.playbackOptions(q=True, maxTime=True) - cmds.playbackOptions(q=True, minTime=True) + 1


def getMayaVersion():
    mainVersion = None

    fullVersion = cmds.about(version=True)
    searchObj = re.search(r'(\d{4})\d+', str(fullVersion))
    if searchObj:
        mainVersion = searchObj.group(1)

    return int(mainVersion)


def getProjectPath():
    return cmds.workspace(q=True, rootDirectory=True)
