# Copyright © Peter Lampen, ISAS Dortmund, 2025
# (20.03.2025)

from pathlib import Path
import pytest
import napari
import numpy as np
import qtpy
from qtpy.QtCore import Qt
from qtpy.QtTest import QTest
from qtpy.QtWidgets import QVBoxLayout, QWidget
from unittest import mock
from unittest.mock import patch
from tifffile import imread, imwrite
from mmv_regionseg._widget import ExampleQWidget

@pytest.fixture
def widget(make_napari_viewer):
    # (20.03.2025)
    return ExampleQWidget(make_napari_viewer())

@pytest.mark.init
def test_init(widget):
    # (12.09.2024)
    assert isinstance(widget, QWidget)              # Base class of ExampleQWidget
    assert isinstance(widget, ExampleQWidget)
    assert issubclass(ExampleQWidget, QWidget)      # Is QWidget the base class?
    assert isinstance(widget.viewer, napari.Viewer)
    assert isinstance(widget.layout(), QVBoxLayout)
    assert widget.name == None
    assert widget.image == None
    assert widget.tolerance == 10
    assert widget.dynamic_range == [0.0, 255.0]
    assert np.array_equal (widget.footprint, np.ones([3, 3, 3], dtype=int))
    assert widget.color == 0
    assert widget.lbl_tolerance.text() == 'Tolerance: 10 % (25.50)'
