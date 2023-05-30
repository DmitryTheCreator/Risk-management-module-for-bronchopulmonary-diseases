class RiskAnalysisData:
    def __init__(self):
        self._disease = None
        self._selected_risks = []

    def set_disease_name(self, name):
        self._disease = name

    def get_disease_name(self):
        return self._disease

    def add_risk(self, risk):
        self._selected_risks.append(risk)

    def remove_risk(self, risk):
        self._selected_risks.remove(risk)

    def get_selected_risks(self):
        return self._selected_risks

    def get_risk_by_id(self, received_id):
        for risk_id in range(len(self._selected_risks)):
            if risk_id == int(received_id):
                return self._selected_risks[risk_id]
        return None
