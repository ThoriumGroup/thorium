
Thorium
=======

Thorium combines various python modules and tools originally sourced from
Nukepedia. It provides a streamlined way of managing their versions and
customizing the installation. While thorium ships as a complete package,
individual submodules can be activated and deactivated via config files or
arguments passed to thorium.

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

## Usage

After the run functions above have executed, each submodule will be available
in it's native namespace. Modules with menu items will appear in their correct
place, and the python commands will be available for use from anywhere in Nuke.

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
