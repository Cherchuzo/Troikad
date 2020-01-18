# Troikad
**A file transfer application with multiple connection modes written in Python**

This python module use all built-in libraries


## Usage

Assuming that you have an internet connection:

There are two connection mode included in this application:

   -standard connection is used when the receiver has opened TCP port 2442, allowing the sender to connect.
   
   -Reverse connection may be used when the receiver has not opened the TCP port or is under [NAT](https://en.wikipedia.org/wiki/Network_address_translation), but requires that the sender has the port open.
    With TCP it is difficult to implement a serverless STUN mechanism


## Installation

First you need to install, if you have not already done so, python.
To do this, if you are using ubuntu, just open Terminal and type:
```
sudo apt-get install python3.x
```
where x is the version you want to install

*If you are using Microsoft Windows:
Go to [python](https://www.python.org/) official website and download the latest version for [Windows](https://www.python.org/downloads/windows/)

## Limitations

This module cannot work on versions of python less than 3.x.
If you encounter problems or bugs, just report it, at least I can try to solve them