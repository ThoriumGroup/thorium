#!/usr/bin/env python
"""

Animated Snap 3D
================

This submodule contains the functions needed to executed an animated snap.

## Public Functions

    animated_snap()
        A wrapper to call the relevant snap functions within a frame
        range loop.

## License

The MIT License (MIT)

animatedSnap3D
Copyright (c) 2011 Ivan Busquets

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

# Nuke Imports
try:
    import nuke
    from nukescripts import snap3d
except ImportError:
    pass

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'animated_snap'
]

# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


def _get_frange():
    """Open a dialog to request a Nuke-style frame range

    Args:
        N/A

    Returns:
        <nuke.FrameRange>
            Returns a FrameRange object if valid frange is entered, or none.

    Raises:
        N/A

    """

    first_frame = int(nuke.numvalue('root.first_frame'))
    last_frame = int(nuke.numvalue('root.last_frame'))
    step = 1
    default_frange = str(nuke.FrameRange(first_frame, last_frame, step))
    frange = nuke.getInput('Enter Frame Range:', default_frange)

    if not frange:
        return None
    else:
        try:
            return nuke.FrameRange(frange)
        except:  # TODO: Determine exact exception
            nuke.message('Invalid frame range')
            return None

# =============================================================================


def _frange_percent(frame, frange):
    """Determines what percent completion a task is based on frame and frange

    Args:
        frame : (int)
            The frame to determine what percent complete we are.

        frange: (<nuke.FrameRange>)
            A nuke.FrameRange object with frange information.

    Returns:
        (int)
            The percentage of completion.

    Raises:
        N/A

    """
    percent = (frame - frange.first()) / float(frange.framges())

    return int(percent * 100)

# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================


def animated_snap(transforms=None, node=None, vertices=None, frange=None):
    """A wrapper to call the relevant snap functions within a frame range loop

    Args:
        transforms=None : [str]
            A list of transforms to apply to the snapped object. Should be
            one or more of the following:
                translate, rotate or scaling

            Default: ['translate']

        node=None : (<nuke.Node>)
            The Nuke node to apply the transforms to.

            Default: nuke.thisNode()

        vertices=None : [<nuke.Vertex>]
            The vertices to use to get the transformation.

            Default: snap3d.getSelection()

        frames=None : (<nuke.FrameRange>)
            Provide a FrameRange object to suppress dialog.

    Returns:
        None

    Raises:
        N/A

    """

    min_verts = 1
    if not node:
        node = nuke.thisNode()
    if not vertices:
        vertices = snap3d.getSelection()
    if not transforms:
        transforms = ['translate']

    snap_func = snap3d.translateToPointsVerified

    knobs = list(transforms)
    knobs.append('xform_order')

    if 'rotate' in knobs:
        knobs.append("rot_order")
        snap_func = snap3d.translateRotateToPointsVerified
    if 'scaling' in knobs:
        min_verts = 3
        snap_func = snap3d.translateRotateScaleToPointsVerified

    # Verify valid selections before we enter the loop
    try:
        snap3d.verifyNodeToSnap(node, knobs)
        snap3d.verifyVertexSelection(vertices, min_verts)
    except ValueError as err:
        nuke.message(err)
        return

    if not frange:
        # Ask for a frame range
        frange = _get_frange()

    if not frange:
        # Exit early if cancelled or empty frange
        return

    # Add a CurveTool for the forced-evaluation hack
    temp = nuke.nodes.CurveTool()

    # Set the animated flag on knobs
    for knob in [node[knob_name] for knob_name in transforms]:
        # Reset animated status
        if knob.isAnimated():
            knob.clearAnimated()
        knob.setAnimated()

    # Set up Progress Task
    task = nuke.ProgressTask("Snapping")
    task.setMessage(
        "Matching position of {node_name} to selected vertices".format(
            node_name=node.name()
        )
    )

    # Loop through the framerange
    for frame in frange:
        if task.isCancelled():
            break

        progress = _frange_percent(frame, frange)
        task.setProgress(progress)

        # Execute the CurveTool node to force evaluation of the tree
        nuke.execute(temp, frame, frame)

        # The vertex selection needs to be computed per frame
        # in order to get the vertices at the right context (time)
        vertices = snap3d.getSelection()

        # Checking vertex selection again in case topology has changed
        try:
            snap3d.verifyVertexSelection(vertices, min_verts)
        except ValueError:
            nuke.message(
                "Number of vertices selected has dropped below {verts}."
                "This is most likely due to changes in geometry topology."
                "\n"
                "Please select new vertices and start again from frame "
                "{frame} on.".format(
                    verts=min_verts,
                    frame=frame
                )
            )
            break
        else:
            # Call the passed snap function from the nukescripts.snap3d module
            snap_func(node, vertices)

    if temp:
        nuke.delete(temp)
