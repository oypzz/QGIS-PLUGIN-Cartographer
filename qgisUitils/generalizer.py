# @Time  : 2024/5/20 11:29
# @Filename : generalizer.py
# import pydevd_pycharm
from osgeo import ogr,gdal
import shapely
import sys,math,random,os
import numpy as np


"""
This py file contains the main generalization processing algorithm,
smooth,dissolve and simplify are contained
"""


# sys.setdefaultencoding('utf-8')
def zig_zag(a,b,c,d): #判断线段是否为曲折的，若是则返回True
    return (a[1]*(c[0]-b[0])+b[1]*(a[0]-c[0])+c[1]*(b[0]-a[0]))*(b[1]*(d[0]-c[0])+c[1]*(b[0]-d[0])+d[1]*(c[0]-b[0])) < -ZERO_EPSILON

def polygon_area(a,b,c,d): # 根据四点求多边形面积
    return (b[0]-a[0])*(b[1]+a[1])+(c[0]-b[0])*(c[1]+b[1])+(d[0]-c[0])*(d[1]+c[1])

def squared_length(p1,p2): #勾股定理返回斜边的长度
    return (p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1])

def segments_angle(p1, p2, p3):
    a1 = math.atan2(p1[1]-p2[1], p1[0]-p2[0])
    a2 = math.atan2(p3[1]-p2[1], p3[0]-p2[0]) #返回三个点之间的夹角
    if (a1 < 0.):
        a1 += 2.*math.pi
    if (a2 < 0.):
        a2 += 2.*math.pi #负角度的话就加上2Π
    if (a1 > a2):
        da = a1 - a2
    else:
        da = a2 - a1 # subtract smaller angle from larger angle
    if (da > math.pi):
        da = math.pi*2. - da; # correct the angle to interval 0-PI
    return da  #最后返回的是两个夹角差

def Smooth(p1,p2,p3):
    ps = np.zeros(2) #temp point for calculation
    pq = np.zeros(2) #temp point for calculation
    aa = squared_length(p1,p3) #square of length of base p1p3
    a = math.sqrt(aa)  #length of base p1p3
    P = 0.5*abs(p1[1]*(p3[0]-p2[0])+p2[1]*(p1[0]-p3[0])+p3[1]*(p2[0]-p1[0])) #知三点坐标求三角形面积，可由行列式推导
    PP = P*P #square of area of triangle p1p2p3
    A = math.pow(432.*PP*(math.sqrt(aa*aa+16.*PP)-aa),0.33333333333333333333) #Ferrari's method(费拉里法) for solution of 4th degree polynom
    B = 0.5*A-72.*PP/A
    z = math.sqrt(aa+B)
    z = -3.*a+z+math.sqrt(2.*aa-B+2.*aa*a/z)
    b = (z+a)/3. #length of the three new segments, they are equal and form isosceles trapesoid等腰梯形

    #calculate the coordinates of the new points ps and pq
    if ((p3[1]-p1[1])==0.): #special case when the base is parallel with x
        q = 0.; p = 2.*P/(a+b)  #上底+下底×高除2逆运算
    else:
        alpha = -(p3[0]-p1[0])/(p3[1]-p1[1]) #底边的斜率
        q = 2.*P/(math.sqrt(1.+alpha*alpha)*(a+b)) #pq视作因为倾斜导致的坐标偏移量
        p = alpha*q
    ps[1] = (p3[1]-p1[1])*0.5*(1.-b/a)+p1[1]+p
    ps[0] = (p3[0]-p1[0])*0.5*(1.-b/a)+p1[0]+q # coordinates of new points
    pq[1] = (p3[1]-p1[1])*0.5*(1.+b/a)+p1[1]+p
    pq[0] = (p3[0]-p1[0])*0.5*(1.+b/a)+p1[0]+q

    #解出来的两个方向，选择与原始方向一致的解，若为反向则减去两倍，关于坐标轴对称
    if ((p1[1]*(p3[0]-p2[0])+p2[1]*(p1[0]-p3[0])+p3[1]*(p2[0]-p1[0]))*(p1[1]*(p3[0]-ps[0])+ps[1]*(p1[0]-p3[0])+p3[1]*(ps[0]-p1[0]))<0.):
        ps[1] -= 2.*p
        ps[0] -= 2.*q
        pq[1] -= 2.*p
        pq[0] -= 2.*q
    return ps,pq

def Smooth_Ring(g, geom_type):
    input_area = g.Area()
    if input_area < DEL_AREA:
        return 0, g

    p_len = g.GetPointCount()  # 获取点的数量
    points = np.zeros((p_len, 2))
    j = 0
    p = g.GetPoint(j)
    points[j, 0] = p[0]  # 分别读取x跟y坐标
    points[j, 1] = p[1]
    for i in range(1, p_len):
        p = g.GetPoint(i)
        # remove duplicate neighbour points
        if points[j, 0] != p[0] or points[j, 1] != p[1]:
            j = j + 1
            points[j, 0] = p[0]
            points[j, 1] = p[1]
    p_len = j + 1  # final number of points in point list

    # 线性的闭合图形，至少需要四个点
    if p_len < 4:
        return 0, g

    # calculate squared segments lengths, algorithm always change line where shorthest segment is found
    segments = np.zeros(p_len - 1)
    for i in range(0, p_len - 1):
        segments[i] = squared_length(points[i], points[i + 1])  # 从列表中读取所有点的坐标并计算斜边长然后存储

    angles = np.zeros(p_len - 1)
    # angles[0] is angle on starting=ending point
    angles[0] = segments_angle(points[p_len - 2], points[0], points[1])  # 这里是最后一个点跟开头两个头(循环)
    for i in range(1, p_len - 1):
        # angles[1] is angle on vertex point[1]
        angles[i] = segments_angle(points[i - 1], points[i], points[i + 1])

    # always change the sharpest angle in line
    i = np.argmin(angles)  # 求最小夹角对应的索引
    min_a = np.amin(angles)  # 最小值
    while min_a < MIN_ANGLE:  # 大于这个角度的线段不需要平滑
        if i == 0:  # 说明最小值点在起始点
            # 线段圆滑长度的阈值tolerance？
            if segments[p_len - 2] < SQR_SMOOTH_LENGTH and segments[i] < SQR_SMOOTH_LENGTH:
                ps, pq = Smooth(points[p_len - 2], points[i], points[i + 1])
                # update the point list
                points[i] = ps  # change starting point
                points[p_len - 1] = ps  # change ending point
                points = np.insert(points, i + 1, pq, 0)  # ps加到了第i个，pq插入到第i+1个，即ps后面
                p_len = p_len + 1
                segments = np.insert(segments, i + 1, squared_length(points[i + 1], points[i + 2]),
                                     0)  # add last segment
                segments[p_len - 2] = squared_length(points[p_len - 2], points[i])  # update middle segment
                segments[i] = squared_length(points[i], points[i + 1])  # update first segment
                angles = np.insert(angles, i + 1,
                                   segments_angle(points[i], points[i + 1], points[i + 2]))  # add angle on point pq
                angles[i] = segments_angle(points[p_len - 2], points[i], points[i + 1])
                angles[p_len - 2] = segments_angle(points[p_len - 3], points[p_len - 2], points[i])
                angles[i + 2] = segments_angle(points[i + 1], points[i + 2], points[i + 3])
            else:
                angles[i] = 2 * MIN_ANGLE  # 角度很尖锐但是线段太长
            # if segments are smaller then threshold
        else:
            if segments[i - 1] < SQR_SMOOTH_LENGTH and segments[i] < SQR_SMOOTH_LENGTH:
                # calculation of the two new points, keeping the area
                ps, pq = Smooth(points[i - 1], points[i], points[i + 1])
                # update the point list
                points[i] = ps  # change middle point
                points = np.insert(points, i + 1, pq, 0)  # add new point before point after middle point
                segments = np.insert(segments, i + 1, squared_length(points[i + 1], points[i + 2]),
                                     0)  # add last segment
                segments[i - 1] = squared_length(points[i - 1], points[i])  # update middle segment
                segments[i] = squared_length(points[i], points[i + 1])  # update first segment
                angles = np.insert(angles, i + 1,
                                   segments_angle(points[i], points[i + 1], points[i + 2]))  # add angle on point pq
                angles[i] = segments_angle(points[i - 1], points[i], points[i + 1])
                if i == 1:
                    angles[i - 1] = segments_angle(points[p_len - 2], points[p_len - 1], points[i])
                else:
                    angles[i - 1] = segments_angle(points[i - 2], points[i - 1], points[i])
                if i == p_len - 2:
                    angles[0] = segments_angle(points[p_len - 2], points[0], points[1])
                else:
                    angles[i + 2] = segments_angle(points[i + 1], points[i + 2], points[i + 3])
                p_len = p_len + 1
            else:
                angles[i] = 2 * MIN_ANGLE
        i = np.argmin(angles)
        min_a = np.amin(angles)


    if geom_type == 0:
        ring = ogr.Geometry(ogr.wkbLinearRing)
    else:
        ring = ogr.Geometry(ogr.wkbLineString)
    for i in range(0, p_len):
        ring.AddPoint(points[i, 0], points[i, 1])
    if points[0, 0] != points[p_len - 1, 0] or points[0, 1] != points[p_len - 1, 1]:
        ring.AddPoint(points[0, 0], points[0, 1])
    return 1, ring

def Smooth_Line(g):
    p_len = g.GetPointCount()
    points = np.zeros((p_len, 2))
    j = 0
    p = g.GetPoint(j)
    points[j, 0] = p[0]
    points[j, 1] = p[1]
    for i in range(1, p_len):
        p = g.GetPoint(i)
        # remove duplicate neighbour points
        if points[j, 0] != p[0] or points[j, 1] != p[1]:
            j = j + 1
            points[j, 0] = p[0]
            points[j, 1] = p[1]
    p_len = j + 1  # final number of points in point list

    # malformed linear geometry, zero or one point
    if p_len < 2:
        return 0, g
    # geometry of one segment, nothing to smooth, return cleaned
    if p_len == 2:
        line = ogr.Geometry(ogr.wkbLineString)
        for i in range(0, p_len):
            line.AddPoint(points[i, 0], points[i, 1])
        return -1, line

    ps = np.zeros(2)  # temp point for calculation
    pq = np.zeros(2)  # temp point for calculation

    # calculate squared segments lengths, algorithm always change line where shorthest segment is found
    segments = np.zeros(p_len - 1)
    for i in range(0, p_len - 1):
        segments[i] = squared_length(points[i], points[i + 1])

    angles = np.zeros(p_len - 1)
    # angles[0] is angle on first point
    angles[0] = 2 * MIN_ANGLE
    for i in range(1, p_len - 1):
        # angles[0] is angle on vertex point[1]
        angles[i] = segments_angle(points[i - 1], points[i], points[i + 1])

    # always change the sharpest angle in line
    i = np.argmin(angles)  # index of sharpest angle
    min_a = np.amin(angles)  # sharpest angle
    while min_a < MIN_ANGLE:
        if segments[i - 1] < SQR_SMOOTH_LENGTH and segments[i] < SQR_SMOOTH_LENGTH:
            # calculation of the two new points, keeping the area
            ps, pq = Smooth(points[i - 1], points[i], points[i + 1])
            # update the point list
            points[i] = ps  # change middle point
            points = np.insert(points, i + 1, pq, 0)  # add new point before point after middle point
            segments = np.insert(segments, i + 1, squared_length(points[i + 1], points[i + 2]), 0)  # add last segment
            segments[i - 1] = squared_length(points[i - 1], points[i])  # update middle segment
            segments[i] = squared_length(points[i], points[i + 1])  # update first segment
            angles = np.insert(angles, i + 1,
                               segments_angle(points[i], points[i + 1], points[i + 2]))  # add angle on point pq
            angles[i] = segments_angle(points[i - 1], points[i], points[i + 1])
            if i > 1:
                angles[i - 1] = segments_angle(points[i - 2], points[i - 1], points[i])
            if i < p_len - 2:
                angles[i + 2] = segments_angle(points[i + 1], points[i + 2], points[i + 3])
            p_len = p_len + 1
        else:
            angles[i] = 2 * MIN_ANGLE  # angle was sharp but segments were too long, skip it in next iteration
        # if segments are smaller then threshold
        i = np.argmin(angles)  # index of sharpest angle
        min_a = np.amin(angles)  # sharpest angle
    # while angle is smaller then threshold

    line = ogr.Geometry(ogr.wkbLineString)
    for i in range(0, p_len):
        line.AddPoint(points[i, 0], points[i, 1])

    return 1, line

def Decide(g, closed, g_type, out_geom, single_line):
    gen = 0
    if closed:
        flag, smooth = Smooth_Ring(g, g_type)
    else:
        flag, smooth = Smooth_Line(g)
    if flag == 1 or flag == -1:
        if single_line:
            out_geom = smooth
        else:
            out_geom.AddGeometry(smooth)
        gen = 1

    return gen, out_geom

def Smoother(inFile, outFile,scale):  # 进行圆滑处理
    global DEL_AREA
    global TOL_LENGTH
    global SQR_TOL_LENGTH
    global ZERO_EPSILON
    global MIN_ANGLE
    global SQR_SMOOTH_LENGTH
    global ZERO_AREA

    DEL_AREA = 0.00000001  # 最小面积阈值
    TOL_LENGTH = scale / 50  # main paramater of the algorithm, determined from manually generalised maps
    SQR_TOL_LENGTH = TOL_LENGTH * TOL_LENGTH  # squared main parameter of the algorithm
    ZERO_EPSILON = 1E-12  # if less then value is considered as zero
    MIN_ANGLE = 160. * math.pi / 180.  # 圆滑的最大角度，当某一夹角大于该角度 则不需要圆滑
    SQR_SMOOTH_LENGTH = 20. * SQR_TOL_LENGTH  # 进行圆滑处理的最大长度，大于该长度的线段不需要圆滑
    ZERO_AREA = 1E-6  # if less then value is considered as zero

    # open input ESRI Shapefile
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  #支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 属性支持中文
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(inFile, 0)
    inLayer = inDataSet.GetLayer()

    # create output ESRI Shapefile
    if os.path.exists(outFile):
        driver.DeleteDataSource(outFile)  # 若路径中已经存在，删除
    outDataSet = driver.CreateDataSource(outFile)
    outLayer = outDataSet.CreateLayer(inLayer.GetName(), geom_type=inLayer.GetGeomType(),options=["ENCODING=GBK"])  #不出现乱码的关键在此处

    # copy fields to output
    inLayerDefn = inLayer.GetLayerDefn()  # 获取图层的详细信息
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # pydevd_pycharm.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
    # get the output layer's feature definition, will be used for copying field values to output
    outLayerDefn = outLayer.GetLayerDefn()
    num_of_objects = inLayer.GetFeatureCount()
    obj_index = 0
    # loop through all input features and generalize them
    for inFeature in inLayer:
        # feat = inLayer.GetFeature(0)
        gen = 0  # assume the feature should be omitted from output
        geom = inFeature.geometry()  # get reference of feature geometry
        if geom.GetGeometryName() == 'MULTIPOLYGON':
            out_geom = ogr.Geometry(ogr.wkbMultiPolygon)  # create output geometry of given type
            for i in range(0, geom.GetGeometryCount()):  # iterate over polygons in multipolygon
                poly = ogr.Geometry(ogr.wkbPolygon)  # create output polygon geometry
                g = geom.GetGeometryRef(i)  # input polygon can have multiple rings
                for j in range(0, g.GetGeometryCount()):  # iterate over rings
                    ring = g.GetGeometryRef(j)  # access to a ring (closed polyline)

                    # output: gen_ring=1 indicates that some geometry is preserved after generalisation
                    # output: poly will receive all generalised rings in it
                    # input: True means that rings are allways closed
                    # input: first 0 means that ogrLinearRing is geometry type for creation
                    # input: poly is reference to geometry in which new generalised geometry of right type will be stored
                    # input: alg_type - generalisation (simplification+smoothing), simplification or smoothing
                    # input: second 0 means that this is multigeometry (polygon with multiple rings)
                    gen_ring, poly = Decide(ring, True, 0, poly, 0)  # perform generalisation

                    # there were some geometry preserved, store this in gen so output feature will be created
                    # some parts could be deleted due to too small area for given scale
                    if gen_ring == 1:
                        gen = 1
                # add polygon to multipolygon
                out_geom.AddGeometry(poly)

        elif geom.GetGeometryName() == 'POLYGON':
            out_geom = ogr.Geometry(ogr.wkbPolygon)  # create output geometry of given type
            for i in range(0, geom.GetGeometryCount()):  # iterate over rings返回单点几何对象
                ring = geom.GetGeometryRef(i)  # access to a ring (closed polyline)

                # output: gen_ring=1 indicates that some geometry is preserved after generalisation
                # output: out_geom will receive all generalised rings in it
                # input: True means that rings are allways closed
                # input: first 0 means that ogrLinearRing is geometry type for creation
                # input: out_geom is reference to geometry in which new generalised geometry of right type will be stored
                # input: alg_type - generalisation (simplification+smoothing), simplification or smoothing
                # input: second 0 means that this is multigeometry (polygon with multiple rings)
                gen_ring, out_geom = Decide(ring, True, 0, out_geom, 0)  # perform generalisation

                # there were some geometry preserved, store this in gen so output feature will be created
                # some parts could be deleted due to too small area for given scale
                if gen_ring == 1:
                    gen = 1

        elif geom.GetGeometryName() == 'MULTILINESTRING':
            out_geom = ogr.Geometry(ogr.wkbMultiLineString)  # create output geometry of given type
            for i in range(0, geom.GetGeometryCount()):  # iterate over lines
                line = geom.GetGeometryRef(i)
                # check if it closed polyline, if so, generalize it as ring, which means
                # that neither vertex is considered as fixed
                # if line is open, starting and ending points are preserved
                ps = line.GetPoint(0)
                pe = line.GetPoint(line.GetPointCount() - 1)
                closed = False
                if (ps[0] == pe[0]) and (ps[1] == pe[1]):
                    closed = True

                # output: gen_line=1 indicates that some geometry is preserved after generalisation
                # output: out_geom will receive all generalised lines in it
                # input: closed indicates whether line is closed or not
                # input: 1 means that ogrLineString is geometry type for creation
                # input: out_geom is reference to geometry in which new generalised geometry of right type will be stored
                # input: alg_type - generalisation (simplification+smoothing), simplification or smoothing
                # input: 0 means that this is multigeometry (multilinestring with multiple linestrings)
                gen_line, out_geom = Decide(line, closed, 1, out_geom,  0)

                # there were some geometry preserved, store this in gen so output feature will be created
                # some parts could be deleted due to too small area for given scale
                if gen_line == 1:
                    gen = 1

        elif geom.GetGeometryName() == 'LINESTRING':
            out_geom = ogr.Geometry(ogr.wkbLineString)  # create output geometry of given type
            # check if it closed polyline, if so, generalize it as ring, which means
            # that neither vertex is considered as fixed
            # if line is open, starting and ending points are preserved
            ps = geom.GetPoint(0)
            pe = geom.GetPoint(geom.GetPointCount() - 1)
            closed = False
            if (ps[0] == pe[0]) and (ps[1] == pe[1]):
                closed = True

            gen, out_geom = Decide(geom, closed, 1, out_geom, 1)

            # if some geometry is preserved after generalisation create output feature with
        # generalised geometry and copy attributes from input feature
        if gen == 1:
            outFeature = ogr.Feature(outLayerDefn)
            # set the geometry
            outFeature.SetGeometry(out_geom)
            # copy the attributes
            for i in range(0, outLayerDefn.GetFieldCount()):
                FieldName = outLayerDefn.GetFieldDefn(i).GetNameRef().encode('utf-8', 'ignore').decode('utf-8')
                FieldCtn = inFeature.GetFieldAsString(i).encode('utf-8', 'ignore').decode('utf-8')
                outFeature.SetField(FieldName, FieldCtn)
            # add the feature to the shapefile
            outLayer.CreateFeature(outFeature)
            # destroy output feature
            outFeature.Destroy()
        # destroy input feature and get the next input feature
        inFeature.Destroy()

    # create .prj file for output if CRS is attached to input layer
    spatialRef = inLayer.GetSpatialRef()
    if spatialRef is not None:
        spatialRef.MorphToESRI()
        file = open(os.path.splitext(outFile)[0] + '.prj', 'w',encoding='UTF-8')
        file.write(spatialRef.ExportToWkt())
        file.close()

    # destroy datasets which will also close files
    inDataSet.Destroy()
    outDataSet.Destroy()


