from ctypes import CFUNCTYPE, c_void_p
from decimal import Decimal
from time import time
import llvmlite.binding as llvm
import os
import subprocess
from llvmlite import ir
from lesma.grammar import *
from lesma.ast import CollectionAccess, DotAccess, Input, VarDecl, Str
from lesma.compiler import RET_VAR, type_map
from lesma.compiler.operations import unary_op, binary_op, cast_ops
from lesma.compiler.builtins import define_builtins
from lesma.type_checker import types_compatible
import lesma.compiler.llvmlite_custom
from lesma.visitor import NodeVisitor
from lesma.utils import *


class CodeGenerator(NodeVisitor):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        self.module = ir.Module()
        self.builder = None
        self._add_builtins()
        func_ty = ir.FunctionType(ir.VoidType(), [type_map[INT32], type_map[INT8].as_pointer().as_pointer()])
        func = ir.Function(self.module, func_ty, 'main')
        entry_block = func.append_basic_block('entry')
        exit_block = func.append_basic_block('exit')
        self.current_function = func
        self.function_stack = [func]
        self.builder = ir.IRBuilder(entry_block)
        self.exit_blocks = [exit_block]
        self.block_stack = [entry_block]
        self.loop_test_blocks = []
        self.loop_end_blocks = []
        self.is_break = False
        self.in_class = False
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        self.anon_counter = 0

        # Add argv and argc to main
        for i in range(2):
            func.args[i].name = '.argc' if i == 0 else '.argv'
            self.alloc_define_store(func.args[i], func.args[i].name[1:], func.args[i].type)

    def __str__(self):
        return str(self.module)

    def visit_program(self, node):
        self.visit(node.block)
        self.branch(self.exit_blocks[0])
        self.position_at_end(self.exit_blocks[0])
        self.builder.ret_void()

    @staticmethod
    def visit_num(node):
        return ir.Constant(type_map[node.val_type], node.value)

    def visit_var(self, node):
        var = self.search_scopes(node.value)
        if isinstance(var, type_map[FUNC]):
            return var
        return self.load(node.value)

    def visit_binop(self, node):
        return binary_op(self, node)

    def visit_anonymousfunc(self, node):
        self.anon_counter += 1
        return self.funcdecl('anon_func.{}'.format(self.anon_counter), node)

    def visit_funcdecl(self, node):
        self.funcdecl(node.name, node)

    def visit_externfuncdecl(self, node):
        self.externfuncdecl(node.name, node)

    def externfuncdecl(self, name, node):
        return_type = node.return_type
        parameters = node.parameters
        varargs = node.varargs
        ret_type = type_map[return_type.value]
        args = [type_map[param.value] for param in parameters.values()]
        func_type = ir.FunctionType(ret_type, args, varargs)
        func_type.parameters = parameters
        if hasattr(return_type, 'func_ret_type') and return_type.func_ret_type:
            func_type.return_type = func_type.return_type(type_map[return_type.func_ret_type.value], [return_type.func_ret_type.value]).as_pointer()
        func = ir.Function(self.module, func_type, name)
        self.define(name, func, 1)

    def funcdecl(self, name, node):
        self.start_function(name, node.return_type, node.parameters, node.parameter_defaults, node.varargs)
        for i, arg in enumerate(self.current_function.args):
            arg.name = list(node.parameters.keys())[i]
            self.alloc_define_store(arg, arg.name, arg.type)
        if self.current_function.function_type.return_type != type_map[VOID]:
            self.alloc_and_define(RET_VAR, self.current_function.function_type.return_type)
        ret = self.visit(node.body)
        self.end_function(ret)

    def visit_return(self, node):
        val = self.visit(node.value)
        if val.type != ir.VoidType():
            val = self.comp_cast(val, self.search_scopes(RET_VAR).type.pointee, node)
            self.store(val, RET_VAR)
        self.branch(self.exit_blocks[-1])
        return True

    def visit_funccall(self, node):
        func_type = self.search_scopes(node.name)
        if isinstance(func_type, ir.Function):
            func_type = func_type.type.pointee
            name = self.search_scopes(node.name)
            name = name.name
        elif isinstance(func_type, ir.IdentifiedStructType):
            return self.struct_assign(node)
        else:
            name = node.name

        if len(node.arguments) < len(func_type.args):
            args = []
            args_supplied = []
            arg_names = []

            for i in func_type.parameters:
                arg_names.append(i)

            for x, arg in enumerate(func_type.args):
                if x < len(node.arguments):
                    args.append(self.visit(node.arguments[x]))
                else:
                    if node.named_arguments and arg_names[x] in node.named_arguments:
                        args.append(self.comp_cast(
                            self.visit(node.named_arguments[arg_names[x]]),
                            self.visit(func_type.parameters[arg_names[x]]),
                            node
                        ))
                    else:
                        if set(node.named_arguments.keys()) & set(args_supplied):
                            raise TypeError('got multiple values for argument(s) {}'.format(set(node.named_arguments.keys()) & set(args_supplied)))

                        args.append(self.comp_cast(
                            self.visit(func_type.parameter_defaults[arg_names[x]]),
                            self.visit(func_type.parameters[arg_names[x]]),
                            node
                        ))
                args_supplied.append(arg)
        elif len(node.arguments) + len(node.named_arguments) > len(func_type.args) and func_type.var_arg is None:
            raise SyntaxError('Unexpected arguments')
        else:
            args = []
            for i, arg in enumerate(node.arguments):
                args.append(self.comp_cast(self.visit(arg), func_type.args[i], node))
        return self.call(name, args)

    def comp_cast(self, arg, typ, node):
        if types_compatible(str(arg.type), typ):
            return cast_ops(self, arg, typ, node)

        return arg

    def visit_compound(self, node):
        ret = None
        for child in node.children:
            temp = self.visit(child)
            if temp:
                ret = temp
        return ret

    def visit_structdeclaration(self, node):
        fields = []
        for field in node.fields.values():
            fields.append(type_map[field.value])

        struct = self.module.context.get_identified_type(node.name)
        struct.fields = [field for field in node.fields.keys()]
        struct.name = 'struct.' + node.name
        struct.set_body([field for field in fields])
        self.define(node.name, struct)

    def visit_classdeclaration(self, node):
        self.in_class = True

        fields = []
        for field in node.class_fields.values():
            fields.append(type_map[field.value])

        classdecl = self.module.context.get_identified_type(node.name)
        classdecl.fields = [field for field in node.class_fields.keys()]
        classdecl.name = 'class.' + node.name
        classdecl.set_body([field for field in fields])

        # self.funcdecl('class.{}.new'.format(node.name), node.constructor)
        self.in_class = False
        self.define(node.name, classdecl)

    def visit_typedeclaration(self, node):
        raise NotImplementedError

    def visit_incrementassign(self, node):
        collection_access = None
        key = None
        if isinstance(node.left, CollectionAccess):
            collection_access = True
            var_name = self.search_scopes(node.left.collection.value)
            key = self.const(node.left.key.value)
            var = self.call('dyn_array_get', [var_name, key])
            pointee = var.type
        else:
            var_name = node.left.value
            var = self.load(var_name)
            pointee = self.search_scopes(var_name).type.pointee
        op = node.op
        temp = ir.Constant(var.type, 1)

        if isinstance(pointee, ir.IntType):
            if op == PLUS_PLUS:
                res = self.builder.add(var, temp)
            elif op == MINUS_MINUS:
                res = self.builder.sub(var, temp)
        elif isinstance(pointee, ir.DoubleType) or isinstance(pointee, ir.FloatType):
            if op == PLUS_PLUS:
                res = self.builder.fadd(var, temp)
            elif op == MINUS_MINUS:
                res = self.builder.fsub(var, temp)
        else:
            raise NotImplementedError()

        if collection_access:
            self.call('dyn_array_set', [var_name, key, res])
        else:
            self.store(res, var_name)

    def visit_aliasdeclaration(self, node):
        type_map[node.name] = type_map[node.collection.value]
        return ALIAS

    def visit_vardecl(self, node):
        var_addr = self.allocate(type_map[node.type.value], name=node.value.value)
        self.define(node.value.value, var_addr)
        self.store(self.visit(node.value), node.value.value)

    @staticmethod
    def visit_type(node):
        return type_map[node.value]

    def visit_if(self, node):
        start_block = self.add_block('if.start')
        end_block = self.add_block('if.end')
        self.branch(start_block)
        self.position_at_end(start_block)
        for x, comp in enumerate(node.comps):
            if_true_block = self.add_block('if.true.{}'.format(x))
            if x + 1 < len(node.comps):
                if_false_block = self.add_block('if.false.{}'.format(x))
            else:
                if_false_block = end_block
            cond_val = self.visit(comp)
            self.cbranch(cond_val, if_true_block, if_false_block)
            self.position_at_end(if_true_block)
            ret = self.visit(node.blocks[x])
            if not ret and not self.is_break:
                self.branch(end_block)
            self.position_at_end(if_false_block)

        if not self.is_break:
            self.position_at_end(end_block)
        else:
            self.is_break = False

    def visit_else(self, _):
        return self.builder.icmp_signed(EQUALS, self.const(1), self.const(1), 'cmptmp')

    def visit_while(self, node):
        cond_block = self.add_block('while.cond')
        body_block = self.add_block('while.body')
        end_block = self.add_block('while.end')
        self.loop_test_blocks.append(cond_block)
        self.loop_end_blocks.append(end_block)
        self.branch(cond_block)
        self.position_at_end(cond_block)
        cond = self.visit(node.comp)
        self.cbranch(cond, body_block, end_block)
        self.position_at_end(body_block)
        self.visit(node.block)
        if not self.is_break:
            self.branch(cond_block)
        else:
            self.is_break = False
        self.position_at_end(end_block)
        self.loop_test_blocks.pop()
        self.loop_end_blocks.pop()

    def visit_for(self, node):
        init_block = self.add_block('for.init')
        zero_length_block = self.add_block('for.zero_length')
        non_zero_length_block = self.add_block('for.non_zero_length')
        cond_block = self.add_block('for.cond')
        body_block = self.add_block('for.body')
        end_block = self.add_block('for.end')
        self.loop_test_blocks.append(cond_block)
        self.loop_end_blocks.append(end_block)
        self.branch(init_block)

        self.position_at_end(init_block)
        zero = self.const(0)
        one = self.const(1)
        if node.iterator.value == RANGE:
            iterator = self.visit(node.iterator)
        else:
            iterator = self.search_scopes(node.iterator.value)
        stop = self.call('dyn_array_length', [iterator])
        self.branch(zero_length_block)

        self.position_at_end(zero_length_block)
        cond = self.builder.icmp_signed(LESS_THAN, zero, stop)
        self.cbranch(cond, non_zero_length_block, end_block)

        self.position_at_end(non_zero_length_block)
        varname = node.elements[0].value
        val = self.call('dyn_array_get', [iterator, zero])
        self.alloc_define_store(val, varname, iterator.type.pointee.elements[2].pointee)
        position = self.alloc_define_store(zero, 'position', type_map[INT])
        self.branch(cond_block)

        self.position_at_end(cond_block)
        cond = self.builder.icmp_signed(LESS_THAN, self.load(position), stop)
        self.cbranch(cond, body_block, end_block)

        self.position_at_end(body_block)
        self.store(self.call('dyn_array_get', [iterator, self.load(position)]), varname)
        self.store(self.builder.add(one, self.load(position)), position)
        self.visit(node.block)
        if not self.is_break:
            self.branch(cond_block)
        else:
            self.is_break = False

        self.position_at_end(end_block)
        self.loop_test_blocks.pop()
        self.loop_end_blocks.pop()

    def visit_loopblock(self, node):
        for child in node.children:
            temp = self.visit(child)
            if temp:
                return temp

    def visit_switch(self, node):
        default_exists = False
        switch_end_block = self.add_block('switch_end')
        default_block = self.add_block('default')
        switch = self.switch(self.visit(node.value), default_block)
        cases = []
        for case in node.cases:
            if case.value == DEFAULT:
                cases.append(default_block)
                default_exists = True
            else:
                cases.append(self.add_block('case'))
        if not default_exists:
            self.position_at_end(default_block)
            self.branch(switch_end_block)
        for x, case in enumerate(node.cases):
            self.position_at_end(cases[x])
            break_ = self.visit(case.block)
            if break_ == BREAK:
                self.branch(switch_end_block)
            else:
                if x == len(node.cases) - 1:
                    self.branch(switch_end_block)
                else:
                    self.branch(cases[x + 1])
            if case.value != DEFAULT:
                switch.add_case(self.visit(case.value), cases[x])
        self.position_at_end(switch_end_block)

    def visit_break(self, _):
        if 'case' in self.builder.block.name:
            return BREAK

        self.is_break = True
        return self.branch(self.loop_end_blocks[-1])

    def visit_continue(self, _):
        self.is_break = True
        return self.branch(self.loop_test_blocks[-1])

    @staticmethod
    def visit_pass(_):
        return

    def visit_unaryop(self, node):
        return unary_op(self, node)

    def visit_range(self, node):
        start = self.visit(node.left)
        stop = self.visit(node.right)
        array_ptr = self.create_array(INT)  # TODO: This should be changed to allow any type
        self.call('create_range', [array_ptr, start, stop])
        return array_ptr

    def visit_assign(self, node):  # TODO: Simplify this, it just keeps getting worse
        if hasattr(node.right, 'name') and isinstance(self.search_scopes(node.right.name), ir.IdentifiedStructType):
            self.define(node.left.value.value, self.visit(node.right))
        elif hasattr(node.right, 'value') and isinstance(self.search_scopes(node.right.value), ir.Function):
            self.define(node.left.value, self.search_scopes(node.right.value))
        else:
            if isinstance(node.right, Input):
                node.right.type = node.left.type_node.value
            var = self.visit(node.right)
            if not var:
                return
            if isinstance(node.left, VarDecl):
                var_name = node.left.value.value
                var_type = type_map[node.left.type.value]
                casted_value = cast_ops(self, var, var_type, node)
                self.alloc_define_store(casted_value, var_name, var_type)
            elif isinstance(node.left, DotAccess):
                obj = self.search_scopes(node.left.obj)
                obj_type = self.search_scopes(obj.struct_name)
                idx = -1
                for i, v in enumerate(obj_type.fields):
                    if v == node.left.field:
                        idx = i
                        break

                elem = self.builder.gep(obj, [self.const(0, width=INT32), self.const(idx, width=INT32)], inbounds=True)
                self.builder.store(self.visit(node.right), elem)
            elif isinstance(node.left, CollectionAccess):
                right = self.visit(node.right)
                self.call('dyn_array_set', [self.search_scopes(node.left.collection.value), self.const(node.left.key.value), right])
            else:
                var_name = node.left.value
                var_value = self.top_scope.get(var_name)
                if var_value:
                    if isinstance(var_value, float):
                        node.right.value = float(node.right.value)
                    self.store(var, var_name)
                elif isinstance(var, ir.Function):
                    self.define(var_name, var)
                else:
                    self.alloc_define_store(var, var_name, var.type)

    def visit_fieldassignment(self, node):
        obj = self.search_scopes(node.obj)
        obj_type = self.search_scopes(obj.struct_name)
        return self.builder.extract_value(self.load(node.obj), obj_type.fields.index(node.field))

    def struct_assign(self, node):
        struct_type = self.search_scopes(node.name)
        struct = self.builder.alloca(struct_type)

        fields = []
        for field in node.named_arguments.values():
            fields.append(self.visit(field))
            elem = self.builder.gep(struct, [self.const(0, width=INT32), self.const(len(fields) - 1, width=INT32)], inbounds=True)
            self.builder.store(fields[len(fields) - 1], elem)

        struct.struct_name = node.name
        return struct

    def visit_dotaccess(self, node):
        obj = self.search_scopes(node.obj)
        obj_type = self.search_scopes(obj.struct_name)
        return self.builder.extract_value(self.load(node.obj), obj_type.fields.index(node.field))

    def visit_opassign(self, node):
        right = self.visit(node.right)
        collection_access = None
        key = None
        if isinstance(node.left, CollectionAccess):
            collection_access = True
            var_name = self.search_scopes(node.left.collection.value)
            key = self.const(node.left.key.value)
            var = self.call('dyn_array_get', [var_name, key])
            pointee = var.type
        else:
            var_name = node.left.value
            var = self.load(var_name)
            pointee = self.search_scopes(var_name).type.pointee
        op = node.op
        right = cast_ops(self, right, var.type, node)
        if isinstance(pointee, ir.IntType):
            if op == PLUS_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.add(var, right)
            elif op == MINUS_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.sub(var, right)
            elif op == MUL_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.mul(var, right)
            elif op == FLOORDIV_ASSIGN:
                # We convert a lot in case that right operand is float
                temp = cast_ops(self, var, ir.DoubleType(), node)
                temp_right = cast_ops(self, right, ir.DoubleType(), node)
                temp = self.builder.fdiv(temp, temp_right)
                res = cast_ops(self, temp, var.type, node)
            elif op == DIV_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.sdiv(var, right)
            elif op == MOD_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.srem(var, right)
            elif op == POWER_ASSIGN:
                if not isinstance(node.right.value, int):
                    error('Cannot use non-integers for power coeficient')
                    # TODO: Send me to typechecker and check for binop as well

                right = cast_ops(self, right, var.type, node)
                temp = self.alloc_and_store(var, type_map[INT])
                for _ in range(node.right.value - 1):
                    res = self.builder.mul(self.load(temp), var)
                    self.store(res, temp)
                res = self.load(temp)
            else:
                raise NotImplementedError()
        elif isinstance(pointee, ir.DoubleType) or isinstance(pointee, ir.FloatType):
            if op == PLUS_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.fadd(var, right)
            elif op == MINUS_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.fsub(var, right)
            elif op == MUL_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.fmul(var, right)
            elif op == FLOORDIV_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.fdiv(var, right)
                temp = cast_ops(self, res, ir.IntType(64), node)
                res = cast_ops(self, temp, res.type, node)
            elif op == DIV_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.fdiv(var, right)
            elif op == MOD_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                res = self.builder.frem(var, right)
            elif op == POWER_ASSIGN:
                right = cast_ops(self, right, var.type, node)
                temp = self.alloc_and_store(var, type_map[DOUBLE])
                for _ in range(node.right.value - 1):
                    res = self.builder.fmul(self.load(temp), var)
                    self.store(res, temp)
                res = self.load(temp)
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

        if collection_access:
            self.call('dyn_array_set', [var_name, key, res])
        else:
            self.store(res, var_name)

    def visit_constant(self, node):
        if node.value == TRUE:
            return self.const(1, BOOL)
        elif node.value == FALSE:
            return self.const(0, BOOL)
        else:
            raise NotImplementedError('file={} line={}'.format(self.file_name, node.line_num))

    def visit_collection(self, node):
        elements = []
        for item in node.items:
            elements.append(self.visit(item))
        if node.type == LIST:
            return self.define_array(node, elements)
        elif node.type == TUPLE:
            return self.define_tuple(node, elements)
        else:
            raise NotImplementedError

    def define_array(self, node, elements):
        array_ptr = self.create_array(node.items[0].val_type)
        for element in elements:
            self.call('dyn_array_append', [array_ptr, element])
        return self.load(array_ptr)

    def create_array(self, array_type):
        dyn_array_type = self.search_scopes('Dynamic_Array')
        array = dyn_array_type([self.const(0), self.const(0), self.const(0).inttoptr(type_map[INT].as_pointer())])
        # ptr = self.const(0).inttoptr(type_map[INT].as_pointer())
        # ptr = self.builder.bitcast(ptr, type_map[array_type].as_pointer())
        # dyn_array_type = ir.LiteralStructType([type_map[INT], type_map[INT], type_map[array_type].as_pointer()])
        # self.define('{}_Array'.format(array_type), dyn_array_type)
        # array = dyn_array_type([self.const(0), self.const(0), ptr])
        array = self.alloc_and_store(array, dyn_array_type)
        # self.call('{}_array_init'.format(array_type), [array])
        self.call('dyn_array_init', [array])
        return array

    def define_tuple(self, node, elements):
        raise NotImplementedError

    def visit_hashmap(self, node):
        raise NotImplementedError

    def visit_collectionaccess(self, node):
        key = self.visit(node.key)
        collection = self.search_scopes(node.collection.value)
        if collection.type.pointee == self.search_scopes('Dynamic_Array'):
            return self.call('dyn_array_get', [collection, key])

        return self.builder.extract_value(self.load(collection.name), [key])

    def visit_str(self, node):
        array = self.create_array(INT)
        string = node.value.encode('utf-8')
        for char in string:
            self.call('dyn_array_append', [array, self.const(char)])
        return array

    def visit_print(self, node):
        if node.value:
            val = self.visit(node.value)
        else:
            self.call('putchar', [ir.Constant(type_map[INT32], 10)])
            return
        if isinstance(val.type, ir.IntType):
            if val.type.width == 1:
                array = self.create_array(BOOL)
                self.call('bool_to_str', [array, val])
                val = array
            else:
                if val.type.signed:
                    if int(str(val.type).split("i")[1]) < 32:
                        val = self.builder.sext(val, type_map[INT32])
                        self.print_num("%d", val)
                    elif int(str(val.type).split("i")[1]) == 32:
                        self.print_num("%d", val)
                    else:
                        self.print_num("%lld", val)
                else:
                    if int(str(val.type).split("i")[1]) <= 32:
                        self.print_num("%u", val)
                    else:
                        self.print_num("%llu", val)
                return
        elif isinstance(val.type, (ir.FloatType, ir.DoubleType)):
            if isinstance(val.type, ir.FloatType):
                val = cast_ops(self, val, ir.DoubleType(), node)
            self.print_num("%g", val)
            return
        self.call('print', [val])

    def print_string(self, string):
        stringz = self.stringz(string)
        str_ptr = self.alloc_and_store(stringz, ir.ArrayType(stringz.type.element, stringz.type.count))
        str_ptr = self.gep(str_ptr, [self.const(0), self.const(0)])
        str_ptr = self.builder.bitcast(str_ptr, type_map[INT].as_pointer())
        self.call('puts', [str_ptr])

    def print_num(self, num_format, num):
        percent_d = self.stringz(num_format)
        percent_d = self.alloc_and_store(percent_d, ir.ArrayType(percent_d.type.element, percent_d.type.count))
        percent_d = self.gep(percent_d, [self.const(0), self.const(0)])
        percent_d = self.builder.bitcast(percent_d, type_map[INT8].as_pointer())
        self.call('printf', [percent_d, num])
        self.call('putchar', [ir.Constant(type_map[INT], 10)])

    def visit_input(self, node):
        # Print text if it exists
        if isinstance(node.value, Str):
            stringz = self.stringz(node.value.value)
            str_ptr = self.alloc_and_store(stringz, ir.ArrayType(stringz.type.element, stringz.type.count))
            str_ptr = self.gep(str_ptr, [self.const(0), self.const(0)])
            str_ptr = self.builder.bitcast(str_ptr, type_map[INT].as_pointer())
            self.call('puts', [str_ptr])

        percent_d = self.stringz('%d')
        percent_ptr = self.alloc_and_store(percent_d, ir.ArrayType(percent_d.type.element, percent_d.type.count))
        percent_ptr_gep = self.gep(percent_ptr, [self.const(0), self.const(0)])
        percent_ptr_gep = self.builder.bitcast(percent_ptr_gep, type_map[INT8].as_pointer())
        return self.call('scanf', [percent_ptr_gep, self.allocate(type_map[INT])])

    def start_function(self, name, return_type, parameters, parameter_defaults=None, varargs=None):
        self.function_stack.append(self.current_function)
        self.block_stack.append(self.builder.block)
        self.new_scope()
        ret_type = type_map[return_type.value]
        args = [type_map[param.value] for param in parameters.values()]
        func_type = ir.FunctionType(ret_type, args, varargs)
        func_type.parameters = parameters
        if parameter_defaults:
            func_type.parameter_defaults = parameter_defaults
        if hasattr(return_type, 'func_ret_type') and return_type.func_ret_type:
            func_type.return_type = func_type.return_type(type_map[return_type.func_ret_type.value], [return_type.func_ret_type.value]).as_pointer()
        func = ir.Function(self.module, func_type, name)
        self.define(name, func, 1)
        self.current_function = func
        entry = self.add_block('entry')
        self.exit_blocks.append(self.add_block('exit'))
        self.position_at_end(entry)

    def end_function(self, returned=False):
        if not returned:
            self.branch(self.exit_blocks[-1])
        self.position_at_end(self.exit_blocks.pop())
        if self.current_function.function_type.return_type != type_map[VOID]:
            retvar = self.load(self.search_scopes(RET_VAR))
            self.builder.ret(retvar)
        else:
            self.builder.ret_void()
        back_block = self.block_stack.pop()
        self.position_at_end(back_block)
        last_function = self.function_stack.pop()
        self.current_function = last_function
        self.drop_top_scope()

    def new_builder(self, block):
        self.builder = ir.IRBuilder(block)
        return self.builder

    def add_block(self, name):
        return self.current_function.append_basic_block(name)

    def position_at_end(self, block):
        self.builder.position_at_end(block)

    def cbranch(self, cond, true_block, false_block):
        self.builder.cbranch(cond, true_block, false_block)

    def branch(self, block):
        self.builder.branch(block)

    def switch(self, value, default):
        return self.builder.switch(value, default)

    def const(self, val, width=None):
        if isinstance(val, int):
            if width:
                return ir.Constant(type_map[width], val)

            return ir.Constant(type_map[INT], val)
        elif isinstance(val, (float, Decimal)):
            return ir.Constant(type_map[DOUBLE], val)
        elif isinstance(val, bool):
            return ir.Constant(type_map[BOOL], bool(val))
        elif isinstance(val, str):
            return self.stringz(val)
        else:
            raise NotImplementedError

    def allocate(self, typ, name=''):
        saved_block = self.builder.block
        var_addr = self.create_entry_block_alloca(name, typ)
        self.builder.position_at_end(saved_block)
        return var_addr

    def alloc_and_store(self, val, typ, name=''):
        var_addr = self.builder.alloca(typ, name=name)
        self.builder.store(val, var_addr)
        return var_addr

    def alloc_and_define(self, name, typ):
        var_addr = self.builder.alloca(typ, name=name)
        self.define(name, var_addr)
        return var_addr

    def alloc_define_store(self, val, name, typ):
        saved_block = self.builder.block
        var_addr = self.builder.alloca(typ, name=name)
        self.define(name, var_addr)
        self.builder.position_at_end(saved_block)
        self.builder.store(val, var_addr)
        return var_addr

    def create_entry_block_alloca(self, name, typ):
        self.builder.position_at_start(self.builder.function.entry_basic_block)
        return self.builder.alloca(typ, size=None, name=name)

    def store(self, value, name):
        if isinstance(name, str):
            self.builder.store(value, self.search_scopes(name))
        else:
            self.builder.store(value, name)

    def load(self, name):
        if isinstance(name, str):
            return self.builder.load(self.search_scopes(name))
        return self.builder.load(name)

    def call(self, name, args):
        if isinstance(name, str):
            func = self.module.get_global(name)
        else:
            func = self.module.get_global(name.name)
        if func is None:
            raise TypeError('Calling non existant function')
        return self.builder.call(func, args)

    def gep(self, ptr, indices, inbounds=False, name=''):
        return self.builder.gep(ptr, indices, inbounds, name)

    def _add_builtins(self):
        malloc_ty = ir.FunctionType(type_map[INT8].as_pointer(), [type_map[INT]])
        ir.Function(self.module, malloc_ty, 'malloc')

        realloc_ty = ir.FunctionType(type_map[INT8].as_pointer(), [type_map[INT8].as_pointer(), type_map[INT]])
        ir.Function(self.module, realloc_ty, 'realloc')

        free_ty = ir.FunctionType(type_map[VOID], [type_map[INT8].as_pointer()])
        ir.Function(self.module, free_ty, 'free')

        exit_ty = ir.FunctionType(type_map[VOID], [type_map[INT32]])
        ir.Function(self.module, exit_ty, 'exit')

        putchar_ty = ir.FunctionType(type_map[INT], [type_map[INT]])
        ir.Function(self.module, putchar_ty, 'putchar')

        printf_ty = ir.FunctionType(type_map[INT32], [type_map[INT8].as_pointer()], var_arg=True)
        ir.Function(self.module, printf_ty, 'printf')

        scanf_ty = ir.FunctionType(type_map[INT], [type_map[INT8].as_pointer(), type_map[INT].as_pointer()], var_arg=True)
        ir.Function(self.module, scanf_ty, 'scanf')

        getchar_ty = ir.FunctionType(ir.IntType(4), [])
        ir.Function(self.module, getchar_ty, 'getchar')

        puts_ty = ir.FunctionType(type_map[INT], [type_map[INT].as_pointer()])
        ir.Function(self.module, puts_ty, 'puts')

        define_builtins(self)

    @staticmethod
    def stringz(string):
        n = len(string) + 1
        buf = bytearray((' ' * n).encode('ascii'))
        buf[-1] = 0
        buf[:-1] = string.encode('utf-8')
        return ir.Constant(ir.ArrayType(type_map[INT8], n), buf)

    def generate_code(self, node):
        return self.visit(node)

    def add_debug_info(self, optimize, filename):
        di_file = self.module.add_debug_info("DIFile", {
            "filename": os.path.basename(os.path.abspath(filename)),
            "directory": os.path.dirname(os.path.abspath(filename)),
        })
        di_module = self.module.add_debug_info("DICompileUnit", {
            "language": ir.DIToken("DW_LANG_Python"),
            "file": di_file,
            "producer": "lesma",
            "runtimeVersion": 1,
            "isOptimized": optimize,
        }, is_distinct=True)
        # self.module.add_global(di_module)
        self.module.add_named_metadata('llvm.dbg.cu', [di_file, di_module])

    def evaluate(self, optimize=True, ir_dump=False, timer=False):
        if ir_dump and not optimize:
            for func in self.module.functions:
                if func.name == "main":
                    print(func)

        llvmmod = llvm.parse_assembly(str(self.module))
        if optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 3
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvmmod)
            if ir_dump:
                print(str(llvmmod))
        target_machine = llvm.Target.from_default_triple().create_target_machine()
        with llvm.create_mcjit_compiler(llvmmod, target_machine) as ee:
            ee.finalize_object()
            fptr = CFUNCTYPE(c_void_p)(ee.get_function_address('main'))
            start_time = time()
            fptr()
            end_time = time()
            if timer:
                print('\nExecuted in {:f} sec'.format(end_time - start_time))

    def compile(self, filename, optimize=True, output=None, emit_llvm=False):
        spinner = Spinner()
        spinner.startSpinner("Compiling")
        compile_time = time()

        self.add_debug_info(optimize, filename)
        program_string = llvm.parse_assembly(str(self.module))

        prog_str = str(program_string)
        if output is None:
            output = os.path.splitext(filename)[0]

        with open(output + '.ll', 'w') as out:
            out.write(prog_str)

        with open(os.devnull, "w") as tmpout:
            subprocess.call('clang {0}.ll -O3 -o {0}'.format(output).split(" "), stdout=tmpout, stderr=tmpout)
            spinner.stopSpinner()
            successful("compilation done in: %.3f seconds" % (time() - compile_time))
            successful("binary file wrote to " + output)

        if emit_llvm:
            successful("llvm assembler wrote to " + output + ".ll")
        else:
            os.remove(output + '.ll')
