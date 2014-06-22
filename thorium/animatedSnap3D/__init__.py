#!/usr/bin/env python
"""

Animated Snap 3D
================

An extension to Nuke's "snap" options for animated 3D objects. Based on a
selection of vertices, this allows for objects to match the position, rotation
and scale of that selection over a specified frame range.

## Usage

As the name suggests, this adds "animated" options to the snap_menu in 3d
nodes since Nuke 6.1. The 3 new options work exactly the same way as their
original counterparts, but extends their use to animated geometry.

## Installation

To install, simply ensure the 'animatedSnap3D' directory is in your .nuke
directory or anywhere else within the Nuke python path.

Then, add the following lines to your 'menu.py' file:
::
    import animatedSnap3D
    animatedSnap3D.run()

## Public Functions

    run()
        Adds the animatedSnap3D functions to the Axis Snap Menu

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

# ==============================================================================
# IMPORTS
# ==============================================================================

# Nuke Imports
try:
    import nuke
except ImportError:
    pass

# animatedSnap3D Imports
from animatedSnap3D import animated_snap

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Ivan Busquets"
__author_email__ = "ivanbusquets@gmail.com"
__copyright__ = "Copyright 2011, Ivan Busquets"
__credits__ = ["Ivan Busquets", "Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "1.2b1"
__maintainer__ = "Sean Wallitsch"
__maintainer_email__ = "sean@grenadehop.com"
__module_name__ = "animatedSnap3D"
__short_desc__ = "An extension to Nuke's 'snap' options for animated 3D objects"
__status__ = "Development"
__url__ = 'http://github.com/ThoriumGroup/animatedSnap3D'

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'run',
    'animated_snap'
]

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def run():
    """Add animatedSnap3D menu items under the Axis Menu"""
    axis_menu = nuke.menu('Axis').findItem('Snap')
    axis_menu.addSeparator()
    axis_menu.addCommand(
        'Match position - Animated',
        'animatedSnap3D.animated_snap(["translate"])'
    )
    axis_menu.addCommand(
        'Match position, orientation - Animated',
        'animatedSnap3D.animated_snap(["translate", "rotate"])'
    )
    axis_menu.addCommand(
        'Match position, orientation, scale - Animated',
        'animatedSnap3D.animated_snap(["translate", "rotate", "scaling"])'
    )
