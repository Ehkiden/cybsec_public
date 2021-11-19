import re
import threading
import warnings
from datetime import datetime
from time import sleep

from netmiko import Netmiko


class DMCA:
    # Filter warnings for CryptographyDeprecationWarning
    warnings.filterwarnings(action='ignore', module='.*paramiko.*')
    global results
    results = [
        {
            "dmca": {
                "device": [],
                "length": [],
                "error": []
            }
        }
    ]

    # Initialize the class with arguments
    def __init__(self, choice, user, password, mac, description):
        self.choice = choice
        self.user = user
        self.password = password
        self.mac = mac
        self.description = description

    # Initialize the controllers
    def do_setup(self):
        # The commented controllers have been deprecated according to Chris Schraff
        """
        cisco_wlc_1 = {
            "host": "172.22.253.15",
            "username": get_user,
            "password": get_password,
            "device_type": "cisco_wlc",
        }

        cisco_wlc_2 = {
            "host": "172.22.253.16",
            "username": get_user,
            "password": get_password,
            "device_type": "cisco_wlc",
        }

        cisco_wlc_3 = {
            "host": "172.22.253.17",
            "username": get_user,
            "password": get_password,
            "device_type": "cisco_wlc",
        }

        cisco_wlc_4 = {
            "host": "172.22.253.31",
            "username": get_user,
            "password": get_password,
            "device_type": "cisco_wlc",
        }
        """
        # create a list of objects for the WLCs
        wlc_list = ["172.24.47.77", "172.24.47.76", "172.24.47.13", "172.24.47.11", "172.22.253.9", "172.22.253.10",]
        wlc_objects = []
        for i in wlc_list:
            wlc_objects.append({
            "host": i,
            "username": self.user,
            "password": self.password,
            "device_type": "cisco_wlc",
        })

        return wlc_objects

        # return device_list

    # Connect to controllers and send commands
    def do_connect(self, device, cmd):
        output = results[0]["dmca"]["device"]
        error = results[0]["dmca"]["error"]
        did_connect = False

        try:
            net_connect = Netmiko(**device, banner_timeout=10)
            did_connect = True
        except Exception as e:
            error.append(e)
            return

        if did_connect:
            device_name = device['host']

            config_output = net_connect.send_config_set(cmd)

            if self.choice == "a":
                if "MAC filter already exists" in config_output:
                    output.append([device_name, self.mac + " already exists in controller!"])
                else:
                    show_output = net_connect.send_command('show exclusionlist')
                    sleep(1)

                    if self.mac in show_output:
                        output.append([device_name, self.mac + " successfully added!"])
                    else:
                        # If all goes wrong - print log
                        output.append([device_name, config_output])
            else:
                if "does not exist" in config_output:
                    output.append([device_name, self.mac + " does not exist in controller!"])
                else:
                    show_output = net_connect.send_command('show exclusionlist')
                    sleep(1)

                    if self.mac not in show_output:
                        output.append([device_name, self.mac + " successfully removed!"])
                    else:
                        # If all goes wrong - print log
                        output.append([device_name, config_output])

            net_connect.disconnect()
            return

    # Start the threading
    def do_dmca(self, get_devices, mac):
        output = results[0]["dmca"]["device"]
        length = results[0]["dmca"]["length"]

        def format_mac(mac: str) -> str:
            mac = re.sub('[.:-]', '', mac).lower()  # remove delimiters and convert to lower case
            mac = ''.join(mac.split())  # remove whitespaces
            assert len(mac) == 12  # length should be now exactly 12 (eg. 008041aefd7e)
            assert mac.isalnum()  # should only contain letters and numbers
            # convert mac in canonical form (eg. 00:80:41:ae:fd:7e)
            mac = ":".join(["%s" % (mac[i:i + 2]) for i in range(0, 12, 2)])
            return mac

        # If user presses enter for description
        if self.description == "":
            self.description = "dmca"

        # make description
        now = datetime.today().strftime("%x")
        desc = self.description + " - " + self.user + " - " + now

        if len(desc) > 32:
            length.append(f"Shorten your WLC description less than 33 characters! Length is {len(desc)} ")
            return results

        if self.choice == "a":
            cmd = ["config exclusionlist add " + format_mac(mac) + " \'" + desc + "\'"]
        elif self.choice == "r":
            cmd = ["config exclusionlist delete " + format_mac(mac)]
        else:
            cmd = ["config show exclusionlist"]

        for a_device in get_devices:
            thread = threading.Thread(target=DMCA.do_connect, args=(self, a_device, cmd), name="DMCA thread")
            thread.start()

        for t in threading.enumerate():
            t.join(10) if t is not threading.currentThread() else None

        return results

    def reset(self):
        global results
        results = [
            {
                "dmca": {
                    "device": [],
                    "length": [],
                    "error": []
                }
            }
        ]
