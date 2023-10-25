# coding : utf-8
# Copyright (C) auto alembic shader assign tool
#
# File: alembic_mtl.py
#
#
#
# Author: ffacce@naver.com 2014
# http://cafe.naver.com/digitaldream

import maya.cmds as cmds

class shapeData:
    name = None
    shape = None
    full_name = None
    full_shape = None
    polyCount = None
    shader_list = None
    isDefualt = None

    def __init__(self):
        self.name = ''
        self.shape = ''
        self.full_name = ''
        self.full_shape = ''
        self.polyCount = 0
        self.shader_list = []
        self.isDefualt = False


class AssignShapeMtl():
    def __init__(self):
        self.all_shapes = []
        self.shaded_shapes = []
        self.default_shapes =[]

    def selectShapes(self, all_list):#received allPaths
        clean_list = list(set(all_list))
        #print 'clean_list', clean_list
        for sh in clean_list:
            shapes = cmds.listRelatives(sh, s=1, pa=1)
            sdata = shapeData()
            sdata.full_name = sh
            sdata.name = sh.split('|')[-1]
            sdata.full_shape = shapes[0]
            sdata.shape = shapes[0].split('|')[-1]

            sdata.polyCount = cmds.polyEvaluate(shapes[0], f=1)
            sha_list = self.getAllShader(shapes[0])

            sdata.shader_list = sha_list
            sdata.isDefualt = self.checkIsDefault(sha_list)

            if sdata.isDefualt:
                self.default_shapes.append(sdata)
            else:
                self.shaded_shapes.append(sdata)

            self.all_shapes.append(sdata)


    def getAllShader(self, sha):
        shadingGrps = cmds.listConnections(sha,type='shadingEngine')
        shaders = list(set(cmds.ls(cmds.listConnections(shadingGrps),materials=1)))
        clean_list = list(set(shaders))
        return clean_list

    def checkIsDefault(self, sha_list):
        if not sha_list:
            return True

        sha_check_list = [x for x in sha_list if x not in ['lambert1']]
        if len(sha_check_list):
            return False
        else:
            return True

    def getDefaultList(self):
        return self.default_shapes

    def getShadedList(self):
        return self.shaded_shapes

    def getShadedCount(self):
        return len(self.shaded_shapes)

    def findSameCountFaces(self, sdata):
        rnt_list = [x for x in self.default_shapes if x.polyCount == sdata.polyCount]
        return rnt_list

    def assignShadeToDefault(self, shaded_, default_):
        for sh in shaded_.shader_list:
            cmds.hyperShade(o= sh)

            sel_list = cmds.ls(sl=1, allPaths=1)
            if not sel_list:
                return

            clean_list = []

            if [x for x in sel_list if '.f[' in x]:
                print('f mode')
                clean_list = [x.replace(shaded_.full_name, default_.full_name) for x in sel_list
                              if shaded_.name ]
            else:
                print('g mode')
                clean_list = [x.replace(shaded_.full_shape, default_.full_shape) for x in sel_list
                              if shaded_.shape in x]
            #print 'clean', clean_list
            cmds.select(clean_list)
            cmds.hyperShade(assign=sh)


    def checkNameInName(self, shade_shape, default_shade):
        if ':' in shade_shape:
            sh_name = shade_shape.split(':')[-1]
            if sh_name in default_shade:
                return True
        else:
            if shade_shape in default_shade:
                return True


        if ':' in default_shade:
            de_name = default_shade.split(':')[-1]
            if de_name in shade_shape:
                return True
        else:
            if default_shade in shade_shape:
                return True

        return False

class AssignMtlCtl(AssignShapeMtl):
    def __init__(self):
        AssignShapeMtl.__init__(self)

    def selectAllCtl(self):
        all_list = cmds.ls(sl=1, o=1, type='transform', ap=1)
        if not all_list:
            return

        assign_list = []
        self.selectShapes(all_list)


        for sh in self.shaded_shapes:
            f_sdata_list = self.findSameCountFaces(sh)
            if f_sdata_list:
                if len(f_sdata_list) > 0:
                    for sha in f_sdata_list:

                        if self.checkNameInName(sh.name, sha.name):
                            assign_list.append(sh.full_name)

                            self.assignShadeToDefault(sh, sha)
        cmds.select(assign_list, r=1)



