# Copyright © Peter Lampen, ISAS Dortmund, 2025
# (06.03.2025)

from typing import TYPE_CHECKING

import napari
import numpy as np
from pathlib import Path
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QFileDialog,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget
)
from skimage.segmentation import flood, flood_fill
from tifffile import imread, imwrite

if TYPE_CHECKING:
    import napari


class mmv_regionseg(QWidget):
    # (06.03.2025)

    # your QWidget.__init__ can optionally request the napari viewer instance
    # use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.name = None
        self.image = None
        self.mask = None
        self.tolerance = 10
        self.color = 0
        self.seed_points = []

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

        # Note
        lbl_note = QLabel('To select, use the right mouse button')
        vbox.addWidget(lbl_note)

        # Button 'Start floot'
        btn_floot = QPushButton('Floot')
        btn_floot.clicked.connect(self.start_floot)
        vbox.addWidget(btn_floot)

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
        # (07.03.2025)
        # Defines the callback function on_click
        if self.name != None:
            layer = self.viewer.layers[self.name]
            layer.mouse_drag_callbacks.append(self.on_click)

            # select the image layer as active
            self.viewer.layers.selection.active = layer
        else:
            print('Can\'t find an image!')

    def on_click(self, layer, event):
        # (07.03.2025)
        # Retrieve mouse-click coordinates
        if event.type == 'mouse_press' and event.button == 2:
            point = event.position
        else:
            return

        # Convert the float tuple into an integer tuple
        iterator = map(int, point)
        point = tuple(iterator)
        self.seed_points.append(point)

        color = self.image[point]
        print('Clicked at:', point, 'color:', color)

    def start_floot(self):
        # (07.03.2025)
        # Delete the callback function on_click
        if self.name != None:
            layer = self.viewer.layers[self.name]
            layer.mouse_drag_callbacks.remove(self.on_click)

        # Determine a mask that corresponds to a flood_fill
        self.color += 1
        self.mask = np.zeros(self.image.shape, dtype=int)
        for point in self.seed_points:
            mask1 = flood(self.image, point, tolerance=self.tolerance)
            mask2 = mask1.astype(int) * self.color
            self.mask += mask2

        # Delete the seed points
        self.seed_points = []

        name1 = 'mask'
        self.viewer.add_labels(self.mask, name=name1)
