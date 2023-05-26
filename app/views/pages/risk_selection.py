from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QApplication, QPushButton, QHBoxLayout, \
    QSizePolicy
from sqlalchemy.orm import joinedload
from app.utils.db.models import Disease, DiseaseRisk
from app.utils.db.session import get_session


class RiskSelectionView(QWidget):
    # Сигнал, отправляемый при переходе к странице анализа рисков
    goToDiseasePageSignal = pyqtSignal()
    # Сигнал, отправляемый при переходе к странице с определением причин и последствий для каждого риска
    goToBowChartPageSignal = pyqtSignal()

    def __init__(self, risk_analysis_data):
        super().__init__()
        self.next_button = QPushButton('Далее')  # Кнопка "Далее" для перехода к следующей странице
        self.back_button = QPushButton('Назад')  # Кнопка "Назад" для перехода на предыдущую страницу
        self.selected_risks = set()  # Множество выбранных рисков
        self.risk_analysis_data = risk_analysis_data  # Данные анализа рисков
        self.init_ui()  # Инициализация пользовательского интерфейса

    def init_ui(self):
        vertical_layout = QVBoxLayout()
        vertical_layout.setContentsMargins(200, 20, 200, 20)
        vertical_layout.setSpacing(10)

        header_text = 'Выберите риски, которые можно оценить количественно'
        header = QLabel(header_text)
        header.setWordWrap(True)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('font: 24pt "MS Sans Serif";')
        vertical_layout.addWidget(header)

        disease_name = self.risk_analysis_data.disease
        disease_label = QLabel(f'для заболевания: "{disease_name}"')
        disease_label.setWordWrap(True)  # Включаем перенос слов
        disease_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        disease_label.setStyleSheet('color: rgb(118, 118, 118); font: 16pt "MS Sans Serif";')
        vertical_layout.addWidget(disease_label)
        vertical_layout.addStretch()

        vertical_layout.addLayout(self.create_grid_widget(disease_name))
        vertical_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button, alignment=Qt.AlignBottom | Qt.AlignLeft)
        button_layout.addStretch(1)
        button_layout.addWidget(self.next_button, alignment=Qt.AlignBottom | Qt.AlignRight)
        vertical_layout.addLayout(button_layout)

        self.back_button.setStyleSheet('background-color: #E0E0E0; font-size: 12pt; height: 30px; width: 300px')
        self.next_button.setStyleSheet('background-color: #E0E0E0; font-size: 12pt; height: 30px; width: 300px')
        self.next_button.setEnabled(False)

        self.back_button.clicked.connect(self.on_back_button_clicked)
        self.next_button.clicked.connect(self.on_next_button_clicked)

        self.setLayout(vertical_layout)

    def create_grid_widget(self, disease_name):
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(20)

        disease_id = get_disease_id(disease_name)  # Получение идентификатора заболевания из базы данных
        risk_labels = get_risks_for_disease(disease_id)  # Получение списка рисков для заболевания

        row = 0
        column = 0

        for risk_label in risk_labels:
            risk_label_widget = QLabel(risk_label)
            risk_label_widget.setFixedHeight(100)
            risk_label_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            risk_label_widget.setWordWrap(True)
            risk_label_widget.setStyleSheet(
                """
                QLabel {
                    font-size: 12pt;
                    background-color: #E0E0E0;
                    border: 1px solid #CCCCCC;
                    padding: 10px;
                    word-wrap: break-word;
                }
                """
            )
            risk_label_widget.setAlignment(Qt.AlignCenter)
            risk_label_widget.mousePressEvent = lambda event: self.on_cell_clicked(event)  # Обработка события клика

            grid_layout.addWidget(risk_label_widget, row, column)

            column += 1
            if column == 3:
                column = 0
                row += 1
        return grid_layout

    def on_cell_clicked(self, event):
        risk_label_widget = QApplication.widgetAt(event.globalX(), event.globalY())
        if risk_label_widget in self.selected_risks:
            # Если ячейка уже выбрана, снимаем выделение
            risk_label_widget.setStyleSheet(
                """
                QLabel {
                    font-size: 12pt;
                    background-color: #E0E0E0;
                    border: 1px solid #CCCCCC;
                    padding: 10px;
                    word-wrap: break-word;
                }
                """
            )
            self.selected_risks.remove(risk_label_widget)
        else:
            # Иначе, выделяем ячейку
            risk_label_widget.setStyleSheet(
                """
                QLabel {
                    font-size: 12pt;
                    background-color: #27374D;
                    border: 1px solid #CCCCCC;
                    padding: 10px;
                    color: white;
                    word-wrap: break-word;
                }
                """
            )
            self.selected_risks.add(risk_label_widget)

        self.next_button.setEnabled(len(self.selected_risks) > 0)

    def on_next_button_clicked(self):
        if len(self.selected_risks) > 0:
            self.risk_analysis_data.selected_risk = [label.text() for label in self.selected_risks]
            self.goToBowChartPageSignal.emit()

    def on_back_button_clicked(self):
        self.goToDiseasePageSignal.emit()


# Вспомогательные функции для получения идентификатора заболевания и списка рисков из базы данных
def get_disease_id(disease_name):
    session = get_session()

    disease = session.query(Disease).filter(Disease.name == disease_name).first()

    if disease:
        return disease.id
    else:
        return None


def get_risks_for_disease(disease_id):
    session = get_session()

    disease_risks = session.query(DiseaseRisk).options(joinedload(DiseaseRisk.risk)). \
        filter(DiseaseRisk.disease_id == disease_id).all()

    if disease_risks:
        return [risk_item.risk.name for risk_item in disease_risks]
    else:
        return []
