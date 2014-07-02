#!/usr/bin/env python
"""

Viewer Sync
===========

Contains the functions required for two views to be kept in sync.

## Public Functions

    remove_callback()
        Removes callback from all selected viewers and all viewers linked.

    setup_sync()
        Sets up a viewerSync between a group of Viewer nodes.

    sync_viewers()
        Syncs all the given viewers to the settings on the caller node.

## License

The MIT License (MIT)

iconPanel
Copyright (c) 2011-2014 Philippe Huberdeau and Sean Wallitsch

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
from ast import literal_eval

# Nuke Imports
try:
    import nuke
except ImportError:
    pass

# =============================================================================
# GLOBALS
# =============================================================================

# The specific text to display on the viewerSync knob for the listed
# viewer knob.
KNOB_TITLES = {
    'channels': 'channels',
    'cliptest': 'zebra-stripe',
    'downrez': 'proxy settings',
    'format_center': 'format center',
    'gain': 'gain',
    'gamma': 'gamma',
    'masking_mode': 'masking mode',
    'masking_ratio': 'masking ratio',
    'overscan': 'overscan',
    'ignore_pixel_aspect': 'ignore pixel aspect ratio',
    'input_number': 'viewed input',
    'input_process': 'input process on/off',
    'input_process_node': 'input process node',
    'inputs': 'input nodes',
    'rgb_only': 'LUT applies to rgb channels only',
    'roi': 'roi',
    'safe_zone': 'safe zone',
    'show_overscan': 'show overscan',
    'viewerInputOrder': 'input process order',
    'viewerProcess': 'LUT',
    'zoom_lock': 'zoom lock'
}

# These are tooltips for the viewerSync knobs, with the keys being the normal
# knob the viewerSync knob refers to.
KNOB_TOOLTIPS = {
    'channels': 'Sync the layers and alpha channel to display in the viewers. '
                'The "display style" is not synced.',
    'cliptest': 'Sync if zebra-striping is enabled or not between viewers.',
    'downrez': 'Sync the scale down factor for proxy mode. Proxy mode '
               'activation is always synced.',
    'format_center': 'Sync if a crosshair is displayed at the center of the '
                     'viewer window.',
    'gain': 'Sync the gain slider between viewers.',
    'gamma': 'Sync the gamma slider between viewers.',
    'masking_mode': 'Sync the mask style between viewers.',
    'masking_ratio': 'Sync the mask ratio selection between viewers.',
    'overscan': 'Sync the amount of overscan displayed between viewers.',
    'ignore_pixel_aspect': 'If selected all viewers will either show square '
                           'pixels or the pixel aspect ratio denoted by '
                           'the format.',
    'input_number': 'Syncs which input number is being viewed between all '
                    'viewers. This does not mean that all viewers are '
                    'viewing the same nodes, just that all viewers are '
                    'viewing input 1, etc.',
    'input_process': 'If selected all viewers will either have the input '
                     'process on, or off.',
    'input_process_node': 'Syncs what node is used as the input process '
                          'between all viewers.',
    'inputs': 'If selected, all viewers will point to the same nodes in the '
              'node graph.',
    'rgb_only': 'Syncs the "apply LUT to color channels only" knob, which '
                'indicates that the viewer will attempt to apply the lut to '
                'only the color channels. This only works with knobs that '
                'have an "rgb_only" knob, which is few.',
    'roi': 'Syncs the ROI window between all viewers. ROI needs to be manually '
           'activated for all viewers.',
    'safe_zone': 'Syncs the safe zone overlays between all viewers.',
    'show_overscan': 'If selected, all viewers will either show overscan or '
                     'not show overscan.',
    'viewerInputOrder': 'Syncs if the input process occurs before or after '
                        'the viewer process between all viewers.',
    'viewerProcess': 'Syncs the LUT between all viewers.',
    'zoom_lock': 'If selected, the zoom lock will apply to all viewers or '
                 'none.'
}

# The default values for a fresh viewerSync. Ideally these would be read from
# a savable config file.
SYNC_DEFAULTS = {
    'channels': False,
    'cliptest': True,
    'downrez': True,
    'format_center': True,
    'gain': False,
    'gamma': False,
    'masking_mode': True,
    'masking_ratio': True,
    'overscan': True,
    'ignore_pixel_aspect': True,
    'input_number': True,
    'input_process': True,
    'input_process_node': True,
    'inputs': False,
    'rgb_only': True,
    'roi': True,
    'safe_zone': True,
    'show_overscan': True,
    'viewerInputOrder': True,
    'viewerProcess': True,
    'zoom_lock': True
}

# List all viewerSync specific knobs.
# These knobs contain the bool values specifying if a normal viewer knob
# should be synced or not.
VIEWER_SYNC_KNOBS = [
    'vs_{knob}'.format(knob=sync_knob) for sync_knob in SYNC_DEFAULTS.keys()
]

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'remove_callbacks',
    'setup_sync',
    'sync_viewers',
]

# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


def _add_sync_knobs(viewer):
    """Adds the sync option knobs to the given given viewer node.

    If this gets called on a node that already has viewerSync knobs, those
    knobs will sync instead of being added again.

    Args:
        viewer : (<nuke.nodes.Viewer>)
            The Viewer node to add viewerSync knobs to.

    Returns:
        None

    Raises:
        N/A

    """
    if 'vs_options' in viewer.knobs():
        # This node already has a settings pane- we'll reset the settings to
        # default.
        for knob in SYNC_DEFAULTS:
            viewer['vs_' + knob].setValue(SYNC_DEFAULTS[knob])
        return

    tab = nuke.Tab_Knob('vs_options', 'Viewer Sync')
    viewer.addKnob(tab)

    def add_knobs(knob_list):
        """For every knob in the list, adds that knob to the current tab"""
        for knob in knob_list:
            new_knob = nuke.Boolean_Knob('vs_' + knob, KNOB_TITLES[knob])
            new_knob.setTooltip(KNOB_TOOLTIPS[knob])
            new_knob.setValue(SYNC_DEFAULTS[knob])
            new_knob.setFlag(nuke.STARTLINE)
            viewer.addKnob(new_knob)

    input_options = nuke.Text_Knob('vs_input_options', 'Input Options')
    viewer.addKnob(input_options)
    add_knobs(['inputs', 'input_number', 'channels'])

    display_options = nuke.Text_Knob('vs_display_options', 'Display Options')
    viewer.addKnob(display_options)
    add_knobs(
        [
            'viewerProcess', 'rgb_only', 'input_process',
            'input_process_node', 'viewerInputOrder', 'gain', 'gamma',
            'ignore_pixel_aspect', 'zoom_lock', 'show_overscan',
            'overscan'
        ]
    )

    overlay_options = nuke.Text_Knob('vs_overlay_options', 'Overlay Options')
    viewer.addKnob(overlay_options)
    add_knobs(
        [
            'masking_mode', 'masking_ratio', 'safe_zone',
            'format_center', 'cliptest'
        ]
    )

    process_options = nuke.Text_Knob('vs_process_options', 'Processing Options')
    viewer.addKnob(process_options)
    add_knobs(['downrez', 'roi'])

# =============================================================================


def _extract_viewer_list(viewer):
    """Extracts a list of Viewer nodes from a callback.

    Searches a viewer node for a viewerSync callback, and extracts the
    value of the `viewers` arg.

    Args:
        viewer : (<nuke.nodes.Viewer>)
            The viewer node with the callback attached.

    Returns:
        [<nuke.nodes.Viewer>]
            A list of viewer nodes that were listed in the callback arg.

    Raises:
        ValueError
            If the callback found on the viewer is present, but not for
            viewerSync.

    """
    callback = viewer['knobChanged'].value()

    if not callback:
        return []
    elif 'viewerSync' not in callback:
        raise ValueError("Not a viewerSync'd viewer.")

    callback = callback.replace('viewerSync.sync_viewers(', '')[:-1]
    linked_viewers = literal_eval(callback)
    viewer_nodes = [
        nuke.toNode(node) for node in linked_viewers if nuke.toNode(node)
    ]

    return viewer_nodes

# =============================================================================


def _remove_knobs(viewer):
    """Removes all viewerSync knobs from a viewer.

    Since this function only deletes knobs that begin with `vs_`, it should
    not raise any exceptions due to missing nodes. One should be able
    to run this on a Viewer- or any node for that matter- with no viewerSync
    knobs on it whatsoever and not raise any errors.

    Args:
        viewer : (<nuke.nodes.Viewer>)
            The viewer node with the viewerSync knobs on it.

    Returns:
        None

    Raises:
        N/A

    """
    for knob in viewer.knobs():
        if knob.startswith('vs_'):
            viewer.removeKnob(viewer[knob])
    # It's unlikely that the tab knob was deleted at first.
    if 'vs_options' in viewer.knobs():
        viewer.removeKnob(viewer['vs_options'])

# =============================================================================


def _sync_knob(source, targets, knob):
    """Syncs a knob setting from the source to the target.

    Args:
        source : (<nuke.Node>)
            Any node that has a knob with a value we want to sync from.

        targets : [<nuke.Node>]
            A list of nodes that should have the same knob as source, that we
            want to have the same value as source. The call to these nodes
            and knobs is protected by a try/except, so even if the knob is
            missing it should resolve without error.

        knob : (str)
            The knob name to match between the source and the targets.

    Returns:
        None

    Raises:
        N/A

    """
    for target in targets:
        try:
            target[knob].setValue(source[knob].value())
        except NameError:
            # Knob doesn't exist on target.
            continue

# =============================================================================


def _set_callback(node, viewers):
    """Sets the callback on the node with the viewers and knobs args.

    Args:
        node : (<nuke.nodes.Viewer>)
            The viewer node we're going to set the callback on.

        viewers : [<nuke.nodes.Viewer>]
            The viewers the callback should reference.

    Returns:
        None

    Raises:
        N/A

    """
    # Create a copy of list, as we're poppin' the `node` if found.
    viewers = list(viewers)
    # Remove our caller from the nodes to update if present.
    if node in viewers:
        viewers.pop(viewers.index(node))

    # Get the list of node names to populate the arg with
    viewer_names = [viewer.fullName() for viewer in viewers]

    node['knobChanged'].setValue(
        'viewerSync.sync_viewers({viewers})'.format(
            viewers=viewer_names
        )
    )

# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================


def remove_callbacks():
    """Removes callback from all selected viewers and all viewers linked.

    Checks to make sure that the callback present is a viewerSync callback
    before we remove the callback, this prevents us from interfering with
    another tool.

    Args:
        N/A

    Returns:
        None

    Raises:
        N/A

    """
    viewers = nuke.selectedNodes('Viewer')

    if not viewers:
        viewers = nuke.allNodes('Viewer')
    else:
        extra_viewers = []  # Viewers that weren't in the selected group.
        for viewer in viewers:
            try:
                linked_viewers = _extract_viewer_list(viewer)
            except ValueError:
                pass
            else:
                extra_viewers.extend(linked_viewers)

        viewers.extend(extra_viewers)

    for viewer in viewers:
        if 'viewerSync' in viewer['knobChanged'].value():
            viewer['knobChanged'].setValue('')
        _remove_knobs(viewer)

# =============================================================================


def setup_sync():
    """Sets up a viewerSync between a group of Viewer nodes.

    This sets up callbacks between either all selected viewers, or all viewers
    at the current node graph level (as defined by what nuke.allNodes()
    returns). It also sets up a series of settings on the Viewer nodes
    themselves, controlling which knobs get synced between the Viewers.

    Before setting up the viewers, we check the current knobChanged value.
    Often that value is a viewerSync callback already. If so, we deactivate
    that viewerSync group before continuing. If the callback is foreign (not
    a viewerSync callback), we leave it alone and remove that Viewer from the
    viewerSync group, rather than mess up another python process.

    Args:
        N/A

    Returns:
        None

    Raises:
        N/A

    """
    # Grab all of our currently selected Viewer nodes:
    viewers = nuke.selectedNodes('Viewer')

    # We'll be using the viewer_levels dictionary to link viewers
    # across the same DAG level, and avoid linking lone viewers on sub DAGs.
    viewer_levels = {}

    # If we find ANY viewers of the currently selected set having a
    # knobChanged value, we'll turn off syncing on all the node's it's linked
    # to. Safer that way.
    remove_viewers = []

    if viewers:
        for viewer in viewers:
            # In case Nuke returns us viewers split across different levels,
            # we'll need to split them up by level so that we don't
            # attempt to link those.
            group = '.'.join(viewer.fullName().split('.')[:-1])
            if not group:
                group = 'root'
            group_viewers = viewer_levels.get(group, [])
            group_viewers.append(viewer)
            viewer_levels[group] = group_viewers
    else:
        # No viewers were provided, so we'll just grab all the viewers
        # at our current level
        viewers = nuke.allNodes('Viewer')
        viewer_levels['group'] = viewers

    for level in viewer_levels.keys():
        if len(viewer_levels[level]) <= 1:
            # Nothing to sync, delete this level.
            del viewer_levels[level]

    bad_viewers = []  # List of viewers that have foreign callbacks

    for viewers in viewer_levels.values():
        for viewer in viewers:
            try:
                linked_viewers = _extract_viewer_list(viewer)
            except ValueError:
                bad_viewers.append(viewer)
            else:
                remove_viewers.extend(linked_viewers)

    for rm_viewer in list(remove_viewers):
        for viewers in viewer_levels.values():
            if rm_viewer in viewers:
                remove_viewers.remove(rm_viewer)
        if rm_viewer in bad_viewers:
            try:
                remove_viewers.remove(rm_viewer)
            except ValueError:
                # We probably already removed this viewer above.
                pass

    if remove_viewers:
        for viewer in set(remove_viewers):
            viewer['knobChanged'].setValue('')
            _remove_knobs(viewer)

    for viewers in viewer_levels.values():
        for viewer in bad_viewers:
            if viewer in viewers:
                viewers.remove(viewer)
        for viewer in viewers:
            _add_sync_knobs(viewer)
            _set_callback(viewer, viewers)

# =============================================================================


def sync_viewers(viewers):
    """Syncs all the given viewers to the settings on the caller node.

    This is the primary callback for viewerSync. Through it, the actual sync
    happens. Before the callback executes, we compare the calling knob to a
    list of knobs that viewerSync is concerned about. If the caller knob isn't
    on the white-list, or the calling knob isn't currently set to sync (via the
    caller node's settings) we return early.

    Otherwise we sync the knob values for the knob that called us.

    Args:
        viewers : [str]
            This list of absolute viewer names will be resolved into
            <nuke.nodes.Viewer>s, which will be synced to the caller
            node's knob values.

    Returns:
        None

    Raises:
        N/A

    """

    caller = nuke.thisNode()
    caller_knob = nuke.thisKnob().name()

    # We need to check what knob is calling us first- if that knob isn't a
    # syncing knob, we'll return.
    if caller_knob not in ['inputChange', 'knobChanged']:
        if caller_knob not in SYNC_DEFAULTS.keys() + VIEWER_SYNC_KNOBS:
            return

        if caller_knob not in VIEWER_SYNC_KNOBS:
            if not caller['vs_{knob}'.format(knob=caller_knob)].value():
                # Sync setting is false for this knob
                return

    # Grab our viewer nodes and remove any that have been deleted.
    viewer_nodes = [
        nuke.toNode(viewer) for viewer in viewers if nuke.toNode(viewer)
    ]

    if caller_knob in VIEWER_SYNC_KNOBS:
        # Sync setting and continue
        _sync_knob(caller, viewer_nodes, caller_knob)
        if caller[caller_knob].value():
            caller_knob = caller_knob.replace('vs_', '')

    if caller_knob in ['inputChange', 'inputs']:
        if caller['vs_inputs'].value():
            for viewer in viewer_nodes:
                for i in xrange(caller.inputs()):
                    viewer.setInput(i, caller.input(i))
        return
    elif caller_knob == 'knobChanged':
        knob_list = [
            knob for knob in SYNC_DEFAULTS.keys() if SYNC_DEFAULTS[knob]
        ]
    else:
        knob_list = [caller_knob]

    # Update remaining viewers to point at our current node.
    for knob in knob_list:
        _sync_knob(caller, viewer_nodes, knob)
