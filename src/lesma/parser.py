from collections import OrderedDict
from typing import Optional

from lesma.ast import *
from lesma.compiler.base import type_map
from lesma.grammar import *
from lesma.utils import error
from lesma.lexer import Lexer, Token


class Parser(object):
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.file_name = lexer.file_name
        self.current_token: Optional[Token] = None
        self.indent_level = 0
        self.next_token()
        self.user_types = []
        self.func_args = False

    @property
    def line_num(self) -> int:
        return self.current_token.line_num

    def next_token(self):
        token = self.current_token
        self.current_token = self.lexer.get_next_token()
        return token

    def eat_type(self, *token_type):
        if self.current_token.type in token_type:
            self.next_token()
        else:
            error('file={} line={} Syntax Error: expected {}'.format(self.file_name, self.line_num, ", ".join(token_type)))

    def eat_value(self, *token_value):
        if self.current_token.value in token_value:
            self.next_token()
        else:
            error('file={} line={} Syntax Error: expected {}'.format(self.file_name, self.line_num, ", ".join(token_value)))

    def preview(self, num=1):
        return self.lexer.preview_token(num)

    def find_until(self, to_find, until):
        num = 0
        x = None
        while x != until:
            num += 1
            x = self.lexer.preview_token(num).value
            if x == to_find:
                return True
            elif x == EOF:
                error('file={} line={} Syntax Error: expected {}'.format(self.file_name, self.line_num, to_find))

        return False

    def keep_indent(self):
        while self.current_token.type == NEWLINE:
            self.eat_type(NEWLINE)
        return self.current_token.indent_level == self.indent_level

    def program(self):
        root = Compound()
        while self.current_token.type != EOF:
            comp = self.compound_statement()
            root.children.extend(comp.children)
        return Program(root)

    def enum_declaration(self):
        self.eat_value(ENUM)
        name = self.next_token()
        self.user_types.append(name.value)
        self.eat_type(NEWLINE)
        self.indent_level += 1
        fields = []
        while self.current_token.indent_level > name.indent_level:
            field = self.next_token().value
            fields.append(field)

            self.eat_type(NEWLINE)

        self.indent_level -= 1
        return EnumDeclaration(name.value, fields, self.line_num)

    def class_declaration(self):
        base = None
        methods = []
        fields = OrderedDict()
        defaults = {}
        instance_fields = None
        self.next_token()
        class_name = self.current_token
        self.user_types.append(class_name.value)
        self.eat_type(NAME)
        if self.current_token.value == COLON:
            self.eat_value(COLON)
            base = self.type_spec()
        self.eat_type(NEWLINE)
        self.indent_level += 1
        while self.keep_indent():
            if self.current_token.type == NEWLINE:
                self.eat_type(NEWLINE)
                continue
            if self.current_token.type == NAME and self.preview().value == COLON:
                field = self.current_token.value
                self.eat_type(NAME)
                self.eat_value(COLON)
                field_type = self.type_spec()
                fields[field] = field_type
                if self.current_token.value == ASSIGN:
                    self.eat_value(ASSIGN)
                    defaults[field] = self.expr()

                self.eat_type(NEWLINE)
            if self.current_token.value == DEF:
                methods.append(self.method_declaration(class_name))
        self.indent_level -= 1
        return ClassDeclaration(class_name.value, base, methods, fields, defaults, instance_fields)

    def variable_declaration(self):
        var_node = Var(self.current_token.value, self.line_num)
        self.eat_type(NAME)
        self.eat_value(COLON)
        type_node = self.type_spec()
        var = VarDecl(var_node, type_node, self.line_num)
        if self.current_token.value == ASSIGN:
            var = self.variable_declaration_assignment(var)
        return var

    def variable_declaration_assignment(self, declaration):
        return Assign(declaration, self.next_token().value, self.expr(), self.line_num)

    def type_declaration(self):
        self.eat_value(TYPE)
        name = self.next_token()
        self.user_types.append(name.value)
        self.eat_value(ASSIGN)
        return TypeDeclaration(name.value, self.type_spec(), self.line_num)

    def function_declaration(self):
        op_func = False
        extern_func = False
        self.eat_value(DEF)
        if self.current_token.value == LPAREN:
            name = ANON
        elif self.current_token.value == OPERATOR:
            self.eat_value(OPERATOR)
            op_func = True
            name = self.next_token()
        elif self.current_token.value == EXTERN:
            self.eat_value(EXTERN)
            extern_func = True
            name = self.next_token()
        else:
            name = self.next_token()
        self.eat_value(LPAREN)
        params = OrderedDict()
        param_defaults = {}
        vararg = None
        while self.current_token.value != RPAREN:
            param_name = self.current_token.value
            self.eat_type(NAME)
            if self.current_token.value == COLON:
                self.eat_value(COLON)
                param_type = self.type_spec()
            else:
                param_type = self.variable(self.current_token)

            params[param_name] = param_type
            if self.current_token.value != RPAREN:
                if self.current_token.value == ASSIGN:
                    if extern_func:
                        error("Extern functions cannot have defaults")
                    self.eat_value(ASSIGN)
                    param_defaults[param_name] = self.expr()
                if self.current_token.value == ELLIPSIS:
                    key, value = params.popitem()
                    if not vararg:
                        vararg = []
                    vararg.append(key)
                    vararg.append(value)
                    self.eat_value(ELLIPSIS)
                    break
                if self.current_token.value != RPAREN:
                    self.eat_value(COMMA)
        self.eat_value(RPAREN)

        if self.current_token.value != ARROW:
            return_type = Void()
        else:
            self.eat_value(ARROW)
            if self.current_token.value == VOID:
                return_type = Void()
                self.next_token()
            else:
                return_type = self.type_spec()

        if extern_func:
            return ExternFuncDecl(name.value, return_type, params, self.line_num, vararg)

        self.eat_type(NEWLINE)
        self.indent_level += 1
        stmts = self.compound_statement()
        self.indent_level -= 1
        if name == ANON:
            return AnonymousFunc(return_type, params, stmts, self.line_num, param_defaults, vararg)
        if op_func:
            if len(params) not in (1, 2):  # TODO: move this to type checker
                error("Operators can either be unary or binary, and the number of parameters do not match")

            name.value = OPERATOR + '.' + name.value
            for param in params:
                type_name = str(type_map[str(params[param].value)]) if str(params[param].value) in type_map else str(params[param].value)
                name.value += '.' + type_name

        return FuncDecl(name.value, return_type, params, stmts, self.line_num, param_defaults, vararg)

    def method_declaration(self, class_name):
        self.eat_value(DEF)
        name = self.next_token()
        self.eat_value(LPAREN)
        params = OrderedDict()
        param_defaults = {}
        vararg = None
        params[SELF] = class_name
        while self.current_token.value != RPAREN:
            param_name = self.current_token.value
            self.eat_type(NAME)
            if self.current_token.value == COLON:
                self.eat_value(COLON)
                param_type = self.type_spec()
            else:
                param_type = self.variable(self.current_token)

            params[param_name] = param_type
            if self.current_token.value != RPAREN:
                if self.current_token.value == ASSIGN:
                    self.eat_value(ASSIGN)
                    param_defaults[param_name] = self.expr()
                if self.current_token.value == ELLIPSIS:
                    key, value = params.popitem()
                    if not vararg:
                        vararg = []
                    vararg.append(key)
                    vararg.append(value)
                    self.eat_value(ELLIPSIS)
                    break
                if self.current_token.value != RPAREN:
                    self.eat_value(COMMA)
        self.eat_value(RPAREN)

        if self.current_token.value != ARROW:
            return_type = Void()
        else:
            self.eat_value(ARROW)
            if self.current_token.value == VOID:
                return_type = Void()
                self.next_token()
            else:
                return_type = self.type_spec()

        self.eat_type(NEWLINE)
        self.indent_level += 1
        stmts = self.compound_statement()
        self.indent_level -= 1

        return FuncDecl("{}.{}".format(class_name.value, name.value), return_type, params, stmts, self.line_num, param_defaults, vararg)

    def bracket_literal(self):
        token = self.next_token()
        if token.value == LCURLYBRACKET:
            return self.curly_bracket_expression(token)
        elif token.value == LPAREN:
            return self.tuple_expression(token)

        return self.square_bracket_expression(token)

    def function_call(self, token):
        if token.value == PRINT:
            self.func_args = True
            return Print(self.expr(), self.line_num)
        elif token.value == INPUT:
            self.func_args = True
            return Input(self.expr(), self.line_num)

        self.eat_value(LPAREN)
        args = []
        named_args = {}
        while self.current_token.value != RPAREN:
            while self.current_token.type == NEWLINE:
                self.eat_type(NEWLINE)
            if self.current_token.value in (LPAREN, LSQUAREBRACKET, LCURLYBRACKET):
                args.append(self.bracket_literal())
            elif self.preview().value == ASSIGN:
                name = self.expr().value
                self.eat_value(ASSIGN)
                named_args[name] = self.expr()
            else:
                args.append(self.expr())
            while self.current_token.type == NEWLINE:
                self.eat_type(NEWLINE)
            if self.current_token.value != RPAREN:
                self.eat_value(COMMA)
        func = FuncCall(token.value, args, self.line_num, named_args)
        self.next_token()
        return func

    def type_spec(self):
        token = self.current_token
        if token.value in self.user_types:
            self.eat_type(NAME)
            return Type(token.value, self.line_num)
        self.eat_type(LTYPE)
        type_spec = Type(token.value, self.line_num)
        func_ret_type = None
        func_params = OrderedDict()
        param_num = 0
        if self.current_token.value == LESS_THAN and token.value in (LIST, TUPLE):
            self.next_token()
            while self.current_token.value != GREATER_THAN:
                param_type = self.type_spec()
                func_params[str(param_num)] = param_type
                param_num += 1
                if self.current_token.value != GREATER_THAN:
                    self.eat_value(COMMA)

            self.eat_value(GREATER_THAN)
            type_spec.func_params = func_params

        elif self.current_token.value == LESS_THAN and token.value == FUNC:
            self.next_token()
            while self.current_token.value != GREATER_THAN:
                param_type = self.type_spec()
                func_params[str(param_num)] = param_type
                param_num += 1
                if self.current_token.value != GREATER_THAN:
                    self.eat_value(COMMA)

            self.eat_value(GREATER_THAN)
            if self.current_token.value == ARROW:
                self.next_token()
                func_ret_type = self.type_spec()
            else:
                func_ret_type = Type(VOID, self.line_num)

            type_spec.func_params = func_params
            type_spec.func_ret_type = func_ret_type

        return type_spec

    def compound_statement(self):
        nodes = self.statement_list()
        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        node = self.statement()
        if self.current_token.type == NEWLINE:
            self.next_token()
        if isinstance(node, Return):
            return [node]
        results = [node]
        while self.keep_indent():
            results.append(self.statement())
            if self.current_token.type == NEWLINE:
                self.next_token()
            elif self.current_token.type == EOF:
                results = [x for x in results if x is not None]
                break
        return results

    def statement(self):
        if self.current_token.value == IF:
            node = self.if_statement()
        elif self.current_token.value == WHILE:
            node = self.while_statement()
        elif self.current_token.value == FOR:
            node = self.for_statement()
        elif self.current_token.value == FALLTHROUGH:
            self.next_token()
            node = Fallthrough(self.line_num)
        elif self.current_token.value == BREAK:
            self.next_token()
            node = Break(self.line_num)
        elif self.current_token.value == CONTINUE:
            self.next_token()
            node = Continue(self.line_num)
        elif self.current_token.value == PASS:
            self.next_token()
            node = Pass(self.line_num)
        elif self.current_token.value == CONST:
            node = self.assignment_statement(self.current_token)
        elif self.current_token.value == DEFER:
            self.next_token()
            node = Defer(self.line_num, self.statement())
        elif self.current_token.value == SWITCH:
            self.next_token()
            node = self.switch_statement()
        elif self.current_token.value == RETURN:
            node = self.return_statement()
        elif self.current_token.type == NAME:
            if self.preview().value == DOT:
                node = self.property_or_method(self.next_token())
            elif self.preview().value == COLON:
                node = self.variable_declaration()
            else:
                node = self.name_statement()
        elif self.current_token.value == DEF:
            node = self.function_declaration()
        elif self.current_token.value == TYPE:
            node = self.type_declaration()
        elif self.current_token.type == LTYPE:
            if self.current_token.value == CLASS:
                node = self.class_declaration()
            elif self.current_token.value == ENUM:
                node = self.enum_declaration()
        elif self.current_token.value == EOF:
            return
        else:
            self.next_token()
            node = self.statement()
        return node

    def square_bracket_expression(self, token):
        if token.value == LSQUAREBRACKET:
            items = []
            while self.current_token.value != RSQUAREBRACKET:
                items.append(self.expr())
                if self.current_token.value == COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(RSQUAREBRACKET)
            return Collection(LIST, self.line_num, False, *items)
        elif self.current_token.type == LTYPE:
            type_token = self.next_token()
            if self.current_token.value == COMMA:
                return self.dictionary_assignment(token)
            elif self.current_token.value == RSQUAREBRACKET:
                self.next_token()
                return self.collection_expression(token, type_token)
        elif self.current_token.type == NUMBER:
            tok = self.expr()
            if self.current_token.value == COMMA:
                return self.slice_expression(tok)
            else:
                self.eat_value(RSQUAREBRACKET)
                access = self.access_collection(token, tok)
                if self.current_token.value in ASSIGNMENT_OP:
                    op = self.current_token
                    if op.value in INCREMENTAL_ASSIGNMENT_OP:
                        return IncrementAssign(access, op.value, self.line_num)
                    else:
                        self.next_token()
                        right = self.expr()
                        if op.value == ASSIGN:
                            return Assign(access, op.value, right, self.line_num)

                        return OpAssign(access, op.value, right, self.line_num)
                return access
        elif token.type == NAME:
            self.eat_value(LSQUAREBRACKET)
            tok = self.expr()
            if self.current_token.value == COMMA:
                return self.slice_expression(tok)

            self.eat_value(RSQUAREBRACKET)
            return self.access_collection(token, tok)
        else:
            raise SyntaxError

    def slice_expression(self, token):
        pass

    def curly_bracket_expression(self, token):
        if token.value == LCURLYBRACKET:
            pairs = OrderedDict()
            while self.current_token.value != RCURLYBRACKET:
                key = self.expr()
                self.eat_value(ASSIGN)
                pairs[key.value] = self.expr()
                if self.current_token.value == COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(RCURLYBRACKET)
            return HashMap(pairs, self.line_num)
        else:
            raise SyntaxError('Wait... what?')

    def tuple_expression(self, token):
        if token.value == LPAREN:
            items = []
            while self.current_token.value != RPAREN:
                items.append(self.expr())
                if self.current_token.value == COMMA:
                    self.next_token()
                else:
                    break
            self.eat_value(RPAREN)
            return Collection(TUPLE, self.line_num, False, *items)

    def collection_expression(self, token, type_token):
        if self.current_token.value == ASSIGN:
            return self.array_of_type_assignment(token, type_token)
        else:
            raise NotImplementedError

    def access_collection(self, collection, key):
        return CollectionAccess(collection, key, self.line_num)

    def array_of_type_assignment(self, token, type_token):
        raise NotImplementedError

    def dot_access(self, token):
        self.eat_value(DOT)
        field = self.current_token.value
        self.next_token()
        return DotAccess(token.value, field, self.line_num)

    def name_statement(self):
        token = self.next_token()
        if self.current_token.value == LPAREN:
            node = self.function_call(token)
        elif self.current_token.value == LSQUAREBRACKET:
            self.next_token()
            node = self.square_bracket_expression(token)
        elif self.current_token.value in ASSIGNMENT_OP:
            node = self.assignment_statement(token)
        else:
            raise SyntaxError('Line {}'.format(self.line_num))
        return node

    def property_or_method(self, token):
        self.eat_value(DOT)
        field = self.current_token.value
        self.next_token()
        left = DotAccess(token.value, field, self.line_num)
        token = self.next_token()
        if token.value in ASSIGNMENT_OP:
            return self.field_assignment(token, left)

        return self.method_call(token, left)

    def method_call(self, _, left):
        args = []
        named_args = {}
        while self.current_token.value != RPAREN:
            while self.current_token.type == NEWLINE:
                self.eat_type(NEWLINE)
            if self.current_token.value in (LPAREN, LSQUAREBRACKET, LCURLYBRACKET):
                args.append(self.bracket_literal())
            elif self.preview().value == ASSIGN:
                name = self.expr().value
                self.eat_value(ASSIGN)
                named_args[name] = self.expr()
            else:
                args.append(self.expr())
            while self.current_token.type == NEWLINE:
                self.eat_type(NEWLINE)
            if self.current_token.value != RPAREN:
                self.eat_value(COMMA)
        method = MethodCall(left.obj, left.field, args, self.line_num, named_args)
        self.next_token()
        return method

    def field_assignment(self, token, left):
        if token.value == ASSIGN:
            right = self.expr()
            node = Assign(left, token.value, right, self.line_num)
        elif token.value in ARITHMETIC_ASSIGNMENT_OP:
            right = self.expr()
            node = OpAssign(left, token.value, right, self.line_num)
        elif token.value in INCREMENTAL_ASSIGNMENT_OP:
            node = IncrementAssign(left, token.value, self.line_num)
        else:
            raise SyntaxError('Unknown assignment operator: {}'.format(token.value))
        return node

    def dictionary_assignment(self, token):
        raise NotImplementedError

    def return_statement(self):
        self.next_token()
        return Return(self.expr(), self.line_num)

    def if_statement(self):
        self.indent_level += 1
        token = self.next_token()
        comp = If(token.value, [self.expr()], [self.compound_statement()], token.indent_level, self.line_num)
        if self.current_token.indent_level < comp.indent_level:
            self.indent_level -= 1
            return comp
        while self.current_token.value == ELSE_IF:
            self.next_token()
            comp.comps.append(self.expr())
            comp.blocks.append(self.compound_statement())
        if self.current_token.value == ELSE:
            self.next_token()
            comp.comps.append(Else())
            comp.blocks.append(self.compound_statement())
        self.indent_level -= 1
        return comp

    def while_statement(self):
        self.indent_level += 1
        token = self.next_token()
        comp = While(token.value, self.expr(), self.loop_block(), self.line_num)
        self.indent_level -= 1
        return comp

    def for_statement(self):
        self.indent_level += 1
        self.next_token()
        elements = []
        while self.current_token.value != IN:
            elements.append(self.expr())
            if self.current_token.value == COMMA:
                self.eat_value(COMMA)
        self.eat_value(IN)
        iterator = self.expr()
        if self.current_token.value == NEWLINE:
            self.eat_type(NEWLINE)
        block = self.loop_block()
        loop = For(iterator, block, elements, self.line_num)
        self.indent_level -= 1
        return loop

    def switch_statement(self):
        self.indent_level += 1
        value = self.expr()
        switch = Switch(value, [], self.line_num)
        if self.current_token.type == NEWLINE:
            self.next_token()
        while self.keep_indent():
            switch.cases.append(self.case_statement())
            if self.current_token.type == NEWLINE:
                self.next_token()
            elif self.current_token.type == EOF:
                return switch
        self.indent_level -= 1
        return switch

    def case_statement(self):
        self.indent_level += 1
        if self.current_token.value == CASE:
            self.next_token()
            value = self.expr()
        elif self.current_token.value == DEFAULT:
            self.next_token()
            value = DEFAULT
        else:
            raise SyntaxError
        block = self.compound_statement()
        self.indent_level -= 1
        return Case(value, block, self.line_num)

    def loop_block(self):
        nodes = self.statement_list()
        root = LoopBlock()
        for node in nodes:
            root.children.append(node)
        return root

    def assignment_statement(self, token):
        if token.value == CONST:
            read_only = True
            self.next_token()
            token = self.current_token
            self.next_token()
        else:
            read_only = False
        left = self.variable(token, read_only)
        token = self.next_token()
        if token.value == ASSIGN:
            right = self.expr()
            node = Assign(left, token.value, right, self.line_num)
        elif token.value in ARITHMETIC_ASSIGNMENT_OP:
            right = self.expr()
            node = OpAssign(left, token.value, right, self.line_num)
        elif token.value in INCREMENTAL_ASSIGNMENT_OP:
            node = IncrementAssign(left, token.value, self.line_num)
        elif token.value == COLON:
            type_node = self.type_spec()
            var = VarDecl(left, type_node, self.line_num)
            node = self.variable_declaration_assignment(var)
        else:
            raise SyntaxError('Unknown assignment operator: {}'.format(token.value))
        return node

    def typ(self, token):
        return Type(token.value, self.line_num)

    def variable(self, token, read_only=False):
        return Var(token.value, self.line_num, read_only)

    def constant(self, token):
        return Constant(token.value, self.line_num)

    def factor(self):
        token = self.current_token
        preview = self.preview()
        if preview.value == DOT:
            if self.preview(2).type == NAME and self.preview(3).value == LPAREN:
                return self.property_or_method(self.next_token())

            self.next_token()
            return self.dot_access(token)
        elif token.value in (PLUS, MINUS, BINARY_ONES_COMPLIMENT):
            self.next_token()
            return UnaryOp(token.value, self.factor(), self.line_num)
        elif token.value == NOT:
            self.next_token()
            return UnaryOp(token.value, self.expr(), self.line_num)
        elif token.type == NUMBER:
            self.next_token()
            return Num(token.value, token.value_type, self.line_num)
        elif token.type == STRING:
            self.next_token()
            return Str(token.value, self.line_num)
        elif token.value == DEF:
            return self.function_declaration()
        elif token.type == LTYPE:
            return self.type_spec()
        elif token.value == LPAREN:
            if self.func_args or not self.find_until(COMMA, RPAREN):
                self.func_args = False
                if preview.value == RPAREN:
                    return []

                self.next_token()
                node = self.expr()
                self.eat_value(RPAREN)
            else:
                token = self.next_token()
                node = self.tuple_expression(token)

            return node
        elif preview.value == LPAREN:
            self.next_token()
            return self.function_call(token)
        elif preview.value == LSQUAREBRACKET:
            self.next_token()
            return self.square_bracket_expression(token)
        elif token.value == LSQUAREBRACKET:
            self.next_token()
            return self.square_bracket_expression(token)
        elif token.value == LCURLYBRACKET:
            self.next_token()
            return self.curly_bracket_expression(token)
        elif token.type == NAME:
            self.next_token()
            if token.value in self.user_types:
                return self.typ(token)
            return self.variable(token)
        elif token.type == CONSTANT:
            self.next_token()
            return self.constant(token)
        else:
            raise SyntaxError

    def term(self):
        node = self.factor()
        ops = (MUL, DIV, FLOORDIV, MOD, POWER, CAST, RANGE) + COMPARISON_OP + LOGICAL_OP + BINARY_OP
        while self.current_token.value in ops:
            token = self.next_token()
            if token.value in COMPARISON_OP or token.value in LOGICAL_OP or token.value in BINARY_OP:
                node = BinOp(node, token.value, self.expr(), self.line_num)
            elif token.value == RANGE:
                node = Range(node, self.expr(), self.line_num)
            else:
                node = BinOp(node, token.value, self.factor(), self.line_num)
        return node

    def expr(self):
        node = self.term()
        while self.current_token.value in (PLUS, MINUS):
            token = self.next_token()
            node = BinOp(node, token.value, self.term(), self.line_num)
        return node

    def parse(self) -> Program:
        node = self.program()
        if self.current_token.type != EOF:
            raise SyntaxError('Unexpected end of program')
        return node
