# @Time  : 2024/5/27 16:36
# @Filename : test_chaikin.py

import  math
import os
from osgeo import gdal,ogr
import numpy as np

def Smooth(inputFile,outputFile,num,FIDS):

    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  #支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "gbk")  # 属性支持中文
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(inputFile, 0)
    inLayer = inDataSet.GetLayer()

    if os.path.exists(outputFile):
        driver.DeleteDataSource(outputFile)  # 若路径中已经存在，删除
    outDataSet = driver.CreateDataSource(outputFile)
    outLayer = outDataSet.CreateLayer(inLayer.GetName(), geom_type=inLayer.GetGeomType(), options=["ENCODING=GBK"])

    inLayerDefn = inLayer.GetLayerDefn()  # 获取图层的详细信息
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    outLayerDefn = outLayer.GetLayerDefn()

    for feat  in inLayer:  # 遍历图层中全部要素
       # for FID in FIDS:     # 遍历选中的全部要素
           if feat.ID in FIDS:
            poly = feat.GetGeometryRef()
            if poly.GetGeometryName() == 'POLYGON':  # 如果选中的要素是多边形
                out_gem = ogr.Geometry(ogr.wkbPolygon)
                ring_count = poly.GetGeometryCount()
                print(ring_count)
                if ring_count == 1 : # 即无洞多边形
                    geom = poly.GetGeometryRef(0)  # 获取多边形外部环
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    x_list = []
                    y_list = []
                    for i in range(geom.GetPointCount()):
                        current_point_x = geom.GetPoint(i)[0]  # 分别获取当前遍历点的xy
                        current_point_y = geom.GetPoint(i)[1]
                        x_list.append(current_point_x)
                        y_list.append(current_point_y)
                    x_points = Chaikin(x_list, num)
                    y_points = Chaikin(y_list, num)
                    for l in range(len(x_points)):
                        ring.AddPoint(x_points[l], y_points[l])
                    ring.AddPoint(x_list[0], y_list[0])  # 使得首尾闭合
                    end_x = x_points[-1]
                    end_y = y_points[-1]
                    sta_x = x_points[0]
                    sta_y = y_points[0]
                    tem_x_list = []
                    tem_y_list = []

                    ring.AddPoint(x_points[0], y_points[0])  # 使得首尾闭合
                    out_gem.AddGeometry(ring)
                    outFeature = ogr.Feature(outLayerDefn)
                    outFeature.SetGeometry(out_gem)  # 设置该feature的几何
                    for i in range(0, outLayerDefn.GetFieldCount()):
                        FieldName = outLayerDefn.GetFieldDefn(i).GetNameRef().encode('utf-8', 'ignore').decode('utf-8')
                        FieldCtn = feat.GetFieldAsString(i).encode('utf-8', 'ignore').decode('utf-8')
                        outFeature.SetField(FieldName, FieldCtn)
                    outLayer.CreateFeature(outFeature)
                    outFeature.Destroy()

                elif ring_count > 1 : # 说明是岛洞多边形
                    for j in range(poly.GetGeometryCount()):
                        geom = poly.GetGeometryRef(j)  # 遍历获取polygon中的各个环
                        ring = ogr.Geometry(ogr.wkbLinearRing)
                        x_list = []
                        y_list = []
                        for i in range(geom.GetPointCount()):
                                current_point_x = geom.GetPoint(i)[0]  # 分别获取当前遍历点的xy
                                current_point_y = geom.GetPoint(i)[1]
                                x_list.append(current_point_x)
                                y_list.append(current_point_y)
                        x_points = Chaikin(x_list,num)
                        y_points = Chaikin(y_list,num)
                        for l in range(len(x_points)):
                            ring.AddPoint(x_points[l], y_points[l])
                        ring.AddPoint(x_points[0],y_points[0])  #使得首尾闭合
                        out_gem.AddGeometry(ring)
                    outFeature = ogr.Feature(outLayerDefn)
                    outFeature.SetGeometry(out_gem)  # 设置该feature的几何
                    for i in range(0, outLayerDefn.GetFieldCount()):
                        FieldName = outLayerDefn.GetFieldDefn(i).GetNameRef().encode('utf-8', 'ignore').decode('utf-8')
                        FieldCtn = feat.GetFieldAsString(i).encode('utf-8', 'ignore').decode('utf-8')
                        outFeature.SetField(FieldName, FieldCtn)
                    outLayer.CreateFeature(outFeature)
                    outFeature.Destroy()


           else:  # 说明不是当前选中的要素
                  out_gem = feat.GetGeometryRef()
                  outFeature = ogr.Feature(outLayerDefn)
                  outFeature.SetGeometry(out_gem)   # 非选中保留原始几何
                  for i in range(0, outLayerDefn.GetFieldCount()):
                      FieldName = outLayerDefn.GetFieldDefn(i).GetNameRef().encode('gbk', 'ignore').decode('gbk')
                      FieldCtn = feat.GetFieldAsString(i).encode('gbk', 'ignore').decode('gbk')
                      outFeature.SetField(FieldName, FieldCtn)
                  outLayer.CreateFeature(outFeature)
                  outFeature.Destroy()

    spatialRef = inLayer.GetSpatialRef()
    if spatialRef is not None:
        spatialRef.MorphToESRI()
        file = open(os.path.splitext(outputFile)[0] + '.prj', 'w', encoding='UTF-8')
        file.write(spatialRef.ExportToWkt())
        file.close()

    # destroy datasets which will also close files
    inDataSet.Destroy()
    outDataSet.Destroy()
    print('Exaggeration finished!')





def Chaikin(points, num = 3):
    while num:
        points = interpolate(points)
        num -= 1
    return points


def interpolate(points):
    ##插值
    interpoints = []
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        interpoints.append(0.75 * p1 + 0.25 * p2)  #计算q的位置
        interpoints.append(0.25 * p1 + 0.75 * p2)  #计算r的位置
    return np.array(interpoints)

# if __name__  == "__main__":
#     inFile = 'D:\\专业课资料\\毕业设计\\测试数据\\K47E011007.shp'
#     outFile = 'D:\\专业课资料\\毕业设计\\测试数据\\功能测试\\test_chaikin3.shp'
#     # FIDS = [65]
#     FIDS = list(range(366))
#     Smooth(inFile,outFile,5,FIDS)