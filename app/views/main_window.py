from PyQt5.QtWidgets import QMainWindow
from app.models.risk_analysis_data import RiskAnalysisData
from app.views.pages.bayesian_network import BayesianNetworkView
from app.views.pages.bow_tie_chart import BowTieChartView
from app.views.pages.disease_selection import DiseaseSelectionView
from app.views.pages.risk_map import RiskMapView
from app.views.pages.risk_selection import RiskSelectionView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.risk_analysis_data = RiskAnalysisData()
        # Отображение страницы выбора заболевания при запуске приложения
        self.show_disease_selection_page()
        # self.show_risk_map_page()
        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self):
        # Настройка основного окна приложения
        self.setWindowTitle('Модуль управления рисками бронхолегочных заболеваний')
        self.setMinimumSize(1080, 720)
        self.setStyleSheet("background-color: rgb(245, 245, 245);")
        self.showMaximized()

    def show_disease_selection_page(self):
        # Создание экземпляра виджета выбора заболевания
        disease_selection = DiseaseSelectionView(self.risk_analysis_data)
        disease_selection.goToRiskPageSignal.connect(self.show_risk_selection_page)
        # Установка виджета выбора заболевания в центральную область главного окна
        self.setCentralWidget(disease_selection)

    def show_risk_selection_page(self):
        # Создание экземпляра виджета выбора рисков
        risk_selection = RiskSelectionView(self.risk_analysis_data)
        risk_selection.goToDiseasePageSignal.connect(self.show_disease_selection_page)
        risk_selection.goToBowChartPageSignal.connect(self.show_bow_tie_chart_page)
        # Установка виджета выбора рисков в центральную область главного окна
        self.setCentralWidget(risk_selection)

    def show_bow_tie_chart_page(self):
        # Создание экземпляра виджета выбора рисков
        bow_tie_chart = BowTieChartView(self.risk_analysis_data)
        bow_tie_chart.goToRiskPageSignal.connect(self.show_risk_selection_page)
        bow_tie_chart.goToBayesianNetworkPageSignal.connect(self.show_bayesian_network_page)
        # Установка виджета выбора рисков в центральную область главного окна
        self.setCentralWidget(bow_tie_chart)

    def show_bayesian_network_page(self):
        # Создание экземпляра виджета байесовских сетей
        bayesian_network = BayesianNetworkView(self.risk_analysis_data)
        bayesian_network.goToBowChartPageSignal.connect(self.show_bow_tie_chart_page)
        bayesian_network.goToRiskMapPageSignal.connect(self.show_risk_map_page)
        # Установка виджета выбора рисков в центральную область главного окна
        self.setCentralWidget(bayesian_network)

    def show_risk_map_page(self):
        risk_map = RiskMapView(self.risk_analysis_data)
        self.setCentralWidget(risk_map)
