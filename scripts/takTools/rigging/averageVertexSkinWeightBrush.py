# Description:
# A custom brush for smoothing skin weight.
# It applies the average of surrounding vertices weight values to the painted vertex.

# Modification:
# - Optimized
# - Support undo/redo.

# Modified by : nuternativ
#       nuttynew@hotmail.com
#       nuternativtd.blogspot.com

# How to install: 1.  Within the folder averageVertexSkinWeight,
#           choose a folder depending on your Maya version.
#           Paste
#           - averageVertexSkinWeightCmd.py (Python version)
#           or
#           - averageVertexSkinWeightCmd.mll (C++ version)
#           to your plugin path.
#           (ie. C:\Program Files\Autodesk\<Version>\bin\plug-ins)
#         2.  Within the same folder as your plugin file (.py or .mll)
#           Paste
#           - averageVertexSkinWeightBrush.py
#           to your python path.
#           (ie. C:\Documents and Settings\<username>\My Documents\maya\<Version>\scripts)
#         3.  Restart Maya and execute the following python command.

# '''

# import averageVertexSkinWeightBrush
# reload(averageVertexSkinWeightBrush)
# averageVertexSkinWeightBrush.paint()

# '''

##############################################################################################################
import maya.mel as mel
from maya.cmds import pluginInfo as pluginInfo
from maya.cmds import loadPlugin as loadPlugin

pluginFileName = 'averageVertexSkinWeightCmd.py'
if pluginInfo(pluginFileName, q=True, l=True) == False:
  loadPlugin(pluginFileName)


def initPaint():
  cmd = '''
  global string $avgVertexSkinWeightsBrushSel[];

  global proc averageVertexWeightBrush(string $context) {
      artUserPaintCtx -e -ic "init_averageVertexWeightBrush" -svc "set_averageVertexWeightBrush"
      -fc "" -gvc "" -gsc "" -gac "" -tcc "" $context;
  }

  global proc init_averageVertexWeightBrush(string $name) {
      global string $avgVertexSkinWeightsBrushSel[];

      $avgVertexSkinWeightsBrushSel = {};
      string $sel[] = `ls -sl -fl`;
      string $obj[] = `ls -sl -o`;
      $objName = $obj[0];

      int $i = 0;
      for($vtx in $sel) {
          string $buffer[];
          int $number = `tokenize $vtx ".[]" $buffer`;
          $avgVertexSkinWeightsBrushSel[$i] = $buffer[2];
          $i++;
          if ($number != 0)
          $objName = $buffer[0];
      }
  }

  global proc set_averageVertexWeightBrush(int $slot, int $index, float $val) {
      global string $avgVertexSkinWeightsBrushSel[];

      if($avgVertexSkinWeightsBrushSel[0] != "") {
          if(!stringArrayContains($index, $avgVertexSkinWeightsBrushSel))
              return;
      }
      averageVertexSkinWeight -i $index -v $val;
  }
  '''
  mel.eval(cmd)



def paint():
  cmd = '''
  ScriptPaintTool;
  artUserPaintCtx -e -tsc "averageVertexWeightBrush" `currentCtx`;
  '''
  mel.eval(cmd)


initPaint()

