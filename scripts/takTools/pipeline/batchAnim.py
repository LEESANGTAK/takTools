import subprocess
import pymel.core as pm


MAYAPY = r"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe"
ROOT_JOINT = 'Root'
WIN_NAME = 'batchAnimWin'


def showUI():
    if pm.window(WIN_NAME, exists=True): pm.deleteUI(WIN_NAME)

    pm.window(WIN_NAME, title='Batch Anim UI', mnb=False, mxb=False)
    pm.columnLayout(adj=True, rowSpacing=5)

    pm.textScrollList('mayaFilesTxtScrLs', allowMultiSelection=True)
    pm.rowLayout(adj=2, numberOfColumns=2)
    pm.button(label='Add', w=150, ann='Add maya files.', c=__addBtnCallback)
    pm.button(label='Remove', w=150, ann='Remove selected files from the list.', c=__removeBtnCallback)

    pm.setParent('..')
    pm.separator(style='none')
    pm.button(label='Batch Export Anim', c=__batchAnimCallback)
    pm.progressBar('batchAnimProgBar')
    pm.window(WIN_NAME, e=True, w=10, h=10)
    pm.showWindow(WIN_NAME)


def __addBtnCallback(*args):
    files = pm.fileDialog2(fm=4, fileFilter='Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)')
    if files:
        existsItems = pm.textScrollList('mayaFilesTxtScrLs', q=True, allItems=True)
        for file in files:
            if file in existsItems:
                continue
            pm.textScrollList('mayaFilesTxtScrLs', e=True, append=file)


def __removeBtnCallback(*args):
    selItems = pm.textScrollList('mayaFilesTxtScrLs', q=True, selectItem=True)
    if selItems:
        for selItem in selItems:
            pm.textScrollList('mayaFilesTxtScrLs', e=True, removeItem=selItem)


def __batchAnimCallback(*args):
    mayaFiles = pm.textScrollList('mayaFilesTxtScrLs', q=True, allItems=True)
    if mayaFiles:
        pm.progressBar('batchAnimProgBar', e=True, max=len(mayaFiles))
        for mayaFile in mayaFiles:
            job = subprocess.Popen([
                    MAYAPY,
                    '-c', 'import maya.standalone; maya.standalone.initialize(); from takTools.pipeline import batchAnim;import imp;imp.reload(batchAnim); batchAnim.exportAnim("{}")'.format(mayaFile)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            out, err = job.communicate()
            pm.progressBar('batchAnimProgBar', e=True, step=1)


def exportAnim(mayaFile):
    pm.openFile(mayaFile, f=True)

    import exporter.fbx_exporter as fbx_exporter
    exporter = fbx_exporter.FBXExporter()
    exporter.fbx_export_properties.bake_animation = True
    exporter.fbx_export_properties.export_animation = True
    exporter.fbx_export_properties.set_fbx_properties()

    rootJnt = pm.ls("*:{}".format(ROOT_JOINT), recursive=True)
    pm.select(rootJnt, hi=True, r=True)
    export_filepath = mayaFile.replace('.ma', '.fbx')
    exporter.export_selected(export_filepath)
