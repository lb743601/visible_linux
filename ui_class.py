from ui import Ui_MainWindow  
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer,QThread,pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
#import ximea_camera_class as camera
import guide_camera_class as camera
import time
import serial
import serial.tools.list_ports
import motor_class
import numpy as np
import datetime
from PIL import Image
import h5py
import sys
sys.path.append('/home/jetson/Downloads/mst++/MST-plus-plus-master/predict_code/')
import run
import os
class outmulti(QThread):
    finish_signal = pyqtSignal(str)
    
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
    
    def run(self):
        self.input_path = self.main_app.ui.lineEdit_6.text()
        if self.input_path != "":
            # 获取MAT文件的目录和文件名
            file_dir, file_name = os.path.split(self.input_path)
            # 获取MAT文件名（不包括扩展名）
            folder_name = os.path.splitext(file_name)[0]
            # 创建与MAT文件同级的新文件夹
            output_folder = os.path.join(file_dir, folder_name)
            os.makedirs(output_folder, exist_ok=True)
            with h5py.File(self.input_path, 'r') as f:
                cube_data = f['cube']
                num_images, height, width = cube_data.shape
                for i in range(num_images):
                    image_data = cube_data[i, :, :]
                    image_data = (image_data - image_data.min()) / (image_data.max() - image_data.min()) * 255
                    image_data = image_data.astype(np.uint8)
                    image_data = np.transpose(image_data)
                    image = Image.fromarray(image_data, mode='L')
                    image_path = os.path.join(output_folder, f"image_{i+1}.bmp")
                    image.save(image_path)
            self.finish_signal.emit("finish output multi")
        else:
            self.finish_signal.emit("failed output multi")
class construct(QThread):
    finish_signal = pyqtSignal(str)
    def __init__(self,main_app):
        super().__init__()
        self.main_app=main_app
    def run(self):
        self.model_path=self.main_app.ui.lineEdit_4.text()
        self.input_image_path=self.main_app.ui.lineEdit_7.text()
        self.output_path=self.main_app.ui.lineEdit_5.text()
        if(self.model_path!="" and self.input_image_path!="" and  self.output_path!=""):
            run.exc(self.model_path,self.input_image_path,self.output_path)
            self.finish_signal.emit("finish construct")  
        else:
            self.finish_signal.emit("failed construct")  
class autothread(QThread):
    finish_signal = pyqtSignal(str)
    update_image_signal = pyqtSignal(np.ndarray)
    def __init__(self,main_app):
        super().__init__()
        self.main_app=main_app
    def run(self):
        self.main_app.judge_dir()
        width,height=self.main_app.cam_data.shape
        self.rgb_data=np.zeros((3,width,height))
        for i in range(3):
            self.rgb_data[i]=self.main_app.cam_data
            self.main_app.mot.send_data('start_pwm(200,72,4267)')
            time.sleep(2)
        self.update_image_signal.emit(self.rgb_data)
        self.finish_signal.emit("finish auto capture")    
    
class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        self.cam=camera.camera()
        self.cam.set_ex(80000)
        self.cam.set_ds("XI_DWN_4x4")
        self.cam_data=None
        self.cam_flag=False
        
        #相机相关内容
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.open_camera)
        self.ui.textBrowser.setReadOnly(True)
        self.ui.lineEdit_3.setReadOnly(True)
        self.ui.lineEdit_4.setReadOnly(True)
        self.ui.lineEdit_5.setReadOnly(True)
        self.ui.lineEdit_6.setReadOnly(True)
        self.update_timer=QTimer()
        self.update_timer.timeout.connect(self.update_image)
        self.ui.pushButton_2.clicked.connect(self.set_ex)
        self.ui.comboBox.addItem("XI_DWN_4x4")
        self.ui.comboBox.addItem("XI_DWN_2x2")
        self.ui.comboBox.addItem("XI_DWN_1x1")
        self.ui.pushButton_3.clicked.connect(self.set_ds)
        self.ui.pushButton_4.clicked.connect(self.open_serial)
        self.ui.pushButton_5.clicked.connect(self.send_command)
        self.ui.pushButton_15.clicked.connect(self.update_port)
        self.ui.pushButton_6.clicked.connect(self.viewfile)
        self.ui.pushButton_7.clicked.connect(self.save_single_image)
        self.ui.pushButton_8.clicked.connect(self.auto)
        self.ui.pushButton_11.clicked.connect(self.viewfile2)
        self.ui.pushButton_14.clicked.connect(self.open_file_dialog3)
        self.ui.pushButton_10.clicked.connect(self.open_file_dialog)
        self.ui.pushButton_9.clicked.connect(self.open_file_dialog)
        self.ui.pushButton_16.clicked.connect(self.open_file_dialog2)
        self.ui.pushButton_12.clicked.connect(self.constr)
        self.ui.pushButton_13.clicked.connect(self.outmulti)
        #界面相关内容
        self.mot=motor_class.mot()
        self.mot_flag=False
        self.mot_dir=1
        #电机相关内容
        self.t=autothread(self)
        self.t.finish_signal.connect(self.update_text)
        self.t.update_image_signal.connect(self.save_rgb_image)
        self.construct_thread=construct(self)
        self.construct_thread.finish_signal.connect(self.update_text)
        self.out_thread=outmulti(self)
        self.out_thread.finish_signal.connect(self.update_text)
    def open_camera(self):
        if self.ui.pushButton.text()=="open the camera":
            self.cam.start()
            self.update_timer.start(1)
            self.ui.pushButton.setText("close the camera")
            self.update_text("open the camera")
            self.cam_flag=True
        else:
            if self.ui.pushButton.text()=="close the camera":
                self.cam.stop_acq()
                self.update_timer.stop()
                self.ui.pushButton.setText("open the camera")
                self.update_text("close the camera")
                self.cam_flag=False
    def update_image(self):
        self.cam_data=self.cam.get_current_image()
        
        #self.update_text(str(self.cam_data.shape))
        if self.cam_data is not None:
            height, width = self.cam_data.shape
            qimage = QImage(self.cam_data.data, width, height, QImage.Format_Grayscale8)
            self.ui.camera_show.setPixmap(QPixmap.fromImage(qimage))
            self.ui.camera_show.setScaledContents(True)  # 自动缩放以适应窗口大小
            #self.resize(width, height)
    def save_rgb_image(self,rgb_data):
        if self.cam_flag:
            if self.ui.lineEdit_3.text()=="":
                save_path="/home/jetson/Downloads/visible/data"
            else:
                save_path=self.ui.lineEdit_3.text()
            current_time = datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
            save_name=save_path+"/"+current_time+".bmp"
            if rgb_data.shape[0] == 3:
                rgb_data = np.transpose(rgb_data, (1, 2, 0))
            rgb_data = rgb_data.astype(np.uint8)
            image = Image.fromarray(rgb_data)
            image.save(save_name)
            self.update_text("save sucess")
        else:
            self.update_text("cam is not opened")
    def save_single_image(self):
        if self.cam_flag:
            if self.ui.lineEdit_3.text()=="":
                save_path="/home/jetson/Downloads/visible/data"
            else:
                save_path=self.ui.lineEdit_3.text()
            current_time = datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
            save_name=save_path+"/"+current_time+".bmp"
            image = Image.fromarray(self.cam_data)
            image.save(save_name)
            self.update_text("save sucess")
        else:
            self.update_text("cam is not opened")
    def viewfile(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择目录", "")

        # 如果用户选择了目录，将其路径显示在文本框中
        if directory:
            self.ui.lineEdit_3.setText(directory)
    def viewfile2(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择目录", "")
        if directory:
            self.ui.lineEdit_5.setText(directory)
    def open_file_dialog(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.ui.lineEdit_4.setText(file_path)
    def open_file_dialog2(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.ui.lineEdit_7.setText(file_path)
    def open_file_dialog3(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.ui.lineEdit_6.setText(file_path)
    def set_ex(self):
        text=self.ui.lineEdit.text()
        try:
            text=int(text)
            self.cam.set_ex(text)
            self.update_text("set ex sucess")
        except:
            self.update_text("set ex error")
    def set_ds(self):
        text=self.ui.comboBox.currentText()
        self.cam.set_ds(text)
        self.update_text("set ds sucess")
    def update_port(self):
         self.ui.comboBox_2.clear()
         ports = serial.tools.list_ports.comports()
         for port in ports:
            self.ui.comboBox_2.addItem(port.device)
    def open_serial(self):
        if self.ui.pushButton_4.text()=="open the com":
            if self.ui.comboBox_2.currentText()=='':
                if self.mot.open_serial()==1:
                    self.update_text("open serial sucess")
                    self.mot_flag=True
                    self.ui.pushButton_4.setText("close the com")
                else:
                    self.update_text("open serial error")
            else:
                name=self.ui.comboBox_2.currentText()
                if self.mot.open_serial_byname(name)==1:
                    self.update_text("open serial sucess")
                    self.mot_flag=True
                    self.ui.pushButton_4.setText("close the com")
                else:
                    self.update_text("open serial error")
            
        else:
            if self.ui.pushButton_4.text()=="close the com":
                if self.mot.close_serial()==1:
                    self.update_text("close serial sucess")
                    self.mot_flag=False
                    self.ui.pushButton_4.setText("open the com")
                else:
                    self.update_text("close serial error")
    def judge_dir(self):
        if self.ui.checkBox.isChecked():
            if self.mot_dir==1:
                self.mot.set_dir(0)
                self.mot_dir=0
                time.sleep(0.5)
                self.update_text("set dir 0")
        else:
            if self.mot_dir==0:
                self.mot.set_dir(1)
                self.mot_dir=1
                time.sleep(0.5)
                self.update_text("set dir 1")
    def auto(self):
        self.t.start()
    def constr(self):
        self.construct_thread.start()
    def outmulti(self):
        self.out_thread.start()
    def send_command(self):
        if self.mot_flag==True:
            self.judge_dir()
            degree=self.ui.lineEdit_2.text()
            try:
                command=self.caculate_rot(int(degree))
                self.mot.send_data(command)
                self.update_text(command)
                self.update_text("send command sucess")
            except:
                self.update_text("send command error")
        else:
            self.update_text("serial is not opened")
    def caculate_rot(self,degree):
        num=int(12800/360*degree)
        pwm_num=int(degree/1.8*64)
        command=f'start_pwm(200,72,{pwm_num})'
        return command
    #显示提示信息
    def update_text(self,str):
        self.ui.textBrowser.append(str)
