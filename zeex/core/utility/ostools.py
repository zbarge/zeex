# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 00:03:14 2016
MIT License

Copyright (c) 2016 Zeke Barge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import zipfile
import shutil
try:
    import zlib
    DEFAULT_COMPRESSION = zipfile.ZIP_DEFLATED
except ImportError:
    DEFAULT_COMPRESSION = zipfile.ZIP_STORED


def path_incremented(p, overwrite=False):
    """
    Increments a file path so you don't overwrite
    an existing file (unless you choose to).
    :param p: (str)
        The file path to possibly increment
    :param overwrite: (str)
        True will just increment once and return the path.
        False will keep incrementing until the path is available
    :return:
        The original file path if it doesn't exist.
        The file path incremented by 1 until it doesn't exist.
    """
    dirname = os.path.dirname(p)
    error = 2
    while os.path.exists(p):
        name = os.path.basename(p)
        name, ext = os.path.splitext(name)

        try:
            val = ''.join(e for e in str(name)[-3:] if e.isdigit())
            count = int(val) + 1
            name = name.replace(val, str(count))
            if str(count) not in name:
                name = "{}{}".format(name, count)
        except ValueError:
            name = "{}{}".format(name, error)
            error += 1
        p = os.path.join(dirname, name + ext)
        if overwrite is True or error > 2500:
            break
    return p


def zipfile_write(filepath, to=None, **kwargs):
    """
    Thin layer over zipfile.ZipFile.write

    :param filepath: (str)
        The filepath to compress
    :param to: (str, default None)
        If None, the filepath is used ensuring the extension is .zip
    :param mode: (str)
        'w', 'a' (Invalid options default to 'a')
    :return: (str)
        The to path after doing the compression.
    """
    if to is None:
        to = os.path.splitext(filepath)[0] + ".zip"
    elif to.lower().endswith(".zip"):
        pass
    if filepath.lower() == to.lower():
        return to


    mode = kwargs.pop('mode', 'a')
    if not mode in ['a', 'w']:
        mode = 'a'
    kwargs['mode'] = mode

    with zipfile.ZipFile(to, **kwargs) as fh:
        fh.write(filepath, compress_type=kwargs.get('compression', DEFAULT_COMPRESSION))

    return to


def zipfile_make_archive(dirname, to=None, **kwargs):
    """
    Thin layer over shutil.make_archive. Just defaults
    the to to the same name as the directory by default.

    :param dirname: (str)
        The directory name
    :param to: (str, default None)
        The file path to create the archive in.
    :param kwargs:
        shutil.make_archive(**kwargs)
    :return: (str)
        The :param to file path.
    """
    if to is None:
        to = dirname
    return shutil.make_archive(to, "zip", root_dir=dirname, **kwargs)


def zipfile_compress(from_path, to=None, **kwargs):
    """
    Compresses a path to a file (or directory).

    :param from_path: (str)
        The path to the file or directory to be compressed.
    :param to: (str, default None)
        The path to the file to create (if different from the :param from_path)
    :param kwargs: (zipfile.ZipFile(**kwargs))
        :param mode: (str, default 'a')
            The mode to open the ZipFile in
        :param compression: (zipfile.ZIP_DEFLATED/ZIP_STORED)
            The compression type (auto-defaulted) to ZIP_DEFLATED if possible.
    :return: (str)
        The :param to path.
    """

    if os.path.isfile(from_path):
        kwargs['mode'] = kwargs.pop('mode', 'a')
        kwargs['compression'] = kwargs.pop('compression', DEFAULT_COMPRESSION)
        return_path =  zipfile_write(from_path, to=to, **kwargs)
    elif os.path.isdir(from_path):
        kwargs.pop('mode', None)
        kwargs.pop('compression', None)
        return_path = zipfile_make_archive(from_path, to=to, **kwargs)
    else:
        raise NotImplementedError(":param from_path is not a file or directory name: {}".format(from_path))
    print("Compressed {} to {}".format(from_path, return_path))
    return return_path

