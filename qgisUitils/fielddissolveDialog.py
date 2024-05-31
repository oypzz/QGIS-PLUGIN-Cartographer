# @Time  : 2024/5/1 17:17
# @Filename : fielddissolveDialog.py
import datetime
import os
# import pydevd_pycharm
import qgis
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QAction
from qgis._core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis, QgsVectorLayer, QgsProcessingParameterField, \
    QgsProcessingFeedback, QgsProcessingContext, QgsFeature, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest
from qgis import processing
from .layerDissolveWindow import Ui_DissolveByAttribute
from datetime import datetime
from qgis.gui import QgisInterface
import geopandas as gpd



PROJECT = QgsProject.instance()

class FieldDissolveWindow(QDialog, Ui_DissolveByAttribute):
    def __init__(self,layer,parent=None):
        super(FieldDissolveWindow,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.initUI()
        self.connFunc()

    def initUI(self):
        self.mFieldComboBox.setText = 'Dissolve field(s)'
        self.mapLayerComboBox.layerChanged.connect(self.mFieldComboBox.setLayer)
        self.output_FileWidget.setStorageMode(3)
        self.output_FileWidget.setFilePath('')

        # self.testBtn()


    def connFunc(self):
        """This function manage all the widgets in the dialog"""
        # self.mFieldComboBox.connected(self.mapLayerComboBox.layerChanged)
        # self.fileBrowserBtn.click =  QAction(self,'浏览文件')
        # self.fileBrowserBtn.clicked(self.actionFileBrowser)
        self.runBtn.clicked.connect(self.DissolvePolygons)  #button按钮传递QT内置信号，要与QGIS连接需要用connect函数
        self.closeBtn.clicked.connect(self.exitWindow)
        self.cancelBtn.clicked.connect(self.cancel_processing)

    def DissolvePolygons(self):
        """Dissolve selected polygons into a larger one """
        layer:QgsVectorLayer = self.mapLayerComboBox.currentLayer()
        source = layer.source()  #获取当前图层的源路径
        input_layer =  QgsProcessingFeatureSourceDefinition(source,
                                                   selectedFeaturesOnly=True,
                                                   featureLimit=5,
                                                   geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid)
        features:QgsFeature = layer.selectedFeatures()
        field:QgsProcessingParameterField = self.mFieldComboBox.currentField()
        keep_disjoint:bool = self.separate_checkBox.isChecked()
        feedback: QgsProcessingFeedback = None
        context: QgsProcessingContext = None
        # self.progressBar.setRange(0, 0)
        output  = self.get_outFile()
        time_sta = datetime.now()
        pydevd_pycharm.settrace('localhost', port=53111, stdoutToServer=True, stderrToServer=True)
        if layer.geometryType() == QgsWkbTypes.GeometryType.PolygonGeometry: #首先判断是否为面图层
            if self.select_checkBox.isChecked() and len(layer.selectedFeatureIds()) > 1 :
                self.progressBar.setValue(0)
                processing.run("native:dissolve", {
                    'INPUT': input_layer,
                    'FIELD': field,
                    'SEPARATE_DISJOINT': keep_disjoint,
                    'OUTPUT': output
                }, context=context, feedback=feedback, is_child_algorithm=False)
                print("Code is running here")
                self.progressBar.setValue(100)
                time_end = datetime.now()
                print('delta_time:', time_end - time_sta)
            elif not self.select_checkBox.isChecked():  #未勾选只处理选中要素
                if not keep_disjoint:
                    self.progressBar.setValue(0)
                    test_data = gpd.read_file(source, encoding='gbk')  # 防止出现中文乱码
                    data_dissolve = test_data.dissolve(by=field)  # 将合并的数据进行拆分
                    data_dissolve.to_file(driver='ESRI Shapefile', filename=output, encoding='gbk')
                    self.progressBar.setValue(100)
                    time_end = datetime.now()
                    print('delta_time:', time_end - time_sta)
                elif  keep_disjoint:
                    self.progressBar.setValue(0)
                    test_data = gpd.read_file(source, encoding='gbk')  # 防止出现中文乱码
                    data_dissolve = test_data.dissolve(by=field).explode(index_parts=True)  # 将合并的数据进行拆分
                    data_dissolve.to_file(driver='ESRI Shapefile', filename=output, encoding='gbk')
                    self.progressBar.setValue(100)
                    time_end = datetime.now()
                    print('delta_time:', time_end - time_sta)

        else:
            QMessageBox.information(self,'Processing error','Make sure the layer is a ploygon!',QMessageBox.Close)
        if self.output_checkBox.isChecked():
           myIface = MyIface()
           myIface.addVectorLayer(output, layer.name()+"_dissolved:", "ogr")
           QMessageBox.information(self,'Processing result','The dissolve operation has been executed!')
           self.exitWindow()
            # self.iface.addVectorLayer(output, layer.name()+"_generalized:", "ogr")


    def get_outFile(self):
        """This function is to make sure the file has a .shp suffix"""
        file_dir = self.output_FileWidget.filePath()
        file_name = file_dir.split('\\')[-1]
        if len(file_name.split('.')) == 2 and file_name.split('.')[-1] == 'shp' :
            return file_dir
        else :
            return file_dir + '.shp'


    def cancel_processing(self):
        """When the cancel btn is clicked, the processing progress stops"""
        self.progressBar.setValue(0)
        if self.output_FileWidget.filePath() != '' :
            file = self.output_FileWidget.filePath()
            print(file)
            filename = file.split('.')[0]
            # filename = filename.split('.')[0]
            # pydevd_pycharm.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
            remove_filename = filename + '.dbf'
            print(remove_filename)
            os.remove( filename + '.dbf')
            os.remove( filename + '.prj')
            os.remove( filename + '.cpg')
            os.remove( filename + '.shx')
            os.remove( filename + '.shp')
            QMessageBox.warning(self,'Cancel dialog','The processing progress has been stopped')
        else:
            QMessageBox.warning(self,'warning','There is something wrong')


    def progress_changed(self):
        self.progressbar.setValue(100)

    def testBtn(self):
        """This funciton is used to test the button operation"""
        QMessageBox.information(self,"testResult","This button functions well!")


    def exitWindow(self):
        """This function is used to close the processing window"""
        self.close()


def addVectorLayer(uri, provider, name):
    vl = QgsVectorLayer(uri, name, provider)
    QgsProject.instance().addMapLayer(vl)
    return vl, name

class MyIface(QgisInterface):
    def __init__(self):
        QgisInterface.__init__(self)

    def addVectorLayer(self, path, name, provider):
        return addVectorLayer(path, provider, name)