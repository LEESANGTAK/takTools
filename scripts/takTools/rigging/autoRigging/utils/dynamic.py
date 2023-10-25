import pymel.core as pm

from . import globalUtil



def changeSolver(dynamicNode, solver=None):
    if not solver:
        solver = pm.createNode('nucleus')
    else:
        solver = pm.PyNode(solver)

    dynamicNode = pm.PyNode(dynamicNode)
    if dynamicNode.nodeType() == 'transform':
        dynamicNode = dynamicNode.getShape()

    oldSolver = list(set(dynamicNode.inputs(type='nucleus')))

    time1 = pm.PyNode('time1')
    time1.outTime.connect(solver.currentTime, f=True)

    solver.startFrame.connect(dynamicNode.startFrame, f=True)

    index = globalUtil.findMultiAttributeEmptyIndex(node=solver, attribute='outputObjects')
    solver.outputObjects[index].connect(dynamicNode.nextState, f=True)

    index = globalUtil.findMultiAttributeEmptyIndex(node=solver, attribute='inputActive')
    dynamicNode.currentState.disconnect()
    dynamicNode.currentState.connect(solver.inputActive[index])

    index = globalUtil.findMultiAttributeEmptyIndex(node=solver, attribute='inputActiveStart')
    dynamicNode.startState.disconnect()
    dynamicNode.startState.connect(solver.inputActiveStart[index])

    pm.delete(oldSolver)
