import os
from PyQt5 import QtCore, QtGui, QtWidgets
from functions import check_files, load_settings, check_selected_filedir, merge


class UiMainWindow(object):
    def __init__(self):
        # Config path and filename
        self.BASE_DIR = os.path.dirname(__file__)
        self.DB = os.path.join(self.BASE_DIR, "Database", "db.csv")
        self.CONFIG_FILE_NAME = os.path.join(self.BASE_DIR, "config.ini")
        self.REESTR_ENCODING = "cp1251"
        self.DB_ENCODING = "cp1251"

    def setup_ui(self, main_window):
        # Create main window
        main_window.setObjectName("main_window")
        main_window.resize(880, 458)
        main_window.setFixedSize(880, 458)
        main_window.setWindowIcon(QtGui.QIcon(os.path.join(self.BASE_DIR, "icon.ico")))
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")

        # Create path line
        self.line_path = QtWidgets.QLineEdit(self.centralwidget)
        self.line_path.setGeometry(QtCore.QRect(10, 2, 591, 31))
        self.line_path.setObjectName("line_path")
        self.line_path.setReadOnly(True)

        # Create id line
        self.line_id = QtWidgets.QLineEdit(self.centralwidget)
        self.line_id.setGeometry(QtCore.QRect(10, 40, 591, 31))
        self.line_id.setObjectName("line_id")
        self.line_id.setPlaceholderText('Введите код организации')

        # Create opendialog button
        self.btn_open = QtWidgets.QPushButton(self.centralwidget)
        self.btn_open.setGeometry(QtCore.QRect(610, 2, 111, 31))
        self.btn_open.setObjectName("btn_open")

        # Create reread button
        self.btn_reread = QtWidgets.QPushButton(self.centralwidget)
        self.btn_reread.setGeometry(QtCore.QRect(610, 39, 111, 31))
        self.btn_reread.setObjectName("btn_reread")

        # Create summ label
        self.summ_label = QtWidgets.QLabel(self.centralwidget)
        self.summ_label.setText("Итого сумма: ")
        self.summ_label.setGeometry(QtCore.QRect(600, 386, 100, 30))

        # Create summ line
        self.line_summ = QtWidgets.QLineEdit(self.centralwidget)
        self.line_summ.setGeometry(QtCore.QRect(700, 386, 150, 30))
        self.line_summ.setObjectName("line_status")
        self.line_summ.setReadOnly(True)

        # Create merge button
        self.btn_merge = QtWidgets.QPushButton(self.centralwidget)
        self.btn_merge.setGeometry(QtCore.QRect(1, 386, 180, 30))
        self.btn_merge.setObjectName("btn_merge")

        # Create LineNumber
        self.line_number = QtWidgets.QLineEdit(self.centralwidget)
        self.line_number.setGeometry(QtCore.QRect(185, 386, 120, 30))
        self.line_number.setObjectName("line_number")
        self.validator = QtGui.QIntValidator(0, 100, self.centralwidget)
        self.line_number.setValidator(self.validator)
        self.line_number.setPlaceholderText('Номер реестра')

        # Create table
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setGeometry(QtCore.QRect(0, 90, 880, 291))
        self.tableWidget.setObjectName("tableView")
        self.tableWidget.setHorizontalHeaderLabels(["Файл реестра: ", "Ошибок: ", "Всего строк: ",
                                                    "Резидентов: ", "Нерезидентов: ", "Сумма по реестру: "])

        # Initial Resize model for table
        # Resize header in full widht!
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # Resize table column in content widht
        self.tableWidget.resizeColumnsToContents()

        # Create statistic lablels
        ############################

        # Create other elements for main window
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Инициализация ПО")

        self.translate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

        # Execute connect functions!
        self.add_functions()

        # Load setting
        load_settings(self)

    def translate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "Проверка реестров ПСБ"))
        self.btn_open.setText(_translate("MainWindow", "Выбор папки"))
        self.btn_reread.setText(_translate("MainWindow", "Перечитать"))
        self.btn_merge.setText(_translate("MainWindow", "Объединить реестры"))

    # All connect functions
    def add_functions(self):
        self.btn_open.clicked.connect(check_selected_filedir(self))
        self.btn_reread.clicked.connect(check_files(self))
        self.btn_merge.clicked.connect(merge(self))
