# @Time  : 2024/4/22 9:34
# @Filename : LayerUtils.py
from qgis._core import QgsProject, QgsRasterDataProvider, QgsCoordinateReferenceSystem, QgsRectangle, \
    QgsVectorDataProvider, QgsWkbTypes
from qgis._gui import QgsMapCanvas
from qgis.core import QgsMapLayer,QgsRasterLayer,QgsVectorLayer
import os
import os.path as osp


PROJECT = QgsProject.instance()  #封装一个Qgs项目，并返回实例对象，以此设置地图样式、参数等

def addMapLayer(layer:QgsMapLayer,mapCanvas:QgsMapCanvas,firstAddLayer=False):
    if layer.isValid(): #returns the status of the layer
        if firstAddLayer: #判断是否为第一次加载图层
            mapCanvas.setDestinationCrs(layer.crs())  #设置画布的参考投影坐标系
            mapCanvas.setExtent(layer.extent()) #设置画布的范围

        while(PROJECT.mapLayersByName(layer.name())): #return the display name of the file,就是osp.basename()返回值
            layer.setName(layer.name()+"_1")

        PROJECT.addMapLayer(layer)
        layers = [layer] + [PROJECT.mapLayer(i) for i in PROJECT.mapLayers()]
        mapCanvas.setLayers(layers)
        mapCanvas.refresh()

def readRasterFile(rasterFilePath):
    """QgsRasterLayer方法创建地图需要的QgsLayer图层，默认使用了GDAL库"""
    rasterLayer = QgsRasterLayer(rasterFilePath,osp.basename(rasterFilePath))
    return rasterLayer

def getRasterLayerAttrs(rasterLayer:QgsRasterLayer):  #参数中的冒号代表类型建议符
    """该方法用于获取栅格图层的属性"""
    rpd:QgsRasterDataProvider = rasterLayer.dataProvider()  #provider对象提供数据来源信息
    crs:QgsCoordinateReferenceSystem = rasterLayer.crs()
    extent:QgsRectangle = rasterLayer.extent()  #Rectangle类获取栅格图像的外接矩形并返回图层范围
    qgisDataTypeDict = {
        0: "UnknownDataType",
        1: "Uint8",
        2: "UInt16",
        3: "Int16",
        4: "UInt32",
        5: "Int32",
        6: "Float32",
        7: "Float64",
        8: "CInt16",
        9: "CInt32",
        10: "CFloat32",
        11: "CFloat64",
        12: "ARGB32",
        13: "ARGB32_Premultiplied"
    }  #API中返回数据类型对应的编号
    resDic = {
        "name": rasterLayer.name(),
        "dataType": qgisDataTypeDict[rpd.dataType(1)], #获取数据第一个波段代表的数据类型，并与字典类型对应
        "memory": getFileSize(rasterLayer.source()), #获取数据所占内存大小
        "source": rasterLayer.source(),
        #冒号代表推荐类型为六位小数浮点数据
        "extent": f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}];max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",
        "height":f"{rasterLayer.height()}",
        "width":f"{rasterLayer.width()}",
        "bands":f"{rasterLayer.bandCount()}",
        "crs": crs.description() #获取目标图层坐标系的详细描述
    }
    return resDic


def readVectorFile(vectorFilePath):
    """创建需要的矢量图层"""
    vectorLayer = QgsVectorLayer(vectorFilePath,osp.basename(vectorFilePath),'ogr')  #basename方法获取末端文件名,第三个参数表示数据源
    return  vectorLayer

def getVectorLayerAttrs(vectorLayer:QgsVectorLayer):  #参数中的冒号代表类型建议符
    """该方法用于获取栅格图层的属性"""
    vdp:QgsVectorDataProvider = vectorLayer.dataProvider()
    extent:QgsRectangle = vectorLayer.extent()
    crs:QgsCoordinateReferenceSystem = vectorLayer.crs()
    qgisDataTypeDict = {
        0: "UnknownDataType",
        1: "Uint8",
        2: "UInt16",
        3: "Int16",
        4: "UInt32",
        5: "Int32",
        6: "Float32",
        7: "Float64",
        8: "CInt16",
        9: "CInt32",
        10: "CFloat32",
        11: "CFloat64",
        12: "ARGB32",
        13: "ARGB32_Premultiplied"
    }  # API中返回数据类型对应的编号
    resDic = {
        "name": vectorLayer.name(),
        "source":vectorLayer.source(),
        "memory":getFileSize(vectorLayer.source()),
        "extent": f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}];max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",
        "geoType":QgsWkbTypes.geometryDisplayString(vectorLayer.geometryType()), #获取几何图形类型
        "featureNum":f"{vectorLayer.featureCount()}",
        "encoding":vdp.encoding(),
        "crs":crs.description(),
        "dpSource":vdp.description()

    }
    return resDic

def getFileSize(filePath):
    fsize = osp.getsize(filePath)  # os.getsize方法返回的是字节大小，还需要进行kb、mb、gb的换算

    if fsize < 1024:
        return f"{round(fsize, 2)}Byte" #round方法返回浮点数的四舍五入值，第二个参数表示取舍的位数
    else:
        KBX = fsize / 1024
        if KBX < 1024:
            return f"{round(KBX, 2)}Kb"
        else:
            MBX = KBX / 1024
            if MBX < 1024:
                return f"{round(MBX, 2)}Mb"
            else:
                return f"{round(MBX/1024,2)}Gb"

if __name__ == '__main__':
    # tifPath = r"D:\DEM_Clip.img"
    # tifLayer = readRasterFile(tifPath)
    # getRasterLayerAttrs(tifLayer)
    shpPath = r"D:\ROI-test.shp"
    shpLayer = readVectorFile(shpPath)
    getVectorLayerAttrs(shpLayer)
