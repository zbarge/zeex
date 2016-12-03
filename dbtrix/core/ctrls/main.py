from PySide import QtGui

class MainController(object):

    def __init__(self, model):
        self.model = model

    # called from view class
    def change_running(self, checked):
        # put control logic here
        self.model.running = checked
        self.model.announce_update()