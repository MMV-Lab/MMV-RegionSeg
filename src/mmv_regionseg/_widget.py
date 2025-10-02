"""
_widget.py
==========

This module provides a QWidget for region segmentation in Napari using
``skimage.segmentation.flood``.

Classes
-------
ExampleQWidget
    Napari plugin widget for interactive region segmentation.
"""

# Copyright © Peter Lampen, ISAS Dortmund, 2025
# (06.03.2025)

from typing import TYPE_CHECKING

import napari
import numpy as np
from pathlib import Path
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QShortcut,
    QWidget
)
from skimage.morphology import ball
from skimage.segmentation import flood, flood_fill
from tifffile import imread

if TYPE_CHECKING:
    import napari


class ExampleQWidget(QWidget):
    """
    Widget for a Napari plugin for region segmentation using
    skimage.segmentation.flood

    Parameters
    ----------
    viewer : class napari.viewer.Viewer

    Attributes
    ----------
    viewer : class napari.viewer.Viewer
    name : str
        Name of the input image
    image : numpy.ndarray
        Input image
    tolerance : int or float
        tolerance for the function skimage.segmentation.flood
    dynamic_range : list of float
        Dynamic range of the input image
    footprint : numpy.ndarray
        footprint for the function skimage.segmentation.flood
    color : int
        Sequential label ID
    lbl_tolerance : str
        QLabel for the tolerance slider
    """

    # (06.03.2025)
    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        """
        Initialize the ExampleQWidget.
        
        Parameters
        ----------
        viewer : napari.viewer.Viewer
            The Napari viewer instance in which this widget operates.
        """
        super().__init__()
        self.viewer = viewer
        self.name = None
        self.image = None
        self.tolerance = 10
        self.dynamic_range = [0.0, 255.0]
        self.footprint = np.ones([3, 3, 3], dtype=int)
        self.color = 0

        # Define a vbox for the main widget
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        # Headline 'MMV REgion Segmentation'
        lbl_headline = QLabel('MMV Region Segmentation')
        vbox.addWidget(lbl_headline)

        # Button 'Read image'
        btn_read = QPushButton('Read image')
        btn_read.clicked.connect(self.read_image)
        vbox.addWidget(btn_read)

        # Label 'Tolerance: x'
        self.lbl_tolerance = QLabel('Tolerance: 10 % (25.50)')
        vbox.addWidget(self.lbl_tolerance)

        # Slider for the tolerance
        sld_tolerance = QSlider(Qt.Horizontal)
        sld_tolerance.setRange(0, 100)
        sld_tolerance.setValue(10)
        sld_tolerance.valueChanged.connect(self.change_tolerance)
        vbox.addWidget(sld_tolerance)

        # Label 'Footprint'
        lbl_footprint = QLabel('Footprint')
        vbox.addWidget(lbl_footprint)

        # Combo box for the foodprint
        cbx_footprint = QComboBox()
        cbx_footprint.addItems(['6 neighbors', '18 neighbors', '26 neighbors'])
        cbx_footprint.setCurrentIndex(2)
        cbx_footprint.currentIndexChanged.connect(self.new_footprint)
        vbox.addWidget(cbx_footprint)

        # Button 'Select seed points'
        btn_seed_points = QPushButton('Select seed points')
        btn_seed_points.clicked.connect(self.new_seed_points)
        vbox.addWidget(btn_seed_points)

        # Button 'Start flood'
        btn_flood = QPushButton('Flood')
        btn_flood.clicked.connect(self.start_flood)
        vbox.addWidget(btn_flood)

        # Button 'Growth'
        btn_growth = QPushButton('Growth')
        btn_growth.clicked.connect(self.growth_tool_3d)
        vbox.addWidget(btn_growth)

    def read_image(self):
        """
        Requests the file name, reads the image file, and displays the image in
        Napari.
        """

        filter1 = 'TIFF files (*.tif *.tiff);;All files (*.*)'
        filename, _ = QFileDialog.getOpenFileName(self, 'Image file', '',
            filter1)
        if filename == '':                      # Cancel has been pressed
            print('The "Cancel" button has been pressed.')
            return
        else:
            path = Path(filename)
            self.name = path.stem               # Name of the file
            extension = path.suffix.lower()     # File extension

        # Load the image file
        if extension != '.tif' and extension != '.tiff':
            print('Unknown file type: %s!' % (extension))
            return
        else:
            print('Load', path)
            try:
                QApplication.setOverrideCursor(Qt.CrossCursor)
                self.image = imread(path)
            except BaseException as error:
                print('Error:', error)
                return
            finally:
                QApplication.restoreOverrideCursor()

        self.viewer.add_image(self.image, name=self.name)   # Show the image

        # determine the dynamic range of the image
        min1 = np.min(self.image)
        max1 = np.max(self.image)
        self.dynamic_range = [min1, max1]
        print('dynamic range:', self.dynamic_range)

    def change_tolerance(self, value: int):
        """
        Update the tolerance value based on the slider input.

        The tolerance is calculated as a percentage of the image
        dynamic range and displayed in the ``lbl_tolerance`` label.

        Parameters
        ----------
        value : int
            Percentage value (0–100) from the slider.
        """

        # (06.03.2025)
        delta = self.dynamic_range[1] - self.dynamic_range[0]
        self.tolerance = value * delta / 100.0
        self.lbl_tolerance.setText('Tolerance: %d %% (%.2f)' % (value,
            self.tolerance))

    def new_footprint(self, i: int):
        """
        Callback for the drop-down list cbx_footprint

        Depending on the value of parameter i, one of three variants is
        selected for the Footprint attribute.

        Parameters
        ----------
        i : int
            Index for selecting a footprint for skimage.segmentation.flood.
        """

        if i == 0:
            self.footprint = np.zeros([3, 3, 3], dtype=int)
            self.footprint[0, 1, 1] = 1
            self.footprint[1, 0, 1] = 1
            self.footprint[1, 1, 0] = 1
            self.footprint[1, 1, 1] = 1
            self.footprint[1, 1, 2] = 1
            self.footprint[0, 2, 1] = 1
            self.footprint[2, 1, 1] = 1
        elif i == 1:
            self.footprint = np.ones([3, 3, 3], dtype=int)
            self.footprint[0, 0, 0] = 0
            self.footprint[0, 0, 2] = 0
            self.footprint[0, 2, 0] = 0
            self.footprint[0, 2, 2] = 0
            self.footprint[2, 0, 0] = 0
            self.footprint[2, 0, 2] = 0
            self.footprint[2, 2, 0] = 0
            self.footprint[2, 2, 2] = 0
        elif i == 2:
            self.footprint = np.ones([3, 3, 3], dtype=int)

    def new_seed_points(self):
        """
        Create a new points layer in napari for seed selection.

        The layer is initialized empty and set to 'add' mode so that
        the user can place seed points interactively in the viewer.
        """

        # (02.04.2025)
        self.points_layer = self.viewer.add_points(data=np.empty((0, 3)),
            size=10, border_color='blue', face_color='red', name='seed points')
        self.points_layer.mode = 'add'

    def start_flood(self):
        """
        Creates a new label layer using the skimage.segmentation.flood function.

        The points defined in the points layer are used as starting points to
        create a label layer. The attributes footprint and tolerance are used
        for this purpose.
        """

        # (07.03.2025)
        # Create a list of coordinate tuples from the ndarray.
        points = self.points_layer.data
        seed_points = [tuple(map(round, row)) for row in points]

        # Determine a mask that corresponds to flood()
        self.color += 1
        mask = np.zeros(self.image.shape, dtype=int)
        for point in seed_points:
            flood_mask = flood(self.image, point, footprint=self.footprint,
                tolerance=self.tolerance)
            flood_mask = flood_mask.astype(int) * self.color
            mask += flood_mask

        # Store the flood mask in a label layer
        self.viewer.add_labels(mask, name='flood_mask')

        # Delete the points layer for the next run.
        if self.points_layer in self.viewer.layers:
            self.viewer.layers.remove(self.points_layer)

    def growth_tool_3d(self):
        """
        Callback for the btn_growth button.

        Using the starting points from the points layer, a mask is calculated
        with the flood function. A sphere with a small radius is placed around
        the starting point. This sphere is intersected with the mask and the
        intersection is displayed as a label layer. The radius of the sphere
        is then increased and the previous steps are repeated until the mask
        is completely enclosed by the sphere.
        """

        # (26.03.2025)
        points = self.points_layer.data
        seed_points = [tuple(map(round, row)) for row in points]

        # Set some start values
        shape = self.image.shape
        self.color += 1

        # Initialize and add the mask
        mask = np.zeros(shape, dtype=int)
        label_layer = self.viewer.add_labels(mask, name='growth_mask')

        for point in seed_points:
            flood_mask = flood(self.image, point, footprint=self.footprint,
                tolerance=self.tolerance)
            radius = 0              # Start radius
            step = 10               # Growth step (radius increase)
            sum0 = 0                # Number of pixels

            go_on = True
            while go_on:
                print('.', end='', flush=True)
                radius += step
                sphere = self.new_sphere(point, radius, shape)

                # Update the mask in Napari
                mask1 = flood_mask & sphere
                mask1 = mask1.astype(int)
                sum1 = np.sum(mask1)
                mask1 *= self.color
                mask = mask | mask1

                label_layer.data = mask
                label_layer.refresh()           # Force an update of the layer
                QApplication.processEvents()    # Qt forces rendering

                if sum1 > sum0:                 # additional points were found
                    sum0 = sum1                 # save sum for next loop
                else:
                    go_on = False               # terminate loop
            print(' ', sum1, 'pixels')

        # Delete the points layer for the next run.
        if self.points_layer in self.viewer.layers:
            self.viewer.layers.remove(self.points_layer)

    def new_sphere(self, seed_point: tuple[int, int, int], radius: int,
        shape: tuple[int, int, int]):
        """
        Create a spherical mask around a given seed point.

        Parameters
        ----------
        seed_point : tuple of int
            Center of the sphere (z, y, x).
        radius : int
            Radius of the shere in pixels.
        shape : tuple
            Shape of the image volume (z, y, x).

        Returns
        -------
        numpy.ndarray of bool
            Boolean mask of the same shape as the image, with ``True`` values
            inside the sphere.
        """

        # (25.03.2025) Expands the mask each time
        sphere = ball(radius)

        # Spherical mask has a shape (d, h, w) where d=depth, h=height, w=width
        d, h, w = sphere.shape
        center = (d // 2, h // 2, w // 2)

        # Find all points within the sphere, rr=row, cc=column, zz=depth
        rr, cc, zz = np.where(sphere > 0)

        # Calculate absolute coordinates
        rr += (seed_point[0] - center[0])
        cc += (seed_point[1] - center[1])
        zz += (seed_point[2] - center[2])

        # Filter invalid indices, which are outside the image
        valid = (rr >= 0) & (rr < shape[0]) & \
                (cc >= 0) & (cc < shape[1]) & \
                (zz >= 0) & (zz < shape[2])
        rr, cc, zz = rr[valid], cc[valid], zz[valid]

        # Update the sphere
        sphere = np.full(shape, False)
        sphere[rr, cc, zz] = True

        return sphere
