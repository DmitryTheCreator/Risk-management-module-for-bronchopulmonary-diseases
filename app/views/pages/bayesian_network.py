import networkx as nx
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class BayesianNetworkView(QWidget):
    def __init__(self, risk_analysis_data):
        super().__init__()
        fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(fig)
        self.ax1 = fig.add_subplot(211)  # Сеть причин
        self.ax2 = fig.add_subplot(212)  # Сеть последствий
        self.risk_analysis_data = risk_analysis_data  # Данные анализа рисков
        self.init_ui()  # Инициализация пользовательского интерфейса

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.canvas)

        g_cause = nx.DiGraph()
        g_consequence = nx.DiGraph()
        for risk in self.risk_analysis_data.get_selected_risks():
            for cause in risk.get_causes():
                g_cause.add_edge(cause, risk.get_name())
            for consequence in risk.get_consequences():
                g_consequence.add_edge(risk.get_name(), consequence)

        pos_cause = set_node_positions(g_cause, 0)
        pos_consequence = set_node_positions(g_consequence, 1)
        nx.draw(g_cause, pos_cause, with_labels=True, ax=self.ax1)
        nx.draw(g_consequence, pos_consequence, with_labels=True, ax=self.ax2)


def set_node_positions(graph, root_node_y):
    pos = {}
    root_nodes = [node for node, in_degree in graph.in_degree() if in_degree == 0]
    leaf_nodes = [node for node, out_degree in graph.out_degree() if out_degree == 0]

    for i, node in enumerate(root_nodes):
        pos[node] = [i, root_node_y]

    leaf_node_y = root_node_y + 1 if root_node_y < 0.5 else root_node_y - 1
    for i, node in enumerate(leaf_nodes):
        pos[node] = [i, leaf_node_y]
    return pos
