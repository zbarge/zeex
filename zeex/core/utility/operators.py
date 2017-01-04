import operator
from pandas import notnull, isnull
from core.utility.collection import Eval
STRING_TO_OP = {
                '+' : operator.add,
                '-' : operator.sub,
                '*' : operator.mul,
                '/' : operator.truediv,
                '%' : operator.mod,
                '^' : operator.xor,
                '>' : operator.ge,
                '<' : operator.le,
                '==': operator.eq,
                '&' : operator.and_,
                'AND': operator.and_,
                'OR': operator.xor
                }
NULL_VALUES = ['nan', 'na', 'none', 'null', '']

def is_like(x, y):
    if x in y:
        return True
    return False


def not_like(x, y):
    if x not in y:
        return True
    return False


def is_null(x):
    return isnull(x) or str(x).lower() in NULL_VALUES


def not_null(x):
    return notnull(x) and str(x).lower() not in NULL_VALUES


WORD_TO_OP = {'IS LIKE':is_like,
              'IS NOT LIKE': not_like,
              'IS NULL': is_null,
              'IS NOT NULL': not_null}
WORD_TO_MAP = {k: k.replace(' ', '__') for k in WORD_TO_OP.keys()}


class CriteriaParser(object):
    def __init__(self):
        self.options = STRING_TO_OP.copy()
        self.words = WORD_TO_OP.copy()

    def parse(self, string):
        string = string.upper().lstrip().rstrip()\
                 .replace('  ', ' ').replace('""', '').replace("''", "")
        for w in self.words.keys():
            # Normalize word operators replacing spaces with '__'
            piece = w.replace(' ', '__')

            string = string.replace(w, piece)

        for o in self.options.keys():
            # Normalize spacing around operators.
            piece = " {} ".format(o)
            string = string.replace(piece, o)
            string = string.replace(o, piece)

        data = list(string.split(' '))    # Split string by spaces
        new_data = []
        for d in data:
            try:
                # Try a direct match
                new_data.append(self.options[d])
            except KeyError:
                try:
                    # Try to map the word to a word operator.
                    op_word = self.words[d.replace('__', ' ')]
                    new_data.append(op_word)
                except KeyError:
                    # No parsing done on this word, append it to the list.
                    new_data.append(d)
        return new_data

    def evaluate(self, data: list):
        if len(data) == 3:
            op1, op, op2 = data
            return op(op1, op2)
        elif len(data) == 2:
            op1, op = data
            return op(op1)
        return None




cp = CriteriaParser()
tests = ['ID > 10', 'FIELD == YO', "CHECK < MATE", "CAT IS LIKE DOG",
         "'' IS NOT NULL", "'' IS NULL", "CAT IS LIKE CAT"]

for t in tests:
    p = cp.parse(t)
    e = cp.evaluate(p)
    print("ORIGINAL: {}\n {}: {}".format(t, p, e))



