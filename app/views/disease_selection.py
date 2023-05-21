from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QTreeView
from app.utils.db.models import Disease
from app.utils.db.session import get_session
from app.widgets.search_line_edit import SearchLineEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Модуль управления рисками бронхолегочных заболеваний')
        self.setMinimumSize(1080, 720)
        self.setStyleSheet("background-color: rgb(245, 245, 245);")
        self.showMaximized()

        central_widget = QWidget()
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
        input_disease_tbx = SearchLineEdit()
        input_disease_tbx.setPlaceholderText('Поиск по названию болезни')
        input_disease_tbx.setFixedHeight(40)
        input_disease_tbx.setFixedWidth(540)
        input_disease_tbx.setStyleSheet(
            """
            SearchLineEdit {
                border: 1px solid #000;
                border-radius: 20px;
                background-color: #E0E0E0;
                padding-left: 10px;
                font-size: 16px;
            }
            """
        )
        h_layout = QHBoxLayout()
        h_layout.addWidget(input_disease_tbx, 0, Qt.AlignCenter)
        vertical_layout.addLayout(h_layout)
        vertical_layout.addWidget(input_disease_tbx)

        vertical_layout.addWidget(self.create_tree_view_widget())

        central_widget.setLayout(vertical_layout)
        self.setCentralWidget(central_widget)

    def create_tree_view_widget(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Код', 'Заболевание'])

        session = get_session()
        diseases = session.query(Disease).all()  # Загружаем все заболевания из БД

        # Словарь для хранения родительских элементов по id
        parents = {None: model}

        # Словарь для хранения диапазонов кодов и соответствующих заболеваний
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
            model.appendRow([category_item, QStandardItem(category_name)])

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

        # Создаем виджет дерева и устанавливаем модель для него
        tree = QTreeView()
        tree.setModel(model)

        font = QFont()
        font.setPointSize(14)
        tree.setFont(font)
        tree.show()
        return tree






