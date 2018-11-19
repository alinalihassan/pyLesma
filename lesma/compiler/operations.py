from llvmlite import ir

from lesma.compiler import NUM_TYPES
from lesma.compiler import type_map
from lesma.grammar import *

I1 = 'i1'
I8 = 'i8'
I32 = 'i32'
I64 = 'i64'
I128 = 'i128'
DOUBLE = 'double'
FLOATINGPOINT = 'float'


def operations(compiler, node):
    op = node.op
    left = compiler.visit(node.left)
    right = compiler.visit(node.right)
    if op == CAST:
        return cast_ops(compiler, left, right, node)
    elif isinstance(left.type, ir.IntType) and isinstance(right.type, ir.IntType):
        return int_ops(compiler, op, left, right, node)
    elif type(left.type) in NUM_TYPES and type(right.type) in NUM_TYPES:
        return float_ops(compiler, op, left, right, node)
    elif isinstance(left, (ir.LoadInstr, ir.GEPInstr)) and isinstance(right, (ir.LoadInstr, ir.GEPInstr)):
        new_left = compiler.search_scopes(node.left.value)
        new_right = compiler.search_scopes(node.right.value)
        return str_ops(compiler, op, new_left, new_right, node)


def int_ops(compiler, op, left, right, node):
    # if left.type.width == 1:
    # 	left = compiler.builder.zext(left, type_map[INT])
    # if right.type.width == 1:
    # 	right = compiler.builder.zext(right, type_map[INT])
    if op == PLUS:
        return compiler.builder.add(left, right, 'addtmp')
    elif op == MINUS:
        return compiler.builder.sub(left, right, 'subtmp')
    elif op == MUL:
        return compiler.builder.mul(left, right, 'multmp')
    elif op == FLOORDIV:
        return compiler.builder.sdiv(left, right, 'divtmp')
    elif op == DIV:
        return compiler.builder.fdiv(compiler.builder.sitofp(left, type_map[DEC]),
            compiler.builder.sitofp(right, type_map[DEC]), 'fdivtmp')
    elif op == MOD:
        return compiler.builder.srem(left, right, 'modtmp')
    elif op == POWER:
        temp = compiler.builder.alloca(type_map[INT])
        compiler.builder.store(left, temp)
        for _ in range(node.right.value - 1):
            res = compiler.builder.mul(compiler.builder.load(temp), left)
            compiler.builder.store(res, temp)
        return compiler.builder.load(temp)
    elif op == AND:
        return compiler.builder.and_(left, right)
    elif op == OR:
        return compiler.builder.or_(left, right)
    elif op == XOR:
        return compiler.builder.xor(left, right)
    elif op == ARITHMATIC_LEFT_SHIFT or op == BINARY_LEFT_SHIFT:
        return compiler.builder.shl(left, right)
    elif op == ARITHMATIC_RIGHT_SHIFT:
        return compiler.builder.ashr(left, right)
    elif op == BINARY_LEFT_SHIFT:
        return compiler.builder.lshr(left, right)
    elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
        cmp = compiler.builder.icmp_signed(op, left, right, 'cmptmp')
        return compiler.builder.sitofp(cmp, type_map[BOOL], 'booltmp')
    else:
        raise SyntaxError('Unknown binary operator', node.op)


def float_ops(compiler, op, left, right, node):
    if op == PLUS:
        return compiler.builder.fadd(left, right, 'faddtmp')
    elif op == MINUS:
        return compiler.builder.fsub(left, right, 'fsubtmp')
    elif op == MUL:
        return compiler.builder.fmul(left, right, 'fmultmp')
    elif op == FLOORDIV:
        return compiler.builder.sdiv(compiler.builder.fptosi(left, ir.IntType(64)),
            compiler.builder.fptosi(right, ir.IntType(64)), 'ffloordivtmp')
    elif op == DIV:
        return compiler.builder.fdiv(left, right, 'fdivtmp')
    elif op == MOD:
        return compiler.builder.frem(left, right, 'fmodtmp')
    elif op == POWER:
        temp = compiler.builder.alloca(type_map[DEC])
        compiler.builder.store(left, temp)
        for _ in range(node.right.value - 1):
            res = compiler.builder.fmul(compiler.builder.load(temp), left)
            compiler.builder.store(res, temp)
        return compiler.builder.load(temp)
    elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
        cmp = compiler.builder.fcmp_ordered(op, left, right, 'cmptmp')
        return compiler.builder.sitofp(cmp, type_map[BOOL], 'booltmp')
    else:
        raise SyntaxError('Unknown binary operator', node.op)


def str_ops(compiler, op, left, right, node):
    # TODO add strings together!
    # left_len = str_get_len(left, compiler)
    # right_len = str_get_len(right, compiler)
    # n = left_len + right_len
    return


# def str_get_len(string, compiler):
# 	if isinstance(string, ir.AllocaInstr):
# 		str_gep = compiler.builder.gep(string, [compiler.const(1), compiler.const(1)])
# 		compiler.print_int(compiler.builder.ptrtoint(str_gep, type_map[INT]))
# 		return str_gep
# 	if isinstance(string, ir.GEPInstr):
# 		return string.pointer.type.pointee.count


def cast_ops(compiler, left, right, node):
    orig_type = str(left.type)
    cast_type = str(right)
    if cast_type == I64:
        if orig_type == DOUBLE:
            cast = compiler.builder.fptosi(left, type_map[INT])
            return cast
    elif cast_type == DOUBLE:
        if orig_type == I64:
            cast = compiler.builder.sitofp(left, type_map[DEC])
            return cast
    elif cast_type == FLOAT:
        raise NotImplementedError
    elif cast_type == COMPLEX:
        raise NotImplementedError
    elif cast_type == STR:
        raise NotImplementedError
    elif cast_type == BOOL:
        raise NotImplementedError
    elif cast_type == BYTES:
        raise NotImplementedError
    elif cast_type == LIST:
        raise NotImplementedError
    elif cast_type == DICT:
        raise NotImplementedError
    elif cast_type == ENUM:
        raise NotImplementedError
    elif cast_type in (ANY, FUNC):
        raise TypeError('file={} line={}: Cannot cast to type {}'.format(
            compiler.file_name,
            node.line_num,
            cast_type
        ))
    else:
        raise TypeError('file={} line={}: Unknown cast type {}'.format(
            compiler.file_name,
            node.line_num,
            cast_type
        ))
