//
// DataTypes.cs
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
    public interface IDataType : IEnumerable<byte>
    {
    }

    /// <summary>
    /// 8-bit signed integer.
    /// </summary>
    public interface IData8 : IDataType
    {
    }

    /// <summary>
    /// 16-bit signed integer.
    /// </summary>
    public interface IData16 : IDataType
    {
    }

    /// <summary>
    /// 32-bit signed integer.
    /// </summary>
    public interface IData32 : IDataType
    {
    }

    /// <summary>
    /// 32-bit IEEE floating point.
    /// </summary>
    public interface IDataFloat : IDataType
    {
    }

    /// <summary>
    /// Null terminated string.
    /// </summary>
    public interface IDataString : IDataType
    {
    }

    abstract class AbstractConstant : IEnumerable<byte>
    {
        /// <summary>
        /// The lms2012 byte code representation of the data type.
        /// </summary>
        protected byte[] Data;

        #region IEnumerable implementation
        public IEnumerator<byte> GetEnumerator ()
        {
            return Data.Cast<byte> ().GetEnumerator ();
        }
        #endregion
        #region IEnumerable implementation
        System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator ()
        {
            return Data.GetEnumerator ();
        }
        #endregion
    }

    /// <summary>
    /// Constants.
    /// </summary>
    public static class Constant
    {
        /// <summary>
        /// Create new 8-bit signed integer constant from value.
        /// </summary>
        /// <param name="value">Value.</param>
        public static IData8 Int8 (sbyte value)
        {
            if (value == sbyte.MinValue) {
                throw new ArgumentException ("Value reserved for Nan8.", nameof (value));
            }
            return new ConstInt8 (value);
        }

        /// <summary>
        /// The maximum 8-bit signed integer value (127).
        /// </summary>
        public static IData8 Int8Max {
            get {
                return new ConstInt8 (sbyte.MaxValue);
            }
        }

        /// <summary>
        /// The minimum 8-bit signed integer value (-127).
        /// </summary>
        public static IData8 Int8Min {
            get {
                return new ConstInt8 (sbyte.MinValue + 1);
            }
        }

        /// <summary>
        /// The 8-bit signed integer not-a-number value (-128).
        /// </summary>
        public static IData8 Int8NaN {
            get {
                return new ConstInt8 (sbyte.MinValue);
            }
        }

        /// <summary>
        /// Create new 16-bit signed integer constant from value.
        /// </summary>
        /// <param name="value">Value.</param>
        public static IData16 Int16 (short value)
        {
            if (value == short.MinValue) {
                throw new ArgumentException ("Value reserved for Nan16.", nameof (value));
            }
            return new ConstInt16 (value);
        }

        /// <summary>
        /// The maximum 16-bit signed integer value (32767).
        /// </summary>
        public static IData16 Int16Max {
            get {
                return new ConstInt16 (short.MaxValue);
            }
        }

        /// <summary>
        /// The minimum 16-bit signed integer value (-32767).
        /// </summary>
        public static IData16 Int16Min {
            get {
                return new ConstInt16 (short.MinValue + 1);
            }
        }

        /// <summary>
        /// The 16-bit signed integer not-a-number value (-32768).
        /// </summary>
        public static IData16 Int16NaN {
            get {
                return new ConstInt16 (short.MinValue);
            }
        }

        /// <summary>
        /// Create new 32-bit signed integer constant from value.
        /// </summary>
        /// <param name="value">Value.</param>
        public static IData32 Int32 (int value)
        {
            if (value == int.MinValue) {
                throw new ArgumentException ("Value reserved for Nan32.", nameof (value));
            }
            return new ConstInt32 (value);
        }

        /// <summary>
        /// The maximum 32-bit signed integer value (2147483647).
        /// </summary>
        public static IData32 Int32Max {
            get {
                return new ConstInt32 (int.MaxValue);
            }
        }

        /// <summary>
        /// The minimum 32-bit signed integer value (-2147483647).
        /// </summary>
        public static IData32 Int32Min {
            get {
                return new ConstInt32 (int.MinValue + 1);
            }
        }

        /// <summary>
        /// The 32-bit signed integer not-a-number value (-2147483648).
        /// </summary>
        public static IData32 Int32NaN {
            get {
                return new ConstInt32 (int.MinValue);
            }
        }

        /// <summary>
        /// Create new 32-bit signed integer constant from value.
        /// </summary>
        /// <param name="value">Value.</param>
        public static IDataFloat Float (float value)
        {
            return new ConstFloat (value);
        }
    }

    sealed class ConstInt8 : AbstractConstant, IData8
    {
        public ConstInt8 (sbyte value)
        {
            // See if value is small enough to fit in a single byte.
            // Cast to int to prevent overflow.
            var absValue = Math.Abs ((int)value);
            if (absValue <= (byte)ParamFlags.IndexMask) {
                var flags = ParamFlags.Const | ParamFlags.Short;
                if (value < 0) {
                    flags |= ParamFlags.ConstSign;
                }
                Data = new [] { (byte)(absValue | (byte)flags) };
            } else {
                var flags = ParamFlags.Const | ParamFlags.Long | ParamFlags.OneByte;
                Data = new [] { (byte)flags, (byte)value };
            }
        }
    }

    sealed class ConstInt16 : AbstractConstant, IData16
    {
        public ConstInt16 (short value)
        {
            var flags = ParamFlags.Const | ParamFlags.Long | ParamFlags.TwoBytes;
            Data = new [] { (byte)flags, (byte)(value & 0xFF), (byte)(value >> 8) };
        }
    }

    sealed class ConstInt32 : AbstractConstant, IData32
    {
        public ConstInt32 (int value)
        {
            var flags = ParamFlags.Const | ParamFlags.Long | ParamFlags.FourBytes;
            Data = new [] {
                (byte)flags,
                (byte)(value & 0xFF),
                (byte)((value >> 8) & 0xFF),
                (byte)((value >> 16) & 0xFF),
                (byte)((value >> 24) & 0xFF),
            };
        }
    }

    sealed class ConstFloat : AbstractConstant, IDataFloat
    {
        public ConstFloat (float value)
        {
            // LEGO uses special value for NaN
            var intValue = float.IsNaN(value) ? 0x7FC00000
                : BitConverter.ToInt32 (BitConverter.GetBytes (value), 0);
            var flags = ParamFlags.Const | ParamFlags.Long | ParamFlags.FourBytes;
            Data = new [] {
                (byte)flags,
                (byte)(intValue & 0xF),
                (byte)((intValue >> 8) & 0xFF),
                (byte)((intValue >> 16) & 0xFF),
                (byte)((intValue >> 24) & 0xFF),
            };
        }
    }

    /// <summary>
    /// Local variable.
    /// </summary>
    public static class LocalVar
    {
        public static IData8 Int8 ()
        {
            return new LocalInt8 ();
        }
    }

    abstract class AbstractVariable : IEnumerable<byte>
    {
        protected ParamFlags Flags;
        internal int Offset;

        #region IEnumerable implementation
        public IEnumerator<byte> GetEnumerator ()
        {
            if (Offset <= (int)ParamFlags.IndexMask) {
                yield return (byte)((byte)Flags | Offset);
            } else {
                // TODO: this could be made more efficent by checking the minimum size
                yield return (byte)(Flags | ParamFlags.Long | ParamFlags.FourBytes);
                yield return (byte)(Offset & 0xFF);
                yield return (byte)((Offset >> 8) & 0xFF);
                yield return (byte)((Offset >> 16) & 0xFF);
                yield return (byte)((Offset >> 24) & 0xFF);
            }
        }
        #endregion
        #region IEnumerable implementation
        System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator ()
        {
            return GetEnumerator ();
        }
        #endregion
    }

    sealed class LocalInt8 : AbstractVariable, IData8
    {
        public LocalInt8 ()
        {
            Flags = ParamFlags.Variable | ParamFlags.Local;
        }
    }

    [Flags]
    enum ParamFlags : byte
    {
        Short = 0x00,
        Long = 0x80,
        Const = 0x00,
        Variable = 0x40,
        Local = 0x00,
        Global = 0x20,
        Handle = 0x10,
        Address = 0x08,
        IndexMask = 0x1F,
        ConstSign = 0x20,
        ValueMask = 0x3F,
        BytesMask = 0x07,
        StringOld = 0,
        OneByte = 1,
        TwoBytes = 2,
        FourBytes = 3,
        String = 4,
        Label = 0x20,
    }
}
