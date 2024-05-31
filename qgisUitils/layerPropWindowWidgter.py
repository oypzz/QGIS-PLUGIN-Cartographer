# @Time  : 2024/4/23 19:01
# @Filename : layerPropWindowWidgter.py

import os
import traceback
from qgis.core import QgsVectorLayer,QgsRasterLayer,QgsProject,QgsStyle,QgsSymbol,QgsWkbTypes,QgsSymbolLayer,Qgis,QgsFeatureRenderer
from qgis.gui import QgsRendererRasterPropertiesWidget,QgsSingleSymbolRendererWidget,QgsCategorizedSymbolRendererWidget
from PyQt5.QtCore import QModelIndex
from qgis.PyQt import uic
from .layerPropWindow import Ui_LayerProp
from PyQt5.QtWidgets import QWidget,QDialog,QListWidgetItem,QTabBar,QMessageBox
from .LayerUtils import getRasterLayerAttrs,getVectorLayerAttrs

PROJECT = QgsProject.instance()

class LayerPropWindowWidgeter(QDialog, Ui_LayerProp):
    def __init__(self,layer,mainwindows,parent=None):
        """
     tab 信息含义：
        0 栅格信息 1 矢量信息 2 栅格图层渲染 3 矢量图层渲染
        :param layer:
        :param parent:
        """
        super(LayerPropWindowWidgeter,self).__init__(mainwindows)
        self.setupUi(self)
        self.layer = layer
        self.mainwindows = mainwindows
        self.parentWindow = parent
        self.initUI()
        self.connectFunc()

    def initUI(self):
        layerbar = self.tabWidget.findChild(QTabBar)
        layerbar.hide()
        renderBar = self.comboTabWidget.findChild(QTabBar)
        renderBar.hide()  #隐藏Tab的选项卡
        self.listWidget.setCurrentRow(0)
        self.initInfomationTab()
        self.decideRasterNVector(0)

    def connectFunc(self):
        self.listWidget.itemClicked.connect(self.listWidgetItemClicked) #将点击事件与控件连接
        self.okPb.clicked.connect(lambda : self.renderApplyPbClicked(needClose=True)) #点击确定按钮不修改渲染方式
        self.cancelPb.clicked.connect( self.close )
        self.applyPb.clicked.connect(lambda : self.renderApplyPbClicked(needClose=False)) #点击应用按钮后修改图层的渲染方式
        self.vecterRenderCB.currentIndexChanged.connect(self.vecterRenderCBChanged) #根据选中的渲染方式显示渲染页面

    # 切换矢量渲染方式
    def vecterRenderCBChanged(self):
        self.comboTabWidget.setCurrentIndex(self.vecterRenderCB.currentIndex()) #单一渲染方式或者分类后的渲染方式

    def initInfomationTab(self):  #根据当前图层决定属性页中显示的内容，并读取图层信息
        if type(self.layer) == QgsRasterLayer:
            rasterLayerDict = getRasterLayerAttrs(self.layer) #得到函数返回的信息字典
            self.rasterNameLabel.setText(rasterLayerDict['name'])
            self.rasterSourceLabel.setText(rasterLayerDict['source'])
            self.rasterMemoryLabel.setText(rasterLayerDict['memory'])
            self.rasterExtentLabel.setText(rasterLayerDict['extent'])
            self.rasterWidthLabel.setText(rasterLayerDict['width'])
            self.rasterHeightLabel.setText(rasterLayerDict['height'])
            self.rasterDataTypeLabel.setText(rasterLayerDict['dataType'])
            self.rasterBandNumLabel.setText(rasterLayerDict['bands'])
            self.rasterCrsLabel.setText(rasterLayerDict['crs'])
            self.rasterRenderWidget = QgsRendererRasterPropertiesWidget(self.layer, self.mainwindows.mapCanvas,parent=None) #子级弹窗需要设置父级窗体
            self.layerRenderLayout.addWidget(self.rasterRenderWidget)

        elif type(self.layer) == QgsVectorLayer:
            self.layer : QgsVectorLayer
            vectorLayerDict = getVectorLayerAttrs(self.layer)
            print(vectorLayerDict)
            self.vectorNameLabel.setText(vectorLayerDict['name'])
            self.vectorSourceLabel.setText(vectorLayerDict['source'])
            self.vectorMemoryLabel.setText(vectorLayerDict['memory'])
            self.vectorExtentLabel.setText(vectorLayerDict['extent'])
            self.vectorGeoTypeLabel.setText(vectorLayerDict['geoType'])
            self.vectorFeatureNumLabel.setText(vectorLayerDict['featureNum'])
            self.vectorEncodingLabel.setText(vectorLayerDict['encoding'])
            self.vectorCrsLabel.setText(vectorLayerDict['crs'])
            self.vectorDpLabel.setText(vectorLayerDict['dpSource'])

            # single Render获取API中的渲染方式并添加到Tab页面中
            self.vectorSingleRenderWidget = QgsSingleSymbolRendererWidget(self.layer,QgsStyle.defaultStyle(),self.layer.renderer())
            self.singleRenderLayout.addWidget(self.vectorSingleRenderWidget)

            # category Render
            self.vectorCateGoryRenderWidget = QgsCategorizedSymbolRendererWidget(self.layer,QgsStyle.defaultStyle(),self.layer.renderer())
            self.cateRenderLayout.addWidget(self.vectorCateGoryRenderWidget)

    def decideRasterNVector(self,index):  #根据选中的Tab，对应显示不同页面的内容，其他内容隐藏
        if index == 0:
            if type(self.layer) == QgsRasterLayer:
                self.tabWidget.setCurrentIndex(0)
            elif type(self.layer) == QgsVectorLayer:
                self.tabWidget.setCurrentIndex(1)
        elif index == 1:
            if type(self.layer) == QgsRasterLayer:
                self.tabWidget.setCurrentIndex(2)
            elif type(self.layer) == QgsVectorLayer:
                self.tabWidget.setCurrentIndex(3)

    def listWidgetItemClicked(self,item:QListWidgetItem):
        tempIndex = self.listWidget.indexFromItem(item).row() #返回目前选中的列表行
        self.decideRasterNVector(tempIndex) #选中后根据是矢量还是栅格来确定右侧显示的内容

    def renderApplyPbClicked(self,needClose=False):
        if self.tabWidget.currentIndex() <= 1:
            print("没有在视图里，啥也不干")
        elif type(self.layer) == QgsRasterLayer:
            self.rasterRenderWidget : QgsRendererRasterPropertiesWidget
            self.rasterRenderWidget.apply()
        elif type(self.layer) == QgsVectorLayer:
            print("矢量渲染")
            #self.vectorRenderWidget : QgsSingleSymbolRendererWidget
            self.layer : QgsVectorLayer
            if self.comboTabWidget.currentIndex() == 0:
                renderer = self.vectorSingleRenderWidget.renderer()
            else:
                renderer = self.vectorCateGoryRenderWidget.renderer()
            self.layer.setRenderer(renderer)
            self.layer.triggerRepaint()
        self.mainwindows.mapCanvas.refresh()
        if needClose:
            self.close()