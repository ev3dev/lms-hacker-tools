#!/usr/bin/env python
#
# lmsasm.py
#
# The MIT License (MIT)
#
# Copyright (c) 2016 David Lechner <david@lechnology.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This program is a translation of the lmsasm tool from lms2012. The original tool was written in logo and required
Java to run."""

from __future__ import print_function
import argparse
import io
import re
import os
import sys

read_stream = None
version = None
stringbuffer = None
next_global = None
is_listing = None
asm_globals = {}


def get_global(name):
    """Works like the global scope in logo. Each variable name is assigned a dictionary."""
    global asm_globals

    if name not in asm_globals:
        asm_globals[name] = {'name': name}
    return asm_globals[name]


def readline():
    """Emulates logo built-in readline procedure. Reads one line from the date set using setread()."""
    global read_stream

    return read_stream.readline()


def lineread():
    """Emulates logo built-in lineread procedure. Reads all data that was set using setread()."""
    global read_stream

    return read_stream.getvalue()


def is_eot():
    """Emulates logo built-in eot? procedure. Tests if we have read all of the data set by setread()."""
    global read_stream

    t = read_stream.tell()
    r = read_stream.read(1)
    read_stream.seek(t, 0)
    return not len(r)


def setread(data):
    """Emulates logo built-in setread procedure. Loads data that can be read with readline(), lineread(), getc() and
    peek()"""
    global read_stream

    if read_stream:
        read_stream.close()
    read_stream = io.StringIO(data)


def getc():
    """Emulates logo-built-in getc procedure. Reads one character from the data set by setread()."""
    global read_stream

    return read_stream.read(1)[0]


def peek():
    """Emulates logo built-in peek procedure. Gets one character from the data set by setread() but does not
    change the file pointer."""
    global read_stream

    t = read_stream.tell()
    r = read_stream.read(1)
    read_stream.seek(t, 0)
    return r[0]


def parse(l):
    """Emulates logo built-in parse procedure. Converts a line to a list of strings, numbers and identifiers.
    We are taking advantage of the fact that the line data is unicode to differentiate between strings (python str
    type) and identifiers (python unicode type)."""
    l = l.split()
    for i, x in enumerate(l):
        if re.match(r"'.*'", x):
            l[i] = str(x[1:-1].replace('\\s', ' '))
        elif re.match(r'".*"', x):
            l[i] = str(x[1:-1].replace('\\s', ' '))
        elif re.match(r'-?\d+\.\d+', x):
            l[i] = float(x)
        elif re.match(r'0[xX][0-9A-Fa-f]+', x):
            l[i] = int(x, 16)
        elif re.match(r'-?\d+', x):
            l[i] = int(x)

    return l


def clearstringbuffer():
    """Emulates logo built-in clearstringbuffer procedure."""
    global stringbuffer

    stringbuffer = u''


def addtostringbuffer(s):
    """Emulates logo built-in addtostringbuffer procedure."""
    global stringbuffer

    stringbuffer += s


def read_defines():
    global version

    preprocess('bytecodes.h')
    version = 0
    while True:
        if is_eot():
            return
        def_line(parse(readline().replace('\\"', chr(39))))


def def_line(l):
    global version

    if len(l) < 3:
        return
    if l[0] != '#define':
        return
    name = l[1]
    if name == 'BYTECODE_VERSION':
        version = int(l[-1] * 100)
        return
    if name[0:2] != 'vm':
        return
    get_global(name[2:])['type'] = 'define'
    get_global(name[2:])['value'] = l[2]


def read_opdefs():
    preprocess('bytecodes.c')
    while True:
        if is_eot():
            return
        read_opdef(parse(readline()))


def read_opdef(l):
    if not l:
        return
    if l[0] == 'OC':
        read_oc(l)
    elif l[0] == 'SC':
        read_sc(l)


def read_oc(l):
    op = get_global(l[1][2:])
    args = extract_args(l[2:])
    op['args'] = args


def read_sc(l):
    op = get_global(l[1] + "_" + l[2])
    args = extract_args(l[3:])
    op['args'] = args


def extract_args(l):
    for i in range(0, len(l)):
        if l[-1] != 0:
            return l
        l = l[:-1]
    return []


def read_enums():
    preprocess('bytecodes.h')
    enum_loop()
    preprocess('bytecodes.c')
    enum_loop()


def enum_loop():
    while True:
        find_enum()
        if is_eot():
            return
        process_enum()


def find_enum():
    while True:
        if is_eot():
            return
        if 'enum' in readline():
            return


def process_enum():
    while True:
        if is_eot():
            return
        l = readline()
        if '}' in l:
            return
        process_enum_line(parse(l))


def process_enum_line(l):
    if len(l) != 3:
        return
    if l[1] != '=':
        return
    enum_define(l[0], l[2])


def enum_define(name, value):
    if name[0:2] == 'op':
        get_global(name[2:])['op'] = value
    else:
        get_global(name)['type'] = 'enum'
        get_global(name)['value'] = value


def preprocess(x):
    with io.FileIO(x) as f:
        setread(f.readall().decode(encoding='utf-8'))
    # clean_up_crs()
    remove_comments()
    # clean_up_whitespace()


def remove_comments():
    global stringbuffer

    clearstringbuffer()
    while True:
        if is_eot():
            setread(stringbuffer)
            return
        rc_char(getc())


def rc_char(c):
    if c == '(':
        addtostringbuffer(' ')
        return
    if c == ')':
        addtostringbuffer(' ')
        return
    if c == ',':
        addtostringbuffer(' ')
        return
    if c == '/':
        handle_slash()
        return
    if c == "'":
        handle_quote()
        return
    addtostringbuffer(c)


def handle_quote():
    addtostringbuffer("'")
    while True:
        if is_eot():
            addtostringbuffer("'")
            return
        c = getc()
        if c == "'":
            addtostringbuffer(c)
            return
        addtostringbuffer(quote_escape(c))


def quote_escape(c):
    if c == ' ':
        return '\\s'
    if c == '\\' and peek() == "'":
        getc()
        return '\\q'
    if c == '\t':
        return '\\t'
    return c


def handle_slash():
    if peek() == '/':
        skip_one_line_comment()
        return
    if peek() == '*':
        skip_multi_line_comment()
        return
    addtostringbuffer('/')


def skip_one_line_comment():
    while True:
        if is_eot():
            return
        c = getc()
        if c == chr(10):
            addtostringbuffer(c)
            return


def skip_multi_line_comment():
    getc()
    getc()
    while True:
        if is_eot():
            return
        c = getc()
        if c == '*' and peek() == '/':
            getc()
            return


def clean_up_crs():
    setread(re.sub(r'\r\n|\r|\n', '\n', lineread()))


def clean_up_whitespace():
    setread(re.sub(r'\n[\s\n]*\n', '\n', lineread()))
    setread(re.sub(r'^\n*', '', lineread()))
    setread(re.sub(r'[\n\t\s]*$', '', lineread()))
    setread(re.sub(r'[ \t]+', ' ', lineread()))
    # we are now taking care of escaped spaces in parse()
    # setread(re.sub(r'\\s', ' ', lineread()))
    setread(re.sub(r'\s*=\s*\n\s*', ' ', lineread()))


def assemble(file_):
    preprocess(file_ + ".lms")
    code = lineread()
    asm_init()
    pass0(code)
    codebytes = pass1(code)
    codebytes = pass2(codebytes)
    codebytes = program_header() + object_headers() + codebytes
    listtofile(file_ + ".rbf", codebytes)


def asm_init():
    global next_global, defines, objects

    next_global = 0
    for i in defines:
        erplist(i)
    erase_locals()
    defines = []
    objects = []


def program_header():
    global pc, version, objects, next_global

    return strbytes('LEGO') + int32bytes(pc) + int16bytes(version) + int16bytes(len(objects)) + int32bytes(next_global)


def object_headers():
    global objects

    res = []
    for i in objects:
        trg = 0
        if i['type'] == 'subcall':
            trg = 1
        res += int32bytes(i['offset']) + [0, 0] + int16bytes(trg) + int32bytes(i['locals'])
    return res


def headersize():
    global objects

    return 16 + 12 * len(objects)


def pass0(code):
    setread(code)
    global thisobject

    thisobject = {'params': 0}
    while True:
        if is_eot():
            return
        pass0_line(parse(readline()))


def pass0_line(line):
    if not line:
        return
    token = line[0]
    if token == 'vmthread':
        setup_object(line)
        return
    if token == 'subcall':
        setup_subcall(line)
        return
    if token == 'define':
        setup_define(line[1], getvalue(line[2:]), 'define')
        return
    if token and token[-1] == ':':
        setup_label(token[:-1])
        return
    if is_param(token):
        thisobject['params'] += 1
        return


def setup_label(name):
    global defines

    fname = lname(name)
    get_global(fname)['value'] = 'undefined'
    get_global(name)['type'] = 'label'
    get_global(fname)['type'] = 'label'
    defines += get_global(name)
    defines += get_global(fname)


def setup_subcall(line):
    setup_object(line)


def setup_object(line):
    global objects, thisobject

    typ = line[0]
    name = line[1]
    objects.append(get_global(name))
    setup_define(name, len(objects), typ)
    get_global(name)['params'] = 0
    thisobject = get_global(name)


def setup_define(name, value, typ):
    global defines

    get_global(name)['value'] = value
    get_global(name)['type'] = typ
    defines += get_global(name)


def pass1(code):
    global thisobject

    res = []
    thisobject = None
    setread(code)
    while True:
        if is_eot():
            return res
        pass1_line(parse(readline()), res)


def pass1_line(line, res):
    global thisobject

    if thisobject:
        pass1_line_inside(line, res)
    else:
        pass1_line_outside(line, res)


def pass1_line_outside(line, res):
    global thisobject

    if not line:
        return
    token = line[0]
    if token in ('vmthread', 'subcall'):
        add(['&' + line[1]], res)
        thisobject = get_global(line[1])
        if token == 'subcall':
            add([thisobject['params']], res)
        return
    if token == 'define':
        return
    if token == 'global':
        setup_global(line[1], int(getvalue(line[2:])))
        return
    if token in ('DATA8', 'DATA16', 'DATA32', 'DATAF', 'HANDLE'):
        setup_data_global(token, line[1])
        return
    if token in ('DATAS', 'ARRAY8'):
        setup_global(line[1], int(getvalue(line[2:])))
        return
    if token == 'ARRAY16':
        setup_global(line[1], 2 * int(getvalue(line[2:])))
        return
    if token in ('ARRAY32', 'ARRAYF'):
        setup_global(line[1], 4 * int(getvalue(line[2:])))
        return
    print('***', line, '???', '***')


def pass1_line_inside(line, res):
    if not line:
        return
    token = line[0]
    if token and token[-1] == ':':
        add([lname(token)], res)
        return
    if token == 'local':
        setup_local(line[1], int(getvalue(line[2:])))
        return
    if token in ('DATA8', 'DATA16', 'DATA32', 'DATAF', 'HANDLE'):
        setup_data_local(token, line[1])
        return
    if token in ('DATAS', 'ARRAY8'):
        setup_local(line[1], int(getvalue(line[2:])))
        return
    if token == 'ARRAY16':
        setup_local(line[1], 2 * int(getvalue(line[2:])))
        return
    if token in ('ARRAY32', 'ARRAYF'):
        setup_local(line[1], 4 * int(getvalue(line[2:])))
        return
    if is_param(token):
        setup_param(line, res)
        return
    if token == '{':
        return
    if token == '}':
        pass1_close(res)
        return
    pass1_instruction(line, res)


def pass1_close(res):
    global thisobject, next_local

    thisobject['locals'] = next_local
    erase_locals()
    if thisobject['type'] == 'subcall':
        add([get_global('RETURN')['op']], res)
    add([get_global('OBJECT_END')['op']], res)
    thisobject = None


def pass1_instruction(l, res):
    op = l[0]
    template = get_template(l)
    if is_listing:
        print(template + l)
    if not get_global(op)['op']:
        print(bad(op, '-'), op)
        return
    if op == 'CALL':
        l = expand_call_arg(l)
    else:
        arg_check(template, l)
    args = get_args(l[1:])
    if is_listing:
        print(len(res), '-', hexl(), get_global(op)['op'], args)
    add([get_global(op)['op']] + args, res)


def get_args(l):
    args = []
    for i in l:
        args += get_arg(i)
    return args


def get_arg(i):
    if is_string(i):
        return pass1_str(i)
    if is_number(i):
        return make_lc(i)
    if is_number(i[:-1]) and i[-1] == 'F':
        return make_lc(floatbits(i[:-1]))
    if i[0] == '@':
        return get_hnd(i[1:])
    if i[0] == '&':
        return get_adr(i[1:])
    if 'local' in get_global(i):
        return addbits(0x40, make_lc(get_global(i)['local']))
    if 'type' in get_global(i):
        if get_global(i)['type'] == 'enum':
            return make_lc(get_global(i)['value'])
        if get_global(i)['type'] == 'global':
            return addbits(0x60, make_lc(get_global(i)['value']))
        if get_global(i)['type'] == 'label':
            return [lname(i)]
        if get_global(i)['type'] == 'vmthread':
            return [get_global(i)['value']]
        if get_global(i)['type'] == 'subcall':
            return make_lc(get_global(i)['value'])
        if get_global(i)['type'] == 'define':
            return get_arg(get_global(i)['value'])
    print('***', i, 'undefined', '***', 'in', thisobject)
    return []


def get_hnd(i):
    if get_global(i)['local']:
        return addbits(0x40, make_hnd(get_global(i)['local']))
    if get_global(i)['type'] == 'global':
        return addbits(0x60, make_hnd(get_global(i)['value']))
    print('***', i, 'undefined', '***', 'in', thisobject)
    return []


def get_adr(i):
    if get_global(i)['local']:
        return addbits(0x40, make_adr(get_global(i)['local']))
    if get_global(i)['type'] == 'global':
        return addbits(0x60, make_adr(get_global(i)['value']))
    print('***', i, 'undefined', '***', 'in', thisobject)


def arg_check(t, l):
    if not t:
        return
    if t[-1] == 'PARNO':
        for i in range(0, l[1:][len(t) - 1]):
            t += ['PAR32']
    if len(l[1:]) != len(t):
        print(argcount('error', '-'), l)


def setup_param(l, res):
    type_ = l[0]
    name = l[1]
    if type_ == 'IN_8':
        setup_plocal(0x80, name, 1, res)
    elif type_ == 'IN_16':
        setup_plocal(0x81, name, 2, res)
    elif type_ == 'IN_32':
        setup_plocal(0x82, name, 4, res)
    elif type_ == 'IN_F':
        setup_plocal(0x83, name, 4, res)
    elif type_ == 'IN_S':
        setup_plocal(0x84, name, get_value(l[2]), res)
    elif type_ == 'OUT_8':
        setup_plocal(0x40, name, 1, res)
    elif type_ == 'OUT_16':
        setup_plocal(0x41, name, 2, res)
    elif type_ == 'OUT_32':
        setup_plocal(0x42, name, 4, res)
    elif type_ == 'OUT_F':
        setup_plocal(0x43, name, 4, res)
    elif type_ == 'OUT_S':
        setup_plocal(0x82, name, get_value(l[2]), res)
    elif type_ == 'IO_8':
        setup_plocal(0xc0, name, 1, res)
    elif type_ == 'IO_16':
        setup_plocal(0xc1, name, 2, res)
    elif type_ == 'IO_32':
        setup_plocal(0xc2, name, 4, res)
    elif type_ == 'IO_F':
        setup_plocal(0xc3, name, 4, res)
    elif type_ == 'IO_S':
        setup_plocal(0xc4, name, get_value(l[2]), res)


def setup_plocal(code, name, len_, res):
    setup_local(name, len_)
    add([code], res)
    if code in (0x44, 0x84, 0xc4):
        add([len_], res)


def get_value(i):
    global thisobject, asm_globals

    if is_number(i):
        return i
    if i in asm_globals:
        if get_global(i)['type'] == 'enum':
            return get_global(i)['value']
        if get_global(i)['type'] == 'define':
            return get_global(i)['value']
    print('***', i, 'undefined', '***', 'in', thisobject)
    return 0


def setup_data_global(type_, name):
    if type_ == 'DATA8':
        setup_global(name, 1)
    elif type_ == 'DATA16':
        setup_global(name, 2)
    elif type_ == 'HANDLE':
        setup_global(name, 2)
    elif type_ == 'DATA32':
        setup_global(name, 4)
    elif type_ == 'DATAF':
        setup_global(name, 4)


def setup_data_local(type_, name):
    if type_ == 'DATA8':
        setup_local(name, 1)
    elif type_ == 'DATA16':
        setup_local(name, 2)
    elif type_ == 'HANDLE':
        setup_local(name, 2)
    elif type_ == 'DATA32':
        setup_local(name, 4)
    elif type_ == 'DATAF':
        setup_local(name, 4)


def setup_global(name, len_):
    global next_global

    if len_ == 2:
        next_global = align(next_global, 2)
    elif len_ == 4:
        next_global = align(next_global, 4)
    setup_define(name, next_global, 'global')
    get_global(name)['size'] = len_
    next_global += len_


def setup_local(name, len_):
    global next_local, locals_

    if len_ == 2:
        next_local = align(next_local, 2)
    elif len_ == 4:
        next_local = align(next_local, 4)
    get_global(name)['local'] = next_local
    next_local += len_
    locals_.append(get_global(name))


def expand_call_arg(l):
    if get_global(l[1])['type'] != 'subcall':
        return 1
    return [l[0], l[1], get_global(l[1])['params']] + l[2:]


def pass1_str(s):
    if len(s) == 2:
        if s[0] == '_':
            return make_lc(ord(s[1]))
    return [0x80] + strbytes(s) + [0]


def is_param(x):
    return not re.sub(r'(IN|OUT|IO)_(8|16|32|F|S)', '', str(x))


def addbits(bits, n):
    if is_number(n):
        return [n + bits]
    return [n[0] + bits] + n[1:]


def make_lc(n):
    if -32 < n < 32:
        return [n & 0x3f]
    if -128 < n < 128:
        return [0x81, n & 0xff]
    if -32768 < n < 32768:
        return [0x82, n & 0xff, (n >> 8) & 0xff]
    return [0x83, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff]


def make_hnd(n):
    if -128 < n < 128:
        return [0x91, n & 0xff]
    return [0x92, n & 0xff, n >> 8]


def make_adr(n):
    if -128 < n < 128:
        return [0x89, n & 0xff]
    if -32768 < n < 32768:
        return [0x8a, n & 0xff, (n >> 8) & 0xff]
    return [0x8b, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff]


def get_template(l):
    t = get_global(l[0])['args']
    if 'SUBP' not in t:
        return t
    return t[0:-2] + get_global(t[-1] + '_' + l[len(t) - 2])['args']


def add(l, res):

    if not l:
        return
    res += l


def pass2(code):
    pass2a(code)
    return pass2b(code)


def pass2a(code):
    global pc

    pc = headersize()
    for i in code:
        if is_number(i):
            pc += 1
        else:
            pass2_syma(i)


def pass2_syma(s):
    global pc

    if s[-1] == ':':
        get_global(s[:-1])['value'] = pc
        return
    if s[0] == '&':
        get_global(s[1:])['offset'] = pc
        return
    pc += 3


def pass2b(code):
    res = []
    for i in code:
        if is_number(i):
            res += [i]
        else:
            if 'type' in get_global(i) and get_global(i)['type'] == 'label':
                offset = get_global(i)['value'] - (headersize() + len(res)) - 3
                res += [0x82, offset & 0xff, (offset >> 8) & 0xff]
    return res


def hexl(l):
    res = []
    for i in [l]:
        if is_number(i):
            i = hexw(i, 2)
        res += i
    return res


def erase_locals():
    global locals_, next_local

    for i in locals_:
        i.pop('local')
    locals_ = []
    next_local = 0


def getvalue(l):
    v = []
    for i in l:
        v.append(get_a_value(i))
    if len(v) == 1:
        return v[0]
    if '+' in v:
        return run(v)
    if '-' in v:
        return run(v)
    if '*' in v:
        return run(v)
    if '/' in v:
        return run(v)
    return v


def get_a_value(x):
    if x in ('+', '-', '*', '/'):
        return x
    if is_number(x):
        return x
    if is_string(x):
        return x
    return get_global(x)['value']


def align(n, a):
    n += a - 1
    return a * (n // a)


def strbytes(s):
    s = s.replace('\\r', chr(13))
    s = s.replace('\\n', chr(10))
    s = s.replace('\\q', chr(34))
    s = s.replace('\\t', chr(9))
    res = []
    for c in s:
        res += [ord(c)]
    return res


def listtofile(file_, l):
    with open(file_, 'wb') as f:
        f.write(bytearray(l))


def lname(n):
    global thisobject

    return thisobject['name'] + '-' + n


def is_number(a):
    return type(a) in (int, float)


def is_string(a):
    global asm_globals

    return type(a) is str


def int32bytes(n):
    return int16bytes(n & 0xffff) + int16bytes((n >> 16) & 0xffff)


def int16bytes(n):
    return [n & 0xff, (n >> 8) & 0xff]


def defines_():
    global defines

    for i in defines:
        print(i)


def app_startup():
    global defines, locals_, is_listing

    if 'defines' in globals():
        return
    defines = []
    locals_ = []
    read_enums()
    read_opdefs()
    read_defines()
    is_listing = False
    if len(sys.argv) != 2:
        print("Bad command line args", file=sys.stderr)
    assemble(sys.argv[1])


if __name__ == '__main__':
    app_startup()
