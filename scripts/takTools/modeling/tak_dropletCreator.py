'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
'''

import pymel.core as pm


class DropletCreator(object):
    # Attributes
    locator = None
    goalMesh = None
    controlGrp = None
    leadParticleSolver = None
    meshParticleSolver = None
    leadParticle = None
    meshParticle = None
    meshParticleEmitter = None

    def __init__(self, locator, goalMesh):
        self.locator = pm.PyNode(locator)
        pm.addAttr(self.locator, ln='leadParticle', dt='string')
        self.goalMesh = pm.PyNode(goalMesh)
        self.main()

    def main(self):
        self.createControlGrp()
        self.createSolvers()
        self.createLeadParticle()
        assignSolver(self.leadParticleSolver, self.leadParticle)
        self.createMeshParticle()
        assignSolver(self.meshParticleSolver, self.meshParticle)
        self.createExpresssions()
        self.connectControl()
        self.cleanupOutliner()

    def createControlGrp(self):
        self.controlGrp = pm.createNode('transform', n=self.locator.name()+'_droplet_grp')
        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        for attr in attrs:
            self.controlGrp.attr(attr).lock(True)
            self.controlGrp.attr(attr).setKeyable(False)
        pm.addAttr(self.controlGrp, ln='startFrame', at='float', keyable=True, dv=pm.playbackOptions(q=True, minTime=True))
        pm.addAttr(self.controlGrp, ln='uDirection', at='float', keyable=True, dv=0.0, min=-1.0, max=1.0)
        pm.addAttr(self.controlGrp, ln='vDirection', at='float', keyable=True, dv=1.0, min=-1.0, max=1.0)
        pm.addAttr(self.controlGrp, ln='speed', at='float', keyable=True, dv=0.001, min=0.001, max=0.01)
        pm.addAttr(self.controlGrp, ln='radius', at='float', keyable=True, dv=0.2, min=0.0)
        pm.addAttr(self.controlGrp, ln='blobbyRadius', at='float', keyable=True, dv=1.5, min=0.0)
        pm.addAttr(self.controlGrp, ln='tailLength', at='float', keyable=True, dv=1.0, min=0.0)

    def createSolvers(self):
        self.leadParticleSolver = pm.createNode('nucleus', n=self.locator+'_leadParticle_nucleus')
        self.meshParticleSolver = pm.createNode('nucleus', n=self.locator+'_meshParticle_nucleus')
        pm.PyNode('time1').outTime >> self.leadParticleSolver.currentTime
        pm.PyNode('time1').outTime >> self.meshParticleSolver.currentTime

    def createLeadParticle(self):
        self.leadParticle = pm.nParticle(p=self.locator.getTranslation())[0]
        pm.goal(self.leadParticle, w=1, utr=False, g=self.goalMesh)
        pm.addAttr(self.leadParticle.getShape(), ln='goalU', dt='doubleArray')
        pm.addAttr(self.leadParticle.getShape(), ln='goalV', dt='doubleArray')
        self.leadParticle.getShape().message >> self.locator.leadParticle

    def createMeshParticle(self):
        pm.select(self.leadParticle, r=True)
        pm.emitter(type='omni', r=100, sro=0, nuv=0, cye='none', cyi=1, spd=0, srn=0, nsp=1, tsp=0, mxd=0, mnd=0, dx=1, dy=0, dz=0, sp=0)[1]

        self.meshParticleEmitter = pm.ls(sl=True)
        self.meshParticle = pm.nParticle()[0]
        self.meshParticle.getShape().collide.set(False)
        self.meshParticle.getShape().radiusScale[1].radiusScale_Position.set(1)
        self.meshParticle.getShape().radiusScale[1].radiusScale_FloatValue.set(0)
        self.meshParticle.getShape().blobbyRadiusScale.set(1.5)
        self.meshParticle.getShape().meshTriangleSize.set(0.1)
        self.meshParticle.getShape().meshSmoothingIterations.set(10)
        self.leadParticleSolver.startFrame >> self.meshParticle.getShape().startFrame

        pm.select(self.meshParticleEmitter, r=True)
        pm.connectDynamic(self.meshParticle, em=self.meshParticleEmitter)

        pm.goal(self.meshParticle, w=1, utr=False, g=self.goalMesh)
        pm.addAttr(self.meshParticle.getShape(), ln='goalU', dt='doubleArray')
        pm.addAttr(self.meshParticle.getShape(), ln='goalV', dt='doubleArray')

        pm.select(self.meshParticle, r=True)
        pm.mel.eval('particleToPoly;')

    def createExpresssions(self):
        closestPointOnMesh = pm.createNode('closestPointOnMesh', n=self.locator+'_closestPoint')
        self.goalMesh.getShape().worldMesh >> closestPointOnMesh.inMesh
        self.locator.translate >> closestPointOnMesh.inPosition

        leadParticleCreationExpr = '''
        {leadParticle}.goalU = {closestPointGoalU};
        {leadParticle}.goalV = {closestPointGoalV};
        '''.format(leadParticle=self.leadParticle.getShape(),
                   closestPointGoalU=closestPointOnMesh.parameterU.get(),
                   closestPointGoalV=closestPointOnMesh.parameterV.get())
        pm.dynExpression(self.leadParticle.getShape(), string=leadParticleCreationExpr, c=True)

        leadParticleRuntimeExpr = '''
        float $uDir = {control}.uDirection;
        float $vDir = {control}.vDirection;
        float $speed = {control}.speed;
        {leadParticle}.goalU -= $uDir * $speed;
        {leadParticle}.goalV -= $vDir * $speed;
        '''.format(control=self.controlGrp, leadParticle=self.leadParticle.getShape())
        pm.dynExpression(self.leadParticle.getShape(), string=leadParticleRuntimeExpr, rbd=True)

        meshParticleCreationExpr = '''
        {meshParticle}.goalU = {leadParticle}.goalU;
        {meshParticle}.goalV = {leadParticle}.goalV;
        '''.format(meshParticle=self.meshParticle.getShape(), leadParticle=self.leadParticle.getShape())
        pm.dynExpression(self.meshParticle.getShape(), string=meshParticleCreationExpr, c=True)

    def connectControl(self):
        self.controlGrp.startFrame >> self.leadParticleSolver.startFrame
        self.controlGrp.startFrame >> self.meshParticleSolver.startFrame
        self.controlGrp.tailLength >> self.meshParticle.getShape().radiusScale[1].radiusScale_Position
        self.controlGrp.radius >> self.meshParticle.getShape().attr('radius')
        self.controlGrp.blobbyRadius >> self.meshParticle.getShape().blobbyRadiusScale

    def cleanupOutliner(self):
        self.controlGrp | self.locator
        self.controlGrp | self.leadParticleSolver
        self.controlGrp | self.meshParticleSolver
        self.controlGrp | self.leadParticle
        self.controlGrp | self.meshParticle
        self.controlGrp | self.meshParticle.getShape().outMesh.connections()[0]


def assignSolver(solver, particle):
    pm.disconnectAttr(particle.getShape().currentState)
    pm.disconnectAttr(particle.getShape().startState)
    pm.disconnectAttr(particle.getShape().nextState)

    particle.getShape().currentState >> solver.inputActive[0]
    particle.getShape().startState >> solver.inputActiveStart[0]
    solver.outputObjects[0] >> particle.getShape().nextState
    solver.startFrame >> particle.getShape().startFrame


def updateStartPosition(locator):
    closestPointOnMesh = locator.translate.connections()[0]
    leadParticleShape = locator.leadParticle.connections()[0]
    leadParticleCreationExpr = '''
    {leadParticle}.goalU = {closestPointGoalU};
    {leadParticle}.goalV = {closestPointGoalV};
    '''.format(leadParticle=leadParticleShape,
                closestPointGoalU=closestPointOnMesh.parameterU.get(),
                closestPointGoalV=closestPointOnMesh.parameterV.get())
    pm.dynExpression(leadParticleShape, string=leadParticleCreationExpr, c=True)


class UI(object):
    dropletCreator = None
    winName = None
    locatorTxtFldGrp = None
    meshTxtFldGrp = None

    def __init__(self):
        self.dropletCreator = DropletCreator
        self.winName = 'dropletWin'
        self.build()

    def build(self):
        if pm.window(self.winName, q=True, exists=True):
            pm.deleteUI(self.winName)
        pm.window(self.winName, title='Droplet Creator', mnb=False, mxb=False)

        pm.columnLayout(adj=True)
        self.locatorTxtFldGrp = pm.textFieldGrp(label='Locator: ', columnWidth=(1,50))
        pm.popupMenu()
        pm.menuItem(label='Load Selected', c=lambda args: self.locatorTxtFldGrp.setText(pm.ls(sl=True)[0]))
        self.meshTxtFldGrp = pm.textFieldGrp(label='Mesh: ', columnWidth=(1,50))
        pm.popupMenu()
        pm.menuItem(label='Load Selected', c=lambda args: self.meshTxtFldGrp.setText(pm.ls(sl=True)[0]))
        pm.button(label='Create Droplet', c=lambda args: self.dropletCreator(self.locatorTxtFldGrp.getText(), self.meshTxtFldGrp.getText()))
        pm.button(label='Update Start Position', c=lambda args: updateStartPosition(pm.ls(sl=True)[0]), ann='Select deoplet locator and press.')

        pm.window(self.winName, e=True, w=10, h=10)
        pm.showWindow(self.winName)
