//
// DirectCommand.cs
//
// Author:
//       David Lechner <david@lechnology.com>
//
// Copyright (c) 2016 David Lechner
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

using System;
using System.Linq;
using System.Collections.Generic;

namespace BrickCommander.IO.EV3
{
    public sealed class DirectCommand : Command
    {
        DirectCommand (DirectCommandOpcode opcode, IEnumerable<byte> data)
            : base (new [] { (byte)opcode }.Concat (data))
        {
        }

        /// <summary>
        /// Add two 8-bit values.
        /// </summary>
        /// <param name="a">The first value.</param>
        /// <param name="b">The second value.</param>
        /// <param name="result">The location to store the result.</param>
        public static DirectCommand Add8 (IData8 a, IData8 b, [Return] IData8 result)
        {
            var data = a.Concat(b).Concat(result);
            return new DirectCommand (DirectCommandOpcode.Add8, data);
        }

        /// <summary>
        /// Add two 16-bit values.
        /// </summary>
        /// <param name="a">The first value.</param>
        /// <param name="b">The second value.</param>
        /// <param name="result">The location to store the result.</param>
        public static DirectCommand Add16 (IData16 a, IData16 b, [Return] IData16 result)
        {
            var data = a.Concat(b).Concat(result);
            return new DirectCommand (DirectCommandOpcode.Add16, data);
        }

        /// <summary>
        /// Add two 32-bit values.
        /// </summary>
        /// <param name="a">The first value.</param>
        /// <param name="b">The second value.</param>
        /// <param name="b">The location to store the result.</param>
        /// <param name="result">The location to store the result.</param>
        public static DirectCommand Add32 (IData32 a, IData32 b, [Return] IData32 result)
        {
            var data = a.Concat(b).Concat(result);
            return new DirectCommand (DirectCommandOpcode.Add32, data);
        }
    }

    /// <summary>
    /// Return attribute.
    /// </summary>
    [AttributeUsage (AttributeTargets.Parameter)]
    class ReturnAttribute : Attribute
    {
        
    }

    enum DirectCommandOpcode : byte
    {
        // VM
        //                                    0000....
        Error                     = 0x00, //      0000
        Nop                       = 0x01, //      0001
        ProgramStop               = 0x02, //      0010
        ProgramStart              = 0x03, //      0011
        ObjectStop                = 0x04, //      0100
        ObjectStart               = 0x05, //      0101
        ObjectTrigger             = 0x06, //      0110
        ObjectWait                = 0x07, //      0111
        Return                    = 0x08, //      1000
        Call                      = 0x09, //      1001
        ObjectEnd                 = 0x0A, //      1010
        Sleep                     = 0x0B, //      1011
        ProgramInfo               = 0x0C, //      1100
        Label                     = 0x0D, //      1101
        Probe                     = 0x0E, //      1110
        Do                        = 0x0F, //      1111

        // cMath "MATH"
        //                                    0001....
        //                    ADD                 00..
        Add8                      = 0x10, //        00
        Add16                     = 0x11, //        01
        Add32                     = 0x12, //        10
        AddFloat                  = 0x13, //        11
        //                    SUB                 01..
        Sub8                      = 0x14, //        00
        Sub16                     = 0x15, //        01
        Sub32                     = 0x16, //        10
        SubFloat                  = 0x17, //        11
        //                    MUL                 10..
        Mul8                      = 0x18, //        00
        Mul16                     = 0x19, //        01
        Mul32                     = 0x1A, //        10
        MulFloat                  = 0x1B, //        11
        //                    DIV                 11..
        Div8                      = 0x1C, //        00
        Div16                     = 0x1D, //        01
        Div32                     = 0x1E, //        10
        DivFloat                  = 0x1F, //        11

        // Logic "LOGIC"
        //        LOGIC                       0010....
        //                    OR                  00..
        OR8                       = 0x20, //        00
        OR16                      = 0x21, //        01
        OR32                      = 0x22, //        10

        //                    AND                 01..
        AND8                      = 0x24, //        00
        AND16                     = 0x25, //        01
        AND32                     = 0x26, //        10

        //                    XOR                 10..
        XOR8                      = 0x28, //        00
        XOR16                     = 0x29, //        01
        XOR32                     = 0x2A, //        10

        //                    RL                  11..
        RL8                       = 0x2C, //        00
        RL16                      = 0x2D, //        01
        RL32                      = 0x2E, //        10

        // cMove "MOVE"
        INIT_BYTES                = 0x2F, //      1111
        //        MOVE                        0011....
        //                    MOVE8_              00..
        MOVE8_8                   = 0x30, //        00
        MOVE8_16                  = 0x31, //        01
        MOVE8_32                  = 0x32, //        10
        MOVE8_F                   = 0x33, //        11
        //                    MOVE16_             01..
        MOVE16_8                  = 0x34, //        00
        MOVE16_16                 = 0x35, //        01
        MOVE16_32                 = 0x36, //        10
        MOVE16_F                  = 0x37, //        11
        //                    MOVE32_             10..
        MOVE32_8                  = 0x38, //        00
        MOVE32_16                 = 0x39, //        01
        MOVE32_32                 = 0x3A, //        10
        MOVE32_F                  = 0x3B, //        11
        //                    MOVEF_              11..
        MOVEF_8                   = 0x3C, //        00
        MOVEF_16                  = 0x3D, //        01
        MOVEF_32                  = 0x3E, //        10
        MOVEF_F                   = 0x3F, //        11

        // cBranch "BRANCH"
        //        BRANCH                      010000..
        JR                        = 0x40, //        00
        JR_FALSE                  = 0x41, //        01
        JR_TRUE                   = 0x42, //        10
        JR_NAN                    = 0x43, //        11

        // cCompare "COMPARE"
        //        COMPARE                     010.....
        //                    CP_LT              001..
        CP_LT8                    = 0x44, //        00
        CP_LT16                   = 0x45, //        01
        CP_LT32                   = 0x46, //        10
        CP_LTF                    = 0x47, //        11
        //                    CP_GT              010..
        CP_GT8                    = 0x48, //        00
        CP_GT16                   = 0x49, //        01
        CP_GT32                   = 0x4A, //        10
        CP_GTF                    = 0x4B, //        11
        //                    CP_EQ              011..
        CP_EQ8                    = 0x4C, //        00
        CP_EQ16                   = 0x4D, //        01
        CP_EQ32                   = 0x4E, //        10
        CP_EQF                    = 0x4F, //        11
        //                    CP_NEQ             100..
        CP_NEQ8                   = 0x50, //        00
        CP_NEQ16                  = 0x51, //        01
        CP_NEQ32                  = 0x52, //        10
        CP_NEQF                   = 0x53, //        11
        //                    CP_LTEQ            101..
        CP_LTEQ8                  = 0x54, //        00
        CP_LTEQ16                 = 0x55, //        01
        CP_LTEQ32                 = 0x56, //        10
        CP_LTEQF                  = 0x57, //        11
        //                    CP_GTEQ            110..
        CP_GTEQ8                  = 0x58, //        00
        CP_GTEQ16                 = 0x59, //        01
        CP_GTEQ32                 = 0x5A, //        10
        CP_GTEQF                  = 0x5B, //        11

        // Select "SELECT"
        //        SELECT                      010111..
        SELECT8                   = 0x5C, //        00
        SELECT16                  = 0x5D, //        01
        SELECT32                  = 0x5E, //        10
        SELECTF                   = 0x5F, //        11


        // VM
        SYSTEM                    = 0x60,
        PORT_CNV_OUTPUT           = 0x61,
        PORT_CNV_INPUT            = 0x62,
        NOTE_TO_FREQ              = 0x63,

        // cBranch "BRANCH"
        //        BRANCH                      011000..
        //?       00
        //?       01
        //?       10
        //?       11
        //                    JR_LT              001..
        JR_LT8                    = 0x64, //        00
        JR_LT16                   = 0x65, //        01
        JR_LT32                   = 0x66, //        10
        JR_LTF                    = 0x67, //        11
        //                    JR_GT              010..
        JR_GT8                    = 0x68, //        00
        JR_GT16                   = 0x69, //        01
        JR_GT32                   = 0x6A, //        10
        JR_GTF                    = 0x6B, //        11
        //                    JR_EQ              011..
        JR_EQ8                    = 0x6C, //        00
        JR_EQ16                   = 0x6D, //        01
        JR_EQ32                   = 0x6E, //        10
        JR_EQF                    = 0x6F, //        11
        //                    JR_NEQ             100..
        JR_NEQ8                   = 0x70, //        00
        JR_NEQ16                  = 0x71, //        01
        JR_NEQ32                  = 0x72, //        10
        JR_NEQF                   = 0x73, //        11
        //                    JR_LTEQ            101..
        JR_LTEQ8                  = 0x74, //        00
        JR_LTEQ16                 = 0x75, //        01
        JR_LTEQ32                 = 0x76, //        10
        JR_LTEQF                  = 0x77, //        11
        //                    JR_GTEQ            110..
        JR_GTEQ8                  = 0x78, //        00
        JR_GTEQ16                 = 0x79, //        01
        JR_GTEQ32                 = 0x7A, //        10
        JR_GTEQF                  = 0x7B, //        11

        // VM
        INFO                      = 0x7C, //  01111100
        STRINGS                   = 0x7D, //  01111101
        MEMORY_WRITE              = 0x7E, //  01111110
        MEMORY_READ               = 0x7F, //  01111111

        //        SYSTEM                      1.......

        // cUi "UI"
        //        UI                          100000..
        UI_FLUSH                  = 0x80, //        00
        UI_READ                   = 0x81, //        01
        UI_WRITE                  = 0x82, //        10
        UI_BUTTON                 = 0x83, //        11
        UI_DRAW                   = 0x84, //  10000100

        // cTimer "TIMER"
        TIMER_WAIT                = 0x85, //  10000101
        TIMER_READY               = 0x86, //  10000110
        TIMER_READ                = 0x87, //  10000111

        // VM
        //        BREAKPOINT                  10001...
        BP0                       = 0x88, //       000
        BP1                       = 0x89, //       001
        BP2                       = 0x8A, //       010
        BP3                       = 0x8B, //       011
        BP_SET                    = 0x8C, //  10001100
        MATH                      = 0x8D, //  10001101
        RANDOM                    = 0x8E, //  10001110

        // cTimer "TIMER"
        TIMER_READ_US             = 0x8F, //  10001111

        // cUi "UI"
        KEEP_ALIVE                = 0x90, //  10010000

        // cCom "COM"
        //                                      100100
        COM_READ                  = 0x91, //        01
        COM_WRITE                 = 0x92, //        10

        // cSound "SOUND"
        //                                      100101
        SOUND                     = 0x94, //        00
        SOUND_TEST                = 0x95, //        01
        SOUND_READY               = 0x96, //        10

        // cInput "INPUT"
        //
        INPUT_SAMPLE              = 0x97, //  10010111

        //                                    10011...
        INPUT_DEVICE_LIST         = 0x98, //       000
        INPUT_DEVICE              = 0x99, //       001
        INPUT_READ                = 0x9A, //       010
        INPUT_TEST                = 0x9B, //       011
        INPUT_READY               = 0x9C, //       100
        INPUT_READSI              = 0x9D, //       101
        INPUT_READEXT             = 0x9E, //       110
        INPUT_WRITE               = 0x9F, //       111
        // cOutput "OUTPUT"
        //                                    101.....
        OUTPUT_GET_TYPE           = 0xA0, //     00000
        OUTPUT_SET_TYPE           = 0xA1, //     00001
        OUTPUT_RESET              = 0xA2, //     00010
        OUTPUT_STOP               = 0xA3, //     00011
        OUTPUT_POWER              = 0xA4, //     00100
        OUTPUT_SPEED              = 0xA5, //     00101
        OUTPUT_START              = 0xA6, //     00110
        OUTPUT_POLARITY           = 0xA7, //     00111
        OUTPUT_READ               = 0xA8, //     01000
        OUTPUT_TEST               = 0xA9, //     01001
        OUTPUT_READY              = 0xAA, //     01010
        OUTPUT_POSITION           = 0xAB, //     01011
        OUTPUT_STEP_POWER         = 0xAC, //     01100
        OUTPUT_TIME_POWER         = 0xAD, //     01101
        OUTPUT_STEP_SPEED         = 0xAE, //     01110
        OUTPUT_TIME_SPEED         = 0xAF, //     01111

        OUTPUT_STEP_SYNC          = 0xB0, //     10000
        OUTPUT_TIME_SYNC          = 0xB1, //     10001
        OUTPUT_CLR_COUNT          = 0xB2, //     10010
        OUTPUT_GET_COUNT          = 0xB3, //     10011

        OUTPUT_PRG_STOP           = 0xB4, //     10100

        // cMemory "MEMORY"
        //                                    11000...
        FILE                      = 0xC0, //       000
        ARRAY                     = 0xC1, //       001
        ARRAY_WRITE               = 0xC2, //       010
        ARRAY_READ                = 0xC3, //       011
        ARRAY_APPEND              = 0xC4, //       100
        MEMORY_USAGE              = 0xC5, //       101
        FILENAME                  = 0xC6, //       110

        // cMove "READ"
        //                                    110010..
        READ8                     = 0xC8, //        00
        READ16                    = 0xC9, //        01
        READ32                    = 0xCA, //        10
        READF                     = 0xCB, //        11

        // cMove "WRITE"
        //                                    110011..
        WRITE8                    = 0xCC, //        00
        WRITE16                   = 0xCD, //        01
        WRITE32                   = 0xCE, //        10
        WRITEF                    = 0xCF, //        11

        // cCom "COM"
        //                                    11010...
        COM_READY                 = 0xD0, //       000
        COM_READDATA              = 0xD1, //       001
        COM_WRITEDATA             = 0xD2, //       010
        COM_GET                   = 0xD3, //       011
        COM_SET                   = 0xD4, //       100
        COM_TEST                  = 0xD5, //       101
        COM_REMOVE                = 0xD6, //       110
        COM_WRITEFILE             = 0xD7, //       111

        //                                    11011...
        MAILBOX_OPEN              = 0xD8, //       000
        MAILBOX_WRITE             = 0xD9, //       001
        MAILBOX_READ              = 0xDA, //       010
        MAILBOX_TEST              = 0xDB, //       011
        MAILBOX_READY             = 0xDC, //       100
        MAILBOX_CLOSE             = 0xDD, //       101

        //        SPARE                       111.....

        // TST
        TST                       = 0xFF,  //  11111111
    }
}
