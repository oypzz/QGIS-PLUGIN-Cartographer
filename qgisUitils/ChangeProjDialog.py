# @Time  : 2024/5/14 11:18
# @Filename : ChangeProjDialog.py
import qgis
from PyQt5.QtWidgets import QDialog, QMessageBox
from qgis._gui import QgisInterface

from .TransformProjDialog import Ui_TransformProjDialog
from qgis._core import QgsProject, QgsVectorLayer, QgsVectorFileWriter

PROJECT = QgsProject.instance()

class ProjChangeWindow(QDialog, Ui_TransformProjDialog):
    def __init__(self,layer,parent=None):
        super(ProjChangeWindow,self).__init__()
        self.setupUi(self)
        self.layer: QgsVectorLayer = layer
        self.iface = qgis.gui.QgisInterface
        self.parentWindow = parent
        self.initUI()
        self.connFunc()

    def initUI(self):
        # self.layerCbmBox.layerChanged.connect(self.Proj_selectBox.setLayerCrs)
        if  not self.layer :
            QMessageBox.warning(self, 'Process error', 'Please put in file!')
            print('error')
        elif self.layerCbmBox.layerChanged:
            lyerCrs = self.layerCbmBox.currentLayer().sourceCrs()
            self.Proj_selectBox.setLayerCrs(lyerCrs)
        self.output_file.setStorageMode(3)
        self.output_file.setFilePath('')

        # self.testBtn()


    def connFunc(self):
        """This function manage all the widgets in the dialog"""
        self.closeBtn.clicked.connect(self.exitWindow)
        self.runBtn.clicked.connect(self.ChangeProj)
        # self.cancelBtn.clicked.connect(self.cancel_processing)


    def ChangeProj(self):
        """Execute the re-proj process """
        lyr = self.layer.clone()
        crs = self.Proj_selectBox.crs()
        save_path = self.get_outFile()
        options = QgsVectorFileWriter.SaveVectorOptions()
        context = QgsProject.instance().transformContext()
        lyr.setCrs(crs)
        options.driverName = "ESRI Shapefile"
        # options.fileEncoding = "GBK"
        QgsVectorFileWriter.writeAsVectorFormatV3(lyr,save_path,transformContext=context,options=options)
        QMessageBox.information(self,'Processing result','The layer has been re-projected correctly!')
        myIface = MyIface()
        myIface.addVectorLayer(save_path, self.layer.name() + "_projected:", "ogr")



    def get_outFile(self):
        """This function is to make sure the file has a .shp suffix"""
        file_dir = self.output_file.filePath()
        file_name = file_dir.split('\\')[-1]
        if len(file_name.split('.')) == 2 and file_name.split('.')[-1] == 'shp' :
            return file_dir
        else :
            return file_dir + '.shp'


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