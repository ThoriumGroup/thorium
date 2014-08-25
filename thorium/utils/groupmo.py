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

## Public Functions

    normalize_docstring()
        Takes a docstring and removes all tabs and single newlines. Will
        also split along a given split text, and bold the first line or any
        lines that end in ':'.

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
from .nodes import center_below, center_y, connect_inline, set_link, space_x

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'Groupmo',
    'normalize_docstring'
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

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

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
        groupmo.addKnob(class_knob)

        if 'name' not in kwargs:
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

            if 'xpos' not in kwargs and 'ypos' not in kwargs:
                center_below(*center_args)

            connect_inline(groupmo, selected)

        elif selected:
            space_args = [selected, padding] if padding else [selected]
            if 'xpos' not in kwargs and 'ypos' not in kwargs:
                groupmo.setXYpos(
                    space_x(*space_args), center_y(groupmo, selected)
                )

        if selected:
            for node in nuke.selectedNodes():
                node['selected'].setValue(False)

        groupmo['selected'].setValue(True)

        return groupmo

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================

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


class MaskMix(Groupmo):
    """Atomic node for applying a mask and mixing an effect.

    This node emulates the common functions found at the top and bottom
    of most Nuke nodes- allowing users to choose what channels to affect,
    if the effect should be limited to a mask area, and what the mix level
    should be between the original and the effect.

    Usage:

    Primary intended to be used within other nodes, """

    Class = 'MaskMix'
    help = "Does masking and mixing yo."

    @classmethod
    def setup(cls, groupmo):

        # =====================================================================
        # Nodes
        # =====================================================================

        # Input ===============================================================

        effect_input = nuke.nodes.Input(
            name='effect'
        )
        bg_input = nuke.nodes.Input(
            name='background',
            xpos=effect_input.xpos() - 480,
            ypos=effect_input.ypos()
        )
        mask_input = nuke.nodes.Input(
            name='mask',
            xpos=effect_input.xpos() + 400,
            ypos=effect_input.ypos()
        )
        mask_dot = nuke.nodes.Dot(
            inputs=[mask_input],
            xpos=mask_input.xpos() + 34,
            ypos=mask_input.ypos() + 216,
        )

        # Layer Select ========================================================

        copy = nuke.nodes.Copy(
            inputs=[mask_dot, effect_input],
            name='EffectChannels',
            xpos=effect_input.xpos(),
            ypos=effect_input.ypos() + 200
        )
        copy['from0'].setValue('none')
        copy['to0'].setValue('none')
        copy['channels'].setValue('rgba')

        # Mask ================================================================

        invert = nuke.nodes.Invert(
            inputs=[mask_dot],
            xpos=mask_dot.xpos() - 34,
            ypos=mask_dot.ypos() + 200,
        )
        keymix = nuke.nodes.Keymix(
            inputs=[copy, mask_dot, invert],
            xpos=copy.xpos(),
            ypos=invert.ypos()
        )
        keymix['maskChannel'].setValue('none')

        bg_dot = nuke.nodes.Dot(
            inputs=[bg_input],
            xpos=bg_input.xpos() + 34,
            ypos=invert.ypos() + 200,
        )

        # Mix =================================================================

        dissolve = nuke.nodes.Dissolve(
            inputs=[bg_dot, keymix],
            xpos=keymix.xpos(),
            ypos=bg_dot.ypos() - 10,
        )
        dissolve['which'].setValue(1)

        # Output ==============================================================

        nuke.nodes.Output(
            inputs=[dissolve],
            xpos=dissolve.xpos(),
            ypos=dissolve.ypos() + 200
        )

        # =====================================================================
        # Knobs
        # =====================================================================

        set_link('channels', groupmo, copy, label='channels')

        groupmo.addKnob(nuke.Text_Knob('channelDiv', ''))

        set_link('maskChannel', groupmo, keymix, label='mask')
        set_link('invertMask', groupmo, keymix, startline=False)
        set_link('which', groupmo, dissolve, label='mix')

# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================


def normalize_docstring(docstring, split_text=None, append=None, bold=True):
    """Removes tabs and single newlines from a docstring, splits given text

    Args:
        docstring : (str)
            The docstring to modify.

        split_text=None : (str)
            Splits the docstring along the given string and takes the first
            result. Use this to cut off argument listing.

        append=None : (str)
            Text to append at the end of the pruned docstring.

        bold=True : (bool)
            If True, bolds the first line of the given text and any line that
            ends with ':'.

    Returns:
        (str)
            Returns docstring as a string with only double newlines
            preserves, and all tabs and 4 white spaces removed.

    Raises:
        N/A

    """
    if split_text:
        doc = docstring.split(split_text)[0]

    if bold:
        doc_lines = doc.split('\n')
        # We want to BOLD the first line and any line that ends with ':'
        for i in xrange(len(doc_lines)):
            if not i or doc_lines[i].endswith(':'):
                doc_lines[i] = '<b>{line}</b>'.format(
                    line=doc_lines[i]
                )
        doc = '\n'.join(doc_lines)

    # This should probably be regex, but the double newlines make regex a
    # pain due to poor look-behind support, so we'll just use replace
    # with the hack that we change the double newlines to a random string.
    doc = doc.replace('\t', '')
    doc = doc.replace('    ', '')
    doc = doc.replace('\n\n', 'DOUBLENEWLINE')
    doc = doc.replace('\n', ' ')
    doc = doc.replace('DOUBLENEWLINE', '\n\n')

    if append:
        doc += append

    return doc
