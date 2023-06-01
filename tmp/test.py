# import sys
# from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QHBoxLayout
#
#
# class Less(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle('hi')
#         self.setMinimumSize(200,300)
#         self.resize(1080,720)
#         t1 =QHBoxLayout()
#         t1.addWidget(QLabel('hgfhjg'))
#         self.setLayout(t1)
#
#
# app = QApplication(sys.argv)
# w= Less()
# w.show()
# app.exec()

a8=(1,2,3)

def a (ty):
    print(2,*ty)
a(a8)
