# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 14:02:26 2016

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


class Bookmark(object):
    """
    Container for a file with text in it.
    """

    def __init__(self, name, file_path=None):
        self.name = name
        self.file_path = file_path
        self._text = None

    def get_text(self):
        """
        Get the text (cached) or read the
        file and return the text.
        :return: (str)
            The text contents of the file.
        """
        if self._text is None:
            with open(self.file_path, "r") as fp:
                self._text = fp.read()
            return self._text

    def set_text(self, text, save_changes=True):
        """
        Sets the object's text property
        and optionally saves changes to file.

        :param text: (str)
            The updated text to set.
        :param save_changes (bool, default True)
            True saves changes to the file_path
            False only sets the text property.
        :return:
        """
        if text != self._text and save_changes is True:
            with open(self.file_path, "w") as fp:
                fp.write(text)

        self._text = text


class BookmarkManager(object):
    """
    Registers bookmark objects and makes them
    easily accesible.
    """

    def __init__(self, name):
        self._bookmarks = {}

    @property
    def names(self) -> list:
        return list(self._bookmarks.keys())

    @property
    def file_paths(self):
        return list(b.file_path for b in self._bookmarks.values())

    def add_bookmark(self, name, file_path):
        self._bookmarks[name] = Bookmark(name, file_path=file_path)

    def bookmark(self, name) -> Bookmark:
        return self._bookmarks[name]

    def model(self):
        from zeex.core.models.bookmark import BookMarkModel
        return BookMarkModel(self)
