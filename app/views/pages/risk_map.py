from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout


class RiskMapView(QWidget):
    def __init__(self, risk_analysis_data):
        super().__init__()
        self.risk_analysis_data = risk_analysis_data  # Данные анализа рисков
        self.init_ui()  # Инициализация пользовательского интерфейса

    def init_ui(self):
        # Создание таблицы для отображения карты рисков
        table_widget = QTableWidget()
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Растягивание столбцов на весь экран
        table_widget.setWordWrap(True)  # Включение переноса слов в ячейках
        self.setup_table(table_widget)

        # Создание макета и добавление элементов
        layout = QGridLayout()  # Использование QGridLayout вместо QVBoxLayout
        layout.addWidget(table_widget, 0, 0)  # Добавление виджета в верхний левый угол макета
        self.setLayout(layout)

    def setup_table(self, table_widget):
        # Получение списка выбранных рисков
        selected_risks = self.risk_analysis_data.get_selected_risks()

        lower_bound_risks, middle_bound_risks, upper_bound_risks = self.sort_risks()
        risks_data = []
        for risk in selected_risks:
            lower_bound_consequences, middle_bound_consequences, upper_bound_consequences = sort_consequences(risk)
            risks_data.append((
                risk,
                lower_bound_consequences,
                middle_bound_consequences,
                upper_bound_consequences
            ))

        column_lower_bound_items, column_middle_bound_items, column_upper_bound_items = 1, 1, 1
        for row in risks_data:
            first_col, second_col, third_col = len(row[1]), len(row[2]), len(row[3])
            if first_col > column_lower_bound_items:
                column_lower_bound_items = first_col
            if second_col > column_middle_bound_items:
                column_middle_bound_items = second_col
            if third_col > column_upper_bound_items:
                column_upper_bound_items = third_col

        bound_items_count = column_lower_bound_items + column_middle_bound_items + column_upper_bound_items
        # Установка количества строк в таблице
        num_rows = len(selected_risks) + 2
        table_widget.setRowCount(num_rows)

        # Установка количества столбцов в таблице
        num_columns = bound_items_count + 2  # 2 столбца для вероятности и названия риска
        table_widget.setColumnCount(num_columns)

        # Скрытие заголовков строк и столбцов
        table_widget.verticalHeader().setVisible(False)
        table_widget.horizontalHeader().setVisible(False)

        # Добавление данных в таблицу
        table_widget.setItem(0, 0, QTableWidgetItem("Вероятность возникновения риска"))
        table_widget.setItem(0, 1, QTableWidgetItem("Название риска"))
        table_widget.setSpan(0, 0, 2, 1)  # Вероятность возникновения риска
        table_widget.setSpan(0, 1, 2, 1)  # Название риска

        table_widget.setItem(0, 2, QTableWidgetItem("Оценка развития осложнений"))
        table_widget.setSpan(0, 2, 1, bound_items_count)

        table_widget.setItem(1, 2, QTableWidgetItem("0-29,99%"))
        table_widget.setSpan(1, 2, 1, column_lower_bound_items)

        table_widget.setItem(1, 2 + column_lower_bound_items, QTableWidgetItem("30-69,99%"))
        table_widget.setSpan(1, 2 + column_lower_bound_items, 1, column_middle_bound_items)

        table_widget.setItem(1, 2 + column_lower_bound_items + column_middle_bound_items,
                             QTableWidgetItem("70% и более"))
        table_widget.setSpan(1, 2 + column_lower_bound_items + column_middle_bound_items, 1, column_upper_bound_items)

        table_widget.setItem(2, 0, QTableWidgetItem("Высокая"))
        table_widget.setSpan(2, 0, len(upper_bound_risks), 1)

        table_widget.setItem(2 + len(upper_bound_risks), 0, QTableWidgetItem("Средняя"))
        table_widget.setSpan(2 + len(upper_bound_risks), 0, len(middle_bound_risks), 1)

        table_widget.setItem(2 + len(upper_bound_risks) + len(middle_bound_risks), 0, QTableWidgetItem("Низкая"))
        table_widget.setSpan(2 + len(upper_bound_risks) + len(middle_bound_risks), 0, len(lower_bound_risks), 1)

        row_counter = 2
        for row, risk_data in enumerate(risks_data):
            table_widget.setItem(row_counter, 1, QTableWidgetItem(risk_data[0].get_name()))
            for column, consequence in enumerate(risk_data[1]):
                item = QTableWidgetItem(f'{consequence.get_name()} -> ({consequence.get_ratio()})')
                if row_counter < 2 + len(upper_bound_risks) + len(middle_bound_risks):
                    item.setBackground(Qt.yellow)
                else:
                    item.setBackground(Qt.green)
                table_widget.setItem(row_counter, column + 2, item)
            for column, consequence in enumerate(risk_data[2]):
                item = QTableWidgetItem(f'{consequence.get_name()} -> ({consequence.get_ratio()})')
                if row_counter < 2 + len(upper_bound_risks) + len(middle_bound_risks):
                    item.setBackground(Qt.yellow)
                else:
                    item.setBackground(Qt.green)
                table_widget.setItem(row_counter, column + column_lower_bound_items + 2, item)
            for column, consequence in enumerate(risk_data[3]):
                item = QTableWidgetItem(f'{consequence.get_name()} -> ({consequence.get_ratio()})')
                if row_counter < 2 + len(upper_bound_risks):
                    item.setBackground(Qt.red)
                else:
                    item.setBackground(Qt.yellow)
                table_widget.setItem(row_counter, column + column_lower_bound_items + column_middle_bound_items + 2,
                                     item)
            row_counter += 1

        # Добавление данных в таблицу и выравнивание текста
        for row in range(table_widget.rowCount()):
            for column in range(table_widget.columnCount()):
                item = table_widget.item(row, column)
                if item is not None:  # Проверка, что элемент существует
                    item.setTextAlignment(Qt.AlignCenter)

    def sort_risks(self, lower_bound=0.75, middle_bound=0.9):
        lower_bound_items, middle_bound_items, upper_bound_items = [], [], []
        for risk in self.risk_analysis_data.get_selected_risks():
            if risk.get_probability_score() < lower_bound:
                lower_bound_items.append(risk)
            elif risk.get_probability_score() < middle_bound:
                middle_bound_items.append(risk)
            else:
                upper_bound_items.append(risk)
        return lower_bound_items, middle_bound_items, upper_bound_items


def sort_consequences(risk, lower_bound=0.3, middle_bound=0.7):
    lower_bound_items, middle_bound_items, upper_bound_items = [], [], []
    for consequence in risk.get_consequences():
        if consequence.get_ratio() < lower_bound:
            lower_bound_items.append(consequence)
        elif consequence.get_ratio() < middle_bound:
            middle_bound_items.append(consequence)
        else:
            upper_bound_items.append(consequence)
    return lower_bound_items, middle_bound_items, upper_bound_items


# def get_color_by_probability(current_row, probability, lower_bound, middle_bound):
#     if current_row < lower_bound:
#         if probability < 0.3:
#             return QColor(Qt.green)
#         elif probability < 0.7:
#             return QColor(Qt.green)
#         else:
#             return QColor(Qt.yellow)
#     elif current_row < middle_bound:
#         if probability < 0.3:
#             return QColor(Qt.green)
#         elif probability < 0.7:
#             return QColor(Qt.yellow)
#         else:
#             return QColor(Qt.red)
#     else:
#         if probability < 0.3:
#             return QColor(Qt.yellow)
#         elif probability < 0.7:
#             return QColor(Qt.yellow)
#         else:
#             return QColor(Qt.red)
