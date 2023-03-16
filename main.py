import sys
from PyQt5 import QtWidgets
from forms import UiMainWindow
from functions import check_files


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainForm = UiMainWindow()
    MainForm.setup_ui(MainWindow)
    MainForm.show()
    check_files(MainForm)
    sys.exit(app.exec())

