from decimal import Decimal
from enum import Enum
from lesma.ast import Type
from lesma.compiler import *


class Symbol(object):
    def __init__(self, name, symbol_type=None):
        self.name = name
        self.type = symbol_type


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name, llvm_type=None, return_type=None):
        super().__init__(name)
        self.llvm_type = llvm_type
        self.return_type = return_type

    def type(self):
        return self.llvm_type.type()

    def __str__(self):
        return self.name

    __repr__ = __str__


ANY_BUILTIN = BuiltinTypeSymbol(ANY)
INT_BUILTIN = BuiltinTypeSymbol(INT, Int)
INT8_BUILTIN = BuiltinTypeSymbol(INT8, Int8)
INT16_BUILTIN = BuiltinTypeSymbol(INT16, Int16)
INT32_BUILTIN = BuiltinTypeSymbol(INT32, Int32)
INT64_BUILTIN = BuiltinTypeSymbol(INT64, Int64)
INT128_BUILTIN = BuiltinTypeSymbol(INT128, Int128)
DEC_BUILTIN = BuiltinTypeSymbol(DEC, Dec)
FLOAT_BUILTIN = BuiltinTypeSymbol(FLOAT, Float)
COMPLEX_BUILTIN = BuiltinTypeSymbol(COMPLEX, Complex)
BOOL_BUILTIN = BuiltinTypeSymbol(BOOL, Bool)
BYTES_BUILTIN = BuiltinTypeSymbol(BYTES, Bytes)
STR_BUILTIN = BuiltinTypeSymbol(STR, Str)
STRUCT_BUILTIN = BuiltinTypeSymbol(STRUCT, Str)
ARRAY_BUILTIN = BuiltinTypeSymbol(ARRAY, Array)
LIST_BUILTIN = BuiltinTypeSymbol(LIST, List)
DICT_BUILTIN = BuiltinTypeSymbol(DICT, Dict)
ENUM_BUILTIN = BuiltinTypeSymbol(ENUM, Enum)
FUNC_BUILTIN = BuiltinTypeSymbol(FUNC, Func)
CLASS_BUILTIN = BuiltinTypeSymbol(CLASS, Class)


class VarSymbol(Symbol):
    def __init__(self, name, var_type, read_only=False):
        super().__init__(name, var_type)
        self.accessed = False
        self.val_assigned = False
        self.read_only = read_only

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__


class StructSymbol(Symbol):
    def __init__(self, name, fields):
        super().__init__(name)
        self.fields = fields
        self.accessed = False
        self.val_assigned = False


class CollectionSymbol(Symbol):
    def __init__(self, name, var_type, item_types):
        super().__init__(name, var_type)
        self.item_types = item_types
        self.accessed = False
        self.val_assigned = False


class FuncSymbol(Symbol):
    def __init__(self, name, return_type, parameters, body, parameter_defaults=None):
        super().__init__(name, return_type)
        self.parameters = parameters
        self.parameter_defaults = parameter_defaults or {}
        self.body = body
        self.accessed = False
        self.val_assigned = True

    def __str__(self):
        return '<{name}:{type} ({params})>'.format(name=self.name, type=self.type, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

    __repr__ = __str__


class AliasSymbol(Symbol):
    def __init__(self, name, types):
        super().__init__(name, types)
        self.accessed = False

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__


class BuiltinFuncSymbol(Symbol):
    def __init__(self, name, return_type, parameters, body):
        super().__init__(name, return_type)
        self.parameters = parameters
        self.body = body
        self.accessed = False
        self.val_assigned = True

    def __str__(self):
        return '<{name}:{type} ({params})>'.format(name=self.name, type=self.type, params=', '.join('{}:{}'.format(key, value.value) for key, value in self.parameters.items()))

    __repr__ = __str__


class NodeVisitor(object):
    def __init__(self):
        self._scope = [{}]
        self._init_builtins()

    def _init_builtins(self):
        self.define(ANY, ANY_BUILTIN)
        self.define(INT, INT_BUILTIN)
        self.define(INT8, INT8_BUILTIN)
        self.define(INT16, INT16_BUILTIN)
        self.define(INT32, INT32_BUILTIN)
        self.define(INT64, INT64_BUILTIN)
        self.define(INT128, INT128_BUILTIN)
        self.define(DEC, DEC_BUILTIN)
        self.define(FLOAT, FLOAT_BUILTIN)
        self.define(COMPLEX, COMPLEX_BUILTIN)
        self.define(BOOL, BOOL_BUILTIN)
        self.define(BYTES, BYTES_BUILTIN)
        self.define(STR, STR_BUILTIN)
        self.define(STRUCT, STRUCT_BUILTIN)
        self.define(ARRAY, ARRAY_BUILTIN)
        self.define(LIST, LIST_BUILTIN)
        self.define(DICT, DICT_BUILTIN)
        self.define(ENUM, ENUM_BUILTIN)
        self.define(FUNC, FUNC_BUILTIN)
        self.define(CLASS, CLASS_BUILTIN)

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__.lower()
        # print("Visited: ", method_name) # DEBUG
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    @staticmethod
    def generic_visit(node):
        raise Exception('No visit_{} method'.format(type(node).__name__.lower()))

    @property
    def top_scope(self):
        return self._scope[-1] if len(self._scope) >= 1 else None

    @property
    def second_scope(self):
        return self._scope[-2] if len(self._scope) >= 2 else None

    def search_scopes(self, name, level=None):
        if level:
            if name in self._scope[level]:
                return self._scope[level][name]
        else:
            for scope in reversed(self._scope):
                if name in scope:
                    return scope[name]

    def define(self, key, value, level=0):
        level = (len(self._scope) - level) - 1
        self._scope[level][key] = value

    def new_scope(self):
        self._scope.append({})

    def drop_top_scope(self):
        self._scope.pop()

    @property
    def symbols(self):
        return [value for scope in self._scope for value in scope.values()]

    @property
    def keys(self):
        return [key for scope in self._scope for key in scope.keys()]

    @property
    def items(self):
        return [(key, value) for scope in self._scope for key, value in scope.items()]

    @property
    def unvisited_symbols(self):
        return [sym_name for sym_name, sym_val in self.items if
            not isinstance(sym_val, (BuiltinTypeSymbol, BuiltinFuncSymbol)) and not sym_val.accessed and sym_name != '_']

    def infer_type(self, value):
        if isinstance(value, BuiltinTypeSymbol):
            return value
        if isinstance(value, FuncSymbol):
            return self.search_scopes(FUNC)
        if isinstance(value, VarSymbol):
            return value.type
        if isinstance(value, Type):
            return self.search_scopes(value.value)
        if isinstance(value, int):
            return self.search_scopes(INT)
        if isinstance(value, Decimal):
            return self.search_scopes(DEC)
        if isinstance(value, float):
            return self.search_scopes(FLOAT)
        if isinstance(value, complex):
            return self.search_scopes(COMPLEX)
        if isinstance(value, str):
            return self.search_scopes(STR)
        if isinstance(value, bool):
            return self.search_scopes(BOOL)
        if isinstance(value, bytes):
            return self.search_scopes(BYTES)
        if isinstance(value, list):
            return self.search_scopes(LIST)
        if isinstance(value, dict):
            return self.search_scopes(DICT)
        if isinstance(value, Enum):
            return self.search_scopes(ENUM)
        if callable(value):
            return self.search_scopes(FUNC)
        raise TypeError('Type not recognized: {}'.format(value))
