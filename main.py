from ui_class import MyApp  # 假设生成的文件名是 example.py
from PyQt5 import QtWidgets
import sys

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()
