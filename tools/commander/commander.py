import os
import re
import subprocess
import argparse

class Commander:

    commander_path = None
    regions = {
      'eu':'0x00',
      'us':'0x01',
      'anz':'0x02',
      'hk':'0x03',
      'in':'0x05',
      'il':'0x06',
      'ru':'0x07',
      'cn':'0x08',
      'us_lr':'0x09',
      'jp':'0x32',
      'kr':'0x33',
    }
        
    def __init__(self):

        #store the commander's path
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.commander_path = os.path.join(base_path, 'tools', 'commander', 'commander', 'commander.exe')
        if not os.path.exists(self.commander_path):
            raise FileNotFoundError("commander.exe not found at path: " + self.commander_path)
        
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

    def reset(self, serialno):
        command = self.commander_path + " device reset --serialno " + str(serialno) + " --device cortex-m33"
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("ERROR", output)
        if match:
            print("ERROR during reset")
            return None
        else :
            print("Device reset")
            return True

    def erase(self, serialno):
        command = self.commander_path + " device recover --serialno " + str(serialno) + " --device cortex-m33"
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("ERROR", output)
        if match:
            print("ERROR during reset")
            return None
        else:
            print("Device erased")
            return True

    def set_region(self, serialno, region):
        command = self.commander_path + " flash --tokengroup znet --token MFG_ZWAVE_COUNTRY_FREQ:" + str(self.regions[region])  + " --serialno " + str(serialno)
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("ERROR", output)
        if match:
            print("ERROR during set region")
            return None
        else:
            print("Region set to " + region.upper())
            return True
        
    def get_region(self, serialno):
        command = self.commander_path + " tokendump --tokengroup znet --token MFG_ZWAVE_COUNTRY_FREQ --serialno " + str(serialno)
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("ERROR", output)
        if match:
            print("ERROR during get region")
            return None
        else:
            match = self.__check_regex("0x[0-9A-Fa-f]+", output)
            if match:
                for key, val in self.regions.items():
                    if val == str(match.group(0)):
                        print("Region is " + str(key).upper())
                        str(key).upper()

            else:
                print("ERROR during get region")
                return None


    def get_dsk(self, serialno):
        command = self.commander_path + " tokendump --tokengroup znet --token MFG_ZW_QR_CODE --serialno " + str(serialno)
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("ERROR", output)
        if match:
            print("ERROR during get dsk")
            return None
        else:
            match = self.__check_regex("\d{90}", output)
            if match:
                number = str(match.group(0))[12:52] # DSK starts at 13th char and 40 chars long
                chunks = [number[i:i+5] for i in range(0, len(number), 5)] # split into chunks of 5 chars
                formatted_number = " - ".join(chunks)
                print("DSK is " + formatted_number)
                return formatted_number
            else:
                print("ERROR during get dsk")
                return None

    def get_qr(self, serialno):
        command = self.commander_path + " --apack device zwave-qrcode --serialno " + str(serialno) + " --timeout 2000 --tif swd"
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("ERROR", output)
        if match:
            print("ERROR during get dsk")
            return None
        else:
            match = self.__check_regex("\d{97}", output)
            if match:
                print("QR is " + str(match.group(0)))
                return str(match.group(0))
            else:
                print("ERROR during get dsk")
                return None

    def flash(self ,serialno, hex_file_path):
        command = self.commander_path + " flash " + hex_file_path + " --serialno " + str(serialno) + " --device cortex-m33"
        output, error, exit_code = self.__run_command(command)
        match = self.__check_regex("ERROR", output)
        if match:
            print("ERROR during flash")
            return None
        else:
            print("Flash successful")
            return True

def main():
    parser = argparse.ArgumentParser(description="Commander Script")
    parser.add_argument("command", choices=["reset", "erase", "set_region", "get_region", "get_dsk", "get_qr", "flash"])
    parser.add_argument("serialno", help="Serial number of the device")
    parser.add_argument("--region", help="Region code for setting region", default=None)
    parser.add_argument("--hex_file_path", help="Path to the hex file for flashing", default=None)

    args = parser.parse_args()

    commander = Commander()

    if args.command == "reset":
        commander.reset(args.serialno)
    elif args.command == "erase":
        commander.erase(args.serialno)
    elif args.command == "set_region":
        if args.region:
            commander.set_region(args.serialno, args.region)
        else:
            print("Region not provided for set_region command")
    elif args.command == "get_region":
        commander.get_region(args.serialno)
    elif args.command == "get_dsk":
        commander.get_dsk(args.serialno)
    elif args.command == "get_qr":
        commander.get_qr(args.serialno)
    elif args.command == "flash":
        if args.hex_file_path:
            commander.flash(args.serialno, args.hex_file_path)
        else:
            print("Hex file path not provided for flash command")

if __name__ == "__main__":
    main()

# Example calls
# python commander_script.py reset       your_serial_number
# python commander_script.py erase       your_serial_number
# python commander_script.py set_region  your_serial_number --region us
# python commander_script.py get_region  your_serial_number
# python commander_script.py get_dsk     your_serial_number
# python commander_script.py get_qr      your_serial_number
# python commander_script.py flash       your_serial_number --hex_file_path your_hex_file_path
