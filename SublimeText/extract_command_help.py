#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Glaukon Ariston
# Date: 27.03.2019
# Abstract:
#

from pyquery import PyQuery as S
import glob
import os.path
import json
import codecs
import re
import pickle
import datetime
import collections
import itertools


MANUAL_ROOT = r'D:/fmslogo-source-r4806/logo/trunk/manual/'

SUBSTITUTIONS = {
    '&PRODUCTNAME;': 'FMSLogo',
    '&GENERICNAME;': 'Logo'
}

MAX_DESC_SIZE = 170


def get(tree, name):
    es = tree('varlistentry').filter(lambda i, e: S(e)('term').text().strip().lower() == name.lower())
    return es


def nextWhile(tree, selector):
    xs = []
    e = tree
    while True:
        e = e.next()
        if not e.is_(selector):
            break
        xs.extend(e)
    return xs


def parse_file(filepath):
    with codecs.open(filepath, 'rb', 'utf-8') as f:
        data = f.read()
    tree = S(data)

    section = get(tree, 'Description')
    desc = section('listitem para').eq(0).text()

    section = get(tree, 'Synopsis')
    synopsis = section('synopsis')
    meta = []
    cs = synopsis('command')
    for c_ in cs:
        c = S(c_)
        ps = nextWhile(c, 'parameter')
        meta.append((c.text(), [S(p).text() for p in ps], desc))
    return (True, meta)


def gen_completions(synopsis):
    completions = {
        'scope': 'source.logo',
        'completions': ['logo']
    }
    generic_names = set([])
    desc_sizes = set([])

    def gen_params(params):
        return ' '.join(['${%d:%s}' % (i+1, p) for p, i in zip(params, range(len(params)))])

    def addCompletion(command, params, desc_):
        # remove markup from the description
        desc = S(desc_).text()
        # trim it to the first sentence only
        i = desc.find('.')
        desc = desc[:i+1] if i >= 0 else desc
        # substitute generic names
        xs = re.findall(r'\&(.+?);', desc)
        if xs:
            print('%s: %s' % (command, xs))
            generic_names.update(xs)
        for key, val in SUBSTITUTIONS.items():
            desc = desc.replace(key, val)
        # if still quite long, try to trim it further down
        if len(desc) > MAX_DESC_SIZE:
            desc_sizes.add(len(desc))
            i = desc.find(';')
            desc = desc[:i+1] if i >= 0 else desc
            desc = desc[:MAX_DESC_SIZE]
            print('%s: len %d' % (command, len(desc)))
        x = { "trigger": '%s\t%s' % (command.lower(), desc), "contents": '%s %s' % (command.lower(), gen_params(params)) }
        completions['completions'].append(x)

    [addCompletion(command, params, desc) for ss in synopsis for (command, params, desc) in ss]
    print('generic_names = %s' % (generic_names))
    print('desc_sizes = %s' % (sorted(desc_sizes, reverse=True)))
    return completions


def parse_files(root):
    filter = root + 'command-*.xml'
    files = glob.glob(filter)
    print('About to process %d files from %s ...' % (len(files), filter))
    #files = glob.glob(MANUAL_ROOT + 'command-and.xml')
    synopsis = [value for f in files for ok, value in [parse_file(f)] if ok]
    with open('synopsis.pkl', 'wb') as f:
        pickle.dump(synopsis, f, -1)
    completions = gen_completions(synopsis)
    with codecs.open('Logo/Logo.sublime-completions', 'wb', 'utf-8') as f:
        json.dump(completions, f, indent=2)


def main():
    t0 = datetime.datetime.now()
    print(t0, 'Start')
    parse_files(MANUAL_ROOT)
    t1 = datetime.datetime.now()
    print(t1, 'End. dT = %s' % (t1-t0))


if __name__ == "__main__":
    main()


