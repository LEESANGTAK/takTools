import pymel.core as pm


def smoothKey(object, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], iteration=5):
    for attr in attributes:
        # Get animCurve node
        animCrv = pm.listConnections('{0}.{1}'.format(object, attr), d=False, type='animCurve')
        if not animCrv:
            continue
        animCrv = animCrv[0]

        # Get key values
        oldKeyValues = []
        for i in range(animCrv.numKeys()):
            oldKeyVal = animCrv.getValue(i)
            oldKeyValues.append(oldKeyVal)

        # Smooth values
        smoothedKeyValues = oldKeyValues
        iter = iteration
        while iter:
            for i in range(1, animCrv.numKeys()-1):
                preVal = smoothedKeyValues[i-1]
                postVal = smoothedKeyValues[i+1]
                curVal = (preVal + postVal) * 0.5
                smoothedKeyValues[i] = curVal
            iter -= 1

        # Set smoothed key values
        for i in range(animCrv.numKeys()):
            animCrv.setValue(i, smoothedKeyValues[i])


def copyAnimation(source, target):
    for input in source.inputs(type="animCurve"):
        dest = input.outputs(type="transform", plugs=True)[0]
        newAnimCrv = input.duplicate()[0]
        newDestAttr = dest.replace(source.name(), target.name())
        if pm.objExists(newDestAttr):
            newDestAttr = pm.PyNode(newDestAttr)
            if not newDestAttr.isLocked():
                newAnimCrv.output >> newDestAttr
