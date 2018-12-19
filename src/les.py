"""Lesma programming language

usage:
    lesma compile [-ldo FILE] <file>
    lesma run [-td] <file>
    lesma [-hv]

options:
    -h, --help                  Shows this help menu
    -v, --version               Shows the version
    -l, --llvm                  Emit llvm code
    -o FILE, --output FILE      Output file
    -t, --timer                 Time the execution
    -d, --debug                 Debug mode
"""

from lesma.lexer import Lexer
from lesma.parser import Parser
from lesma.type_checker import Preprocessor
from lesma.compiler.code_generator import CodeGenerator
from lesma.utils import error
from docopt import docopt
import os


def _run(arg_list):
    les_file = arg_list['<file>']
    timer = arg_list['--timer']
    debug = arg_list['--debug']

    if not os.path.isfile(les_file):
        error(les_file + "is not a valid file")
        return

    code = open(les_file).read()
    lexer = Lexer(code, les_file)
    parser = Parser(lexer)
    t = parser.parse()
    symtab_builder = Preprocessor(parser.file_name)
    symtab_builder.check(t)

    generator = CodeGenerator(parser.file_name)
    generator.generate_code(t)
    generator.evaluate(not debug, debug, timer)


def _compile(arg_list):
    les_file = arg_list['<file>']
    o = arg_list['--output']
    emit_llvm = arg_list['--llvm']
    debug = arg_list['--debug']

    if not os.path.isfile(les_file):
        error(les_file + "is not a valid file")
        return

    les_file = os.path.abspath(les_file)
    code = open(les_file).read()
    lexer = Lexer(code, les_file)
    parser = Parser(lexer)
    t = parser.parse()
    symtab_builder = Preprocessor(parser.file_name)
    symtab_builder.check(t)

    generator = CodeGenerator(parser.file_name)
    generator.generate_code(t)
    generator.compile(les_file, not debug, o, emit_llvm)


if __name__ == "__main__":
    args = docopt(__doc__, version='0.1.0')

    if args['compile']:
        _compile(args)
    elif args['run']:
        _run(args)
    else:
        exit(__doc__)
