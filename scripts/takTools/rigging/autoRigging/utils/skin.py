import pymel.core as pm


def bind(jnts, geos, maxInfluence=4):
    """
    Binds geometries with given joints.

    Args:
        jnts (list): Bind joints.
        geos (list): Geometries to bind.
        maxInfluence (int, optional): Number of influeces per point. Defaults to 1.
    """
    geoShpLs = pm.ls(geos, dag=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface'])

    for geoShp in geoShpLs:
        skinClst = pm.mel.eval('findRelatedSkinCluster("%s");' % geoShp)
        if skinClst:
            pm.select(geoShp, r=True)
            pm.mel.eval('DetachSkin();')
        pm.skinCluster(jnts, geoShp, tsb=True, bm=0, wd=0, omi=False, mi=maxInfluence, dr=4.0)


def createSkinMeshWithJoints(name, joints, width=1.0):
    skinMesh = None

    jntsLength = 0
    for jnt in joints[1:]:
        jntsLength += abs(jnt.tx.get())

    width = jntsLength*0.05
    profileCurve = pm.circle(normal=[1, 0, 0], radius=width, n='profile_crv')[0]

    profileCurves = []
    for jnt in joints:
        dupProfileCrv = profileCurve.duplicate()
        pm.xform(dupProfileCrv, matrix=jnt.worldMatrix.get(), ws=True)
        profileCurves.append(dupProfileCrv)

    skinSurface = pm.loft(profileCurves, degree=1, sectionSpans=int(jntsLength/len(joints)), ch=False)
    skinMesh = pm.nurbsToPoly(skinSurface, format=3, polygonType=1, ch=False, n='{0}_skin'.format(name))

    pm.delete(skinSurface)
    pm.delete(profileCurve)
    pm.delete(profileCurves)

    bind(joints[:-1], skinMesh)  # Exclude end joint for binding

    return skinMesh
