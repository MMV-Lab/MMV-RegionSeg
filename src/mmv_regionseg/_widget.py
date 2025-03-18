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
        self.stem = ''
        self.image = None
        self.mask = None
        self.tolerance = 10
        self.class1 = 1
        self.seed_points = []

        # Define a vbox for the main widget
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.lbl_headline = QLabel('MMV Region Segmentation')
        vbox.addWidget(self.lbl_headline)

        # Button read image
        btn_read = QPushButton('Read image')
        btn_read.clicked.connect(self.read_image)
        vbox.addWidget(btn_read)

        # Slider for the tolerance
        self.lbl_tolerance = QLabel('Tolerance: 10')
        vbox.addWidget(self.lbl_tolerance)
        sld_tolerance = QSlider(Qt.Horizontal)
        sld_tolerance.setRange(1, 50)
        sld_tolerance.setValue(10)
        sld_tolerance.valueChanged.connect(self.tolerance_changed)
        vbox.addWidget(sld_tolerance)

        """
        # Slider for the class
        self.lbl_class = QLabel('Class: 1')
        vbox.addWidget(self.lbl_class)
        sld_class = QSlider(Qt.Horizontal)
        sld_class.setRange(1, 50)
        sld_class.valueChanged.connect(self.class_changed)
        vbox.addWidget(sld_class)
        """

        # Button select seed point
        btn_seed_point = QPushButton('Select seed points')
        btn_seed_point.clicked.connect(self.new_seed_point)
        vbox.addWidget(btn_seed_point)

        # Button start floot_fill
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
            self.stem = path.stem               # Name of the file
            suffix = path.suffix.lower()        # File extension

        # Load the image file
        print('Load', path)
        try:
            if suffix == '.tif' or suffix == '.tiff':
                self.image = imread(path)
            else:
                print('Unknown file type: %s%s!' % (self.stem1, suffix))
                return
        except BaseException as error:
            print('Error:', error)
            return

        self.viewer.add_image(self.image, name=self.stem)   # Show the image

    def tolerance_changed(self, value: int):
        # (06.03.2025)
        self.tolerance = value
        self.lbl_tolerance.setText('Tolerance: %d' % (value))

    """
    def class_changed(self, value: int):
        # (07.03.2025)
        self.class1 = value
        self.lbl_class.setText('Class: %d' % (value))
    """

    def new_seed_point(self):
        if self.stem != '':
            layer = self.viewer.layers[self.stem]
            layer.mouse_drag_callbacks.append(self.on_click)
        else:
            print('Can\'t find an image!')

    def on_click(self, layer, event):
        # (07.03.2025)
        # Retrieve mouse-click coordinates
        point = event.position

        # Convert the float tuple into an integer tuple
        point = tuple(map(int, point))
        value = self.image[point]
        self.seed_points.append(point)

        print('Clicked at:', point, 'value:', value)

    def start_floot(self):
        # (07.03.2025)
        self.mask = np.zeros(self.image.shape, dtype=int)
        for point in self.seed_points:
            mask1 = flood(self.image, point, tolerance=self.tolerance)
            self.mask += mask1

        name1 = 'mask'
        self.viewer.add_labels(self.mask, name=name1)
