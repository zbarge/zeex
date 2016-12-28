import os
import dropbox
import dropbox.exceptions as exceptions
from core.compat import QtCore, QtGui
from collections import defaultdict

class QtDropBox(QtCore.QObject):
    """
    A utility for the DropBox SDK.
    """
    FOLDER_CONFIG = "/config"
    FOLDER_ARCHIVE = "/archive"
    FOLDER_SHARE = "/share"
    FOLDERS_DEFAULT = [FOLDER_CONFIG, FOLDER_ARCHIVE, FOLDER_SHARE]

    def __init__(self, *args, **kwargs):
        QtCore.QObject.__init__(self)
        if args:
            key = args[0]
        else:
            try:
                key = os.environ['DROPBOX_ACCESS_TOKEN']
            except KeyError:
                raise KeyError("You must create an environment variable\
                named 'DROPBOX_ACCESS_TOKEN' to initialize DropBoxManager.")
        self.con = dropbox.Dropbox(key, **kwargs)
        self.fs_model = DropBoxFileSystemModel()

    def crawl_folders(self):
        return self.con.files_list_folder("", recursive=True)

    def create_folder(self, *args, raise_on_error=False, **kwargs):
        try:
            res = self.con.files_create_folder(*args, **kwargs)
        except exceptions.ApiError:
            if raise_on_error:
                raise
            res = None
        return res

    def get_folders_dict(self):
        folders = self.crawl_folders()
        return {f.path_lower: f for f in folders.entries}

    def _create_default_folders(self):
        [self.create_folder(f)
         for f in self.FOLDERS_DEFAULT]

    def get_filesystem_model(self, update=False):
        if self.fs_model.rowCount() == 0 or update:
            self.fs_model.set_folders(self.crawl_folders(), clear=update)

        return self.fs_model

    def upload_file(self, filepath, to_folder, **kwargs):
        filename = os.path.basename(filepath)
        new_name = os.path.join(to_folder, filename).replace("\\", "/")
        with open(filepath, "rb") as fp:
            res = self.con.files_upload(fp.read(), new_name, **kwargs)
        return res

    def download_file(self, from_path, to_path, **kwargs):
        self.con.files_download_to_file(to_path, from_path, **kwargs)


class DropBoxFileSystemModel(QtGui.QStandardItemModel):
    def __init__(self):
        QtGui.QStandardItemModel.__init__(self)


    def set_folders(self, metadata, clear=True):
        if clear:
            self.clear()
        self.setHorizontalHeaderLabels(['folders/files'])
        data = defaultdict(list)
        for entry in metadata.entries:
            if '.' in entry.path_lower[-5:]:
                dirname = os.path.dirname(entry.path_lower)
                filename = os.path.basename(entry.path_lower)
            else:
                dirname = entry.path_lower
                filename = None
            data[dirname].append(filename)

        for dirname, files in sorted(data.items()):
            d = QtGui.QStandardItem(dirname)
            d.setEditable(False)
            files = [f for f in files if f]
            for f in files:
                f = QtGui.QStandardItem(f)
                f.setEditable(False)
                d.appendRow(f)
            self.appendRow(d)

    def filePath(self, idx):
        filename = self.itemFromIndex(idx).text()
        try:
            filename = self.itemFromIndex(idx.parent()).text() + "/" + filename
        except AttributeError:
            pass
        return filename

    def directory(self, idx):
        return self.itemFromIndex(idx).text()














if __name__ == '__main__':
    dbm = QtDropBox()

    res = dbm.upload_file(r"C:\Zeex Projects\test_project2\FL_insurance_sample.csv.zip", dbm.FOLDER_ARCHIVE, autorename=True)
    print(res)
    model = dbm.get_filesystem_model(update=True)
