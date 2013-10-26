Multipath tcp packetdrill version README:
-----------------------------------------

This repository contains the current work status of my work on Packetdrill.

The goal of this packetdrill extension is to enable simultaneous TCP socket support
in order to test multipath TCP stack implementation. Indeed, to properly test it we need to
establish various Multipath TCP subflows, each of them being a TCP flow.
Simultaneous socket support and MPTCP Three-way-handshare are implemented and working.
mp_join was working but is being refactored.

For various reasons the major part of the code was added through a ultra big commit.
I planned to restart from the last packetdrill version and commit portions of code accompanied
of their clear explanation when I will have time.

I started to implement the DSS MPTCP option but it's ongoing work. I'm rather trying to refactor
mp_join code and adding support of various ways to specify parameters to mptcp options (full auto,
full manual, or partially auto.). Thus current mp_join that was working before isn't working right
now due to this major ongoing refactoring.

New packetdrill features offered by this extension:
    
    In local mode (no yet test on wire_server mode), both in ipv4 and ipv6 mode:
    - partial implementation of bind syscall allowing to specify a different destination port
      for each socket.
    - multisocket support: it is possible to establish multiple tcp connections
    in a single packetdrill session (script). An implementation constraint is that
    mutliple tcp three way handshakes can't be interleaved in the script.
    - multipath tcp options implementation: mp_capable and mp_join "in both direction"
    (first syn sent by packetdrill - first syn sent by kernel).
    
Other mptcp options are on the TODO list.
    
README povided by google for their original packetdrill version:
----------------------------------------------------------------

packetdrill
===========

This directory contains the source code for the packetdrill network
stack testing tool.

The web site for packetdrill is here:

https://code.google.com/p/packetdrill/


building
========

To build packetdrill, first install flex and bison.

Then set up the Makefile for your platform:

# ./configure

Then build the tool:

# make


running
=======

Here's a quick example.

On FreeBSD, OpenBSD, and NetBSD, try:

# ./packetdrill examples/fr-4pkt-sack-bsd.pkt

On Linux try:

# ./packetdrill examples/fr-4pkt-sack-linux.pkt


license
=======

The packetdrill tool is released under version 2 of the GPL. See the
COPYING file for full details.


discussion and contributions
==============================

If you have any questions, or code or patches to offer, please join
the packetdrill e-mail list at:

http://groups.google.com/group/packetdrill

Contributions of code or tests are both welcomed!

Enjoy!
