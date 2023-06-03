import re
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QListWidget, \
    QHBoxLayout

from app.models.edge import Cause, Consequence


class BowTieChartView(QWidget):
    # Сигнал, отправляемый при переходе к странице анализа рисков
    goToRiskPageSignal = pyqtSignal()
    # Сигнал, отправляемый при переходе к странице с определением количественной оценки по каждому риску
    goToBayesianNetworkPageSignal = pyqtSignal()

    def __init__(self, risk_analysis_data, parent=None):
        super().__init__(parent)
        # Создаем виджеты и привязываем сигналы к слотам
        self.add_button = QPushButton('Добавить')
        self.add_button.clicked.connect(self.add_cause_consequence)
        self.consequence_input = QLineEdit()
        self.cause_input = QLineEdit()
        self.risk_analysis_data = risk_analysis_data
        self.header = QLabel('Введите причины и последствия')
        self.header.setStyleSheet('font: 16pt; MS Sans Serif;')
        self.chart_view = QWebEngineView()
        self.chart_view.hide()
        self.risks_list = QListWidget()
        self.risks_list.itemClicked.connect(self.on_risk_selected)
        self.remove_cause_button = QPushButton('Удалить причину')
        self.remove_consequence_button = QPushButton('Удалить последствие')
        self.cause_combo = QComboBox()
        self.consequence_combo = QComboBox()
        self.remove_cause_button.clicked.connect(self.remove_cause)
        self.remove_cause_button.setEnabled(False)
        self.remove_consequence_button.clicked.connect(self.remove_consequence)
        self.remove_consequence_button.setEnabled(False)
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
        # Создание и настройка элементов интерфейса
        header = QLabel('Определите причины и последствия для каждого выбранного риска')
        header.setStyleSheet('font: 24pt \"MS Sans Serif\";')
        header.setWordWrap(True)
        header.setAlignment(Qt.AlignCenter)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(header)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.risks_list, 1)
        horizontal_layout.addWidget(self.chart_view, 4)
        horizontal_layout.addWidget(self.header, stretch=4, alignment=Qt.AlignCenter)
        vertical_layout.addLayout(horizontal_layout)

        horizontal_layout = QHBoxLayout()
        vert_layout = QVBoxLayout()
        header = QLabel('Добавление причин или последствий')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('font: 16pt; MS Sans Serif;')
        vert_layout.addWidget(header)
        vert_layout.addSpacing(20)

        hor_layout = QHBoxLayout()
        header = QLabel('Причина')
        header.setStyleSheet('font: 12pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        header = QLabel('Последствие')
        header.setStyleSheet('font: 12pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        vert_layout.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.cause_input)
        hor_layout.addWidget(self.consequence_input)
        vert_layout.addLayout(hor_layout)
        vert_layout.addSpacing(20)
        vert_layout.addWidget(self.add_button)
        horizontal_layout.addLayout(vert_layout, 1)
        horizontal_layout.addSpacing(60)

        vert_layout = QVBoxLayout()
        header = QLabel('Удаление причин или последствий')
        header.setStyleSheet('font: 16pt; MS Sans Serif;')
        header.setAlignment(Qt.AlignCenter)
        vert_layout.addWidget(header)
        vert_layout.addSpacing(20)

        hor_layout = QHBoxLayout()
        header = QLabel('Причина')
        header.setStyleSheet('font: 12pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        header = QLabel('Последствие')
        header.setStyleSheet('font: 12pt; MS Sans Serif;')
        hor_layout.addWidget(header)
        vert_layout.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.cause_combo)
        hor_layout.addWidget(self.consequence_combo)
        vert_layout.addLayout(hor_layout)
        vert_layout.addSpacing(20)

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.remove_cause_button)
        hor_layout.addWidget(self.remove_consequence_button)
        vert_layout.addLayout(hor_layout)
        horizontal_layout.addLayout(vert_layout, 1)
        vertical_layout.addLayout(horizontal_layout)
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
            current_risk.add_cause(Cause(cause))

        if is_valid_input(consequence):
            current_risk.add_consequence(Consequence(consequence))

        if is_valid_input(cause) or is_valid_input(consequence):
            self.update_states(current_risk)

        self.check_filled_risks()
        self.cause_input.clear()
        self.consequence_input.clear()

    def update_combo_boxes(self, risk):
        # Обновление выпадающих списков причин и последствий
        self.cause_combo.clear()
        self.cause_combo.addItems(cause.get_name() for cause in risk.get_causes())
        self.remove_cause_button.setEnabled(len(risk.get_causes()) > 1)

        self.consequence_combo.clear()
        self.consequence_combo.addItems(consequences.get_name() for consequences in risk.get_consequences())
        self.remove_consequence_button.setEnabled(len(risk.get_consequences()) > 1)

    def remove_cause(self):
        # Удаление выбранной причины
        cause = self.cause_combo.currentText()
        risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
        if risk.included_in_causes(cause) and len(risk.get_causes()) > 1:
            risk.remove_cause(risk.get_cause_by_name(cause))
            self.update_states(risk)

    def remove_consequence(self):
        # Удаление выбранного последствия
        consequence = self.consequence_combo.currentText()
        risk = self.risk_analysis_data.get_risk_by_id(self.current_item_index)
        if risk.included_in_consequences(consequence) and len(risk.get_consequences()) > 1:
            risk.remove_consequence(risk.get_consequence_by_name(consequence))
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
        if self.all_data_entered_for_all_risks() or self.risks_list.currentIndex() == self.risks_list.count() - 1:
            self.next_risk_button.hide()
        elif all_data_entered_for_current_risk(risk):
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

    def check_filled_risks(self):
        # Проверка, что все риски имеют заполненные данные
        # for risk in self.risk_analysis_data.get_selected_risks():
        #     if not all_data_entered_for_current_risk(risk):
        #         return
        if self.all_data_entered_for_all_risks():
            self.next_button.setEnabled(True)

    def update_states(self, risk):
        # Обновление состояний элементов интерфейса на основе текущего риска
        self.update_next_risk_button_state(risk)
        self.update_combo_boxes(risk)
        self.update_risk_list_state()
        result = create_chart(risk)
        if isinstance(result, str):
            self.chart_view.hide()
            self.header.show()
        else:
            self.header.hide()
            self.chart_view.show()
            self.chart_view.load(result)

    def all_data_entered_for_all_risks(self):
        # Проверка, что все данные введены для текущего риска
        for risk in self.risk_analysis_data.get_selected_risks():
            if not (len(risk.get_causes()) > 0 and len(risk.get_consequences()) > 0):
                return False
        return True

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


def all_data_entered_for_current_risk(risk):
    # Проверка, что все данные введены для текущего риска
    return len(risk.get_causes()) > 0 and len(risk.get_consequences()) > 0


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


def create_chart(risk):
    # Создание графика галстук-бабочки для риска
    causes = [cause.get_name() for cause in risk.get_causes()]
    consequences = [consequence.get_name() for consequence in risk.get_consequences()]

    if not causes and not consequences:
        message = "Введите причины и последствия"
        return message
    else:
        labels = causes + [risk.get_name()] + consequences
        node_color = ['#FF7F00'] * len(causes) + ['#47A992'] + ['#E84545'] * len(consequences)

        source = [causes.index(cause) for cause in causes] + [len(causes)] * len(consequences)
        target = [len(causes)] * len(causes) + [
            len(causes) + 1 + consequences.index(consequence)
            for consequence in consequences]
        link_color = ['#336699'] * len(causes) + ['#0A4D68'] * len(consequences)

        nodes_amount = len(causes) + len(consequences)
        causes_value = [nodes_amount / 2 / len(causes)] * len(causes) if len(causes) != 0 else []
        consequences_value = [nodes_amount / 2 / len(consequences)] * len(consequences) \
            if len(consequences) != 0 else []
        value = causes_value + consequences_value

    risk.set_chart_data(
        labels=labels,
        node_color=node_color,
        source=source,
        target=target,
        value=value,
        link_color=link_color
    )
    return QUrl.fromLocalFile(risk.get_chart_data().name)
