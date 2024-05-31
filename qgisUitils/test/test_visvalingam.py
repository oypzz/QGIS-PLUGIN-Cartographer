# @Time  : 2024/5/20 15:49
# @Filename : test_visvalingam.py

## This script is to created to simplify
## shapefile geometry using the
## Visvalingam algorithm found here
## http://www2.dcs.hull.ac.uk/CISRG/publications/DPs/DP10/DP10.html

## Threshold is the area of the largest allowed triangle


import fiona
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, LineString, MultiLineString
import heapq
import shapely
from shapely.geometry.polygon import LinearRing
import operator
import sys


class TriangleCalculator:
    def __init__(self, point, index):
        # Need to add better validation

        # Save instance variables
        self.point = point
        self.ringIndex = index # 该点在线/环中的序号
        self.prevTriangle = None
        self.nextTriangle = None
        self.area = None

    # 用来实现类之间的比较操作
    def __eq__(self, other):
      return operator.eq(self.calcArea(), other.calcArea())

    def __lt__(self, other):
        """小于"""
        return operator.lt(self.calcArea(), other.calcArea())

    def __le__(self, other):
        """小于等于"""
        return operator.le(self.calcArea(), other.calcArea())

    def __gt__(self, other):
        """大于"""
        return operator.gt(self.calcArea(), other.calcArea())

    def __ge__(self, other):
        """大于等于"""
        return operator.ge(self.calcArea(), other.calcArea())


    def calcArea(self):
        # Add validation
        if not self.prevTriangle or not self.nextTriangle:  # 未满足三个点的要求
            print ("ERROR:")

        p1 = self.point
        p2 = self.prevTriangle.point
        p3 = self.nextTriangle.point
        area = abs(p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])) / 2.0  # 行列式法求三角形面积
        #print "area = " + str(area) + ", point = " + str(self.point)
        return area



class GeomSimplify:


    def simplify_line(self, line, threshold):


        # Build list of Triangles from the line points
        triangleArray = []
        for index, point in enumerate(line.coords[1:-1]):  # 获取并添加线段内部的全部点(不包含起始和末尾点)
            triangleArray.append(TriangleCalculator(point, index))


        startIndex = 0
        endIndex = len(line.coords)-1
        startTriangle = TriangleCalculator(line.coords[startIndex], startIndex)
        endTriangle = TriangleCalculator(line.coords[endIndex], endIndex)

        for index, triangle in enumerate(triangleArray):
            # set prevIndex to be the adjacent point to index
            prevIndex = index - 1
            nextIndex = index + 1

            if prevIndex >= 0:
                triangle.prevTriangle = triangleArray[prevIndex]   # 设置当前三角形的前后三角形
            else:
                triangle.prevTriangle = startTriangle

            if nextIndex < len(triangleArray):
                triangle.nextTriangle = triangleArray[nextIndex]
            else:
                triangle.nextTriangle = endTriangle

        # Build a min-heap from the TriangleCalculator list
        # print "heapify"
        heapq.heapify(triangleArray)  # 建立最小根堆进行排序



        # 与环的判定不一样，只需要内部有点即可
        while len(triangleArray) > 0:
            if triangleArray[0].calcArea() >= threshold:  # 当前三角形面积大于阈值，则保留
                break
            else:
                # print statement for debugging - prints area's and coords of deleted/simplified pts
                #print "simplify...triangle area's and their corresponding points that were less then the threshold"
                #print "area = " + str(triangleArray[0].calcArea()) + ", point = " + str(triangleArray[0].point)
                prev = triangleArray[0].prevTriangle
                next = triangleArray[0].nextTriangle
                prev.nextTriangle = next
                next.prevTriangle = prev
                heapq.heappop(triangleArray)
                #print "area = " + str(triangle.calcArea()) + ", point = " + str(triangle.point)
                #print "done popping (i.e. area that is less than threshold, and will have point removed)"

        # Create an list of indices from the triangleRing heap
        indexList = []
        for triangle in triangleArray:
            # add 1 b/c the triangle array's first index is actually the second point
            indexList.append(triangle.ringIndex + 1)
        # Append start and end points back into the array
        indexList.append(startTriangle.ringIndex)
        indexList.append(endTriangle.ringIndex)

        # Sort the index list
        indexList.sort()

        # Create a new simplified ring
        simpleLine = []
        for index in indexList:
            simpleLine.append(line.coords[index])

        # Convert list into LineString
        simpleLine = LineString(simpleLine)

        return simpleLine

    def simplify_ring(self, ring, threshold):

        # Build list of TriangleCalculators
        triangleRing = []
        for index, point in enumerate(ring.coords[:-1]):
            triangleRing.append(TriangleCalculator(point, index))  # 因为环的第一个跟最后一个是重复的

        # 双向链表绑定
        for index, triangle in enumerate(triangleRing):
            prevIndex = index - 1
            if prevIndex < 0:  # 环状构造最后一个点等于起始点
                # if prevIndex is less than 0, then it means index = 0, and
                # the prevIndex is set to last value in the index
                # (i.e. adjacent to index[0])
                prevIndex = len(triangleRing) - 1
            # set nextIndex adjacent to index
            nextIndex = index + 1
            if nextIndex == len(triangleRing):
                # if nextIndex is equivalent to the length of the array
                # set nextIndex to 0
                nextIndex = 0
            triangle.prevTriangle = triangleRing[prevIndex]
            triangle.nextTriangle = triangleRing[nextIndex]
            triangle.area = triangle.calcArea()
        # heapq.heapify(triangleRing)
        triangleRing.sort(key= lambda x: x.area)  # 根据面积属性进行排序
        while len(triangleRing) > 2:
            # if the smallest triangle is greater than the threshold, we can stop
            # i.e. loop to point where the heap head is >= threshold

            area = triangleRing[0].calcArea()
            print(triangleRing[0].calcArea())
            print(triangleRing[1].calcArea())
            print(triangleRing[2].calcArea())
            if triangleRing[0].calcArea() >= threshold:
                break   # 最前端的是最小的，当最小的都大于阈值，算法结束
            else:
                prev = triangleRing[0].prevTriangle   # 双向链表，两头绑定操作
                next = triangleRing[0].nextTriangle
                prev.nextTriangle = next
                next.prevTriangle = prev

                heapq.heappop(triangleRing)   # pop自动弹出堆中最小的值(即是最前面的点)

        if len(triangleRing) < 3:
            return None

        # Create an list of indices from the triangleRing heap
        indexList = []
        for triangle in triangleRing:
            indexList.append(triangle.ringIndex)  # 获取处理后点的序号

        indexList.sort()  # 默认升序

        # Create a new simplified ring
        simpleRing = []
        for index in indexList:
            simpleRing.append(ring.coords[index]) # 根据序号获取留下来的点的坐标

        # Convert list into LinearRing
        simpleRing = LinearRing(simpleRing)

        return simpleRing


    def simplify_multipolygon(self, mpoly, threshold):
        # break multipolygon into polys
        polyList = mpoly.geoms
        simplePolyList = []

        # call simplify_polygon() on each
        for poly in polyList:
            simplePoly = self.simplify_polygon(poly, threshold)
            #if not none append to list
            if simplePoly:
                simplePolyList.append(simplePoly)

        # check that polygon count > 0, otherwise return None
        if not simplePolyList:
            return None

        # put back into multipolygon
        return MultiPolygon(simplePolyList)

    def simplify_polygon(self, poly, threshold):

        # 多边形是根据多边形外部的环进行处理
        simpleExtRing = self.simplify_ring(poly.exterior, threshold)  # exterior获取外部环

        # If the exterior ring was removed by simplification, return None
        if simpleExtRing is None:
            return None

        simpleIntRings = []
        for ring in poly.interiors:  # 获取内部环
            simpleRing = self.simplify_ring(ring, threshold)
            if simpleRing is not None:
                simpleIntRings.append(simpleRing)
        return shapely.geometry.Polygon(simpleExtRing, simpleIntRings)  # 根据返回的内外部的点坐标，使用shapely创建多边形

    def simplify_multiline(self, mline, threshold):
         # break MultiLineString into lines
        lineList = mline.geoms
        simpleLineList = []

        # call simplify_line on each
        for line in lineList:
            simpleLine = self.simplify_line(line, threshold)
            #if not none append to list
            if simpleLine:
                simpleLineList.append(simpleLine)

        # check that line count > 0, otherwise return None
        if not simpleLineList:
            return None

        # put back into multilinestring
        return MultiLineString(simpleLineList)

    def process_file(self, inFile, outFile, threshold):

        with fiona.open(inFile, 'r',encoding='utf-8') as input:  # fiona 专门用来打开GIS数据
            meta = input.meta   # 直接复制输入数据的元数据设置 在写入的时候比GDAL更加方便
            # meta数据集中包含driver、schema、crs等，schema内含property geometry
            with fiona.open(outFile, 'w', **meta,encoding='utf-8') as output:  # fiona用utf-8编码，gdal是gbk

                #获取几何类型，以字典的形式打开数据中的每一个要素，property包含字段属性、geometry包含几何坐标
                for myGeom in input:
                    myShape = shape(myGeom['geometry'])  # 根据打开的数据构造对应的shp，shapely和fiona读取主要
                    #有geometry 和 property两部分的内容

                    # 判断矢量数据类型
                    if isinstance(myShape, Polygon):
                        myShape = self.simplify_polygon(myShape, threshold)
                    elif isinstance(myShape, MultiPolygon):
                        myShape = self.simplify_multipolygon(myShape, threshold)
                    elif isinstance(myShape, LineString):
                        myShape = self.simplify_line(myShape, threshold)
                    elif isinstance(myShape, MultiLineString):
                        myShape = self.simplify_multiline(myShape, threshold)
                    else:
                        raise ValueError('Unhandled geometry type: ' + repr(myShape.type))

                    # write to outfile
                    if myShape is not None: #mapping 函数读取几何坐标，并返回为GeoJSON类的文件
                        output.write({'geometry':mapping(myShape),
                                      'properties': myGeom['properties'],
                                      'encoding':'utf-8'})

def Visvalingam(inFile,outFile,threshold=2e-8):
    # inputFile = 'D:\\专业课资料\\毕业设计\\测试数据\\K47E011007_2.shp'
    # # inputFile = 'D:\\专业课资料\\毕业设计\\河流\\road_JL.shp'
    # outputFile = 'D:\\test_visvalingam.shp'
    # threshold = 2e-8


    geomSimplifyObject = GeomSimplify()

    geomSimplifyObject.process_file(inFile, outFile, float(threshold))

    print("Finished simplifying file!")

