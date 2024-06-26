import json

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QSpacerItem, QTabWidget, QComboBox, QHeaderView
import pandas as pd

import mrp as mrp
import msp as msp

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Skateboard MRP")
        self.setWindowIcon(QIcon("images/icon.png"))
        self.resize(QSize(1280, 720))

        self.widget = QWidget()

        self.hlayout = QHBoxLayout()
        self.hlayout.setContentsMargins(40, 20, 40, 20)

        self.widget.setLayout(self.hlayout)
        self.setCentralWidget(self.widget)

        self.vleft_layout = QVBoxLayout()
        self.vright_layout = QVBoxLayout()

        self.vleft_layout.setContentsMargins(30, 10, 30, 10)
        self.vright_layout.setContentsMargins(30, 10, 30, 10)


        self.materials_label = QLabel("Materiały")
        self.orders_label = QLabel("Zamówienia")

        self.materials_table = self.init_materials_table()
        # Styling class declaration example
        self.materials_table.setProperty("class", "table")
        self.orders_table = self.init_orders_table()

        self.error_label = QLabel()

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vleft_layout.addWidget(self.materials_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vleft_layout.addWidget(self.materials_table)
        self.vleft_layout.addWidget(self.orders_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vleft_layout.addWidget(self.orders_table)
        self.vleft_layout.addWidget(self.error_label)
        self.vleft_layout.addItem(self.spacer)

        self.ghp_label = QLabel("Główny harmonogram producji")
        self.ghp_table = self.init_ghp_table()

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.South)

        self.wheel_tab = QWidget()
        self.wheel_tab.setObjectName("wheel")
        self.wood_tab = QWidget()
        self.wood_tab.setObjectName("wood")
        self.truck_tab = QWidget()
        self.truck_tab.setObjectName("truck")
        self.board_tab = QWidget()
        self.board_tab.setObjectName("board")

        self.tabs.addTab(self.wheel_tab, "Kółko")
        self.tabs.addTab(self.wood_tab, "Wood")
        self.tabs.addTab(self.truck_tab, "Truck")
        self.tabs.addTab(self.board_tab, "Deska")

        self.vright_layout.addWidget(self.ghp_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.vright_layout.addWidget(self.ghp_table)
        self.vright_layout.addWidget(self.tabs)

        self.hlayout.addLayout(self.vleft_layout)
        self.hlayout.addLayout(self.vright_layout)

        self.materials_table.cellChanged.connect(self.save_changed_materials_value)
        self.orders_table.cellChanged.connect(self.save_changed_order_value)

        self.init_tabs()

        self.init_calculations()

    def init_materials_table(self):
        with open("data/materials.json", 'r', encoding="utf-8") as f:
            materials = json.load(f)

        table = QTableWidget(5,5)
        table.setHorizontalHeaderLabels(["Czas realizacji", "Na stanie", "Wielkość partii", "Wymagana ilość", "Poziom BOM"])
        table.setVerticalHeaderLabels(["Deskorolka", "Deska", "Truck", "wood", "Kółko"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        row = 0
        for component_name, component_data in materials.items():
            col = 0
            for key, value in component_data.items():
                item = QTableWidgetItem(str(value))
                if key == 'level':
                    item.setFlags(Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)
                col += 1
            row += 1

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def init_orders_table(self):
        with open("data/orders.json", 'r', encoding="utf-8") as f:
            orders_dict = json.load(f)

        table = QTableWidget(1, 7)
        table.setHorizontalHeaderLabels(["1", "2", "3", "4", "5", "6", "7"])
        table.setVerticalHeaderLabels(["Liczba"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        column = 0
        for dictionary in orders_dict:
            item = QTableWidgetItem(str(dictionary["orders"]))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, column, item)
            column += 1

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def init_ghp_table(self):
        table = QTableWidget(3, 7)
        table.setHorizontalHeaderLabels(["1", "2", "3", "4", "5", "6", "7"])
        table.setVerticalHeaderLabels(["Przewidywany popyt", "Produkcja", "Dostępne"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        for col in range(0, 7):
            for row in range(0, 3):
                item = QTableWidgetItem("0")
                item.setFlags(Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def init_mrp_table(self, component):
        title_label = QLabel(component)
        table = QTableWidget(6, 6)
        table.setHorizontalHeaderLabels(["1", "2", "3", "4", "5", "6", "7"])
        table.setVerticalHeaderLabels(["Całkowite zapotrzebowanie", "Planowane przyjęcia", "Przewidywane na stanie", "Zapotrzebowanie netto", "Planowane zamówienia", "Planowane przyjęcie zamówień"])

        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        table.horizontalHeader().setDisabled(True)
        table.verticalHeader().setDisabled(True)

        for col in range(0, 6):
            for row in range(0, 6):
                item = QTableWidgetItem("0")
                item.setFlags(Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)

        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table, title_label

    def init_tabs(self):
        for i in range(0, 4):
            tab = self.tabs.widget(i)
            tab_name = self.tabs.tabText(i)

            mrp_table, mrp_title = self.init_mrp_table(tab_name)
            spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

            vlayout = QVBoxLayout()
            vlayout.addWidget(mrp_title, alignment=Qt.AlignmentFlag.AlignCenter)
            vlayout.addWidget(mrp_table)
            vlayout.addItem(spacer)
            tab.setLayout(vlayout)


 
    def save_changed_materials_value(self, row, column):
        value = self.materials_table.item(row, column).text()

        with open("data/materials.json", 'r', encoding="utf-8") as f:
            materials = json.load(f)

        if row == 0:
            materials.get("skateboard")[list(materials.get("skateboard").keys())[column]] = int(value)
        elif row == 1:
            materials.get("board")[list(materials.get("board").keys())[column]] = int(value)
        elif row == 2:
            materials.get("truck")[list(materials.get("truck").keys())[column]] = int(value)
        elif row == 3:
            materials.get("wood")[list(materials.get("wood").keys())[column]] = int(value)
        elif row == 4:
            materials.get("wheel")[list(materials.get("wheel").keys())[column]] = int(value)

        with open("data/materials.json", 'w', encoding="utf-8") as f:
            json.dump(materials, f, indent=2)

        self.error_label.setText("")
        self.init_calculations()

    def save_changed_order_value(self, row, column):
        value = self.orders_table.item(row, column).text()

        with open("data/orders.json", 'r', encoding="utf-8") as f:
            orders_dict = json.load(f)

        orders_dict[column]["orders"] = int(value)

        with open("data/orders.json", 'w', encoding="utf-8") as f:
            json.dump(orders_dict, f, indent=1)
        
        self.error_label.setText("")
        self.init_calculations()

    def init_calculations(self):
        try:
            materials = pd.read_json("data/materials.json")
            msp_result =  msp.build_msp(materials.skateboard)

            for col in range(0, 7):
                for row in range(0, 3):
                    item = QTableWidgetItem("0")
                    item.setFlags(Qt.ItemFlag.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ghp_table.item(row, col).setText((str(msp_result.iloc[row, col])))

            mrp_elements = [materials.wheel, materials.wood, materials.truck, materials.board]

            for mrp_element in mrp_elements:
                mrp_result = mrp.build_mrp([0,0,0,15,10,0], mrp_element)

                current_tab = None
                for i in range(0, self.tabs.count()):
                    tab = self.tabs.widget(i)
                    if tab.objectName() == mrp_element.name:
                        current_tab = tab

                if current_tab:
                    for col in range(0, 6):
                        for row in range(0, 6):
                            item = QTableWidgetItem("0")
                            item.setFlags(Qt.ItemFlag.ItemIsEditable)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            current_tab.layout().itemAt(1).widget().item(row, col).setText((str(mrp_result.iloc[row, col])))
        except Exception as e:
            self.error_label.setText(str(e))