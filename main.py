import sys
from PyQt5 import QtWidgets
from forms import UiMainWindow
from functions import check_files


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    check_files(ui)
    sys.exit(app.exec())

