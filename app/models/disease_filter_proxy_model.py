from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex

# class DiseaseFilterProxyModel(QSortFilterProxyModel):
#     def filterAcceptsRow(self, source_row, source_parent):
#         model = self.sourceModel()
#         index = model.index(source_row, 1, source_parent)  # Index for the column with the disease name
#         disease_name = model.data(index)  # Get data (disease name)
#         print(f"Row: {source_row}, Disease name: {disease_name}")
#         return self.filterRegExp().indexIn(disease_name) != -1


from PyQt5.QtCore import QSortFilterProxyModel


class DiseaseFilterProxyModel(QSortFilterProxyModel):
    # def filterAcceptsRow(self, source_row, source_parent):
    #     model = self.sourceModel()
    #     index = model.index(source_row, 1, source_parent)  # Index for the column with the disease code
    #
    #     disease_name = model.data(index)  # Get data (disease code)
    #
    #     # If this disease matches the filter and has no children, accept the row
    #     if self.filterRegExp().indexIn(disease_name) != -1 and not model.hasChildren(index):
    #         return True
    #
    #     # Check if any child matches the filter
    #     else:
    #         if model.hasChildren(index):
    #             for i in range(model.rowCount(index)):
    #                 if self.filterAcceptsRow(i, index):
    #                     return True
    #         return False
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 1, source_parent)  # Index for the column with the disease code

        disease_name = model.data(index)  # Get data (disease code)

        # If this disease matches the filter and has no children, accept the row
        if self.filterRegExp().indexIn(disease_name) != -1 and not model.hasChildren(index):
            return True

        # Check if any child or descendant matches the filter
        for i in range(model.rowCount(index)):
            if self.filterAcceptsRow(i, index):
                return True

        return False

    # def filterAcceptsRow(self, source_row, source_parent):
    #     model = self.sourceModel()
    #     index = model.index(source_row, 1, source_parent)  # Index for the column with the disease code
    #
    #     # If there is no parent, this is the first level - ignore it
    #     if not source_parent.isValid():
    #         return True
    #
    #     disease_name = model.data(index)  # Get data (disease code)
    #
    #     # If this disease matches the filter and has no children, accept the row
    #     if self.filterRegExp().indexIn(disease_name.strip()) != -1 and not model.hasChildren(index):
    #         return True
    #     else:
    #         # If the disease does not match the filter, check its children
    #         # If any child matches the filter, accept the row
    #         if model.hasChildren(index):
    #             for i in range(model.rowCount(index)):
    #                 if self.filterAcceptsRow(i, index):
    #                     return True
    #         # If no child matches, do not accept the row
    #         return False

    # def filterAcceptsRow(self, source_row, source_parent):
    #     model = self.sourceModel()
    #     index = model.index(source_row, 1, source_parent)  # Index for the column with the disease code
    #
    #     disease_name = model.data(index)  # Get data (disease code)
    #
    #     # If this disease matches the filter and has no children, accept the row
    #     if self.filterRegExp().indexIn(disease_name.strip()) != -1 and not model.hasChildren(index):
    #         return True
    #
    #     # Check if any child matches the filter
    #     else:
    #         if model.hasChildren(index):
    #             for i in range(model.rowCount(index)):
    #                 if self.filterAcceptsRow(i, index):
    #                     return True
    #         return False

    # def filterAcceptsRow(self, source_row, source_parent):
    #     model = self.sourceModel()
    #     index = model.index(source_row, 1, source_parent)  # Index for the column with the disease code
    #
    #     disease_name = model.data(index)  # Get data (disease code)
    #
    #     # If this disease matches the filter and has no children, accept the row
    #     if self.filterRegExp().indexIn(disease_name.strip()) != -1 and not model.hasChildren(index):
    #         return True
    #
    #     # Check if any child matches the filter
    #     if model.hasChildren(index):
    #         for i in range(model.rowCount(index)):
    #             if self.filterAcceptsRow(i, index):
    #                 return True
    #
    #     # Check if any first-level item without children matches the filter
    #     if not source_parent.isValid():
    #         for i in range(model.rowCount()):
    #             item_index = model.index(i, 0)
    #             if not model.hasChildren(item_index):
    #                 if self.filterAcceptsRow(i, item_index):
    #                     return False
    #
    #     return True

        # If no child matches and it is an element of the first level, do not accept the row
        # if not source_parent.isValid():
        #     return False

        # If no child matches but it is not an element of the first level, accept the row
        # return True













