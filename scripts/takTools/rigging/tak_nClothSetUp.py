"""
Author: Sang-tak Lee
Contact: chst27@gmail.com

Created: 09/14/2015
Last Update: 05/08/2017

Description:
This script build nCloth set up automatically.

Usage:
import tak_nClothSetUp
reload(tak_nClothSetUp)
tak_nClothSetUp.nClothSetUp()
"""

from functools import partial

import maya.cmds as cmds
import maya.mel as mel

from ..modeling import tak_cleanUpModel
from ..common import tak_lib


class nClothSetUp(object):
    # Members/Attributes/Properties
    widgets = {}

    # Methods/Funtions
    @classmethod
    def __init__(cls):
        """
        Initializing.
        """

        cls.widgets['winName'] = 'nClothSetUpWin'

        if cmds.window(cls.widgets['winName'], exists=True):
            cmds.deleteUI(cls.widgets['winName'])

        cls.ui()

    @classmethod
    def ui(cls):
        cmds.window(cls.widgets['winName'], title='nCloth Set Up')

        cls.widgets['mainColLo'] = cmds.columnLayout(p=cls.widgets['winName'], adj=True)

        cls.widgets['mainTabLo'] = cmds.tabLayout(p=cls.widgets['mainColLo'], tv=False)

        cls.widgets['tabColLo'] = cmds.columnLayout(p=cls.widgets['mainTabLo'], adj=True)

        cls.widgets['solverNameTxtFldGrp'] = cmds.textFieldGrp(p=cls.widgets['tabColLo'], label='Solver Name: ',
                                                               columnWidth=[(1, 70), (2, 80)])

        cmds.separator(p=cls.widgets['tabColLo'], h=5, style='none')

        cls.widgets['geoRowColLo'] = cmds.rowColumnLayout(p=cls.widgets['tabColLo'], numberOfColumns=2,
                                                          columnSpacing=[(2, 5)])

        cls.widgets['nClothGeoFrameLo'] = cmds.frameLayout(p=cls.widgets['geoRowColLo'], label='Skin Geo to Dynamic')
        cls.widgets['colliderGeoFrameLo'] = cmds.frameLayout(p=cls.widgets['geoRowColLo'], label='Skin Geo to Collider')

        cls.widgets['nClothGeoTxtScrLs'] = cmds.textScrollList(p=cls.widgets['nClothGeoFrameLo'])
        cls.widgets['nClothGeoPopMenu'] = cmds.popupMenu(p=cls.widgets['nClothGeoTxtScrLs'])
        cmds.menuItem(p=cls.widgets['nClothGeoPopMenu'], label='Load Selected',
                      c=partial(tak_lib.populateTxtScrList, 'textScrollList', cls.widgets['nClothGeoTxtScrLs']))

        cls.widgets['colliderGeoTxtScrLs'] = cmds.textScrollList(p=cls.widgets['colliderGeoFrameLo'])
        cls.widgets['colliderGeoPopMenu'] = cmds.popupMenu(p=cls.widgets['colliderGeoTxtScrLs'])
        cmds.menuItem(p=cls.widgets['colliderGeoPopMenu'], label='Load Selected',
                      c=partial(tak_lib.populateTxtScrList, 'textScrollList', cls.widgets['colliderGeoTxtScrLs']))

        cmds.separator(p=cls.widgets['mainColLo'], h=5, style='none')

        cmds.button(p=cls.widgets['mainColLo'], label='Set Up!', h=30, c=cls.setUpNcloth)

        cmds.window(cls.widgets['winName'], e=True, w=100, h=100)
        cmds.showWindow(cls.widgets['winName'])

    @classmethod
    def setUpNcloth(cls, *args):
        """
        Main method.
        """

        solverName = cmds.textFieldGrp(cls.widgets['solverNameTxtFldGrp'], q=True, text=True)
        nClothGeoList = cmds.textScrollList(cls.widgets['nClothGeoTxtScrLs'], q=True, allItems=True)
        colliderGeoList = cmds.textScrollList(cls.widgets['colliderGeoTxtScrLs'], q=True, allItems=True)

        # Create new solver
        if not cmds.objExists(solverName + '_nucleus'):
            solver = cmds.createNode('nucleus', n=solverName + '_nucleus')
            cmds.setAttr('%s.subSteps' % solver, 12)
            cmds.setAttr('%s.maxCollisionIterations' % solver, 12)
            cmds.setAttr('%s.timeScale' % solver, 1.0)
            cmds.setAttr('%s.spaceScale' % solver, 0.05)
            cmds.setAttr('%s.visibility' % solver, 0)
            cmds.connectAttr('time1.outTime', solver + '.currentTime', f=True)
        else:
            solver = solverName + '_nucleus'

        # Clean up outliner
        if not cmds.objExists(solverName + '_dyn_grp'):
            allGrp = cmds.createNode('transform', n=solverName + '_dyn_grp')
        else:
            allGrp = solverName + '_dyn_grp'

        if not cmds.objExists(solverName + '_collider_grp'):
            colliderGrp = cmds.createNode('transform', n=solverName + '_collider_grp')
        else:
            colliderGrp = solverName + '_collider_grp'

        try:
            cmds.parent(solver, colliderGrp, allGrp)
        except:
            pass

        # Collider set up
        if colliderGeoList:
            for colliderGeo in colliderGeoList:
                cmds.select(colliderGeo, r=True)
                nRgdShp = mel.eval('makeCollideNCloth;')
                nRgdTrsf = cmds.listRelatives(nRgdShp, p=True)[0]
                newNRgdName = cmds.rename(nRgdTrsf, colliderGeo + '_nRigid')

                # Get assigned solver to cloth
                newNRgdShp = cmds.listRelatives(newNRgdName, s=True)
                solverAssignedRgdShp = cmds.listConnections(newNRgdShp, s=False, d=True)

                cmds.select(newNRgdName, r=True)
                mel.eval('assignNSolver "%s";' % solver)

                cmds.parent(newNRgdName, colliderGeo, colliderGrp)

            # Connect time node outTime attribute to solver currentTime attribute
            newNRgdShp = cmds.listRelatives(newNRgdName, s=True)[0]
            timeNode = cmds.listConnections('%s.currentTime' % newNRgdShp)[0]
            try:
                cmds.connectAttr('%s.outTime' % timeNode, '%s.currentTime' % solver)
            except:
                pass

        if nClothGeoList:
            for clothGeo in nClothGeoList:
                skinClst = mel.eval('findRelatedSkinCluster("%s");' % clothGeo)
                if not skinClst:
                    cmds.error('{clothGeo} has no skin cluster.'.format(clothGeo=clothGeo))
                    return

                # Duplicate geo for 'Attract to Matching Mesh' nConstraint
                clothName = clothGeo.rsplit('_', 1)[0]
                goalGeo = cmds.duplicate(clothGeo, n=clothName + '_goal_geo')[0]

                # Clean up gaolGeo and transfer skin from clothGeo
                cmds.select(goalGeo, r=True)
                tak_cleanUpModel.delHis()
                tak_cleanUpModel.delInterMediObj()
                tak_lib.copySkin(clothGeo, goalGeo)

                # Create nCloth
                cmds.select(clothGeo, r=True)
                origNclothShp = mel.eval('createNCloth 0;')
                nClothTrsf = cmds.listRelatives(origNclothShp, p=True)[0]
                newClothName = cmds.rename(nClothTrsf, clothName + '_nCloth')

                # Get assigned solver to cloth
                nClothShp = cmds.ls(cmds.listHistory(newClothName), type='nCloth')
                solverAssignedNcloth = list(set(cmds.ls(cmds.listConnections(nClothShp), type='nucleus')))[0]

                # Change solver
                cmds.select(newClothName, r=True)
                mel.eval('assignNSolver "%s";' % solver)

                # If auto created solver exists delete
                if not solverAssignedNcloth == solver:
                    cmds.delete(solverAssignedNcloth)

                # Attract to Matching Mesh nConstraint
                cmds.select(goalGeo, clothGeo, r=True)
                goalCnstNodes = mel.eval('createNConstraint match 0;')
                cmds.setAttr('%s.constraintMethod' % goalCnstNodes[1], 0)

                goalCnstNRgdPrnt = cmds.listRelatives(goalCnstNodes[0], p=True)[0]
                goalCnstNRgd = cmds.rename(goalCnstNRgdPrnt, clothName + '_goal_cnst_nRigid')

                goalCnstDynCnstPrnt = cmds.listRelatives(goalCnstNodes[1], p=True)[0]
                goalCnstDynCnst = cmds.rename(goalCnstDynCnstPrnt, clothName + '_goal_dynCnst')

                # Clean up outliner
                clothGrp = cmds.createNode('transform', n=clothName + '_nCloth_grp')
                nCnstGrp = cmds.createNode('transform', n=clothName + '_nCnst_grp')
                cmds.setAttr('%s.visibility' % nCnstGrp, 0)

                cmds.parent(clothGeo, newClothName, clothGrp)
                cmds.parent(goalGeo, goalCnstNRgd, goalCnstDynCnst, nCnstGrp)
                cmds.parent(nCnstGrp, clothGrp)
                cmds.parent(clothGrp, allGrp)
