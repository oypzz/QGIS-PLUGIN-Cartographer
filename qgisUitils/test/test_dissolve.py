# @Time  : 2024/5/21 17:01
# @Filename : test_dissolve.py

import geopandas as gpd
from osgeo import gdal,ogr
import os
from shapely import to_wkt
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.colors import ListedColormap


inFile = 'D:\\专业课资料\\毕业设计\\测试数据\\K47E011007.shp'
# inFile = 'D:\\专业课资料\\毕业设计\\河流\\road_JL.shp'
outFile = 'D:\\test_dissolve2.shp'

test_data = gpd.read_file(inFile,encoding='gbk')  # 防止出现中文乱码
# print(test_data.columns)

data = test_data[['面积','周长','GEOBODY_NA']]

data_dissolve = test_data.dissolve(by='GEOBODY_NA').explode(index_parts=True) # 将合并的数据进行拆分

# create the plot
# fig, ax = plt.subplots(figsize = (10,6))

# plot the data
# data_dissolve.reset_index().plot(column = 'GEOBODY_NA', ax=ax)
data_dissolve.to_file(driver='ESRI Shapefile', filename=outFile,encoding='gbk')
# Set plot axis to equal ratio
# ax.set_axis_off()
# plt.axis('equal')

