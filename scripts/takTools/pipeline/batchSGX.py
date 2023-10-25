import os
import glob
import shutil
import subprocess
from functools import partial
import pymel.core as pm


if not pm.pluginInfo('sgx', q=True, loaded=True):
    pm.loadPlugin('sgx')


# ---------------------------------------
# Constants
# ---------------------------------------
SGX_BIN = "S:/Shared/artTools/maya/3rdParty/speechGraphics/SGX/bin/sgx.exe"
RESOURCES_DIR = "S:/Shared/artTools/maya/3rdParty/speechGraphics/resources"
ACTOR_INFO = {
    'JCB': {
        'name': 'Jacob',
        'rig': "S:/Phoenix/ContentArt/Characters/Player/Rig/Player_Face_SGX.ma",
    },
    'DNI': {
        'name': 'Dani',
        'rig': "S:/Phoenix/ContentArt/Characters/Dani/Rig/Dani_SGX.ma",
    }
}
WIN_NAME = 'bathSGXWin'


# ---------------------------------------
# GUI
# ---------------------------------------
def showUI():
    if pm.window(WIN_NAME, exists=True):
        pm.deleteUI(WIN_NAME)

    pm.window(WIN_NAME, title='Batch SGX UI', mnb=False, mxb=False)

    pm.columnLayout('mainColLayout', adj=True, rowSpacing=5)

    pm.textFieldButtonGrp('audioDirTxtFldBtnGrp', label='Audio Directory:', buttonLabel='<<', columnWidth=[(1, 85), (2, 160)], bc=partial(__setPath, 'audioDirTxtFldBtnGrp', 3))
    pm.optionMenu('langOptionMenu', label='Language:', w=275)
    pm.optionMenu('actorTokenMenu', label='Actor Token:', w=275)

    pm.button(label='Generate!', c=__generate)

    __populateOptionMenu('langOptionMenu', 'languages')
    __populateActorTokenMenu()

    pm.window(WIN_NAME, edit=True, w=10, h=10)
    pm.showWindow(WIN_NAME)


def __populateOptionMenu(menuName, folderName):
    for char in glob.glob('{}/{}/*.k'.format(RESOURCES_DIR, folderName)):
        charName = os.path.basename(char).split('.')[0]
        pm.menuItem(label=charName, p=menuName)
    pm.optionMenu('langOptionMenu', e=True, v='English_US')


def __populateActorTokenMenu():
    for actorToken in ACTOR_INFO.keys():
        pm.menuItem(label='{}: {}'.format(actorToken, ACTOR_INFO[actorToken]['name']), p='actorTokenMenu')
    pm.optionMenu('actorTokenMenu', e=True, v='JCB: Jacob')


def __setPath(textFieldButtonGrpName, fileMode):
    path = pm.fileDialog2(fileMode=fileMode)
    if path:
        pm.textFieldButtonGrp(textFieldButtonGrpName, e=True, text=path[0])


def __generate(*args):
    inputAudioDir = pm.textFieldButtonGrp('audioDirTxtFldBtnGrp', q=True, text=True)
    language = pm.optionMenu('langOptionMenu', q=True, value=True)
    actorToken = pm.optionMenu('actorTokenMenu', q=True, value=True).split(':')[0]

    actorAudioFiles = filterActorAudioFiles(inputAudioDir, actorToken)
    actorDir = createActorDirectory(inputAudioDir, ACTOR_INFO[actorToken]['name'])
    copyAudioFiles(actorAudioFiles, actorDir)
    audioListFile = createInputFile(actorAudioFiles, actorDir, 'audio_list.txt')
    eventFiles = generateEvents(audioListFile, actorDir, ACTOR_INFO[actorToken]['name'], language)
    eventListFile = createInputFile(eventFiles, actorDir, 'event_list.txt')

    # When character is loaded already then skip loading character
    namespaces = pm.namespaceInfo(listOnlyNamespaces=True)
    if ACTOR_INFO[actorToken]['name'] not in namespaces:
        pm.newFile(f=True)
        loadCharacter(ACTOR_INFO[actorToken]['rig'], ACTOR_INFO[actorToken]['name'])

    generateMayaFiles(eventListFile, actorDir)
    removeTempFiles(actorDir)



# ---------------------------------------
# API
# ---------------------------------------
def filterActorAudioFiles(audioDir, actorToken):
    actorAudioFiles = []
    for audioFile in glob.glob('{}/*.wav'.format(audioDir)):
        if actorToken in audioFile:
            actorAudioFiles.append(audioFile)
    return actorAudioFiles


def createActorDirectory(audioDir, actorName):
    actorDir = os.path.join(audioDir, actorName)
    if not os.path.exists(actorDir):
        os.mkdir(actorDir)
    return actorDir


def copyAudioFiles(audioFiles, actorDir):
    for audioFile in audioFiles:
        dstAudioFile = os.path.join(actorDir, os.path.basename(audioFile))
        shutil.copyfile(audioFile, dstAudioFile)


def generateEvents(audioListFile, outputEventDir, character, language='English_US'):
    eventFiles = []
    subprocess.call([
        SGX_BIN,
        '-i', audioListFile,
        '-o', outputEventDir,
        '-r', RESOURCES_DIR,
        '-c', character,
        '-l', language,
        '-P', '0.0',
        '-Q', '0.0',
        '-N'
    ])
    with open(audioListFile, 'r') as f:
        fileContents = f.read()
        eventFiles = fileContents.replace('.wav', '.event').split('\n')
    return eventFiles


def loadCharacter(facialRig, character):
    ref = pm.createReference(facialRig, namespace=character)
    charDef = os.path.join(RESOURCES_DIR, 'characters', '{}.k'.format(character))
    pm.sgx_load_character(c=charDef, n=ref.namespace)


def generateMayaFiles(eventListFile, outputMayaDir):
    # pm.sgx_export(i=eventListFile, o=outputMayaDir, f='maya', a=False)
    # When using sgx_export command, file overwrite confirm dialog is poped up if maya file already exists
    with open(eventListFile, 'r') as f:
        eventFiles = f.read().split('\n')
    for eventFile in eventFiles:
        pm.sgx_import(i=os.path.join(outputMayaDir, eventFile), a=True)
        mayaFileName = os.path.basename(eventFile).replace('.event', '.ma')
        pm.exportAll(os.path.join(outputMayaDir, mayaFileName), type='mayaAscii', preserveReferences=True, f=True)


def removeTempFiles(actorDir):
    for file in os.listdir(actorDir):
        ext = os.path.splitext(file)[-1]
        if ext not in ['.ma', '.wav']:
            os.remove(os.path.join(actorDir, file))


def createInputFile(files, actorDir, filename):
    inputFile = os.path.join(actorDir, filename)
    files = [os.path.basename(file) for file in files]
    with open(inputFile, 'w') as f:
        f.write('\n'.join(files))
    return inputFile


# --------------------------------------------------------------
# Codes to process for upated audio files only
# --------------------------------------------------------------
from P4 import P4, P4Exception
from datetime import datetime, timedelta

PORT = '1670'
USER = 'chst27'
AUDIO_DIR = '//Phoenix/Main/Phoenix/ContentArt/Audio/VO/LipFlap'
UPDATE_HOUR = 0
PROCESSING_TIME = 23
AUDIO_EXT = 'wav'


def getUpdatedAudioFiles(startDate, endDate):
    """Get updated audio files from perforce change list with specific period.

    :param startDate: Start date for searcing. Should be YYYY/MM/DD
    :type startDate: str
    :param endDate: End date for searching. Should be YYYY/MM/DD
    :type endDate: str
    """
    p4 = P4()
    p4.port = PORT
    p4.user = USER
    p4.client = "Client"

    try:
        p4.connect()
        changelist = p4.run_filelog('{}...@{},@{}'.format(AUDIO_DIR, startDate, endDate))
        updatedAudioFiles = []
        for r in changelist:
            if r.depotFile.endswith(AUDIO_EXT):
                updatedAudioFiles.append(r.depotFile)
        print(updatedAudioFiles)
    except P4Exception:
        for e in p4.errors:
            print(e)
    finally:
        p4.disconnect()
