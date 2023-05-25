from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QLineEdit
from app.models.disease_filter_proxy_model import DiseaseFilterProxyModel
from app.utils.db.models import Disease
from app.utils.db.session import get_session


class DiseaseSelectionView(QWidget):
    # Сигнал, отправляемый при переходе к странице анализа рисков
    goToRiskPageSignal = pyqtSignal()

    def __init__(self, risk_analysis_data):
        super().__init__()
        self.input_disease_tbx = QLineEdit()  # Поле ввода для поиска болезни
        self.model = QStandardItemModel()  # Модель данных для отображения в QTreeView
        self.tree = QTreeView()  # Виджет дерева для отображения списка болезней
        self.disease_filter_proxy_model = DiseaseFilterProxyModel()  # Прокси-модель для фильтрации данных
        self.next_btn = QPushButton('Далее')  # Кнопка "Далее" для перехода к следующей странице
        self.risk_analysis_data = risk_analysis_data  # Данные анализа рисков
        self.init_ui()  # Инициализация пользовательского интерфейса

    def init_ui(self):
        vertical_layout = QVBoxLayout()
        vertical_layout.setContentsMargins(200, 20, 200, 20)

        header = QLabel('Болезни органов дыхания')
        header.setStyleSheet('font: 30pt \"MS Sans Serif\";')
        header.setAlignment(Qt.AlignCenter)
        vertical_layout.addWidget(header)

        header = QLabel('Согласно Международной классификации болезней МКБ-10')
        header.setStyleSheet('color: rgb(118, 118, 118); font: 14pt; MS Sans Serif;')
        header.setAlignment(Qt.AlignCenter)
        vertical_layout.addWidget(header)
        vertical_layout.addSpacing(20)
        self.input_disease_tbx.setPlaceholderText('Поиск по названию болезни')
        self.input_disease_tbx.setFixedHeight(40)
        self.input_disease_tbx.setFixedWidth(540)
        self.input_disease_tbx.setStyleSheet(
            """
                border: 1px solid #000;
                border-radius: 20px;
                background-color: #E0E0E0;
                padding-left: 10px;
                font-size: 16px;
            """
        )
        # Подключение слота для обработки изменений в поле ввода
        self.input_disease_tbx.textChanged.connect(self.search_diseases)
        # Подключение слота для обработки нажатия на кнопку "Далее"
        self.next_btn.clicked.connect(self.to_risk_register_page)
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet('background-color: #E0E0E0;')
        self.next_btn.setFixedWidth(300)
        self.next_btn.setFixedHeight(30)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.input_disease_tbx, alignment=Qt.AlignCenter)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addSpacing(20)
        header = QLabel('Выберите заболевание для анализа рисков')
        header.setStyleSheet('font: 16pt \"MS Sans Serif\";')
        header.setAlignment(Qt.AlignCenter)
        vertical_layout.addWidget(header)
        vertical_layout.addWidget(self.create_tree_view_widget())

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.next_btn, alignment=Qt.AlignCenter)
        vertical_layout.addLayout(horizontal_layout)
        self.setLayout(vertical_layout)

    def create_tree_view_widget(self):
        self.model.setHorizontalHeaderLabels(['Код', 'Заболевание'])  # Установка заголовков столбцов модели
        session = get_session()
        diseases = session.query(Disease).all()  # Запрос всех болезней из базы данных
        parents = {None: self.model}  # Словарь для хранения родительских элементов

        disease_categories = {
            'J00-J06': (QStandardItem('J00-J06'), 'Острые респираторные инфекции верхних дыхательных путей'),
            'J10-J18': (QStandardItem('J10-J18'), 'Грипп и пневмония'),
            'J20-J22': (QStandardItem('J20-J22'), 'Другие острые респираторные инфекции нижних дыхательных путей'),
            'J30-J39': (QStandardItem('J30-J39'), 'Другие болезни верхних дыхательных путей'),
            'J40-J47': (QStandardItem('J40-J47'), 'Хронические болезни нижних дыхательных путей'),
            'J60-J70': (QStandardItem('J60-J70'), 'Болезни легкого, вызванные внешними агентами'),
            'J80-J84': (QStandardItem('J80-J84'),
                        'Другие респираторные болезни, поражающие главным образом интерстициальную ткань'),
            'J85-J86': (QStandardItem('J85-J86'), 'Гнойные и некротические состояния нижних дыхательных путей'),
            'J90-J94': (QStandardItem('J90-J94'), 'Другие болезни плевры'),
            'J95-J99': (QStandardItem('J95-J99'), 'Другие болезни органов дыхания')
        }

        # Создаем основные родительские элементы для каждой категории
        for _, (category_item, category_name) in disease_categories.items():
            self.model.appendRow([category_item, QStandardItem(category_name)])

        # Сначала добавляем все болезни, которые являются родительскими элементами
        for disease in diseases:
            if disease.parent_id is None:
                for category, (category_item, _) in disease_categories.items():
                    start, end = category.split('-')
                    if int(disease.code[1:]) in range(int(start[1:]), int(end[1:]) + 1):
                        disease_item = QStandardItem(disease.code)
                        disease_name_text = f'\t{disease.name}'
                        category_item.appendRow([disease_item, QStandardItem(disease_name_text)])
                        parents[disease.id] = disease_item

        # Затем добавляем подкатегории
        for disease in diseases:
            if disease.parent_id is not None:
                parent_item = parents[disease.parent_id]
                disease_item = QStandardItem(disease.code)
                disease_name_text = f'\t\t{disease.name}'
                parent_item.appendRow([disease_item, QStandardItem(disease_name_text)])

        self.disease_filter_proxy_model.setSourceModel(self.model)
        # Установка модели данных для виджета QTreeView
        self.tree.setModel(self.disease_filter_proxy_model)

        font = QFont()
        font.setPointSize(14)
        self.tree.setFont(font)
        self.tree.setColumnWidth(0, 120)  # Устанавливаем ширину колонки "Код" (индекс 0) на 100 пикселей
        self.tree.setStyleSheet('QTreeView::item:selected { color: white; background-color: #27374D; }')
        self.tree.show()
        self.tree.selectionModel().selectionChanged.connect(self.update_next_button_state)
        return self.tree

    def search_diseases(self, search_text):
        # Проверяем, что строка поиска не пустая, перед продолжением
        if search_text:
            # Установка фильтра на прокси-модель с помощью регулярного выражения
            self.disease_filter_proxy_model.setFilterRegExp(QRegExp(search_text, Qt.CaseInsensitive))
        else:
            # Если строка поиска пустая, сбрасываем фильтр
            self.disease_filter_proxy_model.setFilterRegExp(QRegExp())

    def update_next_button_state(self):
        # Получаем выбранные индексы
        selected_indexes = self.tree.selectionModel().selectedIndexes()

        # Проверяем, выбран ли хотя бы один элемент
        if selected_indexes:
            # Получаем индекс первого выбранного элемента
            index = selected_indexes[0]

            # Отображаем индекс прокси-модели на исходный индекс
            source_index = self.disease_filter_proxy_model.mapToSource(index)

            # Получаем элемент модели, соответствующий исходному индексу
            item = self.model.itemFromIndex(source_index)

            # Проверяем, что выбранный элемент не имеет дочерних элементов
            if item and item.hasChildren() is False:
                self.risk_analysis_data.disease = ' '.join(source_index.siblingAtColumn(1).data().split())
                # Отключаем кнопку "Далее"
                self.next_btn.setEnabled(True)
            else:
                # Отключаем кнопку "Далее"
                self.next_btn.setEnabled(False)
        else:
            # Отключаем кнопку "Далее"
            self.next_btn.setEnabled(False)

    def to_risk_register_page(self):
        # Испускаем сигнал для перехода к странице анализа рисков
        self.goToRiskPageSignal.emit()
