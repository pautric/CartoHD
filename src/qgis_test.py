
#which qgis
'''
export QGIS_PREFIX_PATH=/usr/bin/qgis
export PYTHONPATH=$QGIS_PREFIX_PATH/python
export PATH=$QGIS_PREFIX_PATH/bin:$PATH
'''


from qgis.core import (
    QgsApplication,
    QgsProcessingFeedback,
    QgsVectorLayer,
    QgsProject
)

# Initialize QGIS application (only needed for standalone scripts)
qgs = QgsApplication([], False)
qgs.initQgis()

