# /************************************************************************************************
#  ************************************************************************************************
#  ***                                                                                          ***
#  ***                                                                                          ***
#  ***                               Spherize v1.01 2013                                        ***
#  ***                                                                                          ***
#  ***                                                                                          ***
#  ************************************************************************************************
#  ************************************************************************************************

#   DESCRIPTION:
#   This script will attempt to 'Spherify' the current selected objects or components.
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  
#   AUTHOR: 
#   Shannon Hochkins
#   shannon@shannonhochkins.com
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  
#   USAGE:
#   1. Open script editor and load spherize.py
#   2. Click File > save script to shelf
#   3. An icon is provided for the shelf button in your download
#   Simply select your desired components or objects to be spherified and press the giant button!
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#   INSPIRATION:
#   I wrote this tool to aid others with the horrible task of modelling cylindrical shapes from a quadrilateral surface.
#   Blender has had this feature for years and I decided to give it a go!
#   Please don't hesitate to let me know if any bugs or comments on this tool!
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -*/
#

import math as math
from pymel.core import *
class sphereizedSelection():
    messages = ["Please make sure you have selected something.", "Completed! ", "Performing checks on selection... "]
    def __init__(self, *args):
        if window("spherizeSelection", exists=1): deleteUI("spherizeSelection")
        window("spherizeSelection", title="Spherize Selection - Shannon Hochkins", w=405, sizeable=0)    
        with columnLayout('content', adjustableColumn=True):
            with frameLayout( label='Settings', borderStyle='in'):
                with columnLayout(columnAttach=('both', 15), rs=15, cal='left', cw=395 ):
                    text(l="Select any component(s) or poly object(s).", h=30)
                    checkBox('flatten',l='Attempt to flatten selection ', cc=self.enableRadio)
                    separator( 'baseSep', height=5, style='in', en=0, vis=0)
                    radioButtonGrp('flattenRadio', numberOfRadioButtons=3, adj=1, label='Normal Axis ', labelArray3=['X', 'Y', 'Z'], en=0, vis=0)
                    radioButtonGrp('flattenRadio', e=1, sl=1, cw=[10,100], cal=((1, 'left')), h=50)
            with columnLayout(columnAttach=('both', 15), rs=15, cal='left', cw=405 ):
                separator( style='none')
                button(c=self.average, l='Average Selection', w=380, )
                button(l='Spherize', c=self.relay, height=50, w=380, backgroundColor=(.2, .2, .2))
                with rowColumnLayout(nc=2, cal=[(1,'right'), (2,'right')], cw=[(1,200),(2,170)]):        
                    text('displayInfo', l=self.messages[2],vis=0)
                    progressBar('buildGridProgBar', maxValue=100, width=150,vis=0)                    
                    showWindow("spherizeSelection")
    def relay(self, *args):        
        b = ls(os=1)
        select(cl=1)
        if (len(b) == 0):
            warning(self.messages[0])
        else:
            text('displayInfo',e=1,vis=1)            
            refresh(f=1)
            for i in range(0,len(b),1):                
                selectedType =  listRelatives(b[i])                      
                if (selectedType != []):
                    type = PyNode(b[i]).getShape().type()
                    if (type == 'mesh'):                        
                        select(polyListComponentConversion(b[i],tv=1),add=1)
                    if (type == 'nurbsCurve'):                        
                        select(b[i],add=1)
                        runtime.SelectCurveCVsAll(b[i])                                                   
                    self.spherize()
                else:
                    select(b[i], add=1)                                
            if (len(selected(fl=1)) > 0 and selectedType == []):
                self.convertToVerts(selected())
                self.spherize() 
    def spherize(self, *args):
        s = selected(fl=1)
        setToolTo('Move')
        s, avd, oda, cs = selected(fl=1), 0, [], manipMoveContext("Move", q=1, p=1)
        select(cl=1)
        if (checkBox('flatten', q=1, v=1) == 1):
            select(s,r=1)
            self.flatten()        
        for verts in range(0, len(s), 1):
            vts = s[verts].getPosition(space='world')
            dfc = math.sqrt(pow(vts[0] - cs[0],2) + pow(vts[1] - cs[1],2) + pow(vts[2] - cs[2],2))
            oda += [(dfc)]
            avd += dfc
            text('displayInfo',e=1,l='Calculating new positions on '+ listRelatives(listRelatives(s[verts],p=1)[0], p=1)[0] +'... ') 
            progressBar('buildGridProgBar', edit=1, progress=int((float((verts + 1)) / float(len(s))) * 100),vis=1)
        avd /= len(s)
        for vert in range(0, len(s), 1):
            vts = s[vert].getPosition(space='world')
            x, y, z = (((avd / oda[vert]) * (vts[0] - cs[0])) + cs[0]), (((avd / oda[vert]) * (vts[1] - cs[1])) + cs[1]), (((avd / oda[vert]) * (vts[2] - cs[2])) + cs[2])
            s[vert].setPosition([x,y,z], space='world')
            text('displayInfo',e=1,l='Performing Witchcraft on '+ listRelatives(listRelatives(s[verts],p=1)[0], p=1)[0] +'... ')
            progressBar('buildGridProgBar', edit=1, progress=int((float((vert + 1)) / float(len(s))) * 100),vis=1)
            refresh()    
            text('displayInfo',e=1,l=self.messages[1])
            select(cl=1)
    def flatten(self, *args):
        self.convertToVerts(selected())
        setToolTo('Scale')
        manipScaleContext("Scale", e=1, mode=9)
        p, oa, r = manipScaleContext("Scale", q=1, p=1), manipScaleContext("Scale", q=1, oa=1), radioButtonGrp('flattenRadio',q=1,sl=1)
        scale((0,1,1) if r == 1 else (1,0,1) if r == 2 else (1,1,0), p=(p[0],p[1],p[2]), ls=1, oa=("%srad"%oa[0],"%srad"%oa[1],"%srad"%oa[2]))
        text('displayInfo',e=1,l=self.messages[1])
        select(cl=1)
    def average(self, *args):
        if (len(selected(fl=1)) == 0):
            warning(self.messages[0])
        else:
            self.convertToVerts(selected())
            s = selected()
            polyAverageVertex(s, ch=1)
    def enableRadio(self, *args):
        if (checkBox('flatten',q=1,v=1) == 1):
            setToolTo('Scale')
            manipScaleContext("Scale", e=1, mode=9)
            radioButtonGrp('flattenRadio', e=1,en=1,vis=1)
            separator('baseSep', e=1,vis=1)
        else:
            radioButtonGrp('flattenRadio', e=1,en=0,vis=0)
            separator('baseSep', e=1,vis=0)
    def convertToVerts(self, object):
        runtime.ConvertSelectionToVertices(object)
sphereizedSelection()