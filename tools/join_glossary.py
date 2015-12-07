#!/usr/bin/env python3

"""
Extract glossary entries from chapters 1-19 and appendix B and create
a consolidated glossary text file delimited by '|' (pipe characters).
"""

import glob
import re
import os
import collections

GLOSSARY = r'Gloss[^-]{3,7}-{8,15}\n(.*)'

GLOSSARY_RE = re.compile(GLOSSARY, re.DOTALL)

GLOSSARY_SECTION_RE = re.compile(GLOSSARY + r'-{8,15}', re.DOTALL)

expected_entries = [  # glossary entries per chapter
    ('01', 21),
    ('02', 19),
    ('03', 22),
    ('04', 11),
    ('05', 15),
    ('06',  5),
    ('07',  8),
    ('08', 12),
    ('09',  3),
    ('10', 14),
    ('11', 20),
    ('12',  8),
    ('13',  6),
    ('14', 14),
    ('15',  9),
    ('16',  7),
    ('17',  9),
    ('18', 13),
    ('19',  5),
    ( 'B', 11),
]

expected_entries_dic = dict(expected_entries)

# \n(.*?)\n\n
ENTRY_RE = re.compile(r'([^\n]+):\n[ ]+(.*?)\n\n', re.DOTALL)

GlossaryEntry = collections.namedtuple('GlossaryEntry', 'term definition')
Definition = collections.namedtuple('Definition', 'chapter_id position text')


def parse_entries(text, chapter_id):
    matches = ENTRY_RE.findall(text)
    entries = []
    for position, match in enumerate(matches, 1):
        term = match[0]
        definition_text = ' '.join(match[1].split())
        #print(term, '::', definition_text)
        entries.append(GlossaryEntry(term,
                                     Definition(chapter_id, position, definition_text)))
    return entries


def scan_files(*paths):
    entries = collections.defaultdict(list)
    for path in paths:
        for name in glob.glob(os.path.join(path, '*.rst')):
            chapter_id = os.path.basename(name).split('-')[0]

            with open(name, encoding='utf-8') as infile:
                rst = infile.read()
                gloss_match = (GLOSSARY_SECTION_RE.search(rst) or
                               GLOSSARY_RE.search(rst))
                if gloss_match:
                    #print('*' * 40, name)
                    new_entries = parse_entries(gloss_match.group(1), chapter_id)
                    for term, definition in new_entries:
                        #if term in entries:
                        #    print('duplicate term:', term)
                        entries[term].append(definition)
                    #print(len(new_entries))
                    assert expected_entries_dic[chapter_id] == len(new_entries), (
                        chapter_id, expected_entries_dic[chapter_id], len(new_entries))
    for term in sorted(entries, key=str.upper):
        definitions = entries[term]
        for i, (chapter_id, position, definition) in enumerate(sorted(definitions)):
            if i:
                term = '\t'
            print(term, chapter_id, position, definition, sep='|')


if __name__ == '__main__':
    import sys
    scan_files(*sys.argv[1:])
