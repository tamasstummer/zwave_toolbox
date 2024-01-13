
import os
import subprocess
import re
import argparse

class DeviceInfo:
    def __init__(self):
        self.devices = {
            'deviceCount': 0,
            'deviceDetails': []
        }

    def add_device(self, jlink_number, board_name):
        self.devices['deviceDetails'].append({'jlink_number': jlink_number, 'board_name': board_name})

    def set_device_count(self, count):
        self.devices['deviceCount'] = count

    def get_device_info(self):
        return self.devices
    
    def print_device_info(self):
        print(self.devices['deviceCount'])
        for device in self.devices['deviceDetails']:
            print(self.devices['jlink_number'] + " " + device['board_name'])

class Inspector:
    inspector_path = None
    device_info = DeviceInfo()

    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.inspector_path = os.path.join(base_path, 'tools', 'inspector', 'inspect_emdll', 'inspect_emdll.exe')
        if not os.path.exists(self.inspector_path):
            raise FileNotFoundError("inspect_emdll.exe not found at path: " + self.inspector_path)
        
    def __run_command(self, command):
        """
        Runs a command and returns its output.
        """
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        return output.decode('utf-8'), error.decode('utf-8'), process.returncode

    def __check_regex(self, regex_input, text):
        """
        Checks if the given regex pattern is found in the text.
        """
        regex = re.compile(regex_input)
        match = regex.search(text)
        return match

    def get_devices(self):
        command = self.inspector_path + " -slist"
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("deviceCount=0", output)
        if match:
            print("ERROR during get devices")
            return None
        else:
            self.__parse_custom_format(output)
            return self.device_info.get_device_info()
    
    def print_devices(self):
        print(self.device_info.get_device_info())
        
    def __parse_custom_format(self, text):
        buffer = []
        for line in text.splitlines():
            if self.__check_regex("deviceCount", line):
                count = line.split("=")[1]
                self.device_info.set_device_count(count)
            # check serialNumber with regex
            if self.__check_regex("serialNumber", line):
                serial_number = line.split("=")[1]
                buffer.append(serial_number)
            if self.__check_regex("boardName", line):
                board_name = line.split("=")[1]
                if board_name.startswith("BRD4001C") or \
                board_name.startswith("BRD4002A") or \
                board_name.startswith("BRD8029A"):
                    continue
                else:
                    buffer.append(board_name.split(" ")[0])
        for i in range(0, len(buffer), 2):
            self.device_info.add_device(buffer[i], buffer[i+1])
                
def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Device Inspector Tool')
    
    # Add arguments
    parser.add_argument('--get_devices', action='store_true', help='Get the list of devices')
    parser.add_argument('--print_devices', action='store_true', help='Print the list of devices')

    # Parse the arguments
    args = parser.parse_args()

    # Create an instance of Inspector
    inspector = Inspector()

    # Execute based on arguments
    if args.get_devices:
        inspector.get_devices()
    if args.print_devices:
        inspector.print_devices()

if __name__ == "__main__":
    main()

# Usage:
# python script_name.py --get_devices
# python script_name.py --print_devices
# python script_name.py --get_devices --print_devices
