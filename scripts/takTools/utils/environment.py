import pymel.core as pm
import re


def getFrameRange():
    return pm.env.maxTime - pm.env.minTime + 1


def getMayaVersion():
    mainVersion = None

    fullVersion = pm.versions.current()
    searchObj = re.search(r'(\d{4})\d+', str(fullVersion))
    if searchObj:
        mainVersion = searchObj.group(1)

    return int(mainVersion)


def getProjectPath():
    return pm.workspace(q=True, rootDirectory=True)
