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
from ctypes import *

# Requires `enum34` package, *not* `enum` package
#
# apt-get install python-enum34
# - or -
# pip install enum34
from enum import Enum

class DataFormat(Enum):
    DATA8        = 0x00
    DATA16       = 0x01
    DATA32       = 0x02
    DATAF        = 0x03
    DATAS        = 0x04
    DATAA        = 0x05
    DATAV        = 0x07
    DATAPCT      = 0x10
    DATARAW      = 0x12
    DATASI       = 0x13

    @property
    def size(self):
        return _DATAFormat_size[self]

_DATAFormat_size = {
    DataFormat.DATA8: 1,
    DataFormat.DATA16: 2,
    DataFormat.DATA32: 4,
    DataFormat.DATAF: 4,
    DataFormat.DATAS: 1,
    DataFormat.DATAA: 1,
    DataFormat.DATAV: 1,
    DataFormat.DATAPCT: 4,
    DataFormat.DATARAW: 4,
    DataFormat.DATASI: 4,
}

class Param(Enum):
    SUBP                = 0x01
    PARNO               = 0x02
    PARLAB              = 0x03
    PARVALUES           = 0x04
    PAR8                = 0x08 + DataFormat.DATA8.value
    PAR16               = 0x08 + DataFormat.DATA16.value
    PAR32               = 0x08 + DataFormat.DATA32.value
    PARF                = 0x08 + DataFormat.DATAF.value
    PARS                = 0x08 + DataFormat.DATAS.value
    PARV                = 0x08 + DataFormat.DATAV.value

class Subparam(Enum):
    UI_READ_SUBP    = 0
    UI_WRITE_SUBP   = 1
    UI_DRAW_SUBP    = 2
    UI_BUTTON_SUBP  = 3
    FILE_SUBP       = 4
    PROGRAM_SUBP    = 5
    VM_SUBP         = 6
    TST_SUBP        = 6
    STRING_SUBP     = 7
    COM_READ_SUBP   = 8
    COM_WRITE_SUBP  = 9
    SOUND_SUBP      = 10
    INPUT_SUBP      = 11
    ARRAY_SUBP      = 12
    MATH_SUBP       = 13
    COM_GET_SUBP    = 14
    COM_SET_SUBP    = 15
    FILENAME_SUBP   = 16

    @property
    def subcode_type(self):
        return _subcode_enums[self]

class Op(Enum):
    # VM
    #                                    0000....
    ERROR                     = 0x00 #       0000
    NOP                       = 0x01 #       0001
    PROGRAM_STOP              = 0x02 #       0010
    PROGRAM_START             = 0x03 #       0011
    OBJECT_STOP               = 0x04 #       0100
    OBJECT_START              = 0x05 #       0101
    OBJECT_TRIG               = 0x06 #       0110
    OBJECT_WAIT               = 0x07 #       0111
    RETURN                    = 0x08 #       1000
    CALL                      = 0x09 #       1001
    OBJECT_END                = 0x0A #       1010
    SLEEP                     = 0x0B #       1011
    PROGRAM_INFO              = 0x0C #       1100
    LABEL                     = 0x0D #       1101
    PROBE                     = 0x0E #       1110
    DO                        = 0x0F #       1111

    # cMath "MATH"
    #                                    0001....
    #                    ADD                 00..
    ADD8                      = 0x10 #         00
    ADD16                     = 0x11 #         01
    ADD32                     = 0x12 #         10
    ADDF                      = 0x13 #         11
    #                    SUB                 01..
    SUB8                      = 0x14 #         00
    SUB16                     = 0x15 #         01
    SUB32                     = 0x16 #         10
    SUBF                      = 0x17 #         11
    #                    MUL                 10..
    MUL8                      = 0x18 #         00
    MUL16                     = 0x19 #         01
    MUL32                     = 0x1A #         10
    MULF                      = 0x1B #         11
    #                    DIV                 11..
    DIV8                      = 0x1C #         00
    DIV16                     = 0x1D #         01
    DIV32                     = 0x1E #         10
    DIVF                      = 0x1F #         11

    # Logic "LOGIC"
    #        LOGIC                       0010....
    #                    OR                  00..
    OR8                       = 0x20 #         00
    OR16                      = 0x21 #         01
    OR32                      = 0x22 #         10

    #                    AND                 01..
    AND8                      = 0x24 #         00
    AND16                     = 0x25 #         01
    AND32                     = 0x26 #         10

    #                    XOR                 10..
    XOR8                      = 0x28 #         00
    XOR16                     = 0x29 #         01
    XOR32                     = 0x2A #         10

    #                    RL                  11..
    RL8                       = 0x2C #         00
    RL16                      = 0x2D #         01
    RL32                      = 0x2E #         10

    # cMove "MOVE"
    INIT_BYTES                = 0x2F #       1111
    #        MOVE                        0011....
    #                    MOVE8_              00..
    MOVE8_8                   = 0x30 #         00
    MOVE8_16                  = 0x31 #         01
    MOVE8_32                  = 0x32 #         10
    MOVE8_F                   = 0x33 #         11
    #                    MOVE16_             01..
    MOVE16_8                  = 0x34 #         00
    MOVE16_16                 = 0x35 #         01
    MOVE16_32                 = 0x36 #         10
    MOVE16_F                  = 0x37 #         11
    #                    MOVE32_             10..
    MOVE32_8                  = 0x38 #         00
    MOVE32_16                 = 0x39 #         01
    MOVE32_32                 = 0x3A #         10
    MOVE32_F                  = 0x3B #         11
    #                    MOVEF_              11..
    MOVEF_8                   = 0x3C #         00
    MOVEF_16                  = 0x3D #         01
    MOVEF_32                  = 0x3E #         10
    MOVEF_F                   = 0x3F #         11

    # cBranch "BRANCH"
    #        BRANCH                      010000..
    JR                        = 0x40 #         00
    JR_FALSE                  = 0x41 #         01
    JR_TRUE                   = 0x42 #         10
    JR_NAN                    = 0x43 #         11

    # cCompare "COMPARE"
    #        COMPARE                     010.....
    #                    CP_LT              001..
    CP_LT8                    = 0x44 #         00
    CP_LT16                   = 0x45 #         01
    CP_LT32                   = 0x46 #         10
    CP_LTF                    = 0x47 #         11
    #                    CP_GT              010..
    CP_GT8                    = 0x48 #         00
    CP_GT16                   = 0x49 #         01
    CP_GT32                   = 0x4A #         10
    CP_GTF                    = 0x4B #         11
    #                    CP_EQ              011..
    CP_EQ8                    = 0x4C #         00
    CP_EQ16                   = 0x4D #         01
    CP_EQ32                   = 0x4E #         10
    CP_EQF                    = 0x4F #         11
    #                    CP_NEQ             100..
    CP_NEQ8                   = 0x50 #         00
    CP_NEQ16                  = 0x51 #         01
    CP_NEQ32                  = 0x52 #         10
    CP_NEQF                   = 0x53 #         11
    #                    CP_LTEQ            101..
    CP_LTEQ8                  = 0x54 #         00
    CP_LTEQ16                 = 0x55 #         01
    CP_LTEQ32                 = 0x56 #         10
    CP_LTEQF                  = 0x57 #         11
    #                    CP_GTEQ            110..
    CP_GTEQ8                  = 0x58 #         00
    CP_GTEQ16                 = 0x59 #         01
    CP_GTEQ32                 = 0x5A #         10
    CP_GTEQF                  = 0x5B #         11

    # Select "SELECT"
    #        SELECT                      010111..
    SELECT8                   = 0x5C #         00
    SELECT16                  = 0x5D #         01
    SELECT32                  = 0x5E #         10
    SELECTF                   = 0x5F #         11


    # VM
    SYSTEM                    = 0x60
    PORT_CNV_OUTPUT           = 0x61
    PORT_CNV_INPUT            = 0x62
    NOTE_TO_FREQ              = 0x63

    # cBranch "BRANCH"
    #        BRANCH                      011000..
                                      #?       00
                                      #?       01
                                      #?       10
                                      #?       11
    #                    JR_LT              001..
    JR_LT8                    = 0x64 #         00
    JR_LT16                   = 0x65 #         01
    JR_LT32                   = 0x66 #         10
    JR_LTF                    = 0x67 #         11
    #                    JR_GT              010..
    JR_GT8                    = 0x68 #         00
    JR_GT16                   = 0x69 #         01
    JR_GT32                   = 0x6A #         10
    JR_GTF                    = 0x6B #         11
    #                    JR_EQ              011..
    JR_EQ8                    = 0x6C #         00
    JR_EQ16                   = 0x6D #         01
    JR_EQ32                   = 0x6E #         10
    JR_EQF                    = 0x6F #         11
    #                    JR_NEQ             100..
    JR_NEQ8                   = 0x70 #         00
    JR_NEQ16                  = 0x71 #         01
    JR_NEQ32                  = 0x72 #         10
    JR_NEQF                   = 0x73 #         11
    #                    JR_LTEQ            101..
    JR_LTEQ8                  = 0x74 #         00
    JR_LTEQ16                 = 0x75 #         01
    JR_LTEQ32                 = 0x76 #         10
    JR_LTEQF                  = 0x77 #         11
    #                    JR_GTEQ            110..
    JR_GTEQ8                  = 0x78 #         00
    JR_GTEQ16                 = 0x79 #         01
    JR_GTEQ32                 = 0x7A #         10
    JR_GTEQF                  = 0x7B #         11

    # VM
    INFO                      = 0x7C #   01111100
    STRINGS                   = 0x7D #   01111101
    MEMORY_WRITE              = 0x7E #   01111110
    MEMORY_READ               = 0x7F #   01111111

    #        SYSTEM                      1.......

    # cUi "UI"
    #        UI                          100000..
    UI_FLUSH                  = 0x80 #         00
    UI_READ                   = 0x81 #         01
    UI_WRITE                  = 0x82 #         10
    UI_BUTTON                 = 0x83 #         11
    UI_DRAW                   = 0x84 #   10000100

    # cTimer "TIMER"
    TIMER_WAIT                = 0x85 #   10000101
    TIMER_READY               = 0x86 #   10000110
    TIMER_READ                = 0x87 #   10000111

    # VM
    #        BREAKPOINT                  10001...
    BP0                       = 0x88 #        000
    BP1                       = 0x89 #        001
    BP2                       = 0x8A #        010
    BP3                       = 0x8B #        011
    BP_SET                    = 0x8C #   10001100
    MATH                      = 0x8D #   10001101
    RANDOM                    = 0x8E #   10001110

    # cTimer "TIMER"
    TIMER_READ_US             = 0x8F #   10001111

    # cUi "UI"
    KEEP_ALIVE                = 0x90 #   10010000

    # cCom "COM"
    #                                      100100
    COM_READ                  = 0x91 #         01
    COM_WRITE                 = 0x92 #         10

    # cSound "SOUND"
    #                                      100101
    SOUND                     = 0x94 #         00
    SOUND_TEST                = 0x95 #         01
    SOUND_READY               = 0x96 #         10

    # cInput "INPUT"
    #
    INPUT_SAMPLE              = 0x97 #   10010111

    #                                    10011...
    INPUT_DEVICE_LIST         = 0x98 #        000
    INPUT_DEVICE              = 0x99 #        001
    INPUT_READ                = 0x9A #        010
    INPUT_TEST                = 0x9B #        011
    INPUT_READY               = 0x9C #        100
    INPUT_READSI              = 0x9D #        101
    INPUT_READEXT             = 0x9E #        110
    INPUT_WRITE               = 0x9F #        111
    # cOutput "OUTPUT"
    #                                    101.....
    OUTPUT_GET_TYPE           = 0xA0 #      00000
    OUTPUT_SET_TYPE           = 0xA1 #      00001
    OUTPUT_RESET              = 0xA2 #      00010
    OUTPUT_STOP               = 0xA3 #      00011
    OUTPUT_POWER              = 0xA4 #      00100
    OUTPUT_SPEED              = 0xA5 #      00101
    OUTPUT_START              = 0xA6 #      00110
    OUTPUT_POLARITY           = 0xA7 #      00111
    OUTPUT_READ               = 0xA8 #      01000
    OUTPUT_TEST               = 0xA9 #      01001
    OUTPUT_READY              = 0xAA #      01010
    OUTPUT_POSITION           = 0xAB #      01011
    OUTPUT_STEP_POWER         = 0xAC #      01100
    OUTPUT_TIME_POWER         = 0xAD #      01101
    OUTPUT_STEP_SPEED         = 0xAE #      01110
    OUTPUT_TIME_SPEED         = 0xAF #      01111

    OUTPUT_STEP_SYNC          = 0xB0 #      10000
    OUTPUT_TIME_SYNC          = 0xB1 #      10001
    OUTPUT_CLR_COUNT          = 0xB2 #      10010
    OUTPUT_GET_COUNT          = 0xB3 #      10011

    OUTPUT_PRG_STOP           = 0xB4 #      10100

    # cMemory "MEMORY"
    #                                    11000...
    FILE                      = 0xC0 #        000
    ARRAY                     = 0xC1 #        001
    ARRAY_WRITE               = 0xC2 #        010
    ARRAY_READ                = 0xC3 #        011
    ARRAY_APPEND              = 0xC4 #        100
    MEMORY_USAGE              = 0xC5 #        101
    FILENAME                  = 0xC6 #        110

    # cMove "READ"
    #                                    110010..
    READ8                     = 0xC8 #         00
    READ16                    = 0xC9 #         01
    READ32                    = 0xCA #         10
    READF                     = 0xCB #         11

    # cMove "WRITE"
    #                                    110011..
    WRITE8                    = 0xCC #         00
    WRITE16                   = 0xCD #         01
    WRITE32                   = 0xCE #         10
    WRITEF                    = 0xCF #         11

    # cCom "COM"
    #                                    11010...
    COM_READY                 = 0xD0 #        000
    COM_READDATA              = 0xD1 #        001
    COM_WRITEDATA             = 0xD2 #        010
    COM_GET                   = 0xD3 #        011
    COM_SET                   = 0xD4 #        100
    COM_TEST                  = 0xD5 #        101
    COM_REMOVE                = 0xD6 #        110
    COM_WRITEFILE             = 0xD7 #        111

    #                                    11011...
    MAILBOX_OPEN              = 0xD8 #        000
    MAILBOX_WRITE             = 0xD9 #        001
    MAILBOX_READ              = 0xDA #        010
    MAILBOX_TEST              = 0xDB #        011
    MAILBOX_READY             = 0xDC #        100
    MAILBOX_CLOSE             = 0xDD #        101

    #        SPARE                       111.....

    # TST
    TST                       = 0xFF  #  11111111

    @property
    def params(self):
        return _op_code_params[self]

_op_code_params = {
    #    VM
    Op.ERROR:                (),
    Op.NOP:                  (),
    Op.PROGRAM_STOP:         (Param.PAR16,),
    Op.PROGRAM_START:        (Param.PAR16, Param.PAR32, Param.PAR32, Param.PAR8),
    Op.OBJECT_STOP:          (Param.PAR16,),
    Op.OBJECT_START:         (Param.PAR16,),
    Op.OBJECT_TRIG:          (Param.PAR16,),
    Op.OBJECT_WAIT:          (Param.PAR16,),
    Op.RETURN:               (),
    Op.CALL:                 (Param.PAR16, Param.PARNO),
    Op.OBJECT_END:           (),
    Op.SLEEP:                (),
    Op.PROGRAM_INFO:         (Subparam.PROGRAM_SUBP,),
    Op.LABEL:                (Param.PARLAB,),
    Op.PROBE:                (Param.PAR16, Param.PAR16, Param.PAR32, Param.PAR32),
    Op.DO:                   (Param.PAR16, Param.PAR32, Param.PAR32),
    #    Math
    Op.ADD8:                 (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.ADD16:                (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.ADD32:                (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.ADDF:                 (Param.PARF, Param.PARF, Param.PARF),
    Op.SUB8:                 (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.SUB16:                (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.SUB32:                (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.SUBF:                 (Param.PARF, Param.PARF, Param.PARF),
    Op.MUL8:                 (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.MUL16:                (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.MUL32:                (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.MULF:                 (Param.PARF, Param.PARF, Param.PARF),
    Op.DIV8:                 (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.DIV16:                (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.DIV32:                (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.DIVF:                 (Param.PARF, Param.PARF, Param.PARF),
    #    Logic
    Op.OR8:                  (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.OR16:                 (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.OR32:                 (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.AND8:                 (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.AND16:                (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.AND32:                (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.XOR8:                 (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.XOR16:                (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.XOR32:                (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.RL8:                  (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.RL16:                 (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.RL32:                 (Param.PAR32, Param.PAR32, Param.PAR32),
    #    Move
    Op.INIT_BYTES:           (Param.PAR8, Param.PAR32, Param.PARVALUES, Param.PAR8),
    Op.MOVE8_8:              (Param.PAR8, Param.PAR8),
    Op.MOVE8_16:             (Param.PAR8, Param.PAR16),
    Op.MOVE8_32:             (Param.PAR8, Param.PAR32),
    Op.MOVE8_F:              (Param.PAR8, Param.PARF),
    Op.MOVE16_8:             (Param.PAR16, Param.PAR8),
    Op.MOVE16_16:            (Param.PAR16, Param.PAR16),
    Op.MOVE16_32:            (Param.PAR16, Param.PAR32),
    Op.MOVE16_F:             (Param.PAR16, Param.PARF),
    Op.MOVE32_8:             (Param.PAR32, Param.PAR8),
    Op.MOVE32_16:            (Param.PAR32, Param.PAR16),
    Op.MOVE32_32:            (Param.PAR32, Param.PAR32),
    Op.MOVE32_F:             (Param.PAR32, Param.PARF),
    Op.MOVEF_8:              (Param.PARF, Param.PAR8),
    Op.MOVEF_16:             (Param.PARF, Param.PAR16),
    Op.MOVEF_32:             (Param.PARF, Param.PAR32),
    Op.MOVEF_F:              (Param.PARF, Param.PARF),
    #    Branch
    Op.JR:                   (Param.PAR32,),
    Op.JR_FALSE:             (Param.PAR8, Param.PAR32),
    Op.JR_TRUE:              (Param.PAR8, Param.PAR32),
    Op.JR_NAN:               (Param.PARF, Param.PAR32),
    #    Compare
    Op.CP_LT8:               (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.CP_LT16:              (Param.PAR16, Param.PAR16, Param.PAR8),
    Op.CP_LT32:              (Param.PAR32, Param.PAR32, Param.PAR8),
    Op.CP_LTF:               (Param.PARF, Param.PARF, Param.PAR8),
    Op.CP_GT8:               (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.CP_GT16:              (Param.PAR16, Param.PAR16, Param.PAR8),
    Op.CP_GT32:              (Param.PAR32, Param.PAR32, Param.PAR8),
    Op.CP_GTF:               (Param.PARF, Param.PARF, Param.PAR8),
    Op.CP_EQ8:               (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.CP_EQ16:              (Param.PAR16, Param.PAR16, Param.PAR8),
    Op.CP_EQ32:              (Param.PAR32, Param.PAR32, Param.PAR8),
    Op.CP_EQF:               (Param.PARF, Param.PARF, Param.PAR8),
    Op.CP_NEQ8:              (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.CP_NEQ16:             (Param.PAR16, Param.PAR16, Param.PAR8),
    Op.CP_NEQ32:             (Param.PAR32, Param.PAR32, Param.PAR8),
    Op.CP_NEQF:              (Param.PARF, Param.PARF, Param.PAR8),
    Op.CP_LTEQ8:             (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.CP_LTEQ16:            (Param.PAR16, Param.PAR16, Param.PAR8),
    Op.CP_LTEQ32:            (Param.PAR32, Param.PAR32, Param.PAR8),
    Op.CP_LTEQF:             (Param.PARF, Param.PARF, Param.PAR8),
    Op.CP_GTEQ8:             (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.CP_GTEQ16:            (Param.PAR16, Param.PAR16, Param.PAR8),
    Op.CP_GTEQ32:            (Param.PAR32, Param.PAR32, Param.PAR8),
    Op.CP_GTEQF:             (Param.PARF, Param.PARF, Param.PAR8),
    #    Select
    Op.SELECT8:              (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8),
    Op.SELECT16:             (Param.PAR8, Param.PAR16, Param.PAR16, Param.PAR16),
    Op.SELECT32:             (Param.PAR8, Param.PAR32, Param.PAR32, Param.PAR32),
    Op.SELECTF:              (Param.PAR8, Param.PARF, Param.PARF, Param.PARF),

    Op.SYSTEM:               (Param.PAR8, Param.PAR32),
    Op.PORT_CNV_OUTPUT:      (Param.PAR32, Param.PAR8, Param.PAR8, Param.PAR8),
    Op.PORT_CNV_INPUT:       (Param.PAR32, Param.PAR8, Param.PAR8),
    Op.NOTE_TO_FREQ:         (Param.PAR8, Param.PAR16),

    #    Branch
    Op.JR_LT8:               (Param.PAR8, Param.PAR8, Param.PAR32),
    Op.JR_LT16:              (Param.PAR16, Param.PAR16, Param.PAR32),
    Op.JR_LT32:              (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.JR_LTF:               (Param.PARF, Param.PARF, Param.PAR32),
    Op.JR_GT8:               (Param.PAR8, Param.PAR8, Param.PAR32),
    Op.JR_GT16:              (Param.PAR16, Param.PAR16, Param.PAR32),
    Op.JR_GT32:              (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.JR_GTF:               (Param.PARF, Param.PARF, Param.PAR32),
    Op.JR_EQ8:               (Param.PAR8, Param.PAR8, Param.PAR32),
    Op.JR_EQ16:              (Param.PAR16, Param.PAR16, Param.PAR32),
    Op.JR_EQ32:              (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.JR_EQF:               (Param.PARF, Param.PARF, Param.PAR32),
    Op.JR_NEQ8:              (Param.PAR8, Param.PAR8, Param.PAR32),
    Op.JR_NEQ16:             (Param.PAR16, Param.PAR16, Param.PAR32),
    Op.JR_NEQ32:             (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.JR_NEQF:              (Param.PARF, Param.PARF, Param.PAR32),
    Op.JR_LTEQ8:             (Param.PAR8, Param.PAR8, Param.PAR32),
    Op.JR_LTEQ16:            (Param.PAR16, Param.PAR16, Param.PAR32),
    Op.JR_LTEQ32:            (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.JR_LTEQF:             (Param.PARF, Param.PARF, Param.PAR32),
    Op.JR_GTEQ8:             (Param.PAR8, Param.PAR8, Param.PAR32),
    Op.JR_GTEQ16:            (Param.PAR16, Param.PAR16, Param.PAR32),
    Op.JR_GTEQ32:            (Param.PAR32, Param.PAR32, Param.PAR32),
    Op.JR_GTEQF:             (Param.PARF, Param.PARF, Param.PAR32),
    #    VM
    Op.INFO:                 (Subparam.VM_SUBP,),
    Op.STRINGS:              (Subparam.STRING_SUBP,),
    Op.MEMORY_WRITE:         (Param.PAR16, Param.PAR16, Param.PAR32, Param.PAR32, Param.PAR8),
    Op.MEMORY_READ:          (Param.PAR16, Param.PAR16, Param.PAR32, Param.PAR32, Param.PAR8),
    #    UI
    Op.UI_FLUSH:             (),
    Op.UI_READ:              (Subparam.UI_READ_SUBP,),
    Op.UI_WRITE:             (Subparam.UI_WRITE_SUBP,),
    Op.UI_BUTTON:            (Subparam.UI_BUTTON_SUBP,),
    Op.UI_DRAW:              (Subparam.UI_DRAW_SUBP,),
    #    Timer
    Op.TIMER_WAIT:           (Param.PAR32, Param.PAR32),
    Op.TIMER_READY:          (Param.PAR32,),
    Op.TIMER_READ:           (Param.PAR32,),
    #    VM
    Op.BP0:                  (),
    Op.BP1:                  (),
    Op.BP2:                  (),
    Op.BP3:                  (),
    Op.BP_SET:               (Param.PAR16, Param.PAR8, Param.PAR32),
    Op.MATH:                 (Subparam.MATH_SUBP,),
    Op.RANDOM:               (Param.PAR16, Param.PAR16, Param.PAR16),
    Op.TIMER_READ_US:        (Param.PAR32,),
    Op.KEEP_ALIVE:           (Param.PAR8,),
    #    Com
    Op.COM_READ:             (Subparam.COM_READ_SUBP,),
    Op.COM_WRITE:            (Subparam.COM_WRITE_SUBP,),
    #    Sound
    Op.SOUND:                (Subparam.SOUND_SUBP,),
    Op.SOUND_TEST:           (Param.PAR8,),
    Op.SOUND_READY:          (),
    #    Input
    Op.INPUT_SAMPLE:         (Param.PAR32, Param.PAR16, Param.PAR16, Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8, Param.PARF),
    Op.INPUT_DEVICE_LIST:    (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.INPUT_DEVICE:         (Subparam.INPUT_SUBP,),
    Op.INPUT_READ:           (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8),
    Op.INPUT_READSI:         (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8, Param.PARF),
    Op.INPUT_TEST:           (Param.PAR8,),
    Op.INPUT_TEST:           (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.INPUT_READY:          (Param.PAR8, Param.PAR8),
    Op.INPUT_READEXT:        (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8, Param.PARNO),
    Op.INPUT_WRITE:          (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8),
    #    Output
    Op.OUTPUT_SET_TYPE:      (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.OUTPUT_RESET:         (Param.PAR8, Param.PAR8),
    Op.OUTPUT_STOP:          (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.OUTPUT_SPEED:         (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.OUTPUT_POWER:         (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.OUTPUT_START:         (Param.PAR8, Param.PAR8),
    Op.OUTPUT_POLARITY:      (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.OUTPUT_READ:          (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR32),
    Op.OUTPUT_READY:         (Param.PAR8, Param.PAR8),
    Op.OUTPUT_TEST:          (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.OUTPUT_STEP_POWER:    (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR32, Param.PAR32, Param.PAR32, Param.PAR8),
    Op.OUTPUT_TIME_POWER:    (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR32, Param.PAR32, Param.PAR32, Param.PAR8),
    Op.OUTPUT_STEP_SPEED:    (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR32, Param.PAR32, Param.PAR32, Param.PAR8),
    Op.OUTPUT_TIME_SPEED:    (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR32, Param.PAR32, Param.PAR32, Param.PAR8),
    Op.OUTPUT_STEP_SYNC:     (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR16, Param.PAR32, Param.PAR8),
    Op.OUTPUT_TIME_SYNC:     (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR16, Param.PAR32, Param.PAR8),
    Op.OUTPUT_CLR_COUNT:     (Param.PAR8, Param.PAR8),
    Op.OUTPUT_GET_COUNT:     (Param.PAR8, Param.PAR8, Param.PAR32),
    Op.OUTPUT_PRG_STOP:      (),
    #    Memory
    Op.FILE:                 (Subparam.FILE_SUBP,),
    Op.ARRAY:                (Subparam.ARRAY_SUBP,),
    Op.ARRAY_WRITE:          (Param.PAR16, Param.PAR32, Param.PARV),
    Op.ARRAY_READ:           (Param.PAR16, Param.PAR32, Param.PARV),
    Op.ARRAY_APPEND:         (Param.PAR16, Param.PARV),
    Op.MEMORY_USAGE:         (Param.PAR32, Param.PAR32),
    Op.FILENAME:             (Subparam.FILENAME_SUBP,),
    #    Move
    Op.READ8:                (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.READ16:               (Param.PAR16, Param.PAR8, Param.PAR16),
    Op.READ32:               (Param.PAR32, Param.PAR8, Param.PAR32),
    Op.READF:                (Param.PARF, Param.PAR8, Param.PARF),
    Op.WRITE8:               (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.WRITE16:              (Param.PAR16, Param.PAR8, Param.PAR16),
    Op.WRITE32:              (Param.PAR32, Param.PAR8, Param.PAR32),
    Op.WRITEF:               (Param.PARF, Param.PAR8, Param.PARF),
    #    Com
    Op.COM_READY:            (Param.PAR8, Param.PAR8),
    Op.COM_READDATA:         (Param.PAR8, Param.PAR8, Param.PAR16, Param.PAR8),
    Op.COM_WRITEDATA:        (Param.PAR8, Param.PAR8, Param.PAR16, Param.PAR8),
    Op.COM_GET:              (Subparam.COM_GET_SUBP,),
    Op.COM_SET:              (Subparam.COM_SET_SUBP,),
    Op.COM_TEST:             (Param.PAR8, Param.PAR8, Param.PAR8),
    Op.COM_REMOVE:           (Param.PAR8, Param.PAR8),
    Op.COM_WRITEFILE:        (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8),

    Op.MAILBOX_OPEN:         (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8),
    Op.MAILBOX_WRITE:        (Param.PAR8, Param.PAR8, Param.PAR8, Param.PAR8, Param.PARNO),
    Op.MAILBOX_READ:         (Param.PAR8, Param.PAR8, Param.PARNO),
    Op.MAILBOX_TEST:         (Param.PAR8, Param.PAR8),
    Op.MAILBOX_READY:        (Param.PAR8,),
    Op.MAILBOX_CLOSE:        (Param.PAR8,),
    #    Test
    Op.TST:                  (Subparam.TST_SUBP,),
}

class UiReadSubcode(Enum):
    GET_VBATT     = 1
    GET_IBATT     = 2
    GET_OS_VERS   = 3
    GET_EVENT     = 4
    GET_TBATT     = 5
    GET_IINT      = 6
    GET_IMOTOR    = 7
    GET_STRING    = 8
    GET_HW_VERS   = 9
    GET_FW_VERS   = 10
    GET_FW_BUILD  = 11
    GET_OS_BUILD  = 12
    GET_ADDRESS   = 13
    GET_CODE      = 14
    KEY           = 15
    GET_SHUTDOWN  = 16
    GET_WARNING   = 17
    GET_LBATT     = 18
    TEXTBOX_READ  = 21
    GET_VERSION   = 26
    GET_IP        = 27
    GET_POWER     = 29
    GET_SDCARD    = 30
    GET_USBSTICK  = 31

    @property
    def params(self):
        return _ui_read_subcode_params[self]

_ui_read_subcode_params = {
    UiReadSubcode.GET_VBATT:              (Param.PARF,),
    UiReadSubcode.GET_IBATT:              (Param.PARF,),
    UiReadSubcode.GET_OS_VERS:            (Param.PAR8,Param.PAR8),
    UiReadSubcode.GET_EVENT:              (Param.PAR8,),
    UiReadSubcode.GET_TBATT:              (Param.PARF,),
    UiReadSubcode.GET_IINT:               (Param.PARF,),
    UiReadSubcode.GET_IMOTOR:             (Param.PARF,),
    UiReadSubcode.GET_STRING:             (Param.PAR8,Param.PAR8),
    UiReadSubcode.KEY:                    (Param.PAR8,),
    UiReadSubcode.GET_SHUTDOWN:           (Param.PAR8,),
    UiReadSubcode.GET_WARNING:            (Param.PAR8,),
    UiReadSubcode.GET_LBATT:              (Param.PAR8,),
    UiReadSubcode.GET_ADDRESS:            (Param.PAR32,),
    UiReadSubcode.GET_CODE:               (Param.PAR32,Param.PAR32,Param.PAR32,Param.PAR8),
    UiReadSubcode.TEXTBOX_READ:           (Param.PAR8,Param.PAR32,Param.PAR8,Param.PAR8,Param.PAR16,Param.PAR8),
    UiReadSubcode.GET_HW_VERS:            (Param.PAR8,Param.PAR8),
    UiReadSubcode.GET_FW_VERS:            (Param.PAR8,Param.PAR8),
    UiReadSubcode.GET_FW_BUILD:           (Param.PAR8,Param.PAR8),
    UiReadSubcode.GET_OS_BUILD:           (Param.PAR8,Param.PAR8),
    UiReadSubcode.GET_VERSION:            (Param.PAR8,Param.PAR8),
    UiReadSubcode.GET_IP:                 (Param.PAR8,Param.PAR8),
    UiReadSubcode.GET_SDCARD:             (Param.PAR8,Param.PAR32,Param.PAR32),
    UiReadSubcode.GET_USBSTICK:           (Param.PAR8,Param.PAR32,Param.PAR32),
}

class UiWriteSubcode(Enum):
    WRITE_FLUSH   = 1
    FLOATVALUE    = 2
    STAMP         = 3
    PUT_STRING    = 8
    VALUE8        = 9
    VALUE16       = 10
    VALUE32       = 11
    VALUEF        = 12
    ADDRESS       = 13
    CODE          = 14
    DOWNLOAD_END  = 15
    SCREEN_BLOCK  = 16
    ALLOW_PULSE   = 17
    SET_PULSE     = 18
    TEXTBOX_APPEND = 21
    SET_BUSY      = 22
    SET_TESTPIN   = 24
    INIT_RUN      = 25
    UPDATE_RUN    = 26
    LED           = 27
    POWER         = 29
    GRAPH_SAMPLE  = 30
    TERMINAL      = 31

    @property
    def params(self):
        return _ui_write_subcode_params[self]

_ui_write_subcode_params = {
    UiWriteSubcode.WRITE_FLUSH:            (),
    UiWriteSubcode.FLOATVALUE:             (Param.PARF,Param.PAR8,Param.PAR8),
    UiWriteSubcode.STAMP:                  (Param.PAR8,),
    UiWriteSubcode.PUT_STRING:             (Param.PAR8,),
    UiWriteSubcode.CODE:                   (Param.PAR8,Param.PAR32),
    UiWriteSubcode.DOWNLOAD_END:           (),
    UiWriteSubcode.SCREEN_BLOCK:           (Param.PAR8,),
    UiWriteSubcode.ALLOW_PULSE:            (Param.PAR8,),
    UiWriteSubcode.SET_PULSE:              (Param.PAR8,),
    UiWriteSubcode.TEXTBOX_APPEND:         (Param.PAR8,Param.PAR32,Param.PAR8,Param.PAR8),
    UiWriteSubcode.SET_BUSY:               (Param.PAR8,),
    UiWriteSubcode.VALUE8:                 (Param.PAR8,),
    UiWriteSubcode.VALUE16:                (Param.PAR16,),
    UiWriteSubcode.VALUE32:                (Param.PAR32,),
    UiWriteSubcode.VALUEF:                 (Param.PARF,),
    UiWriteSubcode.INIT_RUN:               (),
    UiWriteSubcode.UPDATE_RUN:             (),
    UiWriteSubcode.LED:                    (Param.PAR8,),
    UiWriteSubcode.POWER:                  (Param.PAR8,),
    UiWriteSubcode.TERMINAL:               (Param.PAR8,),
    UiWriteSubcode.GRAPH_SAMPLE:           (),
    UiWriteSubcode.SET_TESTPIN:            (Param.PAR8,),
}

class UiButtonSubcode(Enum):
    SHORTPRESS      = 1
    LONGPRESS       = 2
    WAIT_FOR_PRESS  = 3
    FLUSH           = 4
    PRESS           = 5
    RELEASE         = 6
    GET_HORZ        = 7
    GET_VERT        = 8
    PRESSED         = 9
    SET_BACK_BLOCK  = 10
    GET_BACK_BLOCK  = 11
    TESTSHORTPRESS  = 12
    TESTLONGPRESS   = 13
    GET_BUMBED      = 14
    GET_CLICK       = 15

    @property
    def params(self):
        return _ui_button_subcode_params[self]

_ui_button_subcode_params = {
    UiButtonSubcode.SHORTPRESS:             (Param.PAR8,Param.PAR8),
    UiButtonSubcode.LONGPRESS:              (Param.PAR8,Param.PAR8),
    UiButtonSubcode.FLUSH:                  (),
    UiButtonSubcode.WAIT_FOR_PRESS:         (),
    UiButtonSubcode.PRESS:                  (Param.PAR8,),
    UiButtonSubcode.RELEASE:                (Param.PAR8,),
    UiButtonSubcode.GET_HORZ:               (Param.PAR16,),
    UiButtonSubcode.GET_VERT:               (Param.PAR16,),
    UiButtonSubcode.PRESSED:                (Param.PAR8,Param.PAR8),
    UiButtonSubcode.SET_BACK_BLOCK:         (Param.PAR8,),
    UiButtonSubcode.GET_BACK_BLOCK:         (Param.PAR8,),
    UiButtonSubcode.TESTSHORTPRESS:         (Param.PAR8,Param.PAR8),
    UiButtonSubcode.TESTLONGPRESS:          (Param.PAR8,Param.PAR8),
    UiButtonSubcode.GET_BUMBED:             (Param.PAR8,Param.PAR8),
    UiButtonSubcode.GET_CLICK:              (Param.PAR8,),
}

class ComReadSubcode(Enum):
    COMMAND       = 14

    @property
    def params(self):
        return _com_read_subcode_params[self]

_com_read_subcode_params = {
    ComReadSubcode.COMMAND: (Param.PAR32,Param.PAR32,Param.PAR32,Param.PAR8),
}

class ComWriteSubcode(Enum):
    REPLY         = 14

    @property
    def params(self):
        return _com_write_subcode_params[self]

_com_write_subcode_params = {
    ComWriteSubcode.REPLY: (Param.PAR32,Param.PAR32,Param.PAR8),
}

class ComGetSubcode(Enum):
    GET_ON_OFF    = 1
    GET_VISIBLE   = 2
    GET_RESULT    = 4
    GET_PIN       = 5
    SEARCH_ITEMS  = 8
    SEARCH_ITEM   = 9
    FAVOUR_ITEMS  = 10
    FAVOUR_ITEM   = 11
    GET_ID        = 12
    GET_BRICKNAME = 13
    GET_NETWORK   = 14
    GET_PRESENT   = 15
    GET_ENCRYPT   = 16
    CONNEC_ITEMS  = 17
    CONNEC_ITEM   = 18
    GET_INCOMING  = 19
    GET_MODE2     = 20

    @property
    def params(self):
        return _com_get_subcode_params[self]

_com_get_subcode_params = {
    ComGetSubcode.GET_ON_OFF:             (Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_VISIBLE:            (Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_RESULT:             (Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_PIN:                (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.SEARCH_ITEMS:           (Param.PAR8,Param.PAR8),
    ComGetSubcode.SEARCH_ITEM:            (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.FAVOUR_ITEMS:           (Param.PAR8,Param.PAR8),
    ComGetSubcode.FAVOUR_ITEM:            (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_ID:                 (Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_BRICKNAME:          (Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_NETWORK:            (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_PRESENT:            (Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_ENCRYPT:            (Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.CONNEC_ITEMS:           (Param.PAR8,Param.PAR8),
    ComGetSubcode.CONNEC_ITEM:            (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_INCOMING:           (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ComGetSubcode.GET_MODE2:              (Param.PAR8,Param.PAR8),
}

class ComSetSubcode(Enum):
    SET_ON_OFF    = 1
    SET_VISIBLE   = 2
    SET_SEARCH    = 3
    SET_PIN       = 5
    SET_PASSKEY   = 6
    SET_CONNECTION = 7
    SET_BRICKNAME = 8
    SET_MOVEUP    = 9
    SET_MOVEDOWN  = 10
    SET_ENCRYPT   = 11
    SET_SSID      = 12
    SET_MODE2     = 13

    @property
    def params(self):
        return _com_set_subcode_params[self]

_com_set_subcode_params = {
    ComSetSubcode.SET_ON_OFF:             (Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_VISIBLE:            (Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_SEARCH:             (Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_PIN:                (Param.PAR8,Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_PASSKEY:            (Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_CONNECTION:         (Param.PAR8,Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_BRICKNAME:          (Param.PAR8,),
    ComSetSubcode.SET_MOVEUP:             (Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_MOVEDOWN:           (Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_ENCRYPT:            (Param.PAR8,Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_SSID:               (Param.PAR8,Param.PAR8),
    ComSetSubcode.SET_MODE2:              (Param.PAR8,Param.PAR8),
}

class InputDeviceSubcode(Enum):
    INSERT_TYPE     = 1
    GET_FORMAT      = 2
    CAL_MINMAX      = 3
    CAL_DEFAULT     = 4
    GET_TYPEMODE    = 5
    GET_SYMBOL      = 6
    CAL_MIN         = 7
    CAL_MAX         = 8
    SETUP           = 9
    CLR_ALL         = 10
    GET_RAW         = 11
    GET_CONNECTION  = 12
    STOP_ALL        = 13
    SET_TYPEMODE    = 14
    READY_IIC       = 15
    GET_NAME        = 21
    GET_MODENAME    = 22
    SET_RAW         = 23
    GET_FIGURES     = 24
    GET_CHANGES     = 25
    CLR_CHANGES     = 26
    READY_PCT       = 27
    READY_RAW       = 28
    READY_SI        = 29
    GET_MINMAX      = 30
    GET_BUMPS       = 31

    @property
    def params(self):
        return _input_device_subcode_params[self]

_input_device_subcode_params = {
    InputDeviceSubcode.INSERT_TYPE:            (Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.SET_TYPEMODE:           (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.GET_TYPEMODE:           (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.GET_CONNECTION:         (Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.GET_NAME:               (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.GET_SYMBOL:             (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.GET_FORMAT:             (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.GET_RAW:                (Param.PAR8,Param.PAR8,Param.PAR32),
    InputDeviceSubcode.GET_MODENAME:           (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.SET_RAW:                (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR32),
    InputDeviceSubcode.GET_FIGURES:            (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.GET_CHANGES:            (Param.PAR8,Param.PAR8,Param.PARF),
    InputDeviceSubcode.CLR_CHANGES:            (Param.PAR8,Param.PAR8),
    InputDeviceSubcode.READY_PCT:              (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PARNO),
    InputDeviceSubcode.READY_RAW:              (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PARNO),
    InputDeviceSubcode.READY_SI:               (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PARNO),
    InputDeviceSubcode.GET_MINMAX:             (Param.PAR8,Param.PAR8,Param.PARF,Param.PARF),
    InputDeviceSubcode.CAL_MINMAX:             (Param.PAR8,Param.PAR8,Param.PAR32,Param.PAR32),
    InputDeviceSubcode.CAL_DEFAULT:            (Param.PAR8,Param.PAR8),
    InputDeviceSubcode.CAL_MIN:                (Param.PAR8,Param.PAR8,Param.PAR32),
    InputDeviceSubcode.CAL_MAX:                (Param.PAR8,Param.PAR8,Param.PAR32),
    InputDeviceSubcode.GET_BUMPS:              (Param.PAR8,Param.PAR8,Param.PARF),
    InputDeviceSubcode.SETUP:                  (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR16,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    InputDeviceSubcode.CLR_ALL:                (Param.PAR8,),
    InputDeviceSubcode.STOP_ALL:               (Param.PAR8,),
    InputDeviceSubcode.READY_IIC:              (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
}

class ProgramInfoSubcode(Enum):
    OBJ_STOP      = 0
    OBJ_START     = 4
    GET_STATUS    = 22
    GET_SPEED     = 23
    GET_PRGRESULT = 24
    SET_INSTR     = 25

    @property
    def params(self):
        return _program_info_params[self]

_program_info_params = {
    ProgramInfoSubcode.OBJ_STOP:      (Param.PAR16,Param.PAR16),
    ProgramInfoSubcode.OBJ_START:     (Param.PAR16,Param.PAR16),
    ProgramInfoSubcode.GET_STATUS:    (Param.PAR16,Param.PAR8),
    ProgramInfoSubcode.GET_SPEED:     (Param.PAR16,Param.PAR32),
    ProgramInfoSubcode.GET_PRGRESULT: (Param.PAR16,Param.PAR8),
    ProgramInfoSubcode.SET_INSTR:     (Param.PAR16,),
}

class UiDrawSubcode(Enum):
    UPDATE        = 0
    CLEAN         = 1
    PIXEL         = 2
    LINE          = 3
    CIRCLE        = 4
    TEXT          = 5
    ICON          = 6
    PICTURE       = 7
    VALUE         = 8
    FILLRECT      = 9
    RECT          = 10
    NOTIFICATION  = 11
    QUESTION      = 12
    KEYBOARD      = 13
    BROWSE        = 14
    VERTBAR       = 15
    INVERSERECT   = 16
    SELECT_FONT   = 17
    TOPLINE       = 18
    FILLWINDOW    = 19
    SCROLL        = 20
    DOTLINE       = 21
    VIEW_VALUE    = 22
    VIEW_UNIT     = 23
    FILLCIRCLE    = 24
    STORE         = 25
    RESTORE       = 26
    ICON_QUESTION = 27
    BMPFILE       = 28
    POPUP         = 29
    GRAPH_SETUP   = 30
    GRAPH_DRAW    = 31
    TEXTBOX       = 32

    @property
    def params(self):
        return _ui_draw_subcode_params[self]

_ui_draw_subcode_params = {
    UiDrawSubcode.UPDATE:                 (),
    UiDrawSubcode.CLEAN:                  (),
    UiDrawSubcode.FILLRECT:               (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.RECT:                   (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.PIXEL:                  (Param.PAR8,Param.PAR16,Param.PAR16),
    UiDrawSubcode.LINE:                   (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.CIRCLE:                 (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.TEXT:                   (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR8),
    UiDrawSubcode.ICON:                   (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR8),
    UiDrawSubcode.PICTURE:                (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR32),
    UiDrawSubcode.VALUE:                  (Param.PAR8,Param.PAR16,Param.PAR16,Param.PARF,Param.PAR8,Param.PAR8),
    UiDrawSubcode.NOTIFICATION:           (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    UiDrawSubcode.QUESTION:               (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    UiDrawSubcode.KEYBOARD:               (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    UiDrawSubcode.BROWSE:                 (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR8,Param.PAR8),
    UiDrawSubcode.VERTBAR:                (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.INVERSERECT:            (Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.SELECT_FONT:            (Param.PAR8,),
    UiDrawSubcode.TOPLINE:                (Param.PAR8,),
    UiDrawSubcode.FILLWINDOW:             (Param.PAR8,Param.PAR16,Param.PAR16),
    UiDrawSubcode.SCROLL:                 (Param.PAR16,),
    UiDrawSubcode.DOTLINE:                (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.VIEW_VALUE:             (Param.PAR8,Param.PAR16,Param.PAR16,Param.PARF,Param.PAR8,Param.PAR8),
    UiDrawSubcode.VIEW_UNIT:              (Param.PAR8,Param.PAR16,Param.PAR16,Param.PARF,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    UiDrawSubcode.FILLCIRCLE:             (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.STORE:                  (Param.PAR8,),
    UiDrawSubcode.RESTORE:                (Param.PAR8,),
    UiDrawSubcode.ICON_QUESTION:          (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR32),
    UiDrawSubcode.BMPFILE:                (Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR8),
    UiDrawSubcode.GRAPH_SETUP:            (Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR16,Param.PAR16,Param.PAR16),
    UiDrawSubcode.GRAPH_DRAW:             (Param.PAR8,Param.PARF,Param.PARF,Param.PARF,Param.PARF),
    UiDrawSubcode.POPUP:                  (Param.PAR8,),
    UiDrawSubcode.TEXTBOX:                (Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR16,Param.PAR8,Param.PAR32,Param.PAR8,Param.PAR8),
}

class FileSubcode(Enum):
    OPEN_APPEND         = 0
    OPEN_READ           = 1
    OPEN_WRITE          = 2
    READ_VALUE          = 3
    WRITE_VALUE         = 4
    READ_TEXT           = 5
    WRITE_TEXT          = 6
    CLOSE               = 7
    LOAD_IMAGE          = 8
    GET_HANDLE          = 9
    MAKE_FOLDER         = 10
    GET_POOL            = 11
    SET_LOG_SYNC_TIME   = 12
    GET_FOLDERS         = 13
    GET_LOG_SYNC_TIME   = 14
    GET_SUBFOLDER_NAME  = 15
    WRITE_LOG           = 16
    CLOSE_LOG           = 17
    GET_IMAGE           = 18
    GET_ITEM            = 19
    GET_CACHE_FILES     = 20
    PUT_CACHE_FILE      = 21
    GET_CACHE_FILE      = 22
    DEL_CACHE_FILE      = 23
    DEL_SUBFOLDER       = 24
    GET_LOG_NAME        = 25

    OPEN_LOG            = 27
    READ_BYTES          = 28
    WRITE_BYTES         = 29
    REMOVE              = 30
    MOVE                = 31

    @property
    def params(self):
        return _file_subcode_params[self]

_file_subcode_params = {
    FileSubcode.OPEN_APPEND:            (Param.PAR8,Param.PAR16),
    FileSubcode.OPEN_READ:              (Param.PAR8,Param.PAR16,Param.PAR32),
    FileSubcode.OPEN_WRITE:             (Param.PAR8,Param.PAR16),
    FileSubcode.READ_VALUE:             (Param.PAR16,Param.PAR8,Param.PARF),
    FileSubcode.WRITE_VALUE:            (Param.PAR16,Param.PAR8,Param.PARF,Param.PAR8,Param.PAR8),
    FileSubcode.READ_TEXT:              (Param.PAR16,Param.PAR8,Param.PAR16,Param.PAR8),
    FileSubcode.WRITE_TEXT:             (Param.PAR16,Param.PAR8,Param.PAR8),
    FileSubcode.CLOSE:                  (Param.PAR16,),
    FileSubcode.LOAD_IMAGE:             (Param.PAR16,Param.PAR8,Param.PAR32,Param.PAR32),
    FileSubcode.GET_HANDLE:             (Param.PAR8,Param.PAR16,Param.PAR8),
    FileSubcode.MAKE_FOLDER:            (Param.PAR8,Param.PAR8),
    FileSubcode.GET_LOG_NAME:           (Param.PAR8,Param.PAR8),
    FileSubcode.GET_POOL:               (Param.PAR32,Param.PAR16,Param.PAR32),
    FileSubcode.GET_FOLDERS:            (Param.PAR8,Param.PAR8),
    FileSubcode.GET_SUBFOLDER_NAME:     (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    FileSubcode.WRITE_LOG:              (Param.PAR16,Param.PAR32,Param.PAR8,Param.PARF),
    FileSubcode.CLOSE_LOG:              (Param.PAR16,Param.PAR8),
    FileSubcode.SET_LOG_SYNC_TIME:      (Param.PAR32,Param.PAR32),
    FileSubcode.DEL_SUBFOLDER:          (Param.PAR8,Param.PAR8),
    FileSubcode.GET_LOG_SYNC_TIME:      (Param.PAR32,Param.PAR32),
    FileSubcode.GET_IMAGE:              (Param.PAR8,Param.PAR16,Param.PAR8,Param.PAR32),
    FileSubcode.GET_ITEM:               (Param.PAR8,Param.PAR8,Param.PAR8),
    FileSubcode.GET_CACHE_FILES:        (Param.PAR8,),
    FileSubcode.GET_CACHE_FILE:         (Param.PAR8,Param.PAR8,Param.PAR8),
    FileSubcode.PUT_CACHE_FILE:         (Param.PAR8,),
    FileSubcode.DEL_CACHE_FILE:         (Param.PAR8,),
    FileSubcode.OPEN_LOG:               (Param.PAR8,Param.PAR32,Param.PAR32,Param.PAR32,Param.PAR32,Param.PAR32,Param.PAR8,Param.PAR16),
    FileSubcode.READ_BYTES:             (Param.PAR16,Param.PAR16,Param.PAR8),
    FileSubcode.WRITE_BYTES:            (Param.PAR16,Param.PAR16,Param.PAR8),
    FileSubcode.REMOVE:                 (Param.PAR8,),
    FileSubcode.MOVE:                   (Param.PAR8,Param.PAR8),
}

class ArraySubcode(Enum):
    DELETE              = 0
    CREATE8             = 1
    CREATE16            = 2
    CREATE32            = 3
    CREATEF             = 4
    RESIZE              = 5
    FILL                = 6
    COPY                = 7
    INIT8               = 8
    INIT16              = 9
    INIT32              = 10
    INITF               = 11
    SIZE                = 12
    READ_CONTENT        = 13
    WRITE_CONTENT       = 14
    READ_SIZE           = 15
    # File name subcodes
    EXIST               = 16
    TOTALSIZE           = 17
    SPLIT               = 18
    MERGE               = 19
    CHECK               = 20
    PACK                = 21
    UNPACK              = 22
    GET_FOLDERNAME      = 23

    @property
    def params(self):
        return _array_subcode_params[self]

_array_subcode_params = {
    ArraySubcode.CREATE8:                (Param.PAR32,Param.PAR16),
    ArraySubcode.CREATE16:               (Param.PAR32,Param.PAR16),
    ArraySubcode.CREATE32:               (Param.PAR32,Param.PAR16),
    ArraySubcode.CREATEF:                (Param.PAR32,Param.PAR16),
    ArraySubcode.RESIZE:                 (Param.PAR16,Param.PAR32),
    ArraySubcode.DELETE:                 (Param.PAR16,),
    ArraySubcode.FILL:                   (Param.PAR16,Param.PARV),
    ArraySubcode.COPY:                   (Param.PAR16,Param.PAR16),
    ArraySubcode.INIT8:                  (Param.PAR16,Param.PAR32,Param.PAR32,Param.PARVALUES,Param.PAR8),
    ArraySubcode.INIT16:                 (Param.PAR16,Param.PAR32,Param.PAR32,Param.PARVALUES,Param.PAR16),
    ArraySubcode.INIT32:                 (Param.PAR16,Param.PAR32,Param.PAR32,Param.PARVALUES,Param.PAR32),
    ArraySubcode.INITF:                  (Param.PAR16,Param.PAR32,Param.PAR32,Param.PARVALUES,Param.PARF),
    ArraySubcode.SIZE:                   (Param.PAR16,Param.PAR32),
    ArraySubcode.READ_CONTENT:           (Param.PAR16,Param.PAR16,Param.PAR32,Param.PAR32,Param.PAR8),
    ArraySubcode.WRITE_CONTENT:          (Param.PAR16,Param.PAR16,Param.PAR32,Param.PAR32,Param.PAR8),
    ArraySubcode.READ_SIZE:              (Param.PAR16,Param.PAR16,Param.PAR32),
    # FileSubcode
    ArraySubcode.EXIST:                  (Param.PAR8,Param.PAR8),
    ArraySubcode.TOTALSIZE:              (Param.PAR8,Param.PAR32,Param.PAR32),
    ArraySubcode.SPLIT:                  (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ArraySubcode.MERGE:                  (Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8,Param.PAR8),
    ArraySubcode.CHECK:                  (Param.PAR8,Param.PAR8),
    ArraySubcode.PACK:                   (Param.PAR8,),
    ArraySubcode.UNPACK:                 (Param.PAR8,),
    ArraySubcode.GET_FOLDERNAME:         (Param.PAR8,Param.PAR8),
}

class InfoSubcode(Enum):
    SET_ERROR           = 1
    GET_ERROR           = 2
    ERRORTEXT           = 3

    GET_VOLUME          = 4
    SET_VOLUME          = 5
    GET_MINUTES         = 6
    SET_MINUTES         = 7
    # Test subcodes
    TST_OPEN                      = 10
    TST_CLOSE                     = 11
    TST_READ_PINS                 = 12
    TST_WRITE_PINS                = 13
    TST_READ_ADC                  = 14
    TST_WRITE_UART                = 15
    TST_READ_UART                 = 16
    TST_ENABLE_UART               = 17
    TST_DISABLE_UART              = 18
    TST_ACCU_SWITCH               = 19
    TST_BOOT_MODE2                = 20
    TST_POLL_MODE2                = 21
    TST_CLOSE_MODE2               = 22
    TST_RAM_CHECK                 = 23

    @property
    def params(self):
        return _info_subcode_params[self]

_info_subcode_params = {
    InfoSubcode.SET_ERROR:              (Param.PAR8,),
    InfoSubcode.GET_ERROR:              (Param.PAR8,),
    InfoSubcode.ERRORTEXT:              (Param.PAR8,Param.PAR8,Param.PAR8),
    InfoSubcode.GET_VOLUME:             (Param.PAR8,),
    InfoSubcode.SET_VOLUME:             (Param.PAR8,),
    InfoSubcode.GET_MINUTES:            (Param.PAR8,),
    InfoSubcode.SET_MINUTES:            (Param.PAR8,),
    # TestSubcode
    InfoSubcode.TST_OPEN:               (),
    InfoSubcode.TST_CLOSE:              (),
    InfoSubcode.TST_READ_PINS:          (Param.PAR8,Param.PAR8,Param.PAR8),
    InfoSubcode.TST_WRITE_PINS:         (Param.PAR8,Param.PAR8,Param.PAR8),
    InfoSubcode.TST_READ_ADC:           (Param.PAR8,Param.PAR16),
    InfoSubcode.TST_WRITE_UART:         (Param.PAR8,Param.PAR8,Param.PAR8),
    InfoSubcode.TST_READ_UART:          (Param.PAR8,Param.PAR8,Param.PAR8),
    InfoSubcode.TST_ENABLE_UART:        (Param.PAR32,),
    InfoSubcode.TST_DISABLE_UART:       (),
    InfoSubcode.TST_ACCU_SWITCH:        (Param.PAR8,),
    InfoSubcode.TST_BOOT_MODE2:         (),
    InfoSubcode.TST_POLL_MODE2:         (Param.PAR8,),
    InfoSubcode.TST_CLOSE_MODE2:        (),
    InfoSubcode.TST_RAM_CHECK:          (Param.PAR8,),
}

class SoundSubcode(Enum):
    BREAK               = 0
    TONE                = 1
    PLAY                = 2
    REPEAT              = 3
    SERVICE             = 4

    @property
    def params(self):
        return _sound_subcode_params[self]

_sound_subcode_params = {
    SoundSubcode.BREAK:   (),
    SoundSubcode.TONE:    (Param.PAR8,Param.PAR16,Param.PAR16),
    SoundSubcode.PLAY:    (Param.PAR8,Param.PARS),
    SoundSubcode.REPEAT:  (Param.PAR8,Param.PARS),
    SoundSubcode.SERVICE: (),
}

class StringSubcode(Enum):
    GET_SIZE            = 1
    ADD                 = 2
    COMPARE             = 3
    DUPLICATE           = 5
    VALUE_TO_STRING     = 6
    STRING_TO_VALUE     = 7
    STRIP               = 8
    NUMBER_TO_STRING    = 9
    SUB                 = 10
    VALUE_FORMATTED     = 11
    NUMBER_FORMATTED    = 12

    @property
    def params(self):
        return _string_subcode_params[self]

_string_subcode_params = {
    StringSubcode.GET_SIZE:               (Param.PAR8,Param.PAR16),
    StringSubcode.ADD:                    (Param.PAR8,Param.PAR8,Param.PAR8),
    StringSubcode.COMPARE:                (Param.PAR8,Param.PAR8,Param.PAR8),
    StringSubcode.DUPLICATE:              (Param.PAR8,Param.PAR8),
    StringSubcode.VALUE_TO_STRING:        (Param.PARF,Param.PAR8,Param.PAR8,Param.PAR8),
    StringSubcode.STRING_TO_VALUE:        (Param.PAR8,Param.PARF),
    StringSubcode.STRIP:                  (Param.PAR8,Param.PAR8),
    StringSubcode.NUMBER_TO_STRING:       (Param.PAR16,Param.PAR8,Param.PAR8),
    StringSubcode.SUB:                    (Param.PAR8,Param.PAR8,Param.PAR8),
    StringSubcode.VALUE_FORMATTED:        (Param.PARF,Param.PAR8,Param.PAR8,Param.PAR8),
    StringSubcode.NUMBER_FORMATTED:       (Param.PAR32,Param.PAR8,Param.PAR8,Param.PAR8),
}

class DeviceType(Enum):
    MODE_KEEP                     =  -1
    TYPE_KEEP                     =   0

    # Types defined in "typedata.rcf"
    TYPE_NXT_TOUCH                =   1
    TYPE_NXT_LIGHT                =   2
    TYPE_NXT_SOUND                =   3
    TYPE_NXT_COLOR                =   4
    TYPE_NXT_ULTRASONIC           =   5
    TYPE_NXT_TEMPERATURE          =   6
    TYPE_TACHO                    =   7
    TYPE_MINITACHO                =   8
    TYPE_NEWTACHO                 =   9

    TYPE_TOUCH                    =  16

    # Types defined in known EV3/UART sensors
    TYPE_COLOR                    =  29
    TYPE_ULTRASONIC               =  30
    TYPE_GYRO                     =  32
    TYPE_IR                       =  33

    # Type range reserved for third party devices
    TYPE_THIRD_PARTY_START        =  50
    TYPE_THIRD_PARTY_END          =  98
    TYPE_ENERGYMETER              =  99
    TYPE_IIC_UNKNOWN              = 100
    TYPE_NXT_TEST                 = 101

    TYPE_NXT_IIC                  = 123
    TYPE_TERMINAL                 = 124
    TYPE_UNKNOWN                  = 125
    TYPE_NONE                     = 126
    TYPE_ERROR                    = 127

class Slot(Enum):
    GUI_SLOT                      = 0
    USER_SLOT                     = 1
    CMD_SLOT                      = 2
    TERM_SLOT                     = 3
    DEBUG_SLOT                    = 4
    # ONLY VALID IN opPROGRAM_STOP
    CURRENT_SLOT                  = -1

class ButtonType(Enum):
    NO_BUTTON                     = 0
    UP_BUTTON                     = 1
    ENTER_BUTTON                  = 2
    DOWN_BUTTON                   = 3
    RIGHT_BUTTON                  = 4
    LEFT_BUTTON                   = 5
    BACK_BUTTON                   = 6
    ANY_BUTTON                    = 7

class MathSubcode(Enum):
    EXP                           = 1
    MOD                           = 2
    FLOOR                         = 3
    CEIL                          = 4
    ROUND                         = 5
    ABS                           = 6
    NEGATE                        = 7
    SQRT                          = 8
    LOG                           = 9
    LN                            = 10
    SIN                           = 11
    COS                           = 12
    TAN                           = 13
    ASIN                          = 14
    ACOS                          = 15
    ATAN                          = 16
    MOD8                          = 17
    MOD16                         = 18
    MOD32                         = 19
    POW                           = 20
    TRUNC                         = 21

    @property
    def params(self):
        return _math_subcode_params[self]

_math_subcode_params = {
    MathSubcode.EXP:                    (Param.PARF,Param.PARF),
    MathSubcode.MOD:                    (Param.PARF,Param.PARF,Param.PARF),
    MathSubcode.FLOOR:                  (Param.PARF,Param.PARF),
    MathSubcode.CEIL:                   (Param.PARF,Param.PARF),
    MathSubcode.ROUND:                  (Param.PARF,Param.PARF),
    MathSubcode.ABS:                    (Param.PARF,Param.PARF),
    MathSubcode.NEGATE:                 (Param.PARF,Param.PARF),
    MathSubcode.SQRT:                   (Param.PARF,Param.PARF),
    MathSubcode.LOG:                    (Param.PARF,Param.PARF),
    MathSubcode.LN:                     (Param.PARF,Param.PARF),
    MathSubcode.SIN:                    (Param.PARF,Param.PARF),
    MathSubcode.COS:                    (Param.PARF,Param.PARF),
    MathSubcode.TAN:                    (Param.PARF,Param.PARF),
    MathSubcode.ASIN:                   (Param.PARF,Param.PARF),
    MathSubcode.ACOS:                   (Param.PARF,Param.PARF),
    MathSubcode.ATAN:                   (Param.PARF,Param.PARF),
    MathSubcode.MOD8:                   (Param.PAR8,Param.PAR8,Param.PAR8),
    MathSubcode.MOD16:                  (Param.PAR16,Param.PAR16,Param.PAR16),
    MathSubcode.MOD32:                  (Param.PAR32,Param.PAR32,Param.PAR32),
    MathSubcode.POW:                    (Param.PARF,Param.PARF,Param.PARF),
    MathSubcode.TRUNC:                  (Param.PARF,Param.PAR8,Param.PARF),
}

class BrowserType(Enum):
    BROWSE_FOLDERS                = 0
    BROWSE_FOLDS_FILES            = 1
    BROWSE_CACHE                  = 2
    BROWSE_FILES                  = 3

class FontType(Enum):
    NORMAL_FONT                   = 0
    SMALL_FONT                    = 1
    LARGE_FONT                    = 2
    TINY_FONT                     = 3

class IconType(Enum):
    NORMAL_ICON                   = 0
    SMALL_ICON                    = 1
    LARGE_ICON                    = 2
    MENU_ICON                     = 3
    ARROW_ICON                    = 4

class StatusIcon(Enum):
    SICON_CHARGING                = 0
    SICON_BATT_4                  = 1
    SICON_BATT_3                  = 2
    SICON_BATT_2                  = 3
    SICON_BATT_1                  = 4
    SICON_BATT_0                  = 5
    SICON_WAIT1                   = 6
    SICON_WAIT2                   = 7
    SICON_BT_ON                   = 8
    SICON_BT_VISIBLE              = 9
    SICON_BT_CONNECTED            = 10
    SICON_BT_CONNVISIB            = 11
    SICON_WIFI_3                  = 12
    SICON_WIFI_2                  = 13
    SICON_WIFI_1                  = 14
    SICON_WIFI_CONNECTED          = 15

    SICON_USB                     = 21

class NIcon(Enum):
    ICON_NONE                     = -1
    ICON_RUN                      = 0
    ICON_FOLDER                   = 1
    ICON_FOLDER2                  = 2
    ICON_USB                      = 3
    ICON_SD                       = 4
    ICON_SOUND                    = 5
    ICON_IMAGE                    = 6
    ICON_SETTINGS                 = 7
    ICON_ONOFF                    = 8
    ICON_SEARCH                   = 9
    ICON_WIFI                     = 10
    ICON_CONNECTIONS              = 11
    ICON_ADD_HIDDEN               = 12
    ICON_TRASHBIN                 = 13
    ICON_VISIBILITY               = 14
    ICON_KEY                      = 15
    ICON_CONNECT                  = 16
    ICON_DISCONNECT               = 17
    ICON_UP                       = 18
    ICON_DOWN                     = 19
    ICON_WAIT1                    = 20
    ICON_WAIT2                    = 21
    ICON_BLUETOOTH                = 22
    ICON_INFO                     = 23
    ICON_TEXT                     = 24


    ICON_QUESTIONMARK             = 27
    ICON_INFO_FILE                = 28
    ICON_DISC                     = 29
    ICON_CONNECTED                = 30
    ICON_OBP                      = 31
    ICON_OBD                      = 32
    ICON_OPENFOLDER               = 33
    ICON_BRICK1                   = 34

class LIcon(Enum):
    YES_NOTSEL                    = 0
    YES_SEL                       = 1
    NO_NOTSEL                     = 2
    NO_SEL                        = 3
    OFF                           = 4
    WAIT_VERT                     = 5
    WAIT_HORZ                     = 6
    TO_MANUAL                     = 7
    WARNSIGN                      = 8
    WARN_BATT                     = 9
    WARN_POWER                    = 10
    WARN_TEMP                     = 11
    NO_USBSTICK                   = 12
    TO_EXECUTE                    = 13
    TO_BRICK                      = 14
    TO_SDCARD                     = 15
    TO_USBSTICK                   = 16
    TO_BLUETOOTH                  = 17
    TO_WIFI                       = 18
    TO_TRASH                      = 19
    TO_COPY                       = 20
    TO_FILE                       = 21
    CHAR_ERROR                    = 22
    COPY_ERROR                    = 23
    PROGRAM_ERROR                 = 24


    WARN_MEMORY                   = 27

class MIcon(Enum):
    ICON_STAR                     = 0
    ICON_LOCKSTAR                 = 1
    ICON_LOCK                     = 2
    ICON_PC                       = 3
    ICON_PHONE                    = 4
    ICON_BRICK                    = 5
    ICON_UNKNOWN                  = 6
    ICON_FROM_FOLDER              = 7
    ICON_CHECKBOX                 = 8
    ICON_CHECKED                  = 9
    ICON_XED                      = 10

class AIcon(Enum):
    ICON_LEFT                     = 1
    ICON_RIGHT                    = 2

class BluetoothType(Enum):
    BTTYPE_PC                     = 3
    BTTYPE_PHONE                  = 4
    BTTYPE_BRICK                  = 5
    BTTYPE_UNKNOWN                = 6

class LedPattern(Enum):
    LED_BLACK                     = 0
    LED_GREEN                     = 1
    LED_RED                       = 2
    LED_ORANGE                    = 3
    LED_GREEN_FLASH               = 4
    LED_RED_FLASH                 = 5
    LED_ORANGE_FLASH              = 6
    LED_GREEN_PULSE               = 7
    LED_RED_PULSE                 = 8
    LED_ORANGE_PULSE              = 9

class LedType(Enum):
    LED_ALL                       = 0
    LED_RR                        = 1
    LED_RG                        = 2
    LED_LR                        = 3
    LED_LG                        = 4

class FileType(Enum):
    FILETYPE_UNKNOWN              = 0x00
    TYPE_FOLDER                   = 0x01
    TYPE_SOUND                    = 0x02
    TYPE_BYTECODE                 = 0x03
    TYPE_GRAPHICS                 = 0x04
    TYPE_DATALOG                  = 0x05
    TYPE_PROGRAM                  = 0x06
    TYPE_TEXT                     = 0x07
    TYPE_SDCARD                   = 0x10
    TYPE_USBSTICK                 = 0x20

    TYPE_RESTART_BROWSER          = -1
    TYPE_REFRESH_BROWSER          = -2

class Result(Enum):
    OK            = 0
    BUSY          = 1
    FAIL          = 2
    STOP          = 4
    START         = 8

class Delimeter(Enum):
    DEL_NONE      = 0
    DEL_TAB       = 1
    DEL_SPACE     = 2
    DEL_RETURN    = 3
    DEL_COLON     = 4
    DEL_COMMA     = 5
    DEL_LINEFEED  = 6
    DEL_CRLF      = 7

class HardwareTransportLayer(Enum):
    HW_USB        = 1
    HW_BT         = 2
    HW_WIFI       = 3

class EncryptionType(Enum):
    ENCRYPT_NONE  = 0
    ENCRYPT_WPA2  = 1

class Color(Enum):
    RED           = 0
    GREEN         = 1
    BLUE          = 2
    BLANK         = 3

class NxtColor(Enum):
    BLACKCOLOR    = 1
    BLUECOLOR     = 2
    GREENCOLOR    = 3
    YELLOWCOLOR   = 4
    REDCOLOR      = 5
    WHITECOLOR    = 6

class Warning(Enum):
    WARNING_TEMP      = 0x01
    WARNING_CURRENT   = 0x02
    WARNING_VOLTAGE   = 0x04
    WARNING_MEMORY    = 0x08
    WARNING_DSPSTAT   = 0x10
    WARNING_RAM       = 0x20
    WARNING_BATTLOW   = 0x40
    WARNING_BUSY      = 0x80

    WARNINGS          = 0x3F

class ObjectStatus(Enum):
    RUNNING = 0x0010
    WAITING = 0x0020
    STOPPED = 0x0040
    HALTED  = 0x0080

class DeviceCommand(Enum):
    DEVCMD_RESET        = 0x11
    DEVCMD_FIRE         = 0x11
    DEVCMD_CHANNEL      = 0x12

_subcode_enums = {
    Subparam.PROGRAM_SUBP:      ProgramInfoSubcode,
    Subparam.FILE_SUBP:         FileSubcode,
    Subparam.ARRAY_SUBP:        ArraySubcode,
    Subparam.FILENAME_SUBP:     ArraySubcode,
    Subparam.VM_SUBP:           InfoSubcode,
    Subparam.STRING_SUBP:       StringSubcode,
    Subparam.UI_READ_SUBP:      UiReadSubcode,
    Subparam.UI_WRITE_SUBP:     UiWriteSubcode,
    Subparam.UI_DRAW_SUBP:      UiDrawSubcode,
    Subparam.UI_BUTTON_SUBP:    UiButtonSubcode,
    Subparam.COM_READ_SUBP:     ComReadSubcode,
    Subparam.COM_WRITE_SUBP:    ComWriteSubcode,
    Subparam.SOUND_SUBP:        SoundSubcode,
    Subparam.INPUT_SUBP:        InputDeviceSubcode,
    Subparam.MATH_SUBP:         MathSubcode,
    Subparam.COM_GET_SUBP:      ComGetSubcode,
    Subparam.COM_SET_SUBP:      ComSetSubcode,
}

class Callparam(Enum):
    IN_8      = 0x80 | DataFormat.DATA8.value
    IN_16     = 0x80 | DataFormat.DATA16.value
    IN_32     = 0x80 | DataFormat.DATA32.value
    IN_F      = 0x80 | DataFormat.DATAF.value
    IN_S      = 0x80 | DataFormat.DATAS.value
    OUT_8     = 0x40 | DataFormat.DATA8.value
    OUT_16    = 0x40 | DataFormat.DATA16.value
    OUT_32    = 0x40 | DataFormat.DATA32.value
    OUT_F     = 0x40 | DataFormat.DATAF.value
    OUT_S     = 0x40 | DataFormat.DATAS.value
    IO_8      = IN_8  | OUT_8
    IO_16     = IN_16 | OUT_16
    IO_32     = IN_32 | OUT_32
    IO_F      = IN_F  | OUT_F
    IO_S      = IN_S  | OUT_S

    @property
    def DATAFormat(self):
        return DataFormat(self.value & 0x3F)

class ProgramHeader(LittleEndianStructure):
    _fields_ = [
        ("lego", c_char * 4),
        ("size", c_int32),
        ("_byte_code_version", c_uint16),
        ("num_objects", c_int16),
        ("global_bytes", c_int32)
    ]

    @property
    def byte_code_version(self):
        return "{0:.2f}".format(self._byte_code_version / 100.0)

class ObjectHeader(LittleEndianStructure):
    _fields_ = [
        ("offset", c_int32),
        ("owner", c_uint16),
        ("trigger_count", c_int16),
        ("local_bytes", c_int32)
    ]

    @property
    def is_vmthread(self):
        return self.owner == 0 and self.trigger_count == 0

    @property
    def is_subcall(self):
        return self.owner == 0 and self.trigger_count == 1

    @property
    def is_block(self):
        return self.owner != 0 and self.local_bytes == 0

LC0_MIN = -31
LC0_MAX = 31
DATA8_MIN = -127
DATA8_MAX = 127
DATA16_MIN = -32767
DATA16_MAX = 32767
DATA32_MIN = -2147483647
DATA32_MAX = 2147483647
DATAF_MIN = -2147483647
DATAF_MAX = 2147483647
DATA8_NAN = 0x80
DATA16_NAN = 0x8000
DATA32_NAN = 0x80000000
DATAF_NAN = 0x7FC00000

class Data8(LittleEndianStructure):
    _fields_ = [("value", c_int8)]

class Data16(LittleEndianStructure):
    _fields_ = [("value", c_int16)]

class Data32(LittleEndianStructure):
    _fields_ = [("value", c_int32)]

class DataFloat(LittleEndianStructure):
    _fields_ = [("value", c_float)]

PRIMPAR_SHORT        = 0x00
PRIMPAR_LONG         = 0x80
PRIMPAR_CONST        = 0x00
PRIMPAR_VARIABLE     = 0x40
PRIMPAR_LOCAL        = 0x00
PRIMPAR_GLOBAL       = 0x20
PRIMPAR_HANDLE       = 0x10
PRIMPAR_ADDR         = 0x08
PRIMPAR_INDEX        = 0x1F
PRIMPAR_CONST_SIGN   = 0x20
PRIMPAR_VALUE        = 0x3F
PRIMPAR_BYTES        = 0x07
PRIMPAR_STRING_OLD   = 0
PRIMPAR_1_BYTE       = 1
PRIMPAR_2_BYTES      = 2
PRIMPAR_4_BYTES      = 3
PRIMPAR_STRING       = 4
PRIMPAR_LABEL        = 0x20

DIRECT_COMMAND_REPLY    = 0x00
DIRECT_COMMAND_NO_REPLY = 0x80
DIRECT_REPLY            = 0x02
DIRECT_REPLY_ERROR      = 0x04
SYSTEM_COMMAND_REPLY    = 0x01
SYSTEM_COMMAND_NO_REPLY = 0x81
SYSTEM_REPLY            = 0x03
SYSTEM_REPLY_ERROR      = 0x05
