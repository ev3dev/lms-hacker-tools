//
// EV3DataTypesTest.cs
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

using NUnit.Framework;
using System;
using System.Linq;
using BrickCommander.IO.EV3;

namespace IOTest
{
    [TestFixture]
    public class EV3DataTypesTest
    {
        [Test]
        public void TestConstInt8 ()
        {
            byte[] actual, expected;

            actual = Constant.Int8 (0).ToArray ();
            expected = new byte [] { 0x00 };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the largest value that fits in one byte
            actual = Constant.Int8 (31).ToArray ();
            expected = new byte [] { 0x1F };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the smallest value that fits in one byte
            actual = Constant.Int8 (-31).ToArray ();
            expected = new byte [] { 0x3F };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the smallest positive value that requires two bytes
            actual = Constant.Int8 (32).ToArray ();
            expected = new byte [] { 0x81, 0x20 };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the largest negative value that requires two bytes
            actual = Constant.Int8 (-32).ToArray ();
            expected = new byte [] { 0x81, 0xE0 };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the largest possible value
            actual = Constant.Int8 (sbyte.MaxValue).ToArray ();
            expected = new byte [] { 0x81, 0x7F };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the smallest possible value
            actual = Constant.Int8 (sbyte.MinValue + 1).ToArray ();
            expected = new byte [] { 0x81, 0x81 };
            Assert.That (actual, Is.EqualTo (expected));

            // this is not allowed
            Assert.That (() => Constant.Int8 (sbyte.MinValue),
                Throws.ArgumentException);
        }

        [Test]
        public void TestConstMin8 ()
        {
            var expected = new byte [] { 0x81, 0x81 };
            Assert.That (Constant.Int8Min, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstMax8 ()
        {
            var expected = new byte [] { 0x81, 0x7F };
            Assert.That (Constant.Int8Max, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstNan8 ()
        {
            var expected = new byte [] { 0x81, 0x80 };
            Assert.That (Constant.Int8NaN, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstInt16 ()
        {
            byte[] actual, expected;

            actual = Constant.Int16 (0).ToArray ();
            expected = new byte [] { 0x82, 0x00, 0x00 };
            Assert.That (actual, Is.EqualTo (expected));

            actual = Constant.Int16 (1).ToArray ();
            expected = new byte [] { 0x82, 0x01, 0x00 };
            Assert.That (actual, Is.EqualTo (expected));

            actual = Constant.Int16 (-1).ToArray ();
            expected = new byte [] { 0x82, 0xFF, 0xFF };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the largest possible value
            actual = Constant.Int16 (short.MaxValue).ToArray ();
            expected = new byte [] { 0x82, 0xFF, 0x7F };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the smallest possible value
            actual = Constant.Int16 (short.MinValue + 1).ToArray ();
            expected = new byte [] { 0x82, 0x01, 0x80 };
            Assert.That (actual, Is.EqualTo (expected));

            // this is not allowed
            Assert.That (() => Constant.Int16 (short.MinValue),
                Throws.ArgumentException);
        }

        [Test]
        public void TestConstMin16 ()
        {
            var expected = new byte [] { 0x82, 0x01, 0x80 };
            Assert.That (Constant.Int16Min, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstMax16 ()
        {
            var expected = new byte [] {  0x82, 0xFF, 0x7F };
            Assert.That (Constant.Int16Max, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstNan16 ()
        {
            var expected = new byte [] { 0x82, 0x00, 0x80 };
            Assert.That (Constant.Int16NaN, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstInt32 ()
        {
            byte[] actual, expected;

            actual = Constant.Int32 (0).ToArray ();
            expected = new byte [] { 0x83, 0x00, 0x00, 0x00, 0x00 };
            Assert.That (actual, Is.EqualTo (expected));

            actual = Constant.Int32 (1).ToArray ();
            expected = new byte [] { 0x83, 0x01, 0x00, 0x00, 0x00 };
            Assert.That (actual, Is.EqualTo (expected));

            actual = Constant.Int32 (-1).ToArray ();
            expected = new byte [] { 0x83, 0xFF, 0xFF, 0xFF, 0xFF };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the largest possible value
            actual = Constant.Int32 (int.MaxValue).ToArray ();
            expected = new byte [] { 0x83, 0xFF, 0xFF, 0xFF, 0x7F };
            Assert.That (actual, Is.EqualTo (expected));

            // this is the smallest possible value
            actual = Constant.Int32 (int.MinValue + 1).ToArray ();
            expected = new byte [] { 0x83, 0x01, 0x00, 0x00, 0x80 };
            Assert.That (actual, Is.EqualTo (expected));

            // this is not allowed
            Assert.That (() => Constant.Int32 (int.MinValue),
                Throws.ArgumentException);
        }

        [Test]
        public void TestConstMin32 ()
        {
            var expected = new byte [] { 0x83, 0x01, 0x00, 0x00, 0x80 };
            Assert.That (Constant.Int32Min, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstMax32 ()
        {
            var expected = new byte [] { 0x83, 0xFF, 0xFF, 0xFF, 0x7F };
            Assert.That (Constant.Int32Max, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstNan32 ()
        {
            var expected = new byte [] { 0x83, 0x00, 0x00, 0x00, 0x80 };
            Assert.That (Constant.Int32NaN, Is.EqualTo (expected));
        }

        [Test]
        public void TestConstFloat ()
        {
            byte[] actual, expected;

            actual = Constant.Float (0).ToArray ();
            expected = new byte [] { 0x83, 0x00, 0x00, 0x00, 0x00 };
            Assert.That (actual, Is.EqualTo (expected));

            actual = Constant.Float (1).ToArray ();
            expected = new byte [] { 0x83, 0x00, 0x00, 0x80, 0x3F };
            Assert.That (actual, Is.EqualTo (expected));

            actual = Constant.Float (-1).ToArray ();
            expected = new byte [] { 0x83, 0x00, 0x00, 0x80, 0xBF };
            Assert.That (actual, Is.EqualTo (expected));

            // LEGO is special and has a non-standard floating point NaN.
            actual = Constant.Float (float.NaN).ToArray ();
            expected = new byte [] { 0x83, 0x00, 0x00, 0xC0, 0x7F };
            Assert.That (actual, Is.EqualTo (expected));
        }
    }
}
