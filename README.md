# CartoHD

[CartoHD](https://github.com/jgaffuri/CartoHD/) is a tool for producing large scale and high definition maps from [LIDAR](https://en.wikipedia.org/wiki/Lidar) data.

![map with LIDAR data](/img/arcon/anim.gif)


## Process

- hillshaded and sloped LIDAR DSM, as grayscale
- shadow depth simulation from DSM
- hue from classification for vegetation and buildings
- BD Topo for roads (white) and water bodies (blue), etc.
- RPC for fields

## Usage

[CartoHD](https://github.com/jgaffuri/CartoHD/) is a python process. Input data are LIDAR files in LAZ or LAS format. It requires [PDAL](https://pdal.io/) and [GDAL](https://gdal.org/) to be installed as command line programs.

- Check PDAL and GDAL are installed
- Edit the PDAL pipeline *.json files to specify where the input data is located, under `"filename"` field.
- Edit the `process.py` file to specify where the output data should be created. Default is `output_folder = "tmp/"`
- Run `process.py` python script.
- Use the ouptut files with your favorite GIS/mapping software to apply the style you prefer, and overlay some auxilary topographic data. Some examples of QGIS projects are provided for France and Luxembourg.

## Gallery

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

![map with LIDAR data](/img/misc/arcon_black_white.jpg)
