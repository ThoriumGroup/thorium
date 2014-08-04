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
from ..utils import (
    center_below, center_x, center_y, Groupmo, set_link, space_x
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = []

# =============================================================================
# CLASSES
# =============================================================================


class SpillSuppress(Groupmo):
    """Spill Suppression for the cultured class"""
    Class = 'SpillSuppress'

    @classmethod
    def setup(cls, groupmo):
        """blah"""

        # =====================================================================
        # Nodes
        # =====================================================================

        input_node = nuke.nodes.Input()
        dot = nuke.nodes.Dot(inputs=[input_node])
        center_below(dot, input_node, 100)

        def set_shuffle(shuffle, color):
            """Sets all the color channels of a shuffle to be the same color"""
            shuffle['red'].setValue(color)
            shuffle['green'].setValue(color)
            shuffle['blue'].setValue(color)
            shuffle['alpha'].setValue('white')

        # Shuffle to extract the green channel
        green_shuffle = nuke.nodes.Shuffle(
            inputs=[dot],
            name='Green'
        )
        center_below(green_shuffle, dot, 200)
        set_shuffle(green_shuffle, 'green')

        # Shuffle to extract the red channel
        red_shuffle = nuke.nodes.Shuffle(
            inputs=[dot],
            name='Red'
        )
        red_shuffle.setXYpos(
            green_shuffle.xpos() - 160,
            green_shuffle.ypos()
        )
        set_shuffle(red_shuffle, 'red')

        # Shuffle to extract the blue channel
        blue_shuffle = nuke.nodes.Shuffle(
            inputs=[dot],
            name='Blue'
        )
        blue_shuffle.setXYpos(
            space_x(green_shuffle),
            green_shuffle.ypos()
        )

        dot2 = nuke.nodes.Dot(
            inputs=[dot],
        )
        dot2.setXYpos(
            space_x(blue_shuffle),
            blue_shuffle.ypos()
        )

        # Switch Nodes
        # This will autoswitch from green primary to blue primary, depending
        # on which color has a higher value.
        main_switch = nuke.nodes.Switch(
            inputs=[blue_shuffle, green_shuffle],
            name='BGSwitch'
        )
        center_below(main_switch, blue_shuffle, 100)
        # We set this to an expression which looks at the AutoBalance node.
        # Expression Reads:
        # If AutoBalance's Source Color Green channel minus the Blue channel is
        # greater than 0, value should be 1. Else, value should be 0.
        main_switch['which'].setExpression(
            'AutoBalance.source.g-AutoBalance.source.b>0?1:0'
        )

        # Inverse Switch (will be the opposite of Main Switch)
        inverse_switch = nuke.nodes.Switch(
            inputs=[green_shuffle, blue_shuffle],
            name='BGSwitchInverse'
        )
        center_below(inverse_switch, green_shuffle, 100)

        # Mix Nodes
        # These nodes will determine how the alternate color channels
        # (the color channels that are NOT the spill channel) are mixed
        # together to help determine how much of the spill channel is spill.
        cross = nuke.nodes.Merge2(
            inputs=[red_shuffle, inverse_switch],
            name='Cross'
        )
        center_below(cross, red_shuffle, 200)
        cross['mix'].setValue(0.5)

        max = nuke.nodes.Merge2(
            inputs=[red_shuffle, inverse_switch],
            name='Max'
        )
        max.setXYpos(
            cross.xpos() - 160,
            cross.ypos(),
        )
        max['operation'].setValue('max')

        # Mix Switch will be a user controlled switch. When checked, it will
        # use the Max method instead of Crossing between the two.
        mix_switch = nuke.nodes.Switch(
            inputs=[cross, max],
            name='MaxOrCross'
        )
        center_below(mix_switch, max, 40)
        mix_switch['which'].setExpression('parent.useMax')

        # Threshold Controls
        # These control the ebb and flow of the spill mask.
        thresh_gamma = nuke.nodes.Gamma(
            inputs=[mix_switch],
            name='ThresholdGamma'
        )
        center_below(thresh_gamma, mix_switch)
        thresh_gamma['value'].setExpression('parent.gamma')

        thresh_gain = nuke.nodes.Multiply(
            inputs=[thresh_gamma],
            name='ThresholdGain'
        )
        center_below(thresh_gain, thresh_gamma)
        thresh_gain['value'].setExpression('parent.gain')

        # Spill Removal
        # After the adjustments to the spill matte with gain and gamma, we
        # can now subtract the spill.
        subtract_spill = nuke.nodes.Merge2(
            inputs=[thresh_gain, main_switch],
            name='SubtractSpill'
        )
        subtract_spill.setXYpos(
            center_x(subtract_spill, main_switch),
            center_y(subtract_spill, thresh_gain)
        )
        subtract_spill['operation'].setValue('minus')

        remove_negatives = nuke.nodes.Expression(
            inputs=[subtract_spill],
            name='RemoveNegatives'
        )
        center_below(remove_negatives, subtract_spill)
        remove_negatives['expr0'].setValue('r>0?r:0')
        remove_negatives['expr1'].setValue('g>0?g:0')
        remove_negatives['expr2'].setValue('b>0?b:0')

        # Balancing
        # These nodes, by way of adding or removing spill channel, determine
        # the resultant color balance of the shot.
        auto_balance = nuke.nodes.Expression(
            inputs=[remove_negatives],
            name='AutoBalance'
        )
        auto_balance.setXYpos(
            center_x(auto_balance, remove_negatives) - 180,
            remove_negatives.ypos() + 100
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
            'source.g-source.b>0?gspill:bspill'
        )

        auto_balance['expr0'].setValue('r * (dest.r - source.r) / spill')
        auto_balance['expr1'].setValue('g * (dest.g - source.g) / spill')
        auto_balance['expr2'].setValue('b * (dest.b - source.b) / spill')

        # Now we need to add the knobs it's referencing to the AutoBalance
        # node.
        auto_balance.addKnob(nuke.tab_knob('spillcontrols', 'Spill Controls'))
        auto_balance.addKnob(nuke.Color_Knob('source', 'source color'))
        auto_balance.addKnob(nuke.Color_Knob('dest', 'destination color'))
        auto_balance['source'].setValue([0.1, 0.2, 0.3])
        auto_balance['dest'].setValue([0.3, 0.3, 0.3])

        # Manual Balancing
        # Much easier.
        manual_balance = nuke.nodes.Multiply(
            inputs=[remove_negatives],
            name='ManualBalance',
            channels='rgb'
        )
        manual_balance.setXYpos(
            center_x(manual_balance, remove_negatives + 100),
            remove_negatives.ypos() + 100
        )
        # We need to set the values to trigger the channels to split.
        manual_balance['value'].setValue([0.1, 0.1, 0.1, 1])
        # But now we can set their expressions
        manual_balance['value'].setExpression('parent.manual.r', 0)
        manual_balance['value'].setExpression('parent.manual.g', 1)
        manual_balance['value'].setExpression('parent.manual.b', 2)

        auto_switch = nuke.nodes.Switch(
            inputs=[auto_balance, manual_balance],
            name='AutoManualSwitch'
        )
        center_below(auto_switch, remove_negatives, 200)
        auto_switch['which'].setExpression('parent.useManual')

        blur = nuke.nodes.Blur(
            inputs=[auto_switch],
            name='BlurSpill',
        )
        center_below(blur, auto_switch)

        dot3 = nuke.nodes.Dot(
            inputs=[dot2]
        )
        dot3.setXYpos(
            dot2.xpos(),
            blur.ypos()
        )

        remove_spill = nuke.nodes.Merge2(
            inputs=[dot3, blur],
            name='RemoveSpill'
        )
        center_below(remove_spill, blur, 50)
        remove_spill['operation'].setValue('plus')

        copy_channels = nuke.nodes.Copy(
            inputs=[dot3, remove_spill],
            name='ProtectAll'
        )
        copy_channels['from_0'].setValue('rgba.red')
        copy_channels['from_1'].setValue('rgba.green')
        copy_channels['from_2'].setValue('rgba.blue')
        center_below(copy_channels, remove_spill, 100)

        output_node = nuke.nodes.Output(
            inputs=[copy_channels],
        )
        center_below(output_node, copy_channels)

        # =====================================================================
        # Knobs
        # =====================================================================

        set_link('source', groupmo, auto_balance)

        groupmo.addKnob(nuke.Text_Knob('source_divider', ''))

        set_link('mix', groupmo, cross, label='channel mix')
        use_max = nuke.Bool_Knob('useMax', 'use maximum for mix')
        use_max.clearFlag(nuke.STARTLINE)
        groupmo.addKnob(use_max)

        gain = nuke.Float_Knob('gain', 'gain')
        gamma = nuke.Float_Knob('gamma', 'gamma')
        gamma.clearFlag(nuke.STARTLINE)
        groupmo.addKnob(gain)
        groupmo.addKnob(gamma)

        set_link('size', groupmo, blur, label='blur spill')

        groupmo.addKnob(nuke.Text_Knob('destination_divider', ''))

        set_link('dest', groupmo, auto_balance)

        groupmo.addKnob(nuke.Color_Knob('manual', 'manual balance'))
        use_manual = nuke.Bool_Knob('useManual', 'use manual balancing')
        use_manual.clearFlag(nuke.STARTLINE)
        groupmo.addKnob(use_manual)
