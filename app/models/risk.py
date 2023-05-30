import tempfile
import plotly.graph_objects as go


class Risk:
    def __init__(self, name):
        self._name = name
        self._causes = []
        self._consequences = []
        self.is_enable = False
        self._chart_data = None

    def get_name(self):
        return self._name

    def add_cause(self, cause):
        self._causes.append(cause)

    def remove_cause(self, cause):
        self._causes.remove(cause)

    def get_causes(self):
        return self._causes

    def add_consequence(self, consequence):
        self._consequences.append(consequence)

    def remove_consequence(self, consequence):
        self._consequences.remove(consequence)

    def get_consequences(self):
        return self._consequences

    def get_enable_state(self):
        return self.is_enable

    def set_enable_state(self):
        self.is_enable = True

    def get_chart_data(self):
        return self._chart_data

    def set_chart_data(self, labels, node_color, source, target, value, link_color):
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=100,
                thickness=100,
                line=dict(color="black", width=0.5),
                label=labels,
                color=node_color
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_color
            )
        )])
        fig.update_layout(font=dict(size=20), autosize=True)
        self._chart_data = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        fig.write_html(self._chart_data.name, config={
            'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'toImage'],
            'displaylogo': False
        })
