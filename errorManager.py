import gtk, sys, traceback
from tools import label_set_autowrap

ERROR = 0x00
WARNING = 0x01
NOTIFY = 0x02

class ErrorManager:
    def __init__(self):
        self.gui = gtk.Builder()
        self.gui.add_from_file('errormanager.glade')
        self.gui.connect_signals({
                "hideWin" : self.hide,
                "selectRow" : self.selectRow
                })
        label_set_autowrap(self.gui.get_object('label3'))
        self.errorList = []

    def show(self):
        errorstore = self.gui.get_object('liststore1')
        errorstore.clear()
        for x in self.errorList:
            if x[0] == 0x00:
                pixbuf = gtk.gdk.pixbuf_new_from_file('error.png')
            elif x[0] == 0x01:
                pixbuf = gtk.gdk.pixbuf_new_from_file('warning.png')
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file('info.png')
            errorstore.append([pixbuf, x[1], x[2]])
        self.gui.get_object('errorm').show()

    def hide(self, obj, event=None):
        self.gui.get_object('errorm').hide()
        return True

    def selectRow(self, obj, event=None):
        treeselection = self.gui.get_object('treeview2').get_selection()
        (model, iter) = treeselection.get_selected()
        self.gui.get_object('label3').set_text(model[iter][2])

    def debug(self, message):
        self.errorList.append([0x01, message, ''])

    def exception(self):
        error_type, error_value, trbk = sys.exc_info()
        tb_list = traceback.format_tb(trbk, 3)
        info_list = ["Error: %s \nDescription: %s \nTraceback:\n" % (error_type.__name__, error_value), ]
        info_list.extend(tb_list)
        details = ''.join(info_list)
        self.errorList.append([0x00, error_type.__name__, details])

    def _error(self, tip, msg, tb):
        tb_list = traceback.format_tb(tb, 3)
        details = ''.join(tb_list)
        self.errorList.append([0x00, tip.__name__ + ': ' + str(msg), details])
        return True
