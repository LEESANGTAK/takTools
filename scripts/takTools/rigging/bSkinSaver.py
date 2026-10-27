"""
=====================================================================
    Tool for saving and loading skinWeights in Maya

    (c) 2013 - 2016 by Thomas Bittner
    thomasbittner@hotmail.de

    source the file and then run: showUI()


=====================================================================

"""



import os
import shutil
import difflib
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
from maya import cmds, mel
import maya.OpenMayaUI as mui
import time


MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    import shiboken2 as shiboken
elif 2025 <= MAYA_VERSION:
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    import shiboken6 as shiboken


EXT = '.sw'


def getSelectedGeometries():
    selShapes = cmds.ls(sl=True, dag=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface'])
    selGeos = cmds.filterExpand(selShapes, sm=[9, 10, 12])
    return selGeos


def showUI():
    global mainWin
    mainWin = bSkinSaverUI()
    mainWin.show()

    dirName = os.path.dirname(mainWin.objectsFileLine.text())
    fileName = 'fileName{}'.format(EXT)
    selGeos = getSelectedGeometries()
    if selGeos:
        fileName = selGeos[0] + EXT
    mainWin.objectsFileLine.setText(os.path.join(dirName, fileName))


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr:
        return shiboken.wrapInstance(int(ptr), QWidget)
    return None



def parseSwFileJoints(inputFile):
    """
    Parses a .sw file and returns:
    - objects: list of object names
    - objectJoints: dict of { objectName: [joint1, joint2, ...] }
    - uniqueJoints: list of unique joint names in order of appearance
    """
    if not os.path.isfile(inputFile):
        return [], {}, []

    objects = []
    objectJoints = {}
    uniqueJoints = []
    seen = set()

    currentObj = None
    filePosition = 0

    with open(inputFile, 'r') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                if filePosition == 2:
                    filePosition = 0
                continue

            if filePosition == 0:
                currentObj = stripped
                objects.append(currentObj)
                objectJoints[currentObj] = []
                filePosition = 1
            elif filePosition == 1:
                if stripped.startswith("============"):
                    filePosition = 2
                else:
                    objectJoints[currentObj].append(stripped)
                    if stripped not in seen:
                        seen.add(stripped)
                        uniqueJoints.append(stripped)
            elif filePosition == 2:
                # weight line
                pass

    return objects, objectJoints, uniqueJoints


def getSceneGeometryNames():
    """
    Returns unique short names of all geometry transforms in the Maya scene.
    """
    shapes = cmds.ls(dag=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface']) or []
    if not shapes:
        return []
    transforms = cmds.listRelatives(shapes, p=True, fullPath=False) or []
    seen = set()
    result = []
    for t in transforms:
        short = t.split('|')[-1]
        if short not in seen:
            seen.add(short)
            result.append(short)
    return result


def checkMissingGeometries(fileGeos, namespace=''):
    """
    Checks which geometries in fileGeos do not exist in the Maya scene.
    Returns:
    - missingGeos: list of geometries in file that don't exist in scene
    - existingGeos: list of geometries in file that do exist in scene
    """
    sceneGeos = set(getSceneGeometryNames())
    missing = []
    existing = []

    for fg in fileGeos:
        target = (namespace + fg) if namespace and not fg.startswith(namespace) else fg
        if target in sceneGeos or fg in sceneGeos or cmds.objExists(target):
            existing.append(fg)
        else:
            missing.append(fg)

    return missing, existing


def autoMatchGeometry(fileGeo, sceneGeos):
    """
    Tries to find the best match for fileGeo in sceneGeos.
    """
    if not sceneGeos or not fileGeo:
        return None

    fileLower = fileGeo.lower()
    for sg in sceneGeos:
        if sg.lower() == fileLower:
            return sg

    def normalizeGeo(n):
        n = n.lower()
        for s in ['_geo', '_mesh', '_ply', '_shape', '_geom', '_grp']:
            if n.endswith(s):
                n = n[:-len(s)]
        return n

    normFile = normalizeGeo(fileGeo)
    for sg in sceneGeos:
        if normalizeGeo(sg) == normFile:
            return sg

    matches = difflib.get_close_matches(fileGeo, sceneGeos, n=1, cutoff=0.55)
    if matches:
        return matches[0]

    return None


def getSceneJointNames():
    """
    Returns unique short names of all joints in the Maya scene.
    """
    joints = cmds.ls(type='joint') or []
    shortNames = [j.split('|')[-1] for j in joints]
    seen = set()
    result = []
    for name in shortNames:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def checkMissingJoints(fileJoints, namespace=''):
    """
    Checks which joints in fileJoints do not exist in the Maya scene.
    Returns:
    - missingJoints: list of joints in file that don't exist in scene
    - existingJoints: list of joints in file that do exist in scene
    """
    sceneJoints = set(getSceneJointNames())
    missing = []
    existing = []

    for fj in fileJoints:
        target = (namespace + fj) if namespace and not fj.startswith(namespace) else fj
        if target in sceneJoints or fj in sceneJoints or cmds.objExists(target):
            existing.append(fj)
        else:
            missing.append(fj)

    return missing, existing


def autoMatchJoint(fileJoint, sceneJoints):
    """
    Tries to find the best match for fileJoint in sceneJoints.
    """
    if not sceneJoints or not fileJoint:
        return None

    fileLower = fileJoint.lower()
    for sj in sceneJoints:
        if sj.lower() == fileLower:
            return sj

    def normalizeName(n):
        n = n.lower()
        if n.startswith('left_') or n.startswith('l_'):
            n = 'l_' + n.split('_', 1)[-1]
        elif n.startswith('right_') or n.startswith('r_'):
            n = 'r_' + n.split('_', 1)[-1]
        for s in ['_jnt', '_joint', '_bind', '_skn', '_drv', '_bn']:
            if n.endswith(s):
                n = n[:-len(s)]
        return n

    normFile = normalizeName(fileJoint)
    for sj in sceneJoints:
        if normalizeName(sj) == normFile:
            return sj

    matches = difflib.get_close_matches(fileJoint, sceneJoints, n=1, cutoff=0.55)
    if matches:
        return matches[0]

    return None


def updateSwFileWithMapping(inputFile, jointMapping=None, geoMapping=None, backup=True):
    """
    Updates geometry and joint names in .sw file according to:
    - geoMapping {oldGeoName: newGeoName}
    - jointMapping {oldJointName: newJointName}
    Optionally creates a .bak backup.
    """
    if not os.path.isfile(inputFile):
        cmds.warning("File does not exist: {}".format(inputFile))
        return False

    if backup:
        bakFile = inputFile + '.bak'
        try:
            shutil.copy2(inputFile, bakFile)
        except Exception as e:
            cmds.warning("Failed to create backup: {}".format(e))

    with open(inputFile, 'r') as f:
        lines = f.readlines()

    newLines = []
    filePosition = 0
    modifiedJointCount = 0
    modifiedGeoCount = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if filePosition == 2:
                filePosition = 0
            newLines.append(line)
            continue

        if filePosition == 0:
            filePosition = 1
            if geoMapping and stripped in geoMapping and geoMapping[stripped]:
                newGeo = geoMapping[stripped]
                ending = '\n' if line.endswith('\n') else ''
                newLines.append(newGeo + ending)
                if newGeo != stripped:
                    modifiedGeoCount += 1
            else:
                newLines.append(line)

        elif filePosition == 1:
            if stripped.startswith("============"):
                filePosition = 2
                newLines.append(line)
            else:
                if jointMapping and stripped in jointMapping and jointMapping[stripped]:
                    newJoint = jointMapping[stripped]
                    ending = '\n' if line.endswith('\n') else ''
                    newLines.append(newJoint + ending)
                    if newJoint != stripped:
                        modifiedJointCount += 1
                else:
                    newLines.append(line)

        elif filePosition == 2:
            newLines.append(line)

    with open(inputFile, 'w') as f:
        f.writelines(newLines)

    print("Updated {} geometry names and {} joint names in {}".format(
        modifiedGeoCount, modifiedJointCount, inputFile
    ))
    return True


remapDialogWin = None

def showSkinRemapDialog(swFilePath, namespace='', geoCheck=False, parent=getMayaWindow(), initialTab=0):
    global remapDialogWin
    if remapDialogWin is not None:
        try:
            remapDialogWin.close()
            remapDialogWin.deleteLater()
        except Exception:
            pass
    remapDialogWin = SkinRemapDialog(
        swFilePath=swFilePath,
        namespace=namespace,
        geoCheck=geoCheck,
        parent=parent,
        initialTab=initialTab
    )
    remapDialogWin.show()
    remapDialogWin.raise_()
    remapDialogWin.activateWindow()
    return remapDialogWin


class SkinRemapDialog(QDialog):
    def __init__(self, swFilePath, namespace='', geoCheck=False, parent=getMayaWindow(), initialTab=0):
        super(SkinRemapDialog, self).__init__(parent)
        self.swFilePath = swFilePath
        self.namespace = namespace
        self.geoCheck = geoCheck

        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setModal(False)

        self.sceneGeos = getSceneGeometryNames()
        self.sceneJoints = getSceneJointNames()
        self.objects, self.objectJoints, self.uniqueJoints = parseSwFileJoints(self.swFilePath)

        self.setWindowTitle('bSkinSaver - Remapper (Geometry & Joint)')
        self.resize(800, 620)

        self.initUI(initialTab)
        self.populateGeoTable()
        self.populateJointTable()
        self.updateSummary()
        self.applyGeoFilter()
        self.applyJointFilter()

    def initUI(self, initialTab):
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(6)

        # 1. Info Header
        infoGroup = QGroupBox("SW File Information")
        infoLayout = QVBoxLayout(infoGroup)
        infoLayout.setSpacing(3)

        fileLabel = QLabel("<b>File:</b> {}".format(self.swFilePath))
        fileLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        infoLayout.addWidget(fileLabel)

        self.summaryLabel = QLabel("")
        infoLayout.addWidget(self.summaryLabel)
        mainLayout.addWidget(infoGroup)

        # 2. Tab Widget
        self.tabWidget = QTabWidget()

        # Tab 1: Geometries
        geoTab = QWidget()
        self.initGeoTab(geoTab)
        self.tabWidget.addTab(geoTab, "🧊 Geometries")

        # Tab 2: Joints
        jointTab = QWidget()
        self.initJointTab(jointTab)
        self.tabWidget.addTab(jointTab, "🦴 Joints")

        self.tabWidget.setCurrentIndex(initialTab)
        mainLayout.addWidget(self.tabWidget)

        # 3. Bottom Action Buttons
        bottomLayout = QHBoxLayout()
        self.saveFileButton = QPushButton("Save Mapping to .sw File")
        self.saveFileButton.setToolTip("Permanently update geometry and joint names in the .sw file (creates a .bak backup)")
        self.saveFileButton.clicked.connect(self.saveMappingToFile)
        bottomLayout.addWidget(self.saveFileButton)

        bottomLayout.addStretch()

        self.loadWeightsButton = QPushButton("Load Weights with Mapping")
        self.loadWeightsButton.setStyleSheet("font-weight: bold; padding: 6px 16px; background-color: #3870a0; color: white;")
        self.loadWeightsButton.clicked.connect(self.loadWeightsWithMapping)
        bottomLayout.addWidget(self.loadWeightsButton)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        bottomLayout.addWidget(self.closeButton)

        mainLayout.addLayout(bottomLayout)

    # ------------------ Geometries Tab ------------------
    def initGeoTab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(6)

        toolsLayout = QHBoxLayout()
        self.geoShowMissingCheck = QCheckBox("Show Missing / Mapped Only")
        self.geoShowMissingCheck.setChecked(True)
        self.geoShowMissingCheck.toggled.connect(self.applyGeoFilter)
        toolsLayout.addWidget(self.geoShowMissingCheck)

        toolsLayout.addSpacing(10)
        toolsLayout.addWidget(QLabel("Filter:"))
        self.geoFilterEdit = QLineEdit()
        self.geoFilterEdit.setPlaceholderText("Search geometry name...")
        self.geoFilterEdit.textChanged.connect(self.applyGeoFilter)
        toolsLayout.addWidget(self.geoFilterEdit)

        self.geoAutoMatchAllButton = QPushButton("Smart Auto Match All")
        self.geoAutoMatchAllButton.clicked.connect(self.autoMatchAllGeos)
        toolsLayout.addWidget(self.geoAutoMatchAllButton)
        layout.addLayout(toolsLayout)

        self.geoTable = QTableWidget(0, 4)
        self.geoTable.setHorizontalHeaderLabels(["Status", "SW File Geometry", "Scene Target Geometry", "Suggested Match"])
        header = self.geoTable.horizontalHeader()
        if hasattr(header, 'setSectionResizeMode'):
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        else:
            header.setResizeMode(0, QHeaderView.ResizeToContents)
            header.setResizeMode(1, QHeaderView.Stretch)
            header.setResizeMode(2, QHeaderView.Stretch)
            header.setResizeMode(3, QHeaderView.ResizeToContents)

        self.geoTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.geoTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.geoTable.verticalHeader().setDefaultSectionSize(26)
        layout.addWidget(self.geoTable)

        selLayout = QHBoxLayout()
        self.geoAssignButton = QPushButton("Assign Selected from Maya")
        self.geoAssignButton.setToolTip("Assign selected mesh/curve from Maya viewport/outliner to table row(s)")
        self.geoAssignButton.clicked.connect(self.assignSelectedGeosFromMaya)
        selLayout.addWidget(self.geoAssignButton)

        self.geoSelectButton = QPushButton("Select Target in Maya")
        self.geoSelectButton.clicked.connect(self.selectTargetGeoInMaya)
        selLayout.addWidget(self.geoSelectButton)

        self.geoClearButton = QPushButton("Clear Selected")
        self.geoClearButton.clicked.connect(self.clearSelectedGeoRows)
        selLayout.addWidget(self.geoClearButton)
        selLayout.addStretch()
        layout.addLayout(selLayout)

    def populateGeoTable(self):
        self.geoTable.setRowCount(len(self.objects))
        sceneGeoSet = set(self.sceneGeos)

        for row, fg in enumerate(self.objects):
            target = (self.namespace + fg) if self.namespace and not fg.startswith(self.namespace) else fg
            inScene = (target in sceneGeoSet or fg in sceneGeoSet or cmds.objExists(target))

            statusItem = QTableWidgetItem()
            statusItem.setTextAlignment(Qt.AlignCenter)
            statusItem.setFlags(statusItem.flags() & ~Qt.ItemIsEditable)

            fgItem = QTableWidgetItem(fg)
            fgItem.setFlags(fgItem.flags() & ~Qt.ItemIsEditable)
            fgItem.setToolTip(fg)

            combo = QComboBox()
            combo.setEditable(True)
            combo.setInsertPolicy(QComboBox.NoInsert)
            combo.addItem("")
            combo.addItems(self.sceneGeos)

            completer = QCompleter(self.sceneGeos, combo)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            if hasattr(completer, 'setFilterMode') and hasattr(Qt, 'MatchContains'):
                completer.setFilterMode(Qt.MatchContains)
            combo.setCompleter(completer)

            suggested = autoMatchGeometry(fg, self.sceneGeos)
            suggestItem = QTableWidgetItem(suggested if suggested else "")
            suggestItem.setFlags(suggestItem.flags() & ~Qt.ItemIsEditable)
            if suggested:
                suggestItem.setToolTip("Double-click to apply '{}'".format(suggested))

            if inScene:
                matchedName = target if target in sceneGeoSet else fg
                combo.setCurrentText(matchedName)
                statusItem.setText("Found")
                statusItem.setForeground(QColor("#5cb85c"))
            else:
                if suggested:
                    combo.setCurrentText(suggested)
                    statusItem.setText("Suggested")
                    statusItem.setForeground(QColor("#f0ad4e"))
                else:
                    combo.setCurrentText("")
                    statusItem.setText("Missing")
                    statusItem.setForeground(QColor("#d9534f"))

            self.geoTable.setItem(row, 0, statusItem)
            self.geoTable.setItem(row, 1, fgItem)
            self.geoTable.setCellWidget(row, 2, combo)
            self.geoTable.setItem(row, 3, suggestItem)

            def makeGeoComboCallback(r):
                return lambda text: self.onGeoComboChanged(r, text)

            if hasattr(combo, 'currentTextChanged'):
                combo.currentTextChanged.connect(makeGeoComboCallback(row))
            else:
                combo.editTextChanged.connect(makeGeoComboCallback(row))

        self.geoTable.cellDoubleClicked.connect(self.onGeoCellDoubleClicked)

    def onGeoComboChanged(self, row, text):
        text = text.strip()
        fgItem = self.geoTable.item(row, 1)
        if not fgItem:
            return
        fg = fgItem.text()
        statusItem = self.geoTable.item(row, 0)
        sceneGeoSet = set(self.sceneGeos)

        target = (self.namespace + text) if self.namespace and not text.startswith(self.namespace) else text
        inScene = (target in sceneGeoSet or text in sceneGeoSet or (text and cmds.objExists(target)))

        if not text or not inScene:
            statusItem.setText("Missing")
            statusItem.setForeground(QColor("#d9534f"))
        elif text == fg or target == fg:
            statusItem.setText("Found")
            statusItem.setForeground(QColor("#5cb85c"))
        else:
            statusItem.setText("Mapped")
            statusItem.setForeground(QColor("#5bc0de"))

        self.updateSummary()

    def onGeoCellDoubleClicked(self, row, col):
        if col == 3:
            suggestItem = self.geoTable.item(row, 3)
            if suggestItem and suggestItem.text().strip():
                combo = self.geoTable.cellWidget(row, 2)
                if combo:
                    combo.setCurrentText(suggestItem.text().strip())
        elif col in [1, 2]:
            combo = self.geoTable.cellWidget(row, 2)
            if combo:
                tg = combo.currentText().strip()
                target = (self.namespace + tg) if self.namespace and not tg.startswith(self.namespace) else tg
                if cmds.objExists(target):
                    cmds.select(target, r=True)
                elif cmds.objExists(tg):
                    cmds.select(tg, r=True)

    def applyGeoFilter(self):
        onlyMissing = self.geoShowMissingCheck.isChecked()
        filterText = self.geoFilterEdit.text().strip().lower()

        for r in range(self.geoTable.rowCount()):
            stItem = self.geoTable.item(r, 0)
            fgItem = self.geoTable.item(r, 1)
            combo = self.geoTable.cellWidget(r, 2)
            if not stItem or not fgItem or not combo:
                continue

            status = stItem.text()
            fg = fgItem.text().lower()
            tg = combo.currentText().strip().lower()

            hide = False
            if onlyMissing and status == "Found":
                hide = True
            if filterText and (filterText not in fg and filterText not in tg):
                hide = True

            self.geoTable.setRowHidden(r, hide)

    def autoMatchAllGeos(self):
        self.sceneGeos = getSceneGeometryNames()
        sceneGeoSet = set(self.sceneGeos)

        selectedRows = sorted(list(set([idx.row() for idx in self.geoTable.selectedIndexes()])))
        if selectedRows:
            targetRows = selectedRows
        else:
            targetRows = []
            for r in range(self.geoTable.rowCount()):
                fgItem = self.geoTable.item(r, 1)
                if not fgItem:
                    continue
                fg = fgItem.text()
                target = (self.namespace + fg) if self.namespace and not fg.startswith(self.namespace) else fg
                if target in sceneGeoSet or fg in sceneGeoSet or cmds.objExists(target):
                    continue
                targetRows.append(r)

        matchedCount = 0
        clearedCount = 0

        for r in targetRows:
            fgItem = self.geoTable.item(r, 1)
            combo = self.geoTable.cellWidget(r, 2)
            suggestItem = self.geoTable.item(r, 3)
            if not fgItem or not combo:
                continue

            fg = fgItem.text()
            suggested = autoMatchGeometry(fg, self.sceneGeos)

            if suggestItem:
                suggestItem.setText(suggested if suggested else "")
                if suggested:
                    suggestItem.setToolTip("Double-click to apply '{}'".format(suggested))
                else:
                    suggestItem.setToolTip("")

            if suggested:
                combo.setCurrentText(suggested)
                matchedCount += 1
            else:
                combo.setCurrentText("")
                clearedCount += 1

        self.updateSummary()
        self.applyGeoFilter()
        cmds.inViewMessage(amg="<b>bSkinSaver:</b> Auto-matched {} geometry(s).".format(matchedCount), pos='topCenter', fade=True)

    def assignSelectedGeosFromMaya(self):
        sels = cmds.ls(sl=True) or []
        if not sels:
            cmds.warning("Please select geometry in Maya.")
            return

        # Find transform names of selected geometries
        selectedTransforms = []
        for s in sels:
            if cmds.nodeType(s) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
                parent = cmds.listRelatives(s, p=True)
                if parent:
                    selectedTransforms.append(parent[0].split('|')[-1])
            else:
                shapes = cmds.listRelatives(s, s=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface'])
                if shapes:
                    selectedTransforms.append(s.split('|')[-1])

        if not selectedTransforms:
            selectedTransforms = [s.split('|')[-1] for s in sels]

        selectedRows = sorted(list(set([idx.row() for idx in self.geoTable.selectedIndexes()])))
        if not selectedRows:
            curr = self.geoTable.currentRow()
            if curr >= 0:
                selectedRows = [curr]
        if not selectedRows:
            cmds.warning("Please select row(s) in the Geometries table.")
            return

        if len(selectedTransforms) == 1:
            for row in selectedRows:
                combo = self.geoTable.cellWidget(row, 2)
                if combo:
                    combo.setCurrentText(selectedTransforms[0])
        else:
            for i, row in enumerate(selectedRows):
                if i < len(selectedTransforms):
                    combo = self.geoTable.cellWidget(row, 2)
                    if combo:
                        combo.setCurrentText(selectedTransforms[i])

    def selectTargetGeoInMaya(self):
        selectedRows = sorted(list(set([idx.row() for idx in self.geoTable.selectedIndexes()])))
        targetsToSelect = []
        for r in selectedRows:
            combo = self.geoTable.cellWidget(r, 2)
            if combo:
                tg = combo.currentText().strip()
                if tg:
                    target = (self.namespace + tg) if self.namespace and not tg.startswith(self.namespace) else tg
                    if cmds.objExists(target):
                        targetsToSelect.append(target)
                    elif cmds.objExists(tg):
                        targetsToSelect.append(tg)

        if targetsToSelect:
            cmds.select(targetsToSelect, r=True)
        else:
            cmds.warning("No existing target geometries to select in Maya.")

    def clearSelectedGeoRows(self):
        selectedRows = sorted(list(set([idx.row() for idx in self.geoTable.selectedIndexes()])))
        for r in selectedRows:
            combo = self.geoTable.cellWidget(r, 2)
            if combo:
                combo.setCurrentText("")

    def getGeoMappingDict(self):
        mapping = {}
        for r in range(self.geoTable.rowCount()):
            fgItem = self.geoTable.item(r, 1)
            combo = self.geoTable.cellWidget(r, 2)
            if fgItem and combo:
                fg = fgItem.text()
                tg = combo.currentText().strip()
                if tg:
                    mapping[fg] = tg
        return mapping

    # ------------------ Joints Tab ------------------
    def initJointTab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(6)

        toolsLayout = QHBoxLayout()
        self.jointShowMissingCheck = QCheckBox("Show Missing / Mapped Only")
        self.jointShowMissingCheck.setChecked(True)
        self.jointShowMissingCheck.toggled.connect(self.applyJointFilter)
        toolsLayout.addWidget(self.jointShowMissingCheck)

        toolsLayout.addSpacing(10)
        toolsLayout.addWidget(QLabel("Filter:"))
        self.jointFilterEdit = QLineEdit()
        self.jointFilterEdit.setPlaceholderText("Search joint name...")
        self.jointFilterEdit.textChanged.connect(self.applyJointFilter)
        toolsLayout.addWidget(self.jointFilterEdit)

        self.jointAutoMatchAllButton = QPushButton("Smart Auto Match All")
        self.jointAutoMatchAllButton.clicked.connect(self.autoMatchAllJoints)
        toolsLayout.addWidget(self.jointAutoMatchAllButton)
        layout.addLayout(toolsLayout)

        replaceGroup = QGroupBox("Batch Search & Replace")
        replaceLayout = QHBoxLayout(replaceGroup)
        replaceLayout.setContentsMargins(6, 6, 6, 6)
        replaceLayout.addWidget(QLabel("Search:"))
        self.searchEdit = QLineEdit()
        self.searchEdit.setPlaceholderText("e.g. old_")
        replaceLayout.addWidget(self.searchEdit)

        replaceLayout.addWidget(QLabel("Replace:"))
        self.replaceEdit = QLineEdit()
        self.replaceEdit.setPlaceholderText("e.g. new_")
        replaceLayout.addWidget(self.replaceEdit)

        self.applyRuleButton = QPushButton("Apply Rule")
        self.applyRuleButton.clicked.connect(self.applyBatchRule)
        replaceLayout.addWidget(self.applyRuleButton)
        layout.addWidget(replaceGroup)

        self.jointTable = QTableWidget(0, 4)
        self.jointTable.setHorizontalHeaderLabels(["Status", "SW File Joint", "Scene Target Joint", "Suggested Match"])
        header = self.jointTable.horizontalHeader()
        if hasattr(header, 'setSectionResizeMode'):
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        else:
            header.setResizeMode(0, QHeaderView.ResizeToContents)
            header.setResizeMode(1, QHeaderView.Stretch)
            header.setResizeMode(2, QHeaderView.Stretch)
            header.setResizeMode(3, QHeaderView.ResizeToContents)

        self.jointTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.jointTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.jointTable.verticalHeader().setDefaultSectionSize(26)
        layout.addWidget(self.jointTable)

        selLayout = QHBoxLayout()
        self.jointAssignButton = QPushButton("Assign Selected from Maya")
        self.jointAssignButton.clicked.connect(self.assignSelectedJointsFromMaya)
        selLayout.addWidget(self.jointAssignButton)

        self.jointSelectButton = QPushButton("Select Target in Maya")
        self.jointSelectButton.clicked.connect(self.selectTargetJointInMaya)
        selLayout.addWidget(self.jointSelectButton)

        self.jointClearButton = QPushButton("Clear Selected")
        self.jointClearButton.clicked.connect(self.clearSelectedJointRows)
        selLayout.addWidget(self.jointClearButton)
        selLayout.addStretch()
        layout.addLayout(selLayout)

    def populateJointTable(self):
        self.jointTable.setRowCount(len(self.uniqueJoints))
        sceneJointSet = set(self.sceneJoints)

        for row, fj in enumerate(self.uniqueJoints):
            target = (self.namespace + fj) if self.namespace and not fj.startswith(self.namespace) else fj
            inScene = (target in sceneJointSet or fj in sceneJointSet or cmds.objExists(target))

            statusItem = QTableWidgetItem()
            statusItem.setTextAlignment(Qt.AlignCenter)
            statusItem.setFlags(statusItem.flags() & ~Qt.ItemIsEditable)

            fjItem = QTableWidgetItem(fj)
            fjItem.setFlags(fjItem.flags() & ~Qt.ItemIsEditable)
            fjItem.setToolTip(fj)

            combo = QComboBox()
            combo.setEditable(True)
            combo.setInsertPolicy(QComboBox.NoInsert)
            combo.addItem("")
            combo.addItems(self.sceneJoints)

            completer = QCompleter(self.sceneJoints, combo)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            if hasattr(completer, 'setFilterMode') and hasattr(Qt, 'MatchContains'):
                completer.setFilterMode(Qt.MatchContains)
            combo.setCompleter(completer)

            suggested = autoMatchJoint(fj, self.sceneJoints)
            suggestItem = QTableWidgetItem(suggested if suggested else "")
            suggestItem.setFlags(suggestItem.flags() & ~Qt.ItemIsEditable)
            if suggested:
                suggestItem.setToolTip("Double-click to apply '{}'".format(suggested))

            if inScene:
                matchedName = target if target in sceneJointSet else fj
                combo.setCurrentText(matchedName)
                statusItem.setText("Found")
                statusItem.setForeground(QColor("#5cb85c"))
            else:
                if suggested:
                    combo.setCurrentText(suggested)
                    statusItem.setText("Suggested")
                    statusItem.setForeground(QColor("#f0ad4e"))
                else:
                    combo.setCurrentText("")
                    statusItem.setText("Missing")
                    statusItem.setForeground(QColor("#d9534f"))

            self.jointTable.setItem(row, 0, statusItem)
            self.jointTable.setItem(row, 1, fjItem)
            self.jointTable.setCellWidget(row, 2, combo)
            self.jointTable.setItem(row, 3, suggestItem)

            def makeJointComboCallback(r):
                return lambda text: self.onJointComboChanged(r, text)

            if hasattr(combo, 'currentTextChanged'):
                combo.currentTextChanged.connect(makeJointComboCallback(row))
            else:
                combo.editTextChanged.connect(makeJointComboCallback(row))

        self.jointTable.cellDoubleClicked.connect(self.onJointCellDoubleClicked)

    def onJointComboChanged(self, row, text):
        text = text.strip()
        fjItem = self.jointTable.item(row, 1)
        if not fjItem:
            return
        fj = fjItem.text()
        statusItem = self.jointTable.item(row, 0)
        sceneJointSet = set(self.sceneJoints)

        target = (self.namespace + text) if self.namespace and not text.startswith(self.namespace) else text
        inScene = (target in sceneJointSet or text in sceneJointSet or (text and cmds.objExists(target)))

        if not text or not inScene:
            statusItem.setText("Missing")
            statusItem.setForeground(QColor("#d9534f"))
        elif text == fj or target == fj:
            statusItem.setText("Found")
            statusItem.setForeground(QColor("#5cb85c"))
        else:
            statusItem.setText("Mapped")
            statusItem.setForeground(QColor("#5bc0de"))

        self.updateSummary()

    def onJointCellDoubleClicked(self, row, col):
        if col == 3:
            suggestItem = self.jointTable.item(row, 3)
            if suggestItem and suggestItem.text().strip():
                combo = self.jointTable.cellWidget(row, 2)
                if combo:
                    combo.setCurrentText(suggestItem.text().strip())
        elif col in [1, 2]:
            combo = self.jointTable.cellWidget(row, 2)
            if combo:
                tj = combo.currentText().strip()
                target = (self.namespace + tj) if self.namespace and not tj.startswith(self.namespace) else tj
                if cmds.objExists(target):
                    cmds.select(target, r=True)
                elif cmds.objExists(tj):
                    cmds.select(tj, r=True)

    def applyJointFilter(self):
        onlyMissing = self.jointShowMissingCheck.isChecked()
        filterText = self.jointFilterEdit.text().strip().lower()

        for r in range(self.jointTable.rowCount()):
            stItem = self.jointTable.item(r, 0)
            fjItem = self.jointTable.item(r, 1)
            combo = self.jointTable.cellWidget(r, 2)
            if not stItem or not fjItem or not combo:
                continue

            status = stItem.text()
            fj = fjItem.text().lower()
            tj = combo.currentText().strip().lower()

            hide = False
            if onlyMissing and status == "Found":
                hide = True
            if filterText and (filterText not in fj and filterText not in tj):
                hide = True

            self.jointTable.setRowHidden(r, hide)

    def autoMatchAllJoints(self):
        self.sceneJoints = getSceneJointNames()
        sceneJointSet = set(self.sceneJoints)

        selectedRows = sorted(list(set([idx.row() for idx in self.jointTable.selectedIndexes()])))
        if selectedRows:
            targetRows = selectedRows
        else:
            targetRows = []
            for r in range(self.jointTable.rowCount()):
                fjItem = self.jointTable.item(r, 1)
                if not fjItem:
                    continue
                fj = fjItem.text()
                target = (self.namespace + fj) if self.namespace and not fj.startswith(self.namespace) else fj
                if target in sceneJointSet or fj in sceneJointSet or cmds.objExists(target):
                    continue
                targetRows.append(r)

        matchedCount = 0
        clearedCount = 0

        for r in targetRows:
            fjItem = self.jointTable.item(r, 1)
            combo = self.jointTable.cellWidget(r, 2)
            suggestItem = self.jointTable.item(r, 3)
            if not fjItem or not combo:
                continue

            fj = fjItem.text()
            suggested = autoMatchJoint(fj, self.sceneJoints)

            if suggestItem:
                suggestItem.setText(suggested if suggested else "")
                if suggested:
                    suggestItem.setToolTip("Double-click to apply '{}'".format(suggested))
                else:
                    suggestItem.setToolTip("")

            if suggested:
                combo.setCurrentText(suggested)
                matchedCount += 1
            else:
                combo.setCurrentText("")
                clearedCount += 1

        self.updateSummary()
        self.applyJointFilter()
        cmds.inViewMessage(amg="<b>bSkinSaver:</b> Auto-matched {} joint(s).".format(matchedCount), pos='topCenter', fade=True)

    def applyBatchRule(self):
        searchTxt = self.searchEdit.text()
        replaceTxt = self.replaceEdit.text()
        if not searchTxt:
            cmds.warning("Please enter a search string.")
            return

        appliedCount = 0

        for r in range(self.jointTable.rowCount()):
            fjItem = self.jointTable.item(r, 1)
            combo = self.jointTable.cellWidget(r, 2)
            stItem = self.jointTable.item(r, 0)
            if not fjItem or not combo or not stItem:
                continue

            if stItem.text() == "Found":
                continue

            fj = fjItem.text()
            if searchTxt in fj:
                candidate = fj.replace(searchTxt, replaceTxt)
                combo.setCurrentText(candidate)
                appliedCount += 1

        cmds.inViewMessage(amg="<b>bSkinSaver:</b> Applied rule to {} joint(s).".format(appliedCount), pos='topCenter', fade=True)

    def assignSelectedJointsFromMaya(self):
        selJoints = cmds.ls(sl=True, type='joint') or []
        if not selJoints:
            cmds.warning("Please select at least one joint in Maya.")
            return

        selShort = [j.split('|')[-1] for j in selJoints]
        selectedRows = sorted(list(set([idx.row() for idx in self.jointTable.selectedIndexes()])))
        if not selectedRows:
            curr = self.jointTable.currentRow()
            if curr >= 0:
                selectedRows = [curr]
        if not selectedRows:
            cmds.warning("Please select row(s) in the Joints table.")
            return

        if len(selShort) == 1:
            for row in selectedRows:
                combo = self.jointTable.cellWidget(row, 2)
                if combo:
                    combo.setCurrentText(selShort[0])
        else:
            for i, row in enumerate(selectedRows):
                if i < len(selShort):
                    combo = self.jointTable.cellWidget(row, 2)
                    if combo:
                        combo.setCurrentText(selShort[i])

    def selectTargetJointInMaya(self):
        selectedRows = sorted(list(set([idx.row() for idx in self.jointTable.selectedIndexes()])))
        targetsToSelect = []
        for r in selectedRows:
            combo = self.jointTable.cellWidget(r, 2)
            if combo:
                tj = combo.currentText().strip()
                if tj:
                    target = (self.namespace + tj) if self.namespace and not tj.startswith(self.namespace) else tj
                    if cmds.objExists(target):
                        targetsToSelect.append(target)
                    elif cmds.objExists(tj):
                        targetsToSelect.append(tj)

        if targetsToSelect:
            cmds.select(targetsToSelect, r=True)
        else:
            cmds.warning("No existing target joints to select in Maya.")

    def clearSelectedJointRows(self):
        selectedRows = sorted(list(set([idx.row() for idx in self.jointTable.selectedIndexes()])))
        for r in selectedRows:
            combo = self.jointTable.cellWidget(r, 2)
            if combo:
                combo.setCurrentText("")

    def getJointMappingDict(self):
        mapping = {}
        for r in range(self.jointTable.rowCount()):
            fjItem = self.jointTable.item(r, 1)
            combo = self.jointTable.cellWidget(r, 2)
            if fjItem and combo:
                fj = fjItem.text()
                tj = combo.currentText().strip()
                if tj:
                    mapping[fj] = tj
        return mapping

    # ------------------ Overall Summary & Action Buttons ------------------
    def updateSummary(self):
        geoTotal = self.geoTable.rowCount()
        geoMissing = sum(1 for r in range(geoTotal) if self.geoTable.item(r, 0) and self.geoTable.item(r, 0).text() == "Missing")

        jointTotal = self.jointTable.rowCount()
        jointMissing = sum(1 for r in range(jointTotal) if self.jointTable.item(r, 0) and self.jointTable.item(r, 0).text() == "Missing")

        self.summaryLabel.setText(
            "<b>Geometries:</b> {} total (<span style='color:{};'>{} missing</span>) &nbsp;|&nbsp; "
            "<b>Joints:</b> {} total (<span style='color:{};'>{} missing</span>)".format(
                geoTotal, "#d9534f" if geoMissing else "#5cb85c", geoMissing,
                jointTotal, "#d9534f" if jointMissing else "#5cb85c", jointMissing
            )
        )

    def closeEvent(self, event):
        global remapDialogWin
        remapDialogWin = None
        event.accept()

    def saveMappingToFile(self):
        geoMap = self.getGeoMappingDict()
        jointMap = self.getJointMappingDict()

        if not geoMap and not jointMap:
            cmds.warning("No mappings to save.")
            return

        res = QMessageBox.question(
            self,
            "Save Mapping to .sw File",
            "This will update geometry and joint names directly in the .sw file.\nA backup file (.sw.bak) will be created.\nDo you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if res != QMessageBox.Yes:
            return

        success = updateSwFileWithMapping(self.swFilePath, jointMapping=jointMap, geoMapping=geoMap, backup=True)
        if success:
            QMessageBox.information(
                self,
                "Success",
                "Successfully updated mapping in:\n{}\n\nBackup created at:\n{}.bak".format(self.swFilePath, self.swFilePath)
            )
            self.objects, self.objectJoints, self.uniqueJoints = parseSwFileJoints(self.swFilePath)
            self.populateGeoTable()
            self.populateJointTable()
            self.updateSummary()
            self.applyGeoFilter()
            self.applyJointFilter()

    def loadWeightsWithMapping(self):
        geoMap = self.getGeoMappingDict()
        jointMap = self.getJointMappingDict()
        sceneGeoSet = set(self.sceneGeos)
        sceneJointSet = set(self.sceneJoints)

        unmappedGeos = []
        for r in range(self.geoTable.rowCount()):
            fgItem = self.geoTable.item(r, 1)
            combo = self.geoTable.cellWidget(r, 2)
            if not fgItem or not combo:
                continue
            fg = fgItem.text()
            tg = combo.currentText().strip()
            target = (self.namespace + tg) if self.namespace and not tg.startswith(self.namespace) else tg
            inScene = (target in sceneGeoSet or tg in sceneGeoSet or (tg and cmds.objExists(target)))
            if not inScene:
                unmappedGeos.append(fg)

        unmappedJoints = []
        for r in range(self.jointTable.rowCount()):
            fjItem = self.jointTable.item(r, 1)
            combo = self.jointTable.cellWidget(r, 2)
            if not fjItem or not combo:
                continue
            fj = fjItem.text()
            tj = combo.currentText().strip()
            target = (self.namespace + tj) if self.namespace and not tj.startswith(self.namespace) else tj
            inScene = (target in sceneJointSet or tj in sceneJointSet or (tj and cmds.objExists(target)))
            if not inScene:
                unmappedJoints.append(fj)

        if unmappedGeos or unmappedJoints:
            warnLines = []
            if unmappedGeos:
                warnLines.append("Geometries ({} unmapped):\n - {}".format(len(unmappedGeos), "\n - ".join(unmappedGeos[:5])))
            if unmappedJoints:
                warnLines.append("Joints ({} unmapped):\n - {}".format(len(unmappedJoints), "\n - ".join(unmappedJoints[:5])))

            res = QMessageBox.warning(
                self,
                "Unmapped Influences / Geometries",
                "Some items are still missing or not properly mapped:\n\n{}\n\nDo you still want to proceed with loading?".format("\n\n".join(warnLines)),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if res != QMessageBox.Yes:
                return

        try:
            bLoadSkinValues(
                loadOnSelection=False,
                inputFile=self.swFilePath,
                namespace=self.namespace,
                geometry=False,
                jointMapping=jointMap,
                geoMapping=geoMap
            )
            cmds.inViewMessage(amg="<b>bSkinSaver:</b> Skin weights successfully loaded with mapping!", pos='topCenter', fade=True)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Skin", "An error occurred while loading skin weights:\n{}".format(e))



class bSkinSaverUI(QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(bSkinSaverUI, self).__init__(parent)

        tab_widget = QTabWidget()
        objectsTab = QWidget()
        verticesTab = QWidget()

        tab_widget.addTab(objectsTab, "Objects")
        tab_widget.addTab(verticesTab, "Vertices")
        self.descLabel = QLabel("(C) 2015 by Thomas Bittner\nUpdated by LEE SANGTAK", parent=self)
        self.setWindowTitle('bSkinSaver')

        self.geoCheckBox = QCheckBox("Geometry", parent=self)
        self.geoCheckBox.setToolTip("If checked, the geometry will be saved/loaded with the skinWeights.\nIf not checked, only the skinWeights will be saved/loaded.")
        self.objectsFileLine = QLineEdit('{}/fileName{}'.format(os.path.join(os.path.expanduser("~"), "Downloads"), EXT), parent=self)
        self.selectObjectsFileButton = QPushButton("Set File", parent=self)
        self.saveObjectsButton = QPushButton("Save Weights from selected Objects", parent=self)
        self.loadObjectsButton = QPushButton("Load", parent=self)

        objectsLayout = QVBoxLayout(objectsTab)
        objectsLayout.setAlignment(Qt.AlignTop)
        objectsLayout.setSpacing(3)

        objectsLayout.addWidget(self.geoCheckBox)

        objectsFileLayout = QBoxLayout(QBoxLayout.LeftToRight)
        objectsFileLayout.addWidget(self.objectsFileLine)
        objectsFileLayout.addWidget(self.selectObjectsFileButton)
        objectsLayout.addLayout(objectsFileLayout)

        objectsButtonLayout = QBoxLayout(QBoxLayout.TopToBottom)
        objectsButtonLayout.setSpacing(0)
        objectsButtonLayout.addWidget(self.saveObjectsButton)
        objectsButtonLayout.addWidget(self.loadObjectsButton)

        objectsLayout.addLayout(objectsButtonLayout)

        self.verticesFileLine = QLineEdit('/Users/thomas/defaultVertex.weights', parent=self)
        self.selectVerticesFileButton = QPushButton("Set File", parent=self)
        self.saveVerticesButton = QPushButton("Save Weights from selected Vertices", parent=self)
        self.loadVerticesButton = QPushButton("Load onto selected Object", parent=self)
        self.ignoreSoftSelectionWhenSaving = QCheckBox("ignore Soft Selection when Saving", parent=self)
        self.ignoreJointLocksWhenLoading = QCheckBox("ignore Joint Locks when Loading", parent=self)


        verticesLayout = QVBoxLayout(verticesTab)
        verticesLayout.setAlignment(Qt.AlignTop)
        verticesLayout.setSpacing(3)
        verticesFileLayout = QBoxLayout(QBoxLayout.LeftToRight)
        verticesFileLayout.addWidget(self.verticesFileLine)
        verticesFileLayout.addWidget(self.selectVerticesFileButton)
        verticesLayout.addLayout(verticesFileLayout)

        verticesButtonLayout = QBoxLayout(QBoxLayout.TopToBottom)
        verticesButtonLayout.setSpacing(0)
        verticesButtonLayout.addWidget(self.saveVerticesButton)
        verticesButtonLayout.addWidget(self.loadVerticesButton)
        verticesButtonLayout.addWidget(self.ignoreSoftSelectionWhenSaving)
        verticesButtonLayout.addWidget(self.ignoreJointLocksWhenLoading)
        verticesLayout.addLayout(verticesButtonLayout)


        self.layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        namespaceLayout = QHBoxLayout()
        self._namespaceLabel = QLabel('Namespace:')
        self._namespaceCBox = QComboBox()
        self._populateNamespaces()
        namespaceLayout.addWidget(self._namespaceLabel)
        namespaceLayout.addWidget(self._namespaceCBox)
        namespaceLayout.addStretch()
        self.layout.addLayout(namespaceLayout)

        self.layout.addWidget(tab_widget)
        self.layout.addWidget(self.descLabel)
        self.resize(400, 10)


        #select files
        self.connect(self.selectObjectsFileButton, SIGNAL("clicked()"), self.selectObjectsFile)
        self.connect(self.selectVerticesFileButton, SIGNAL("clicked()"), self.selectVerticesFile)

        self.connect(self.saveObjectsButton, SIGNAL("clicked()"), self.saveObjects)
        self.connect(self.loadObjectsButton, SIGNAL("clicked()"), self.loadObjects)

        self.connect(self.saveVerticesButton, SIGNAL("clicked()"), self.saveVertices)
        self.connect(self.loadVerticesButton, SIGNAL("clicked()"), self.loadVertices)

    def _populateNamespaces(self):
        self._namespaceCBox.addItem('')
        namespaces = set(cmds.namespaceInfo(listOnlyNamespaces=True, recurse=False)) - set(['UI', 'shared'])
        self._namespaceCBox.addItems([ns+':' for ns in namespaces])

    def selectObjectsFile(self):
        startDir = os.path.dirname(self.objectsFileLine.text())
        fileResult = cmds.fileDialog2(dir=startDir, fileMode=0, fileFilter="All Files (*{})".format(EXT))
        if fileResult != None:
            self.objectsFileLine.setText(fileResult[0])

    def selectVerticesFile(self):
        fileResult = cmds.fileDialog2()
        if fileResult != None:
            self.verticesFileLine.setText(fileResult[0])


    def loadObjects(self):
        filePath = str(self.objectsFileLine.text())
        if not os.path.isfile(filePath):
            cmds.warning("File does not exist: {}".format(filePath))
            return

        namespace = self._namespaceCBox.currentText()
        geoChecked = self.geoCheckBox.isChecked()

        if geoChecked:
            dirPath = os.path.dirname(filePath.replace('\\', '/'))
            abcFileName = os.path.basename(filePath).replace(EXT, '.abc')
            abcFilePath = "{}/{}".format(dirPath, abcFileName)
            if os.path.isfile(abcFilePath):
                mel.eval('AbcImport -mode import "{}";'.format(abcFilePath))
            else:
                cmds.warning("Alembic file not found: {}".format(abcFilePath))

        fileObjs, _, fileJoints = parseSwFileJoints(filePath)

        missingGeos = []
        if fileObjs:
            missingGeos, _ = checkMissingGeometries(fileObjs, namespace)

        missingJoints = []
        if fileJoints:
            missingJoints, _ = checkMissingJoints(fileJoints, namespace)

        if missingGeos or missingJoints:
            details = []
            if missingGeos:
                details.append("- Geometries: {} missing in scene".format(len(missingGeos)))
            if missingJoints:
                details.append("- Joints: {} missing in scene".format(len(missingJoints)))

            res = QMessageBox.question(
                self,
                "Missing Items Found",
                "Some items in the .sw file were not found in the scene:\n{}\n\nWould you like to open the Remapper?".format("\n".join(details)),
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            if res == QMessageBox.Yes:
                initialTab = 0 if missingGeos else 1
                self.openRemapUI(initialTab=initialTab)
            else:
                cmds.inViewMessage(amg="<b>bSkinSaver:</b> Load cancelled.", pos='topCenter', fade=True)
            return

        bLoadSkinValues(False, filePath, namespace, False)

    def loadObjectsSelection(self):
        # Kept for backward compatibility
        self.loadObjects()

    def openRemapUI(self, *args, **kwargs):
        filePath = str(self.objectsFileLine.text())
        if not os.path.isfile(filePath):
            cmds.warning("File does not exist: {}".format(filePath))
            return

        initialTab = kwargs.get('initialTab', 0)
        namespace = self._namespaceCBox.currentText()
        showSkinRemapDialog(
            swFilePath=filePath,
            namespace=namespace,
            geoCheck=self.geoCheckBox.isChecked(),
            parent=getMayaWindow(),
            initialTab=initialTab
        )

    def saveObjects(self):
        bSaveSkinValues(str(self.objectsFileLine.text()), self.geoCheckBox.isChecked())

    def loadVertices(self):
        bLoadVertexSkinValues(str(self.verticesFileLine.text()), self.ignoreJointLocksWhenLoading.isChecked())

    def saveVertices(self):
        bSaveVertexSkinValues(str(self.verticesFileLine.text()), self.ignoreSoftSelectionWhenSaving.isChecked())



bSkinPath = OpenMaya.MDagPath()
def bFindSkinCluster(objectName):
    skinClst = mel.eval('findRelatedSkinCluster("{}");'.format(objectName))
    if skinClst:
        sels = OpenMaya.MSelectionList()
        sels.add(skinClst)
        skinObj = OpenMaya.MObject()
        sels.getDependNode(0, skinObj)
        return skinObj
    return False



def bLoadVertexSkinValues(inputFile, ignoreJointLocks):
    timeBefore = time.time()

    line = ''
    fileJoints = []
    splittedStrings = []
    splittedWeights = []
    selectionList = OpenMaya.MSelectionList()
    vertexCount = 0

    OpenMaya.MGlobal.getActiveSelectionList( selectionList )
    node = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    selectionList.getDagPath( 0, node, component )

    if not node.hasFn(OpenMaya.MFn.kTransform):
        print('select a skinned object')

    NewTransform = OpenMaya.MFnTransform (node)
    if not NewTransform.childCount() or not NewTransform.child(0).hasFn(OpenMaya.MFn.kMesh):
        print('select a skinned object..')

    mesh = NewTransform.child(0)
    objectName = OpenMaya.MFnDagNode(mesh).name()
    skinCluster = bFindSkinCluster(objectName)
    if not skinCluster.hasFn(OpenMaya.MFn.kSkinClusterFilter):
        print('select a skinned object')

    fnSkinCluster = OpenMayaAnim.MFnSkinCluster(skinCluster)
    input = open(inputFile, 'r')

    fileJoints = []
    filePosition = 0

    # getting the weightLines
    #
    fileWeightFloats = []
    fnVtxComp = OpenMaya.MFnSingleIndexedComponent()
    vtxComponents = OpenMaya.MObject()
    vtxComponents = fnVtxComp.create( OpenMaya.MFn.kMeshVertComponent )

    bindVertCount = 0
    didCheckSoftSelection = False
    while True:
        line = input.readline().strip()
        if not line:
            break

        if filePosition == 0:
            vertexCount = int(line)
            if OpenMaya.MItGeometry(node).count() != vertexCount:
                print("vertex counts don't match!")
                return
            filePosition = 1

        elif filePosition == 1:
            if not line.startswith("========"):
                fileJoints.append(line)
            else:
                filePosition = 2

        elif filePosition == 2:
            splittedStrings = line.split(':')

            # do we have softselection?
            if not didCheckSoftSelection:
                if len(splittedStrings) == 3:
                    weightsIndex = 2
                    doSoftSelection = True
                    softWeights = [1.0] * bindVertCount
                else:
                    weightsIndex = 1
                    doSoftSelection=False
                didCheckSoftSelection = True

            # vertId
            vertId = int(splittedStrings[0])
            fnVtxComp.addElement(vertId)

            #softselection
            if doSoftSelection:
                softWeights.append(float(splittedStrings[1]))

            # weights
            splittedWeights = splittedStrings[weightsIndex].split(' ')
            fileWeightFloats.append([float(splittedWeight) for splittedWeight in splittedWeights])

            bindVertCount += 1


    # getting mayaJoints
    #
    influenceArray = OpenMaya.MDagPathArray()
    mayaJoints = []

    infCount = fnSkinCluster.influenceObjects(influenceArray)
    for i in range(infCount):
        mayaJoints.append(OpenMaya.MFnDagNode(influenceArray[i]).name().split('|')[-1])


    # getting old weights
    #
    oldWeightDoubles = OpenMaya.MDoubleArray()
    scriptUtil = OpenMaya.MScriptUtil()
    infCountPtr = scriptUtil.asUintPtr()
    fnSkinCluster.getWeights(bSkinPath, vtxComponents, oldWeightDoubles, infCountPtr)


    # making allJoints
    #
    allJoints = list(fileJoints)
    for mayaJoint in mayaJoints:
        if mayaJoint not in fileJoints:
            allJoints.append(mayaJoint)



    # mapping joints and making sure we have all joints in the skinCluster
    #
    allInfluencesInScene = True
    missingInfluencesList = []
    for i in range(len(fileJoints)):
        influenceInScene = False
        for k in range(len(mayaJoints)):
            if mayaJoints[k] == fileJoints[i]:
                influenceInScene = True

        if not influenceInScene:
            allInfluencesInScene = False
            missingInfluencesList.append(fileJoints[i])

    if not allInfluencesInScene:
        print('There are influences missing:', missingInfluencesList)
        return



    # getting allExistInMaya
    #
    allExistInMaya = [-1] * len(allJoints)
    for i in range(len(allJoints)):
        for k in range(len(mayaJoints)):
            if allJoints[i] == mayaJoints[k]:
                allExistInMaya[i] = k
                break


    # getting joint locks
    #
    allLocks = [False] * len(allJoints)
    if not ignoreJointLocks:
        for i in range(len(allJoints)):
            allLocks[i] = cmds.getAttr('%s.liw' % allJoints[i])



    weightDoubles = OpenMaya.MDoubleArray(0)

    # copy weights from fileWeightFloats and oldWeightDoubles into weightDoubles (include joint locks) and softWeights lists
    #
    print('bindVertCount: ', bindVertCount)
    for i in range(bindVertCount):
        for k in range(len(allJoints)):

            # fileJoints:
            #
            if k < len(fileJoints):
                if not allLocks[k]:
                    weightDoubles.append(fileWeightFloats[i][k])        #weightDoubles[k + len(allJoints) * i] = fileWeightFloats[i][k]
                else:
                    if allExistInMaya[k]:
                        weightDoubles.append(oldWeightDoubles[allExistInMaya[k] + len(mayaJoints) * i])
                    else:
                        weightDoubles.append(0)

            # mayaJoints
            #
            else:
                if not allLocks[k]:
                    weightDoubles.append(0)
                else:
                    if allExistInMaya[k]:
                        weightDoubles.append(oldWeightDoubles[allExistInMaya[k] + len(mayaJoints) * i])
                    else:
                        weightDoubles.append(0)


    # normalize
    #
    for i in range(bindVertCount):
        sumA = 0
        sumB = 0
        for inf in range(len(allJoints)):
            if not allLocks[inf]:
                sumA += weightDoubles[inf + i*len(allJoints)]
            else:
                sumB += weightDoubles[inf + i*len(allJoints)]

        if sumA > 0.0001:
            sumADenom = 1 / sumA
            for inf in range(len(allJoints)):
                if not allLocks[inf]:
                    weightDoubles[inf + i*len(allJoints)] *= sumADenom * (1-sumB)


    # soft selection
    #
    if doSoftSelection:
        for i in range(bindVertCount):
            for inf in range(len(allExistInMaya)):
                index = inf + i*len(allExistInMaya)
                oldWeights = oldWeightDoubles[allExistInMaya[inf] + len(mayaJoints) * i]

                weightDoubles[index] = weightDoubles[index] * softWeights[i] + oldWeights * (1.0-softWeights[i])



    #SET WEIGHTS
    #
    allJointsIndices = OpenMaya.MIntArray(len(allExistInMaya))
    for i in range(len(allExistInMaya)):
        allJointsIndices[i] = allExistInMaya[i]


    print('setting weights...')
    fnSkinCluster.setWeights(bSkinPath, vtxComponents, allJointsIndices, weightDoubles, 0)

    # select the vertices
    #
    pointSelectionList = OpenMaya.MSelectionList()
    pointSelectionList.add(OpenMaya.MDagPath(node),vtxComponents)
    OpenMaya.MGlobal.setActiveSelectionList(pointSelectionList)


    print('done, it took', (time.time()-timeBefore), ' seconds')



def vertexToId(vertex):
    return int(vertex.split('[')[1].split(']')[0])

def vertexToIdList(verts):
    vertIds = [0] * len(verts)
    for i, vert in enumerate(verts):
        vertIds[i] = vertexToId(vert)
    return vertIds


def bSaveVertexSkinValues(inputFile, ignoreSoftSelection):

    timeBefore = time.time()

    print('saving Vertex skinWeights.. ')


    if not ignoreSoftSelection:
        verts, softWeights = getSoftSelection()
    else:
        verts = cmds.ls(selection=True, flatten=True)

    vertIds = vertexToIdList(verts)
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selection )

    iterate = OpenMaya.MItSelectionList(selection)
    dagPath = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    iterate.getDagPath(dagPath, component)

    skinCluster = bFindSkinCluster(OpenMaya.MFnDagNode(dagPath).partialPathName())
    fnSkinCluster = OpenMayaAnim.MFnSkinCluster(skinCluster)


    if not skinCluster.hasFn(OpenMaya.MFn.kSkinClusterFilter):
        print('no skinCluster found on selected vertices')
        return

    output = open(inputFile, 'w')
    output.write(str(OpenMaya.MItGeometry(dagPath).count()) + '\n')

    fnVtxComp = OpenMaya.MFnSingleIndexedComponent()
    vtxComponents = OpenMaya.MObject()
    vtxComponents = fnVtxComp.create( OpenMaya.MFn.kMeshVertComponent )

    WeightArray = OpenMaya.MFloatArray()
    meshIter = OpenMaya.MItMeshVertex ( dagPath, component)
    for vertId in vertIds:
        fnVtxComp.addElement( vertId)

    vertexCount = meshIter.count()
    scriptUtil = OpenMaya.MScriptUtil()
    infCountPtr = scriptUtil.asUintPtr()
    fnSkinCluster.getWeights(dagPath, vtxComponents, WeightArray, infCountPtr)
    infCount = OpenMaya.MScriptUtil.getUint(infCountPtr)

    weightCheckArray = []
    for i in range(infCount):
        weightCheckArray.append(False)

    for i in range(vertexCount):
        for k in range(infCount):
            if not weightCheckArray[k] and WeightArray[((i * infCount) + k)]:
                weightCheckArray[k] = True

    #joints..
    influentsArray = OpenMaya.MDagPathArray()
    fnSkinCluster.influenceObjects(influentsArray)
    for i in range(infCount):
        if (weightCheckArray[i]):
            output.write(OpenMaya.MFnDagNode(influentsArray[i]).name() + '\n')

    output.write('============\n')

    for i in range(len(vertIds)):
        vertId = vertIds[i]
        softWeight = ''
        if not ignoreSoftSelection:
            softWeight = '%f:' % softWeights[i]

        weightsString = ' '.join(['0' if x == 0 else str(x) for n,x in enumerate(WeightArray[i*infCount : (i+1)*infCount]) if weightCheckArray[n]])
        weightArrayString = "%d:%s%s" % (vertId, softWeight, weightsString)

        output.write(weightArrayString + '\n')
        meshIter.next()

    output.close()

    print('done, it took', (time.time()-timeBefore), ' seconds')



def bSaveSkinValues(inputFile, geometry=False):
    selGeos = getSelectedGeometries()
    if not selGeos:
        cmds.warning('no geometries selected')
        return

    timeBefore = time.time()

    if geometry:
        nicePath = inputFile.replace('\\', '/')
        dirPath = os.path.dirname(nicePath)
        abcFileName = os.path.basename(nicePath).replace(EXT, '.abc')
        rootFlags = ''
        for selGeo in selGeos:
            rootFlags += ' -root {0}'.format(selGeo)
        mel.eval('AbcExport -j "-frameRange 0 0 -stripNamespaces -uvWrite -worldSpace -writeUVSets -dataFormat ogawa {0} -file {1}/{2}";'.format(rootFlags, dirPath, abcFileName))

    output = open(inputFile, 'w')

    cmds.select(selGeos, r=True)
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)
    iterate = OpenMaya.MItSelectionList(selection)
    while not iterate.isDone():
        node = OpenMaya.MDagPath()
        component = OpenMaya.MObject()
        iterate.getDagPath (node, component)
        objectName = OpenMaya.MFnDagNode(node).name()

        newTransform = OpenMaya.MFnTransform(node)
        for childIndex in range(newTransform.childCount()):
            childObject = newTransform.child(childIndex)
            if childObject.hasFn(OpenMaya.MFn.kMesh) or childObject.hasFn(OpenMaya.MFn.kNurbsSurface) or childObject.hasFn(OpenMaya.MFn.kCurve):
                skinCluster = bFindSkinCluster(OpenMaya.MFnDagNode(childObject).partialPathName())
                if skinCluster is not False:
                    bSkinPath = OpenMaya.MDagPath()
                    fnSkinCluster = OpenMayaAnim.MFnSkinCluster(skinCluster)
                    fnSkinCluster.getPathAtIndex(0,bSkinPath)
                    influenceArray = OpenMaya.MDagPathArray()
                    fnSkinCluster.influenceObjects(influenceArray)
                    influentsCount = influenceArray.length()
                    output.write(objectName + '\n')

                    for k in range(influentsCount):
                        jointTokens = str(influenceArray[k].fullPathName()).split('|')
                        jointTokens = jointTokens[len(jointTokens)-1].split(':')
                        output.write(jointTokens[len(jointTokens)-1] + '\n')

                    output.write('============\n')


                    fnVtxComp = OpenMaya.MFnSingleIndexedComponent()
                    vtxComponents = OpenMaya.MObject()
                    vtxComponents = fnVtxComp.create( OpenMaya.MFn.kMeshVertComponent )

                    vertexCount = OpenMaya.MFnMesh(bSkinPath).numVertices()
                    for i in range(vertexCount):
                        fnVtxComp.addElement( i )

                    WeightArray = OpenMaya.MFloatArray()
                    scriptUtil = OpenMaya.MScriptUtil()
                    infCountPtr = scriptUtil.asUintPtr()
                    fnSkinCluster.getWeights(bSkinPath, vtxComponents, WeightArray, infCountPtr)
                    infCount = OpenMaya.MScriptUtil.getUint(infCountPtr)

                    for i in range(vertexCount):
                        saveString = ' '.join(['0' if x == 0 else str(x) for n,x in enumerate(WeightArray[i*infCount : (i+1)*infCount])])
                        output.write(saveString + '\n')

                    output.write('\n')

        iterate.next()

    output.close()
    print('done saving weights, it took ', (time.time()-timeBefore), ' seconds.')





def bSkinObject(objectName, fileJoints, weights):
    if not cmds.objExists(objectName):
        print(objectName, " doesn't exist - skipping. ")
        return

    # quick check if all the joints are in scene
    #
    allInfluencesInScene = True
    sceneJointTokens = []

    for jointIndex in range(len(fileJoints)):
        jointHere = False
        it = OpenMaya.MItDependencyNodes ( OpenMaya.MFn.kJoint)
        while not it.isDone():
            sceneJointTokens = str(OpenMaya.MFnDagNode(it.item()).fullPathName()).split('|')
            if str(fileJoints[jointIndex]) == str(sceneJointTokens[len(sceneJointTokens) - 1]):
                jointHere = True

            it.next()

        if not jointHere:
            allInfluencesInScene = False
            print('missing influence: ', fileJoints[jointIndex])

    if not allInfluencesInScene:
        print(objectName, " can't be skinned because of missing influences.")
        return

    # create some arrays
    #
    allJointsHere = False
    fileJointsMapArray = list(range(len(fileJoints)))
    objectEmptyJoints = []

    # Show shape visibility and store visibility state
    shape = objectName if cmds.nodeType(objectName) == 'mesh' else cmds.listRelatives(objectName, s=True, ni=True)[0]
    shapeVisState = cmds.getAttr('{}.visibility'.format(shape))
    cmds.setAttr('{}.visibility'.format(shape), True)

    # let's check if there's already a skinCluster, let's try to use that - if it contains all the needed joints
    #
    skinCluster = bFindSkinCluster(objectName)
    if type(skinCluster) != type(True):
        fnSkinCluster = OpenMayaAnim.MFnSkinCluster(skinCluster)
        influentsArray = OpenMaya.MDagPathArray()
        infCount = fnSkinCluster.influenceObjects(influentsArray)

        influenceStringArray = []
        for i in range(infCount):
            influenceStringArray.append(OpenMaya.MFnDagNode(influentsArray[i]).name())

        allJointsHere = True
        for joint in fileJoints:
            if joint not in influenceStringArray:
                print('missing a joint (', joint, ', ..)')
                allJointsHere = False
                break

        if not allJointsHere:
            mel.eval("DetachSkin " + objectName)
        else:
            objectFoundJointsInFile = [False] * len(influenceStringArray)

            for i in range(len(fileJoints)):
                for k in range(len(influenceStringArray)):
                    if fileJoints[i] == influenceStringArray[k]:
                        fileJointsMapArray[i] = k
                        objectFoundJointsInFile[k] = True

            for i in range(len(influenceStringArray)):
                if not objectFoundJointsInFile[i]:
                    objectEmptyJoints.append(i)

    if not allJointsHere:
        cmd = "select "
        for i in range(len(fileJoints)):
            cmd += " " + fileJoints[i]

        cmd += " " + objectName
        print(cmd)
        mel.eval(cmd)

        mel.eval("skinCluster -tsb -mi 10")
        mel.eval("select `listRelatives -p " + objectName + "`")
        mel.eval("refresh")

        skinCluster = bFindSkinCluster(objectName)

    fnSkinCluster = OpenMayaAnim.MFnSkinCluster(skinCluster)
    influentsArray = OpenMaya.MDagPathArray()
    fnSkinCluster.influenceObjects(influentsArray)

    bSkinPath = OpenMaya.MDagPath()
    fnSkinCluster.getPathAtIndex(fnSkinCluster.indexForOutputConnection(0),bSkinPath)

    weightStrings = []
    vertexIter = OpenMaya.MItGeometry (bSkinPath)

    weightDoubles = OpenMaya.MDoubleArray()

    singleIndexed = True
    vtxComponents = OpenMaya.MObject()
    fnVtxComp = OpenMaya.MFnSingleIndexedComponent()
    fnVtxCompDouble = OpenMaya.MFnDoubleIndexedComponent()


    if bSkinPath.node().apiType() == OpenMaya.MFn.kMesh:
        vtxComponents = fnVtxComp.create( OpenMaya.MFn.kMeshVertComponent )
    elif bSkinPath.node().apiType() == OpenMaya.MFn.kNurbsSurface:
        singleIndexed = False
        vtxComponents = fnVtxCompDouble.create( OpenMaya.MFn.kSurfaceCVComponent )
    elif bSkinPath.node().apiType() == OpenMaya.MFn.kNurbsCurve:
        vtxComponents = fnVtxComp.create( OpenMaya.MFn.kCurveCVComponent )

    # nurbs curves..
    #
    counterValue = 0
    if not singleIndexed:
        currentU = 0
        currentV = 0

        cvsU = OpenMaya.MFnNurbsSurface(bSkinPath.node()).numCVsInU()
        cvsV = OpenMaya.MFnNurbsSurface(bSkinPath.node()).numCVsInV()
        formU = OpenMaya.MFnNurbsSurface(bSkinPath.node()).formInU()
        formV = OpenMaya.MFnNurbsSurface(bSkinPath.node()).formInV()

        if formU == 3:
            cvsU -= 3
        if formV == 3:
            cvsV -= 3

    # go through all vertices and append to the weightDoubles array
    #
    vertexIter = OpenMaya.MItGeometry (bSkinPath)
    while not vertexIter.isDone():
        weightStrings = []
        if singleIndexed:
            fnVtxComp.addElement(counterValue)
        else:
            fnVtxCompDouble.addElement(currentU, currentV)
            currentV += 1
            if currentV >= cvsV:
                currentV = 0
                currentU += 1

        weightStrings = weights[counterValue].split(' ')
        for i in range(len(weightStrings)):
            weightDoubles.append(float(weightStrings[i]))
        for i in range(len(objectEmptyJoints)):
            weightDoubles.append(0)

        counterValue += 1
        vertexIter.next()

    # createing the influence Array
    #
    mayafileJointsMapArray = OpenMaya.MIntArray()
    for i in range(len(fileJointsMapArray)):
        mayafileJointsMapArray.append(fileJointsMapArray[i])
    for i in range(len(objectEmptyJoints)):
        mayafileJointsMapArray.append(objectEmptyJoints[i])

    # set the weights
    #
    fnSkinCluster.setWeights(bSkinPath, vtxComponents, mayafileJointsMapArray, weightDoubles, 0)

    # Restore shape visibility
    cmds.setAttr('{}.visibility'.format(shape), shapeVisState)


def bLoadSkinValues(loadOnSelection, inputFile, namespace='', geometry=False, jointMapping=None, geoMapping=None):

    timeBefore = time.time()

    joints = []
    weights = []
    PolygonObject = ""

    if geometry:
        dirPath = os.path.dirname(inputFile.replace('\\', '/'))
        abcFileName = os.path.basename(inputFile).replace(EXT, '.abc')
        abcFilePath = "{}/{}".format(dirPath, abcFileName)
        if os.path.isfile(abcFilePath):
            mel.eval('AbcImport -mode import "{}";'.format(abcFilePath))

    if loadOnSelection == True:
        sels = cmds.ls(sl=True)
        if sels:
            meshes = cmds.listRelatives(sels[0], ni=True, shapes=True, type='mesh')
            if meshes:
                PolygonObject = meshes[0]

    if loadOnSelection and len(PolygonObject) == 0:
        print("You need to select a polygon object")
        return

    input = open(inputFile, 'r')

    FilePosition = 0
    while True:
        line = input.readline()
        if not line:
            break

        line = line.strip()

        if FilePosition != 0:
            if not line.startswith("============"):
                if FilePosition == 1:
                    rawJoint = line
                    if jointMapping and rawJoint in jointMapping and jointMapping[rawJoint]:
                        mappedJoint = jointMapping[rawJoint]
                    else:
                        mappedJoint = rawJoint

                    if namespace and not mappedJoint.startswith(namespace):
                        finalJoint = namespace + mappedJoint
                    else:
                        finalJoint = mappedJoint

                    joints.append(finalJoint)
                elif FilePosition == 2:
                    if len(line) > 0:
                        weights.append(line)
                    else:
                        bSkinObject(PolygonObject, joints, weights)
                        PolygonObject = ""
                        joints = []
                        weights = []
                        FilePosition = 0
                        if loadOnSelection == True:
                            break

            else: # it's ========
                FilePosition = 2

        else: #FilePosition is 0
            if not loadOnSelection:
                rawGeo = line
                if geoMapping and rawGeo in geoMapping and geoMapping[rawGeo]:
                    mappedGeo = geoMapping[rawGeo]
                else:
                    mappedGeo = rawGeo

                if namespace and not mappedGeo.startswith(namespace):
                    PolygonObject = namespace + mappedGeo
                else:
                    PolygonObject = mappedGeo

            FilePosition = 1

            if cmds.objExists(PolygonObject):
                mel.eval("select " + PolygonObject)
                mel.eval("refresh")

    print('done loading weights, it took ', (time.time()-timeBefore), ' seconds.')



def getSoftSelection():
    #Grab the soft selection

    selection = OpenMaya.MSelectionList()
    softSelection = OpenMaya.MRichSelection()
    OpenMaya.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)

    dagPath = OpenMaya.MDagPath()
    component = OpenMaya.MObject()

    iter = OpenMaya.MItSelectionList( selection,OpenMaya.MFn.kMeshVertComponent )
    elements, weights = [], []
    while not iter.isDone():
        iter.getDagPath( dagPath, component )
        dagPath.pop() #Grab the parent of the shape node
        node = dagPath.fullPathName()
        fnComp = OpenMaya.MFnSingleIndexedComponent(component)
        getWeight = lambda i: fnComp.weight(i).influence() if fnComp.hasWeights() else 1.0

        for i in range(fnComp.elementCount()):
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
            weights.append(getWeight(i))
        iter.next()

    return elements, weights
