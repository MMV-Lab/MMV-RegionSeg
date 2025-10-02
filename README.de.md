# mmv-regionseg

[![License BSD-3](https://img.shields.io/pypi/l/mmv-regionseg.svg?color=green)](https://github.com/MMV-Lab/mmv-regionseg/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mmv-regionseg.svg?color=green)](https://pypi.org/project/mmv-regionseg)
[![Python Version](https://img.shields.io/pypi/pyversions/mmv-regionseg.svg?color=green)](https://python.org)
[![tests](https://github.com/MMV-Lab/MMV-RegionSeg/actions/workflows/test_and_deploy.yml/badge.svg)](https://github.com/MMV-Lab/MMV-RegionSeg/actions/workflows/test_and_deploy.yml)
[![codecov](https://codecov.io/gh/MMV-Lab/mmv-regionseg/branch/main/graph/badge.svg)](https://codecov.io/gh/MMV-Lab/mmv-regionseg)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/mmv-regionseg)](https://napari-hub.org/plugins/mmv-regionseg)

Ein Napari-Plugin zur Segmentierung von Regionen mittels Flood-Fill.

---

## Installation

Du kannst `mmv-regionseg` mit [pip] installieren:

```bash
pip install mmv-regionseg
```

Für die neueste Entwicklungs-Version:

```bash
pip install git+https://github.com/MMV-Lab/mmv-regionseg.git
```

---

## Beschreibung

**MMV-RegionSeg** ist ein Napari-Plugin, mit dem dreidimensionale Bilddaten anhand des Grauwerts eines ausgewählten Startpunkts segmentiert werden können. Nachbarvoxels werden derselben Klasse zugeordnet, wenn ihr Intensitätswert ähnlich zum Startpunkt ist oder innerhalb eines definierten Toleranzbereichs liegt.

---

### Plugin starten

1. Napari öffnen  
2. Menü **Plugins** auswählen  
3. **MMV-RegionSeg** anklicken  

Ein Widget erscheint rechts im Napari-Fenster mit Buttons, Labels und einem Slider.

---

### Screenshot

![MMV-RegionSeg Plugin Screenshot](https://raw.githubusercontent.com/MMV-Lab/MMV-RegionSeg/main/docs/images/plugin_screenshot1.png)

---

### Bilddaten laden

Klicke auf **"Read image"**, um ein 3D-Bild im TIFF-Format zu laden. Das Bild wird als **Image-Layer** angezeigt.

---

### Toleranz einstellen

Mit dem **Slider** unter dem Bild-Button lässt sich die Grauwert-Toleranz (0%–100% des Dynamikbereichs) einstellen:

- **Niedrig** → Gefahr unvollständiger Segmentierung  
- **Hoch** → Gefahr, dass unerwünschte Bereiche eingeschlossen werden  

> ⚠️ Optimale Toleranz erfordert oft Ausprobieren.

---

### Footprint auswählen

Im **Dropdown-Menü** wählst du das Footprint für  
`skimage.segmentation.flood`.  
Siehe auch: [Flood Fill].

- **6 Nachbarn** → nur direkt angrenzende Voxels (X, Y, Z)  
- **18 Nachbarn** → auch diagonal angrenzende Voxels entlang Flächen und Kanten  
- **26 Nachbarn** → alle Nachbarvoxels werden berücksichtigt  

---

### Seed Points setzen

Klicke auf **"Select seed points"**, um einen neuen **Points-Layer** zu aktivieren. Dann Punkte direkt im Viewer setzen.

- Jeder Seed Point wird angezeigt  
- Mehrere Punkte in einem Schritt → eine Klasse  
- Layer Controls nutzen, um Punkte zu verschieben oder zu löschen  

---

### Segmentierungsoptionen

Nach dem Setzen der Seed Points kannst du zwischen zwei Methoden wählen:

#### Flood

Klick auf **"Flood"**, um `skimage.segmentation.flood` auszuführen.  
Die Nachbarvoxels innerhalb der Toleranz werden in einem neuen **Label-Layer** gespeichert.

#### Growth

Klick auf **"Growth"**, um die Segmentierung **Schritt für Schritt** zu sehen.  
Simuliert das Wachstum einer Region, ähnlich wie eine Zellkolonie.

---

### Neue Segmentierung starten

Nach Erstellung eines Label-Layers wird der **Points-Layer entfernt**, sodass neue Seed Points definiert werden können, ohne bestehende Segmentierungen zu beeinflussen.

---

## Mitwirken

Beiträge sind willkommen!  
Tests können mit [tox] durchgeführt werden. Achte darauf, dass die Testabdeckung nicht sinkt, bevor du einen Pull Request erstellst.

---

## Lizenz

Veröffentlicht unter [BSD-3].  
**mmv-regionseg** ist freie Open-Source-Software.

---

## Probleme melden

Probleme bitte [hier melden] und eine detaillierte Beschreibung beifügen.

[pip]: https://pypi.org/project/pip/  
[tox]: https://tox.readthedocs.io/en/latest/  
[Flood Fill]: https://scikit-image.org/docs/0.25.x/auto_examples/segmentation/plot_floodfill  
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause  
[hier melden]: https://github.com/MMV-Lab/mmv-regionseg/issues
