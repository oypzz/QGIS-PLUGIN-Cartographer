# @Time  : 2024/5/20 21:33
# @Filename : test_dp.py


import geopandas as gpd
from osgeo import gdal,ogr
import os
from shapely import to_wkt


# inFile = 'D:\\专业课资料\\毕业设计\\测试数据\\K47E011007.shp'
# inFile = 'D:\\专业课资料\\毕业设计\\河流\\road_JL.shp'
# outFile = 'D:\\test_dp_road.shp'

def Douglas(inFile,outFile,tolerance):  # tolerance移除直线距离小于该值的点
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  #支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 属性支持中文
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(inFile, 0)
    inLayer = inDataSet.GetLayer()
    if os.path.exists(outFile):
        driver.DeleteDataSource(outFile)  # 若路径中已经存在，删除
    outDataSet = driver.CreateDataSource(outFile)
    outLayer = outDataSet.CreateLayer(inLayer.GetName(), geom_type=inLayer.GetGeomType(),options=["ENCODING=GBK"])  #不出现乱码的关键在此处

    # 使用DP算法进行简化处理
    d = gpd.read_file(inFile,encoding='gbk')


    simplified = d.simplify(tolerance, preserve_topology=False)  # preserve_topology保存几何图形有效性，检查图形自相交等


     # copy fields to output
    inLayerDefn = inLayer.GetLayerDefn()  # 获取图层的详细信息
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)  # 创建字段类型和内容

    outLayerDefn = outLayer.GetLayerDefn()

    i = 0
    for inFeature in inLayer:
        geom = inFeature.geometry()
        if geom.GetGeometryName() == 'LINESTRING': # 如果要处理的线要素
            feat_count = inLayer.GetFeatureCount()
            # out_geom = ogr.Geometry(ogr.wkbMultiPolygon)
            out_geom = ogr.Geometry(ogr.wkbMultiLineString)
            poly = simplified[i]
            i = i + 1
            # poltLine = poly.replace('POLYGON','LINEARRING')
            wkt = to_wkt(poly)


            # poly2 = poly[0]
            polygon = ogr.CreateGeometryFromWkt(wkt)  # shapely数据类型与OGR类型不一致，先转换为wkt格式
            print(type(polygon))
            out_geom.AddGeometry(polygon) # 从wkt格式中读取并创建几何要素
            outFeature = ogr.Feature(outLayerDefn)  #创建要素属性
            outFeature.SetGeometry(out_geom)  # 设置要素几何


            # copy the attributes
            for j in range(0, outLayerDefn.GetFieldCount()):
                FieldName = outLayerDefn.GetFieldDefn(j).GetNameRef().encode('gbk', 'ignore').decode('gbk')
                FieldCtn = inFeature.GetFieldAsString(j).encode('gbk', 'ignore').decode('gbk')
                outFeature.SetField(FieldName, FieldCtn)

            # inFeature = inLayer.GetNextFeature()
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()
        elif geom.GetGeometryName() == 'POLYGON':  #如果要处理的是面要素数据
            feat_count = inLayer.GetFeatureCount()
            out_geom = ogr.Geometry(ogr.wkbMultiPolygon)
            # out_geom = ogr.Geometry(ogr.wkbMultiLineString)
            poly = simplified[i]
            i = i + 1
            # poltLine = poly.replace('POLYGON','LINEARRING')
            wkt = to_wkt(poly)

            # poly2 = poly[0]
            polygon = ogr.CreateGeometryFromWkt(wkt)  # shapely数据类型与OGR类型不一致，先转换为wkt格式
            print(type(polygon))
            out_geom.AddGeometry(polygon)  # 从wkt格式中读取并创建几何要素
            outFeature = ogr.Feature(outLayerDefn)  # 创建要素属性
            outFeature.SetGeometry(out_geom)  # 设置要素几何

            # copy the attributes
            for j in range(0, outLayerDefn.GetFieldCount()):
                FieldName = outLayerDefn.GetFieldDefn(j).GetNameRef().encode('gbk', 'ignore').decode('gbk')
                FieldCtn = inFeature.GetFieldAsString(j).encode('gbk', 'ignore').decode('gbk')
                outFeature.SetField(FieldName, FieldCtn)

            # inFeature = inLayer.GetNextFeature()
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()
        # inFeature.Destroy()
    # 复制原始数据的参考坐标信息
    spatialRef = inLayer.GetSpatialRef()
    if spatialRef is not None:
        spatialRef.MorphToESRI()
        file = open(os.path.splitext(outFile)[0] + '.prj', 'w',encoding='gbk')
        file.write(spatialRef.ExportToWkt())
        file.close()




# print(simplified[0])
# simplified.to_file(outFile)