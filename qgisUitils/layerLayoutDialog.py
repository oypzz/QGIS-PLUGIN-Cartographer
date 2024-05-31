# @Time  : 2024/5/28 8:51
# @Filename : layerLayoutDialog.py

import os
# import pydevd_pycharm
import qgis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QAction
from qgis._core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis, QgsVectorLayer, QgsPrintLayout, QgsLayoutSize, \
    QgsUnitTypes, QgsLayoutItemPage, QgsLayoutItemMap, QgsCoordinateReferenceSystem, QgsMapSettings, QgsRectangle, \
    QgsLayoutPoint, QgsLayoutItemLegend, QgsLayerTree, QgsLegendStyle, QgsLegendRenderer, QgsLayoutItemScaleBar, \
    QgsLayoutItemPicture, QgsLayoutItemMapGrid, QgsLayoutItemLabel, QgsLayoutExporter
from qgis.gui import QgisInterface
from .LayoutDialog import Ui_LayoutDialog
from .generalizer import Smoother
from .test.test_exaggerate import exaggerate
from .LayerUtils import readVectorFile

PROJECT = QgsProject.instance()
class layerLayoutDialog(QDialog, Ui_LayoutDialog):
    def __init__(self,layer,iface,parent=None):
        super(layerLayoutDialog,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        # self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.iface = iface
        self.initUI()
        self.connFunc()

    def initUI(self):
        """This function initialize  the window"""
        self.output_FileWidget_3.setStorageMode(3)
        self.output_FileWidget_3.setFilePath('')

    def connFunc(self):
        """This function controls the widgets interaction"""
        self.runBtn.clicked.connect(self.layerLayout)
        self.closeBtn.clicked.connect(self.exitWindow)

    def layerLayout(self):
        """Lay out settings"""
        layer = self.mapLayerComboBox_3.currentLayer()

        project = QgsProject.instance()
        manager = project.layoutManager()
        layoutName = 'MyLayout'
        layouts_list = manager.printLayouts()
        # 移除项目中重复的布局
        for layout in layouts_list:
            if layout.name() == layoutName:
                manager.removeLayout(layout)
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.pageCollection().pages()[0].setPageSize(QgsLayoutSize(310, 230, QgsUnitTypes.LayoutMillimeters))
        layout.setName(layoutName)

        manager.addLayout(layout)

        # 获取页面大小
        width = layout.width()
        print(width)
        page = QgsLayoutItemPage(layout)

        # 创建地图项目
        map = QgsLayoutItemMap(layout)
        map.setRect(20, 20, 20, 20)  # 起始坐标的xy，高和宽，此处只是在初始化过程中的随意设置
        map.zoomToExtent(self.iface.mapCanvas().extent())
        crs = self.mQgsProjectionSelectionWidget.crs()
        map.setCrs(crs)
        # print('extent now:',map.extent())
        # print(map.crs())

        # set the map extent
        ms = QgsMapSettings()
        ms.setDestinationCrs(crs)
        # layer.setCrs(QgsCoordinateReferenceSystem(4610))
        print("layer:", layer.crs())
        print(ms.destinationCrs())
        ms.setLayers([layer])  # set layers to be mapped
        rect = QgsRectangle(ms.fullExtent())  # 设置地图的全副作为地图的显示范围
        # print('extent:',ms.fullExtent())  #到这里已经是xian 80坐标系
        rect.scale(1.0)  # 缩放比例系数，数值越大图层越小
        ms.setExtent(rect)
        map.setExtent(rect)
        map.mapUnitsToLayoutUnits()
        map.setFrameEnabled(True)

        map.setBackgroundColor(QColor(255, 255, 255, 0))
        # map.zoomToExtent(iface.mapCanvas().extent())
        layout.addLayoutItem(map)

        map.attemptMove(QgsLayoutPoint(20, 30, QgsUnitTypes.LayoutMillimeters))
        map.attemptResize(QgsLayoutSize(160, 160, QgsUnitTypes.LayoutMillimeters))

        # 设置图例
        if self.checkBox_legend.isChecked():
            legend = QgsLayoutItemLegend(layout)
            legend.setTitle("图     例")
            legend.setTitleAlignment(Qt.AlignmentFlag.AlignHCenter)  # 设置图例水平居中
            layerTree = QgsLayerTree()
            layerTree.addLayer(layer)
            legend.model().setRootGroup(layerTree)
            tree_layer = legend.model().rootGroup().findLayer(layer)  # QgsLayerTreeLayer 继承自 QgsLayerTreeNode
            print(tree_layer)
            QgsLegendRenderer.setNodeLegendStyle(tree_layer, QgsLegendStyle.Hidden)  # 设置起始节点隐藏
            legend.updateLegend()
            legend.setLegendFilterByMapEnabled(True)
            layout.addLayoutItem(legend)
            legend.attemptMove(QgsLayoutPoint(210, 15, QgsUnitTypes.LayoutMillimeters))

        # 设置比例尺
        if self.checkBox_scalebar.isChecked():
            scalebar = QgsLayoutItemScaleBar(layout)
            scalebar.setStyle('Single Box')
            scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
            scalebar.setNumberOfSegments(3)  # 比例尺上分隔线的数量
            scalebar.setNumberOfSegmentsLeft(0)
            scalebar.setUnitsPerSegment(1)
            scalebar.setLinkedMap(map)
            scalebar.setUnitLabel('km')
            scalebar.setFont(QFont('Arial', 14))
            scalebar.update()
            scalebar.attemptResize(QgsLayoutSize(23, 23, QgsUnitTypes.LayoutMillimeters))
            layout.addLayoutItem(scalebar)
            scalebar.attemptMove(QgsLayoutPoint(270, 25, QgsUnitTypes.LayoutMillimeters))
            print('runnnn')

        # 创建指北针
        if self.checkBox_arrow.isChecked():
            north = QgsLayoutItemPicture(layout)
            north.setPicturePath("D:\\QGIS\\apps\\qgis\\svg\\arrows\\NorthArrow_02.svg")
            layout.addLayoutItem(north)
            north.attemptResize(QgsLayoutSize(18, 18, QgsUnitTypes.LayoutMillimeters))
            north.attemptMove(QgsLayoutPoint(270, 5, QgsUnitTypes.LayoutMillimeters))

        # 创建网格
        # 要用map.grid才能起作用
        map.grid().setEnabled(True)
        interval = self.SpinBox_intervals.value()
        map.grid().setIntervalY(interval)
        map.grid().setIntervalX(interval)
        map.grid().setCrs(crs)
        map.grid().setUnits(QgsLayoutItemMapGrid.MapUnit)
        if self.comboBox_grid.currentIndex() == 0:
            map.grid().setFrameStyle(QgsLayoutItemMapGrid.ExteriorTicks)
            map.grid().setAnnotationFormat(3)  # 设置标注格式
            map.grid().setAnnotationEnabled(True)
        elif self.comboBox_grid.currentIndex() == 1:
            map.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
            map.grid().setAnnotationFormat(3)  # 设置标注格式
            map.grid().setAnnotationEnabled(True)
        elif self.comboBox_grid.currentIndex() == 2:
            map.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorExteriorTicks)
            map.grid().setAnnotationFormat(3)  # 设置标注格式
            map.grid().setAnnotationEnabled(True)
            # grid.setCrs(QgsCoordinateReferenceSystem(4610))

        # 设置标题
        text = self.txt_title.text()
        title = QgsLayoutItemLabel(layout)
        title.setText(text)
        title.setFont(QFont('宋体', 24))
        title.adjustSizeToText()
        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(60, 5, QgsUnitTypes.LayoutMillimeters))  # 使得标题水平居中
        # title.setHAlign(Qt.AlignmentFlag.AlignHCenter)

        layout = manager.layoutByName(layoutName)
        exporter = QgsLayoutExporter(layout)

        # fn = 'D:\\专业课资料\\毕业设计\\测试数据\\layout_export.pdf'
        # fn2 = 'D:\\专业课资料\\毕业设计\\测试数据\\layout_export.png'
        fn = self.output_FileWidget_3.filePath()
        exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())
        # exporter.exportToPdf(fn, QgsLayoutExporter.PdfExportSettings())
        QMessageBox.information(self, 'Process result', 'The lay out has been exported successfully!', QMessageBox.Ok)
        self.exitWindow()

    def exitWindow(self):
        """This function is used to close the processing window"""
        self.close()

    def get_outFile(self):
        """This function is to make sure the file has a .shp suffix"""
        file_dir = self.output_file.filePath()
        file_name = file_dir.split('\\')[-1]
        if len(file_name.split('.')) == 2 and file_name.split('.')[-1] == 'shp':
            return file_dir
        else:
            return file_dir + '.shp'