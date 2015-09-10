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
import os
import sys
from ctypes import *

from lms2012 import *

def parse_program_header(infile, size):
    header = ProgramHeader()
    infile.readinto(header)
    if header.lego != 'LEGO':
        raise ValueError("Bad file - does not start with 'LEGO'")
    if header.size != size:
        raise ValueError("Bad file - size is incorrect")
    return header.byte_code_version, header.num_objects, header.global_bytes

def parse_object_header(infile):
    header = ObjectHeader()
    infile.readinto(header)
    return header

def parse_object(infile, outfile, i):
    header = parse_object_header(infile)
    save_position = infile.tell()
    infile.seek(header.offset)
    num_args = 0
    arg_bytes = 0
    if header.is_vmthread:
        type = "vmthread"
    elif header.is_subcall:
        type = "subcall"
        num_args = ord(infile.read(1))
    elif header.is_block:
        type = "block"
    else:
        raise ValueError("Unknown object type")
    print("{0} OBJECT{1}".format(type, i+1), file=outfile)
    print("{", file=outfile)
    if num_args:
        for i in range(num_args):
            type = Callparam(ord(infile.read(1)))
            format = type.data_format
            string_size = 0
            if format is DataFormat.DATA_S:
                string_size = ord(infile.read(1))
            string_size_str = ''
            if string_size:
                string_size_str = " {0}".format(string_size)
            print("\t", type.name, " LOCAL", arg_bytes, string_size_str, sep='', file=outfile)
            arg_bytes += string_size or format.size

        print(file=outfile)
    if header.local_bytes - arg_bytes:
        for i in range(arg_bytes, header.local_bytes):
            print("\tDATA8 LOCAL", i, sep='', file=outfile)
        print(file=outfile)
    while True:
        offset = infile.tell()
        line = parse_ops(infile, header.offset)
        if not line:
            break
        print("OFFSET", offset - header.offset, ":", sep='', file=outfile)
        if line == "RETURN()":
            # skip printing "RETURN()" if it is the last op in an object
            peek = ord(infile.read(1))
            infile.seek(-1, os.SEEK_CUR)
            if peek == Op.OBJECT_END.value:
                continue
        print("\t", line, sep='', file=outfile)
    print("}", file=outfile)
    infile.seek(save_position)

def parse_ops(infile, start):
    op = Op(ord(infile.read(1)))
    if op == Op.OBJECT_END:
        return None
    params = []
    for param in op.params:
        if isinstance(param, Subparam):
            value = parse_param(param, infile)
            params.append(parse_subparam(param, value, infile))
        else:
            params.append(parse_param(param, infile))
        # special handling for CALL
        if op.name == "CALL" and param is Param.PAR16:
            params[-1] = "OBJECT{0}".format(params[-1])
        # special handling for varargs
        if param is Param.PARNO:
            value = int(params[-1])
            del params[-1]
            for i in range(value):
                params.append(parse_param(Param.PARV, infile))
    # special handling for jump ops
    if op.name[:2] == "JR":
        offset = int(params[-1])
        del params[-1]
        params.append("OFFSET{0}".format(infile.tell() - start + offset))
    return "{0}({1})".format(op.name, ",".join(params))

def parse_param(param, infile):
    first_byte = ord(infile.read(1))
    if first_byte & PRIMPAR_LONG:
        if first_byte & PRIMPAR_VARIABLE:
            if first_byte & PRIMPAR_GLOBAL:
                scope = 'GLOBAL'
            else:
                scope = 'LOCAL'
            size = first_byte & PRIMPAR_BYTES
            if size == PRIMPAR_1_BYTE:
                data = Data8()
            elif size == PRIMPAR_2_BYTES:
                data = Data16()
            elif size == PRIMPAR_4_BYTES:
                data == Data32()
            infile.readinto(data)
            handle = ''
            if first_byte & PRIMPAR_HANDLE:
                handle = '@'
            elif first_byte & PRIMPAR_ADDR:
                raise NotImplementedError()
            return "{0}{1}{2}".format(handle,scope,data.value)
        else: # PRIMPAR_CONST
            if first_byte & PRIMPAR_LABEL:
                return "LABEL{0}".format(ord(infile.read(1)))
            size = first_byte & PRIMPAR_BYTES
            if param is Param.PARF:
                if size != PRIMPAR_4_BYTES:
                    raise ValueError("Expecting float value")
                data = DataFloat()
                infile.readinto(data)
                int_value = c_int.from_buffer(data).value
                if int_value == DATAF_MAX:
                    return "DATAF_MAX"
                if int_value == DATAF_MIN:
                    return "DATAF_MIN"
                if int_value == DATAF_NAN:
                    return "DATAF_NAN"
                return str(data.value) + "F"
            if size == PRIMPAR_STRING_OLD or size == PRIMPAR_STRING:
                return parse_string(infile)
            elif size == PRIMPAR_1_BYTE:
                data = Data8()
            elif size == PRIMPAR_2_BYTES:
                data = Data16()
            elif size == PRIMPAR_4_BYTES:
                data = Data32()
            infile.readinto(data)
            return str(data.value)
    else:  # PRIMPAR_SHORT
        if first_byte & PRIMPAR_VARIABLE:
            if first_byte & PRIMPAR_GLOBAL:
                scope = 'GLOBAL'
            else:
                scope = 'LOCAL'
            return "{0}{1}".format(scope, first_byte & PRIMPAR_INDEX)
        else:
            if first_byte & PRIMPAR_CONST_SIGN:
                # special handling for negative numbers
                return str((first_byte & PRIMPAR_VALUE) - (PRIMPAR_VALUE + 1))
            return str(first_byte & PRIMPAR_VALUE)

    raise NotImpementedError("TODO")

def parse_subparam(type, value, infile):
    subcode_type = type.subcode_type(int(value))
    params = [ subcode_type.name ]
    for param in subcode_type.params:
        params.append(parse_param(param, infile))
        # special handling for varargs
        if param is Param.PARNO:
            if not int(params[-1]):
                del params[-1]
            else:
                for i in range(int(params[-1])):
                    params.append(parse_param(Param.PARV, infile))
    return ",".join(params)

def parse_string(infile):
    value = ''
    while True:
        ch = infile.read(1)
        if not ord(ch):
            break
        value += ch
    value = value.replace("\t", "\\t")
    value = value.replace("\r", "\\r")
    value = value.replace("\n", "\\n")
    value = value.replace("\"", "\\q")
    return "'{0}'".format(value)

def main():
    parser = argparse.ArgumentParser(description='Disassemble lms2012 byte codes.')
    parser.add_argument('input', type=argparse.FileType('rb', 0),
                       help='The .rbf file to disassemble.')
    parser.add_argument('-o', '--output', type=argparse.FileType('wb', 0), default='-',
                       help='The .lms file that will contain the result.')
    args = parser.parse_args()

    file_size = os.path.getsize(args.input.name)
    version, num_objs, global_bytes = parse_program_header(args.input, file_size)
    print("// Disassembly of", args.input.name, file=args.output)
    print("//", file=args.output)
    print("// Byte code version:", version, file=args.output)
    print(file=args.output)
    for i in range(global_bytes):
        print("DATA8 GLOBAL", i, sep='', file=args.output)
    for i in range(num_objs):
        print(file=args.output)
        parse_object(args.input, args.output, i)

if __name__ == '__main__':
    main()
