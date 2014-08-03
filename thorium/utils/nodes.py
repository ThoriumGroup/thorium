#!/usr/bin/env python
"""

Thorium Utils Nodes
===================

Generic utilities for Nuke node manipulation included within Thorium

## Public Functions

    allNodes()
        Wraps nuke.allNodes to allow filtering and recursion. Note that this
        name violates the style conventions to be a transparent replacement
        for nuke.allNodes().

    center_x()
        Returns the x position needed to center a target node relative to a
        source node in x.

    center_y()
        Returns the y position needed to center a target node to the side of
        the source node.

    connect_inline()
        Connects a target node in between a source node and all of its
        dependents.

    space_x()
        Returns the x position needed to space a target node to the side of a
        source node.

    space_y()
        Returns the y position needed to space a target node under a source
        node.

## License

The MIT License (MIT)

Thorium
Copyright (c) 2014 Sean Wallitsch

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
    import nukescripts
except ImportError:
    pass

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'allNodes',
    'center_x',
    'center_y',
    'connect_inline',
    'space_x',
    'space_y',
]

# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================


def allNodes(filter=None, group=nuke.root(), recurseGroups=False):
    """ Wraps nuke.allNodes to allow filtering and recursion.

    Args:
        filter=None : (str)
            A Nuke node name to filter for. Must be exact match.

        group=nuke.root() : (<nuke.nodes.Group>)
            A Nuke node of type `Group` to search within. If not provided, will
            begin the search at the root level.

        recurseGroups=False : (bool)
            If we should continue our search into any encountered group nodes.

    Returns:
        [<nuke.Node>]
            A list of any Nuke nodes found whose Class matches the given filter.

    Raises:
        N/A

    """
    # First we'll check if we need to execute our custom allNodes function.
    # If we don't have a filter AND recurseGroups=True, `nuke.allNodes` will
    # do the job fine.
    if filter and recurseGroups:
        # Search for every node, then filter using a list comprehension.
        # Faster than searching for all groups, then searching again
        # for the filter.
        all_nodes = nuke.allNodes(group, recurseGroups=True)

        return [node for node in all_nodes if node.Class() == filter]

    else:
        # We just need to execute Nuke's `nuke.allNodes` function.
        # But we need to modify our list of keyword arguments and remove
        # the filter argument if it wasn't passed, otherwise Nuke chokes.
        kwargs = {
            'group': group,
            'recurseGroups': recurseGroups
        }

        # Add filter argument if present
        if filter:
            kwargs['filter'] = filter

        return nuke.allNodes(**kwargs)

# =============================================================================


def center_below(target, source, padding=6):
    """Centers a target node below a source node in both x and y

    Args:
        target : (<nuke.Node>)
            The node to place below the source node.

        source : (<nuke.Node>)
            The parent node to place the target node below.

        padding=6 : (int)
            The amount of padding between the source and target node. Nuke's
            default is `6`.

    Returns:
        None

    Raises:
        N/A

    """
    target.setXpos(center_x(target, source))
    target.setYpos(space_y(source, padding))

# =============================================================================


def center_x(target, source):
    """Returns the x position needed to center target relative to source.

    Args:
        target : (<nuke.Node>)
            The Nuke node to return the desired position for.

        source : (<nuke.Node>)
            The Nuke node that will be used for determining the center point.

    Returns:
        (int)
            Returns the x position the `target` node should be placed at to be
            centered exactly below or above the `source` node.

    Raises:
        N/A

    """
    return source.xpos() - ((target.screenWidth() - source.screenWidth()) / 2)

# =============================================================================


def center_y(target, source):
    """Returns the y position needed to center target relative to source.

    Args:
        target : (<nuke.Node>)
            The Nuke node to return the desired position for.

        source : (<nuke.Node>)
            The Nuke node that will be used for determining the center point.

    Returns:
        (int)
            Returns the y position the `target` node should be placed at to be
            centered exactly to the side of the `source` node.

    Raises:
        N/A

    """
    return source.ypos() - (
        (target.screenHeight() - source.screenHeight()) / 2
    )

# =============================================================================


def connect_inline(target, source):
    """Connects a target node in between source and all dependent nodes.

    Args:
        target : (<nuke.Node>)
            The Nuke node to connect inline between source and all of source's
            dependent nodes.

        source : (<nuke.Node>)
            The Nuke node that should be target should be connected to.

    Returns:
        None

    Raises:
        N/A

    """
    dependents = source.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS)
    target.setInput(0, source)

    if target.maxOutputs():
        for node in dependents:
            print node.fullName()
            for i in xrange(node.inputs()):
                print "setting input {0}".format(i)
                print node.input(i)
                if node.input(i) == source:
                    print "setting that input"
                    node.setInput(i, target)

# =============================================================================


def space_x(source, padding=80):
    """Returns the x position needed to place a node to the right of source.

    This is accomplished by taking into account the source node DAG icon
    width, the desired padding and the xpos the source node is already at.

    Args:
        source : (<nuke.Node>)
            The Nuke node that target should to the side of.

        padding=80 : (int)
            The desired padding between the source and target node. Nuke
            doesn't really have a default for this, but it looks nice
            with exactly one standard node width between.

    Returns:
        (int)
            Returns the x position the `target` node should be placed at to be
            neatly spaced to the right of `source`.

    Raises:
        N/A

    """
    return source.screenWidth() + source.xpos() + padding

# =============================================================================


def space_y(source, padding=6):
    """Returns the y position needed to place a node beneath source.

    This is accomplished by taking into account the source node DAG icon
    height, the desired padding and the ypos the source node is already at.

    Args:
        source : (<nuke.Node>)
            The Nuke node that target should be placed below.

        padding=6 : (int)
            The desired padding between the source and target node. Nuke's
            default is `6`.

    Returns:
        (int)
            Returns the y position the `target` node should be placed at to be
            neatly spaced below `source`.

    Raises:
        N/A

    """
    return source.screenHeight() + source.ypos() + padding
