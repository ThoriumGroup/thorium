#!/usr/bin/env python
"""
Tests the top level functions and classes of thorium

REQUIREMENTS:

mock
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Imports
import mock
import sys
import unittest

sys.path.append('../')

# Thorium Imports
import thorium

# =============================================================================
# GLOBALS
# =============================================================================

BUILTINS = dict(sys.modules['__builtin__'].__dict__)

# =============================================================================
# TEST CLASSES
# =============================================================================


class testGlobalInjector(unittest.TestCase):
    """Tests the GlobalInjector() class"""

    # =========================================================================
    # SETUP & TEARDOWN
    # =========================================================================

    def setUp(self):
        self.global_injector = None

    def tearDown(self):
        try:
            self.global_injector.reset()
        except AttributeError:
            pass

    # =========================================================================
    # TESTS
    # =========================================================================

    def test_inject_single(self):
        """Tests that a single module gets inserted into namespace"""

        self.assertTrue(
            'string' not in sys.modules['__builtin__'].__dict__
        )

        self.assertEqual(
            BUILTINS,
            sys.modules['__builtin__'].__dict__
        )

        self.global_injector = thorium.GlobalInjector()
        self.global_injector.string = thorium._importer('string')

        self.assertEqual(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            string.ascii_uppercase
        )

    # =========================================================================

    def test_reset(self):
        """Tests resetting the global namespace"""

        self.assertTrue(
            'random' not in sys.modules['__builtin__'].__dict__
        )

        self.global_injector = thorium.GlobalInjector()
        self.global_injector.random = thorium._importer('random')

        self.assertEqual(
            0,
            random.randint(0, 0)
        )

        self.global_injector.reset()

        self.assertTrue(
            'random' not in sys.modules['__builtin__'].__dict__
        )

    # =========================================================================

    def test_empty(self):
        """Just makes sure nothing is in the builtin dict that we use"""

        self.assertTrue(
            'random' not in sys.modules['__builtin__'].__dict__
        )

        self.assertTrue(
            'string' not in sys.modules['__builtin__'].__dict__
        )


class testRunGui(unittest.TestCase):
    """Tests the run_gui function"""

    # =========================================================================
    # TESTS
    # =========================================================================

    @mock.patch('thorium._importer')
    def test_no_imports(self, mock_importer):
        """Tests run_gui with no imports"""

        thorium.run_gui(default=False)

        self.assertFalse(
            mock_importer.called
        )

    # =========================================================================

    @mock.patch('thorium._importer')
    @mock.patch('thorium.animatedSnap3D.run')
    def test_animated_snap_imported(self, mock_module, mock_importer):
        """Tests that animatedSnap3D is imported by default"""

        thorium.run_gui({'animatedSnap3D': True}, default=False)

        mock_importer.assert_called_once_with('animatedSnap3D')
        mock_module.assert_called_once_with()

    # =========================================================================

    @mock.patch('thorium._importer')
    @mock.patch('thorium.cardToTrack.run')
    def test_card_to_track_imported(self, mock_module, mock_importer):
        """Tests that animatedSnap3D is imported by default"""

        thorium.run_gui({'cardToTrack': True}, default=False)

        mock_importer.assert_called_once_with('cardToTrack')
        mock_module.assert_called_once_with(menu='Thorium')

# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    unittest.main()