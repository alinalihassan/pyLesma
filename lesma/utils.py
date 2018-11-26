from huepy import bad, good, info, bold, red, green, orange
import sys

def error(text):
    print(bad(bold(red("Error:"))) + text, file=sys.stderr)
    sys.exit(1)

def warning(text):
    print(info(bold(orange("Warning:"))) + text, file=sys.stderr)

def successful(text):
    print(good(bold(green("Success:"))) + text, file=sys.stderr)