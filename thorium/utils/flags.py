#!/usr/bin/env python
"""

Thorium Utils Flags
===================

Nuke Knob Flags which can be difficult to access due to Nuke not storing
readily available variables for them, forcing the use the integer values as
seen below.

Any of these flags can now be used with:
::
    from thorium.utils import flags

And then when needed:
::
    gain = nuke.Array_Knob('gain')
    gain.setFlag(flags.SLIDER)
    gain.setFlag(flags.LOG_SLIDER)

Non-PEP8 Styling is used within this script to preserve readability.

## Version Restrictions

Flags new in 6.3:

    * KNOB_CHANGED_RECURSIVE
    * MODIFIES_GEOMETRY
    * OUTPUT_ONLY
    * NO_KNOB_CHANGED_FINISHED
    * SET_SIZE_POLICY
    * EXPAND_TO_WIDTH

Flags new in 6.2:

    * READ_ONLY
    * GRANULARY_UNDO
    * NO_RECURSIVE_PATHS

## License

The MIT License (MIT)

Flags
Copyright (c) 2010-2014 John R.A. Benson

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
# GLOBALS
# =============================================================================


# General Flags ===============================================================

# Must not intersect any class-specific flags

DISABLED            = 0x0000000000000080    # DISABLED Set by disable(), cleared by enable().

NO_ANIMATION        = 0x0000000000000100    # NO_ANIMATION Prevent the value from being animated.
                                            #   This removes any anymation or view buttons, and
                                            #   it stops tcl expressions from being evaluated in
                                            #   string knobs, and may make it ignore attempts to
                                            #   set expressions or key frames (nyi).

DO_NOT_WRITE        = 0x0000000000000200    # DO_NOT_WRITE Don't ever save this knob to a script
                                            #   (including copy & paste!)

INVISIBLE           = 0x0000000000000400    # INVISIBLE The knob does not appear in the panels.
                                            #   No widgets are created. This is not the same
                                            #   as hide(), and show() will not undo it!

RESIZABLE           = 0x0000000000000800    # RESIZABLE The knob can stretch in the panel so
                                            #   that it fills up all the remaining space in the line.
                                            #   Defaults to true for most of the complex knobs,
                                            #   but off for buttons, checkmarks, and pulldown lists.

STARTLINE           = 0x0000000000001000    # STARTLINE This knob starts a new row in the panel.
                                            #   The default is true unless a zero-length (not NULL)
                                            #   string is passed as the label. Currently the default
                                            #   is false for checkmarks and buttons but this may
                                            #   change in future versions.

ENDLINE             = 0x0000000000002000    # ENDLINE This knob will end a row, acts exactly
                                            #    like STARTLINE was set on the next knob.
                                            #   Set true for divider lines.

NO_RERENDER         = 0x0000000000004000    # NO_RERENDER This knob does not contribute to the
                                            #   hash value for the op. This should be used on knobs
                                            #   that have no effect on the op's output.

NO_HANDLES          = 0x0000000000008000    # NO_HANDLES Don't draw anything in the viewer,
                                            #   this is useful if the Op draws it's own indicators.

KNOB_CHANGED_ALWAYS = 0x0000000000010000    # KNOB_CHANGED_ALWAYS will call node()->knob_changed()
                                            #   every time the value of the knob changes. Normally
                                            #   it is only called if the user changes the value with
                                            #   the panel open. This allows you to track all changes to
                                            #   the value. Be careful as knob_changed() will be called
                                            #   without storing the new values into your structure.

NO_KNOB_CHANGED     = 0x0000000000020000    # NO_KNOB_CHANGED: Don't bother calling Op::knob_changed()
                                            #   with this knob. This is turned on automatically
                                            #   if the knob_changed() returns false.

HIDDEN              = 0x0000000000040000    # HIDDEN Set by hide(), cleared by show().

NO_UNDO             = 0x0000000000080000    # NO_UNDO Don't undo/redo any changes to this knob.
                                            #   May be replaced with "output knob" in the future.

ALWAYS_SAVE         = 0x0000000000100000    # ALWAYS_SAVE save the knob to a script even if not_default()
                                            #   returns false. *Deprecated*, instead override
                                            #   not_default() and make it return true!

NODE_KNOB           = 0x0000000000200000    # NODE_KNOB is used by Nuke internally for controls on
                                            #   the DAG appearance such as xpos and ypos.

HANDLES_ANYWAY      = 0x0000000000400000    # HANDLES_ANYWAY makes the handles appear in the viewer when
                                            #    the panel is open even if a different tab is selected.

READ_ONLY           = 0x0000000010000000    # knob cannot be modified by UI intervention but can
                                            #   still be copied from etc


# Internal Use Flags ==========================================================

INDETERMINATE       = 0x0000000000800000
COLOURCHIP_HAS_UNSET = 0x0000000001000000   #/< whether a color chip can be in the 'unset' state,
                                            #   DEFAULTS TO FALSE

SMALL_UI            = 0x0000000002000000
NO_NUMERIC_FIELDS   = 0x0000000004000000
NO_CURVE_EDITOR     = 0x0000000020000000
NO_MULTIVIEW        = 0x0000000040000000
EARLY_STORE         = 0x0000000080000000

KNOB_CHANGED_RECURSIVE = 0x0000000008000000 # 6.3 recursive knobChanged calls are guarded against.
                                            #   To override the non-recursion on a particular knob,
                                            #   specify this flag

MODIFIES_GEOMETRY   = 0x0000000100000000    # 6.3 MODIFIES_GEOMETRY should be set for any knob
                                            #   that modifies geometry, either by affecting the
                                            #   internal geometry directly or by changing its transform

OUTPUT_ONLY         = 0x0000000200000000    # 6.3
NO_KNOB_CHANGED_FINISHED    = 0x0000000400000000 # 6.3
SET_SIZE_POLICY     = 0x0000000800000000    # 6.3
EXPAND_TO_WIDTH     = 0x0000001000000000    # 6.3 Just for enum knobs currently


# Numeric Knob Flags ==========================================================

MAGNITUDE           = 0x0000000000000001    # MAGNITUDE If there are several numbers, this enables a
                                            #    button to only show a single number, and all are set
                                            #    equal to this number. Default is true for WH_knob()
                                            #    and Color_knob().

SLIDER              = 0x0000000000000002    # SLIDER Turns on the slider. Currently this only works if
                                            #   the size is 1 or MAGNITUDE is enabled and it is set
                                            #   to single numbers.
                                            #   Defaults to on for most non-integer numerical controls.

LOG_SLIDER          = 0x0000000000000004    # LOG_SLIDER Tick marks on the slider (if enabled with SLIDER)
                                            #   are spaced logarithmically. This is turned on for
                                            #   WH_knob() and Color_knob(), and if the range has both
                                            #   ends greater than zero. If you turn this on and the
                                            #   range passes through zero, the scale is actually the cube
                                            #   root of the number, not the logarithim.

STORE_INTEGER       = 0x0000000000000008    # STORE_INTEGER Only integer values should be displayed/stored

FORCE_RANGE         = 0x0000000000000010    # FORCE_RANGE Clamps the value to the range when storing.

ANGLE               = 0x0000000000000020    # ANGLE Turn on a widget depicting this number as an angle.

NO_PROXYSCALE       = 0x0000000000000040    # NO_PROXYSCALE disables proxy scaling for XY or WH knobs.
                                            #   Useful if you just want two numbers called "x" and "y"
                                            #   that are not really a position.
                                            #   You probably also want to do NO_HANDLES.


# String Knob Flags ===========================================================

GRANULAR_UNDO       = 0x0000000000000001
NO_RECURSIVE_PATHS  = 0x0000000000000002


# Enumeration Knob Flags ======================================================

SAVE_MENU           = 0x0000000002000000    # SAVE_MENU writes the contents of the menu to the saved
                                            #   script. Useful if your plugin modifies the list of items.

# BeginGroup Knob Flags =======================================================

CLOSED              = 0x0000000000000001    # CLOSED True for a BeginGroup knob that is closed
TOOLBAR_GROUP       = 0x0000000000000002    # Make the group into a viewer toolbar
TOOLBAR_LEFT        = 0x0000000000000000    # Position in the viewer. Only set one of these:
TOOLBAR_TOP         = 0x0000000000000010
TOOLBAR_BOTTOM      = 0x0000000000000020
TOOLBAR_RIGHT       = 0x0000000000000030
TOOLBAR_POSITION    = 0x0000000000000030    # A mask for the position part of the flags


# ChannelSet/Channel Knob Flags ===============================================

NO_CHECKMARKS       = 0x0000000000000001    # NO_CHECKMARKS Get rid of the individual channel checkmarks.

NO_ALPHA_PULLDOWN   = 0x0000000000000002    # NO_ALPHA_PULLDOWN Get rid of the extra pulldown that lets
                                            #   you set the 4th channel to an arbitrary different layer
                                            #   than the first 3.

# Format Knob Flags ===========================================================
PROXY_DEFAULT       = 0x0000000000000001    # PROXY_DEFAULT makes the default value be the
                                            #   root.proxy_format rather than the root.format.

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'ALWAYS_SAVE',
    'ANGLE',
    'CLOSED',
    'COLOURCHIP_HAS_UNSET',
    'DISABLED',
    'DO_NOT_WRITE',
    'EARLY_STORE',
    'ENDLINE',
    'EXPAND_TO_WIDTH',
    'FORCE_RANGE',
    'GRANULAR_UNDO',
    'HANDLES_ANYWAY',
    'HIDDEN',
    'INDETERMINATE',
    'INVISIBLE',
    'KNOB_CHANGED_ALWAYS',
    'KNOB_CHANGED_RECURSIVE',
    'LOG_SLIDER',
    'MAGNITUDE',
    'MODIFIES_GEOMETRY',
    'NODE_KNOB',
    'NO_ALPHA_PULLDOWN',
    'NO_ANIMATION',
    'NO_CHECKMARKS',
    'NO_CURVE_EDITOR',
    'NO_HANDLES',
    'NO_KNOB_CHANGED',
    'NO_KNOB_CHANGED_FINISHED',
    'NO_MULTIVIEW',
    'NO_NUMERIC_FIELDS',
    'NO_PROXYSCALE',
    'NO_RECURSIVE_PATHS',
    'NO_RERENDER',
    'NO_UNDO',
    'OUTPUT_ONLY',
    'PROXY_DEFAULT',
    'READ_ONLY',
    'RESIZABLE',
    'SAVE_MENU',
    'SET_SIZE_POLICY',
    'SLIDER',
    'SMALL_UI',
    'STARTLINE',
    'STORE_INTEGER',
    'TOOLBAR_BOTTOM',
    'TOOLBAR_GROUP',
    'TOOLBAR_LEFT',
    'TOOLBAR_POSITION',
    'TOOLBAR_RIGHT',
    'TOOLBAR_TOP',
]
