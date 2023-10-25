"""

          X
         XXX
         X XX        
         X   XX      
        XX    XX     
       XX      XX    
     XX          XX  
   XX             XX 
 XXX               XX
XX             X    X
X              XX   X
X              XX   X
X             XX   XX
XX           XX    X 
 XXX      XXX     XX
   XXX         XXX   
     XXXXXXXXXXX     





Water Droplet Generator v1.2

Move the scripts to: Documents\maya\YEAR\scripts
Move the images to: Documents\maya\YEAR\prefs\icons


Copy and Paste this section of code to launch the UI. Make sure you set it to Python.

import gui
reload(gui)
gui.windowUI



CONTACT DETAILS:

Name: Zeno Pelgrims
Portfolio: www.graffik.be
Twitter: https://twitter.com/zenopelgrims
Blog: zenopelgrims.tumblr.com
Email: info@graffik.be


"""


# import modules
from waterDropFunctions import *
import maya.cmds as cmds

# user interface
def windowUI(*args):

	# create the window
	if cmds.window("windowUI", exists=True):
		cmds.deleteUI("windowUI")
	cmds.window("windowUI", title="Water Droplet Generator v1.2", resizeToFitChildren = True, sizeable = False)

	# header image
	cmds.rowColumnLayout(w=380)
	cmds.image(image="waterDropGenerator_header.png")
	cmds.setParent("..")

	# base object layout
	cmds.frameLayout(label = "General", collapsable=False, mw=5, mh=5)
	cmds.rowColumnLayout(nc=3, cal=[(1,"right")], cw=[(1,80),(2,200),(3,95)])
	cmds.text(l="Base Object: ")
	cmds.textField("baseObject")
	cmds.button("baseObjectButton", l="Select", c=selectBaseObjectButton)
	cmds.setParent("..")
	cmds.separator(h=10, st='in')

	# density
	cmds.rowColumnLayout(w=380)
	cmds.intSliderGrp("dropDensity", l="Density: ", v=1200, cw3=[80,40,200], min=1, max=2500, fmx=10000, f=True)

	# minDropSize
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("minDropSize", l="Minimum Size: ", v=0.02, cw3=[80,40,200], min=0.01, max=0.1, fmx=1, f=True, pre = 2)

	# maxDropSize
	cmds.rowColumnLayout(w=380)
	cmds.floatSliderGrp("maxDropSize", l="Maximum Size: ", v=0.35, cw3=[80,40,200], min=0.1, max=1, fmx=10, f=True, pre = 2)
	cmds.separator(h=10, st='in')

	# randomness
	cmds.rowColumnLayout(w=380)
	cmds.checkBox("optCheckBox", l='Use an optimised randomness combination (recommended)', value=True, onc="cmds.intSliderGrp('randomness', e=True, en=False)", ofc="cmds.intSliderGrp('randomness', e=True, en=True)")
	cmds.intSliderGrp("randomness", l="Randomness: ", v=8, cw3=[80,40,230], min=1, max=8, fmx=10, f=True, enable=False)
	cmds.separator(h=10, st='in')

	# extra options
	cmds.rowColumnLayout(w=380)
	cmds.frameLayout(label = "Extra Options", collapsable=True, cl = True, mw = 5, mh = 5)
	cmds.checkBox("smoothCheckBox", l='Smooth preview the waterdrops', value=True)
	cmds.checkBox("shaderCheckBox", l='Apply a simple blinn water material - NCCA purposes only', value=False)
	cmds.setParent("..")
	cmds.separator(h=10, st='in')

	# check buttons
	cmds.rowColumnLayout(nc=2, cal=[(1,"right")], cw=[(1,185),(2,185)])
	cmds.button("checkMeshButton", l="Check Mesh", al="center", c=checkMeshButton, bgc=[0.15,0.4,0.15])
	cmds.button("subDMeshButton", l="Subdivide Mesh", al="center", c=subDMeshButton, bgc=[0.4,0.15,0.15])
	cmds.setParent("..")
	cmds.separator(h=10, st='in')

	# generate button
	cmds.button("generateButton", l="Make it rain baby", w=370, h = 40, al="center", bgc=[0.4,0.15,0.15], c=waterDropsButton)

	# reset button
	cmds.button("resetButton", l="Reset to default values", w=370, al="center", c=windowUI)
	
	# add to shelf button
	cmds.button("shelfButton", l="Add this script to the shelf", w=370, al="center", c=shelfButton)

	# text
	cmds.text(l='', w=370, h=10, ww=True)
	cmds.text(l='Please bear in mind that the default size values are physically accurate when your object is correctly scaled to real world units.', w=370, h=30, ww=True)
	cmds.text(l='The algorithm works best on objects with evenly spaced topology.', w=370, h=30, ww=True)
	cmds.text(l='Zeno Pelgrims - www.graffik.be - NCCA 2014', w=370, h=30, ww=True, fn="smallPlainLabelFont")

	cmds.showWindow("windowUI")


def selectBaseObjectButton(*args):
	# variables
	selectedObject = cmds.ls(sl=True, tr=True)

	# call selectBaseObject function
	selectBaseObject(selectedObject)


def checkMeshButton(*args):
	# variables
	selectedObject = cmds.ls(sl=True, tr=True)
	dropDensity = cmds.intSliderGrp("dropDensity", query=True, v=True)

	#call function
	checkMesh(selectedObject, dropDensity)


def subDMeshButton(*args):
	# variables
	dropDensity = cmds.intSliderGrp("dropDensity", query=True, v=True)

	# call function
	subDMesh(dropDensity)


def waterDropsButton(*args):
	# variables
	dropDensity = cmds.intSliderGrp("dropDensity", query=True, v=True)
	minDropSize = cmds.floatSliderGrp("minDropSize", query=True, v=True)
	maxDropSize = cmds.floatSliderGrp("maxDropSize", query=True, v=True)
	randomness = cmds.intSliderGrp("randomness", query=True, v=True)
	optRandCheckBox = cmds.checkBox("optCheckBox", query=True, v=True)
	smoothCheckBox = cmds.checkBox('smoothCheckBox', query=True, v=True)
	shaderCheckBox = cmds.checkBox("shaderCheckBox", query=True, v=True)

	# call function
	waterDrops(dropDensity, minDropSize, maxDropSize, randomness, optRandCheckBox, smoothCheckBox)
	waterShader(shaderCheckBox)

def shelfButton(*args):
	# write the current shelf to a variable
	currentTab = mel.eval('tabLayout -q -selectTab $gShelfTopLevel;')
	
	# copy the script into the shelf
	cmds.shelfButton(l='Water Drop Generator', annotation="Water Droplet Generator v1.2", i1="waterDropGenerator_shelfIcon_small.png", w=30, h=30, p=currentTab, command=str("import gui;reload(gui);gui.windowUI"))


windowUI()
