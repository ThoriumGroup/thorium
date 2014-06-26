#!/usr/bin/env python
"""

Card To Track
=============

Converts a 3d card's corners to tracking points, corner pins or a
matrix calculation for use on a corner pin or roto.

## Usage

Select a camera, the card to track, and a background plate (for calculating
image resolution) and select CardToTrack from the menu. Fill out the desired
frame range, the type of output requested (Defaults to "All", which will export
a Tracker node with 4 tracking points, a Corner Pin node with the corner's
tracked, a Corner Pin node set with a matrix calculation, and a Roto set with
a matrix calculation), and the desired reference frame. If you only want the
translation tracked, check that box.

CardToTrack will then create the intermediate nodes required to calculate the
final desired output, run through the frame range, create the output nodes, and
finally clean up after itself.

More usage information is available in this YouTube video from the creator,
Alexey Kuchinski:

https://www.youtube.com/watch?v=-NTdTy2PzQ0

## Installation

To install, simply ensure the 'cardToTrack' directory is in your .nuke
directory or anywhere else within the Nuke python path.

Then, add the following lines to your 'menu.py' file:
::
    import cardToTrack
    cardToTrack.run()

## Public Functions

    run()
        Adds the cardToTrack functions to the User top menu.

## License

The MIT License (MIT)

cardToTrack
Copyright (c) 2011-2014, Alexey Kuchinski and Sean Wallitsch

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

# cardToTrack Imports
from .cardToTrack import (
    card_to_track, card_to_track_wrapper, corner_pin_to_corner_matrix,
    matrix_to_roto_matrix, reconcile_to_corner, reconcile_to_tracks
)

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Alexey Kuchinski"
__author_email__ = "lamakaha@gmail.com"
__copyright__ = "Copyright 2011-2014, Alexey Kuchinski and Sean Wallitsch"
__credits__ = ["Alexey Kuchinski", "Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "6.0b1"
__maintainer__ = "Sean Wallitsch"
__maintainer_email__ = "sean@grenadehop.com"
__module_name__ = "cardToTrack"
__short_desc__ = "Converts a 3d card to tracking points, corner pins or matrix"
__status__ = "Development"
__url__ = "http://github.com/ThoriumGroup/cardToTrack"

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'card_to_track',
    'card_to_track_wrapper',
    'corner_pin_to_corner_matrix',
    'matrix_to_roto_matrix',
    'reconcile_to_corner',
    'reconcile_to_tracks',
    'run',
]

# ==============================================================================
# PRIVATE FUNCTIONS
# ==============================================================================


def _get_menu_item_index(menu, item):
    """Determines what should be the index of item if menu was alphabetical

    Args:
        menu : (<nuke.Menu>)
            The Nuke menu that we want to determine the place our item in.

        item : (str)
            The name of the menu item we want to determine the alphabteical
            index if placed within menu.

    Returns:
        (int)
            The index of `item` if placed within a sorted list of the items
            that already exist in `menu`.

    Raises:
        N/A

    """
    menu_items = [entry.name() for entry in menu.items()]
    menu_items.append(item)
    menu_items.sort()
    return menu_items.index(item)

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def run(menu=None, submenu=None, submenu_index=None, item_index=None):
    """Add cardToTrack menu items.

    Args:
        menu=None : (str)
            Top menu to add CardToTrack under.

            Default: 'User'

        submenu=None : (str)
            Submenu to add CardToTrack under. If no submenu desired, giving
            this a value of '.' will result in no submenu being used.

            Default: '3D'

        submenu_index=None : (int)
            Position of submenu within the top menu.

            Default: Will parse menu, sort items alphabetically to determine
                what the index would be assuming menu was already
                alphabetically sorted.

        item_index=None : (int)
            Position of cardToTrack command within the submenu.

            Default: Will parse submenu, sort items alphabetically to
            determine what the index would be assuming submenu was already
            alphabetically sorted.

    Returns:
        None

    Raises:
        N/A

    """
    # Find and setup our top level menu
    if not menu:
        menu = 'User'
    top_level_menu = nuke.menu('Nuke').findItem(menu)
    if not top_level_menu:
        # The top level menu item doesn't exist yet, we'll create it.
        top_level_menu = nuke.menu('Nuke').addMenu(menu)

    # Find and setup our submenu under the top level menu
    if not submenu:
        submenu = '3D'
    if submenu != '.':
        dest_menu = top_level_menu.findItem(submenu)
        if not dest_menu:
            # The submenu doesn't exist yet, we'll create it.
            dest_menu = top_level_menu.addMenu(
                submenu,
                index=submenu_index if submenu_index is not None else
                _get_menu_item_index(top_level_menu, submenu)
            )
    else:
        dest_menu = top_level_menu

    # Setup our command
    dest_menu.addCommand(
        'CardToTrack',
        'cardToTrack.card_to_track_wrapper()',
        index=item_index if item_index is not None else
        _get_menu_item_index(dest_menu, 'CardToTrack')
    )
