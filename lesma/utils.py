from huepy import bad, good, info, bold, red, green, orange
import sys

def error(text):
    print(bad(bold(red("Error:"))), text)
    sys.exit(1)

def warning(text):
    print(info(bold(orange("Warning:"))), text)

def successful(text):
    print(good(bold(green("Success:"))), text)
