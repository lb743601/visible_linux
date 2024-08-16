import serial
class mot:
    def __init__(self):
        self.s=serial.Serial()
        self.s.port="/dev/ttyUSB0"
        self.s.baudrate = 115200
        self.s.bytesize = 8
        self.s.stopbits = 1
        self.s.parity = 'N'
    def open_serial_byname(self,com):
        self.s.port=com
        try:
            self.s.open()
            return 1
        except:
            return -1
    def open_serial(self):
        try:
            self.s.open()
            return 1
        except:
            return -1
    def send_data(self,command):
        if self.s.is_open:
            command=command+"\r\n"
            self.s.write(command.encode('utf-8'))
            return 1
        else:
            return -1
    def set_dir(self,dir):
        if dir==0:
            command="set_dir(0)\r\n"
        else:
            command="set_dir(1)\r\n"
        if self.send_data(command)==1:
            return 1
        else:
            return -1
    def close_serial(self):
        try:
            self.s.close()
            return 1
        except:
            return -1
