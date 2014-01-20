import math
import pickle
import pymel.core as pm


# Decorators
def moveFix(function):
    '''
    Fixs "Some items cannot be moved in the 3D view" Warning
    '''
    def decoratedFunction(*args, **kwargs):
        currentTool = pm.currentCtx()
        selectTool = pm.melGlobals['gSelect']
        if currentTool != selectTool:
            pm.setToolTo(selectTool)
            function(*args, **kwargs)
            pm.setToolTo(currentTool)
        else:
            function(*args, **kwargs)
    return decoratedFunction


class UI(object):
    def __init__(self):
        title = 'pbUV'
        ver = '1.00'

        if pm.window('pbUV', exists=True):
            pm.deleteUI('pbUV')

        window = pm.window('pbUV', s=True, title='{0} | {1}'.format(title, ver), toolbox=False)

        try:
            pane = pm.paneLayout('textureEditorPanel', paneSize=[1, 1, 1], cn='vertical2', swp=1)
        except:
            pane = pm.paneLayout('textureEditorPanel', paneSize=[1, 1, 1], cn='vertical2')

        uvTextureViews = pm.getPanel(scriptType='polyTexturePlacementPanel')
        if len(uvTextureViews):
            pm.scriptedPanel(uvTextureViews[0], e=True, unParent=True)

        with pm.columnLayout(p=pane):
            transformUI()
            globalOptions()
            setEditorUI()
            densityUI()
            snapshotUI()

        pm.scriptedPanel(uvTextureViews[0], e=True, parent=pane)

        # Replace Default UV Editor Toolbar
        flowLayout = pm.melGlobals['gUVTexEditToolBar']
        frameLayout = pm.flowLayout(flowLayout, q=True, p=True)
        frameLayout = pm.uitypes.FrameLayout(frameLayout)
        pm.deleteUI(flowLayout)

        flowLayout = pm.flowLayout(p=frameLayout)
        tools01UI(flowLayout)
        cutSewUI(flowLayout)
        unfoldUI(flowLayout)
        alignUI(flowLayout)
        pushUI(flowLayout)
        snapUI(flowLayout)
        layoutUI(flowLayout)
        isolateUI(flowLayout, uvTextureViews[0])
        opts01UI(flowLayout, uvTextureViews[0])
        opts02UI(flowLayout, uvTextureViews[0])
        opts03UI(flowLayout, uvTextureViews[0])
        manipUI(flowLayout)

        window.show()

    @staticmethod
    def dumpSettings():
        pass

    @staticmethod
    def loadSettings():
        pass


class globalOptions(object):
    def __init__(self):
        with pm.frameLayout(l='Options', cll=True, cl=False, bs='out'):
            with pm.columnLayout():
                pm.text('Map Size:')
                pm.separator(st='in', width=160, height=8)
                with pm.rowColumnLayout(nc=3, cw=[20, 60]):
                    pm.text(l='Width:')
                    self.width = pm.intField(v=1024, width=42)
                    self.resPresets = pm.optionMenu()
                    pm.text(l='Height:')
                    self.height = pm.intField(v=1024, width=42)
                    self.resPresets = pm.optionMenu()
                pm.button(l='Get Map Size')

                pm.separator(st='in', width=160, height=8)
                with pm.columnLayout():
                    self.compSpace = pm.checkBox(l='Retain Component Spaceing',
                                                 cc=lambda *args: pm.texMoveContext('texMoveContext', e=True, scr=self.compSpace.getValue()),
                                                 v=pm.texMoveContext('texMoveContext', q=True, scr=True))
                    self.pixelUnits = pm.checkBox(l='Transform In Pixels')

    def dumpSettings(self):
        pass


class transformUI(object):
    def __init__(self):
        with pm.frameLayout(l='Transform:', cll=True, cl=False, bs='out'):
            with pm.columnLayout():
                with pm.gridLayout(nc=5):
                    pm.iconTextButton(image1='pbUV/tRot90CCW.png', c=lambda *args: self.rotate(angle=90, dir='ccw'),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tRotCCW.png', c=lambda *args: self.rotate(dir='ccw'),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tTranslateUp.png', c=lambda *args: self.move(v=1),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tRotCW.png', c=lambda *args: self.rotate(dir='cw'))
                    pm.iconTextButton(image1='pbUV/tRot90CW.png', c=lambda *args: self.rotate(angle=90, dir='cw'),
                                      commandRepeatable=True)

                    flipUV = pm.iconTextButton(image1='pbUV/tFlipUV.png', c=lambda *args: self.flip(axis='u'),
                                               commandRepeatable=True)
                    pm.popupMenu(button=3, p=flipUV, pmc=lambda *args: self.flip(axis='v'))
                    pm.iconTextButton(image1='pbUV/tTranslateLeft.png', c=lambda *args: self.move(u=-1),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tTranslateDown.png', c=lambda *args: self.move(v=-1),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tTranslateRight.png', c=lambda *args: self.move(u=1),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tRot180CCW.png', c=lambda *args:self.rotate(angle=180, dir='ccw'),
                                      commandRepeatable=True)

                with pm.rowColumnLayout(nc=4):
                    self.manipValue = pm.floatField(v=1.0)
                    pm.iconTextButton(image1='pbUV/tScaleU.png', c=lambda *args: self.scale(axis='u'),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tScaleV.png', c=lambda *args: self.scale(axis='v'),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tScaleUV.png', c=lambda *args: self.scale(),
                                      commandRepeatable=True)

                pm.separator(st='in', width=160, height=8)

                with pm.rowLayout(nc=2):
                    pm.button(l='Orient Edge', c=self.orientEdge)
                    pm.button(l='Orient Bounds', c=self.orientBounds)

                pm.separator(st='in', width=160, height=8)

                with pm.columnLayout(cal='left'):
                    pm.text(l='Pivot:')
                    self.pivType = pm.radioButtonGrp(nrb=2, labelArray2=['Selection', 'Custom'], cw2=[64, 64], cc=self._pivChange, sl=1)
                    with pm.rowLayout(nc=3, en=False) as self.pivPos:
                        pm.text('POS:')
                        self.pivU = pm.floatField()
                        self.pivV = pm.floatField()
                    self.sampleSel = pm.button(l='Sample Selection', height=18, en=False, c=self.sampleSelCmd)

    def _pivChange(self, *args):
        if self.pivType.getSelect() == 1:
            self.pivPos.setEnable(False)
            self.sampleSel.setEnable(False)
        else:
            self.pivPos.setEnable(True)
            self.sampleSel.setEnable(True)

    def pivLoc(self, *args):
        if self.pivType.getSelect() == 1:
            uvs = UV()
            return uvs.getPivot()
        else:
            return self.pivU.getValue(), self.pivV.getValue()

    def sampleSelCmd(self, *args):
        uvs = UV()
        piv = uvs.getPivot()
        self.pivU.setValue(piv[0])
        self.pivV.setValue(piv[1])

    @moveFix
    def move(self, u=0, v=0):
        pm.polyEditUV(uValue=self.manipValue.getValue() * u, vValue=self.manipValue.getValue() * v)

    def rotate(self, angle=None, dir='ccw'):
        if angle == None:
            angle = self.manipValue.getValue()

        if dir == 'ccw':
            dir = 1
        elif dir =='cw':
            dir = -1

        pm.polyEditUV(pu=self.pivLoc()[0], pv=self.pivLoc()[1], angle=angle * dir)

    def scale(self, axis=None, flip=False):
        if axis == 'u':
            u = self.manipValue.getValue()
            v = 0
        elif axis == 'v':
            u = 0
            v = self.manipValue.getValue()
        else:
            u = self.manipValue.getValue()
            v = self.manipValue.getValue()

        pm.polyEditUV(pu=self.pivLoc()[0], pv=self.pivLoc()[1], su=u, sv=v)

    def flip(self, axis='u'):
        if axis == 'u':
            u = -1
            v = 1
        elif axis == 'v':
            u = 1
            v = -1

        pm.polyEditUV(pu=self.pivLoc()[0], scaleU=u, scaleV=v)

    def orientEdge(self, *args):
        pass

    def orientBounds(self, *args):
        pass


class setEditorUI(object):
    def __init__(self):
        with pm.frameLayout(l='Set Editor:', cll=True, cl=False, bs='out'):
            with pm.columnLayout(width=162):
                self.uvs = pm.textScrollList(w=160, h=72,
                                             sc=self.selectSet,
                                             dcc=self.renameSet,
                                             dkc=self.deleteSet)
                self.updateSets()

                with pm.rowLayout(nc=4):
                    pm.button(l='New', c=self.addSet)
                    pm.button(l='Copy', c=self.dupSet)
                    pm.button(l='Rename', c=self.renameSet)
                    pm.button(l='Delete', c=self.deleteSet)
                with pm.rowLayout(nc=2):
                    pm.button(l='UV Linking', c=lambda *args:pm.mel.UVCentricUVLinkingEditor())
                    pm.button(l='Refresh', c=self.updateSets)

    def updateSets(self, *args):  # FIXME
        self.uvs.removeAll()
        sel = pm.selected()

        if all(isinstance(i, pm.nt.Transform) for i in sel):
            sel = [i.getShape() for i in sel]

        elif all(isinstance(i, pm.Component) for i in sel):
            sel = [sel[0].node()]

        uvSets = []
        for obj in sel:
            for uvSet in obj.getUVSetNames():
                uvSets.append('{0} | {1}'.format(obj.getParent(), uvSet))
        self.uvs.append(uvSets)

        # Select Current UV Set
        try:
            self.uvs.setSelectItem('{0} | {1}'.format(sel[0].getParent(), sel[0].getCurrentUVSetName()))
        except:
            pass


    def selectSet(self, *args):
        uvSet = self.uvs.getSelectItem()[0].split(' | ')
        pm.polyUVSet(uvSet[0], currentUVSet=True, uvSet=uvSet[1])

    def renameSet(self, *args):
        bDialog = pm.promptDialog(title='Rename UVSet',
                                  message='Enter New UvSet Name:',
                                  button=['OK', 'Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        if bDialog == 'OK':
            uvSet = self.uvs.getSelectItem()[0].split(' | ')
            pm.polyUVSet(uvSet[0], rename=True, uvSet=uvSet[1], newUVSet=pm.promptDialog(q=True, text=True))
            self.updateSets()

    def deleteSet(self, *args):
        uvSet = self.uvs.getSelectItem()[0].split(' | ')
        try:
            pm.polyUVSet(uvSet[0], delete=True, uvSet=uvSet[1])
            self.updateSets()
        except RuntimeError:
            pm.warning('The defualt uv set cannot be deleted.')
            self.updateSets()

    def addSet(self, *args):
        uvSet = self.uvs.getSelectItem()[0].split(' | ')
        bDialog = pm.promptDialog(title='Add New UVSet',
                                  message='Enter New UVSet Name:',
                                  button=['OK', 'Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        if bDialog == 'OK':
            pm.polyUVSet(uvSet[0], create=True, uvSet=pm.promptDialog(q=True, text=True))
            self.updateSets()

    def dupSet(self, *args):
        uvSet = self.uvs.getSelectItem()[0].split(' | ')
        bDialog = pm.promptDialog(title='Duplicate UVSet',
                                  message='Enter New UVSet Name:',
                                  button=['OK', 'Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        if bDialog == 'OK':
            pm.polyUVSet(uvSet[0], copy=True, uvSet=uvSet[1], newUVSet=pm.promptDialog(q=True, text=True))
            self.updateSets()


class densityUI(object):
    def __init__(self):
        with pm.frameLayout(l='Texel Density:', cll=True, cl=False, bs='out'):
            with pm.columnLayout(width=162):
                pass


class snapshotUI(object):
    def __init__(self):
        with pm.frameLayout(l='UV Snapshot:', cll=True, cl=False, bs='out'):
            with pm.columnLayout(width=162):
                pass


# ToolBar UI Stuff
class toolsUI(object):
    def __init__(self, par):
        self.sep = pm.iconTextButton(image1='textureEditorOpenBar.png', p=par, c=self.toggleVisible)

    def toggleVisible(self, *args):
        if self.layout.getVisible():
            self.layout.setVisible(False)
            self.sep.setImage1('textureEditorCloseBar.png')
        else:
            self.layout.setVisible(True)
            self.sep.setImage1('textureEditorOpenBar.png')


class tools01UI(toolsUI):
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[26, 26]) as self.layout:
            pm.toolButton(dcc=lambda *args: pm.toolPropertyWindow,
                          collection='toolCluster',
                          tool=pm.texLatticeDeformContext(),
                          image1='uvlattice.png', style='iconOnly',
                          width=24, height=24)

            pm.toolButton(dcc=lambda *args: pm.toolPropertyWindow,
                          collection='toolCluster',
                          tool=pm.texMoveUVShellContext(),
                          image1='moveUVShell.png', style='iconOnly',
                          width=24, height=24)

            pm.toolButton(dcc=lambda *args: pm.toolPropertyWindow,
                          collection='toolCluster',
                          tool=pm.texSmoothContext(),
                          image1='texSmooth.png', style='iconOnly',
                          width=24, height=24)

            pm.toolButton(dcc=lambda *args: pm.toolPropertyWindow,
                          collection='toolCluster',
                          tool=pm.texSmudgeUVContext(),
                          image1='textureEditorSmudgeUV.png', style='iconOnly',
                          width=24, height=24)

            pm.toolButton(dcc=lambda *args: pm.toolPropertyWindow,
                          collection='toolCluster',
                          tool=pm.texSelectContext(),
                          image1='textureEditorShortestEdgePath.png', style='iconOnly',
                          width=24, height=24)


class cutSewUI(toolsUI):
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[26, 26]) as self.layout:
            pm.iconTextButton(image1='cutUV.png',
                              c=lambda *args: pm.polyMapCut(),
                              commandRepeatable=True,
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kSeparateUVsAlongSelectedEdgesAnnot'))

            pm.iconTextButton(image1='polySplitUVs.png',
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kSplitSelectedUV'),
                              c=lambda *args: pm.mel.polySplitTextureUV(),
                              commandRepeatable=True)

            pm.iconTextButton(image1='tearface', ann='Tear Off Selected Face From UVs',
                              c=self.tearFace,
                              commandRepeatable=True)

            sewUV = pm.iconTextButton(image1='sewUV.png',
                                      c=self.sewUV, commandRepeatable=True,
                                      ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kSewSelectedUVsTogetherAnnot'))
            pm.popupMenu(button=3, p=sewUV, pmc=lambda *args: pm.mel.performPolyMergeUV(1))

            moveSewUV = pm.iconTextButton(image1='moveSewUV.png',
                                          c=lambda *args: pm.mel.performPolyMapSewMove(0),
                                          commandRepeatable=True,
                                          ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kMoveAndSewSelectedEdgesAnnot'))
            pm.popupMenu(button=3, p=moveSewUV, pmc=lambda *args: pm.mel.performPolyMapSewMove(1))

    def sewUV(self):  # FIXME
        edges = pm.filterExpand(ex=False, selectionMask=32)
        uvs = pm.filterExpand(ex=False, selectionMask=35)
        if edges:
            pm.polyMapSew
        if uvs:
            pm.mel.performPolyMergeUV(0)

    def tearFace(self):
        sel = pm.selected()
        moveTool = pm.melGlobals['gMove']
        if all(isinstance(i, pm.MeshFace) for i in sel):
            if len(sel) == 1:
                pm.polyMapCut(sel)
                sel = pm.polyListComponentConversion(sel, ff=True, tuv=True)
                pm.select(sel)
            else:
                sewSel = pm.polyListComponentConversion(ff=True, te=True, internal=True)
                pm.polyMapCut(sel)
                pm.polyMapSewMove(sewSel, nf=10, lps=0, ch=1)
                sel = pm.polyListComponentConversion(sel, ff=True, tuv=True)
                pm.select(sel)
            pm.setToolTo(moveTool)


class unfoldUI(toolsUI):
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            unfold = pm.iconTextButton(image1='textureEditorUnfoldUVs.png',
                                       ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUnfoldAnnot'),
                                       c=lambda *args: pm.mel.performUnfold(0),
                                       commandRepeatable=True)
            pm.popupMenu(button=3, p=unfold, pmc=lambda *args: pm.mel.performUnfold(1))

            unfoldSep = pm.iconTextButton(image1='textureEditorUnfoldUVs.png',
                                          ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUnfoldAnnot'),
                                          c=lambda *args: self.unfoldSepCmd(2))
            pm.popupMenu(button=3, p=unfoldSep, pmc=lambda *args: self.unfoldSepCmd(1))

            relaxUV = pm.iconTextButton(image1='relaxUV.png',
                                        ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kRelaxUVsAnnot'),
                                        c=lambda *args: pm.mel.performPolyUntangleUV('relax', 0))
            pm.popupMenu(button=3, p=relaxUV, pmc=lambda *args: pm.mel.performPolyUntangleUV('relax', 1))

            pm.iconTextButton(image='Null',
                              c=lambda *args: self.matchShell(0.01),
                              commandRepeatable=True)

    def unfoldSepCmd(self, axis):
        pm.unfold(i=pm.optionVar['unfoldIterations'],
                  ss=pm.optionVar['unfoldStopThreshold'],
                  gb=pm.optionVar['unfoldGlobalBlend'],
                  gmb=pm.optionVar['unfoldGlobalMethodBlend'],
                  pub=pm.optionVar['unfoldPinBorder'],
                  ps=pm.optionVar['unfoldPinSelected'],
                  oa=axis,
                  useScale=False)

    def matchShell(self, maxRange):

        snapUVs = pm.ls(pm.polyListComponentConversion(tuv=True), sl=True, fl=True)  # getUVs to match

        objs = [i.getShape() for i in pm.ls(hl=True, fl=True)]
        allUVs = pm.ls(pm.polyListComponentConversion(objs, tuv=True), fl=True)
        allUVs = sorted(set(allUVs) - set(snapUVs))  # get all uvs and subtract from snap uvs

        snapPos = [pm.polyEditUV(i, q=True) for i in snapUVs]  # Get pos for snap and all
        allPos = [pm.polyEditUV(i, q=True) for i in allUVs]

        for i in range(len(snapUVs)):
            inRange = []
            for j in range(len(allUVs)):
                x = snapPos[i][0] - allPos[j][0]
                y = snapPos[i][1] - allPos[j][1]
                dist = math.sqrt((x**2) + (y**2))
                if dist < maxRange:
                    inRange.append((allPos[j], dist))

            if inRange:
                inRange = min(inRange, key=lambda x: x[1])
                pm.polyEditUV(snapUVs[i], u=inRange[0][0], v=inRange[0][1], r=False)

class alignUI(toolsUI):
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[26, 26]) as self.layout:
            pm.iconTextButton(image1='NS_alUVleft.bmp',
                              c=lambda *args: self.alignShells('left'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVCenterU.bmp',
                              c=lambda *args: self.alignShells('centerU'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVRight.bmp',
                              c=lambda *args: self.alignShells('right'),
                              commandRepeatable=True)

            pm.iconTextButton(image1='NS_alUVTop.bmp',
                              c=lambda *args: self.alignShells('top'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVCenterV.bmp',
                              c=lambda *args: self.alignShells('centerV'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVBottom.bmp',
                              c=lambda *args: self.alignShells('bottom'),
                              commandRepeatable=True)

    @moveFix
    def alignShells(self, align):
        sel = UV()
        sel.getShells()

        shellsUVs = []
        for shell in sel.shells:
            for uv in shell.uvs:
                shellsUVs.append(uv)

        allUVs = UV(shellsUVs)
        allUVs.getBounds()

        for shell in sel.shells:
            if align == 'left':
                pm.polyEditUV(shell.uvs, u=allUVs.xMin - shell.xMin)
            elif align == 'centerU':
                pm.polyEditUV(shell.uvs, u=(allUVs.xMin + allUVs.xMax) / 2 - (shell.xMax + shell.xMin) / 2)
            elif align == 'right':
                pm.polyEditUV(shell.uvs, u=allUVs.xMin - shell.xMin)

            elif align == 'top':
                pm.polyEditUV(shell.uvs, v=allUVs.yMax - shell.yMax)
            elif align == 'centerV':
                pm.polyEditUV(shell.uvs, v=(allUVs.yMin + allUVs.yMax) / 2 - (shell.yMax + shell.xMin) / 2)
            elif align == 'bottom':
                pm.polyEditUV(shell.uvs, v=allUVs.yMin - shell.yMin)


class pushUI(toolsUI):  # TODO Annotations
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[26, 26]) as self.layout:
            pm.iconTextButton(image1='pbUV/pushMinU.png',
                              c=lambda *args: pm.mel.alignUV(1, 1, 0, 0),
                              commandRepeatable=True)
            pm.iconTextButton(image1='pbUV/pushCenterU.png',
                              c=lambda *args: self.pushAverage('u'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='pbUV/pushMaxU.png',
                              c=lambda *args: pm.mel.alignUV(1, 0, 0, 0),
                              commandRepeatable=True)

            pm.iconTextButton(image1='pbUV/pushMaxV.png',
                              c=lambda *args: pm.mel.alignUV(0, 0, 1, 0),
                              commandRepeatable=True)
            pm.iconTextButton(image1='pbUV/pushCenterV.png',
                              c=lambda *args: self.pushAverage('v'))
            pm.iconTextButton(image1='pbUV/pushMaxV.png',
                              c=lambda *args: pm.mel.alignUV(0, 0, 1, 1),
                              commandRepeatable=True)

    def pushAverage(self, dir):
        uvs = UV()
        center = uvs.getPivot()
        if dir == 'u':
            pm.polyEditUV(uvs.uvs, r=False, u=center[0])
        if dir == 'v':
            pm.polyEditUV(uvs.uvs, r=False, v=center[1])


class snapUI(toolsUI):
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[18, 18]) as self.layout:
            pm.iconTextButton(image1='NS_snapTopLeft.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('topLeft'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapTop.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('topCenter'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapTopRight.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('topRight'),
                              commandRepeatable=True)

            pm.iconTextButton(image1='NS_snapLeft.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('centerLeft'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapCenter.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('center'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapRight.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('centerRight'),
                              commandRepeatable=True)

            pm.iconTextButton(image1='NS_snapBottomLeft.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('bottomLeft'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapBottom.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('bottomCenter'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapBottomRight.bmp', width=16, height=16,
                              c=lambda *args: self.snapUVs('bottomRight'),
                              commandRepeatable=True)

    def snapUVs(self, pos):
        uvs = UV()

        piv = uvs.getPivot()
        bounds = uvs.getBounds()
        centerU = 0.5 - piv[0]
        centerV = 0.5 - piv[1]

        left = -bounds[0][0]
        right = 1 - bounds[0][1]
        top = 1 - bounds[1][1]
        bottom = -bounds[1][0]

        if pos == 'topLeft':
            pm.polyEditUV(uvs.uvs, u=left, v=top)
        if pos == 'topCenter':
            pm.polyEditUV(uvs.uvs, u=centerU, v=top)
        if pos == 'topRight':
            pm.polyEditUV(uvs.uvs, u=right, v=top)
        if pos == 'centerLeft':
            pm.polyEditUV(uvs.uvs, u=left, v=centerV)
        if pos == 'center':
            pm.polyEditUV(uvs.uvs, u=centerU, v=centerV)
        if pos == 'centerRight':
            pm.polyEditUV(uvs.uvs, u=right, v=centerV)
        if pos == 'bottomLeft':
            pm.polyEditUV(uvs.uvs, u=left, v=bottom)
        if pos =='bottomCenter':
            pm.polyEditUV(uvs.uvs, u=centerU, v=bottom)
        if pos == 'bottomRight':
            pm.polyEditUV(uvs.uvs, u=right, v=bottom)


class layoutUI(toolsUI):
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            layoutButton = pm.iconTextButton(image='layoutUV.png',
                                             ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kSelectFacesToMoveAnnot'),
                                             c=lambda *args: pm.mel.performPolyLayoutUV(0),
                                             commandRepeatable=True)
            pm.popupMenu(button=3, parent=layoutButton, pmc=lambda *args: pm.mel.performPolyLayoutUV(1))

            layoutUorV = pm.iconTextButton(image='layoutUV.png',  # FIXME new image
                                           ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kSelectFacesToMoveAnnot'),
                                           c=lambda *args: self.UorV(0),
                                           commandRepeatable=True)
            pm.popupMenu(button=3, parent=layoutUorV, pmc=lambda *args: self.UorV(1))

    def UorV(self, val):
        if val == 0:
            pass
        else:
            pass


class isolateUI(toolsUI):  # TODO
    def __init__(self, par, editor):
        self.editor = editor
        toolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            pm.iconTextCheckBox(image='uvIsolateSelect.png',
                                ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kToggleIsolateSelectModeAnnot'),
                                onc=lambda *args: self.setIsolate(True),
                                ofc=lambda *args: self.setIsolate(False))

            pm.iconTextButton(image='uvIsolateSelectReset.png',
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kRemoveAllUVsAnnot'),
                              c=lambda *args: pm.mel.textureEditorIsolateSelect(0),
                              commandRepeatable=True)

            pm.iconTextButton(image='uvIsolateSelectAdd.png',
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kAddSelectedUVsAnnot'),
                              c=lambda *args: pm.mel.textureEditorIsolateSelect(1),
                              commandRepeatable=True)

            pm.iconTextButton(image='uvIsolateSelectRemove.png',
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kRemoveSelectedUVsAnnot'),
                              c=lambda *args: pm.mel.textureEditorIsolateSelect(2),
                              commandRepeatable=True)

    def setIsolate(self, val):
        if val:
            pm.textureWindow(self.editor, e=True, useFaceGroup=True)
            pm.optionVar['textureWindowShaderFacesMode'] = 2
        else:
            pm.textureWindow(self.editor, e=True, useFaceGroup=False)
            pm.optionVar['textureWindowShaderFacesMode'] = 0



class manipUI(toolsUI):
    def __init__(self, par):
        toolsUI.__init__(self, par)
        with pm.columnLayout() as self.layout:
            with pm.rowLayout(nc=4):
                pm.floatField('uvEntryFieldU', precision=3, ed=True, width=46,
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kEnterValueTotransformInUAnnot'),
                              cc=lambda *args: pm.mel.textureWindowUVEntryCommand(1))

                pm.floatField('uvEntryFieldV', precision=3, ed=True, width=46,
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kEnterValueTotransformInVAnnot'),
                              cc=lambda *args: pm.mel.textureWindowEntryCommand(0))

                pm.iconTextButton(image1='uvUpdate.png',
                                  ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kRefreshUVValuesAnnot'),
                                  c=self.uvUpdate,
                                  commandRepeatable=True)

                pm.iconTextCheckBox('uvEntryTransformModeButton', image1='uvEntryToggle.png',
                                    ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUVTransformationEntryAnnot'),
                                    value=pm.melGlobals['gUVEntryTransformMode'],
                                    onc=lambda *args: pm.mel.uvEntryTransformModeCommand(),
                                    ofc=lambda *args: pm.mel.uvEntryTransformModeCommand())

            with pm.rowLayout(nc=6):
                copyUV = pm.iconTextButton('copyUVButton', image1='copyUV.png',
                                           ann=pm.mel.getRunTimeCommandAnnotation('PolygonCopy'),
                                           c=lambda *args: pm.mel.PolygonCopy())
                pm.popupMenu('copyUVButtonPopup', button=3, p=copyUV, pmc=lambda *args: pm.mel.PolygonCopyOptions())

                pasteUV = pm.iconTextButton('pasteUVButton', image1='pasteUV.png',
                                            ann=pm.mel.getRunTimeCommandAnnotation('PolygonPaste'),
                                            c=lambda *args: pm.mel.PolygonPaste())
                pm.popupMenu('pasteUVButtonPopup', button=3, p=pasteUV, pmc=lambda *args: pm.mel.PolygonPasteOptions())

                pm.iconTextButton('pasteUButton', image1='pasteUDisabled.png', en=False,
                                  ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kPasteUValueAnnot'),
                                  c=lambda *args: pm.mel.textureWindowCreateToolBar_uvPaste(1, 0))

                pm.iconTextButton('pasteVButton', image1='pasteVDisabled.png', en=False,
                                  ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kPasteVValueAnnot'),
                                  c=lambda *args: pm.mel.textureWindowCreateToolBar_uvPaste(0, 1))

                pm.iconTextCheckBox(image1='copyUVMode.png',
                                    ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kToggleCopyPasteAnnot'),
                                    onc=lambda *args: pm.mel.textureWindowCreateToolBar_copyPasteMode(1),
                                    ofc=lambda *args: pm.mel.textureWindowCreateToolBar_copyPasteMode(0))

                pm.iconTextButton(image1='cycleUVs.png',
                                  ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kCycleUVsCounterClockwiseAnnot'),
                                  c=lambda *args: pm.mel.polyRotateUVsByVertex(),
                                  commandRepeatable=True)

    def uvUpdate(self):
        pm.undoInfo(swf=False)
        pm.mel.textureWindowCreateToolBar_isUVTransformed()
        pm.undoInfo(swf=True)


class opts01UI(toolsUI):
    def __init__(self, par, editor):
        self.editor = editor
        toolsUI.__init__(self, par)
        # with pm.gridLayout(p=par, nc=2, cwh=[46, 26]) as self.layout:
        with pm.columnLayout(p=par) as self.layout:
            with pm.rowLayout(nc=3):
                self.imageDisplay = pm.iconTextCheckBox('imageDisplayButton', image1='imageDisplay.png',
                                                        v=pm.textureWindow(self.editor, q=True, id=True),
                                                        cc=self.toggleImageDisplay,
                                                        ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kDisplayImageAnnot'))
                pm.popupMenu(button=3, p=self.imageDisplay, pmc=lambda *args: pm.mel.performTextureViewImageRangeOptions(1))

                self.edgeColorBtn = pm.iconTextButton(image1='pbUV/opts01EdgeColor.png', c=self.edgeColCmd)  # FIXME build new icon.
                self.edgeColSld = pm.intSlider(min=1, max=31, value=pm.displayColor('polymesh', q=True, active=True) + 1,
                                               dc=self.edgeColAttr)

            with pm.rowLayout(nc=3):
                pm.iconTextCheckBox(image1='filteredMode.png', v=pm.textureWindow(self.editor, q=True, iuf=True),
                                    onc=lambda *args: pm.textureWindow(self.editor, e=True, iuf=True),
                                    ofc=lambda *args: pm.textureWindow(self.editor, e=True, iuf=False),
                                ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kToggleFilteredImageAnnot'))

                self.dimImageBtn = pm.iconTextCheckBox('dimmerButton', image1='dimTexture.png',
                                                       ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kDimImageAnnot'),
                                                       onc=lambda *args: self.dimImageCmd(True),
                                                       ofc=lambda *args: self.dimImageCmd(False),
                                                       value=pm.textureWindow(self.editor, q=True, imageBaseColor=True) < 0.9)

                self.dimImage = pm.floatSlider(minValue=0.0, maxValue=1.0,
                                            value=pm.textureWindow(self.editor, q=True, imageBaseColor=True)[0],
                                            cc=self.dimImageAttr, dc=self.dimImageAttr)


    def toggleImageDisplay(self, *args):
        if pm.textureWindow(self.editor, q=True, id=True):
            pm.textureWindow(self.editor, e=True, id=False)
            self.imageDisplay.setValue(False)
        else:
            pm.textureWindow(self.editor, e=True, id=True)
            self.imageDisplay.setValue(True)

    def dimImageCmd(self, value):
        if value:
            pm.textureWindow(self.editor, e=True, imageBaseColor=[0.5, 0.5, 0.5])
            self.dimImage.setValue(0.5)
        else:
            pm.textureWindow(self.editor, e=True, imageBaseColor=[1.0, 1.0, 1.0])
            self.dimImage.setValue(1.0)

    def dimImageAttr(self, *args):
        val = self.dimImage.getValue()
        pm.textureWindow(self.editor, e=True, imageBaseColor=[val, val, val])

        if val < 0.99:
            self.dimImageBtn.setValue(True)
        else:
            self.dimImageBtn.setValue(False)

    def edgeColCmd(self, *args):
        pm.displayColor('polymesh', 16, active=True)
        self.edgeColSld.setValue(16)

    def edgeColAttr(self, *args):
        pm.displayColor('polymesh', self.edgeColSld.getValue(), active=True)


class opts02UI(toolsUI):
    def __init__(self, par, editor):
        self.editor = editor
        toolsUI.__init__(self, par)

        with pm.gridLayout(p=par, nc=3, cwh=[26, 26]) as self.layout:
            gridDisp = pm.iconTextCheckBox(image1='gridDisplay.png',
                                           value=pm.textureWindow(self.editor, q=True, toggle=True),
                                           onc=lambda *args: pm.textureWindow(self.editor, e=True, toggle=True),
                                           ofc=lambda *args: pm.textureWindow(self.editor, e=True, toggle=False),
                                           ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kViewGridAnnot'))
            pm.popupMenu(button=3, p=gridDisp, pmc=lambda *args: pm.mel.performTextureViewGridOptions(1))

            pxSnap = pm.iconTextCheckBox(image1='pixelSnap.png',
                                         value=pm.snapMode(q=True, pixelSnap=True),
                                         onc=lambda *args: pm.snapMode(pixelSnap=True),
                                         ofc=lambda *args: pm.snapMode(pixelSnap=False),
                                         ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kPixelSnapAnnot'))
            pm.popupMenu(button=3, p=pxSnap, pmc=lambda *args: pm.mel.performPixelSnapOptions(1))

            pm.iconTextCheckBox(image1='textureEditorShadeUVs.png',
                                value=pm.textureWindow(self.editor, q=True, displaySolidMap=True),
                                onc=lambda *args: pm.textureWindow(self.editor, e=True, displaySolidMap=True),
                                ofc=lambda *args: pm.textureWindow(self.editor, e=True, displaySolidMap=False),
                                ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kOverlapAnnot'))

            polyOpts = pm.iconTextButton(image1='textureBorder.png', c=self.toggleTxBorder,
                                         ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kToggleTextureBordersAnnot'))
            pm.popupMenu(button=3, p=polyOpts, pmc=lambda *args: pm.mel.CustomPolygonDisplayOptions())

            pm.iconTextButton(image1='textureEditorDisplayColor.png',
                              c=lambda *args: pm.textureWindow(self.editor, e=True, displayStyle='color'),
                              ann='m_textureWindowCreateToolBar.kDisplayRGBChannelsAnnot')

            pm.iconTextButton(image1='textureEditorDisplayAlpha.png',
                              c=lambda *args: pm.textureWindow(self.editor, e=True, displayStyle='mask'),
                              ann='m_textureWindowCreateToolBar.kDisplayAlphaChannelsAnnot')

    def toggleTxBorder(self, *args):
        if pm.polyOptions(q=True, displayMapBorder=True)[0]:
            pm.polyOptions(displayMapBorder=False)
        else:
            pm.polyOptions(displayMapBorder=True)


class opts03UI(toolsUI):
    def __init__(self, par, editor):
        toolsUI.__init__(self, par)
        self.editor = editor
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            swapBG = pm.iconTextCheckBox(image1='swapBG.png',
                                         value=pm.optionVar['displayEditorImage'],
                                         ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUVTextureEditorBakingAnnot'),
                                         cc=lambda *args: pm.mel.textureWindowToggleEditorImage(self.editor))
            pm.popupMenu(button=3, p=swapBG, pmc=lambda *arg: pm.mel.performTextureViewBakeTextureOptions(1))

            pm.iconTextButton(image1='updatePsdTextureEditor.png',
                                ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUpdatePSDNetworksAnnot'),
                                c=lambda *args: pm.mel.psdUpdateTextures(),
                                commandRepeatable=True)

            pm.iconTextButton(image1='bakeEditor.png',
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kForceEditorTextureRebakeAnnot'),
                              c=lambda *args: pm.mel.textureWindowBakeEditorImage(),
                              commandRepeatable=True)

            pm.iconTextCheckBox(image1='imageRatio.png',
                                ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUseImageRatioAnnot'),
                                value=pm.textureWindow(self.editor, q=True, imageRatio=True),
                                onc=lambda *args: pm.textureWindow(self.editor, e=True, imageRatio=True),
                                ofc=lambda *args: pm.textureWindow(self.editor, e=True, imageRatio=False))


# Data Classes
class UV(object):
    def __init__(self, uvs=None):
        if not uvs:
            self.uvs = pm.ls(pm.polyListComponentConversion(tuv=True), fl=True)
        else:
            self.uvs = uvs

        self.shells = []
        self.type = 'standard'

    def __repr__(self):
        return repr(self.uvs)

    def getBounds(self):
        self.bounds = pm.polyEvaluate(self.uvs, bc2=True)
        self.xMin = self.bounds[0][0]
        self.xMax = self.bounds[0][1]
        self.yMin = self.bounds[1][0]
        self.yMax = self.bounds[1][1]
        return self.bounds

    def getPivot(self):
        piv = pm.polyEvaluate(self.uvs, bc2=True)
        pivU = ((piv[0][0] + piv[0][1]) * 0.5)
        pivV = ((piv[1][0] + piv[1][1]) * 0.5)
        return pivU, pivV

    def getShells(self):
        if len(self.shells):
            pm.warning('Class is already a shell')
            return

        curSel = pm.selected()
        self.shells = []
        for uv in self.uvs:
            found = False
            for shell in self.shells:
                if uv in shell.uvs:
                    found = True
            if not found:
                pm.select(uv)
                pm.mel.polySelectBorderShell(0)
                sel = pm.ls(pm.polyListComponentConversion(tuv=True), fl=True)
                thisShell = UV(sel)
                thisShell.getBounds()

                self.shells.append(thisShell)

        pm.select(curSel)
        return self.shells
