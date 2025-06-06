"""
=====================================================================
    Tool for saving and loading skinWeights in Maya

    (c) 2013 - 2016 by Thomas Bittner
    thomasbittner@hotmail.de

    source the file and then run: showUI()


=====================================================================

"""



import os
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


def showUI():
    global mainWin
    mainWin = bSkinSaverUI()
    mainWin.show()

    dirName = os.path.dirname(mainWin.objectsFileLine.text())
    fileName = 'fileName.sw'
    sels = cmds.ls(sl=True)
    if sels:
        fileName = sels[0] + '.sw'
    mainWin.objectsFileLine.setText(os.path.join(dirName, fileName))


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(int(ptr), QWidget)


class bSkinSaverUI(QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(bSkinSaverUI, self).__init__(parent)

        tab_widget = QTabWidget()
        objectsTab = QWidget()
        verticesTab = QWidget()

        tab_widget.addTab(objectsTab, "Objects")
        tab_widget.addTab(verticesTab, "Vertices")
        self.descLabel = QLabel("(C) 2015 by Thomas Bittner", parent=self)
        self.setWindowTitle('bSkinSaver 1.1')

        self.geoCheckBox = QCheckBox("Geometry", parent=self)
        self.geoCheckBox.setToolTip("If checked, the geometry will be saved/loaded with the skinWeights.\nIf not checked, only the skinWeights will be saved/loaded.")
        self.objectsFileLine = QLineEdit('{0}/fileName.sw'.format(os.path.join(os.path.expanduser("~"), "Downloads")), parent=self)
        self.selectObjectsFileButton = QPushButton("Set File", parent=self)
        self.saveObjectsButton = QPushButton("Save Weights from selected Objects", parent=self)
        self.loadObjectsButton = QPushButton("Load", parent=self)
        self.loadObjectsSelectionButton = QPushButton("Load to Selected Object", parent=self)

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
        objectsButtonLayout.addWidget(self.loadObjectsSelectionButton)

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
        self.connect(self.loadObjectsSelectionButton, SIGNAL("clicked()"), self.loadObjectsSelection)

        self.connect(self.saveVerticesButton, SIGNAL("clicked()"), self.saveVertices)
        self.connect(self.loadVerticesButton, SIGNAL("clicked()"), self.loadVertices)

    def _populateNamespaces(self):
        self._namespaceCBox.addItem('')
        namespaces = set(cmds.namespaceInfo(listOnlyNamespaces=True, recurse=False)) - set(['UI', 'shared'])
        self._namespaceCBox.addItems([ns+':' for ns in namespaces])

    def selectObjectsFile(self):
        startDir = os.path.dirname(self.objectsFileLine.text())
        fileResult = cmds.fileDialog2(dir=startDir, fileMode=0, fileFilter="All Files (*.sw)")
        if fileResult != None:
            self.objectsFileLine.setText(fileResult[0])

    def selectVerticesFile(self):
        fileResult = cmds.fileDialog2()
        if fileResult != None:
            self.verticesFileLine.setText(fileResult[0])


    def loadObjects(self):
        namespace = self._namespaceCBox.currentText()
        bLoadSkinValues (False, str(self.objectsFileLine.text()), namespace, self.geoCheckBox.isChecked())

    def loadObjectsSelection(self):
        namespace = self._namespaceCBox.currentText()
        bLoadSkinValues (True, str(self.objectsFileLine.text()), namespace)

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

    # it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kSkinClusterFilter)
    # while not it.isDone():
    #     fnSkinCluster = OpenMayaAnim.MFnSkinCluster(it.item())
    #     fnSkinCluster.getPathAtIndex(0,bSkinPath)

    #     if OpenMaya.MFnDagNode(bSkinPath.node()).partialPathName() == objectName or OpenMaya.MFnDagNode(OpenMaya.MFnDagNode(bSkinPath.node()).parent(0)).partialPathName() == objectName:
    #         return it.item()
    #     it.next()
    # return False

    # skinClst = False

    # sels = OpenMaya.MSelectionList()
    # sels.add(objectName)
    # shape = OpenMaya.MDagPath()
    # sels.getDagPath(0, shape)

    # dgIt = OpenMaya.MItDependencyGraph(shape.node(), OpenMaya.MFn.kSkinClusterFilter, OpenMaya.MItDependencyGraph.kUpstream)
    # while not dgIt.isDone():
    #     skinClst = dgIt.currentItem()
    #     dgIt.next()

    # return skinClst



def bLoadVertexSkinValues(inputFile, ignoreJointLocks):
    timeBefore = time.time()

    line = ''
    fileJoints = []
    weights = []
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
    weightLines = []
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

    #print('fileWeightFloats: ', fileWeightFloats)


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

    #print('allExistInMaya: ', allExistInMaya)

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

    #print('mayaJoints: ', mayaJoints)
    #print('allJointsIndices: ', allJointsIndices)
    #print('allJoints: ', allJoints)
    #print('weightDoubles before: ', weightDoubles)

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
    #while not meshIter.isDone():
    for vertId in vertIds:
        fnVtxComp.addElement( vertId)
        #meshIter.next()

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

    counter = 0
    weightArrayString = []
    for i in range(len(vertIds)):
        vertId = vertIds[i]
        softWeight = ''
        if not ignoreSoftSelection:
            softWeight = '%f:' % softWeights[i]

        #weightArrayString = '%d:%s' % (vertId, softWeight)

        """
        for k in range(infCount):
            if weightCheckArray[k] == True:
                weightArrayString += str(WeightArray[(counter * infCount) + k]) + ' '
        """
        weightsString = ' '.join(['0' if x == 0 else str(x) for n,x in enumerate(WeightArray[i*infCount : (i+1)*infCount]) if weightCheckArray[n]])
        weightArrayString = "%d:%s%s" % (vertId, softWeight, weightsString)

        output.write(weightArrayString + '\n')
        counter += 1
        meshIter.next()

    output.close()

    print('done, it took', (time.time()-timeBefore), ' seconds')



def bSaveSkinValues(inputFile, geometry=False):

    timeBefore = time.time()

    output = open(inputFile, 'w')

    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)

    iterate = OpenMaya.MItSelectionList(selection)

    while not iterate.isDone():
        node = OpenMaya.MDagPath()
        component = OpenMaya.MObject()
        iterate.getDagPath (node, component)
        if not node.hasFn(OpenMaya.MFn.kTransform):
            print(OpenMaya.MFnDagNode(node).name() + ' is not a Transform node (need to select transform node of polyMesh)')
        else:
            objectName = OpenMaya.MFnDagNode(node).name()

            if geometry:
                mel.eval('AbcExport -j "-frameRange 0 0 -stripNamespaces -uvWrite -worldSpace -writeUVSets -dataFormat ogawa -root {0} -file {1}/{0}.abc";'.format(objectName, os.path.dirname(inputFile.replace('\\', '/'))))

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
                            #saveString = ' '.join(map(str,WeightArray[i*infCount : (i+1)*infCount]))
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

    it = OpenMaya.MItDependencyNodes ( OpenMaya.MFn.kJoint)

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
    totalJointsCount = len(fileJoints)
    fileJointsMapArray = list(range(len(fileJoints)))
    objectEmptyJoints = []

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
            totalJointsCount = len(fileJointsMapArray) + len(objectEmptyJoints)

            #print('jointMapArray: ', fileJointsMapArray)

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
        #mel.eval("undoInfo -st 1")

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
    #mel.eval("skinPercent -normalize true " + fnSkinCluster.name() + " " + objectName)




def bLoadSkinValues(loadOnSelection, inputFile, namespace='', geometry=False):

    timeBefore = time.time()

    joints = []
    weights = []
    PolygonObject = ""

    if geometry:
        geo = os.path.basename(inputFile).replace('.sw', '')
        mel.eval('AbcImport -mode import "{}/{}";'.format(os.path.dirname(inputFile.replace('\\', '/')), geo+'.abc'))

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
                    joints.append(namespace+line)
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
                PolygonObject = line
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
