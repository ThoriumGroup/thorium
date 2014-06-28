#!/usr/bin/env python
"""

Icon Panel
==========

A debug panel for Nuke that displays and provides location for every icon
in Nuke's icon folder.

## Classes

    IconPanel
        This is the icon panel itself, it displays the icon name, the icon
        itself, and the path to the icon for use.

## License

The MIT License (MIT)

iconPanel
Copyright (c) 2010-2011 Frank Rueter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Imports
from fnmatch import fnmatch
import os

# Nuke Imports
try:
    import nuke
    import nukescripts
except ImportError:
    pass

# =============================================================================
# GLOBALS
# =============================================================================

INTERNAL_ICONS = (
    'NukeApp.png', 'frame.png', 'SliderThumb.png', 'Eyedropper.png',
    'ArrowWhiteLeft.png', 'ArrowWhiteRight.png', 'arrow_left.png',
    'arrow_right.png', 'arrow_up.png', 'arrow_down.png', 'next.png',
    'previous.png', 'undo.png', 'redo.png', 'revert.png', 'Add.png',
    'Remove.png', 'TCStart.png', 'TCEnd.png', 'TCFrameBackward.png',
    'TCFrameForward.png', 'TCKeyBackward.png', 'TCKeyForward.png',
    'TCPlayBackward.png', 'TCPlayForward.png', 'TCStop.png',
    'TCIntervalBackward.png', 'TCIntervalForward.png', 'RangeBackward.png',
    'RangeForward.png', 'GroupShow.png', 'Disable.png', 'Cached.png',
    'HideInput.png', 'PostageStamp.png', 'Help.png', 'Bold.png', 'Italic.png',
    'File_Knob.png', 'Color_Knob.png', 'MultiView.png', 'SingleView.png',
    'Curve_Button.png', 'Color_Knob.png', 'SVG/VisibleCurrentFrame.svg',
    'SVG/MoveUpOne.svg', 'SVG/Reveal.svg', 'ShowStructure.png', 'select.png',
    'AxisIcon.png', 'FolderIcon.png', 'GeoSelect_Nodes_16x16.png',
    'GeoSelect_Vertices_16x16.png', 'GeoSelect_OcclusionTest_16x16.png',
    'show_points.png', 'show_point_num.png', 'show_point_info.png',
    'show_point_normals.png', 'show_point_uvs.png', 'show_vertex_num.png',
    'show_vertex_normals.png', 'show_vertex_uvs.png', 'show_prim_num.png',
    'show_prim_normals.png', 'show_prim_bbox.png', 'grid_display.png',
    'View.png', 'Lock.png', 'Unlock.png', 'Camera.png', 'Refresh.png',
    'ROI.png', 'Proxy.png', 'Pause.png', 'IP.png', 'zebra.png',
    'FrameRangeLock.png', 'FrameRangeUnlock.png', 'MonitorOut.png',
    'Toggle3DToolbar_16x16.png', 'Loop.png', 'Bounce.png', 'StopPlay.png',
    'Plugin.png', 'ToolbarImage.png', 'ToolbarDraw.png', 'ToolbarTime.png',
    'ToolbarChannel.png', 'ToolbarColor.png', 'Toolbar3DLUT.png',
    'ToolbarFilter.png', 'ToolbarKeyer.png', 'ToolbarMerge.png',
    'ToolbarTransform.png', 'Toolbar3D.png', 'Toolbar3DLights.png',
    'ToolbarViews.png', 'ToolbarStereo.png', 'ToolbarOther.png',
    'ToolbarOFX.png', 'AllPlugins.png', 'SVG/Eraser.svg', 'SVG/Selection.svg',
    'SVG/MoveToTop.svg', 'SVG/Paint.svg', 'CenterThisNode12p.png',
    'QuestionMark12p.png', 'SVG/VisibleSpecificRange.svg', 'SVG/Clone.svg',
    'SVG/MoveDownOne.svg', 'SVG/VisibleFromNowOn.svg', 'SVG/Key.svg',
    'SVG/UnlimitedLife.svg', 'SVG/MoveToBottom.svg',
    'SVG/VisibleUpTillNow.svg', 'ScriptEditor/clearHistory.png',
    'ScriptEditor/source.png', 'ScriptEditor/load.png',
    'ScriptEditor/save.png', 'ScriptEditor/run.png',
    'ScriptEditor/inputOn.png', 'ScriptEditor/inputOff.png',
    'ScriptEditor/outputOn.png', 'ScriptEditor/outputOff.png',
    'ScriptEditor/bothOn.png', 'ScriptEditor/bothOff.png',
    'ScriptEditor/clearOutput.png', 'ControlPanelBin/clear.png',
    'ControlPanelBin/lock.png', 'ControlPanelBin/unlock.png',
    'CursorTranslate.png', 'CursorRotateNW.png', 'CursorRotateNE.png',
    'CursorRotateSW.png', 'CursorRotateSE.png', 'CursorSizeAll.png',
    'CursorSkew.png', 'CursorMovePoint.png', 'CursorAddPoint.png',
    'CursorRemovePoint.png', 'CursorClosePath.png', 'CursorFeatherPoint.png',
    'CursorRemoveFeatherPoint.png', 'CursorSmoothPoint.png',
    'CursorCuspPoint.png', 'KeyLeft.png', 'KeyRight.png', 'KeyPlus.png',
    'KeyMinus.png', 'Brush.png', 'Roto/Curve.png', 'Roto/Shape.png',
    'Roto/Layer.png', 'Roto/BlendUnion.png', 'Roto/BlendIntersect.png',
    'Roto/BlendOver.png', 'Roto/BlendDarken.png', 'Roto/BlendMultiply.png',
    'Roto/BlendColorBurn.png', 'Roto/BlendLighten.png', 'Roto/BlendScreen.png',
    'Roto/BlendColorDodge.png', 'Roto/BlendAdd.png', 'Roto/BlendOverlay.png',
    'Roto/BlendSoftLight.png', 'Roto/BlendHardLight.png',
    'Roto/BlendDifference.png', 'Roto/BlendExclusion.png',
    'Roto/BlendFrom.png', 'Roto/BlendMinus.png', 'Roto/InvertOn.png',
    'Roto/InvertOff.png', 'Roto/MotionBlurOn.png', 'Roto/MotionBlurOff.png',
    'Roto/Visible.png', 'Roto/Invisible.png', 'Roto/Color.png',
    'Roto/OverlayColor.png', 'Roto/OverlayColor.png', 'Roto/SelectAllTool.png',
    'Roto/SelectCurvesTool.png', 'Roto/SelectPointsTool.png',
    'Roto/SelectFeatherPointsTool.png', 'Roto/BezierTool.png',
    'Roto/BSplineTool.png', 'Roto/EllipseTool.png', 'Roto/RectangleTool.png',
    'Roto/AddPointsTool.png', 'Roto/RemovePointsTool.png',
    'Roto/CuspPointsTool.png', 'Roto/CurvePointsTool.png',
    'Roto/RemoveFeatherTool.png', 'Roto/CloseCurveTool.png',
    'Roto/BrushTool.png', 'Roto/PencilTool.png', 'Roto/EraserTool.png',
    'Roto/CloneTool.png', 'Roto/RevealTool.png', 'Roto/BlurTool.png',
    'Roto/SharpenTool.png', 'Roto/SmearTool.png', 'Roto/DodgeTool.png',
    'Roto/BurnTool.png', 'Roto/LinkedFeather.png', 'Roto/UnlinkedFeather.png',
    'Roto/SingleKeyframe.png', 'Roto/RippleKeyframe.png',
    'Roto/ShowCurvesOnDrag.png', 'Roto/ShowPointsOnDrag.png',
    'Roto/ShowAllOnDrag.png', 'Roto/CurvePriority.png',
    'Roto/PointPriority.png', 'Roto/ShowTransformNone.png',
    'Roto/ShowTransformJack.png', 'Roto/ShowTransformBBox.png',
    'Roto/ShowTransformBoth.png', 'Roto/ShowPointNumbers.png',
    'Roto/UnlimitedLife.png', 'Roto/VisibleFromNowOn.png',
    'Roto/VisibleCurrentFrame.png', 'Roto/VisibleUpTillNow.png',
    'Roto/VisibleSpecificRange.png', 'Roto/CloneToolbar.png',
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'IconPanel'
]

# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


def _find_files(directory, pattern):
    """Searches a directory finding all files and dirs matching unix pattern.

    Args:
        directory : (str)
            The directory to search in.

        patterns : (str)
            A unix style pattern to search for. This should be the same style
             of pattern that fnmatch or glob would take, and not regex.

    Returns:
        [str]
            A list of file and directory names matching one of the patterns is
            returned. The file names are relative to the directory we were
            given.

    Raises:
        N/A

    """
    files = [item for item in os.listdir(directory) if fnmatch(item, pattern)]
    files.sort(key=lambda v: v.lower())

    return files

# =============================================================================
# CLASSES
# =============================================================================


class IconPanel(nukescripts.PythonPanel):
    """Displays the icon names, icons, and their paths"""

    def __init__(self):
        super(IconPanel, self).__init__(
            'Universal Icons',
            'com.thorium.IconPanel'
        )

        self.external_icons = self.find_file_icons()
        self.internal_icons = INTERNAL_ICONS
        self.batch = 30

        # We'll have two tabs up on top, one for External icons and one for
        # internal Icons
        # Inside each tab will be a bunch of subtabs, each containing about 30
        # icons.
        #
        # We accomplish this nested tabbing by starting and ending tab groups.
        # The top level tab group contains the External and Internal tabs,
        # then within each tab we'll start and end another tab group.
        self.addKnob(nuke.BeginTabGroup_Knob())

        # Build our external icons
        self.addKnob(nuke.Tab_Knob('external_icons', 'External Icons'))
        self.build_icon_list(
            self.external_icons,
            html_style=False,
            alpha_title=True
        )

        # Build our internal icons
        self.addKnob(nuke.Tab_Knob('internal_icons', 'Internal Icons'))
        self.build_icon_list(
            self.internal_icons,
            html_style=True
        )

        self.addKnob(nuke.EndTabGroup_Knob())

    # =========================================================================

    @staticmethod
    def build_icon_knob(icon, html_style=True, html_root=None):
        """Builds an individual icon knob

        Args:
            icon : (str)
                The icon filename relative to the external_icons directory.

            html_style=True : (bool)
                To use html <img src=""> code to link to the image, or use
                @ to find a relative image in Nuke's search path.

            html_root=None : (str)
                When using html style, the root to prepend to the icon.

        Returns:
            (<nuke.String_Knob>)
                A string knob with the filename and then the icon

        Raises:
            N/A

        """
        name = os.path.splitext(icon.split('/')[-1])[0]

        # HTML style vs @ style:
        # HTML style is used to bring in images that are not in Nuke's search
        # path, by explicitly linking to them (bad) or bring in images from
        # Nuke's built in images. We'll default to bringing in Nuke's built
        # in images, with :qrc/images/
        if html_style:
            html_root = html_root if html_root else ':qrc/images/'
            icon_string = '{name} <img src="{html_root}{icon}">'.format(
                name=name,
                html_root=html_root,
                icon=icon
            )
        else:
            icon_string = '{name} @{icon}'.format(
                name=name,
                icon=icon
            )

        icon_knob = nuke.String_Knob(icon, icon_string)
        icon_knob.setValue(icon_string)

        return icon_knob

    # =========================================================================

    def build_icon_list(self, icon_list, html_style=True, alpha_title=False):
        """Builds the panel list of icons"""
        # Start our tab group
        self.addKnob(nuke.BeginTabGroup_Knob())

        # Add all of our child icon knobs and tabs
        for i, icon in enumerate(icon_list):
            # Every time we hit the batch limit, we'll be creating a new tab
            counter = i % self.batch
            if counter == 0:
                tab_name = icon[:2].title() if alpha_title else str(i)
                tab = nuke.Tab_Knob(tab_name, tab_name)
                self.addKnob(tab)

            icon_knob = self.build_icon_knob(icon, html_style)
            self.addKnob(icon_knob)

        # End our tab group
        self.addKnob(nuke.EndTabGroup_Knob())

    # =========================================================================

    @staticmethod
    def find_file_icons():
        """Finds all the external_icons in the Nuke icon folder"""
        nuke_dir = os.path.split(nuke.EXE_PATH)[0]
        icon_path = os.path.join(nuke_dir, 'plugins/icons')
        icons = _find_files(icon_path, '*.png')

        return icons
