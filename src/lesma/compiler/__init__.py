from lesma.compiler.types import *
from lesma.grammar import *
import lesma.compiler.llvmlite_custom

RET_VAR = 'ret_var'
NUM_TYPES = (ir.IntType, ir.DoubleType, ir.FloatType)
main_module = ir.Module()

type_map = {
    BOOL: ir.IntType(1, signed=False),
    INT: ir.IntType(64),
    INT8: ir.IntType(8),
    INT16: ir.IntType(16),
    INT32: ir.IntType(32),
    INT64: ir.IntType(64),
    INT128: ir.IntType(128),
    UINT: ir.IntType(64, signed=False),
    UINT8: ir.IntType(8, signed=False),
    UINT16: ir.IntType(16, signed=False),
    UINT32: ir.IntType(32, signed=False),
    UINT64: ir.IntType(64, signed=False),
    UINT128: ir.IntType(128, signed=False),
    DOUBLE: ir.DoubleType(),
    FLOAT: ir.FloatType(),
    FUNC: ir.FunctionType,
    VOID: ir.VoidType(),
}

llvm_to_lesma_type = {
    "u1": BOOL,
    "u8": UINT8,
    "u16": UINT16,
    "u32": UINT32,
    "u64": UINT64,
    "u128": UINT128,
    "i8": INT8,
    "i16": INT16,
    "i32": INT32,
    "i64": INT,
    "i128": INT128,
    "double": DOUBLE,
    "float": FLOAT,
}

llvm_type_map = {
    "u1": ir.IntType(1, signed=False),
    "u8": ir.IntType(8, signed=False),
    "u16": ir.IntType(16, signed=False),
    "u32": ir.IntType(32, signed=False),
    "u64": ir.IntType(64, signed=False),
    "u128": ir.IntType(128, signed=False),
    "i1": ir.IntType(1),
    "i8": ir.IntType(8),
    "i16": ir.IntType(16),
    "i32": ir.IntType(32),
    "i64": ir.IntType(64),
    "i128": ir.IntType(128),
    "double": ir.DoubleType(),
    "float": ir.FloatType(),
}

type_map2 = {
    ANY: Any(),
    BOOL: Bool(),
    UINT: UInt(),
    UINT8: UInt8(),
    UINT16: UInt16(),
    UINT32: UInt32(),
    UINT64: UInt64(),
    UINT128: UInt128(),
    INT: Int(),
    INT8: Int8(),
    INT16: Int16(),
    INT32: Int32(),
    INT64: Int64(),
    INT128: Int128(),
    DOUBLE: Double(),
    FLOAT: Float(),
    COMPLEX: Complex(),
    LIST: List(),
    STR: Str(),
    TUPLE: Tuple(),
    SET: Set(),
    DICT: Dict(),
    ENUM: Enum(),
    STRUCT: Struct(),
    FUNC: Func(),
    CLASS: Class(),
}
