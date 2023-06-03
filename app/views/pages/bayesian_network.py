from collections import defaultdict

import networkx as nx
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QListWidget, QComboBox, QHBoxLayout, \
    QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from app.models.edge import Cause


class BayesianNetworkView(QWidget):
    # Сигнал, отправляемый при переходе к странице определения причин и последствий
    goToBowChartPageSignal = pyqtSignal()
    # Сигнал, отправляемый при переходе к странице с форированием карты рисков
    goToRiskMapPageSignal = pyqtSignal()

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
        self.cause_add_button = QPushButton('Оценить причину')
        self.consequence_add_button = QPushButton('Оценить последствие')

        self.cause_add_button.clicked.connect(self.add_cause_probability)
        self.consequence_add_button.clicked.connect(self.add_consequence_probability)

        self.risks_list = QListWidget()
        self.risks_list.itemClicked.connect(self.on_risk_selected)

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
        # Установка состояния первого риска и заполнение списка рисков
        self.risk_analysis_data.get_risk_by_id(0).set_enable_state()
        self.fill_risks_list()

        # Обновление состояния интерфейса на основе первого риска
        self.check_filled_risks()
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

        cause_total_prob = 0
        for cause in risk.get_causes():
            cause_prob = cause.get_probability()
            cause_total_prob += cause_prob if cause_prob is not None else 0
            g_cause.add_node(cause.get_name(), probability=cause_prob)
        g_cause.add_node(risk.get_name(), probability=round(cause_total_prob, 8))
        for cause in risk.get_causes():
            g_cause.add_edge(risk.get_name(), cause.get_name())

        consequence_total_prob = 0
        for consequence in risk.get_consequences():
            consequence_prob = consequence.get_probability()
            consequence_total_prob += consequence_prob if consequence_prob is not None else 0
            g_consequence.add_node(consequence.get_name(), probability=consequence_prob)
        g_consequence.add_node(risk.get_name(), probability=round(consequence_total_prob, 8))
        for consequence in risk.get_consequences():
            g_consequence.add_edge(risk.get_name(), consequence.get_name())

        pos_cause = set_node_positions(g_cause, 0)
        pos_consequence = set_node_positions(g_consequence, 1)

        node_sizes_cause = [600 if node == risk.get_name() else 500 for node in g_cause.nodes()]
        node_colors_cause = ['#47A992' if node == risk.get_name() else '#FF7F00' for node in g_cause.nodes()]
        node_sizes_consequence = [600 if node == risk.get_name() else 500 for node in g_consequence.nodes()]
        node_colors_consequence = ['#47A992' if node == risk.get_name() else '#E84545' for node in
                                   g_consequence.nodes()]

        nx.draw(g_cause, pos_cause, with_labels=False, ax=self.ax1, node_size=node_sizes_cause,
                node_color=node_colors_cause, edge_color='#336699', font_size=10)
        nx.draw(g_consequence, pos_consequence, with_labels=False, ax=self.ax2, node_size=node_sizes_consequence,
                node_color=node_colors_consequence, edge_color='#0A4D68', font_size=10)

        for node, (x, y) in pos_cause.items():
            probability = g_cause.nodes[node]['probability']
            if probability is None:
                label = f'{node}'
            else:
                label = f'{node}\n({probability})'
            self.ax1.text(x, y, label, fontsize=10, ha='center')

        for node, (x, y) in pos_consequence.items():
            probability = g_consequence.nodes[node]['probability']
            if probability is None:
                label = f'{node}'
            else:
                label = f'{node}\n({probability})'
            self.ax2.text(x, y, label, fontsize=10, ha='center')

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

    def add_cause_probability(self):
        # Добавление причины и последствия к текущему риску
        cause_text = self.cause_add_combo.currentText()
        input_value = self.cause_add_input.text()
        current_risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
        current_cause = current_risk.get_cause_by_name(cause_text)

        if is_valid_input(input_value, current_risk, current_cause):
            current_cause.set_probability(round(float(input_value), 8))
            self.update_states(current_risk)

        self.check_filled_risks()
        self.cause_add_input.clear()

    def add_consequence_probability(self):
        # Добавление причины и последствия к текущему риску
        consequence_text = self.consequence_add_combo.currentText()
        input_value = self.consequence_add_input.text()
        current_risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
        current_consequence = current_risk.get_consequence_by_name(consequence_text)

        if is_valid_input(input_value, current_risk, current_consequence):
            current_consequence.set_probability(round(float(input_value), 8))
            self.update_states(current_risk)

        self.check_filled_risks()
        self.consequence_add_input.clear()

    def update_combo_boxes(self, risk):
        # Обновление выпадающих списков причин и последствий
        self.cause_add_combo.clear()
        cause_add_items = [cause.get_name() for cause in risk.get_causes()]
        self.cause_add_combo.addItems(cause_add_items)

        self.consequence_add_combo.clear()
        consequence_add_items = [consequence.get_name() for consequence in risk.get_consequences()]
        self.consequence_add_combo.addItems(consequence_add_items)

    def switch_to_next_risk(self):
        # Переключение на следующий риск
        if is_valid_probabilities(self.risk_analysis_data.get_risk_by_id(self.current_item_index)):
            self.current_item_index += 1
            current_risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
            current_risk.set_enable_state()
            self.update_states(current_risk)
            if self.current_item_index + 1 >= self.risks_list.count():
                self.next_risk_button.hide()

    def check_filled_risks(self):
        # Проверка, что все риски имеют заполненные данные
        for risk in self.risk_analysis_data.get_selected_risks():
            if not all_data_entered_for_current_risk(causes=risk.get_causes(), consequences=risk.get_consequences()):
                return
            if not is_valid_probabilities(risk):
                return
        for risk in self.risk_analysis_data.get_selected_risks():
            risk.set_enable_state()
        self.next_risk_button.hide()
        self.next_button.setEnabled(True)

    def update_next_risk_button_state(self, risk):
        # Обновление состояния кнопки перехода к следующему риску
        # Кнопка активна, если текущий риск имеет хотя бы одну причину и одно последствие
        if self.risks_list.currentIndex() == self.risks_list.count() - 1:
            self.next_risk_button.hide()
        elif all_data_entered_for_current_risk(risk.get_causes(), risk.get_consequences()):
            self.next_risk_button.setEnabled(True)
        else:
            self.next_risk_button.setEnabled(False)

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
        update_last_edge_probability(risk)
        self.update_next_risk_button_state(risk)
        self.update_combo_boxes(risk)
        self.update_risk_list_state()
        self.draw_bayesian_networks(risk)

    def on_next_button_clicked(self):
        # Обработка нажатия кнопки "Далее"
        self.goToRiskMapPageSignal.emit()

    def on_back_button_clicked(self):
        # Обработка нажатия кнопки "Назад"
        for risk in self.risk_analysis_data.get_selected_risks():
            risk.set_enable_state()

        self.goToBowChartPageSignal.emit()


def update_last_edge_probability(risk):
    # Обновление вероятности последнего незаполненного узла в сети причин
    is_none_list = []
    for cause in risk.get_causes():
        if cause.get_probability() is None:
            is_none_list.append(cause)
    if len(is_none_list) == 1:
        # Если есть только одна незаполненная причина и сумма вероятностей остальных причин неотрицательна,
        # устанавливаем вероятность последней незаполненной причины равной оставшейся сумме вероятностей
        if risk.get_causes_remaining_probability() >= 0:
            is_none_list[0].set_probability(round(risk.get_causes_remaining_probability(), 8))
        else:
            # Иначе, если сумма вероятностей остальных причин отрицательна, устанавливаем вероятность последней
            # незаполненной причины равной 0
            is_none_list[0].set_probability(0)
        # Сбрасываем оставшуюся сумму вероятностей причин на 0
        risk.change_causes_remaining_probability(0, False)

    # Обновление вероятности последнего незаполненного узла в сети последствий
    is_none_list = []
    for consequence in risk.get_consequences():
        if consequence.get_probability() is None:
            is_none_list.append(consequence)
    if len(is_none_list) == 1:
        # Если есть только одно незаполненное последствие и сумма вероятностей остальных последствий неотрицательна,
        # устанавливаем вероятность последнего незаполненного последствия равной оставшейся сумме вероятностей
        if risk.get_consequences_remaining_probability() >= 0:
            is_none_list[0].set_probability(round(risk.get_consequences_remaining_probability(), 8))
        else:
            # Иначе, если сумма вероятностей остальных последствий отрицательна, устанавливаем вероятность последнего
            # незаполненного последствия равной 0
            is_none_list[0].set_probability(0)
        # Сбрасываем оставшуюся сумму вероятностей последствий на 0
        risk.change_consequences_remaining_probability(0, False)


def show_error_input_message(is_incorrect_input):
    # Отображение сообщения об ошибке ввода
    if is_incorrect_input:
        mes = 'Введите корректную количественную оценку'
    else:
        mes = f'Вводимое значение должно быть в диапазоне от 0 до 1'
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(mes)
    msg.setWindowTitle("Ошибка ввода")
    msg.exec_()


def show_error_total_message(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(message)
    msg.setWindowTitle("Ошибка ввода")
    msg.exec_()


def all_data_entered_for_current_risk(causes=None, consequences=None):
    # Проверяем, что для каждой причины в сети причин указана вероятность
    if causes:
        for cause in causes:
            if cause.get_probability() is None:
                return False
    # Проверяем, что для каждого последствия в сети последствий указана вероятность
    if consequences:
        for consequence in consequences:
            if consequence.get_probability() is None:
                return False
    return True


def is_valid_input(input_str, risk, edge):
    # Проверка корректности ввода данных
    if len(input_str.strip()) == 0:
        return False
    else:
        try:
            # Пробуем преобразовать входную строку в число
            input_value = float(input_str)

            # Проверяем, что число входит в заданный диапазон
            if 0 <= input_value <= 1:
                # Уменьшаем оставшуюся вероятность
                current_prob = edge.get_probability()
                if current_prob is not None:
                    value = input_value - current_prob
                else:
                    value = input_value
                if type(edge) is Cause:
                    risk.change_causes_remaining_probability(value, False)
                else:
                    risk.change_consequences_remaining_probability(value, False)
                return True
            else:
                show_error_input_message(False)
                return False
        except ValueError:
            # Если преобразование не удалось, значит, ввод не был числом
            show_error_input_message(True)
            return False


def is_valid_probabilities(risk):
    # Вычисляем сумму вероятностей для причин
    causes_probability_amount = 0
    for cause in risk.get_causes():
        causes_probability_amount += cause.get_probability()
    round_cause_prob_amount = round(causes_probability_amount, 8)

    # Проверяем, что сумма вероятностей причин не меньше 1
    if round_cause_prob_amount < 1:
        show_error_total_message(f'Сумма вероятностей всех узлов сети причин не может быть меньше 1! Текущее '
                                 f'значение {round_cause_prob_amount}')
        return False
    # Проверяем, что сумма вероятностей причин не больше 1
    elif round_cause_prob_amount > 1:
        show_error_total_message(f'Сумма вероятностей всех узлов сети причин не может превышать 1! Текущее '
                                 f'значение {round_cause_prob_amount}')
        return False

    consequences_probability_amount = 0
    for consequence in risk.get_consequences():
        consequences_probability_amount += consequence.get_probability()
    consequence_prob_amount = round(consequences_probability_amount, 8)

    # Проверяем, что сумма вероятностей последствий не меньше 1
    if consequence_prob_amount < 1:
        show_error_total_message(f'Сумма вероятностей всех узлов сети последствий не может быть меньше 1! Текущее '
                                 f'значение {consequence_prob_amount}')
        return False
    # Проверяем, что сумма вероятностей последствий не больше 1
    elif consequence_prob_amount > 1:
        show_error_total_message(f'Сумма вероятностей всех узлов сети последствий не может превышать 1! Текущее '
                                 f'значение {consequence_prob_amount}')
        return False
    return True


def set_node_positions(graph, root_node_y):
    # Функция для определения позиций узлов в графе

    pos = {}  # Словарь для хранения позиций узлов
    levels = defaultdict(list)  # Словарь для хранения уровней узлов
    level = 0

    # Находим узлы-листья (узлы без исходящих ребер) и помещаем их в список leaf_nodes
    leaf_nodes = [node for node, out_degree in graph.out_degree() if out_degree == 0]

    next_level = leaf_nodes.copy()

    # Постепенно проходим по каждому уровню графа, начиная с листьев и двигаясь к корню
    while next_level:
        current_level = next_level
        next_level = []

        for node in current_level:
            levels[level].append(node)
            next_level.extend(list(graph.predecessors(node)))
        level += 1  # Переходим на следующий уровень

    total_levels = len(levels)  # Общее количество уровней графа

    # Проходим по каждому уровню, начиная с последнего
    for level, nodes in reversed(list(levels.items())):
        if level == 0:
            # Если это корневой уровень, располагаем узлы равномерно по горизонтали
            for i, node in enumerate(nodes):
                pos[node] = [i / (len(nodes) - 1) if len(nodes) > 1 else 0.5, root_node_y]
        else:
            # Если это не корневой уровень
            for node in nodes:
                parents = list(graph.predecessors(node))  # Предшествующие узлы
                if parents:
                    # Если есть предшествующие узлы, определяем позицию текущего узла между ними
                    min_parent_x = min(pos[parent][0] for parent in parents)
                    max_parent_x = max(pos[parent][0] for parent in parents)

                    siblings = [n for n in nodes if n != node]  # Узлы-соседи текущего узла
                    sibling_x_positions = [pos[sibling][0] for sibling in siblings]  # Координаты x соседних узлов
                    sibling_x_positions.sort()

                    lower_bound = sibling_x_positions[0] if sibling_x_positions else 0  # Нижняя граница координаты x
                    upper_bound = sibling_x_positions[-1] if sibling_x_positions else 1  # Верхняя граница координаты x

                    pos[node] = [(min_parent_x + max_parent_x) / 2, (total_levels - level) / total_levels]

                    if pos[node][0] < lower_bound:
                        pos[node][0] = lower_bound
                    elif pos[node][0] > upper_bound:
                        pos[node][0] = upper_bound
                else:
                    # Если нет предшествующих узлов, устанавливаем позицию текущего узла в центре по горизонтали
                    pos[node] = [0.5, (total_levels - level) / total_levels]
    return pos

