#!/usr/bin/env python
"""

Thorium Keying SpillSuppress
============================

Spill Suppression Groupmo

## Classes

    SpillSuppress
        Spill Suppression Groupmo that gives many different controls for
        suppressing spill from keys.

## License

The MIT License (MIT)

Thorium
Copyright (c) 2014 Sean Wallitsch & Chris Kenny

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
from ..utils import flags, Groupmo, normalize_docstring, set_link

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'SpillSuppress'
]

# =============================================================================
# CLASSES
# =============================================================================


class SpillSuppress(Groupmo):
    """Spill Suppression that works by subtracting excess spill.

    This is a raw method that gets very pleasant results. The spill
    channel is compared to either the average or the maximum of the alternate
    color channels.

    Values above the average/maximum are determined to be spill. We can then
    manipulate that spill amount to dial in the spill matte, eating in on edges
    or treating them more gently, etc.

    Then we balance that spill matte versus our desired result color, adding or
    removing the spill matte values from the color channels of that spill matte
    until we end up with a spill area that is of similar color to our desired
    background.

    Usage:

    Select 'Source Color' from the color of the key, not skin tones.

    Select 'Destination Color' from the background of the image the
    keyed element will go in front of in the composite.

    If colored edges are still visible on the element, try adjusting the
    'channel mix' value, or even using a maximum operation instead of an
    average.

    Adjusting gain and gamma will affect the spill threshold- which determines
    exactly what is considered spill. Adjusting the gain down increases the
    amount of the image that is considered spill, which has a large effect in
    bright areas.

    If the spill correction looks grainy, adding a small amount of blur with
    the 'blur spill' control can help smooth it out. If the spill correction
    looks incredibly grainy and blurring does little to help, the 'Destination
    Color' is probably too intense. Try brightening or darkening the desired
    'Destination Color.'

    If desired, the 'Destination Color' can be used as a manual balancing tool
    by checking the 'use for manual balancing' checkbox.

    Class Attributes:

        Class
            The name of the `Groupmo`: `SpillSuppress`

    Public Methods:

        disable_channel_mix_callback()
            Sets the `chanMix` knob to be the opposite of the `useMax` knob.

        setup()
            Builds all the interior nodes of the SpillSuppress, then promotes
            and creates the various control knobs.

    """
    Class = 'SpillSuppress'
    help = normalize_docstring(
        __doc__,
        'Class Attributes',
        'From <b>Thorium</b> by Sean Wallitsch'
    )

    # =========================================================================
    # Public Methods
    # =========================================================================

    @staticmethod
    def disable_channel_mix_callback():
        """Disables the channel mix average float if `useMax` is checked"""
        # Stop any knob except `useMax` from triggering
        if nuke.thisKnob().name() != 'useMax':
            return
        else:
            node = nuke.thisNode()
            useMax = node['useMax']
            node['chanMix'].setEnabled(not useMax.value())

    # =========================================================================

    @classmethod
    def setup(cls, groupmo):
        """Builds all the interior nodes and knobs of SpillSuppress"""

        # =====================================================================
        # Nodes
        # =====================================================================

        # Input ===============================================================

        input_node = nuke.nodes.Input()
        dot = nuke.nodes.Dot(
            inputs=[input_node],
            xpos=input_node.xpos() + 40 - 6,
            ypos=input_node.ypos() + 100
        )

        # Shuffles ============================================================

        def set_shuffle(shuffle, color):
            """Sets all the color channels of a shuffle to be the same color"""
            shuffle['red'].setValue(color)
            shuffle['green'].setValue(color)
            shuffle['blue'].setValue(color)
            shuffle['alpha'].setValue('white')

        # Shuffle to extract the green channel
        green_shuffle = nuke.nodes.Shuffle(
            inputs=[dot],
            name='Green',
            xpos=input_node.xpos(),
            ypos=dot.ypos() + 100
        )
        set_shuffle(green_shuffle, 'green')

        # Shuffle to extract the red channel
        red_shuffle = nuke.nodes.Shuffle(
            inputs=[dot],
            name='Red',
            xpos=green_shuffle.xpos() - 160,
            ypos=green_shuffle.ypos()
        )
        set_shuffle(red_shuffle, 'red')

        # Shuffle to extract the blue channel
        blue_shuffle = nuke.nodes.Shuffle(
            inputs=[dot],
            name='Blue',
            xpos=green_shuffle.xpos() + 160,
            ypos=green_shuffle.ypos()
        )
        set_shuffle(blue_shuffle, 'blue')

        dot2 = nuke.nodes.Dot(
            inputs=[dot],
            xpos=blue_shuffle.xpos() + 160,
            ypos=blue_shuffle.ypos() + 4,
        )

        # Color Switches ======================================================

        # This will autoswitch from green primary to blue primary, depending
        # on which color has a higher value.
        main_switch = nuke.nodes.Switch(
            inputs=[blue_shuffle, green_shuffle],
            name='BGSwitch',
            xpos=blue_shuffle.xpos(),
            ypos=blue_shuffle.ypos() + 100
        )
        # We set this to an expression which looks at the AutoBalance node.
        # Expression Reads:
        # If AutoBalance's Source Color Green channel minus the Blue channel is
        # greater than 0, value should be 1. Else, value should be 0.
        main_switch['which'].setExpression(
            'AutoBalance.source.g - AutoBalance.source.b > 0 ? 1 : 0'
        )

        # Inverse Switch (will be the opposite of Main Switch)
        inverse_switch = nuke.nodes.Switch(
            inputs=[green_shuffle, blue_shuffle],
            name='BGSwitchInverse',
            xpos=green_shuffle.xpos(),
            ypos=green_shuffle.ypos() + 100
        )
        inverse_switch['which'].setExpression(
            'BGSwitch.which'
        )

        # Channel Mixing ======================================================

        # These nodes will determine how the alternate color channels
        # (the color channels that are NOT the spill channel) are mixed
        # together to help determine how much of the spill channel is spill.
        cross = nuke.nodes.Merge2(
            inputs=[red_shuffle, inverse_switch],
            name='Cross',
            xpos=red_shuffle.xpos(),
            ypos=red_shuffle.ypos() + 200)
        cross.addKnob(nuke.Array_Knob('chanMix', 'channel mix'))
        cross['chanMix'].setValue(0.5)
        cross['chanMix'].setTooltip(
            "Adjust the weighted average of the alternate color channels. 0 "
            "is always the full red channel, 1 is either the blue or green "
            "channel. If the spill color is blue, 1 is the green channel and "
            "vice versa."
        )
        cross['chanMix'].setFlag(flags.SLIDER)
        cross['chanMix'].setFlag(flags.FORCE_RANGE)
        cross['mix'].setExpression('chanMix')

        max = nuke.nodes.Merge2(
            inputs=[red_shuffle, inverse_switch],
            name='Max',
            xpos=cross.xpos() - 160,
            ypos=cross.ypos(),
        )
        max['operation'].setValue('max')

        # Mix Switch will be a user controlled switch. When checked, it will
        # use the Max method instead of Crossing between the two.
        mix_switch = nuke.nodes.Switch(
            inputs=[cross, max],
            name='MaxOrCross',
            xpos=cross.xpos(),
            ypos=cross.ypos() + 100
        )
        mix_switch['which'].setExpression('parent.useMax')

        # Spill Controls ======================================================

        # These control the ebb and flow of the spill mask.
        thresh_gamma = nuke.nodes.Gamma(
            inputs=[mix_switch],
            name='ThresholdGamma',
            xpos=mix_switch.xpos(),
            ypos=mix_switch.ypos() + 26
        )
        thresh_gamma['value'].setExpression('parent.gamma')

        thresh_gain = nuke.nodes.Multiply(
            inputs=[thresh_gamma],
            name='ThresholdGain',
            xpos=thresh_gamma.xpos(),
            ypos=thresh_gamma.ypos() + 38)
        thresh_gain['value'].setExpression('parent.gain')

        # Spill Removal =======================================================

        # After the adjustments to the spill matte with gain and gamma, we
        # can now subtract the spill.
        subtract_spill = nuke.nodes.Merge2(
            inputs=[thresh_gain, main_switch],
            name='SubtractSpill',
            xpos=main_switch.xpos(),
            ypos=thresh_gain.ypos() + 6,
        )
        subtract_spill['operation'].setValue('minus')

        remove_negatives = nuke.nodes.Expression(
            inputs=[subtract_spill],
            name='RemoveNegatives',
            xpos=subtract_spill.xpos(),
            ypos=subtract_spill.ypos() + 26
        )
        remove_negatives['expr0'].setValue('r>0?r:0')
        remove_negatives['expr1'].setValue('g>0?g:0')
        remove_negatives['expr2'].setValue('b>0?b:0')

        # Balancing ===========================================================

        # These nodes, by way of adding or removing spill channel, determine
        # the resultant color balance of the shot.
        auto_balance = nuke.nodes.Expression(
            inputs=[remove_negatives],
            name='AutoBalance',
            xpos=remove_negatives.xpos() - 80,
            ypos=remove_negatives.ypos() + 100
        )

        # We'll be using these variables in the channel calculations
        #
        # Essentially, we're determining the multiplier value needed to get
        # from the despilled source color to the destination color.
        # Most of these calculations are determining what the despilled
        # color will look like.
        auto_balance['temp_name0'].setValue('bspill')
        auto_balance['temp_expr0'].setValue(
            'source.b - pow(source.r * (1 - Cross.mix) '
            '+ source.g * Cross.mix, 1 / (ThresholdGamma.value '
            '+ 0.000001) ) * ThresholdGain.value'
        )
        auto_balance['temp_name1'].setValue('gspill')
        auto_balance['temp_expr1'].setValue(
            'source.g - pow(source.r * (1 - Cross.mix) '
            '+ source.b * Cross.mix, 1 / (ThresholdGamma.value '
            '+ 0.000001) ) * ThresholdGain.value'
        )
        # This expression simply compares the two colors to determine which
        # spill calculation to use, then we'll that below.
        auto_balance['temp_name2'].setValue('spill')
        auto_balance['temp_expr2'].setValue(
            'source.g - source.b > 0 ? gspill : bspill'
        )

        auto_balance['expr0'].setValue(
            'r * (dest.r - source.r) / spill'
        )
        auto_balance['expr1'].setValue(
            'g * (dest.g - source.g) / spill'
        )
        auto_balance['expr2'].setValue(
            'b * (dest.b - source.b) / spill'
        )

        # Now we need to add the knobs it's referencing to the AutoBalance
        # node.
        auto_balance.addKnob(nuke.Tab_Knob('spillcontrols', 'Spill Controls'))
        auto_balance.addKnob(nuke.Color_Knob('source', 'Source Color'))
        auto_balance.addKnob(nuke.Color_Knob('dest', 'Destination Color'))
        auto_balance['source'].setValue([0.1, 0.2, 0.3])
        auto_balance['dest'].setValue([0.3, 0.3, 0.3])

        # Auto Balancing Tooltips
        auto_balance['source'].setTooltip(
            "Color of spill to remove. This color will be used to determine if "
            "the screen color is blue or green, based on which color channel"
            "has a higher value."
        )
        auto_balance['dest'].setTooltip(
            "Color to change the spill color to. This should be a sampled "
            "average of the background behind your character. This color is "
            "normally not the neutral grey most spill suppression corrects to. "
            "Spill suppression should not only suppress the spill color, but "
            "transform the spill and reflected spill to reflect the "
            "environment. This will lead to better edges and color. "
            "Extremely bright or dark values will break. Adjust values until "
            "result is no longer 'grainy.'"
        )

        # Manual Balancing
        manual_balance = nuke.nodes.Multiply(
            inputs=[remove_negatives],
            name='ManualBalance',
            channels='rgb',
            xpos=remove_negatives.xpos() + 80,
            ypos=auto_balance.ypos(),
        )
        # We need to set the values to trigger the channels to split.
        manual_balance['value'].setValue([0.1, 0.1, 0.1, 1])
        # But now we can set their expressions
        manual_balance['value'].setExpression('AutoBalance.dest.r', 0)
        manual_balance['value'].setExpression('AutoBalance.dest.g', 1)
        manual_balance['value'].setExpression('AutoBalance.dest.b', 2)

        auto_switch = nuke.nodes.Switch(
            inputs=[auto_balance, manual_balance],
            name='AutoManualSwitch',
            xpos=remove_negatives.xpos(),
            ypos=remove_negatives.ypos() + 200
        )
        auto_switch['which'].setExpression('parent.useManual')

        blur = nuke.nodes.Blur(
            inputs=[auto_switch],
            name='BlurSpill',
            xpos=auto_switch.xpos(),
            ypos=auto_switch.ypos() + 26
        )

        dot3 = nuke.nodes.Dot(
            inputs=[dot2],
            xpos=dot2.xpos(),
            ypos=blur.ypos() + 42,
        )

        remove_spill = nuke.nodes.Merge2(
            inputs=[dot3, blur],
            name='RemoveSpill',
            xpos=blur.xpos(),
            ypos=blur.ypos() + 38,
        )
        remove_spill['operation'].setValue('plus')

        # Output ==============================================================

        copy_channels = nuke.nodes.Copy(
            inputs=[dot3, remove_spill],
            name='ProtectAll',
            xpos=remove_spill.xpos(),
            ypos=remove_spill.ypos() + 100
        )
        copy_channels['from0'].setValue('rgba.red')
        copy_channels['from1'].setValue('rgba.green')
        copy_channels['from2'].setValue('rgba.blue')
        copy_channels['to0'].setValue('rgba.red')
        copy_channels['to1'].setValue('rgba.green')
        copy_channels['to2'].setValue('rgba.blue')

        nuke.nodes.Output(
            inputs=[copy_channels],
            xpos=copy_channels.xpos(),
            ypos=copy_channels.ypos() + 100
        )

        # =====================================================================
        # Knobs
        # =====================================================================

        set_link('source', groupmo, auto_balance)

        groupmo.addKnob(nuke.Text_Knob('source_divider', ''))

        set_link('chanMix', groupmo, cross)
        use_max = nuke.Boolean_Knob('useMax', 'use maximum for mix')
        use_max.clearFlag(nuke.STARTLINE)
        use_max.setTooltip(
            "Instead of averaging the alternate color channels, use a max "
            "operation to combine them."
        )
        groupmo.addKnob(use_max)

        gain = nuke.Array_Knob('gain', 'gain')
        gamma = nuke.Array_Knob('gamma', 'gamma')
        gamma.clearFlag(nuke.STARTLINE)
        gain.setValue(0.95)
        gamma.setValue(0.95)
        gain.setFlag(flags.SLIDER)
        gain.setFlag(flags.LOG_SLIDER)
        gamma.setFlag(flags.SLIDER)
        gamma.setFlag(flags.LOG_SLIDER)
        gain.setTooltip(
            "Multiples the spill threshold to increase or decrease what gets "
            "considered spill. Has a larger effect on brighter areas."
        )
        gamma.setTooltip(
            "Does a gamma operation on the spill threshold, which has a "
            "larger effect on midtones."
        )
        groupmo.addKnob(gain)
        groupmo.addKnob(gamma)

        set_link('size', groupmo, blur, label='blur spill')

        groupmo.addKnob(nuke.Text_Knob('destination_divider', ''))

        set_link('dest', groupmo, auto_balance)
        use_manual = nuke.Boolean_Knob('useManual', 'use for manual balancing')
        use_manual.clearFlag(nuke.STARTLINE)
        use_manual.setTooltip(
            "If selected, the Destination Color will instead become a manual "
            "gain control for the final result."
        )
        groupmo.addKnob(use_manual)

        # =====================================================================
        # Callbacks
        # =====================================================================

        groupmo['knobChanged'].setValue(
            'keying.SpillSuppress.disable_channel_mix_callback()'
        )
