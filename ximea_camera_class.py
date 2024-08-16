from ximea import xiapi
import numpy as np
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
    def get_imgdataformat(self):
        return self.cam.get_imgdataformat()
    def start(self):
        
        self.cam.start_acquisition()
    def get_current_image(self):
        self.cam.get_image(self.img)
        self.data = self.img.get_image_data_numpy()
        return self.data
    
    def stop_acq(self):
        self.cam.stop_acquisition()
    def close(self):
        self.cam.close_device()
if __name__=="__main__":
    cam=camera()
    print(cam.get_imgdataformat())