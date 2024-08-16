import time
import serial
import cv2
import threading
import tkinter as tk
from tkinter import simpledialog
from ximea import xiapi
from PIL import Image
import datetime
import os
def initialize_serial(port, baudrate=115200):
    ser = serial.Serial(port, baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    return ser

def send_data(ser, data):
    # 将数据编码为UTF-8并添加换行符
    data += "\r\n"
    ser.write(data.encode('utf-8'))
class camera:
    def __init__(self):
        self.cam = xiapi.Camera()
        print('Opening first camera...')
        self.cam.open_device()
        self.img = xiapi.Image()
        self.data=None

    def set_ex(self, ex):
        self.cam.set_exposure(ex)

    def set_ds(self, ds):
        self.cam.set_downsampling(ds)
    def start(self):
        self.cam.start_acquisition()
    def outp(self):
        t0 = time.time()
        while True:

            self.cam.get_image(self.img)

            # create numpy array with data from camera. Dimensions of the array are
            # determined by imgdataformat
            self.data = self.img.get_image_data_numpy()
            

            #plt.hist(self.data,256)
            #plt.show()
            #cv2.waitKey(0)
            # show acquired image with time since the beginning of acquisition
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # text = '{:5.2f}'.format(time.time() - t0)
            # cv2.putText(data, text, (900, 150), font, 4, (255, 255, 255), 2)
            cv2.namedWindow("show",0)
            cv2.imshow('show', self.data)
            cv2.waitKey(1)
            if cv2.getWindowProperty('show', cv2.WND_PROP_VISIBLE) < 1:
                break
    def save(self):
        if self.data is not None:
            # 确保保存目录存在
            save_dir = os.path.abspath("./data/")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # 生成时间戳文件名
            tif_time = datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
            name = os.path.join(save_dir, tif_time + ".tif")

            # 保存图像
            image = Image.fromarray(self.data)
            image.save(name)
            print(f"Image saved as {name}")
        else:
            print("No image data to save.")
    def close(self):
        self.cam.stop_acquisition()
        self.cam.close_device()
def on_set_exposure():
    ex = simpledialog.askinteger("Set Exposure", "Enter exposure value:")
    if ex is not None:
        cam.set_ex(ex)
def on_auto_capture():
    cam.save()
    time.sleep(0.1)
    send_data(ser, 'start_pwm(200,72,4267)')
    time.sleep(2)
    cam.save()
    time.sleep(0.1)
    send_data(ser, 'start_pwm(200,72,4267)')
    time.sleep(2)
    cam.save()
    time.sleep(0.1)
    send_data(ser, 'start_pwm(200,72,4267)')
def on_save_image():
    cam.save()
def on_rotate():
    angle = simpledialog.askinteger("Rotate", "Enter rotation angle:")
    if angle is not None:
        pwm_num=int(angle/1.8*64)
        send_data(ser, f'start_pwm(200,72,{pwm_num})')
# 示例用法
if __name__ == "__main__":

    # 初始化串口
    ser = initialize_serial('/dev/ttyUSB0')  # 修改为实际的串口名称
    #
    # # 发送数据
    # send_data(ser, 'start_pwm(200,72,4267)')
    # time.sleep(2)
    # send_data(ser, 'stop_pwm()')
    # # 关闭串口
    # ser.close()
    cam=camera()
    cam.set_ex(20000)
    cam.set_ds("XI_DWN_1x1")
    cam.start()
    t=threading.Thread(target=cam.outp)
    t.start()
    root = tk.Tk()
    root.title("Camera Control")

    btn_set_exposure = tk.Button(root, text="Set Exposure", command=on_set_exposure)
    btn_set_exposure.pack(pady=10)

    btn_auto_capture = tk.Button(root, text="Auto Capture", command=on_auto_capture)
    btn_auto_capture.pack(pady=10)

    btn_save_image = tk.Button(root, text="Save Image", command=on_save_image)
    btn_save_image.pack(pady=10)

    btn_rotate_image = tk.Button(root, text="Rotate", command=on_rotate)
    btn_rotate_image.pack(pady=10)

    root.mainloop()
    send_data(ser, 'stop_pwm()')
    ser.close()
    print('Stopping acquisition...')
    cam.cam.stop_acquisition()

    cam.cam.close_device()
