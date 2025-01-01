# CartoHD

[CartoHD](https://github.com/jgaffuri/CartoHD/) is a tool for producing large scale and high definition maps from [LiDAR](https://en.wikipedia.org/wiki/Lidar) data.

![map with LiDAR data](/img/arcon/anim.gif)


## Main process steps

- Production of 20cm resolution [Digital Surface Model (DSM) and Digital Terrain Model (DTM)](https://en.wikipedia.org/wiki/Digital_elevation_model) from [LiDAR](https://en.wikipedia.org/wiki/Lidar) points. Rough gap filling for no data pixels.
- DSM: Computation of hillshading, slope and shadow depth.
- DTM: Computation of slope (to detect and show vertical terrain features). Production of contour lines, 1m interval. Classification of the contour lines.
- Production of 20cm resolution images of buildings and vegetation areas using LiDAR classification. Application of various morphological operators to extract main patches and eliminate noise.
- Vectorisation of the buildings image. Simplification of the building features with douglass-peucker filter.
- Cartographic design with software (such as [QGIS](https://www.qgis.org/)). Overlay of auxilary vector topographic data from national topographic databases: Cadastral and agriculture parcels, water bodies, transport networks, geographical names, etc.
- Suitable scales: 1:500 to 1:5000.

## Usage

[CartoHD](https://github.com/jgaffuri/CartoHD/) is a python process. Input data are LiDAR files in LAZ or LAS format. It requires [PDAL](https://pdal.io/) and [GDAL](https://gdal.org/) to be installed as command line programs.

- Check PDAL and GDAL are installed as command. Run `pdal` and `ogr2ogr` commands (for example) in a command prompt.
- Edit the `process.py` file to specify where the input data are stored and where the output data should be saved, respectivelly under `input_lidar_data` and under `output_folder` variables. It is also possible to specify the area of interest bounding box under `bounds` variable. Leave it to `None` of `False` to process the entire dataset.
- Run `process.py` python script.
- Use the ouptut files with your favorite GIS/mapping software to apply the style you prefer, and overlay some auxilary topographic data. Some examples of QGIS projects are provided for France and Luxembourg.

TODO: describe shadow depth computation with qgis

## Gallery

See some examples on [**this interactive map**](https://jgaffuri.github.io/CartoHD_webmap/viewer/dist/).

Full resolution maps can be downloaded [here](https://e.pcloud.link/publink/show?code=kZyIaxZiUumqBqt8UFGCMxrJEraY4L9Qnv7).

These example were produced using [ACT-LiDAR data](https://act.public.lu/fr/cartographie/lidar1.html) for Luxembourg and [IGN-LiDAR-HD](https://geoservices.ign.fr/lidarhd) data for France.

![map with LiDAR data](/img/misc/kirchberg_.png)

![map with LiDAR data](/img/misc/ch_mars.png)

![map with LiDAR data](/img/misc/notre_dame.jpg)

![map with LiDAR data](/img/misc/ensg.png)

![map with LiDAR data](/img/misc/olive.jpg)

![map with LiDAR data](/img/misc/kirchberg1.jpg)

![map with LiDAR data](/img/misc/kirchberg2.jpg)

![map with LiDAR data](/img/misc/contas.png)

![map with LiDAR data](/img/misc/marseille.jpg)

![map with LiDAR data](/img/misc/marseille1.jpg)

![map with LiDAR data](/img/misc/marseille2.jpg)

![map with LiDAR data](/img/misc/athenee.png)

![map with LiDAR data](/img/misc/carcassonne.jpg)

![map with LiDAR data](/img/arcon/1000.png)

![map with LiDAR data](/img/arcon/2000.png)

![map with LiDAR data](/img/arcon/4000.png)

![map with LiDAR data](/img/misc/shading_test.gif)

![map with LiDAR data](/img/misc/arcon_black_white.jpg)

