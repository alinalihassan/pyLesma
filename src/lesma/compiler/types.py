from llvmlite import ir

import lesma.compiler.llvmlite_custom
from lesma.grammar import *


class Any:
    def __init__(self):
        self.name = ANY

    def __str__(self):
        return '<{}>'.format(self.name)

    __repr__ = __str__


class Number(Any):
    def __init__(self):
        super().__init__()
        self.name = None


class Bool(Number):
    def __init__(self):
        super().__init__()
        self.name = BOOL

    @staticmethod
    def type():
        return ir.IntType(1, signed=False)


class Int(Number):
    def __init__(self):
        super().__init__()
        self.name = INT

    @staticmethod
    def type():
        return ir.IntType(64)


class Int8(Number):
    def __init__(self):
        super().__init__()
        self.name = INT8

    @staticmethod
    def type():
        return ir.IntType(8)


class Int16(Number):
    def __init__(self):
        super().__init__()
        self.name = INT16

    @staticmethod
    def type():
        return ir.IntType(16)


class Int32(Number):
    def __init__(self):
        super().__init__()
        self.name = INT32

    @staticmethod
    def type():
        return ir.IntType(32)


class Int64(Number):
    def __init__(self):
        super().__init__()
        self.name = INT64

    @staticmethod
    def type():
        return ir.IntType(64)


class Int128(Number):
    def __init__(self):
        super().__init__()
        self.name = INT128

    @staticmethod
    def type():
        return ir.IntType(128)


class UInt(Number):
    def __init__(self):
        super().__init__()
        self.name = UINT

    @staticmethod
    def type():
        return ir.IntType(64, False)


class UInt8(Number):
    def __init__(self):
        super().__init__()
        self.name = UINT8

    @staticmethod
    def type():
        return ir.IntType(8, False)


class UInt16(Number):
    def __init__(self):
        super().__init__()
        self.name = UINT16

    @staticmethod
    def type():
        return ir.IntType(16, False)


class UInt32(Number):
    def __init__(self):
        super().__init__()
        self.name = UINT32

    @staticmethod
    def type():
        return ir.IntType(32, False)


class UInt64(Number):
    def __init__(self):
        super().__init__()
        self.name = UINT64

    @staticmethod
    def type():
        return ir.IntType(64, False)


class UInt128(Number):
    def __init__(self):
        super().__init__()
        self.name = UINT128

    @staticmethod
    def type():
        return ir.IntType(128, False)


class Double(Number):
    def __init__(self):
        super().__init__()
        self.name = DOUBLE

    @staticmethod
    def type():
        return ir.DoubleType()


class Float(Number):
    def __init__(self):
        super().__init__()
        self.name = FLOAT

    @staticmethod
    def type():
        return ir.FloatType()


class Complex(Number):
    def __init__(self):
        super().__init__()
        self.name = COMPLEX

    @staticmethod
    def type():
        raise NotImplementedError


class Collection(Any):
    def __init__(self):
        super().__init__()
        self.name = None


class List(Collection):
    def __init__(self):
        super().__init__()
        self.name = LIST

    @staticmethod
    def type(element_type, count):
        return ir.ArrayType(element_type, count)


class Str(List):
    def __init__(self):
        super().__init__()
        self.name = STR


class Tuple(Collection):
    def __init__(self):
        super().__init__()
        self.name = TUPLE

    @staticmethod
    def type():
        raise NotImplementedError


class Set(Collection):
    def __init__(self):
        super().__init__()
        self.name = SET

    @staticmethod
    def type():
        raise NotImplementedError


class Dict(Collection):
    def __init__(self):
        super().__init__()
        self.name = DICT

    @staticmethod
    def type():
        raise NotImplementedError


class Enum(Collection):
    def __init__(self):
        super().__init__()
        self.name = ENUM

    @staticmethod
    def type():
        raise NotImplementedError


class Struct(Collection):
    def __init__(self):
        super().__init__()
        self.name = STRUCT

    @staticmethod
    def type():
        raise NotImplementedError


class Func(Any):
    def __init__(self):
        super().__init__()
        self.name = FUNC

    @staticmethod
    def type():
        return ir.FunctionType


class Class(Struct):
    def __init__(self):
        super().__init__()
        self.name = CLASS

    @staticmethod
    def type():
        raise NotImplementedError
