//
// Program.cs
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
using System.IO;
using System.Linq;

using Crc32;
using GUdev;

namespace Ev3FirmwareLoader.Cli
{
    class MainClass
    {
        public static void Main (string[] args)
        {
            Console.WriteLine ("EV3 Firmware Loader.");

            if (args.Length != 1) {
                Console.Error.WriteLine ("Usage: ev3fwload.exe <file>");
                Environment.Exit (1);
            }

            byte[] fwData = null;
            var fwFileName = args [0];

            try {
                fwData = File.ReadAllBytes (fwFileName);
            } catch (Exception ex) {
                Console.Error.WriteLine ("Error while opening '{0}'", fwFileName);
                Console.Error.WriteLine ("{0}", ex.Message);
                Environment.Exit (1);
            }

            Device ev3Device = null;

            try {
                using (var client = new Client (new [] { "hidraw" }))
                using (var hidrawDevices = client.QueryBySubsystem ("hidraw")) {
                    ev3Device = hidrawDevices.OfType<Device> ().Single (x => {
                        var usb = x.GetParentWithSubsystem ("usb", "usb_device");

                        var idVendor = usb.GetSysfsAttr ("idVendor");
                        if (idVendor != "0694") {
                            return false;
                        }

                        var idProduct = usb.GetSysfsAttr ("idProduct");
                        if (idProduct != "0006") {
                            return false;
                        }

                        return true;
                    });
                }
            } catch (Exception ex) {
                Console.Error.WriteLine ("Could not find EV3 Firmware Upload device");
                Console.Error.WriteLine ("{0}", ex.Message);
                Environment.Exit (1);
            }

            Stream hidrawStream = null;

            try {
                hidrawStream = File.Open (ev3Device.DeviceFile, FileMode.Open);
            } catch (Exception ex) {
                Console.Error.WriteLine ("Error while opening USB device '{0}'",
                    ev3Device.DeviceFile);
                Console.Error.WriteLine ("{0}", ex.Message);
                Environment.Exit (1);
            }

            var connection = new Connection (hidrawStream);

            var hwid = connection.GetVersion ();
            Console.WriteLine ("hwid: {0}", hwid);

            Console.WriteLine ("Erasing memory...");
            connection.EraseChip ();
            Console.WriteLine ("Done.");

            Console.WriteLine ("Downloading firmware...");
            connection.Download (fwData);
            Console.WriteLine ("Done.");

            Console.WriteLine ("Verifying...");
            var checksum = connection.GetChecksum (0, (uint)fwData.Length);
            var expectedChecksum = Crc32Algorithm.Compute (fwData);
            if (checksum != expectedChecksum) {
                Console.Error.WriteLine ("Bad checksum!");
                Environment.Exit (1);
            }
            Console.WriteLine ("OK.");

            Console.WriteLine ("Restaring EV3...");
            connection.StartApp ();
        }
    }

    /// <summary>
    /// Connection to EV3.
    /// </summary>
    public class Connection
    {
        /// <summary>
        /// The maximum size of the data that can be sent in a single message.
        /// </summary>
        const int maxDataSize = 1018;

        /// <summary>
        /// Global message counter.
        /// </summary>
        static ushort messageCount = 0;

        Stream stream;

        /// <summary>
        /// Initializes a new instance of the <see cref="Ev3FirmwareLoader.Cli.Connection"/> class.
        /// </summary>
        /// <param name="stream">The stream to use for communication.</param>
        public Connection (Stream stream)
        {
            this.stream = stream;
        }

        /// <summary>
        /// Download the specified data to the specified address.
        /// </summary>
        /// <param name="data">The data to download.</param>
        /// <param name="address">The address where the data will be stored.</param>
        public void Download (byte[] data, uint address = 0)
        {
            var paramData = new byte[8];

            WriteUInt32 (paramData, 0, address);
            WriteUInt32 (paramData, 4, (uint)data.Length);

            var num = SendCommand (Command.BeginDownload, paramData);
            ReceiveReply (Command.BeginDownload, num);

            var payload = new byte[maxDataSize];
            for (int i = 0; i < data.Length; i += maxDataSize) {
                var remainingLength = data.Length - i;
                if (remainingLength < maxDataSize) {
                    payload = new byte[remainingLength];
                }
                Array.Copy (data, i, payload, 0, payload.Length);
                num = SendCommand (Command.DownloadData, payload);
                ReceiveReply (Command.DownloadData, num);
            }
        }

        /// <summary>
        /// Erases the flash memory chip.
        /// </summary>
        public void EraseChip ()
        {
            var num = SendCommand (Command.ChipErase);
            ReceiveReply (Command.ChipErase, num);
        }

        /// <summary>
        /// Restarts the device
        /// </summary>
        public void StartApp ()
        {
            var num = SendCommand (Command.StartApp);
            ReceiveReply (Command.StartApp, num);
        }

        /// <summary>
        /// Gets the checksum.
        /// </summary>
        /// <returns>The checksum.</returns>
        /// <param name="address">The starting address of the data.</param>
        /// <param name="size">The size of the data.</param>
        public uint GetChecksum (uint address, uint size)
        {
            var paramData = new byte[8];

            WriteUInt32 (paramData, 0, address);
            WriteUInt32 (paramData, 4, size);

            var num = SendCommand (Command.GetChecksum, paramData);
            var result = ReceiveReply (Command.GetChecksum, num);

            uint checksum = ReadUInt32 (result, 0);

            return checksum;
        }

        /// <summary>
        /// Gets the version.
        /// </summary>
        /// <returns>The hwid version.</returns>
        public uint GetVersion ()
        {
            uint hwid, fwid;

            GetVersion (out hwid, out fwid);

            return hwid;
        }

        /// <summary>
        /// Gets the version.
        /// </summary>
        /// <param name="hwid">Hardware ID.</param>
        /// <param name="fwid">Firmware ID.</param>
        public void GetVersion (out uint hwid, out uint fwid)
        {
            var num = SendCommand (Command.GetVersion);
            var result = ReceiveReply (Command.GetVersion, num);
            hwid = ReadUInt32 (result, 0);
            fwid = ReadUInt32 (result, 4);
        }

        /// <summary>
        /// Sends the command.
        /// </summary>
        /// <returns>The message number.</returns>
        /// <param name="cmd">The command.</param>
        /// <param name="data">Extra command data.</param>
        ushort SendCommand (Command cmd, params byte[] data)
        {
            var message = new byte[1024];
            var num = messageCount++;

            if (data != null && data.Length > maxDataSize) {
                throw new ArgumentException ("Data is too large.", nameof (data));
            }

            ushort length = 4;
            if (data != null) {
                length += (ushort)data.Length;
                Array.Copy (data, 0, message, 6, data.Length);
            }
            WriteUInt16 (message, 0, length);
            WriteUInt16 (message, 2, num);
            message [4] = (byte)MessageType.SystemCommandReply;
            message [5] = (byte)cmd;

            stream.Write (message, 0, length + 2);

            return num;
        }

        /// <summary>
        /// Receives the reply.
        /// </summary>
        /// <returns>Extry reply data.</returns>
        /// <param name="cmd">The command.</param>
        /// <param name="num">The expected message number.</param>
        byte[] ReceiveReply (Command cmd, ushort num)
        {
            var message = new byte[1024];

            stream.Read (message, 0, 2);
            var length = ReadUInt16 (message, 0);

            stream.Read (message, 2, length);
            // there is always more to read, so get rid of it.
            stream.Flush ();

            var replyNum = ReadUInt16 (message, 2);
            if (replyNum != num) {
                throw new Exception ("Message number does not match in reply.");
            }

            var replyType = (MessageType)message [4];
            if (replyType == MessageType.SystemReplyError) {
                var replyStatus = (ReplyStatusCode)message [6];
                throw new ReplyStatusException (replyStatus);
            }
            if (replyType != MessageType.SystemReply) {
                throw new Exception ("Unexpected reply type.");
            }

            var replyCommand = (Command)message [5];
            if (replyCommand != cmd) {
                throw new Exception ("Command does not match in reply.");
            }

            return message.Skip (7).Take (length - 5).ToArray ();
        }

        /// <summary>
        /// Reads unsigned 16-bit little-endian integer from bytes.
        /// </summary>
        /// <returns>The value read.</returns>
        /// <param name="array">Array.</param>
        /// <param name="offset">Offset.</param>
        static ushort ReadUInt16(byte[] array, int offset)
        {
            return (ushort)((array [offset + 1] << 8) + array [offset]);
        }

        /// <summary>
        /// Writes unsigned 16-bit integer as little-endian bytes.
        /// </summary>
        /// <param name="array">Array.</param>
        /// <param name="offset">Offset.</param>
        /// <param name="value">The value to write.</param>
        static void WriteUInt16(byte[] array, int offset, ushort value)
        {
            array [offset] = (byte)(value & 0xFF);
            array [offset + 1] = (byte)((value >> 8) & 0xFF);
        }

        /// <summary>
        /// Reads unsigned 32-bit little-endian integer from bytes.
        /// </summary>
        /// <returns>The value read.</returns>
        /// <param name="array">Array.</param>
        /// <param name="offset">Offset.</param>
        static uint ReadUInt32(byte[] array, int offset)
        {
            return (uint)((array [offset + 3] << 24)
                + (array [offset + 2] << 16)
                + (array [offset + 1] << 8)
                + array [offset]);
        }

        /// <summary>
        /// Writes unsigned 32-bit integer as little-endian bytes.
        /// </summary>
        /// <param name="array">Array.</param>
        /// <param name="offset">Offset.</param>
        /// <param name="value">The value to write.</param>
        static void WriteUInt32(byte[] array, int offset, uint value)
        {
            array [offset] = (byte)(value & 0xFF);
            array [offset + 1] = (byte)((value >> 8) & 0xFF);
            array [offset + 2] = (byte)((value >> 16) & 0xFF);
            array [offset + 3] = (byte)((value >> 24) & 0xFF);
        }
    }

    /// <summary>
    /// Message type.
    /// </summary>
    public enum MessageType
    {
        /// <summary>
        /// System command, reply required.
        /// </summary>
        SystemCommandReply = 0x01,

        /// <summary>
        /// System command, reply not required.
        /// </summary>
        SystemCommandNoReply = 0x81,

        /// <summary>
        /// System reply, OK.
        /// </summary>
        SystemReply = 0x03,

        /// <summary>
        /// System reply, error.
        /// </summary>
        SystemReplyError = 0x05,
    }

    /// <summary>
    /// Reply status code.
    /// </summary>
    public enum ReplyStatusCode
    {
        Success,
        UnknownHandle,
        HandleNotReady,
        CorruptFile,
        NoHandlesAvailable,
        NoPermission,
        IllegalPath,
        FileExists,
        EndOfFile,
        SizeError,
        UnknownError,
        IllegalFileName,
        IllegalConnection,
    }

    /// <summary>
    /// Command.
    /// </summary>
    public enum Command
    {
        BeginDownloadWithErase = 0xF0,
        BeginDownload,
        DownloadData,
        ChipErase,
        StartApp,
        GetChecksum,
        GetVersion,
    }

    public class ReplyStatusException : Exception
    {
        public ReplyStatusCode Code { get; private set; }

        public ReplyStatusException (ReplyStatusCode code)
            : base (string.Format ("{0}", code))
        {
            Code = code;
        }
    }
}
