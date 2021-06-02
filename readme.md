# Casey Doran's Keybow 2040 config

## embedded code
Circuitpython source lives in the `embedded/` directory. I use whatever circuitpython image came pre-flashed on the keybow when I got it. The code is pretty much all following examples that came pre-flashed, though I had to discover the `usb_cdc` trick myself.

## service code
I'm working on a simple python service that snoops your user dbus session, slurps up notification events, and sends commands to the keybow over serial. For instance, a thunderbird notification might send a "light up" command to your keybow's email key, or a "lock" key might only be lit when the user session is unlocked.
Snooping the user is accomplished (maybe) following the example on https://github.com/facebookincubator/pystemd/blob/master/examples/monitor.py to use the `BecomeMonitor` call. 

## art
I have some docs in this directory that I can print out and cut out with an x-acto knife to provide icons for the Pimoroni Relegendable Keycaps. I find that white printer paper looks fine, and I only have a laser printer so the icons are all black. I got the icons from https://github.com/gusbemacbe/suru-plus-aspromauros