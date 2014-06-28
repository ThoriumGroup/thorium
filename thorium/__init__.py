#!/usr/bin/env python
"""

Thorium
=======

Thorium is a project that combines various python modules and tools originally
sourced from Nukepedia. It provides a streamlined way of managing their
versions and  customizing the installation. While thorium ships as a complete
package, individual submodules can be activated and deactivated via config
files or arguments passed to thorium.

## Installation

Before we get into installation, a quick warning. Thorium is made up of many
submodules that are designed and still released to work independent of
thorium. When thorium imports those modules, it imports them into the global
namespace so that Nuke can access the modules directly, without having to go
through the thorium namespace. It does this by directly accessing and importing
straight into the `__builtin__` namespace. This is normally not recommended.

While every effort has been made to ensure that these submodules are named
uniquely, the python namespace can get very tricky and managers of facility
installations should carefully compare the modules thorium is set to import
with any global facility modules, otherwise those facility modules will
be inaccessible from within Nuke.

Installation can be done via pip (`pip install thorium`), an rpm or by manually
placing the 'thorium' folder in your .nuke directory or anywhere else within
the Nuke python path.

Then, add the following lines to your 'init.py' file:
::
    import thorium
    thorium.run()

And the following lines to your 'menu.py' file:
::
    import thorium
    thorium.run_gui()

You can turn off the usage of specific modules by passing a dictionary with the
module name and a bool.
::
    import thorium
    thorium.run_gui({'animatedSnap3D': False})

Now `animatedSnap3D` will not load, and every other module will. You can
reverse this behavior by passing the `default` argument `False`, which will
cause all modules not specifically listed as True to not be loaded.
::
    import thorium
    thorium.run_gui({'animatedSnap3D': True}, default=False)

Now `animatedSnap3D` will be the ONLY module that loads- all others will not
load, since the default is False.

## Usage

After the run functions above have executed, each submodule will be available
in it's native namespace. Modules with menu items will appear in their correct
place, and the python commands will be available for use from anywhere in Nuke.

## Classes

    GlobalInjector
        Injects set attributes directly into the global namespace. Thorium
        uses this to import modules into '__builtin__'

## Public Functions

    run()
        Imports and runs the thorium submodules that should be available to
        nuke and scripts at all times.

    run_gui()
        Imports and runs the thorium submodules that are only needed to user
        interaction in the GUI.

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
# GLOBALS
# =============================================================================

__author__ = "Sean Wallitsch"
__author_email__ = "sean@grenadehop.com"
__copyright__ = "Copyright 2014, Sean Wallitsch"
__credits__ = [
    "Ivan Busquets",
    "Alexey Kuchinski",
    "Frank Rueter",
    "Sean Wallitsch",
]
__license__ = "MIT"
__version__ = "0.1b3"
__maintainer__ = "Sean Wallitsch"
__maintainer_email__ = "sean@grenadehop.com"
__module_name__ = "thorium"
__short_desc__ = "Combines and manages many Nuke python packages"
__status__ = "Development"
__url__ = "https://github.com/ThoriumGroup/thorium"

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'run',
    'run_gui'
]

# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


def _importer(module):
    """Imports and returns the given string as a module"""
    return __import__(module, globals())

# =============================================================================
# CLASSES
# =============================================================================


class GlobalInjector(object):
    """Inject into the global namespace of "__builtin__"

    Assigning to variables declared global in a function, injects them only
    into the module's global namespace.

    >>> global_namespace = sys.modules['__builtin__'].__dict__
    >>> #would need
    >>> global_namespace['aname'] = 'avalue'
    >>> #With
    >>> global_namespace = GlobalInjector()
    >>> #one can do
    >>> global_namespace.bname = 'bvalue'
    >>> #reading from it is simply
    >>> bname
    bvalue

    Class is from the following stackoverflow:

    http://stackoverflow.com/questions/11813287/insert-variable-into-global-namespace-from-within-a-function

    """
    def __init__(self):
        import sys
        self.__dict__['modules'] = []
        self.__dict__['builtin'] = sys.modules['__builtin__'].__dict__

    def __setattr__(self, name, value):
        """Adds an object to the __builtin__ namespace under name.

        While this can be used to inject any object into the __builtin__
        namespace, it's particularly useful for importing.

        >>> global_namespace = GlobalInjector()
        >>> global_namespace.random = __import__("random", globals())
        >>> random.randint(0, 100)
        67

        `random` has now been imported into the global namespace. This works
        even when global_namespace is within a local scope.

        Args:
            name : (str)
                The variable name the module should be added under.

            value : (<module>|any other object)
                The python object to be referenced by name.

        Returns:
            None

        Raises:
            N/A

        """
        self.builtin[name] = value
        self.modules.append(name)

    def reset(self):
        """ Removes the objects that GlobalInjector has placed in the namespace

        Note that when used for imported modules, this does not reload, or
        uncache the modules.

        This is mostly useful for testing.

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        for module in self.modules:
            if module in self.builtin:
                del(self.builtin[module])

        self.modules = []

# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================


def run(modules=None, default=True):
    """Imports and runs the submodules that must be available at all times"""
    global_namespace = GlobalInjector()

    if not modules:
        modules = {}
    pass

# =============================================================================


def run_gui(modules=None, default=True, menu_name='Thorium'):
    """Imports and runs gui only submodules"""
    global_namespace = GlobalInjector()

    if not modules:
        modules = {}

    if modules.get('animatedSnap3D', default):
        global_namespace.animatedSnap3D = _importer('animatedSnap3D')
        animatedSnap3D.run()

    if modules.get('cardToTrack', default):
        global_namespace.cardToTrack = _importer('cardToTrack')
        cardToTrack.run(menu=menu_name)

    if modules.get('iconPanel', default):
        global_namespace.iconPanel = _importer('iconPanel')
        iconPanel.run()
