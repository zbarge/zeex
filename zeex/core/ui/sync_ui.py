import os
import logging
import subprocess

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

ICONS_SOURCE_QRC = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))),
    'icons', 'icons.qrc').replace("\\", "/")
ICONS_SOURCE_PY = "{}_rc.py".format(
    os.path.splitext(ICONS_SOURCE_QRC)[0])\
    .replace("\\", '/')


def sync_ui(ui_dir=None, icons_src_qrc=None, icon_import_base='zeex.icons'):
    """
    Helper function calls the pyside-uic {file.ui} -o {file_ui.py}
    on each recently modified .ui file in the :param ui_dir.

    Each .py file generated gets 'import icons_rc' replaced
    with 'from zeex.icons import icons_rc' to prevent import errors
    when the program runs.

    :param ui_dir: (str)
        The name of the directory to scan for .ui files.

    :param icons_src_qrc (str, default None)
        The path to the icons.qrc file to sync.

    :param icon_import_base (str, default 'zeex.icons')
        The name of the package where the icons module will be found.
        This is used to replace the icons import statement.
        None will leave the import statement as is.

    :return: None
    """
    if ui_dir is None:
        ui_dir = os.path.dirname(__file__)

    if icons_src_qrc is None:
        icons_src_qrc = ICONS_SOURCE_QRC
        icons_src_py = ICONS_SOURCE_PY
    else:
        icons_src_qrc = icons_src_qrc.replace("\\", "/")
        icons_src_py = "{}_rc.py".format(
            os.path.splitext(icons_src_qrc)[0]
        ).replace("\\", "/")

    icons_module = os.path.splitext(os.path.basename(icons_src_py))[0]

    log.debug("UI files directory: {}".format(ui_dir))
    log.debug("Icons source path: {}".format(icons_src_qrc))

    synced = list()

    for dirname, subdirs, files in os.walk(ui_dir):
        for f in files:
            if not f.endswith('.ui'):
                log.debug("Skipping {}".format(f))
                continue

            i_path = os.path.join(dirname, f)
            o_path = os.path.splitext(i_path)[0] + '_ui.py'

            # Ensure .ui file was modified.
            if os.path.exists(o_path):
                i_mod = os.path.getmtime(i_path)
                o_mod = os.path.getmtime(o_path)
                if i_mod <= o_mod:
                    log.debug("Skipping {}".format(f))
                    continue

            i_path = os.path.normpath(i_path).replace("\\", "/")
            o_path = os.path.normpath(o_path).replace("\\", "/")

            # Do pyside file conversion call
            cmd = 'pyside-uic "{}" -o "{}"'.format(
                i_path, o_path)
            log.debug(cmd)
            subprocess.call(cmd)

            # Swap out icons import statement if needed.
            with open(o_path, mode='r') as fh:
                lines = fh.readlines()

            if icon_import_base is not None \
                    and 'import {}'.format(icons_module) in lines[-1] \
                    and icon_import_base not in lines[-1]:

                lines[-1] = 'from {} import {}'.format(
                    icon_import_base, icons_module)

                with open(o_path, mode='w') as fh:
                    fh.writelines(lines)

            synced.append(o_path)
            log.info("Synced {}".format(os.path.basename(o_path)))

    # refresh icons.qrc
    if os.path.exists(icons_src_qrc):
        cmd = 'pyside-rcc -py3 "{}" -o "{}"'.format(
            icons_src_qrc, icons_src_py)

        # change if modified
        if os.path.exists(icons_src_py):
            i_mod = os.path.getmtime(icons_src_qrc)
            o_mod = os.path.getmtime(icons_src_py)
            if i_mod >= o_mod:
                log.debug(cmd)
                subprocess.call(cmd)
                log.info("Synced {}".format(os.path.basename(icons_src_py)))
                synced.append(icons_src_py)
            else:
                log.debug("Skipping file {}".format(icons_src_py))
        else:
            log.debug(cmd)
            subprocess.call(cmd)
            log.info("Generated {}".format(os.path.basename(icons_src_py)))
            synced.append(icons_src_py)

    log.debug("Sync complete. Files changed {}".format(len(synced)))
    return synced








if __name__ == '__main__':
    sync_ui()
