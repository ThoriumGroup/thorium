#!/usr/bin/env python
"""

Thorium Utils.Groupmo
=====================

Contains a class which makes it easier to build `Groupmo`s, Groups that
function similarly to Nuke's `Gizmo`s, but built with Python and saved within
the Nuke script.

## Classes

    Groupmo
        A Group that functions like a Gizmo.

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

# Thorium Imports
from .nodes import center_below, center_y, connect_inline, space_x

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'Groupmo'
]

# =============================================================================
# CLASSES
# =============================================================================


class Groupmo(object):
    """Template for creating Gizmo-like Groups with Python.

    A Groupmo is driven by the `__new__()` special method, and the normal
    `setup()` method (blank here). `__new__()`


    """

    Class = 'Groupmo'

    def __new__(cls, *args, **kwargs):
        """New Stuff"""
        padding = kwargs.pop('padding', None)

        # Grab our selected node if there is one.
        try:
            selected = nuke.selectedNode()
        except ValueError:
            selected = None

        # Create Group, passing along all given arguments.
        groupmo = nuke.nodes.Group(*args, **kwargs)

        # Add tab that matches class name
        groupmo.addKnob(
            nuke.Tab_Knob(
                cls.Class,
                cls.Class
            )
        )

        # Set our groupmo class id knob
        class_knob = nuke.Text_Knob(
            'groupmo_class',
            'Groupmo Class: ',
            cls.Class
        )
        class_knob.setFlag(nuke.INVISIBLE)

        # Set our groupmo's name.
        groupmo.setName(cls.Class)

        # Call the setup function, which will be overriden by each Groupmo.
        groupmo.begin()
        cls.setup(groupmo)
        groupmo.end()

        if selected and groupmo.maxInputs():
            # If we've been given a padding, obey it. Otherwise, do not
            # pass padding and let the default padding for the func rule.
            center_args = [groupmo, selected]
            if padding:
                center_args.append(padding)

            center_below(*center_args)
            connect_inline(groupmo, selected)

        elif selected:
            space_args = [selected, padding] if padding else [selected]
            groupmo.setXYpos(
                space_x(*space_args), center_y(groupmo, selected)
            )

        if selected:
            print 'time to deselect'
            for node in nuke.selectedNodes():
                node['selected'].setValue(False)

        groupmo['selected'].setValue(True)

        return groupmo

    @classmethod
    def setup(cls, groupmo):
        pass
