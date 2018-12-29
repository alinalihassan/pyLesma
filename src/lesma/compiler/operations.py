from llvmlite import ir

from lesma.compiler import NUM_TYPES
from lesma.compiler import type_map, llvm_type_map
from lesma.grammar import *
import lesma.compiler.llvmlite_custom

# TODO: Determine size using a comparison function
int_types = ('i1', 'i8', 'i16', 'i32', 'i64', 'i128')
float_types = ('float', 'double')

false = ir.Constant(type_map[BOOL], 0)
true = ir.Constant(type_map[BOOL], 1)


def hasFunction(compiler, func_name):
    for func in compiler.module.functions:
        if func.name == func_name:
            return True

def userdef_unary_str(op, expr):
    return 'operator' + '.' + op + '.' + str(expr.type)


# Hacky way of checking if it's an expression or type
def userdef_binary_str(op, left, right):
    try:
        return 'operator' + '.' + op + '.' + str(left.type) + '.' + str(right.type)
    except Exception:
        return 'operator' + '.' + op + '.' + str(left.type) + '.' + str(right)


def unary_op(compiler, node):
    op = node.op
    expr = compiler.visit(node.expr)
    if hasFunction(compiler, userdef_unary_str(op, expr)):
        return compiler.builder.call(compiler.module.get_global(userdef_unary_str(op, expr)),
                                     [expr], "unop")
    elif op == MINUS:
        if isinstance(expr.type, ir.IntType):
            return compiler.builder.neg(expr)
        elif isinstance(expr.type, (ir.FloatType, ir.DoubleType)):
            return compiler.builder.fsub(ir.Constant(ir.DoubleType(), 0), expr)
    elif op == NOT:
        if isinstance(expr.type, ir.IntType) and str(expr.type).split("i")[1] == '1':
            return compiler.builder.not_(expr)
    elif op == BINARY_ONES_COMPLIMENT:
        if isinstance(expr.type, ir.IntType):
            return compiler.builder.not_(expr)


def binary_op(compiler, node):
    op = node.op
    left = compiler.visit(node.left)
    right = compiler.visit(node.right)
    if hasFunction(compiler, userdef_binary_str(op, left, right)):
        return compiler.builder.call(compiler.module.get_global(userdef_binary_str(op, left, right)),
                                     (left, right), "binop")
    elif op == CAST:
        return cast_ops(compiler, left, right, node)
    elif op in (IS, IS_NOT):
        return is_ops(compiler, op, left, right, node)
    elif isinstance(left.type, ir.IntType) and isinstance(right.type, ir.IntType):
        return int_ops(compiler, op, left, right, node)
    elif type(left.type) in NUM_TYPES and type(right.type) in NUM_TYPES:
        return float_ops(compiler, op, left, right, node)


def is_ops(compiler, op, left, right, node):
    orig = str(left.type)
    compare = str(right)
    if op == IS:
        return compiler.const(orig == compare, BOOL)
    elif op == IS_NOT:
        return compiler.const(orig != compare, BOOL)
    else:
        raise SyntaxError('Unknown identity operator', node.op)


def int_ops(compiler, op, left, right, node):
    # Cast values if they're different but compatible
    if str(left.type) in int_types and \
       str(right.type) in int_types and \
       str(left.type) != str(right.type):
        width_left = int(str(left.type).split("i")[1])
        width_right = int(str(right.type).split("i")[1])
        if width_left > width_right:
            right = cast_ops(compiler, right, left.type, node)
        else:
            left = cast_ops(compiler, left, right.type, node)

    if op == PLUS:
        return compiler.builder.add(left, right, 'addtmp')
    elif op == MINUS:
        return compiler.builder.sub(left, right, 'subtmp')
    elif op == MUL:
        return compiler.builder.mul(left, right, 'multmp')
    elif op == FLOORDIV:
        if left.type.signed:
            return compiler.builder.sdiv(left, right, 'divtmp')
        else:
            return compiler.builder.udiv(left, right, 'divtmp')
    elif op == DIV:
        return (compiler.builder.fdiv(cast_ops(compiler, left, type_map[DOUBLE], node),
                                      cast_ops(compiler, right, type_map[DOUBLE], node), 'fdivtmp'))
    elif op == MOD:
        if left.type.signed:
            return compiler.builder.srem(left, right, 'modtmp')
        else:
            return compiler.builder.urem(left, right, 'modtmp')
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
    elif op == BINARY_RIGHT_SHIFT:
        return compiler.builder.lshr(left, right)
    elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
        if left.type.signed:
            cmp_res = compiler.builder.icmp_signed(op, left, right, 'cmptmp')
        else:
            cmp_res = compiler.builder.icmp_unsigned(op, left, right, 'cmptmp')
        return compiler.builder.uitofp(cmp_res, type_map[BOOL], 'booltmp')
    else:
        raise SyntaxError('Unknown binary operator', node.op)


def float_ops(compiler, op, left, right, node):
    # Cast values if they're different but compatible
    if str(left.type) in float_types and \
       str(right.type) in float_types and \
       str(left.type) != str(right.type):  # Do a more general approach for size comparisons
        width_left = 0 if str(left.type) == 'float' else 1
        width_right = 0 if str(right.type) == 'float' else 1
        if width_left > width_right:
            right = cast_ops(compiler, right, left.type, node)
        else:
            left = cast_ops(compiler, left, right.type, node)

    if op == PLUS:
        return compiler.builder.fadd(left, right, 'faddtmp')
    elif op == MINUS:
        return compiler.builder.fsub(left, right, 'fsubtmp')
    elif op == MUL:
        return compiler.builder.fmul(left, right, 'fmultmp')
    elif op == FLOORDIV:
        return (compiler.builder.sdiv(cast_ops(compiler, left, ir.IntType(64), node),
                                      cast_ops(compiler, right, ir.IntType(64), node), 'ffloordivtmp'))
    elif op == DIV:
        return compiler.builder.fdiv(left, right, 'fdivtmp')
    elif op == MOD:
        return compiler.builder.frem(left, right, 'fmodtmp')
    elif op == POWER:
        temp = compiler.builder.alloca(type_map[DOUBLE])
        compiler.builder.store(left, temp)
        for _ in range(node.right.value - 1):
            res = compiler.builder.fmul(compiler.builder.load(temp), left)
            compiler.builder.store(res, temp)
        return compiler.builder.load(temp)
    elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
        cmp_res = compiler.builder.fcmp_ordered(op, left, right, 'cmptmp')
        return compiler.builder.uitofp(cmp_res, type_map[BOOL], 'booltmp')
    else:
        raise SyntaxError('Unknown binary operator', node.op)


def cast_ops(compiler, left, right, node):
    orig_type = str(left.type)
    cast_type = str(right)

    if cast_type in int_types and \
       orig_type in int_types and \
       cast_type == orig_type:
        left.type.signed = right.signed
        return left

    elif orig_type == cast_type:  # cast to the same type
        return left

    elif cast_type in int_types:  # int
        if orig_type in float_types:  # from float
            if right.signed:
                return compiler.builder.fptosi(left, llvm_type_map[cast_type])
            else:
                return compiler.builder.fptoui(left, llvm_type_map[cast_type])
        elif orig_type in int_types:  # from signed int
            width_cast = int(cast_type.split("i")[1])
            width_orig = int(orig_type.split("i")[1])
            if width_cast > width_orig:
                if left.type.signed:
                    return compiler.builder.sext(left, llvm_type_map[cast_type])
                else:
                    return compiler.builder.zext(left, llvm_type_map[cast_type])
            elif width_orig > width_cast:
                return compiler.builder.trunc(left, llvm_type_map[cast_type])

    elif cast_type in float_types:  # float
        if orig_type in int_types:  # from signed int
            if left.type.signed:
                return compiler.builder.sitofp(left, type_map[cast_type])
            else:
                return compiler.builder.uitofp(left, type_map[cast_type])
        elif orig_type in float_types:  # from float
            if cast_type == 'double' and orig_type == 'float':
                return compiler.builder.fpext(left, llvm_type_map[cast_type])
            elif cast_type == 'float' and orig_type == 'double':
                return compiler.builder.fptrunc(left, llvm_type_map[cast_type])

    elif cast_type == STR:
        raise NotImplementedError

    elif cast_type in (ANY, FUNC, ENUM, DICT, TUPLE):
        raise TypeError('file={} line={}: Cannot cast from {} to type {}'.format(
            compiler.file_name,
            node.line_num,
            orig_type,
            cast_type
        ))

    raise TypeError('file={} line={}: Unknown cast from {} to {}'.format(
        compiler.file_name,
        node.line_num,
        orig_type,
        cast_type
    ))
