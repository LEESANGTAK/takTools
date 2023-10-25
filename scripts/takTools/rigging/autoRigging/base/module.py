import pymel.core as pm


class Module():
    def __init__(self, name, parentSpace=None):
        self.name = name
        self.parentSpace = parentSpace

        self.topGrp = None
        self.geoGrp = None
        self.outGrp = None
        self.systemGrp = None
        self.noTransformGrp = None
        self.ctrlGrp = None

        self.createGroups()
        self.parentGroups()

    def createGroups(self):
        self.topGrp = pm.group(n=self.name + '_module', empty=True)
        self.geoGrp = pm.group(n=self.name + '_geo_grp', empty=True)
        self.geoGrp.inheritsTransform.set(False)
        self.outGrp = pm.group(n=self.name + '_out_grp', empty=True)
        self.systemGrp = pm.group(n=self.name + '_sys_grp', empty=True)
        self.noTransformGrp = pm.group(n=self.name + '_noTransform_grp', empty=True)
        self.noTransformGrp.inheritsTransform.set(False)
        self.ctrlGrp = pm.group(n=self.name + '_ctrl_grp', empty=True)

    def parentGroups(self):
        pm.parent(self.geoGrp, self.outGrp, self.systemGrp, self.ctrlGrp, self.topGrp)
        pm.parent(self.noTransformGrp, self.systemGrp)
        if self.parentSpace:
            pm.parent(self.topGrp, self.parentSpace)
