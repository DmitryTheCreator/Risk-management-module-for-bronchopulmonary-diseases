from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton
from app.models.disease_filter_proxy_model import DiseaseFilterProxyModel
from app.utils.db.models import Disease
from app.utils.db.session import get_session
from app.widgets.search_line_edit import SearchLineEdit


class RiskSelectionView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Новое содержимое")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        vertical_layout = QVBoxLayout()
        vertical_layout.setContentsMargins(200, 20, 200, 20)
        header = QLabel('Болезни органов дыхания')
        header.setStyleSheet('font: 30pt \"MS Sans Serif\";')
        header.setAlignment(Qt.AlignCenter)
        vertical_layout.addWidget(header)
        central_widget.setLayout(vertical_layout)
        self.setLayout(vertical_layout)
