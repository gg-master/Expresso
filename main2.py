import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWidgets import QWidget, QTableWidgetItem


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


class MyDialog(QDialog):
    def __init__(self, changed=False, info=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.arr = []
        self.buttonBox.accepted.connect(self.accept1)
        self.buttonBox.rejected.connect(self.reject1)
        if changed:
            self.arr = info
            self.lineEdit.setText(str(self.arr[0]))
            self.lineEdit_2.setText(str(self.arr[1]))
            self.lineEdit_3.setText(str(self.arr[2]))
            self.lineEdit_4.setText(str(self.arr[3]))
            self.lineEdit_5.setText(str(self.arr[4]))
            self.lineEdit_6.setText(str(self.arr[5]))

    def reject1(self):
        self.close()

    def accept1(self):
        self.arr = [self.lineEdit.text(), self.lineEdit_2.text(),
                    self.lineEdit_3.text(), self.lineEdit_4.text(),
                    self.lineEdit_5.text(), self.lineEdit_6.text()]
        self.close()

    def get_items(self):
        return self.arr


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_2.ui", self)
        self.con = sqlite3.connect("expresso_db.db")
        self.setWindowTitle("Коршунов-экспрессо")

        self.pushButton.clicked.connect(self.update_tab1)
        self.pushButton_2.clicked.connect(self.add_it)
        self.pushButton_3.clicked.connect(self.change_it)

        self.tableWidget.itemChanged.connect(self.item_changed_1)
        self.modified = {}
        self.titles = None

        self.update_tab1()

    def add_it(self):
        cur = self.con.cursor()

        mdf = MyDialog()
        mdf.show()
        mdf.exec_()

        data = mdf.get_items()
        if data and len(data) == 6:
            max_id = max(list(map(lambda x: x[0],
                                  cur.execute(
                                      """Select id from menu""").fetchall())))

            cur = self.con.cursor()
            # Получили результат запроса, который ввели в текстовое поле
            cur.execute("""INSERT INTO menu(id, 
            name, level_obj, type, taste, price, volume) 
            VALUES(?, ?, ?, ?, ?, ?, ?)""", (
                max_id + 1, data[0],
                data[1], data[2], data[3], data[4], data[5]))
            self.con.commit()
            self.update_tab1()

    def change_it(self):
        cur = self.con.cursor()

        rows = list(
            set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        # Спрашиваем у пользователя подтверждение на удаление элементов
        if not ids:
            self.statusBar.setText('Записть не выделена')
            return
        elif len(ids) > 1:
            self.statusBar.setText('Выбрано более 1 записи')
            return
        item_inf = cur.execute(
            "SELECT * FROM menu WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids).fetchall()[0]

        mdf = MyDialog(True, [item_inf[1], item_inf[2], item_inf[3],
                              item_inf[4], item_inf[5], item_inf[6]])
        mdf.show()
        mdf.exec_()

        data = mdf.get_items()

        if data:
            id = item_inf[0]
            cur.execute('''UPDATE menu 
            SET  name = ?, level_obj = ?, type = ?, taste = ?, 
            price = ?, volume = ?
            where id LIKE ?''',
                        (data[0], data[1],
                         data[2], data[3],
                         data[4], data[5],
                         id))
            self.con.commit()
            self.update_tab1()

    def update_tab1(self):
        cur = self.con.cursor()
        result = cur.execute('select * from menu')
        self.titles = [description[0] for description in result.description]
        result = result.fetchall()
        self.tableWidget.setRowCount(len(result))

        header = ['ID', 'название сорта',
                  'степень обжарки', 'молотый/в зернах',
                  'описание вкуса', 'цена', 'объем упаковки']

        self.tableWidget.setColumnCount(len(header))
        self.tableWidget.setHorizontalHeaderLabels(header)

        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed_1(self, item):
        # Если значение в ячейке было изменено,
        # то в словарь записывается пара: название поля, новое значение
        self.modified[self.titles[item.column()]] = item.text()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
