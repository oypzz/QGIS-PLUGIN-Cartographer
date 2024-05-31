# @Time  : 2024/5/22 18:39
# @Filename : test_exaggerate.py
import  math
import os
from osgeo import gdal,ogr

"""This file is used to test the exaggerate algorithm"""



# inputFile = 'D:\\专业课资料\\毕业设计\\测试数据\\K47E011007.shp'
# # # inputFile = 'D:\\专业课资料\\毕业设计\\河流\\road_JL.shp'
# outputFile = 'D:\\专业课资料\\毕业设计\\测试数据\\功能测试\\test_exaggerate.shp'
# # FID = 345
# FIDS = [68,345]
exaggerate_scale = 1.5


def create_equal_dist_points(points, L, gravity_point):
    """
    @brief      创建等间距的边界内点
    @param      points         The points
    @param      L         间距
    @param      gravity_point  重心
    @return     创建等间距点
    """
    # 判断输入条件
    if len(points) <= 2 or not gravity_point:
        return list()

    length = len(points)
    # 获取边的单位向量
    normal_vector = list()
    for i in range(length):
        vector_x = points[(i + 1) % length][0] - points[i][0]
        vector_y = points[(i + 1) % length][1] - points[i][1]
        normal_vector_x = vector_x / math.sqrt(vector_x ** 2 + vector_y ** 2)
        normal_vector_y = vector_y / math.sqrt(vector_x ** 2 + vector_y ** 2)
        normal_vector.append([normal_vector_x, normal_vector_y])

    # 获取夹角
    theta = list()
    for i in range(length):
        x1 = normal_vector[i][0]
        y1 = normal_vector[i][1]
        x2 = normal_vector[(i - 1) % len(points)][0]
        y2 = normal_vector[(i - 1) % len(points)][1]
        sin_theta = abs(x1 * y2 - x2 * y1)
        theta.append(sin_theta)

    # 计算向内扩展的点坐标
    new_points = list()
    for i in range(length):
        point = points[i]
        x1 = -normal_vector[(i - 1) % len(points)][0]
        y1 = -normal_vector[(i - 1) % len(points)][1]
        x2 = normal_vector[i][0]
        y2 = normal_vector[i][1]
        add_x = L / theta[i] * (x1 + x2)
        add_y = L / theta[i] * (y1 + y2)
        new_point_x = point[0] + add_x
        new_point_y = point[1] + add_y
        new_point = [new_point_x, new_point_y]
        # 判断点是否在里面，如果不在减去2倍的矢量增量
        if get_distance(new_point, gravity_point) > get_distance(point, gravity_point):
            new_point[0] -= 2 * add_x
            new_point[1] -= 2 * add_y

        new_points.append(new_point)
    return new_point


def get_distance(point1, point2):
    """
    @brief      计算两点之间的距离
    @param      point1  The point 1
    @param      point2  The point 2
    @return     The distance.
    """
    diff = [(point1[x] - point2[x]) for x in range(2)]
    dist = math.sqrt(diff[0] ** 2 + diff[1] ** 2)
    return dist



def get_gravity_point(points):
    """
    @brief      获取多边形的重心点
    @param      points  The points
    @return     The center of gravity point.
    """
    if len(points) <= 2:
        return list()

    area = 0.0
    x, y = 0.0, 0.0
    for i in range(len(points)):
        lng = points[i][0]
        lat = points[i][1]
        nextlng = points[i - 1][0]
        nextlat = points[i - 1][1]

        tmp_area = (nextlng * lat - nextlat * lng) / 2.0
        area += tmp_area
        x += tmp_area * (lng + nextlng) / 3.0
        y += tmp_area * (lat + nextlat) / 3.0
    x = x / area
    y = y / area
    return [float(x), float(y)]



def exaggerate(inputFile,outputFile,exaggerate_scale,FIDS):

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
                    points = geom.GetPoints()
                    gravity_point = get_gravity_point(points)
                    gra_x = gravity_point[0]
                    gra_y = gravity_point[1]
                    centroid_point = geom.Centroid()
                    cen_x = centroid_point.GetX()
                    cen_y = centroid_point.GetY()
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    for i in range(geom.GetPointCount()):
                        current_point_x = geom.GetPoint(i)[0]  # 分别获取当前遍历点的xy
                        current_point_y = geom.GetPoint(i)[1]
                        # new_x = exaggerate_scale * (current_point_x - cen_x)
                        # new_y = exaggerate_scale * (current_point_y - cen_y)
                        new_x = exaggerate_scale * (current_point_x - gra_x)  + gra_x
                        new_y = exaggerate_scale * (current_point_y - gra_y)  + gra_y
                        ring.AddPoint(new_x,new_y)
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
                        points = geom.GetPoints()
                        gravity_point = get_gravity_point(points)
                        gra_x = gravity_point[0]
                        gra_y = gravity_point[1]
                        ring = ogr.Geometry(ogr.wkbLinearRing)
                        for i in range(geom.GetPointCount()):
                            current_point_x = geom.GetPoint(i)[0]  # 分别获取当前遍历点的xy
                            current_point_y = geom.GetPoint(i)[1]
                            # new_x = exaggerate_scale * (current_point_x - cen_x)
                            # new_y = exaggerate_scale * (current_point_y - cen_y)
                            new_x = exaggerate_scale * (current_point_x - gra_x) + gra_x
                            new_y = exaggerate_scale * (current_point_y - gra_y) + gra_y
                            ring.AddPoint(new_x, new_y)
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

# exaggerate(inputFile,outputFile,exaggerate_scale,FIDS)

