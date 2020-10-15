import sys

class Capabilities:
    """
    Identify what capabilities we have
    """
    def __init__(self, args=None):
        self.bluetooth_owners_capability = True
        self.bluetooth_speaker_capability = True
        self.network_monitor_capability = True
        self.internet_monitor_capability = True
        self.keyboard_monitor_capability = True
        if args is None:
            args = sys.argv
        self.enable_capabilities_from_command_line(args)

    def expect_keyboard(self):
        return self.keyboard_monitor_capability

    def expect_network(self):
        return self.network_monitor_capability

    def expect_internet(self):
        return self.internet_monitor_capability

    def expect_identity(self):
        return self.bluetooth_owners_capability

    def expect_bluetooth_speaker(self):
        return self.bluetooth_speaker_capability

    def enable_capabilities_from_command_line(self, args):
        for arg in args:
            if arg == "-owners":
                self.bluetooth_owners_capability = False
            if arg == "-bluetooth-speaker":
                self.bluetooth_speaker_capability = False
            if arg == "-network-monitor":
                self.network_monitor_capability = False
            if arg == "-internet-monitor":
                self.internet_monitor_capability = False
            if arg == "-keyboard":
                self.keyboard_monitor_capability = False

    def __repr__(self):
        str = "Identity={}, ".format(self.bluetooth_owners_capability)
        str += "Bt Speaker={}, ".format(self.bluetooth_speaker_capability)
        str += "Lnet={}, ".format(self.network_monitor_capability)
        str += "Inet={}, ".format(self.internet_monitor_capability)
        str += "Keyb={}".format(self.keyboard_monitor_capability)
        return str


