'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date:

Description:
'''

import maya.cmds as cmds



class UI(object):
    winName = 'crvToPolyWin'
    widgets = {}
    
    @classmethod
    def __init__(cls):
        if cmds.window(cls.winName, exists = True):
            cmds.deleteUI(cls.winName)

        cls.ui()


    @classmethod
    def ui(cls):
        cmds.window(cls.winName, title = 'Curve To Poly', mnb = False, mxb = False)

        cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

        cls.widgets['radiusSldrGrp'] = cmds.floatSliderGrp(label = 'Radius: ', field = True, min = 0.01, max = 15, fmn = 0.1, fmx = 100, v = 1, step = 0.01, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.radiusCmd)
        cls.widgets['scaleEndSldrGrp'] = cmds.floatSliderGrp(label = 'Scale End: ', field = True, min = 0, max = 10, fmn = 0, fmx = 10, v = 1, step = 0.01, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.scaleEndCmd)
        cls.widgets['scaleXSldrGrp'] = cmds.floatSliderGrp(label = 'Scale X: ', field = True, min = 0.1, max = 30, fmn = 0.1, fmx = 30, v = 1, step = 0.01, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.scaleXCmd)
        cls.widgets['scaleZSldrGrp'] = cmds.floatSliderGrp(label = 'Scale Z: ', field = True, min = 0.1, max = 30, fmn = 0.1, fmx = 30, v = 1, step = 0.01, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.scaleZCmd)

        cmds.separator(style = 'in', h = 5, p = cls.widgets['mainColLo'])

        cls.widgets['divFrntSldrGrp'] = cmds.intSliderGrp(label = 'Subdiv Front: ', field = True, min = 1, max = 1000, fmn = 1, fmx = 1000, v = 8, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.subdivFrontCmd)
        cls.widgets['divSideSldrGrp'] = cmds.intSliderGrp(label = 'Subdiv Side: ', field = True, min = 3, max = 20, fmn = 3, fmx = 20, v = 8, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.subdivSideCmd)
        cls.widgets['sweepSldrGrp'] = cmds.floatSliderGrp(label = 'Sweep: ', field = True, min = 0, max = 360, fmn = 0, fmx = 360, v = 360, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.sweepCmd)

        cmds.separator(style = 'in', h = 5, p = cls.widgets['mainColLo'])

        cls.widgets['rotateSldrGrp'] = cmds.floatSliderGrp(label = 'Rotate: ', field = True, min = 0, max = 360, fmn = 0, fmx = 360, v = 45, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.rotateCmd)
        cls.widgets['twistSldrGrp'] = cmds.floatSliderGrp(label = 'Twist: ', field = True, min = 0, max = 360, fmn = 0, fmx = 360, v = 0, columnWidth = [(1, 80)], p = cls.widgets['mainColLo'], cc = Functions.twistCmd)

        cmds.separator(style = 'none', h = 5, p = cls.widgets['mainColLo'])

        cls.widgets['mainBtnRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnWidth = [(1, 90), (2, 90), (3, 90), (4, 90)], columnOffset = [(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2)], p = cls.widgets['mainColLo'])
        cmds.button(label = 'Convert', p = cls.widgets['mainBtnRowColLo'], c = Functions.convert)
        cmds.button(label = 'Select Profile', p = cls.widgets['mainBtnRowColLo'], c = Functions.selProfile)
        cmds.button(label = 'Select Curve', p = cls.widgets['mainBtnRowColLo'], c = Functions.selCrv)
        cmds.button(label = 'Apply', p = cls.widgets['mainBtnRowColLo'], c = Functions.apply)

        cmds.window(cls.winName, e = True, w = 300, h = 200)
        cmds.showWindow(cls.winName)



class Functions(object):

    @classmethod
    def convert(cls, *args):
        cls.selCrvs = cmds.ls(sl = True)
        polyTubeLs = []

        for crv in cls.selCrvs:
            # create nurbs circle for profile and place to start point of the Path
            profile = cmds.circle(name = '%s_profile' %(crv), normal = (0, 1, 0), degree = 1, constructionHistory = True)[0]
            zroCvPos = cmds.pointPosition('%s.cv[0]' %(crv), world = True)
            cmds.xform(profile, ws = True, t = zroCvPos)
            # profile scale grp
            scaleGrp = cmds.duplicate(profile, po = True, n = '%s_scale' %(profile))
            cmds.makeIdentity(scaleGrp, apply = True)
            cmds.parent(profile, scaleGrp)
            # set to profile rotation 45 degree as default
            cmds.setAttr('%s.rotateY' %(profile), 45)

            # rebuild crv
            # cls.rebuildCrv(crv, 8)

            # extrude
            extrRslt = cmds.extrude(profile, crv, ch = True, rn = False, et = 2, po = 1, ucp = 1, fpt = 1, upn = 1, rsp = 1, n = '%s_poly' %(crv))
            polyTubeLs.append(extrRslt[0])

            # hide curve and profile
            cmds.hide(profile)

        cmds.select(polyTubeLs)

        # Set polygon shape with ui information
        cls.radiusCmd()
        cls.scaleEndCmd()
        cls.scaleXCmd()
        cls.scaleZCmd()
        cls.subdivFrontCmd()
        cls.subdivSideCmd()
        cls.sweepCmd()
        cls.rotateCmd()
        cls.twistCmd()


    @classmethod
    def rebuildCrv(cls, crvName, numSpan):
        cmds.rebuildCurve(crvName, replaceOriginal = True, keepEndPoints = True, spans = numSpan, degree = 3)


    @classmethod
    def subdivFrontCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        subDivFrontVal = cmds.intSliderGrp(UI.widgets['divFrntSldrGrp'], q = True, v = True)

        for crv in selCrvs:
            cls.rebuildCrv(crv, subDivFrontVal)
            cmds.select(selCrvs, r = True)
        cmds.select(selLs, r = True)
        

    @classmethod
    def subdivSideCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        subDivSideVal = cmds.intSliderGrp(UI.widgets['divSideSldrGrp'], q = True, v = True)

        for crv in selCrvs:
            crvProfileShape = cmds.listRelatives('%s_profile' %(crv), s = True)
            crvProfileMakeNode = cmds.listConnections(crvProfileShape, s = True, d = False)[0]
            cmds.setAttr('%s.sections' %(crvProfileMakeNode), subDivSideVal)


    @classmethod
    def sweepCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        sweepVal = cmds.floatSliderGrp(UI.widgets['sweepSldrGrp'], q = True, v = True)

        for crv in selCrvs:
            crvProfileShape = cmds.listRelatives('%s_profile' %(crv), s = True)
            crvProfileMakeNode = cmds.listConnections(crvProfileShape, s = True, d = False)[0]
            cmds.setAttr('%s.sweep' %(crvProfileMakeNode), sweepVal)


    @classmethod
    def scaleXCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        scaleXVal = cmds.floatSliderGrp(UI.widgets['scaleXSldrGrp'] , q = True, v = True)

        for crv in selCrvs:
            cmds.setAttr('%s_profile_scale.scaleX' %(crv), scaleXVal)


    @classmethod
    def scaleZCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        scaleZVal = cmds.floatSliderGrp(UI.widgets['scaleZSldrGrp'] , q = True, v = True)

        for crv in selCrvs:
            cmds.setAttr('%s_profile_scale.scaleZ' %(crv), scaleZVal)


    @classmethod
    def radiusCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        radiusVal = cmds.floatSliderGrp(UI.widgets['radiusSldrGrp'], q = True, v = True)

        for crv in selCrvs:
            crvProfileShape = cmds.listRelatives('%s_profile' %(crv), s = True)
            crvProfileMakeNode = cmds.listConnections(crvProfileShape, s = True, d = False)[0]
            cmds.setAttr('%s.radius' %(crvProfileMakeNode), radiusVal)


    @classmethod
    def scaleEndCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        scaleEndVal = cmds.floatSliderGrp(UI.widgets['scaleEndSldrGrp'], q = True, v = True)

        for crv in selCrvs:
            crvProfileShape = cmds.listRelatives('%s_profile' %(crv), s = True)
            extrudeNode = cmds.listConnections(crvProfileShape, s = False, d = True)[0]
            cmds.setAttr('%s.scale' %(extrudeNode), scaleEndVal)


    @classmethod
    def rotateCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        rotateVal = cmds.floatSliderGrp(UI.widgets['rotateSldrGrp'], q = True, v = True)

        for crv in selCrvs:
            cmds.setAttr('%s_profile.rotateY' %(crv), rotateVal)


    @classmethod
    def twistCmd(cls, *args):
        # cmds.select(cls.selCrvs)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        twistVal = cmds.floatSliderGrp(UI.widgets['twistSldrGrp'], q = True, v = True)

        for crv in selCrvs:
            crvProfileShape = cmds.listRelatives('%s_profile' %(crv), s = True)
            extrudeNode = cmds.listConnections(crvProfileShape, s = False, d = True)[0]
            cmds.setAttr('%s.rotation' %(extrudeNode), twistVal)


    @classmethod
    def apply(cls, *args):
        # cmds.select(cls.selCrvs, r = True)
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)

        for crv in selCrvs:
            # # delete cv 1 and before of end cv
            # degs = cmds.getAttr('%s.degree' %(crv))
            # spans = cmds.getAttr('%s.spans' %(crv))
            # cvs = degs+spans
            # cmds.delete('%s.cv[%d]' %(crv, cvs - 2))
            # cmds.delete('%s.cv[%d]' %(crv, 1))

            # merge vertex
            cmds.select('%s_poly' %crv, r = True)
            cmds.polyMergeVertex(d = 0.001)

            # delete construction history of polygon
            cmds.delete('%s_poly' %crv, ch = True)

            # delete curve and profile
            cmds.delete(crv, '%s_profile_scale' %(crv))

        cmds.select(cl = True)


    @classmethod
    def selProfile(cls, *args):
        selLs = cmds.ls(sl = True)
        selCrvs = cls.getPathCrvFromPoly(selLs)
        profileList = []

        for sel in selCrvs:
            profileName = '%s_profile' %(sel)
            profileList.append(profileName)

        cmds.select(profileList, r = True)


    @classmethod
    def selCrv(cls, *args):
        '''
        Select curve(s).
        '''

        cmds.select(cls.selCrvs, r = True)


    @staticmethod
    def getPathCrvFromPoly(selPolyTubes, *args):
        '''
        Get path curves form selected poly tubes.
        '''

        pathCrvLs = []

        for tube in selPolyTubes:
            tubeShp = cmds.listRelatives(tube, s = True)[0]
            nrbsTessNode = cmds.listConnections(tubeShp, d = False)
            extrNode = cmds.listConnections(nrbsTessNode, d = False)
            srcCrvLs = cmds.listConnections(extrNode, d = False)
            for crv in srcCrvLs:
                if not 'profile' in crv:
                    pathCrvLs.append(crv)
                    break
        return pathCrvLs