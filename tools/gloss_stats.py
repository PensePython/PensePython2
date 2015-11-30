#!/usr/bin/env python3

import csv
import unicodedata
import string
import collections

GLOSSARY_DATA_PATH = './glossary.csv'
FIELDS = 'term us_term br_term chapter order us_definition br_definition'.split()

GlossaryEntry = collections.namedtuple('GlossaryEntry', FIELDS)

def asciize(txt):
    """Return only ASCII letters from text"""
    return ''.join(c for c in unicodedata.normalize('NFD', txt)
                     if c in string.ascii_lowercase)

def count_glossary():
    counter = collections.Counter()
    master_glossary = []
    with open(GLOSSARY_DATA_PATH) as csvfile:
        reader = csv.DictReader(csvfile, FIELDS)
        next(reader)  # skip header line
        for row in reader:
            entry = GlossaryEntry(**row)
            #print(entry)
            normal_term = asciize(entry.term.casefold())
            counter[normal_term[0]] += 1
    return counter
    
if __name__ == '__main__':
    res = count_glossary().most_common()
    for letter, count in sorted(res):
        print(letter, count)
