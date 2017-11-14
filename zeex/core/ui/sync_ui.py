import os
import subprocess


def sync_ui(ui_dir=None):
    """
    Helper function calls the pyside-uic {file.ui} -o {file_ui.py}
    on each recently modified .ui file in the :param ui_dir.

    Each .py file generated gets 'import icons_rc' replaced
    with 'from zeex.icons import icons_rc' to prevent import errors
    when the program runs.

    :param ui_dir: (str)
        The name of the directory to scan for .ui files.

    :return: None
    """
    if ui_dir is None:
        ui_dir = os.path.dirname(__file__)

    for dirname, subdirs, files in os.walk(ui_dir):
        for f in files:
            if not f.endswith('.ui'):
                continue

            i_path = os.path.join(dirname, f)
            o_path = os.path.splitext(i_path)[0] + '_ui.py'

            # Ensure .ui file was modified.
            if os.path.exists(o_path):
                i_mod = os.path.getmtime(i_path)
                o_mod = os.path.getmtime(o_path)
                if i_mod <= o_mod:
                    continue

            i_path = os.path.normpath(i_path).replace("\\", "/")
            o_path = os.path.normpath(o_path).replace("\\", "/")

            # Do pyside file conversion call
            cmd = 'pyside-uic "{}" -o "{}"'.format(i_path, o_path)
            subprocess.call(cmd)

            # Swap out icons_rc import statement if needed.
            with open(o_path, mode='r') as fh:
                lines = fh.readlines()

            if 'import icons_rc' in lines[-1] \
                    and 'zeex' not in lines[-1]:
                lines[-1] = 'from zeex.icons import icons_rc'
                with open(o_path, mode='w') as fh:
                    fh.writelines(lines)
            print("Synced {}".format(os.path.basename(o_path)))

if __name__ == '__main__':
    sync_ui()
