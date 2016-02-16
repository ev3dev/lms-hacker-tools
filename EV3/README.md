EV3
===

Tools for LEGO MINDSTORMS EV3

ev3_dissector.lua
-----------------

A [Wireshark](https://www.wireshark.org/) dissector for decoding the LEGO
MINDSTORMS EV3 communication protocol.

### Usage

Start Wireshark from the command line using:

    wireshark -X lua_script:ev3_dissector.lua

Or add `ev3_dissector.lua` to your Wireshark personal plugins directory. You can
find this directory by looking at the `Folders` tab of the `About` dialog box
in Wireshark.

Any packets to or from TCP port 5555 will be interpreted as "EV3" protocol. USB
interrupt data with class IF_CLASS_UNKNOWN will also be interpreted as "EV3"
protocol.

You can also use the filter to search for packets that contain certain types of
data. For example if you want to search for all packets that use the `LIST_FILES`
system command, then you would use `ev3.sys_cmd == 0x99` for the filter.

### Status

* Currently works with Wi-Fi and USB only.
* All opcodes for direct commands are implemented.
* Only a few system commands are implemented.

### TODO

* Finish implementing direct commands
* Prevent duplicate global variables in replies.
* Add support for Bluetooth.

lmsdisasm.py
------------

Disassembler for LEGO MINDSTORMS EV3 `.rbf` program files. Files are converted
to `.lms` format that can be recompiled using the `assembler.jar` tool that is
included in the `lms2012` source code.

### Prerequisites

Install required package:

    pip install enum34

or

    sudo apt-get install python-enum34

### Usage

From a command line run:

    python lmsdisasm.py input.rbf -o output.lms

If the `-o output.lms` option is omitted, then the `.lms` file is printed to
the standard output.
