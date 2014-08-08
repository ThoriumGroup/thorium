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
    `setup()` method (just a pass here). `__new__()` will return an instance
    of `nuke.nodes.Group()` instead of `Groupmo` or it's subclasses.

    `__new__()` will do the following:

        * Create the Group node, passing all arguments and keyword arguments
            given.
        * Add a Tab named the same as the `cls.Class` variable value.
        * Add an invisible knob named `groupmo_class` to the Group with the
            `cls.Class` value.
        * Sets the name of the group to the `cls.Class` value.
        * Executes the `setup()` method:
            * Before execution, we run `Group.begin()` which dumps us
                inside of the Group. Any nodes added will be added inside of
                group.
            * After execution, we run `Group.end()`, closing the Group.
            * `setup()` requires & passes one argument- the
                `nuke.nodes.Group()` instance.
        * If after `setup()` the Groupmo has an input, that input is connected
            to the currently selected node (if any).
        * If after `setup()` the Groupmo has an output, that output is
            connected to all the nodes formally dependent on the selected node.
        * If a node is currently selected, the Groupmo is placed below it, the
            amount of padding can be controlled by passing a `padding` keyword
            argument when creating the `Groupmo`. This `padding` kwarg will not
            be passed through to the creation of the Group.
        * If a node is currently selected, that node is de-selected, leaving
            only the newly created Groupmo selected.

    Class Attributes:

        Class : (str)
            The `Class` of the Groupmo, within the context of Nuke. In Nuke,
            every node has a `Class`. Blur nodes are the Blur class, modern
            merge nodes are the `Merge2` class. The class name can be used to
            find certain types of nodes with `nuke.allNodes()`.

            The Class name on a Groupmo node is used to name the group, add
            a parameters tab named the same as the Class name, and creates an
            invisible text knob on the Groupmo that contains the Class name.

            That invisible knob is used by Thorium's `allNodes()` function to
            enable Groupmos to behave like native Nuke nodes. If you had a
            `SpillSuppress` Groupmo, you could get all instances of that
            Groupmo in your current script by running
            `utils.allNodes('SpillSuppress')`

            This attribute should be overridden by all subclasses.

            Default: 'Groupmo'

        help : (str)
            The help string that will be displayed when the user hovers over
            the help icon in the upper right hand corner of the Groupmo's
            parameter panel.

            This should describe general usage about the node.

            Default: "Python constructed Groupmo, which is meant to function
            similarly to a Gizmo. This is otherwise a normal Nuke Group, which
            acts a nesting container for a set of nodes. Hit 'show' to see the
            internal structure"

    Class Methods:

        setup()
            This method is the one that should be overridden by the subclasses
            of Groupmo. Replace this method with the nodes that will make up
            the Groupmo.

            Any nodes added within `setup()` will be added inside of the
            Groupmo. Any knobs added within `setup()` will be added to the
            tab named after the `Class` attribute. Additional tabs can be
            created as normal.

            For Groupmo's that have an input and an output, `setup()` would
            start with the instancing of a `nuke.nodes.Input()` and end with
            the instancing of a `nuke.nodes.Output()`.

            This is also the place to add parameter knobs.

            `setup()` needs to accept an argument that takes the created
            `nuke.nodes.Group()` instance, which is the Groupmo. This is so
            you can add knobs to Groupmo, which requires that you have access
            to the Groupmo instance.

    """

    Class = 'Groupmo'
    help = (
        "Python constructed Groupmo, which is meant to function "
        "similarly to a Gizmo. This is otherwise a normal Nuke Group, which "
        "acts a nesting container for a set of nodes. Hit 'show' to see the "
        "internal structure"
    )

    def __new__(cls, *args, **kwargs):
        """Constructs a Groupmo and returns the node.

        Args:
            All args and keyword args will be passed to the creation of the
            Nuke Group with the exception of:

            padding : (int)
                The amount of spacing between any currently selected node
                and the newly created Groupmo, if the Groupmo has inputs.

        Returns:
            (<nuke.nodes.Group>)
                Note that this does NOT return an instance of `Groupmo`. We
                instead return the nuke node.

        Raises:
            N/A

        """
        padding = kwargs.pop('padding', None)

        if 'help' not in kwargs:
            kwargs['help'] = cls.help

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
        """Creates all nodes and promotes all knobs for the Groupmo

        When subclassing `Groupmo`, this method must be overridden and filled
        with content.

        Args:
            groupmo : (<nuke.nodes.Group>)
                The Group node which we're creating the Groupmo on.

        Returns:
            None

        Raises:
            N/A

        """
        pass
