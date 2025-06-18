#!/usr/bin/env python3
"""Small program for the MNT Reform laptop to watch keyboard events and issue
an unconditional shutdown command when a certain key combination is pressed.
"""

### Parameters
input_device = "/dev/input/by-id/usb-MNT_Research_MNT_Reform_Keyboard_4.0_US_LT_RP2040-event-kbd"
shutdown_scancodes_combo = {59, 88}	#F1 and F12 pressed simulaneously
shutdown_command = "/usr/sbin/shutdown now"



### Modules
import os
import sys
import argparse
from setproctitle import setproctitle
from time import sleep
from evdev import InputDevice, categorize, ecodes
from select import select



### Routines
def main():
 
  setproctitle("mnt_hotkey_shutdown")

  # Parse the command line arguments
  argparser = argparse.ArgumentParser()

  argparser.add_argument(
	"-s", "--show-scancodes",
	help = "Print scancodes and simulate the shutdown command",
	action = "store_true")

  args = argparser.parse_args()


  # Open the HID device, watch scancodes coming in and initiate a shutdown
  # when the right combination is hit
  hiddev = None
  close_device = False
  stop = False

  current_keys_pressed = set()

  while True:

    # Close the HID device if needed
    if close_device:
      if hiddev is not None:
        try:
          hiddev.close()
        except:
          pass
        hiddev = None

      # Wait a bit to reopen the device if we're not stopping
      if not stop:
        sleep(2)

      close_device = False

    # Stop if needed
    if stop:
      return 0

    # Open the HID device
    if hiddev is None:
      try:
        hiddev = InputDevice(input_device)

      except KeyboardInterrupt:
        return -1

      except Exception as e:
        print("Error: could not open {}: {}".format(input_device, e),
		file = sys.stderr)
        close_device = True
        continue

      # If the user only wants to see the scancodes, tell them how to quit
      if args.show_scancodes:
        print("Showing scancodes. Press ESC to quit.")

    # Get events from the HID reader
    try:
      select([hiddev.fd], [], [], None)
      events = list(hiddev.read())

    except Exception as e:
      print("Error: could not get events from {}: {}".format(input_device, e),
		file = sys.stderr)
      close_device = True
      continue

    # Process HID events
    for event in events:

      # Key events?
      if event.type == ecodes.EV_KEY:

        d = categorize(event)

        scancode = d.scancode
        keydown = d.keystate

        # Track the keys currently pressed
        if keydown:
          current_keys_pressed.add(scancode)
        elif scancode in current_keys_pressed:
          current_keys_pressed.remove(scancode)

        # Show scancodes and simulate shutdown command if requested
        if args.show_scancodes:

          if keydown:

            # Did the user press ESC?
            if scancode == 1:
              close_device = True
              stop = True

            # Print the scancode
            else:
              print("Scancode:", d.scancode)

            # Print the shutdown command if the right keys are pressed
            if current_keys_pressed == shutdown_scancodes_combo:
              print("  Shutdown command to be issued:", shutdown_command)

          continue

        # Issue the shutdown command if the right keys are pressed
        if current_keys_pressed == shutdown_scancodes_combo:
          os.system(shutdown_command)



### Main routine
if __name__ == "__main__":
  sys.exit(main())
