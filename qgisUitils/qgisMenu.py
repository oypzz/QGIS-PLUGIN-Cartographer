# @Time  : 2024/4/22 19:37
# @Filename : qgisMenu.py

import os
import os.path as osp

# import pydevd_pycharm
from osgeo import gdal
import traceback
from shutil import copyfile
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette,QColor
from PyQt5.QtWidgets import QMenu, QAction,QFileDialog,QMessageBox,QTableView,QDialog
from qgis import processing
from qgis.core import QgsLayerTreeNode, QgsLayerTree, QgsMapLayerType,QgsVectorLayer, QgsProject\
        ,QgsVectorFileWriter,QgsWkbTypes,Qgis,QgsFillSymbol,QgsSingleSymbolRenderer,QgsVectorLayerCache\
        ,QgsMapLayer,QgsRasterLayer,QgsLayerTreeGroup,QgsLayerTreeLayer
from qgis.gui import QgsLayerTreeViewMenuProvider, QgsLayerTreeView, QgsLayerTreeViewDefaultActions, QgsMapCanvas,QgsMessageBar,\
    QgsAttributeTableModel,QgsAttributeTableView,QgsAttributeTableFilterModel,QgsGui,QgsAttributeDialog,QgsProjectionSelectionDialog

from .attributeDialog import AttributeDialog
from .layerPropWindowWidgter import LayerPropWindowWidgeter

PROJECT = QgsProject.instance()

class menuProvider(QgsLayerTreeViewMenuProvider):
    def __init__(self,mainWindow, *args, **kwargs):  #该类中不指定参数个数
        super().__init__(*args, **kwargs)   #继承父类
        self.layerTreeView: QgsLayerTreeView = mainWindow.layerTreeView
        self.mapCanvas: QgsMapCanvas = mainWindow.mapCanvas  #获取当前画布中的图层
        self.mainWindows = mainWindow
        self.layer: QgsMapLayer = self.layerTreeView.currentLayer()
        self.lp = LayerPropWindowWidgeter(self.layer, self.mainWindows)

    def createContextMenu(self) -> QtWidgets.QMenu:
        try:
            menu = QMenu()
            self.actions : QgsLayerTreeViewDefaultActions = self.layerTreeView.defaultActions()
            if not self.layerTreeView.currentIndex().isValid():  #判断当前图层树中节点的数量

                # 清除图层 deleteAllLayer
                actionDeleteAllLayer = QAction('清除图层', menu)
                actionDeleteAllLayer.triggered.connect(lambda: self.deleteAllLayer())
                menu.addAction(actionDeleteAllLayer)

                menu.addAction('展开所有图层',self.layerTreeView.expandAllNodes)
                menu.addAction('折叠所有图层',self.layerTreeView.collapseAllNodes)
                return menu

            if len(self.layerTreeView.selectedLayers()) > 1:
                # 添加组
                self.actionGroupSelected = self.actions.actionGroupSelected()
                menu.addAction(self.actionGroupSelected)  #返回当前选取的图层

                actionDeleteSelectedLayers = QAction('删除选中图层',menu)  #菜单中新增选项，并在触发事件时进行删除操作
                actionDeleteSelectedLayers.triggered.connect(self.deleteSelectedLayer)
                menu.addAction(actionDeleteSelectedLayers)

                return menu

            node: QgsLayerTreeNode = self.layerTreeView.currentNode()  #获取当前节点数
            if node:
                if QgsLayerTree.isGroup(node):  #如果选中的是一个组节点
                    print("目前程序运行到这")
                    group: QgsLayerTreeGroup = self.layerTreeView.currentGroupNode()
                    self.actionRenameGroup = self.actions.actionRenameGroupOrLayer(menu)
                    menu.addAction(self.actionRenameGroup)
                    actionDeleteGroup = QAction('删除组', menu)
                    actionDeleteGroup.triggered.connect(lambda: self.deleteGroup(group))
                    menu.addAction(actionDeleteGroup)
                elif QgsLayerTree.isLayer(node):  #如果是图层
                    self.actionMoveToTop = self.actions.actionMoveToTop(menu)
                    menu.addAction(self.actionMoveToTop)
                    self.actionZoomToLayer = self.actions.actionZoomToLayer(self.mapCanvas, menu)
                    menu.addAction(self.actionZoomToLayer)


                    layer: QgsMapLayer = self.layerTreeView.currentLayer()

                    if layer.type() == QgsMapLayerType.VectorLayer: #判断是否为矢量图层
                        actionOpenAttributeDialog = QAction('打开属性表', menu)
                        actionOpenAttributeDialog.triggered.connect(lambda: self.openAttributeDialog(layer))
                        menu.addAction(actionOpenAttributeDialog)

                    actionOpenLayerProp = QAction('图层属性', menu)
                    actionOpenLayerProp.triggered.connect(lambda: self.openLayerPropTriggered(layer))
                    menu.addAction(actionOpenLayerProp)

                    actionDeleteLayer = QAction("删除图层", menu)
                    actionDeleteLayer.triggered.connect(lambda: self.deleteLayer(layer))
                    menu.addAction(actionDeleteLayer)

                return menu
        except:
              print(traceback.format_exc()) #返回并打印详细报错信息


    def updateRasterLayerRenderer(self, widget, layer):
        print("change")
        layer.setRenderer(widget.renderer())
        self.mapCanvas.refresh()

    def deleteSelectedLayer(self):
        deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除所选图层？", QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)  #最后面的参数代表是默认选中的按钮
        if deleteRes == QMessageBox.Yes:
            layers = self.layerTreeView.selectedLayers()
            for layer in layers:
                self.deleteLayer(layer)

    def deleteAllLayer(self):
        if len(PROJECT.mapLayers().values()) == 0:
            QMessageBox.about(None, '信息', '您的图层为空')
        else:
            deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除所有图层？", QMessageBox.Yes | QMessageBox.No,
                                                 QMessageBox.No)
            if deleteRes == QMessageBox.Yes:
                for layer in PROJECT.mapLayers().values():
                    self.deleteLayer(layer)

    def deleteGroup(self, group: QgsLayerTreeGroup):  #group继承的是node类，所以可以作为removeChildNode的参数
        deleteRes = QMessageBox.question(self.mainWindows, '信息', "确定要删除组？", QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
        if deleteRes == QMessageBox.Yes:
            layerTreeLayers = group.findLayers()
            for layer in layerTreeLayers:
                self.deleteLayer(layer.layer())
        PROJECT.layerTreeRoot().removeChildNode(group)  #从图层树中移除掉组代表的节点

    def deleteLayer(self,layer):
        # pydevd_pycharm.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
        PROJECT.removeMapLayer(layer)
        self.mapCanvas.refresh()
        return 0

    def openLayerPropTriggered(self,layer):
        try:
            # processing.run("native:dissolve", {'INPUT': 'D:/专业课资料/毕业设计/测试数据/K47E011007.shp', 'FIELD': ['GEOBODY_NA'],
            #                                    'SEPARATE_DISJOINT': True, 'OUTPUT': 'TEMPORARY_OUTPUT'})
            self.lp = LayerPropWindowWidgeter(layer, self.mainWindows) #实例化属性窗口类
            print(type(self.lp))
            self.lp.exec_()  #显示属性窗口
        except:
            #此处的类是一个属性类，第一个参数组件需要指明是哪个mainWindow
            QMessageBox.warning(self.mainWindows,'错误提示',f'{traceback.format_exc()}',QMessageBox.Close)
            print(traceback.format_exc())

    def openAttributeDialog(self, layer): #显示矢量图层属性表
        ad = AttributeDialog(self.mainWindows, layer)
        ad.show()