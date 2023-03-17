import os
import csv
import datetime
import fileinput
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QSettings
    
    
# Main Functions
def check_selected_filedir(ui) -> None:
    print(ui.BASE_DIR)
    root_path = ui.line_path.text()
    ui.path = QtWidgets.QFileDialog.getExistingDirectory(None, "Выберите папку с реестрами ПСБ", root_path, 
                                                            QtWidgets.QFileDialog.ShowDirsOnly)
    if ui.path:
        ui.line_path.setText(ui.path)
        save_settings(ui)
        check_files(ui)


def check_files(ui: QtWidgets) -> None:
    save_id(ui)
    ui.path = ui.line_path.text()
    if ui.path:
        try:
            database = read_db_csv(ui)
            files = get_files(ui, ui.path)
            fill_table(ui, files, database)
        except Exception as e:
            ui.statusbar.showMessage("Ошибка чтения реестров: %s" % str(e))
    else:
        show_error(ui, "Папка для проверки реестров ПСБ не указана! Хотите указать сейчас?")


def get_files(ui: QtWidgets, path: str) -> tuple:
    files = tuple(
        filter(lambda name: name.endswith(".txt") and name.startswith(ui.line_id.text()), os.listdir(path)))
    if len(files) == 0:
        show_error(ui, "В указанной папке не найдены реестры "
                       "ПСБ для текущего кода организации. Хотите выбрать другую папку?")
    return files


def fill_table(ui: QtWidgets, files: tuple, database: list) -> None:
    all_errors = []
    all_summ = 0
    if files:
        ui.tableWidget.setRowCount(len(files))
        # Create table rows
        for index, filename in enumerate(files):
            r_results = match(ui, filename, database)
            if len(r_results['r_error_list']) != 0:
                for error in r_results['r_error_list']:
                    all_errors.append(error)
            all_summ += r_results.get('r_summ')
            r_name = QtWidgets.QTableWidgetItem(filename)
            r_errors = QtWidgets.QTableWidgetItem(str(r_results.get('r_errors')))
            r_len = QtWidgets.QTableWidgetItem(str(r_results.get('r_len')))
            r_residents = QtWidgets.QTableWidgetItem(str(r_results.get('r_resident')))
            r_non_residents = QtWidgets.QTableWidgetItem(str(r_results.get('r_non_resident')))
            r_summ = QtWidgets.QTableWidgetItem(str(format(r_results.get('r_summ'), ',').replace(',', ' ')))

            ui.tableWidget.setItem(index, 0, r_name)
            ui.tableWidget.setItem(index, 1, r_errors)
            ui.tableWidget.setItem(index, 2, r_len)
            ui.tableWidget.setItem(index, 3, r_residents)
            ui.tableWidget.setItem(index, 4, r_non_residents)
            ui.tableWidget.setItem(index, 5, r_summ)

            ui.tableWidget.resizeRowsToContents()
            # Disable editing in table
            ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        ui.line_summ.setText(format(all_summ, ',.2f').replace(',', ' '))
        if len(all_errors) != 0:
            show_error_table(ui, all_errors)


def read_db_csv(ui: QtWidgets) -> list:
    ui.statusbar.showMessage("Чтение базы данных ...")
    data = []
    try:
        with open(ui.DB, "r", newline="", encoding=ui.DB_ENCODING) as csvfile:
            fieldnames = ['account', 'last_name', 'first_name', 'middle_name']
            reader = csv.DictReader(csvfile, delimiter=";", fieldnames=fieldnames)
            for row in reader:
                data.append(row)
            if len(data) != 0:
                ui.statusbar.showMessage("База данных загружена. Записей в БД: %s" % str(len(data)))
            else:
                ui.statusbar.showMessage("Ошибка загрузки! База данных пуста!")
    except FileNotFoundError:
        ui.statusbar.showMessage("Ошибка чтения базы данных: Нет такого файла или каталога - %s" % ui.DB)
    except Exception as e:
        ui.statusbar.showMessage("Ошибка чтения базы данных: %s" % str(e))
    return data


def match(ui: QtWidgets, filename: str, database: list) -> dict:
    r_file = os.path.join(ui.line_path.text(), filename)
    r_len = 0
    r_summ = 0
    r_non_resident = 0
    r_resident = 0
    r_errors = 0
    r_error_list = []
    try:
        with open(r_file, 'r', encoding=ui.REESTR_ENCODING) as f:
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
                    line_error_text += "Отсутствует л/с в базе данных счетов!"
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
        ui.statusbar.showMessage("Ошибка чтения реестров: %s" % str(e))

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


def show_error(ui: QtWidgets, text: str):
    error = QtWidgets.QMessageBox()
    error.setWindowTitle("Ошибка проверки реестров")
    error.setText(text)
    error.setIcon(QtWidgets.QMessageBox.Warning)
    error.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

    error.exec()

    # If clicked ok - started check_selected_dir
    button = error.clickedButton()
    sb = error.standardButton(button)
    if sb == QtWidgets.QMessageBox.Yes:
        check_selected_filedir(ui)
    if sb == QtWidgets.QMessageBox.No:
        pass


def show_merge_error(text: str):
    error = QtWidgets.QMessageBox()
    error.setWindowTitle("Предупреждение!")
    error.setText(text)
    error.setIcon(QtWidgets.QMessageBox.Warning)
    error.exec()


def show_error_table(ui: QtWidgets, all_errors: list):
    dialog = QtWidgets.QDialog()
    dialog.setWindowIcon(QtGui.QIcon(os.path.join(ui.BASE_DIR, "icon.ico")))
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
    # Resize header in full width!
    dialog.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    # Resize table column in content width
    dialog.tableWidget.resizeColumnsToContents()

    for index, error in enumerate(all_errors):
        r_name = QtWidgets.QTableWidgetItem(error.get('r_name'))
        r_account = QtWidgets.QTableWidgetItem(error.get('account'))
        r_first_name = QtWidgets.QTableWidgetItem(error.get('first_name'))
        r_last_name = QtWidgets.QTableWidgetItem(error.get('last_name'))
        r_middle_name = QtWidgets.QTableWidgetItem(error.get('middle_name'))
        r_error_text = QtWidgets.QTableWidgetItem(error.get('error_text'))

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


def merge(ui: QtWidgets):
    save_id(ui)
    ui.path = ui.line_path.text()
    date_ = get_date()
    if ui.path:
        filenames = get_files(ui, ui.path)
        filelist = [os.path.join(ui.path, filename) for filename in filenames]
        if ui.line_number.text():
            number_ = "{:03d}".format(int(ui.line_number.text()))
            ui.merge_path = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                                       "Выберите папку для сохранения реестра",
                                                                       "",
                                                                       QtWidgets.QFileDialog.ShowDirsOnly)
            if ui.merge_path:
                ui.merged_file = os.path.join(ui.merge_path,
                                              ui.line_id.text() + "2" + date_.get('month') + date_.get('day')
                                              + number_ + '.txt')
                save_merged(ui, filelist, ui.merged_file)
        else:
            show_merge_error("Введите номер для реестра и попробуйте снова!")
    else:
        show_error(ui,
                   "Укажите папку, содержащую реестры для объединения и попробуйте снова! Выбрать папку сейчас?")


def save_merged(ui: QtWidgets, filelist: list, merged_file: str):
    if merged_file in filelist:
        show_merge_error(
            "Невозможно сохранить файл в указанный каталог. Укажите другой номер для реестра, либо выберите другой "
            "каталог для сохранения!")
    else:
        try:
            with fileinput.FileInput(files=filelist, openhook=fileinput.hook_encoded(ui.REESTR_ENCODING)) as fr, open(
                    merged_file, 'w', encoding=ui.REESTR_ENCODING) as fw:
                for line in fr:
                    fw.write(line)
        except Exception as e:
            ui.statusbar.showMessage('Ошибка: %s' % e)
        else:
            ui.statusbar.showMessage('Реестр сохранен в: %s' % merged_file)


def get_date() -> dict:
    date = datetime.datetime.now()
    month = date.strftime("%m")
    day = date.strftime("%d")
    return {"month": month, "day": day}


def save_settings(ui: QtWidgets):
    settings = QSettings(ui.CONFIG_FILE_NAME, QSettings.IniFormat)
    settings.setValue("path", ui.line_path.text())
    settings.setValue("id", ui.line_id.text())


def save_id(ui: QtWidgets):
    settings = QSettings(ui.CONFIG_FILE_NAME, QSettings.IniFormat)
    settings.setValue("id", ui.line_id.text())


def load_settings(ui: QtWidgets):
    settings = QSettings(ui.CONFIG_FILE_NAME, QSettings.IniFormat)
    ui.line_path.setText(settings.value("path"))
    ui.line_id.setText(settings.value("id"))
