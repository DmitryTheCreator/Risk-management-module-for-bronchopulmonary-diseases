from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QToolButton, QHBoxLayout


class SearchLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__(parent)

        self.button = QToolButton(self)
        self.button.setFixedSize(24, 24)
        self.button.setIcon(QIcon('app/resources/icons/search.png'))
        self.button.setStyleSheet('border: none;')
        self.button.setCursor(Qt.ArrowCursor)
        self.button.clicked.connect(self.button_clicked)

        layout = QHBoxLayout(self)
        layout.addWidget(self.button, 0, Qt.AlignRight)
        layout.setContentsMargins(0, 0, 20, 0)
        layout.setSpacing(0)

        self.setPlaceholderText('Поиск по названию болезни')
        self.setFixedHeight(40)
        self.setFixedWidth(540)

        self.setStyleSheet(
            """
            QLineEdit {{
                border: 1px solid #000;
                border-radius: 20px;
                background-color: #E0E0E0;
                padding-left: 10px;
                padding-right: {}px;
                font-size: 16px;
                overflow: hidden;
            }}
            """.format(self.button.width() + 10)
        )
        self.setTextMargins(0, 0, self.button.width() + 30, 0)

    def button_clicked(self):
        # Получите текущий текст из SearchLineEdit
        search_text = self.text()

        print("search_text:", search_text)
        print("type of search_text:", type(search_text))

        # Получите ссылку на главное окно
        main_window = self.window()

        # Вызовите функцию поиска с search_text
        main_window.search_diseases(search_text)

    def set_button_visible(self, visible):
        self.button.setVisible(visible)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.button.setIconSize(self.button.size())
