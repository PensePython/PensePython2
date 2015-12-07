#!/usr/bin/env python3

"""
Generate consolidated RST glossary file and chapter include files from 
consolidated CSV glossary file. 

THIS SCRIPT IS NO LONGER USED, SEE ``split_glossary.py``
"""

import glob
import os
import csv
import collections
import operator
import unicodedata
import string

from join_glossary import expected_entries

RST_PATH = '../book/'
GLOSSARY_DATA_PATH = './glossary.csv'
FIELDS = 'term us_term br_term chapter order us_definition br_definition'.split()

GLOSSARY_HEAD = '''\
Glossário Consolidado
=====================

Este glossário é a união de todos os glossários dos capítulos.
Cada entrada está vinculada ao capítulo onde ela aparece, por exemplo:
*bug* :ref:`[1] <glossary01>`.

Note que alguns termos aparecem em mais de um capítulo, às vezes
com definições diferentes, de acordo com o contexto.
\n\n'''

GlossaryEntry = collections.namedtuple('GlossaryEntry', FIELDS)


def asciize(txt):
    """Return only ASCII letters from text"""
    return ''.join(c for c in unicodedata.normalize('NFD', txt)
                     if c in string.ascii_lowercase)

def master_order(entry):
    return asciize(entry.term.casefold()) + '|' + entry.chapter


def read_glossary():
    master_glossary = []
    glossaries = collections.defaultdict(list)
    with open(GLOSSARY_DATA_PATH) as csvfile:
        reader = csv.DictReader(csvfile, FIELDS)
        next(reader)  # skip header line
        for row in reader:
            row['order'] = int(row['order'])
            entry = GlossaryEntry(**row)
            #print(entry)
            glossaries[row['chapter']].append(entry)
            master_glossary.append(entry)
    return master_glossary, glossaries


def formatted_head(entry):
    us_term = entry.us_term
    if '``' in us_term:
        if us_term != '``None``':
            symbol, noun = us_term.split()
            us_term = '{} *{}*'.format(symbol, noun)
    else:
        us_term = '*{}*'.format(us_term)
    if entry.br_term == '-':  # no BR term
        head = us_term
    elif entry.term != entry.us_term:  # adopted BR term
        head = '{} ({})'.format(entry.term, us_term)
    else:  # adopted US term
        head = '{} ({})'.format(us_term, entry.br_term)
    return head

def main():
    master_glossary, chapter_glossaries = read_glossary()

    link_fmt = ':ref:`[1] <glossary01>`'

    out_path = os.path.join(RST_PATH, 'C-glossary.rst')
    with open(out_path, 'wt', encoding='utf-8') as out_file:
        out_file.write(GLOSSARY_HEAD)
        for entry in sorted(master_glossary, key=master_order):
            short_chapter = entry.chapter.lstrip('0')
            definition = entry.br_definition.strip() or entry.us_definition.strip()
            out_file.write('{} :ref:`[{}] <glossary{}>`\n  {}\n\n'
                           .format(formatted_head(entry), short_chapter,
                                   entry.chapter, definition))

    for chapter_id, entries_qty in expected_entries:
        chapter_glob = os.path.join(RST_PATH, chapter_id+'*.rst')
        found = glob.glob(chapter_glob)
        assert len(found) == 1, 'found: {}'.format(len(found))
        out_path = os.path.join(RST_PATH, 'glossary', chapter_id+'.txt')
        glossary = chapter_glossaries[chapter_id]
        with open(out_path, 'wt', encoding='utf-8') as out_file:
            for entry in sorted(glossary, key=operator.attrgetter('order')):
                definition = entry.br_definition.strip() or entry.us_definition.strip()
                out_file.write('{}\n  {}\n\n'.format(formatted_head(entry), definition))

    print()

if __name__ == '__main__':
    main()



