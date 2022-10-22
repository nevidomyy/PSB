import os, fileinput, datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QSettings
import csv


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        
        # Config path and filename
        self.BASE_DIR = os.path.dirname(__file__)
        self.DB = os.path.join(self.BASE_DIR, "Database", "db.csv")
        self.CONFIG_FILE_NAME = os.path.join(self.BASE_DIR, "config.ini")
        self.REESTR_ENCODING = "cp1251"
        self.DB_ENCODING = "cp1251"

        # Create main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(880, 458)
        MainWindow.setFixedSize(880, 458)
        MainWindow.setWindowIcon(QtGui.QIcon(os.path.join(self.BASE_DIR, "icon.ico")))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
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
        self.summ_label.setGeometry(QtCore.QRect(600, 386 ,100, 30))
        
        # Create summ line
        self.line_summ = QtWidgets.QLineEdit(self.centralwidget)
        self.line_summ.setGeometry(QtCore.QRect(700, 386, 150, 30))
        self.line_summ.setObjectName("line_status")
        self.line_summ.setReadOnly(True)

        #Create merge button
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
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Инициализация ПО")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
       
        #Execute connect functions!
        self.add_functions()
        
        # Load setting
        self.load_settings()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Проверка реестров ПСБ"))
        self.btn_open.setText(_translate("MainWindow", "Выбор папки"))
        self.btn_reread.setText(_translate("MainWindow", "Перечитать"))
        self.btn_merge.setText(_translate("MainWindow", "Объединить реестры"))


    #All connect functions
    def add_functions(self):
        self.btn_open.clicked.connect(self.check_selected_filedir)
        self.btn_reread.clicked.connect(self.check_files)
        self.btn_merge.clicked.connect(self.merge)


    # Main Functions
    def check_selected_filedir(self) -> None:
        self.path = QtWidgets.QFileDialog.getExistingDirectory(None, "Выберите папку с реестрами ПСБ", "", 
                                                               QtWidgets.QFileDialog.ShowDirsOnly)
        if self.path:
            self.line_path.setText(self.path)
            self.save_settings()
            self.check_files()

    def check_files(self) -> None:
        self.save_id()
        self.path = self.line_path.text()
        if self.path:
            try:
                database = self.read_db_csv()
                files = self.get_files(self.path)
                self.fill_table(files, database)
            except Exception as e:
                self.statusbar.showMessage("Ошибка чтения реестров: %s" % str(e))
        else:
            self.show_error("Папка для проверки реестров ПСБ не указана! Хотите указать сейчас?")

    def get_files(self, path: str) -> tuple:
        files = tuple(filter(lambda name: name.endswith(".txt") and name.startswith(self.line_id.text()), os.listdir(path)))
        if len(files) == 0:
            self.show_error("В указанной папке не найдены реестры ПСБ для текущего кода организации. Хотите выбрать другую папку?")
        return files

    def fill_table(self, files: list, database: list) -> None:
        all_errors = []
        all_summ = 0
        if files:
            self.tableWidget.setRowCount(len(files))
            # Create table rows
            for index, filename in enumerate(files):
                r_results = self.match(filename, database)
                if len(r_results['r_error_list']) != 0:
                    for error in r_results['r_error_list']:
                        all_errors.append(error)
                all_summ += r_results.get('r_summ')
                r_name = QtWidgets.QTableWidgetItem(filename)
                r_errors = QtWidgets.QTableWidgetItem(str(r_results.get('r_errors')))
                r_len = QtWidgets.QTableWidgetItem(str(r_results.get('r_len')))
                r_residents = QtWidgets.QTableWidgetItem(str(r_results.get('r_resident')))
                r_non_residents = QtWidgets.QTableWidgetItem(str(r_results.get('r_non_resident')))
                r_summ =  QtWidgets.QTableWidgetItem(str(format(r_results.get('r_summ'), ',').replace(',', ' ')))
                
                self.tableWidget.setItem(index, 0, r_name)
                self.tableWidget.setItem(index, 1, r_errors)
                self.tableWidget.setItem(index, 2, r_len)
                self.tableWidget.setItem(index, 3, r_residents)
                self.tableWidget.setItem(index, 4, r_non_residents)
                self.tableWidget.setItem(index, 5, r_summ)
                
                self.tableWidget.resizeRowsToContents()
                # Disable editing in table
                self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.line_summ.setText(format(all_summ, ',.2f').replace(',', ' '))
            if len(all_errors) != 0:
                self.show_error_table(all_errors)

    def read_db_csv(self) -> list:
        self.statusbar.showMessage("Чтение базы данных ...")
        data = []
        try:
            with open (self.DB, "r", newline = "", encoding=self.DB_ENCODING) as csvfile:
                fieldnames = ['account', 'last_name', 'first_name', 'middle_name']
                reader = csv.DictReader(csvfile, delimiter=";", fieldnames=fieldnames)
                for row in reader:
                    data.append(row)
                if len(data) != 0:
                    self.statusbar.showMessage("База данных загружена. Записей в БД: %s" % str(len(data)))
                else:
                    self.statusbar.showMessage("Ошибка загрузки! База данных пуста!")
        except FileNotFoundError as e:
            self.statusbar.showMessage("Ошибка чтения базы данных: Нет такого файла или каталога - %s" % self.DB)
        except Exception as e:
            self.statusbar.showMessage("Ошибка чтения базы данных: %s" % str(e))
        return data

    def match(self, filename: str, database: list ) -> dict:
        r_file = os.path.join(self.line_path.text(), filename)
        r_len = 0
        r_summ = 0
        r_non_resident = 0
        r_resident = 0
        r_errors = 0
        r_error_list = []
        try:
            with open(r_file, 'r', encoding=self.REESTR_ENCODING) as f:
                for line in f:
                    r_len += 1
                    data = line.split('^')
                    account = data[0]
                    first_name = data[4]
                    last_name = data[3]
                    middle_name = data[5]
                    line_error_text = ''
                    resident = next((elem for elem in database if elem.get('account') == account), None)
                    if resident:
                        r_resident += 1
                        if resident["last_name"].upper() != last_name.upper():
                            line_error_text += "Ошибка в Фамилии; "
                            r_errors += 1
                        if resident["first_name"].upper() != first_name.upper():
                            line_error_text += "Ошибка в Имени; "
                            r_errors += 1
                        if resident["middle_name"].upper() != middle_name.upper():
                            line_error_text += "Ошибка в Отчестве; "
                            r_errors += 1
                    if not resident:
                        line_error_text += ("Отсутствует л/с в базе данных счетов!")
                        r_non_resident += 1
                        r_errors += 1
                    if len(line_error_text) != 0:
                        r_error_list.append({
                            "r_name": filename,
                            "account": account,
                            "first_name": first_name,
                            "last_name": last_name,
                            "middle_name": middle_name,
                            "error_text": line_error_text}
                            )
                    r_summ += float(data[2])
        
        except Exception as e:
            self.statusbar.showMessage("Ошибка чтения реестров: %s" % str(e))
        
        results = {
                "r_name": filename, 
                "r_len": r_len,
                "r_errors": r_errors,
                "r_summ": float('{:.2f}'.format(r_summ)),
                "r_resident": r_resident,
                "r_non_resident": r_non_resident,
                "r_error_list": r_error_list
                }

        return results

    def show_error(self, text: str):
        error = QtWidgets.QMessageBox()
        error.setWindowTitle("Ошибка проверки реестров")
        error.setText(text)
        error.setIcon(QtWidgets.QMessageBox.Warning)
        error.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.Cancel)
    
        error.exec()
        
        # If clicked ok - started check_selected_dir
        button = error.clickedButton()
        sb = error.standardButton(button)
        if sb == QtWidgets.QMessageBox.Yes:
            self.check_selected_filedir()
        if sb == QtWidgets.QMessageBox.No:
            pass

    def show_merge_error(self, text: str):
        error = QtWidgets.QMessageBox()
        error.setWindowTitle("Предупреждение!")
        error.setText(text)
        error.setIcon(QtWidgets.QMessageBox.Warning)
        error.exec()

    def show_error_table(self, all_errors: dict):
        dialog = QtWidgets.QDialog()
        dialog.setWindowIcon(QtGui.QIcon(os.path.join(self.BASE_DIR, "icon.ico")))
        dialog.setWindowTitle("Список ошибок")
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
         # Create table   
        dialog.tableWidget = QtWidgets.QTableWidget(dialog)
        dialog.tableWidget.setColumnCount(6)
        dialog.tableWidget.setRowCount(len(all_errors))
        dialog.tableWidget.setGeometry(QtCore.QRect(0, 0, 1000, 350))
        dialog.setFixedSize(1000, 350)
        dialog.tableWidget.setObjectName("tableView")
        dialog.tableWidget.setHorizontalHeaderLabels(["Файл реестра: ", "Номер счета: ", "Фамилия: ",
                                                    "Имя: ", "Отчество: ", "Текст ошибки: "])
        
        # Initial Resize model for table
        # Resize header in full widht!
        dialog.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # Resize table column in content widht
        dialog.tableWidget.resizeColumnsToContents()
        
        for index, error in enumerate(all_errors):
            r_name = QtWidgets.QTableWidgetItem(error.get('r_name'))
            r_account = QtWidgets.QTableWidgetItem(error.get('account'))
            r_first_name = QtWidgets.QTableWidgetItem(error.get('first_name'))
            r_last_name = QtWidgets.QTableWidgetItem(error.get('last_name'))
            r_middle_name = QtWidgets.QTableWidgetItem(error.get('middle_name'))
            r_error_text =  QtWidgets.QTableWidgetItem(error.get('error_text'))
                
            dialog.tableWidget.setItem(index, 0, r_name)
            dialog.tableWidget.setItem(index, 1, r_account)
            dialog.tableWidget.setItem(index, 2, r_last_name)
            dialog.tableWidget.setItem(index, 3, r_first_name)
            dialog.tableWidget.setItem(index, 4, r_middle_name)
            dialog.tableWidget.setItem(index, 5, r_error_text)
        
        dialog.tableWidget.resizeRowsToContents()
        # Disable editing in table
        dialog.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        dialog.exec()
    
    def merge(self):
        self.save_id()
        self.path = self.line_path.text()
        date_ = self.get_date()
        if self.path:
            filenames = self.get_files(self.path)
            self.filelist = [os.path.join(self.path, filename) for filename in filenames]
            if self.line_number.text():
                number_ = "{:03d}".format(int(self.line_number.text()))
                self.merge_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Выберите папку для сохранения реестра", "", 
                                                                        QtWidgets.QFileDialog.ShowDirsOnly)
                if self.merge_path:
                    self.merged_file = os.path.join(self.merge_path, self.line_id.text() + "2" + date_.get('month') + date_.get('day') + number_+ '.txt')
                    self.save_merged(self.filelist, self.merged_file)
            else:
                self.show_merge_error("Введите номер для реестра и попробуйте снова!")
        else:
            self.show_error("Укажите папку, содержащую реестры для объединения и попробуйте снова! Выбрать папку сейчас?")


    def save_merged(self, filelist: list, merged_file: str):
        if merged_file in filelist:
            self.show_merge_error("Невозможно сохранить файл в указанный каталог. Укажите другой номер для реестра, либо выберите другой каталог для сохранения!")
        else:
            try:
                with fileinput.FileInput(files=filelist, openhook=fileinput.hook_encoded(self.REESTR_ENCODING)) as fr, open(merged_file, 'w', encoding=self.REESTR_ENCODING) as fw:
                    for line in fr:
                        fw.write(line)
            except Exception as e:
                self.statusbar.showMessage('Ошибка: %s' % e)
            else:
                self.statusbar.showMessage('Реестр сохранен в: %s' % merged_file) 
    
    def get_date(self) -> dict:
        date = datetime.datetime.now()
        month = date.strftime("%m")
        day = date.strftime("%d")
        return {"month": month, "day": day}

    def save_settings(self):
        settings = QSettings(self.CONFIG_FILE_NAME, QSettings.IniFormat)
        settings.setValue("path", self.line_path.text())
        settings.setValue("id", self.line_id.text())
    
    def save_id(self):
        settings = QSettings(self.CONFIG_FILE_NAME, QSettings.IniFormat)
        settings.setValue("id", self.line_id.text())

    def load_settings(self):
        settings = QSettings(self.CONFIG_FILE_NAME, QSettings.IniFormat)
        self.line_path.setText(settings.value("path"))
        self.line_id.setText(settings.value("id"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.check_files()
    sys.exit(app.exec())
