#!/usr/bin/env python
"""

Thorium Utils
=============

Useful python utilities for Nuke included within the Thorium package.

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

# Local Imports
from . import flags
from .nodes import (allNodes, center_below, center_x, center_y,
                    connect_inline, node_height, node_width,
                    set_link, space_x, space_y)
from .groupmo import Groupmo, normalize_docstring

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'allNodes',
    'center_below',
    'center_x',
    'center_y',
    'connect_inline',
    'flags',
    'Groupmo',
    'node_height',
    'node_width',
    'normalize_docstring',
    'set_link',
    'space_x',
    'space_y',
]
