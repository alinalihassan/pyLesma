from lesma.compiler.types import *
from lesma.grammar import *

RET_VAR = 'ret_var'
NUM_TYPES = (ir.IntType, ir.DoubleType, ir.FloatType)
main_module = ir.Module()

type_map = {
	BOOL: ir.IntType(1),
	INT: ir.IntType(64),
	INT8: ir.IntType(8),
	INT32: ir.IntType(32),
	INT64: ir.IntType(64),
	INT128: ir.IntType(128),
	DEC: ir.DoubleType(),
	FLOAT: ir.FloatType(),
	FUNC: ir.FunctionType,
	VOID: ir.VoidType(),
}
type_map2 = {
	ANY: Any(),
	BOOL: Bool(),
	INT: Int(),
	INT8: Int8(),
	INT16: Int16(),
	INT32: Int32(),
	INT64: Int64(),
	INT128: Int128(),
	DEC: Dec(),
	FLOAT: Float(),
	COMPLEX: Complex(),
	BYTES: Bytes(),
	ARRAY: Array(),
	STR: Str(),
	LIST: List(),
	SET: Set(),
	DICT: Dict(),
	ENUM: Enum(),
	STRUCT: Struct(),
	FUNC: Func(),
	CLASS: Class(),
}
