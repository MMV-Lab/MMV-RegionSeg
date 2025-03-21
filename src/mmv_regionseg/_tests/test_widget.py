# Copyright © Peter Lampen, ISAS Dortmund, 2025
# (20.03.2025)

import pytest
import napari
import numpy as np
import qtpy
from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtTest import QTest
from qtpy.QtCore import Qt
from unittest import mock
from unittest.mock import patch
from pathlib import Path
from tifffile import imread, imwrite
from mmv_regionseg._widget import MMV_RegionSeg

# A single constant
PARENT = Path(__file__).parent / 'data'

# make_napari_viewer is a pytest fixture that returns a napari viewer object
# you don't need to import it, as long as napari is installed in your
# testing environment
@pytest.fixture
def region_seg(make_napari_viewer):
    # (20.03.2025) create a mmv_regionseg object and give it back
    viewer = make_napari_viewer()
    return MMV_RegionSeg(viewer)

@pytest.mark.init
def test_init(region_seg):
    # (12.09.2024)
    assert isinstance(region_seg, MMV_RegionSeg)
    assert region_seg.name == None
    assert region_seg.image == None
    assert region_seg.mask == None
    assert region_seg.tolerance == 10
    assert region_seg.color == 0
    assert region_seg.seed_points == []
    assert region_seg.layout() is not None
    assert isinstance(region_seg.layout(), QVBoxLayout)
    assert region_seg.lbl_tolerance.text() == 'Tolerance: 10'
