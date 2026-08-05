from maya import cmds


def smoothKey(object, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], iteration=5):
    for attr in attributes:
        anim_crvs = cmds.listConnections('{}.{}'.format(object, attr), d=False, s=True, type='animCurve')
        if not anim_crvs:
            continue

        anim_crv = anim_crvs[0]
        times = cmds.keyframe(anim_crv, q=True, tc=True) or []
        values = cmds.keyframe(anim_crv, q=True, vc=True) or []
        if len(times) < 3 or len(values) < 3:
            continue

        smoothed_values = list(values)
        iterations = iteration
        while iterations:
            for i in range(1, len(smoothed_values) - 1):
                pre_val = smoothed_values[i - 1]
                post_val = smoothed_values[i + 1]
                smoothed_values[i] = (pre_val + post_val) * 0.5
            iterations -= 1

        for time, value in zip(times, smoothed_values):
            cmds.keyframe(anim_crv, e=True, time=(time, time), vc=value)


def copyAnimation(source, target):
    source = str(source)
    target = str(target)

    anim_crvs = cmds.listConnections(source, s=True, d=False, type='animCurve') or []
    for anim_crv in anim_crvs:
        dest_plugs = cmds.listConnections(anim_crv, d=True, s=False, plugs=True) or []
        for dest_plug in dest_plugs:
            if not dest_plug.startswith(source + '.'):
                continue

            new_dest_attr = dest_plug.replace(source, target)
            if cmds.objExists(new_dest_attr) and not cmds.getAttr(new_dest_attr, lock=True):
                new_anim_crv = cmds.duplicate(anim_crv)[0]
                cmds.connectAttr('{}.output'.format(new_anim_crv), new_dest_attr, force=True)


def transferRootSidemotionToPelvis(worldUpAxis='Y', rootJoint='Root', pelvisJoint='pelvis'):
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    attrs = [ch + axis for ch in 'trs' for axis in 'xyz']

    # Extract animations of the root front and pelvis in the world coordinate
    rootLoc = cmds.spaceLocator(n='{}_loc'.format(rootJoint))[0]
    pelvisLoc = cmds.spaceLocator(n='{}_loc'.format(pelvisJoint))[0]
    cmds.parent(pelvisLoc, rootLoc)

    if worldUpAxis == 'Y':
        cmds.pointConstraint(rootJoint, rootLoc, mo=False, skip=['x', 'y'])
    elif worldUpAxis == 'Z':
        cmds.pointConstraint(rootJoint, rootLoc, mo=False, skip=['x', 'z'])
    cmds.parentConstraint(pelvisJoint, pelvisLoc, mo=False)

    cmds.select([rootLoc, pelvisLoc], r=True)
    cmds.bakeResults(t=(minTime, maxTime))

    # Transfer extracted world animation to the root and pelvis joint
    cmds.cutKey(rootJoint, pelvisJoint, cl=True, at=attrs)

    if worldUpAxis == 'Y':
        cmds.pointConstraint(rootLoc, rootJoint, mo=False, skip=['x', 'y'])
    elif worldUpAxis == 'Z':
        cmds.pointConstraint(rootLoc, rootJoint, mo=False, skip=['x', 'z'])
    cmds.parentConstraint(pelvisLoc, pelvisJoint, mo=False)

    cmds.select([rootJoint, pelvisJoint], r=True)
    cmds.bakeResults(t=(minTime, maxTime))

    cmds.delete(rootLoc, pelvisLoc)
