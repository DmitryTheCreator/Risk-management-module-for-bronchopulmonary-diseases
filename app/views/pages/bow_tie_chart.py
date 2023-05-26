import time

from PyQt5.QtCore import Qt, QUrl, QDir
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
import plotly.graph_objects as go


class BowTieChartView(QWidget):
    def __init__(self, risk_analysis_data, parent=None):
        super().__init__(parent)
        self.add_button = QPushButton('Добавить')
        self.consequence_input = QLineEdit()
        self.cause_input = QLineEdit()
        self.header = QLabel('Согласно Международной классификации болезней МКБ-10')
        self.risk_analysis_data = risk_analysis_data  # Данные анализа рисков
        self.chart_view = QWebEngineView()
        self.causes, self.consequences = ['Причина 1'], ['Последствие 1']  # начальные значения
        self.first_cause_input, self.first_consequence_input = True, True  # флаги для первого ввода
        self.chart_view = self.create_chart()  # Создаем начальный график
        self.init_ui()

    def init_ui(self):
        self.header.setStyleSheet('color: rgb(118, 118, 118); font: 14pt; MS Sans Serif;')
        self.header.setAlignment(Qt.AlignCenter)
        self.add_button.clicked.connect(self.add_cause_consequence)

        vert_layout = QVBoxLayout()
        vert_layout.addWidget(self.header)
        vert_layout.addWidget(self.cause_input)
        vert_layout.addWidget(self.consequence_input)
        vert_layout.addWidget(self.add_button)
        vert_layout.addWidget(self.chart_view)
        self.setLayout(vert_layout)

    def create_chart(self):
        if not self.causes and not self.consequences:
            labels = ['Выбранный риск']
            node_color = ['#FF7F00']
            source, target, link_color, value = [], [], [], [0]
        else:
            labels = self.causes + ['Выбранный риск'] + self.consequences
            node_color = ['#FF7F00'] * len(self.causes) + ['#47A992'] + ['#E84545'] * len(self.consequences)

            source = [self.causes.index(cause) for cause in self.causes] + [len(self.causes)] * len(self.consequences)
            target = [len(self.causes)] * len(self.causes) + [
                len(self.causes) + 1 + self.consequences.index(consequence)
                for consequence in self.consequences]
            link_color = ['#0A4D68'] * len(self.causes) + ['#336699'] * len(self.consequences)

            nodes_amount = len(self.causes) + len(self.consequences)
            causes_value = [nodes_amount / 2 / len(self.causes)] * len(self.causes) if len(self.causes) != 0 else [0]
            consequences_value = [nodes_amount / 2 / len(self.consequences)] * len(self.consequences) \
                if len(self.consequences) != 0 else [0]
            value = causes_value + consequences_value

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=100,
                thickness=100,
                line=dict(color="black", width=0.5),
                label=labels,
                color=node_color
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_color
            )
        )])

        fig.update_layout(font=dict(size=20))

        fig.write_html("test_plot.html")

        chart_view = QWebEngineView()
        chart_view.load(QUrl.fromLocalFile(QDir.current().absoluteFilePath("test_plot.html")))

        return chart_view

    def add_cause_consequence(self):
        cause = self.cause_input.text()
        consequence = self.consequence_input.text()

        if self.is_valid_input(cause):
            if self.first_cause_input:  # если это первый ввод причины
                self.causes[0] = cause  # заменить начальное значение новым
                self.first_cause_input = False  # установить флаг первого ввода в False
            else:
                self.causes.append(cause)  # иначе, добавить новую причину

        if self.is_valid_input(consequence):
            if self.first_consequence_input:  # если это первый ввод последствия
                self.consequences[0] = consequence  # заменить начальное значение новым
                self.first_consequence_input = False  # установить флаг первого ввода в False
            else:
                self.consequences.append(consequence)  # иначе, добавить новое последствие

        if self.is_valid_input(cause) or self.is_valid_input(consequence):
            self.create_chart()  # Создаем новый график с обновленными данными
            self.chart_view.load(QUrl.fromLocalFile(QDir.current().absoluteFilePath("test_plot.html")))
            self.chart_view.reload()

        self.cause_input.clear()
        self.consequence_input.clear()

    def is_valid_input(self, input_str):
        return len(input_str.strip()) > 0

