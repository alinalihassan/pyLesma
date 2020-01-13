from llvmlite import ir

import lesma.compiler.llvmlite_custom
from lesma.compiler.base import NUM_TYPES, llvm_type_map, type_map
from lesma.grammar import *
from lesma.utils import error

# TODO: Determine size using a comparison function
int_types = ('i1', 'i8', 'i16', 'i32', 'i64', 'i128')
float_types = ('float', 'double')


def hasFunction(self, func_name):
    for func in self.module.functions:
        if func.name == func_name:
            return True

    return False


def userdef_unary_str(op, expr):
    # Check first if it's an built in type, then user defined type
    type_name = expr.type.name if hasattr(expr.type, 'name') else str(expr.type)
    return OPERATOR + '.' + op + '.' + type_name


def userdef_binary_str(op, left, right):
    # Check first if it's a type, then if it's an built in type, then user defined type
    ltype_name = str(left) if not hasattr(left, 'type') else (str(left.type) if not hasattr(left.type, 'name') else left.type.name)
    rtype_name = str(right) if not hasattr(right, 'type') else (str(right.type) if not hasattr(right.type, 'name') else right.type.name)
    return OPERATOR + '.' + op + '.' + ltype_name + '.' + rtype_name


def unary_op(self, node):
    op = node.op
    expr = self.visit(node.expr)
    if hasFunction(self, userdef_unary_str(op, expr)) and \
       self.current_function.name != userdef_unary_str(op, expr):
        return self.builder.call(self.module.get_global(userdef_unary_str(op, expr)),
                                 [expr], "unop")
    elif op == MINUS:
        if isinstance(expr.type, ir.IntType):
            return self.builder.neg(expr)
        elif isinstance(expr.type, (ir.FloatType, ir.DoubleType)):
            return self.builder.fsub(ir.Constant(ir.DoubleType(), 0), expr)
    elif op == NOT:
        if isinstance(expr.type, ir.IntType) and str(expr.type).split("i")[1] == '1':
            return self.builder.not_(expr)
    elif op == BINARY_ONES_COMPLIMENT:
        if isinstance(expr.type, ir.IntType):
            return self.builder.not_(expr)
    else:
        error('file={} line={}: Unknown operator {} for {}'.format(
            self.file_name,
            node.line_num,
            op,
            expr
        ))


def binary_op(self, node):
    op = node.op
    left = self.visit(node.left)
    right = self.visit(node.right)

    if hasFunction(self, userdef_binary_str(op, left, right)):
        return self.builder.call(self.module.get_global(userdef_binary_str(op, left, right)),
                                 (left, right), "binop")
    elif op == CAST:
        return cast_ops(self, left, right, node)
    elif op in (IS, IS_NOT):
        return is_ops(self, op, left, right, node)
    elif isinstance(left.type, ir.IntType) and isinstance(right.type, ir.IntType):
        return int_ops(self, op, left, right, node)
    elif type(left.type) in NUM_TYPES and type(right.type) in NUM_TYPES:
        if isinstance(left.type, ir.IntType):
            left = cast_ops(self, left, right.type, node)
        elif isinstance(right.type, ir.IntType):
            right = cast_ops(self, right, left.type, node)
        return float_ops(self, op, left, right, node)
    elif is_enum(left.type) and is_enum(right.type):
        return enum_ops(self, op, left, right, node)
    else:
        error('file={} line={}: Unknown operator {} for {} and {}'.format(
            self.file_name,
            node.line_num,
            op, node.left, node.right
        ))


def is_enum(typ):
    if typ.is_pointer:
        typ = typ.pointee
    return hasattr(typ, 'type') and typ.type == ENUM


def is_ops(self, op, left, right, node):
    orig = str(left.type)
    compare = str(right)
    if op == IS:
        return self.const(orig == compare, BOOL)
    elif op == IS_NOT:
        return self.const(orig != compare, BOOL)
    else:
        raise SyntaxError('Unknown identity operator', node.op)


def enum_ops(self, op, left, right, node):
    if left.type.is_pointer:
        left = self.builder.load(left)
    if right.type.is_pointer:
        right = self.builder.load(right)

    if op == EQUALS:
        left_val = self.builder.extract_value(left, 0)
        right_val = self.builder.extract_value(right, 0)
        return self.builder.icmp_unsigned(op, left_val, right_val, 'cmptmp')
    else:
        raise SyntaxError('Unknown binary operator', node.op)


def int_ops(self, op, left, right, node):
    # Cast values if they're different but compatible
    if str(left.type) in int_types and \
       str(right.type) in int_types and \
       str(left.type) != str(right.type):
        width_left = int(str(left.type).split("i")[1])
        width_right = int(str(right.type).split("i")[1])
        if width_left > width_right:
            right = cast_ops(self, right, left.type, node)
        else:
            left = cast_ops(self, left, right.type, node)

    if op == PLUS:
        return self.builder.add(left, right, 'addtmp')
    elif op == MINUS:
        return self.builder.sub(left, right, 'subtmp')
    elif op == MUL:
        return self.builder.mul(left, right, 'multmp')
    elif op == FLOORDIV:
        if left.type.signed:
            return self.builder.sdiv(left, right, 'divtmp')
        else:
            return self.builder.udiv(left, right, 'divtmp')
    elif op == DIV:
        return (self.builder.fdiv(cast_ops(self, left, type_map[DOUBLE], node),
                                  cast_ops(self, right, type_map[DOUBLE], node), 'fdivtmp'))
    elif op == MOD:
        if left.type.signed:
            return self.builder.srem(left, right, 'modtmp')
        else:
            return self.builder.urem(left, right, 'modtmp')
    elif op == POWER:
        temp = self.builder.alloca(type_map[INT])
        self.builder.store(left, temp)
        for _ in range(node.right.value - 1):
            res = self.builder.mul(self.builder.load(temp), left)
            self.builder.store(res, temp)
        return self.builder.load(temp)
    elif op == AND:
        return self.builder.and_(left, right)
    elif op == OR:
        return self.builder.or_(left, right)
    elif op == XOR:
        return self.builder.xor(left, right)
    elif op == ARITHMATIC_LEFT_SHIFT or op == BINARY_LEFT_SHIFT:
        return self.builder.shl(left, right)
    elif op == ARITHMATIC_RIGHT_SHIFT:
        return self.builder.ashr(left, right)
    elif op == BINARY_RIGHT_SHIFT:
        return self.builder.lshr(left, right)
    elif op in (EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
        if left.type.signed:
            cmp_res = self.builder.icmp_signed(op, left, right, 'cmptmp')
        else:
            cmp_res = self.builder.icmp_unsigned(op, left, right, 'cmptmp')
        return self.builder.uitofp(cmp_res, type_map[BOOL], 'booltmp')
    else:
        raise SyntaxError('Unknown binary operator', node.op)


def float_ops(self, op, left, right, node):
    # Cast values if they're different but compatible
    if str(left.type) in float_types and \
       str(right.type) in float_types and \
       str(left.type) != str(right.type):  # Do a more general approach for size comparisons
        width_left = 0 if str(left.type) == 'float' else 1
        width_right = 0 if str(right.type) == 'float' else 1
        if width_left > width_right:
            right = cast_ops(self, right, left.type, node)
        else:
            left = cast_ops(self, left, right.type, node)

    if op == PLUS:
        return self.builder.fadd(left, right, 'faddtmp')
    elif op == MINUS:
        return self.builder.fsub(left, right, 'fsubtmp')
    elif op == MUL:
        return self.builder.fmul(left, right, 'fmultmp')
    elif op == FLOORDIV:
        return (self.builder.sdiv(cast_ops(self, left, ir.IntType(64), node),
                                  cast_ops(self, right, ir.IntType(64), node), 'ffloordivtmp'))
    elif op == DIV:
        return self.builder.fdiv(left, right, 'fdivtmp')
    elif op == MOD:
        return self.builder.frem(left, right, 'fmodtmp')
    elif op == POWER:
        temp = self.builder.alloca(type_map[DOUBLE])
        self.builder.store(left, temp)
        for _ in range(node.right.value - 1):
            res = self.builder.fmul(self.builder.load(temp), left)
            self.builder.store(res, temp)
        return self.builder.load(temp)
    elif op in (NOT_EQUALS):
        cmp_res = self.builder.fcmp_unordered(op, left, right, 'cmptmp')
        return self.builder.uitofp(cmp_res, type_map[BOOL], 'booltmp')
    elif op in (EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL_TO, GREATER_THAN, GREATER_THAN_OR_EQUAL_TO):
        cmp_res = self.builder.fcmp_ordered(op, left, right, 'cmptmp')
        return self.builder.uitofp(cmp_res, type_map[BOOL], 'booltmp')
    else:
        raise SyntaxError('Unknown binary operator', node.op)


def cast_ops(self, left, right, node):
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
                return self.builder.fptosi(left, llvm_type_map[cast_type])
            else:
                return self.builder.fptoui(left, llvm_type_map[cast_type])
        elif orig_type in int_types:  # from signed int
            width_cast = int(cast_type.split("i")[1])
            width_orig = int(orig_type.split("i")[1])
            if width_cast > width_orig:
                if left.type.signed:
                    return self.builder.sext(left, llvm_type_map[cast_type])
                else:
                    return self.builder.zext(left, llvm_type_map[cast_type])
            elif width_orig > width_cast:
                return self.builder.trunc(left, llvm_type_map[cast_type])

    elif cast_type in float_types:  # float
        if orig_type in int_types:  # from signed int
            if left.type.signed:
                return self.builder.sitofp(left, type_map[cast_type])
            else:
                return self.builder.uitofp(left, type_map[cast_type])
        elif orig_type in float_types:  # from float
            if cast_type == 'double' and orig_type == 'float':
                return self.builder.fpext(left, llvm_type_map[cast_type])
            elif cast_type == 'float' and orig_type == 'double':
                return self.builder.fptrunc(left, llvm_type_map[cast_type])

    elif cast_type == str(type_map[STR]):
        raise NotImplementedError

    elif cast_type in (ANY, FUNC, STRUCT, CLASS, ENUM, DICT, LIST, TUPLE):
        raise TypeError('file={} line={}: Cannot cast from {} to type {}'.format(
            self.file_name,
            node.line_num,
            orig_type,
            cast_type
        ))

    raise TypeError('file={} line={}: Unknown cast from {} to {}'.format(
        self.file_name,
        node.line_num,
        orig_type,
        cast_type
    ))
