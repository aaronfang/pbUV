from pymel.util.common import path
import math
import os
import pymel.core as pm


# Decorators
def move_fix(function):
    """
    Fix "Some items cannot be moved in the 3D view" Warning
    """

    def decorated_function(*args, **kwargs):
        currenttool = pm.currentCtx()
        selecttool = pm.melGlobals['gSelect']
        if currenttool != selecttool:
            pm.setToolTo(selecttool)
            function(*args, **kwargs)
            pm.setToolTo(currenttool)
        else:
            function(*args, **kwargs)

    return decorated_function


class UI(object):
    def __init__(self):
        title = 'pbUV'
        ver = '1.00'

        if pm.window('pbUV', exists=True):
            pm.deleteUI('pbUV')

        window = pm.window('pbUV', s=True, title='{0} | {1}'.format(title, ver))

        try:
            pane = pm.paneLayout('textureEditorPanel', paneSize=[1, 1, 1], cn='vertical2', swp=1)
        except:
            pane = pm.paneLayout('textureEditorPanel', paneSize=[1, 1, 1], cn='vertical2')

        uvtextureviews = pm.getPanel(scriptType='polyTexturePlacementPanel')
        if len(uvtextureviews):
            pm.scriptedPanel(uvtextureviews[0], e=True, unParent=True)

        with pm.columnLayout(p=pane):
            TransformUI()
            opts = GlobalOptions()
            SetEditorUI()
            DensityUI(opts)
            SnapshotUI(opts)

        pm.scriptedPanel(uvtextureviews[0], e=True, parent=pane)

        # Replace Default UV Editor Toolbar
        flowlayout = pm.melGlobals['gUVTexEditToolBar']
        framelayout = pm.flowLayout(flowlayout, q=True, p=True)
        framelayout = pm.uitypes.FrameLayout(framelayout)
        pm.deleteUI(flowlayout)

        flowlayout = pm.flowLayout(p=framelayout)
        Tools01UI(flowlayout)
        CutSewUI(flowlayout)
        UnfoldUI(flowlayout)
        AlignUI(flowlayout)
        PushUI(flowlayout)
        SnapUI(flowlayout)
        LayoutUI(flowlayout)
        IsolateUI(flowlayout, uvtextureviews[0])
        Opts01UI(flowlayout, uvtextureviews[0])
        Opts02UI(flowlayout, uvtextureviews[0])
        Opts03UI(flowlayout, uvtextureviews[0])
        ManipUI(flowlayout)

        window.show()

    @staticmethod
    def dump_settings():
        pass

    @staticmethod
    def load_settings():
        pass


class GlobalOptions(object):
    def __init__(self):
        respresets = [4096, 2048, 1024, 512, 256, 128, 64, 32]
        with pm.frameLayout(l='Options', cll=True, cl=False, bs='out'):
            with pm.columnLayout():
                pm.text('Map Size:')
                pm.separator(st='in', width=160, height=8)
                with pm.rowColumnLayout(nc=3, cw=[20, 60]):
                    pm.text(l='Width:')
                    self.width = pm.intField(v=1024, width=42)
                    with pm.optionMenu():
                        for i in respresets:
                            pm.menuItem(l=i)
                    pm.text(l='Height:')
                    self.height = pm.intField(v=1024, width=42)
                    with pm.optionMenu():
                        for i in respresets:
                            pm.menuItem(l=i)
                pm.button(l='Get Map Size')

                pm.separator(st='in', width=160, height=8)
                with pm.columnLayout():
                    self.compSpace = pm.checkBox(l='Retain Component Spaceing',
                                                 cc=lambda *args: pm.texMoveContext('texMoveContext', e=True,
                                                                                    scr=self.compSpace.getValue()),
                                                 v=pm.texMoveContext('texMoveContext', q=True, scr=True))
                    self.pixelUnits = pm.checkBox(l='Transform In Pixels')


class TransformUI(object):
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

                    flipuv = pm.iconTextButton(image1='pbUV/tFlipUV.png', c=lambda *args: self.flip(axis='u'),
                                               commandRepeatable=True)
                    pm.popupMenu(button=3, p=flipuv, pmc=lambda *args: self.flip(axis='v'))
                    pm.iconTextButton(image1='pbUV/tTranslateLeft.png', c=lambda *args: self.move(u=-1),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tTranslateDown.png', c=lambda *args: self.move(v=-1),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tTranslateRight.png', c=lambda *args: self.move(u=1),
                                      commandRepeatable=True)
                    pm.iconTextButton(image1='pbUV/tRot180CCW.png', c=lambda *args: self.rotate(angle=180, dir='ccw'),
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
                    pm.button(l='Orient Edge', c=self.orient_edge)
                    pm.button(l='Orient Bounds', c=self.orient_bounds)

                pm.separator(st='in', width=160, height=8)

                with pm.columnLayout(cal='left'):
                    pm.text(l='Pivot:')
                    self.pivType = pm.radioButtonGrp(nrb=2, labelArray2=['Selection', 'Custom'], cw2=[64, 64],
                                                     cc=self._piv_change, sl=1)
                    with pm.rowLayout(nc=3, en=False) as self.pivPos:
                        pm.text('POS:')
                        self.pivU = pm.floatField()
                        self.pivV = pm.floatField()
                    self.sampleSel = pm.button(l='Sample Selection', height=18, en=False, c=self.sample_sel_cmd)

    def _piv_change(self, *args):
        if self.pivType.getSelect() == 1:
            self.pivPos.setEnable(False)
            self.sampleSel.setEnable(False)
        else:
            self.pivPos.setEnable(True)
            self.sampleSel.setEnable(True)

    def piv_loc(self, *args):
        if self.pivType.getSelect() == 1:
            uvs = UV()
            return uvs.get_pivot()
        else:
            return self.pivU.getValue(), self.pivV.getValue()

    def sample_sel_cmd(self, *args):
        uvs = UV()
        piv = uvs.get_pivot()
        self.pivU.setValue(piv[0])
        self.pivV.setValue(piv[1])

    @move_fix
    def move(self, u=0, v=0):
        pm.polyEditUV(uValue=self.manipValue.getValue() * u, vValue=self.manipValue.getValue() * v)

    def rotate(self, angle=None, dir='ccw'):
        if angle is None:
            angle = self.manipValue.getValue()

        if dir == 'ccw':
            dir = 1
        elif dir == 'cw':
            dir = -1

        pm.polyEditUV(pu=self.piv_loc()[0], pv=self.piv_loc()[1], angle=angle * dir)

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

        pm.polyEditUV(pu=self.piv_loc()[0], pv=self.piv_loc()[1], su=u, sv=v)

    def flip(self, axis='u'):
        if axis == 'u':
            u = -1
            v = 1
        elif axis == 'v':
            u = 1
            v = -1

        pm.polyEditUV(pu=self.piv_loc()[0], scaleU=u, scaleV=v)

    def orient_edge(self, *args):  # FIXME
        pass

    def orient_bounds(self, *args):  # FIXME
        pass


class SetEditorUI(object):
    def __init__(self):
        with pm.frameLayout(l='Set Editor:', cll=True, cl=False, bs='out') as setUI:
            with pm.columnLayout(width=162):
                self.uvs = pm.textScrollList(w=160, h=72,
                                             sc=self.select_set,
                                             dcc=self.rename_set,
                                             dkc=self.delete_set)
                self.update_sets()

                with pm.rowLayout(nc=3):
                    pm.button(l='New', c=self.add_set)
                    pm.button(l='Copy', c=self.dup_set)
                    pm.button(l='UV Linking', c=lambda *args: pm.mel.UVCentricUVLinkingEditor())

        pm.scriptJob(event=['SelectionChanged', self.update_sets], protected=True, p=setUI)

    def update_sets(self, *args):
        self.uvs.removeAll()
        sel = pm.selected()

        if all(isinstance(i, pm.nt.Transform) for i in sel):
            sel = [i.getShape() for i in sel]

        elif all(isinstance(i, pm.Component) for i in sel):
            sel = [sel[0].node()]

        try:
            uvsets = []
            for obj in sel:
                for uvSet in obj.getUVSetNames():
                    uvsets.append('{0} | {1}'.format(obj.getParent(), uvSet))
            self.uvs.append(uvsets)
        except:
            pass

        # Select Current UV Set
        try:
            self.uvs.setSelectItem('{0} | {1}'.format(sel[0].getParent(), sel[0].getCurrentUVSetName()))
        except:
            pass

    def select_set(self, *args):
        uvset = self.uvs.getSelectItem()[0].split(' | ')
        pm.polyUVSet(uvset[0], currentUVSet=True, uvSet=uvset[1])

    def rename_set(self, *args):
        bdialog = pm.promptDialog(title='Rename UVSet',
                                  message='Enter New UvSet Name:',
                                  button=['OK', 'Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        if bdialog == 'OK':
            uvSet = self.uvs.getSelectItem()[0].split(' | ')
            pm.polyUVSet(uvSet[0], rename=True, uvSet=uvSet[1], newUVSet=pm.promptDialog(q=True, text=True))
            self.update_sets()

    def delete_set(self, *args):
        uvset = self.uvs.getSelectItem()[0].split(' | ')
        try:
            pm.polyUVSet(uvset[0], delete=True, uvSet=uvset[1])
            self.update_sets()
        except RuntimeError:
            pm.warning('The defualt uv set cannot be deleted.')
            self.update_sets()

    def add_set(self, *args):
        uvset = self.uvs.getSelectItem()[0].split(' | ')
        bdialog = pm.promptDialog(title='Add New UVSet',
                                  message='Enter New UVSet Name:',
                                  button=['OK', 'Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        if bdialog == 'OK':
            pm.polyUVSet(uvset[0], create=True, uvSet=pm.promptDialog(q=True, text=True))
            self.update_sets()

    def dup_set(self, *args):
        uvset = self.uvs.getSelectItem()[0].split(' | ')
        bdialog = pm.promptDialog(title='Duplicate UVSet',
                                  message='Enter New UVSet Name:',
                                  button=['OK', 'Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        if bdialog == 'OK':
            pm.polyUVSet(uvset[0], copy=True, uvSet=uvset[1], newUVSet=pm.promptDialog(q=True, text=True))
            self.update_sets()


class DensityUI(object):
    def __init__(self, opts):
        self.opts = opts
        with pm.frameLayout(l='Texel Density:', cll=True, cl=False, bs='out'):
            with pm.columnLayout(width=162):
                with pm.rowLayout(nc=2):
                    pm.text(l='Pixels Per Unit:')
                    self.texelDensity = pm.floatField(v=1)

                with pm.rowColumnLayout(nc=2):
                    pm.button(l='Set Density', c=self.set_density)
                    pm.button(l='Sample Density', c=self.sample_density)

    def set_density(self, *args):
        sel = pm.selected()

        for i in sel:
            txscale = self.texelDensity.getValue() / self.opts.width.getValue()
            pm.unfold(i, i=0, us=True, applyToShell=False, s=txscale)

    def sample_density(self, *args):
        sel = pm.ls(pm.polyListComponentConversion(pm.selected(), tf=True), fl=True)

        ratios = []
        for i in sel:
            ratios.append(math.sqrt(i.getUVArea() / i.getArea()))
        ratio = (sum(ratios) / len(sel)) * self.opts.width.getValue()
        self.texelDensity.setValue(ratio)


class SnapshotUI(object):
    def __init__(self, opts):
        self.opts = opts
        with pm.frameLayout(l='UV Snapshot:', cll=True, cl=False, bs='out'):
            with pm.columnLayout(width=162):
                self.path = pm.textFieldButtonGrp(l='Path:', bl='...', cw3=[28, 104, 32], bc=self.set_path)
                self.col = pm.colorSliderGrp(l='Color:', cw3=[32, 48, 74])
                with pm.rowLayout(nc=2):
                    self.of = pm.checkBox(l='Open File')
                    self.aa = pm.checkBox(l='Anti-Alias', v=True)
                pm.button(l='Save Snapshot', width=156, c=self.snap_shot)

    def set_path(self, *args):
        snappath = pm.fileDialog2(fm=0, okc='Save', ff='Targa (*.tga);;PNG (*.png);;JPEG (*.jpg);;TIFF (*.tif)')
        if snappath:
            self.path.setText(snappath[0])

    def snap_shot(self, *args):
        snappath = path(self.path.getText())
        col = [i * 255 for i in self.col.getRgbValue()]

        pm.uvSnapshot(name=snappath, ff=snappath.ext[1:],
                      aa=self.aa.getValue(), r=col[0], g=col[1], b=col[2], o=True,
                      xr=self.opts.width.getValue(), yr=self.opts.height.getValue())

        if self.of.getValue():
            os.startfile(snappath)


# ToolBar UI Stuff
class ToolsUI(object):
    def __init__(self, par):
        self.sep = pm.iconTextButton(image1='textureEditorOpenBar.png', p=par, c=self.toggle_visible)

    def toggle_visible(self, *args):
        if self.layout.getVisible():
            self.layout.setVisible(False)
            self.sep.setImage1('textureEditorCloseBar.png')
        else:
            self.layout.setVisible(True)
            self.sep.setImage1('textureEditorOpenBar.png')


class Tools01UI(ToolsUI):
    def __init__(self, par):
        ToolsUI.__init__(self, par)
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


class CutSewUI(ToolsUI):
    def __init__(self, par):
        ToolsUI.__init__(self, par)
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
                              c=self.tear_face,
                              commandRepeatable=True)

            sewuv = pm.iconTextButton(image1='sew_uv.png',
                                      c=self.sew_uv, commandRepeatable=True,
                                      ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kSewSelectedUVsTogetherAnnot'))
            pm.popupMenu(button=3, p=sewuv, pmc=lambda *args: pm.mel.performPolyMergeUV(1))

            movesewuv = pm.iconTextButton(image1='moveSewUV.png',
                                          c=lambda *args: pm.mel.performPolyMapSewMove(0),
                                          commandRepeatable=True,
                                          ann=pm.mel.uiRes(
                                              'm_textureWindowCreateToolBar.kMoveAndSewSelectedEdgesAnnot'))
            pm.popupMenu(button=3, p=movesewuv, pmc=lambda *args: pm.mel.performPolyMapSewMove(1))

    def sew_uv(self):  # FIXME
        edges = pm.filterExpand(ex=False, selectionMask=32)
        uvs = pm.filterExpand(ex=False, selectionMask=35)
        if edges:
            pm.polyMapSew()
        if uvs:
            pm.mel.performPolyMergeUV(0)

    def tear_face(self):
        sel = pm.selected()
        movetool = pm.melGlobals['gMove']
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
            pm.setToolTo(movetool)


class UnfoldUI(ToolsUI):
    def __init__(self, par):
        ToolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            unfold = pm.iconTextButton(image1='textureEditorUnfoldUVs.png',
                                       ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUnfoldAnnot'),
                                       c=lambda *args: pm.mel.performUnfold(0),
                                       commandRepeatable=True)
            pm.popupMenu(button=3, p=unfold, pmc=lambda *args: pm.mel.performUnfold(1))

            unfoldsep = pm.iconTextButton(image1='textureEditorUnfoldUVs.png',
                                          ann='Unfold selected UVs along U or V',
                                          c=lambda *args: self.unfold_sep_cmd(2))
            pm.popupMenu(button=3, p=unfoldsep, pmc=lambda *args: self.unfold_sep_cmd(1))

            relaxuv = pm.iconTextButton(image1='relaxUV.png',
                                        ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kRelaxUVsAnnot'),
                                        c=lambda *args: pm.mel.performPolyUntangleUV('relax', 0))
            pm.popupMenu(button=3, p=relaxuv, pmc=lambda *args: pm.mel.performPolyUntangleUV('relax', 1))

            pm.iconTextButton(image='Null',
                              c=lambda *args: self.match_shell(0.01),  # FIXME maxRange stuff
                              commandRepeatable=True,
                              ann='Match Selected Shell to closest Shell')

    def unfold_sep_cmd(self, axis):
        pm.unfold(i=pm.optionVar['unfoldIterations'],
                  ss=pm.optionVar['unfoldStopThreshold'],
                  gb=pm.optionVar['unfoldGlobalBlend'],
                  gmb=pm.optionVar['unfoldGlobalMethodBlend'],
                  pub=pm.optionVar['unfoldPinBorder'],
                  ps=pm.optionVar['unfoldPinSelected'],
                  oa=axis,
                  useScale=False)

    def match_shell(self, maxrange):  # FIXME MAX Range set

        snapuvs = pm.ls(pm.polyListComponentConversion(tuv=True), sl=True, fl=True)  # getUVs to match

        objs = [i.getShape() for i in pm.ls(hl=True, fl=True)]
        alluvs = pm.ls(pm.polyListComponentConversion(objs, tuv=True), fl=True)
        alluvs = sorted(set(alluvs) - set(snapuvs))  # get all uvs and subtract from snap uvs

        snappos = [pm.polyEditUV(i, q=True) for i in snapuvs]  # Get pos for snap and all
        allpos = [pm.polyEditUV(i, q=True) for i in alluvs]

        for i in range(len(snapuvs)):
            inrange = []
            for j in range(len(alluvs)):
                x = snappos[i][0] - allpos[j][0]
                y = snappos[i][1] - allpos[j][1]
                dist = math.sqrt((x ** 2) + (y ** 2))
                if dist < maxrange:
                    inrange.append((allpos[j], dist))

            if inrange:
                inrange = min(inrange, key=lambda x: x[1])
                pm.polyEditUV(snapuvs[i], u=inrange[0][0], v=inrange[0][1], r=False)


class AlignUI(ToolsUI):
    def __init__(self, par):
        ToolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[26, 26]) as self.layout:
            pm.iconTextButton(image1='NS_alUVleft.bmp',
                              c=lambda *args: self.align_shells('left'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVCenterU.bmp',
                              c=lambda *args: self.align_shells('centerU'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVRight.bmp',
                              c=lambda *args: self.align_shells('right'),
                              commandRepeatable=True)

            pm.iconTextButton(image1='NS_alUVTop.bmp',
                              c=lambda *args: self.align_shells('top'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVCenterV.bmp',
                              c=lambda *args: self.align_shells('centerV'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_alUVBottom.bmp',
                              c=lambda *args: self.align_shells('bottom'),
                              commandRepeatable=True)

    @move_fix
    def align_shells(self, align):
        sel = UV()
        sel.get_shells()

        shellsuvs = []
        for shell in sel.shells:
            for uv in shell.uvs:
                shellsuvs.append(uv)

        alluvs = UV(shellsuvs)
        alluvs.get_bounds()

        for shell in sel.shells:
            if align == 'left':
                pm.polyEditUV(shell.uvs, u=alluvs.xMin - shell.xMin)
            elif align == 'centerU':
                pm.polyEditUV(shell.uvs, u=(alluvs.xMin + alluvs.xMax) / 2 - (shell.xMax + shell.xMin) / 2)
            elif align == 'right':
                pm.polyEditUV(shell.uvs, u=alluvs.xMin - shell.xMin)

            elif align == 'top':
                pm.polyEditUV(shell.uvs, v=alluvs.yMax - shell.yMax)
            elif align == 'centerV':
                pm.polyEditUV(shell.uvs, v=(alluvs.yMin + alluvs.yMax) / 2 - (shell.yMax + shell.xMin) / 2)
            elif align == 'bottom':
                pm.polyEditUV(shell.uvs, v=alluvs.yMin - shell.yMin)


class PushUI(ToolsUI):  # FIXME Annotations
    def __init__(self, par):
        ToolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[26, 26]) as self.layout:
            pm.iconTextButton(image1='pbUV/pushMinU.png',
                              c=lambda *args: pm.mel.alignUV(1, 1, 0, 0),
                              commandRepeatable=True)
            pm.iconTextButton(image1='pbUV/pushCenterU.png',
                              c=lambda *args: self.push_average('u'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='pbUV/pushMaxU.png',
                              c=lambda *args: pm.mel.alignUV(1, 0, 0, 0),
                              commandRepeatable=True)

            pm.iconTextButton(image1='pbUV/pushMaxV.png',
                              c=lambda *args: pm.mel.alignUV(0, 0, 1, 0),
                              commandRepeatable=True)
            pm.iconTextButton(image1='pbUV/pushCenterV.png',
                              c=lambda *args: self.push_average('v'))
            pm.iconTextButton(image1='pbUV/pushMaxV.png',
                              c=lambda *args: pm.mel.alignUV(0, 0, 1, 1),
                              commandRepeatable=True)

    def push_average(self, dir):
        uvs = UV()
        center = uvs.get_pivot()
        if dir == 'u':
            pm.polyEditUV(uvs.uvs, r=False, u=center[0])
        if dir == 'v':
            pm.polyEditUV(uvs.uvs, r=False, v=center[1])


class SnapUI(ToolsUI):
    def __init__(self, par):
        ToolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=3, cwh=[18, 18]) as self.layout:  # FIXME new icons, and annotations
            pm.iconTextButton(image1='NS_snapTopLeft.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('topLeft'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapTop.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('topCenter'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapTopRight.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('topRight'),
                              commandRepeatable=True)

            pm.iconTextButton(image1='NS_snapLeft.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('centerLeft'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapCenter.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('center'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapRight.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('centerRight'),
                              commandRepeatable=True)

            pm.iconTextButton(image1='NS_snapBottomLeft.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('bottomLeft'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapBottom.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('bottomCenter'),
                              commandRepeatable=True)
            pm.iconTextButton(image1='NS_snapBottomRight.bmp', width=16, height=16,
                              c=lambda *args: self.snap_uvs('bottomRight'),
                              commandRepeatable=True)

    def snap_uvs(self, pos):
        uvs = UV()

        piv = uvs.get_pivot()
        bounds = uvs.get_bounds()
        centeru = 0.5 - piv[0]
        centerv = 0.5 - piv[1]

        left = -bounds[0][0]
        right = 1 - bounds[0][1]
        top = 1 - bounds[1][1]
        bottom = -bounds[1][0]

        if pos == 'topLeft':
            pm.polyEditUV(uvs.uvs, u=left, v=top)
        if pos == 'topCenter':
            pm.polyEditUV(uvs.uvs, u=centeru, v=top)
        if pos == 'topRight':
            pm.polyEditUV(uvs.uvs, u=right, v=top)
        if pos == 'centerLeft':
            pm.polyEditUV(uvs.uvs, u=left, v=centerv)
        if pos == 'center':
            pm.polyEditUV(uvs.uvs, u=centeru, v=centerv)
        if pos == 'centerRight':
            pm.polyEditUV(uvs.uvs, u=right, v=centerv)
        if pos == 'bottomLeft':
            pm.polyEditUV(uvs.uvs, u=left, v=bottom)
        if pos == 'bottomCenter':
            pm.polyEditUV(uvs.uvs, u=centeru, v=bottom)
        if pos == 'bottomRight':
            pm.polyEditUV(uvs.uvs, u=right, v=bottom)


class LayoutUI(ToolsUI):
    def __init__(self, par):
        ToolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            layoutbutton = pm.iconTextButton(image='layoutUV.png',
                                             ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kSelectFacesToMoveAnnot'),
                                             c=lambda *args: pm.mel.performPolyLayoutUV(0),
                                             commandRepeatable=True)
            pm.popupMenu(button=3, parent=layoutbutton, pmc=lambda *args: pm.mel.performPolyLayoutUV(1))

            layout_u_or_v = pm.iconTextButton(image='layoutUV.png',  # FIXME new image
                                              ann='Select Faces to be moved in U or V Space',
                                              c=lambda *args: self.u_or_v(0),
                                              commandRepeatable=True)
            pm.popupMenu(button=3, parent=layout_u_or_v, pmc=lambda *args: self.u_or_v(1))

    def u_or_v(self, val):  # FIXME
        if val == 0:
            pass
        else:
            pass


class IsolateUI(ToolsUI):
    def __init__(self, par, editor):
        self.editor = editor
        ToolsUI.__init__(self, par)
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            pm.iconTextCheckBox(image='uvIsolateSelect.png',
                                ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kToggleIsolateSelectModeAnnot'),
                                onc=lambda *args: self.set_isolate(True),
                                ofc=lambda *args: self.set_isolate(False))

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

    def set_isolate(self, val):
        if val:
            pm.textureWindow(self.editor, e=True, useFaceGroup=True)
            pm.optionVar['textureWindowShaderFacesMode'] = 2
        else:
            pm.textureWindow(self.editor, e=True, useFaceGroup=False)
            pm.optionVar['textureWindowShaderFacesMode'] = 0


class ManipUI(ToolsUI):
    def __init__(self, par):
        ToolsUI.__init__(self, par)
        with pm.columnLayout() as self.layout:
            with pm.rowLayout(nc=4):
                pm.floatField('uvEntryFieldU', precision=3, ed=True, width=46,
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kEnterValueTotransformInUAnnot'),
                              cc=lambda *args: pm.mel.textureWindowUVEntryCommand(1))

                pm.floatField('uvEntryFieldV', precision=3, ed=True, width=46,
                              ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kEnterValueTotransformInVAnnot'),
                              cc=lambda *args: pm.mel.textureWindowEntryCommand(0))

                pm.iconTextButton(image1='uv_update.png',
                                  ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kRefreshUVValuesAnnot'),
                                  c=self.uv_update,
                                  commandRepeatable=True)

                pm.iconTextCheckBox('uvEntryTransformModeButton', image1='uvEntryToggle.png',
                                    ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUVTransformationEntryAnnot'),
                                    value=pm.melGlobals['gUVEntryTransformMode'],
                                    onc=lambda *args: pm.mel.uvEntryTransformModeCommand(),
                                    ofc=lambda *args: pm.mel.uvEntryTransformModeCommand())

            with pm.rowLayout(nc=6):
                copyuv = pm.iconTextButton('copyUVButton', image1='copyUV.png',
                                           ann=pm.mel.getRunTimeCommandAnnotation('PolygonCopy'),
                                           c=lambda *args: pm.mel.PolygonCopy())
                pm.popupMenu('copyUVButtonPopup', button=3, p=copyuv, pmc=lambda *args: pm.mel.PolygonCopyOptions())

                pasteuv = pm.iconTextButton('pasteUVButton', image1='pasteUV.png',
                                            ann=pm.mel.getRunTimeCommandAnnotation('PolygonPaste'),
                                            c=lambda *args: pm.mel.PolygonPaste())
                pm.popupMenu('pasteUVButtonPopup', button=3, p=pasteuv, pmc=lambda *args: pm.mel.PolygonPasteOptions())

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

    def uv_update(self):
        pm.undoInfo(swf=False)
        pm.mel.textureWindowCreateToolBar_isUVTransformed()
        pm.undoInfo(swf=True)


class Opts01UI(ToolsUI):
    def __init__(self, par, editor):
        self.editor = editor
        ToolsUI.__init__(self, par)
        with pm.columnLayout(p=par) as self.layout:
            with pm.rowLayout(nc=4):
                self.imageDisplay = pm.iconTextCheckBox('imageDisplayButton', image1='imageDisplay.png',
                                                        v=pm.textureWindow(self.editor, q=True, id=True),
                                                        cc=self.toggle_image_display,
                                                        ann=pm.mel.uiRes(
                                                            'm_textureWindowCreateToolBar.kDisplayImageAnnot'))
                pm.popupMenu(button=3, p=self.imageDisplay,
                             pmc=lambda *args: pm.mel.performTextureViewImageRangeOptions(1))

                pm.iconTextCheckBox(image1='textureEditorShadeUVs.png',
                                    value=pm.textureWindow(self.editor, q=True, displaySolidMap=True),
                                    onc=lambda *args: pm.textureWindow(self.editor, e=True, displaySolidMap=True),
                                    ofc=lambda *args: pm.textureWindow(self.editor, e=True, displaySolidMap=False),
                                    ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kOverlapAnnot'))

                self.edgeColorBtn = pm.iconTextButton(image1='pbUV/opts01EdgeColor.png', c=self.edge_col_cmd)
                self.edgeColSld = pm.intSlider(min=1, max=31,
                                               value=pm.displayColor('polymesh', q=True, active=True) + 1,
                                               dc=self.edge_col_attr)

            with pm.rowLayout(nc=4):
                pm.iconTextCheckBox(image1='filteredMode.png', v=pm.textureWindow(self.editor, q=True, iuf=True),
                                    onc=lambda *args: pm.textureWindow(self.editor, e=True, iuf=True),
                                    ofc=lambda *args: pm.textureWindow(self.editor, e=True, iuf=False),
                                    ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kToggleFilteredImageAnnot'))

                polyOpts = pm.iconTextButton(image1='textureBorder.png', c=self.toggle_tx_border,
                                             ann=pm.mel.uiRes(
                                                 'm_textureWindowCreateToolBar.kToggleTextureBordersAnnot'))
                pm.popupMenu(button=3, p=polyOpts, pmc=lambda *args: pm.mel.CustomPolygonDisplayOptions())

                self.dimImageBtn = pm.iconTextCheckBox('dimmerButton', image1='dimTexture.png',
                                                       ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kDimImageAnnot'),
                                                       onc=lambda *args: self.dim_image_cmd(True),
                                                       ofc=lambda *args: self.dim_image_cmd(False),
                                                       value=pm.textureWindow(self.editor, q=True,
                                                                              imageBaseColor=True) < 0.9)

                self.dimImage = pm.floatSlider(minValue=0.0, maxValue=1.0,
                                               value=pm.textureWindow(self.editor, q=True, imageBaseColor=True)[0],
                                               cc=self.dim_image_attr, dc=self.dim_image_attr)

    def toggle_image_display(self, *args):
        if pm.textureWindow(self.editor, q=True, id=True):
            pm.textureWindow(self.editor, e=True, id=False)
            self.imageDisplay.setValue(False)
        else:
            pm.textureWindow(self.editor, e=True, id=True)
            self.imageDisplay.setValue(True)

    def dim_image_cmd(self, value):
        if value:
            pm.textureWindow(self.editor, e=True, imageBaseColor=[0.5, 0.5, 0.5])
            self.dimImage.setValue(0.5)
        else:
            pm.textureWindow(self.editor, e=True, imageBaseColor=[1.0, 1.0, 1.0])
            self.dimImage.setValue(1.0)

    def dim_image_attr(self, *args):
        val = self.dimImage.getValue()
        pm.textureWindow(self.editor, e=True, imageBaseColor=[val, val, val])

        if val < 0.99:
            self.dimImageBtn.setValue(True)
        else:
            self.dimImageBtn.setValue(False)

    def edge_col_cmd(self, *args):
        pm.displayColor('polymesh', 16, active=True)
        self.edgeColSld.setValue(16)

    def edge_col_attr(self, *args):
        pm.displayColor('polymesh', self.edgeColSld.getValue(), active=True)

    def toggle_tx_border(self, *args):
        if pm.polyOptions(q=True, displayMapBorder=True)[0]:
            pm.polyOptions(displayMapBorder=False)
        else:
            pm.polyOptions(displayMapBorder=True)


class Opts02UI(ToolsUI):
    def __init__(self, par, editor):
        self.editor = editor
        ToolsUI.__init__(self, par)

        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            griddisp = pm.iconTextCheckBox(image1='gridDisplay.png',
                                           value=pm.textureWindow(self.editor, q=True, toggle=True),
                                           onc=lambda *args: pm.textureWindow(self.editor, e=True, toggle=True),
                                           ofc=lambda *args: pm.textureWindow(self.editor, e=True, toggle=False),
                                           ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kViewGridAnnot'))
            pm.popupMenu(button=3, p=griddisp, pmc=lambda *args: pm.mel.performTextureViewGridOptions(1))

            pxsnap = pm.iconTextCheckBox(image1='pixelSnap.png',
                                         value=pm.snapMode(q=True, pixelSnap=True),
                                         onc=lambda *args: pm.snapMode(pixelSnap=True),
                                         ofc=lambda *args: pm.snapMode(pixelSnap=False),
                                         ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kPixelSnapAnnot'))
            pm.popupMenu(button=3, p=pxsnap, pmc=lambda *args: pm.mel.performPixelSnapOptions(1))

            pm.iconTextButton(image1='textureEditorDisplayColor.png',
                              c=lambda *args: pm.textureWindow(self.editor, e=True, displayStyle='color'),
                              ann='m_textureWindowCreateToolBar.kDisplayRGBChannelsAnnot')

            pm.iconTextButton(image1='textureEditorDisplayAlpha.png',
                              c=lambda *args: pm.textureWindow(self.editor, e=True, displayStyle='mask'),
                              ann='m_textureWindowCreateToolBar.kDisplayAlphaChannelsAnnot')


class Opts03UI(ToolsUI):
    def __init__(self, par, editor):
        ToolsUI.__init__(self, par)
        self.editor = editor
        with pm.gridLayout(p=par, nc=2, cwh=[26, 26]) as self.layout:
            swapbg = pm.iconTextCheckBox(image1='swapBG.png',
                                         value=pm.optionVar['displayEditorImage'],
                                         ann=pm.mel.uiRes('m_textureWindowCreateToolBar.kUVTextureEditorBakingAnnot'),
                                         cc=lambda *args: pm.mel.textureWindowToggleEditorImage(self.editor))
            pm.popupMenu(button=3, p=swapbg, pmc=lambda *arg: pm.mel.performTextureViewBakeTextureOptions(1))

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

    def get_bounds(self):
        self.bounds = pm.polyEvaluate(self.uvs, bc2=True)
        self.xMin = self.bounds[0][0]
        self.xMax = self.bounds[0][1]
        self.yMin = self.bounds[1][0]
        self.yMax = self.bounds[1][1]
        return self.bounds

    def get_pivot(self):
        piv = pm.polyEvaluate(self.uvs, bc2=True)
        pivu = ((piv[0][0] + piv[0][1]) * 0.5)
        pivv = ((piv[1][0] + piv[1][1]) * 0.5)
        return pivu, pivv

    def get_shells(self):
        if len(self.shells):
            pm.warning('Class is already a shell')
            return

        cursel = pm.selected()
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
                thisShell.get_bounds()

                self.shells.append(thisShell)

        pm.select(cursel)
        return self.shells
