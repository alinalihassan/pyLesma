from huepy import bad, good, info, bold, red, green, orange
import sys

def error(text):
    print(bad(bold(red("Error:"))) + asciiToUnicode(text), file=sys.stderr)
    sys.exit(1)

def warning(text):
    print(info(bold(orange("Warning:"))) + asciiToUnicode(text), file=sys.stderr)

def successful(text):
    print(good(bold(green("Success:"))) + asciiToUnicode(text), file=sys.stderr)

def asciiToUnicode(text):
    finalStr = ""
    i = 0
    while i < len(text):
        if text[i] != "\\":
            finalStr += text[i]
            i+=1
        else:
            curUni = "0x"
            for j in range(i+3, i+7):
                curUni += text[j].upper()
            finalStr += chr(int(curUni, 16))
            i+=7

    return finalStr