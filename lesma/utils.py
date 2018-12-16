import sys
from halo import Halo

spinner = ""


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


def startSpinner(text):
    global spinner
    newLine = {
        "interval": 130,
        "frames": [
            "[-] {}".format(text),
            "[\\] {}".format(text),
            "[|] {}".format(text),
            "[/] {}".format(text)
        ]
    }
    spinner = Halo(text='', spinner=newLine, color="magenta")
    spinner.start()


def stopSpinner():
    spinner.stop()


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
