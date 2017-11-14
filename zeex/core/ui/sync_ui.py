import os
import subprocess


def normpath(x):
    return os.path.normpath(x).replace("\\", "/")


def sync_ui():
    ui_dir = os.path.dirname(__file__)
    for dirname, subdirs, files in os.walk(ui_dir):
        for f in files:
            if f.endswith('.ui'):
                i_path = os.path.join(dirname, f)
                o_path = os.path.splitext(i_path)[0] + '_ui.py'
                i_path = normpath(i_path)
                o_path = normpath(o_path)
                cmd = "pyside-uic {} -o {}".format(i_path, o_path)
                print(cmd)
                subprocess.call(cmd)



if __name__ == '__main__':
    sync_ui()
