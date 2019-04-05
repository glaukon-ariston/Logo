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
from functools import reduce


MANUAL_ROOT = r'D:/RE/Languaging/Logo/fmsLogo/fmslogo-source-r4806/logo/trunk/manual/'

SUBSTITUTIONS = {
    '&PRODUCTNAME;': 'FMSLogo',
    '&GENERICNAME;': 'Logo'
}

MAX_DESC_SIZE = 170

PREFIXES = 'active arrayTo before bit bitLoad bitmap bitPasteTo but buttOn clear checkbox \
    combobox comboboxAdd comboboxDelete comboboxGet comboboxSet debug dialog dialogFile dll \
    erase event flood fontface gif greater greaterp groupbox has keyboard listbox \
    listboxDelete listTo logo maybe message midi net netAccept netAcceptReceive \
    netAcceptSend netConnect netConnectReceive netConnectSend noBitmap open pen port portRead \
    portWrite print printDepth printWidth radio radioButton read readRaw scrollbar \
    set setActive setCursor setFlood setLabel setPen setRead setScreen setTurtle setWrite static \
    text turtle unbury window windowFile'.split()


generic_names = set([])
desc_sizes = set([])


def concat(xs):
    '''concat :: [[a]] -> [a]'''
    return list(itertools.chain.from_iterable(xs))


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


def parse_xml_file(filepath):
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


def trim_desc(command, desc_):
    global generic_names
    # remove markup from the description
    desc = S(desc_).text()
    # remove space after comma
    desc = desc.replace(' , ', ', ')
    # trim it to the first sentence only
    xs = [m.start()+2 for m in re.finditer(r'\.\s+|\.$', desc) if m.start() > MAX_DESC_SIZE]
    if xs:
        desc = desc[:xs[0]]
    # substitute generic names
    xs = re.findall(r'\&(.+?);', desc)
    if xs:
        print('%s: %s' % (command, xs))
        generic_names.update(xs)
    for key, val in SUBSTITUTIONS.items():
        desc = desc.replace(key, val)
    return desc


def shorten_desc(command, desc):
    # if still quite long, try to trim it further down
    if len(desc) > MAX_DESC_SIZE:
        desc_sizes.add(len(desc))
        i = desc.find(';')
        desc = desc[:i+1] if i >= 0 else desc
        desc = desc[:MAX_DESC_SIZE]
        print('%s: len %d' % (command, len(desc)))
    return desc


def gen_camelCase(synopsis):
    syn_sorted = sorted(concat(synopsis), key=lambda x: x[0].lower())
    commands = [command.lower() for (command, _, _) in syn_sorted]

    def camelCase(c_):
        c = c_
        for p in PREFIXES:
            if c_.startswith(p.lower()) and len(c_) > len(p):
                n = len(p)
                c = p + c[n].upper() + c[n+1:]
        return c
    camelCaseCmds = {c: camelCase(c) for c in commands}
    with codecs.open('commands.txt', 'wb', 'utf-8') as f:
        [f.write('%s\n' % (cc)) for _, cc in camelCaseCmds.items()]
    with open('camelCaseCmds.pkl', 'wb') as f:
        pickle.dump(camelCaseCmds, f, -1)


def gen_completions(synopsis, cmdMap, descMap):
    syn_sorted = sorted(concat(synopsis), key=lambda x: x[0].lower())
    with open('camelCaseCmds.pkl', 'rb') as f:
        camelCaseCmds = pickle.load(f)

    completions = {
        'scope': 'source.logo',
        'completions': ['logo']
    }
    def gen_params(params):
        return ' '.join(['${%d:%s}' % (i+1, p) for p, i in zip(params, range(len(params)))])

    def addCompletion(command, params, desc_):
        desc = shorten_desc(command, desc_)
        c = camelCaseCmds[command.lower()]
        suffix = '\n\t\nend\n\n' if c == 'to' else ''
        x = { "trigger": '%s\t%s' % (c, desc), "contents": '%s %s' % (c, gen_params(params) + suffix) }
        completions['completions'].append(x)

    [addCompletion(command, params, descMap[cmdMap[command]]) for (command, params, _) in syn_sorted]
    print('generic_names = %s' % (generic_names))
    print('desc_sizes = %s' % (sorted(desc_sizes, reverse=True)))
    return completions


def extract_descriptions(synopsis):
    syn_sorted = sorted(concat(synopsis), key=lambda x: x[0].lower())
    xs = [(i, command, trim_desc(command, desc)) for (i, (command, _, desc)) in zip(range(len(syn_sorted)), syn_sorted)]
    with codecs.open('descriptions.txt', 'wb', 'utf-8') as f:
        [f.write('%d! %s\n' % (i, desc)) for (i, _, desc) in xs]
    with codecs.open('descriptions_cmdmap.txt', 'wb', 'utf-8') as f:
        [f.write('%d %s\n' % (i, command)) for (i, command, _) in xs]


def preserveCase(s, w):
    if not s: return s
    return s[0].upper() + s[1:] if w and w[0].isupper() else s


def fix_translation_hr():
    SUBS = {
        'emitira': 'daje',
        'izlazi': 'daje',
        'njegovih': '',
        'njegovog': '',
        'njezinih': '',
        'njezinog': '',
        'unosa': 'ulaza',
        'unos': 'ulaz',
        'obrnuti': 'inverzni',
        'proizvod': 'umnožak',
    }
    POST_SUBS = {
        ', u suprotnom': ' u suprotnom'
    }
    EXCEPTIONS = {
        'BYE': 'izlazi'
    }
    def fix_word(w, cmd):
        ex = EXCEPTIONS.get(cmd)
        if w == ex: return w
        s = SUBS.get(w.lower())
        return preserveCase(s,w) if s is not None else w
    def fix_line(ln):
        cmd = cmdMap[re.match(r'^(\d+)', ln).group(1)]
        xs = [fix_word(w, cmd) for w in re.split(r'\b', ln)]
        # coalesce spaces
        s = re.sub(r'[ ]+', ' ', ''.join(xs))
        for (key,val) in POST_SUBS.items():
            s = re.sub(key, val, s)
        return s

    with codecs.open('descriptions_cmdmap.txt', 'rb', 'utf-8') as f:
        cmdMap = dict([re.match(r'^(\d+) (.*)$', ln).groups() for ln in f if ln])
    with codecs.open('descriptions_GoogleTranslate_hr.txt', 'rb', 'utf-8') as f:
        lines = [fix_line(ln) for ln in f]
    with codecs.open('descriptions_GoogleTranslate_hr_fixed.txt', 'wb', 'utf-8') as f:
        [f.write(ln) for ln in lines]


def completions_en(synopsis):
    with codecs.open('descriptions_cmdmap.txt', 'rb', 'utf-8') as f:
        cmdMap = dict([reversed(re.match(r'^(\d+) (.*)$', ln).groups()) for ln in f if ln])
    with codecs.open('descriptions.txt', 'rb', 'utf-8') as f:
        descMap = dict([re.match(r'^(\d+)! (.*)$', ln).groups() for ln in f if ln])
    completions = gen_completions(synopsis, cmdMap, descMap)
    with codecs.open('Logo/Logo.sublime-completions_en', 'wb', 'utf-8') as f:
        json.dump(completions, f, indent=2)


def completions_hr(synopsis):
    with codecs.open('descriptions_cmdmap.txt', 'rb', 'utf-8') as f:
        cmdMap = dict([reversed(re.match(r'^(\d+) (.*)$', ln).groups()) for ln in f if ln])
    with codecs.open('descriptions_GoogleTranslate_hr_fixed.txt', 'rb', 'utf-8') as f:
        descMap = dict([re.match(r'^(\d+)! (.*)$', ln).groups() for ln in f if ln])
    completions = gen_completions(synopsis, cmdMap, descMap)
    with codecs.open('Logo/Logo.sublime-completions_hr', 'wb', 'utf-8') as f:
        json.dump(completions, f, indent=2)


def parse_xml_files(root):
    filter = root + 'command-*.xml'
    files = glob.glob(filter)
    print('About to process %d files from %s ...' % (len(files), filter))
    #files = glob.glob(MANUAL_ROOT + 'command-and.xml')
    synopsis = [value for f in files for ok, value in [parse_xml_file(f)] if ok]
    with open('synopsis.pkl', 'wb') as f:
        pickle.dump(synopsis, f, -1)


def main():
    t0 = datetime.datetime.now()
    print(t0, 'Start')
    #parse_xml_files(MANUAL_ROOT)
    with open('synopsis.pkl', 'rb') as f:
        synopsis = pickle.load(f)
    gen_camelCase(synopsis)
    extract_descriptions(synopsis)
    completions_en(synopsis)
    #fix_translation_hr()
    completions_hr(synopsis)
    t1 = datetime.datetime.now()
    print(t1, 'End. dT = %s' % (t1-t0))


if __name__ == "__main__":
    main()


