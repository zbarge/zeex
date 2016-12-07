from PySide import QtGui


class Model(object):
    def __init__(self):
        self._update_funcs = []

        # variable placeholders
        self.running = False

    # subscribe a view method for updating
    def subscribe_update_func(self, func):
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    # unsubscribe a view method for updating
    def unsubscribe_update_func(self, func):
        if func in self._update_funcs:
            self._update_funcs.remove(func)

    # update registered view methods
    def announce_update(self):
        for func in self._update_funcs:
            func()

            
class FieldsListModel(QtGui.QStandardItemModel):
    def __init__(self,  items=None):
        super(FieldsListModel, self).__init__()
        if items:
            for item in items:
                item = QtGui.QStandardItem(item)
                self.appendRow(item)

    def get_data_list(self):
        return [item.text()
                for item
                in [self.item(i) for i in range(self.rowCount())]]


        
        