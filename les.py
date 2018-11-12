from lesma.lexer import Lexer
from lesma.parser import Parser
from lesma.type_checker import Preprocessor
from lesma.compiler.code_generator import CodeGenerator


file = 'test.les'
code = open(file).read()
lexer = Lexer(code, file)
parser = Parser(lexer)
t = parser.parse()
symtab_builder = Preprocessor(parser.file_name)
symtab_builder.check(t)
if not symtab_builder.warnings:
    generator = CodeGenerator(parser.file_name)
    generator.generate_code(t)
    # generator.evaluate(False, True, False)
    generator.compile(file[:-4], False, True)
else:
    print('Did not run')
