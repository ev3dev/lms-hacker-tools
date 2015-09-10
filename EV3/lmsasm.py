#!/usr/bin/env python

# The MIT License (MIT)

# Copyright (c) 2015 David Lechner <david@lechnology.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import print_function
import argparse
import collections
import re
import os
from ctypes import *

from lms2012 import *

Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

def tokenize(s):
    keywords = { 'define', 'vmthread', 'subcall' }
    token_specification = [
        ('NUMBER',              r'\d+(\.\d*)?'), # Integer or decimal number
        ('PARAM_LIST_START',    r'\('),          # Start of parameter list
        ('PARAM_LIST_END',      r'\)'),          # End of parameter list
        ('BLOCK_START',         r'\{'),          # Start of block
        ('BLOCK_END',           r'\}'),          # End of block
        ('LIST_SEPARATOR',      r','),           # List separator
        ('LABEL',               r'[A-Za-z_][A-Za-z_0-9]*:'), # Label
        ('IDENTIFIER',          r'[A-Za-z_][A-Za-z_0-9]*'),  # Identifiers
        ('NEWLINE',             r'[\r\n]+'),     # Line endings
        ('WHITESPACE',          r'[ \t]+'),      # Whitespace
        ('INLINE_COMMENT',      r'//[^\r\n]*'),  # Inline comment
        ('BLOCK_COMMENT',       r'/\*.*\*/'),    # Block comment
    ]
    trivia_types = [ 'WHITESPACE', 'INLINE_COMMENT', 'BLOCK_COMMENT' ]
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    get_token = re.compile(token_regex, re.DOTALL).match
    line = 1
    pos = line_start = 0
    mo = get_token(s)
    line_has_tokens = False
    while mo is not None:
        typ = mo.lastgroup
        if typ == 'NEWLINE':
            if line_has_tokens:
                yield Token('EOL', '<EOL>', line, mo.start()-line_start)
            line_start = pos
            line += 1
            line_has_tokens = False
        elif not typ in trivia_types:
            val = mo.group(typ)
            if typ == 'IDENTIFIER' and val in keywords:
                typ = val.upper()
            yield Token(typ, val, line, mo.start()-line_start)
            line_has_tokens = True
        pos = mo.end()
        mo = get_token(s, pos)
    if line_has_tokens:
        # handle case where file does not have trailing newline
        yield Token('EOL', '', line, line_start)
    if pos != len(s):
        raise RuntimeError('Unexpected character %r on line %d' %(s[pos], line))

Expression = collections.namedtuple('Expression', ['typ', 'token', 'byte_codes'])

def expect_token(t, typ):
    token = t and t[0]
    if token and token.typ == typ:
        t.pop(0)
        return token
    return None

def require_token(t, typ):
    token = expect_token(t, typ)
    if not token:
        raise RuntimeError('Expecting %r at %d:%d' %(typ, t[0].line, t[0].column))
    return token

def expect_literal_expression(t):
    return expect_numeric_literal_expression(t) or expect_string_literal_expression(t, 'STRING')

def require_literal_expression(t):
    expression = expect_literal_expression(t)
    if not expression:
        raise RuntimeError('Expecting literal at %d:%d' %(t[0].line, t[0].column))
    return expression

def expect_numeric_literal_expression(t):
    token = expect_token(t, 'NUMBER')
    if token:
        value = int(token.value)
        abs_value = abs(value)
        if (abs_value) > DATA32_MAX:
            raise RuntimeError('Integer value out of range at %d:%d' %(token.line, token.column))
        if abs_value > DATA16_MAX:
            byte_codes = (PRIMPAR_LONG | PRIMPAR_CONST | PRIMPAR_4_BYTES,
                value & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 24) & 0xFF,)
        elif abs_value > DATA8_MAX:
            byte_codes = (PRIMPAR_LONG | PRIMPAR_CONST | PRIMPAR_2_BYTES,
                value & 0xFF,
                (value >> 8),)
        elif abs_value > LC0_MAX:
            byte_codes = (PRIMPAR_LONG | PRIMPAR_CONST | PRIMPAR_1_BYTE,
                value & 0xFF,)
        else:
            byte_codes = (PRIMPAR_SHORT | PRIMPAR_CONST | (value & PRIMPAR_VALUE),)
        return Expression('LITERAL', token, byte_codes)
    return None

def expect_string_literal_expression(t):
    token = expect_token(t, 'STRING')
    if token:
        return Expression('LITERAL', token, byte_codes)
    return None

def expect_identifier(t, enum):
    token = t and t[0]
    print(token)
    if token and token.typ == 'IDENTIFIER':
        if token.value in enum.__members__:
            t.pop(0)
            return token
    return None

def require_identifier(t, enum):
    token = expect_identifier(t, enum)
    if not token:
        raise RuntimeError('Expecting %r at %d:%d' %(enum, t[0].line, t[0].column))
    return token

def expect_variable_reference_expression(t):
    token = expect_token(t, 'IDENTIFIER')
    if token:
        # TODO: lookup variable
        return Expression('VARIABLE', token, ())
    return None

def require_expression(t):
    expression = expect_variable_reference_expression(t) or expect_literal_expression(t)
    if not expression:
        raise RuntimeError('Expecting expression at %d:%d' %(t[0].line, t[0].column))
    return expression

global_constants = {}
global_variables = {}
global_objects = {}
local_constants = {}
local_variables = {}
local_labels = {}

def global_constant(t):
    return define(t, global_constants)

def local_constant(t):
    return define(t, local_constants)

def define(t, constants):
    if expect_token(t, 'DEFINE'):
        id = require_token(t, 'IDENTIFIER')
        value = require_literal_expression(t)
        require_token(t, 'EOL')
        if id.value in constants:
            raise RuntimeError('symbol %r at %d:%d is already defined' %(id.value, id.line, id.column))
        constants[id.value] = value

def global_variable_declaration(t):
    pass

def local_variable_declaration(t):
    pass

def label_declaration(t):
    pass

Statement = collections.namedtuple('Statement', ('token', 'param_list', 'byte_codes'))

def statement_declaration(t):
    token = expect_identifier(t, Op)
    if not token:
        return None

    param_list = []
    require_token(t, 'PARAM_LIST_START')
    op = Op[token.value]
    first = True
    for param in op.params:
        if first:
            first = False
        else:
            require_token(t, 'LIST_SEPARATOR')
        if isinstance(param, Subparam):
            subparam_token = require_identifier(t, param.subcode_type)
            subparam_type = param.subcode_type[subparam_token.value]
            expression = Expression('SUBPARAM', subparam_token, (subparam_type.value,))
            param_list.append(expression)
            for subparam in subparam_type.params:
                require_token(t, 'LIST_SEPARATOR')
                expression = require_expression(t)
                param_list.append(expression)
                print(expression)
        else:
            expression = require_expression(t)
            param_list.append(expression)
            print(expression)
    require_token(t, 'PARAM_LIST_END')
    require_token(t, 'EOL')
    return Statement(token, param_list, (op.value,))

Object = collections.namedtuple('Object', ('token', 'statement_list', 'byte_codes',))

def object_declaration(t):
    return vmthread_declaration(t) or subcall_declaration(t)

def vmthread_declaration(t):
    token = expect_token(t, 'VMTHREAD')
    if not token:
        return None

    id = require_token(t, 'IDENTIFIER')
    expect_token(t, 'EOL')
    require_token(t, 'BLOCK_START')
    require_token(t, 'EOL')
    statement_list = []
    while True:
        if local_constant(t):
            continue
        if local_variable_declaration(t):
            continue
        if label_declaration(t):
            continue
        statement = statement_declaration(t)
        if statement:
            print(statement)
            statement_list.append(statement)
            continue
        break
    require_token(t, 'BLOCK_END')
    require_token(t, 'EOL')
    return Object(token, statement_list, (),)

def subcall_declaration(t):
    pass

def compile(t):
    token_list = list(tokenize(t))
    for token in token_list:
        print(token)
    obj_list = []
    while True:
        if global_constant(token_list):
            continue
        if global_variable_declaration(token_list):
            continue
        obj = object_declaration(token_list)
        if obj:
            print(obj)
            obj_list.append(obj)
            continue
        break

    if token_list:
        token = token_list[0]
        raise RuntimeError('Unexpected token %r at %d:%d' %(token.value,
            token.line, token.column))
    if not obj_list:
        raise RuntimeError('No objects defined')

    message_counter = (0x00, 0x00)
    command = DIRECT_COMMAND_NO_REPLY
    global_bytes = 0
    local_bytes = 0
    byte_codes = message_counter + (command, global_bytes & 0xFF,
        (local_bytes << 2) & (global_bytes >> 8))
    for obj in obj_list:
        byte_codes += obj.byte_codes
        for s in obj.statement_list:
            byte_codes += s.byte_codes
            for p in s.param_list:
                byte_codes += p.byte_codes
    size = len(byte_codes)
    byte_codes = (size & 0xFF, size >> 8) + byte_codes
    for b in byte_codes:
        print("0x{0:02X}".format(b), end=", ")
    print()

def main():
    parser = argparse.ArgumentParser(description='Compile lms2012 byte codes.')
    parser.add_argument('input', type=argparse.FileType('rb', 0),
                       help='The .lms file to compile.')
    parser.add_argument('-o', '--output', type=argparse.FileType('wb', 0), default='-',
                       help='The .rbf file that will contain the result.')
    args = parser.parse_args()

    tokens = args.input.read()
    compile(tokens)

if __name__ == '__main__':
    main()
