 # Copyright © Peter Lampen, ISAS Dortmund, 2025
# (06.03.2025)

from typing import TYPE_CHECKING

import napari
import numpy as np
from pathlib import Path
from qtpy.QtCore import Qt
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import (
    QApplication,
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
import time

if TYPE_CHECKING:
    import napari


class MMV_RegionSeg(QWidget):
    # (06.03.2025)

    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.name = None
        self.image = None
        self.tolerance = 10
        self.color = 0
        self.first_call = True

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
        self.lbl_tolerance = QLabel('Tolerance: 10')
        vbox.addWidget(self.lbl_tolerance)

        # Slider for the tolerance
        sld_tolerance = QSlider(Qt.Horizontal)
        sld_tolerance.setRange(1, 50)
        sld_tolerance.setValue(10)
        sld_tolerance.valueChanged.connect(self.tolerance_changed)
        vbox.addWidget(sld_tolerance)

        # Button 'Select seed points'
        btn_seed_points = QPushButton('Select seed points')
        btn_seed_points.clicked.connect(self.new_seed_points)
        vbox.addWidget(btn_seed_points)

        # Button 'Start floot'
        btn_floot = QPushButton('Floot')
        btn_floot.clicked.connect(self.start_floot)
        vbox.addWidget(btn_floot)

        # Button 'Growth'
        btn_growth = QPushButton('Growth')
        btn_growth.clicked.connect(self.growth_tool_3d)
        vbox.addWidget(btn_growth)

    def read_image(self):
        # Find and load the image file
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
                self.image = imread(path)
            except BaseException as error:
                print('Error:', error)
                return

        self.viewer.add_image(self.image, name=self.name)   # Show the image

    def tolerance_changed(self, value: int):
        # (06.03.2025)
        self.tolerance = value
        self.lbl_tolerance.setText('Tolerance: %d' % (value))

    def new_seed_points(self):
        # (02.04.2025)
        # Define a points layer
        self.points_layer = self.viewer.add_points(data=np.empty((0, 3)),
            size=10, border_color='blue', face_color='red', name='seed points')
        self.points_layer.mode = 'add'

    def start_floot(self):
        # (07.03.2025)
        # Form a list of tuples from the ndarray points_layer.data and convert
        # the data into int values
        points = self.points_layer.data
        seed_points = [tuple(map(round, row)) for row in points]

        # Determine a mask that corresponds to flood()
        self.color += 1
        mask = np.zeros(self.image.shape, dtype=int)
        for point in seed_points:
            flood_mask = flood(self.image, point, tolerance=self.tolerance)
            flood_mask = flood_mask.astype(int) * self.color
            mask += flood_mask

        # Store the flood mask in a label layer
        self.viewer.add_labels(mask, name='flood_mask')

        # Delete the points layer for the next run.
        if self.points_layer in self.viewer.layers:
            self.viewer.layers.remove(self.points_layer)

    def growth_tool_3d(self):
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
            flood_mask = flood(self.image, point, tolerance=self.tolerance)
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

    def new_sphere(self, seed_point, radius, shape):
        # (25.03.2025) Expands the mask each time
        # Draw a spherical region with the current radius
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
