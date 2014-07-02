#!/usr/bin/env python
"""

Viewer Sync
===========

Synchronizes two or more viewers in Nuke so that they always show the same node.

## Usage

Synchronizing viewers in nuke is as easy as hitting `Shift+j` with two or more
viewers selected. If no viewers are selected, all viewers on the root node
graph level are synchronized.

From that point on, certain designated settings are synced between those
viewers whenever you change one of those settings on either one. Those settings
are selectable from a new 'Viewer Sync' tab in the Viewer settings. You can
choose to sync channels, inputs, viewed input number, luts, input processes,
color corrections, overlays, ROI, and more.

To remove the synchronization from nodes, select the nodes you wish to remove
synchronization from, and select 'Remove Viewer Sync'. If no nodes are
selected, all the viewers found on the root node graph level are de-synced.
Note that any viewers that are in the same group

## Installation

To install, simply ensure the 'viewerSync' directory is in your .nuke
directory or anywhere else within the Nuke python path.

Then, add the following lines to your 'menu.py' file:
::
    import viewerSync
    viewerSync.run()

Hotkey can be set with the `hotkey` argument, which defaults to `Shift+j`.

## Public Functions

    run()
        Adds the viewerSync menu item to the User menu.

## License

The MIT License (MIT)

viewerSync
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

# ==============================================================================
# IMPORTS
# ==============================================================================

# Nuke Imports
try:
    import nuke
except ImportError:
    pass

# viewerSync Imports
from .viewerSync import remove_callbacks, setup_sync, sync_viewers

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Philippe Huberdeau"
__author_email__ = "philpma@free.fr"
__copyright__ = "Copyright 2011-2014, Philippe Huberdeau and Sean Wallitsch"
__credits__ = ["Philippe Huberdeau", "Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "2.0b1"
__maintainer__ = "Sean Wallitsch"
__maintainer_email__ = "sean@grenadehop.com"
__module_name__ = "viewerSync"
__short_desc__ = "Synchronizes two or more viewers in Nuke."
__status__ = "Development"
__url__ = "http://github.com/ThoriumGroup/viewerSync"

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'remove_callbacks',
    'run',
    'setup_sync',
    'sync_viewers',
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


def run(menu='Viewer', hotkey='Shift+j', submenu=None, submenu_index=None,
        item_index=-1):
    """Adds viewerSync menu items.

    Args:
        menu='Viewer' : (str)
            Top menu to add viewerSync under. Defaults to adding it under
            the built in 'Viewer' menu.

        hotkey='Shift+j' : (str)
            The hotkey to trigger viewerSync.

        submenu=None : (str)
            Submenu to add viewerSync under. If no submenu desired, giving
            this a value of None will result in no submenu being used.

        submenu_index=None : (int)
            Position of submenu within the top menu.

            Default: Will parse menu, sort items alphabetically to determine
                what the index would be assuming menu was already
                alphabetically sorted.

        item_index=-1 : (int)
            Position of viewerSync toggle command within the submenu.

            If given `None`, will parse submenu, sort items alphabetically to
            determine what the index would be assuming submenu was already
            alphabetically sorted.

    Returns:
        None

    Raises:
        N/A

    """
    # Find and setup our top level menu
    top_level_menu = nuke.menu('Nuke').findItem(menu)
    if not top_level_menu:
        # The top level menu item doesn't exist yet, we'll create it.
        top_level_menu = nuke.menu('Nuke').addMenu(menu)

    # Find and setup our submenu under the top level menu
    if submenu:
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

    dest_menu.addCommand(
        'Create Viewer Sync',
        'viewerSync.setup_sync()',
        hotkey,
        index=item_index if item_index is not None else
        _get_menu_item_index(dest_menu, 'Create Viewer Sync')
    )

    dest_menu.addCommand(
        'Remove Viewer Sync',
        'viewerSync.remove_callbacks()',
        index=item_index if item_index is not None else
        _get_menu_item_index(dest_menu, 'Remove Viewer Sync')
    )
