import os
import re
import subprocess

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

# def main():
#     commander = Commander()
#     commander.erase("440265308")
#     commander.reset("440265308")
#     commander.set_region("440265308", "us_lr")
#     commander.get_region("440265308")
#     commander.flash("440265308", "C:/Users/tastumme/Desktop/z-wave/demos/zwave_soc_power_strip/zwave_soc_power_strip-brd4205b-eu.hex")
#     commander.get_dsk("440265308")
#     commander.get_qr("440265308")

# if __name__ == "__main__":
#     main()
