import gi.repository.GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import pprint
from IPython import embed

def notifications(bus, message):
    pprint.pp(message)
    pprint.pp(message.get_args_list())
    # embed()

DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications'")
bus.add_message_filter(notifications)

mainloop = gi.repository.GLib.MainLoop()
mainloop.run()