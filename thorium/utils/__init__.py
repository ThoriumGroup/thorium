#!/usr/bin/env python
"""

Thorium Utils
=============

Generic utilities for Nuke included within the Thorium package.

## Public Functions

    allNodes()
        Wraps nuke.allNodes to allow filtering and recursion. Note that this
        name violates the style conventions to be a transparent replacement
        for nuke.allNodes().

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
    'allNodes'
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
