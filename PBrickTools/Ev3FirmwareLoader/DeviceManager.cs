//
// DeviceManager.cs
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
using GUdev;

namespace Ev3FirmwareLoader
{
    public class DeviceManager
    {
        const string usb_subsystem = "usb";
        const string hid_subsystem = "hid";
        const string hidraw_subsystem = "hidraw";

        const string lego_usb_vendor_id = "0694";
        const string lego_ev3_usb_product_id = "0005";
        const string lego_ev3_fw_update_usb_product_id = "0006";

        Client client;

        public delegate void DeviceAddedHandler (object sender, DeviceAddedEventArgs e);

        public event DeviceAddedHandler DeviceAdded;

        public DeviceManager ()
        {
            client = new Client (new [] { hidraw_subsystem });
        }

        public void Init ()
        {
            client.Uevent += Client_Uevent;
            foreach (var device in client.QueryBySubsystem (hidraw_subsystem)) {
                var args = new UeventArgs () {
                    Args = new object[] { "add", device }
                };
                Client_Uevent (this, args);
            }
        }

        void Client_Uevent (object o, UeventArgs args)
        {
            var usb = args.Device.GetParentWithSubsystem (usb_subsystem, "usb_device");
            var hid = args.Device.GetParentWithSubsystem (hid_subsystem, null);
            var idVendor = usb.GetSysfsAttr ("idVendor");
            var idProduct = usb.GetSysfsAttr ("idProduct");
            if (idVendor != "0694" || idProduct != "0006") {
                return;
            }
            switch (args.Action) {
            case "add":
                onDeviceAdded (new Device (hid.GetProperty ("HID_NAME"), args.Device.DeviceFile));
                break;
            case "remove":
                break;
            }
        }

        void onDeviceAdded (Device device)
        {
            if (DeviceAdded != null) {
                DeviceAdded (this, new DeviceAddedEventArgs (device));
            }
        }
    }

    public class DeviceAddedEventArgs : EventArgs
    {
        public Device Device { get; private set; }

        public DeviceAddedEventArgs (Device device)
        {
            Device = device;
        }
    }
}
