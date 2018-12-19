import sys
from halo import Halo


class Spinner:
    def __init__(self):
        self.spinner = None

    def startSpinner(self, text):
        newLine = {
            "interval": 130,
            "frames": [
                "[-] {}".format(text),
                "[\\] {}".format(text),
                "[|] {}".format(text),
                "[/] {}".format(text)
            ]
        }
        self.spinner = Halo(text='', spinner=newLine, color="magenta")
        self.spinner.start()

    def stopSpinner(self):
        if self.spinner is not None:
            self.spinner.stop()


def error(text):
    print(u'\033[{}m{}\033[0m{}'.format("31;1", "[-] Error: ",
          asciiToUnicode(text)), file=sys.stderr)
    sys.exit(1)


def warning(text):
    print(u'\033[{}m{}\033[0m{}'.format("33;1", "[!] Warning: ",
          asciiToUnicode(text)), file=sys.stderr)


def successful(text):
    print(u'\033[{}m{}\033[0m{}'.format("32;1", "[+] Success: ",
          asciiToUnicode(text)), file=sys.stderr)


def asciiToUnicode(text):
    finalStr = ""
    i = 0
    while i < len(text):
        if text[i] != "\\":
            finalStr += text[i]
            i += 1
        else:
            curUni = "0x"
            for j in range(i + 3, i + 7):
                curUni += text[j].upper()
            finalStr += chr(int(curUni, 16))
            i += 7

    return finalStr
