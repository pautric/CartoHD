# CartoHD

[CartoHD](https://github.com/jgaffuri/CartoHD/) is a tool for producing large scale and high definition maps from [LIDAR](https://en.wikipedia.org/wiki/Lidar) data.

![map with LIDAR data](/img/arcon/anim.gif)


## Main process steps

- Production of 20cm resolution [Digital Surface Model (DSM) and Digital Terrain Model (DTM)](https://en.wikipedia.org/wiki/Digital_elevation_model) from [LIDAR](https://en.wikipedia.org/wiki/Lidar) points. Rough gap filling for no data pixels.
- DSM: Computation of hillshading, slope and shadow depth.
- DTM: Computation of slope (to detect and show vertical terrain features). Production of contour lines, 1m interval. Classification of the contour lines.
- Production of 20cm resolution images of buildings and vegetation areas using LIDAR classification. Application of various morphological operators to extract main patches and eliminate noise.
- Vectorisation of the buildings image. Simplification of the building features with douglass-peucker filter.
- Cartographic design with software (such as [QGIS](https://www.qgis.org/)). Overlay of auxilary vector topographic data from national topographic databases: Cadastral and agriculture parcels, water bodies, transport networks, geographical names, etc.
- Suitable scales: 1:500 to 1:5000.

## Usage

[CartoHD](https://github.com/jgaffuri/CartoHD/) is a python process. Input data are LIDAR files in LAZ or LAS format. It requires [PDAL](https://pdal.io/) and [GDAL](https://gdal.org/) to be installed as command line programs.

- Check PDAL and GDAL are installed as command. Run `pdal` and `ogr2ogr` commands (for example) in a command prompt.
- Edit the PDAL pipeline `*.json` files to specify where the input LAZ or LAS file(s) is/are located, under `"filename"` field.
- Edit the `process.py` file to specify where the output data should be saved, under `output_folder` variable. Default is `output_folder = "tmp/"`.
- Run `process.py` python script.
- Use the ouptut files with your favorite GIS/mapping software to apply the style you prefer, and overlay some auxilary topographic data. Some examples of QGIS projects are provided for France and Luxembourg.

TODO: describe shadow depth computation with qgis

## Gallery

These example were produced using [ACT-LIDAR data](https://act.public.lu/fr/cartographie/lidar1.html) for Luxembourg and [IGN-LIDAR-HD](https://geoservices.ign.fr/lidarhd) data for France.

![map with LIDAR data](/img/misc/kirchberg_.png)

![map with LIDAR data](/img/misc/ch_mars.png)

![map with LIDAR data](/img/misc/notre_dame.jpg)

![map with LIDAR data](/img/misc/ensg.png)

![map with LIDAR data](/img/misc/olive.jpg)

![map with LIDAR data](/img/misc/kirchberg1.jpg)

![map with LIDAR data](/img/misc/kirchberg2.jpg)

![map with LIDAR data](/img/misc/contas.png)

![map with LIDAR data](/img/misc/marseille.jpg)

![map with LIDAR data](/img/misc/marseille1.jpg)

![map with LIDAR data](/img/misc/marseille2.jpg)

![map with LIDAR data](/img/misc/athenee.png)

![map with LIDAR data](/img/misc/carcassonne.jpg)

![map with LIDAR data](/img/arcon/1000.png)

![map with LIDAR data](/img/arcon/2000.png)

![map with LIDAR data](/img/arcon/4000.png)

![map with LIDAR data](/img/misc/shading_test.gif)

![map with LIDAR data](/img/misc/arcon_black_white.jpg)
