# @Time  : 2024/4/25 18:56
# @Filename : TryDic.py

# from plugins import processing
from qgis import processing
# name = '河北省师范学院'
# print(name)
# print(name.encode('GBK'))
# print(type(str(name.encode('GBK'))))
# print(type(name))
#
# processing.run("native:dissolve", {'INPUT':'D:/专业课资料/毕业设计/测试数据/K47E011007.shp','FIELD':[],'SEPARATE_DISJOINT':False,'OUTPUT':'TEMPORARY_OUTPUT'})

# from shapely.geometry import shape, mapping
# from shapely.ops import unary_union
# import fiona
# import itertools
# with fiona.open('cb_2013_us_county_20m.shp') as input:
#     # preserve the schema of the original shapefile, including the crs
#     meta = input.meta
#     with fiona.open('dissolve.shp', 'w', **meta) as output:
#         # groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
#         e = sorted(input, key=lambda k: k['properties']['STATEFP'])
#         # group by the 'STATEFP' field
#         for key, group in itertools.groupby(e, key=lambda x:x['properties']['STATEFP']):
#             properties, geom = zip(*[(feature['properties'],shape(feature['geometry'])) for feature in group])
#             # write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
#             output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})

# processing.algorithmHelp("native:buffer")

file_dir = 'D:\\专业课资料\\毕业设计\\测试数据\\K47E011007'
def getname(file_dir):
    file_name = file_dir.split('\\')[-1]
    if len(file_name.split('.')) == 2 and file_name.split('.')[-1] == 'shp' :
        return file_dir
    else :
        return file_dir + '.shp'

if __name__ == "__main__":
    name =  getname(file_dir)
    print(name )