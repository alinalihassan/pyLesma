from decimal import Decimal
from lesma.grammar import *


class Token(object):
    def __init__(self, token_type, value, line_num, indent_level, value_type=None):
        self.type = token_type
        self.value = value
        self.value_type = value_type
        self.line_num = line_num
        self.indent_level = indent_level

    def __str__(self):
        return 'Token(type={type}, value={value}, line_num={line_num}, indent_level={indent_level})'.format(
            type=self.type,
            value=repr(self.value),
            line_num=self.line_num,
            indent_level=self.indent_level
        )

    __repr__ = __str__


class Lexer(object):
    def __init__(self, text, file_name=None):
        self.text = text
        self.file_name = file_name
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.char_type = None
        self.word = ''
        self.word_type = None
        self._line_num = 1
        self._indent_level = 0
        self.current_token = None

    def next_char(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
            self.char_type = None
        else:
            self.current_char = self.text[self.pos]
            self.char_type = self.get_type(self.current_char)

    def reset_word(self):
        old_word = self.word
        self.word = ''
        self.word_type = None
        return old_word

    def peek(self, num):
        peek_pos = self.pos + num
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def preview_token(self, num=1):
        if num < 1:
            raise ValueError('num argument must be 1 or greater')
        next_token = None
        current_pos = self.pos
        current_char = self.current_char
        current_char_type = self.char_type
        current_word = self.word
        current_word_type = self.word_type
        current_line_num = self.line_num
        current_indent_level = self.indent_level
        for _ in range(num):
            next_token = self.get_next_token()
        self.pos = current_pos
        self.current_char = current_char
        self.char_type = current_char_type
        self.word = current_word
        self.word_type = current_word_type
        self._line_num = current_line_num
        self._indent_level = current_indent_level
        return next_token

    def skip_whitespace(self):
        if self.peek(-1) == '\n':
            raise SyntaxError('Only tab characters can indent')
        while self.current_char is not None and self.current_char.isspace():
            self.next_char()
            self.reset_word()

    def skip_comment(self):
        while self.current_char != '\n':
            self.next_char()
            if self.current_char is None:
                return self.eof()
        self.eat_newline()
        if self.current_char == '#':
            self.skip_comment()

    def increment_line_num(self):
        self._line_num += 1

    @property
    def line_num(self):
        return self._line_num

    @property
    def indent_level(self):
        return self._indent_level

    def reset_indent_level(self):
        self._indent_level = 0
        return self._indent_level

    def decriment_indent_level(self):
        self._indent_level -= 1
        return self._indent_level

    def increment_indent_level(self):
        self._indent_level += 1
        return self._indent_level

    def eat_newline(self):
        self.reset_word()
        token = Token(NEWLINE, '\n', self.line_num, self.indent_level)
        self.reset_indent_level()
        self.increment_line_num()
        self.next_char()
        return token

    def skip_indent(self):
        while self.current_char is not None and self.current_char == '\t':
            self.reset_word()
            self.increment_indent_level()
            self.next_char()

    def eof(self):
        return Token(EOF, EOF, self.line_num, self.indent_level)

    @staticmethod
    def get_type(char):
        if char.isspace():
            return WHITESPACE
        if char == '#':
            return COMMENT
        if char == '\\':
            return ESCAPE
        if char in OPERATORS:
            return OPERATIC
        if char.isdigit():
            return NUMERIC
        else:
            return ALPHANUMERIC

    def get_next_token(self):
        if self.current_char is None:
            return self.eof()

        if self.current_char == '\n':
            return self.eat_newline()

        elif self.current_char == '\t':
            self.skip_indent()

        if self.current_char.isspace():
            self.skip_whitespace()

        if self.current_char == '#':
            self.skip_comment()
            return self.get_next_token()

        if self.current_char == '"':
            self.next_char()
            while self.current_char != '"':
                if self.current_char == '\\' and self.peek(1) == '"':
                    self.next_char()
                self.word += self.current_char
                self.next_char()
            self.next_char()
            return Token(STRING, self.reset_word(), self.line_num, self.indent_level)

        if self.current_char == "'":
            self.next_char()
            while self.current_char != "'":
                if self.current_char == '\\' and self.peek(1) == "'":
                    self.next_char()
                self.word += self.current_char
                self.next_char()
            self.next_char()
            return Token(STRING, self.reset_word(), self.line_num, self.indent_level)

        if not self.char_type:
            self.char_type = self.get_type(self.current_char)
        if not self.word_type:
            self.word_type = self.char_type

        if self.word_type == OPERATIC:
            while self.char_type == OPERATIC:
                self.word += self.current_char
                self.next_char()
                if self.current_char in SINGLE_OPERATORS or self.word in SINGLE_OPERATORS:
                    break
            return Token(OP, self.reset_word(), self.line_num, self.indent_level)

        if self.word_type == ALPHANUMERIC:
            while self.char_type == ALPHANUMERIC or self.char_type == NUMERIC:
                self.word += self.current_char
                self.next_char()

            if self.word in OPERATORS:
                if self.word in MULTI_WORD_OPERATORS and self.preview_token(1).value in MULTI_WORD_OPERATORS:
                    self.next_char()
                    self.word += ' '
                    while self.char_type == ALPHANUMERIC or self.char_type == NUMERIC:
                        self.word += self.current_char
                        self.next_char()
                    return Token(OP, self.reset_word(), self.line_num, self.indent_level)
                else:
                    return Token(OP, self.reset_word(), self.line_num, self.indent_level)

            if self.word in KEYWORDS:
                if self.word in MULTI_WORD_KEYWORDS and self.preview_token(1).value in MULTI_WORD_KEYWORDS:
                    self.next_char()
                    self.word += ' '
                    while self.char_type == ALPHANUMERIC or self.char_type == NUMERIC:
                        self.word += self.current_char
                        self.next_char()
                    return Token(KEYWORD, self.reset_word(), self.line_num, self.indent_level)
                else:
                    return Token(KEYWORD, self.reset_word(), self.line_num, self.indent_level)
            elif self.word in TYPES:
                return Token(TYPE, self.reset_word(), self.line_num, self.indent_level)
            elif self.word in CONSTANTS:
                return Token(CONSTANT, self.reset_word(), self.line_num, self.indent_level)
            else:
                return Token(NAME, self.reset_word(), self.line_num, self.indent_level)

        if self.word_type == NUMERIC:
            while self.char_type == NUMERIC or self.current_char == DOT and self.peek(1) != DOT:
                self.word += self.current_char
                self.next_char()
                if self.char_type == ALPHANUMERIC:
                    raise SyntaxError('Variables cannot start with numbers')
            value = self.reset_word()
            if '.' in value:
                value = Decimal(value)
                value_type = DEC
            else:
                value = int(value)
                value_type = INT
            return Token(NUMBER, value, self.line_num, self.indent_level, value_type=value_type)

        if self.char_type == ESCAPE:
            self.reset_word()
            self.next_char()
            line_num = self.line_num
            if self.current_char == '\n':
                self.increment_line_num()
            self.next_char()
            return Token(ESCAPE, '\\', line_num, self.indent_level)

        raise SyntaxError('Unknown character')

    def analyze(self):
        token = self.get_next_token()
        while token.type != EOF:
            yield token
            token = self.get_next_token()
        yield token


# if __name__ == '__main__':
file = 'test.les'
lexer = Lexer(open(file).read(), file)
for t in lexer.analyze():
    print(t)

