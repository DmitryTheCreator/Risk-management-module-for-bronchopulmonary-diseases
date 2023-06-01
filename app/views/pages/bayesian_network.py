import re
from collections import defaultdict

import networkx as nx
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QListWidget, QComboBox, QHBoxLayout, \
    QMessageBox


class BayesianNetworkView(QWidget):
    def __init__(self, risk_analysis_data):
        super().__init__()
        self.risk_analysis_data = risk_analysis_data
        for risk in self.risk_analysis_data.get_selected_risks():
            risk.set_enable_state(False)
        self.risk_analysis_data.get_risk_by_id(0).set_enable_state()

        self.fig_cause = Figure(figsize=(5, 4), dpi=100)
        self.fig_consequence = Figure(figsize=(5, 4), dpi=100)
        self.canvas_cause = FigureCanvas(self.fig_cause)
        self.canvas_consequence = FigureCanvas(self.fig_consequence)

        # Добавление субграфиков на каждую фигуру
        self.ax1 = self.fig_cause.add_subplot(111)  # Сеть причин
        self.ax2 = self.fig_consequence.add_subplot(111)  # Сеть последствий

        self.cause_add_combo = QComboBox()
        self.consequence_add_combo = QComboBox()
        self.cause_add_input = QLineEdit()
        self.consequence_add_input = QLineEdit()
        self.cause_remove_combo = QComboBox()
        self.consequence_remove_combo = QComboBox()
        self.cause_add_button = QPushButton('Определить оценку для причины')
        self.consequence_add_button = QPushButton('Определить оценку для последствия')
        self.cause_remove_button = QPushButton('Удалить оценку для причины')
        self.consequence_remove_button = QPushButton('Удалить оценку для последствия')
        # self.add_button.clicked.connect(self.add_cause_consequence)
        self.risks_list = QListWidget()
        self.risks_list.itemClicked.connect(self.on_risk_selected)


        # self.remove_cause_button.clicked.connect(self.remove_cause)
        # self.remove_cause_button.setEnabled(False)
        # self.remove_consequence_button.clicked.connect(self.remove_consequence)
        # self.remove_consequence_button.setEnabled(False)
        self.next_risk_button = QPushButton('Перейти к следующему риску')
        self.next_risk_button.clicked.connect(self.switch_to_next_risk)
        self.next_risk_button.setEnabled(False)
        self.next_button = QPushButton('Далее')
        self.back_button = QPushButton('Назад')
        self.next_button.setEnabled(False)
        self.back_button.clicked.connect(self.on_back_button_clicked)
        self.next_button.clicked.connect(self.on_next_button_clicked)
        # Инициализация индекса текущего выбранного риска и списка активных элементов списка
        self.current_item_index = 0
        self.enabled_list_items = [self.risk_analysis_data.get_risk_by_id(self.current_item_index).get_name()]

        # Установка состояния первого риска и заполнение списка рисков
        self.risk_analysis_data.get_risk_by_id(0).set_enable_state()
        self.fill_risks_list()

        # Обновление состояния интерфейса на основе первого риска
        self.update_risk_list_state()
        self.init_ui()
        self.update_states(self.risk_analysis_data.get_risk_by_id(0))

    def init_ui(self):
        header = QLabel('Определите количественную оценку для каждого узла для сетей причин и последствий')
        header.setStyleSheet('font: 24pt \"MS Sans Serif\";')
        header.setWordWrap(True)
        header.setAlignment(Qt.AlignCenter)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(header)
        horizontal_layout = QHBoxLayout()
        vertical_layout_left = QVBoxLayout()
        vertical_layout_right = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout_left, 1)
        horizontal_layout.addLayout(vertical_layout_right, 5)
        vertical_layout.addLayout(horizontal_layout)

        vertical_layout_left.addWidget(self.risks_list)
        header = QLabel('Определение количественной оценки')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('font: 12pt; MS Sans Serif;')
        vertical_layout_left.addWidget(header)
        vertical_layout_left.addSpacing(20)

        hor_layout = QHBoxLayout()
        header = QLabel('Причина')
        header.setStyleSheet('font: 10pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        header = QLabel('Последствие')
        header.setStyleSheet('font: 10pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        vertical_layout_left.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.cause_add_combo)
        hor_layout.addWidget(self.consequence_add_combo)
        vertical_layout_left.addLayout(hor_layout)
        vertical_layout_left.addSpacing(10)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.cause_add_input)
        hor_layout.addWidget(self.consequence_add_input)
        vertical_layout_left.addLayout(hor_layout)
        vertical_layout_left.addSpacing(10)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.cause_add_button)
        hor_layout.addWidget(self.consequence_add_button)
        vertical_layout_left.addLayout(hor_layout)
        vertical_layout_left.addSpacing(20)

        header = QLabel('Удаление количественной оценки')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('font: 12pt; MS Sans Serif;')
        vertical_layout_left.addWidget(header)
        vertical_layout_left.addSpacing(20)

        hor_layout = QHBoxLayout()
        header = QLabel('Причина')
        header.setStyleSheet('font: 10pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        header = QLabel('Последствие')
        header.setStyleSheet('font: 10pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        vertical_layout_left.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.cause_remove_combo)
        hor_layout.addWidget(self.consequence_remove_combo)
        vertical_layout_left.addLayout(hor_layout)
        vertical_layout_left.addSpacing(10)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.cause_remove_button)
        hor_layout.addWidget(self.consequence_remove_button)
        vertical_layout_left.addLayout(hor_layout)

        vertical_layout_right.addWidget(self.canvas_cause)
        vertical_layout_right.addWidget(self.canvas_consequence)

        vertical_layout.addSpacing(40)
        vertical_layout.addWidget(self.next_risk_button, alignment=Qt.AlignCenter)
        vertical_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button, alignment=Qt.AlignBottom | Qt.AlignLeft)
        button_layout.addStretch(1)
        button_layout.addWidget(self.next_button, alignment=Qt.AlignBottom | Qt.AlignRight)
        vertical_layout.addLayout(button_layout)

        self.next_risk_button.setStyleSheet(
            'background-color: #E0E0E0; font-size: 10pt; height: 20px; width: 300px')
        self.back_button.setStyleSheet('background-color: #E0E0E0; font-size: 12pt; height: 30px; width: 300px')
        self.next_button.setStyleSheet('background-color: #E0E0E0; font-size: 12pt; height: 30px; width: 300px')

        self.setLayout(vertical_layout)

        self.draw_bayesian_networks(self.risk_analysis_data.get_risk_by_id(0))

    def draw_bayesian_networks(self, risk):
        self.ax1.clear()
        self.ax2.clear()

        g_cause = nx.DiGraph()
        g_consequence = nx.DiGraph()

        for cause in risk.get_causes():
            g_cause.add_node(cause.get_name())
        g_cause.add_node(risk.get_name())
        for cause in risk.get_causes():
            g_cause.add_edge(risk.get_name(), cause.get_name())

        for consequence in risk.get_consequences():
            g_consequence.add_node(consequence.get_name())
        g_consequence.add_node(risk.get_name())
        for consequence in risk.get_consequences():
            g_consequence.add_edge(risk.get_name(), consequence.get_name())

        pos_cause = set_node_positions(g_cause, 0)
        pos_consequence = set_node_positions(g_consequence, 1)

        # Выбор размера узлов и цвета для корневого узла и причин
        node_sizes_cause = [600 if node == risk.get_name() else 500 for node in g_cause.nodes()]
        node_colors_cause = ['#47A992' if node == risk.get_name() else '#FF7F00' for node in g_cause.nodes()]

        nx.draw(g_cause, pos_cause, with_labels=True, ax=self.ax1, node_size=node_sizes_cause,
                node_color=node_colors_cause, edge_color='#336699', font_size=10)

        # Выбор размера узлов и цвета для корневого узла и последствий
        node_sizes_consequence = [600 if node == risk.get_name() else 500 for node in g_consequence.nodes()]
        node_colors_consequence = ['#47A992' if node == risk.get_name() else '#E84545' for node in g_consequence.nodes()]

        nx.draw(g_consequence, pos_consequence, with_labels=True, ax=self.ax2, node_size=node_sizes_consequence,
                node_color=node_colors_consequence, edge_color='#0A4D68', font_size=10)

        # отрисовка сетей
        self.canvas_cause.draw()
        self.canvas_consequence.draw()

    def fill_risks_list(self):
        # Заполнение списка рисков
        self.risks_list.clear()
        self.risks_list.addItems([risk.get_name() for risk in self.risk_analysis_data.get_selected_risks()])

        if self.risks_list.count() == 1:
            self.next_risk_button.hide()

    def on_risk_selected(self):
        # Обработка выбора риска из списка
        risk = self.risk_analysis_data.get_risk_by_id(self.risks_list.row(self.risks_list.currentItem()))
        if risk.get_enable_state():
            self.current_item_index = self.risk_analysis_data.get_selected_risks().index(risk)
            self.update_states(risk)

    def add_cause_consequence(self):
        # Добавление причины и последствия к текущему риску
        cause = self.cause_input.text()
        consequence = self.consequence_input.text()
        current_risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)

        if is_valid_input(cause):
            current_risk.add_cause(cause)

        if is_valid_input(consequence):
            current_risk.add_consequence(consequence)

        if is_valid_input(cause) or is_valid_input(consequence):
            self.update_states(current_risk)

        self.check_filled_risks()
        self.cause_input.clear()
        self.consequence_input.clear()

    def update_combo_boxes(self, risk):
        # Обновление выпадающих списков причин и последствий
        self.cause_add_combo.clear()
        self.cause_remove_combo.clear()
        cause_items = [cause.get_name() for cause in risk.get_causes()]
        self.cause_add_combo.addItems(cause_items)
        self.cause_remove_combo.addItems(cause_items)
        self.cause_remove_button.setEnabled(len(risk.get_causes()) > 1)

        self.consequence_add_combo.clear()
        self.consequence_remove_combo.clear()
        consequence_items = [consequence.get_name() for consequence in risk.get_consequences()]
        self.consequence_add_combo.addItems(consequence_items)
        self.consequence_remove_combo.addItems(consequence_items)
        self.consequence_remove_button.setEnabled(len(risk.get_consequences()) > 1)

    def remove_cause(self):
        # Удаление выбранной причины
        cause = self.cause_combo.currentText()
        risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
        causes = risk.get_causes()
        if cause in causes and len(causes) > 1:
            risk.remove_cause(cause)
            self.update_states(risk)

    def remove_consequence(self):
        # Удаление выбранного последствия
        consequence = self.consequence_combo.currentText()
        risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
        consequences = risk.get_consequences()
        if consequence in consequences and len(consequences) > 1:
            risk.remove_consequence(consequence)
            self.update_states(risk)

    def switch_to_next_risk(self):
        # Переключение на следующий риск
        self.current_item_index += 1
        current_risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
        current_risk.set_enable_state()
        self.update_states(current_risk)
        if self.current_item_index + 1 >= self.risks_list.count():
            self.next_risk_button.hide()

    def update_next_risk_button_state(self, risk):
        # Обновление состояния кнопки перехода к следующему риску
        # Кнопка активна, если текущий риск имеет хотя бы одну причину и одно последствие
        if all_data_entered_for_current_risk(risk):
            self.next_risk_button.setEnabled(True)
        else:
            self.next_risk_button.setEnabled(False)

        if self.risks_list.currentIndex() == self.risks_list.count() - 1:
            self.next_risk_button.hide()

    def update_risk_list_state(self):
        # Обновление состояния списка рисков
        self.fill_risks_list()

        for index in range(len(self.risk_analysis_data.get_selected_risks())):
            if self.risk_analysis_data.get_selected_risks()[index].get_enable_state():
                self.risks_list.item(index).setForeground(Qt.black)
            else:
                self.risks_list.item(index).setForeground(Qt.gray)

        self.risks_list.item(self.current_item_index).setText(
            "--> " + self.risks_list.item(self.current_item_index).text())

    def update_states(self, risk):
        # Обновление состояний элементов интерфейса на основе текущего риска
        self.update_next_risk_button_state(risk)
        self.update_combo_boxes(risk)
        self.update_risk_list_state()
        self.draw_bayesian_networks(risk)

    def on_next_button_clicked(self):
        # Обработка нажатия кнопки "Далее"
        self.goToBayesianNetworkPageSignal.emit()

    def on_back_button_clicked(self):
        # Обработка нажатия кнопки "Назад"
        selected_risks = self.risk_analysis_data.get_selected_risks()
        risks_to_remove = selected_risks.copy()

        for risk in risks_to_remove:
            self.risk_analysis_data.remove_risk(risk)

        self.goToRiskPageSignal.emit()


def show_error_message():
    # Отображение сообщения об ошибке ввода
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("Вводимые данные могут содержать только буквы, цифры и пробелы.")
    msg.setWindowTitle("Ошибка ввода")
    msg.exec_()


def is_valid_input(input_str):
    # Проверка корректности ввода данных
    if len(input_str.strip()) == 0:
        return False
    elif not re.match("^[A-Za-zА-Яа-я0-9 ]*$", input_str):
        show_error_message()
        return False
    else:
        return True


def all_data_entered_for_current_risk(risk):
    # Проверка, что все данные введены для текущего риска
    return len(risk.get_causes()) > 0 and len(risk.get_consequences()) > 0


def set_node_positions(graph, root_node_y):
    pos = {}
    levels = defaultdict(list)
    level = 0
    leaf_nodes = [node for node, out_degree in graph.out_degree() if out_degree == 0]
    next_level = leaf_nodes.copy()

    while next_level:
        current_level = next_level
        next_level = []
        for node in current_level:
            levels[level].append(node)
            next_level.extend(list(graph.predecessors(node)))
        level += 1

    total_levels = len(levels)
    for level, nodes in reversed(list(levels.items())):
        if level == 0:
            for i, node in enumerate(nodes):
                pos[node] = [i / (len(nodes) - 1) if len(nodes) > 1 else 0.5, root_node_y]
        else:
            for node in nodes:
                parents = list(graph.predecessors(node))
                if parents:
                    min_parent_x = min(pos[parent][0] for parent in parents)
                    max_parent_x = max(pos[parent][0] for parent in parents)
                    siblings = [n for n in nodes if n != node]
                    sibling_x_positions = [pos[sibling][0] for sibling in siblings]
                    sibling_x_positions.sort()
                    lower_bound = sibling_x_positions[0] if sibling_x_positions else 0
                    upper_bound = sibling_x_positions[-1] if sibling_x_positions else 1
                    pos[node] = [(min_parent_x + max_parent_x) / 2, (total_levels - level) / total_levels]
                    if pos[node][0] < lower_bound:
                        pos[node][0] = lower_bound
                    elif pos[node][0] > upper_bound:
                        pos[node][0] = upper_bound
                else:
                    pos[node] = [0.5, (total_levels - level) / total_levels]
    return pos
