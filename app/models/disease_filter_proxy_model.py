from PyQt5.QtCore import QSortFilterProxyModel


class DiseaseFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        # Создаем QModelIndex для текущей строки
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        # Проверяем, соответствует ли текущая строка фильтру
        if self.row_matches_filter(source_index):
            return True
        # Если текущая строка не соответствует фильтру, проверяем ее потомков
        if self.has_accepted_children(source_index):
            return True
        return False

    def row_matches_filter(self, index):
        """
        Проверяет, соответствует ли текущая строка фильтру.
        Возвращает True, если соответствует, и False в противном случае.
        """
        disease_name = self.sourceModel().data(index)
        filter_text = self.filterRegExp().pattern().lower()
        disease_text = ' '.join(disease_name.split())
        return filter_text.lower() in disease_text.lower()

    def has_accepted_children(self, parent_index):
        """
        Проверяет, есть ли у родителя дочерние элементы, которые соответствуют фильтру.
        Возвращает True, если есть соответствующие дочерние элементы, и False в противном случае.
        """
        # Проверяем, есть ли у родителя дети
        child_count = self.sourceModel().rowCount(parent_index)
        for i in range(child_count):
            # Создаем QModelIndex для каждого ребенка
            child_index = self.sourceModel().index(i, 1, parent_index)
            # Проверяем, соответствует ли ребенок фильтру
            if self.row_matches_filter(child_index):
                return True
            # Если текущий ребенок не соответствует фильтру, проверяем его потомков
            if self.has_accepted_children(child_index):
                return True
        return False
