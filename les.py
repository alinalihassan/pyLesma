"""Lesma programming language

usage:
    lesma compile [-lo FILE] <file> 
    lesma run [-t] <file>
    lesma [-hv]

options:
    -h, --help                  shows the help
    -v, --version               shows the version
    -l, --llvm                  Emit llvm code
    -o FILE, --output FILE      Output file
    -t, --timer                 Time the execution
"""

from lesma.lexer import Lexer
from lesma.parser import Parser
from lesma.type_checker import Preprocessor
from lesma.compiler.code_generator import CodeGenerator
from lesma.utils import error
import os
from docopt import docopt

def _run(arg_list):
    les_file = arg_list['<file>']
    timer = arg_list['--timer']

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
    generator.evaluate(True, False, timer)


def _compile(arg_list):
    les_file = arg_list['<file>']
    o = arg_list['--output']
    emit_llvm = arg_list['--llvm']

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
    generator.compile(les_file, True, o, emit_llvm)


if __name__ == "__main__":
    args = docopt(__doc__, version='0.1.0')
    
    if args['compile']:
        _compile(args)
    elif args['run']:
        _run(args)
    else:
        exit(__doc__)
