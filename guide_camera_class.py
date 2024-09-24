import cv2
import numpy as np
class camera:
    def __init__(self):
        self.cam=cv2.VideoCapture("/dev/video0")
        print('Opening first camera...')
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
        #self.img = xiapi.Image()
        self.data=None

    def set_ex(self, ex):
        pass

    def set_ds(self, ds):
        pass
    def get_imgdataformat(self):
        pass
    def start(self):
        pass
    def get_current_image(self):
        ret, frame = self.cam.read()

        self.data = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.data
    
    def stop_acq(self):
        pass
    def close(self):
        self.cam.release()
if __name__=="__main__":
    cam=camera()