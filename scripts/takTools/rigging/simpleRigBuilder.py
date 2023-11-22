import pymel.core as pm


def cleanupGeometry(geometry):
    geo = pm.PyNode(geometry)
    pm.makeIdentity(geo, apply=True)
    pm.delete(geo, ch=True)


def rigGeometry(geometry):
    geo = pm.PyNode(geometry)

    rootJnt = pm.createNode("joint", n="root")
    rootJnt.jointOrientX.set(-90)
    pm.skinCluster(geo, rootJnt)

    geoWidth = geo.boundingBox().width()
    globalCtrl = pm.circle(n="global_ctrl", r=geoWidth, normal=(0, 1, 0), ch=False)[0]
    pm.group(n="{0}_zero".format(globalCtrl))
    pm.group(n="rig")

    pm.parentConstraint(globalCtrl, rootJnt, mo=True)
    pm.scaleConstraint(globalCtrl, rootJnt, mo=True)


pm.undoInfo(openChunk=True)
geo = pm.selected()[0]
cleanupGeometry(geo)
rigGeometry(geo)
pm.undoInfo(closeChunk=True)