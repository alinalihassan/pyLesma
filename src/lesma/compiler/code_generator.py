from ctypes import CFUNCTYPE, c_void_p
from decimal import Decimal
from time import time
import llvmlite.binding as llvm
import os
from math import inf
import subprocess
from llvmlite import ir
from lesma.grammar import *
from lesma.ast import CollectionAccess, DotAccess, Input, VarDecl, Str
from lesma.compiler import RET_VAR, type_map, llvm_type_map
from lesma.compiler.operations import unary_op, binary_op, cast_ops
from lesma.compiler.builtins import define_builtins
from lesma.compiler.builtins import create_dynamic_array_methods
from lesma.compiler.builtins import array_types
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
        func_ty = ir.FunctionType(ir.IntType(64), [])  # [type_map[INT32], type_map[INT8].as_pointer().as_pointer()])
        func = ir.Function(self.module, func_ty, 'main')
        entry_block = func.append_basic_block('entry')
        exit_block = func.append_basic_block('exit')
        self.current_function = func
        self.function_stack = [func]
        self.builder = ir.IRBuilder(entry_block)
        self.exit_blocks = [exit_block]
        self.block_stack = [entry_block]
        self.defer_stack = [[]]
        self.loop_test_blocks = []
        self.loop_end_blocks = []
        self.is_break = False
        self.in_class = False
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        self.anon_counter = 0

        # for i in range(2):
        #     func.args[i].name = '.argc' if i == 0 else '.argv'
        #     self.alloc_define_store(func.args[i], func.args[i].name[1:], func.args[i].type)

    def __str__(self):
        return str(self.module)

    def visit_program(self, node):
        self.visit(node.block)
        for stat in self.defer_stack[-1]:
            self.visit(stat)
        self.branch(self.exit_blocks[0])
        self.position_at_end(self.exit_blocks[0])
        self.builder.ret(self.const(0))

    @staticmethod
    def visit_num(node):
        return ir.Constant(type_map[node.val_type], node.value)

    def visit_var(self, node):
        var = self.search_scopes(node.value)
        if isinstance(var, type_map[FUNC]) or isinstance(var, ir.Function):
            return var
        return self.load(node.value)

    def visit_binop(self, node):
        return binary_op(self, node)

    def visit_defer(self, node):
        self.defer_stack[-1].append(node.statement)

    def visit_anonymousfunc(self, node):
        self.anon_counter += 1
        self.funcdef('anon_func.{}'.format(self.anon_counter), node, "private")
        return self.search_scopes('anon_func.{}'.format(self.anon_counter))

    def visit_funcdecl(self, node):
        self.funcdef(node.name, node)

    def visit_externfuncdecl(self, node):
        self.externfuncdecl(node.name, node)

    def externfuncdecl(self, name, node):
        for func in self.module.functions:
            if func.name == name:
                self.define(name, func, 1)
                return
        return_type = node.return_type
        parameters = node.parameters
        varargs = node.varargs
        ret_type = self.get_type(return_type)
        args = self.get_args(parameters)
        func_type = ir.FunctionType(ret_type, args, varargs)
        func_type.parameters = parameters
        func = ir.Function(self.module, func_type, name)
        self.define(name, func, 1)

    def funcdecl(self, name, node, linkage=None):
        self.func_decl(name, node.return_type, node.parameters, node.parameter_defaults, node.varargs, linkage)

    def funcimpl(self, name, node):
        self.implement_func_body(name)
        for i, arg in enumerate(self.current_function.args):
            arg.name = list(node.parameters.keys())[i]

            # TODO: a bit hacky, cannot handle pointers atm but we need them for class reference
            if arg.name == SELF and isinstance(arg.type, ir.PointerType):
                self.define(arg.name, arg)
            else:
                self.alloc_define_store(arg, arg.name, arg.type)
        if self.current_function.function_type.return_type != type_map[VOID]:
            self.alloc_and_define(RET_VAR, self.current_function.function_type.return_type)
        ret = self.visit(node.body)
        self.end_function(ret)

    def funcdef(self, name, node, linkage=None):
        self.start_function(name, node.return_type, node.parameters, node.parameter_defaults, node.varargs, linkage)
        for i, arg in enumerate(self.current_function.args):
            arg.name = list(node.parameters.keys())[i]

            # TODO: a bit hacky, cannot handle pointers atm but we need them for class reference
            if arg.name == SELF and isinstance(arg.type, ir.PointerType):
                self.define(arg.name, arg)
            else:
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

    def visit_methodcall(self, node):
        obj = self.search_scopes(node.obj)
        method = self.search_scopes(obj.type.pointee.name + '.' + node.name)
        return self.methodcall(node, method, obj)

    def methodcall(self, node, func, obj):
        func_type = func.function_type
        if len(node.arguments) + 1 < len(func_type.args):
            args = []
            args_supplied = []
            arg_names = []

            for i in func_type.parameters:
                arg_names.append(i)

            for x, arg in enumerate(func_type.args):
                if x == 0:
                    continue
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

        args.insert(0, obj)
        return self.builder.call(func, args)

    def visit_funccall(self, node):
        func_type = self.search_scopes(node.name)
        isFunc = False
        if isinstance(func_type, ir.AllocaInstr):
            name = self.load(func_type)
            func_type = name.type.pointee
            isFunc = True
        elif isinstance(func_type, ir.Function):
            func_type = func_type.type.pointee
            name = self.search_scopes(node.name)
            name = name.name
        elif isinstance(func_type, ir.IdentifiedStructType):
            typ = self.search_scopes(node.name)
            if typ.type == STRUCT:
                return self.struct_assign(node)
            elif typ.type == CLASS:
                return self.class_assign(node)
            error("Unexpected Identified Struct Type")
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

        if isFunc:
            return self.builder.call(name, args)
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

    def visit_enumdeclaration(self, node):
        enum = self.module.context.get_identified_type(node.name)
        enum.fields = [field for field in node.fields]
        enum.name = node.name
        enum.type = ENUM
        enum.set_body(ir.IntType(8, signed=False))
        self.define(node.name, enum)

    def visit_structdeclaration(self, node):
        fields = []
        for field in node.fields.values():
            fields.append(type_map[field.value])

        struct = self.module.context.get_identified_type(node.name)
        struct.fields = [field for field in node.fields.keys()]
        struct.defaults = node.defaults
        struct.name = node.name
        struct.type = STRUCT
        struct.set_body(*[field for field in fields])
        self.define(node.name, struct)

    def visit_classdeclaration(self, node):
        self.in_class = True

        fields = []
        for field in node.fields.values():
            fields.append(self.get_type(field))

        classdecl = self.module.context.get_identified_type(node.name)
        classdecl.fields = [field for field in node.fields.keys()]
        classdecl.name = node.name
        classdecl.type = CLASS
        classdecl.set_body(*[field for field in fields])
        self.define(node.name, classdecl)
        for method in node.methods:
            self.funcdecl(method.name, method)

        for method in node.methods:
            self.funcimpl(method.name, method)
        classdecl.methods = [self.search_scopes(method.name) for method in node.methods]

        self.in_class = False
        self.define(node.name, classdecl)

    def visit_incrementassign(self, node):
        collection_access = None
        key = None
        if isinstance(node.left, CollectionAccess):
            collection_access = True
            var_name = self.search_scopes(node.left.collection.value)
            array_type = str(var_name.type.pointee.elements[-1].pointee)
            key = self.const(node.left.key.value)
            var = self.call('{}.array.get'.format(array_type), [var_name, key])
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
            self.call('{}.array.set'.format(array_type), [var_name, key, res])
        else:
            self.store(res, var_name)

    def visit_typedeclaration(self, node):
        if node.collection.value in type_map:
            type_map[node.name] = type_map[node.collection.value]
        else:
            self.define(node.name, self.search_scopes(node.collection.value))
        return TYPE

    def visit_vardecl(self, node):
        typ = self.get_type(node.type)
        if node.type.value == FUNC:
            func_ret_type = self.get_type(node.type.func_ret_type)
            func_parameters = self.get_args(node.type.func_params)
            func_ty = ir.FunctionType(func_ret_type, func_parameters, None).as_pointer()
            typ = func_ty
            self.alloc_and_define(node.value.value, typ)
        elif node.type.value in (LIST, TUPLE):
            array_type = self.get_type(node.type.func_params['0'])
            self.create_array(array_type)
            typ = self.search_scopes('{}.array'.format(array_type))
            self.alloc_and_define(node.value.value, typ)
        else:
            self.alloc_and_define(node.value.value, typ)

    def visit_type(self, node):
        return type_map[node.value] if node.value in type_map else self.search_scopes(node.value)

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
        array_type = None
        if node.iterator.value == RANGE:
            iterator = self.alloc_and_store(self.visit(node.iterator), type_map[STR])
            array_type = "i64"
        else:
            iterator = self.search_scopes(node.iterator.value)
            array_type = str(iterator.type.pointee.elements[-1].pointee)

        stop = self.call('{}.array.length'.format(array_type), [iterator])
        self.branch(zero_length_block)

        self.position_at_end(zero_length_block)
        cond = self.builder.icmp_signed(LESS_THAN, zero, stop)
        self.cbranch(cond, non_zero_length_block, end_block)

        self.position_at_end(non_zero_length_block)
        varname = node.elements[0].value
        val = self.call('{}.array.get'.format(array_type), [iterator, zero])
        self.alloc_define_store(val, varname, iterator.type.pointee.elements[2].pointee)
        position = self.alloc_define_store(zero, 'position', type_map[INT])
        self.branch(cond_block)

        self.position_at_end(cond_block)
        cond = self.builder.icmp_signed(LESS_THAN, self.load(position), stop)
        self.cbranch(cond, body_block, end_block)

        self.position_at_end(body_block)
        self.store(self.call('{}.array.get'.format(array_type), [iterator, self.load(position)]), varname)
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
            fallthrough = self.visit(case.block)
            if fallthrough != FALLTHROUGH:
                self.branch(switch_end_block)
            else:
                if x == len(node.cases) - 1:
                    self.branch(switch_end_block)
                else:
                    self.branch(cases[x + 1])
            if case.value != DEFAULT:
                switch.add_case(self.visit(case.value), cases[x])
        self.position_at_end(switch_end_block)

    def visit_fallthrough(self, node):
        if 'case' in self.builder.block.name:
            return FALLTHROUGH
        else:  # TODO: Move this to typechecker
            error('file={} line={} Syntax Error: fallthrough keyword cannot be used outside of switch statements'.format(self.file_name, node.line_num))

    def visit_break(self, node):
        if len(self.loop_end_blocks) == 0:  # TODO: Move this to typechecker
            error('file={} line={} Syntax Error: break keyword cannot be used outside of control flow statements'.format(self.file_name, node.line_num))
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
        array_ptr = self.create_array(type_map[INT])
        self.call('@create_range', [array_ptr, start, stop])
        return self.load(array_ptr)

    def visit_assign(self, node):
        if isinstance(node.right, DotAccess) and self.search_scopes(node.right.obj).type == ENUM or \
           hasattr(node.right, 'name') and isinstance(self.search_scopes(node.right.name), ir.IdentifiedStructType):
            var_name = node.left.value if isinstance(node.left.value, str) else node.left.value.value
            self.define(var_name, self.visit(node.right))
        elif hasattr(node.right, 'value') and isinstance(self.search_scopes(node.right.value), ir.Function):
            self.define(node.left.value, self.search_scopes(node.right.value))
        else:
            if isinstance(node.right, Input):
                if hasattr(node.left, 'type'):
                    node.right.type = node.left.type
                else:
                    node.right.type = str
            var = self.visit(node.right)
            if not var:
                return
            if isinstance(node.left, VarDecl):
                var_name = node.left.value.value
                if node.left.type.value in (LIST, TUPLE):
                    var_type = type_map[list(node.left.type.func_params.items())[0][1].value]
                    self.alloc_define_store(var, var_name, var.type)
                else:
                    var_type = type_map[node.left.type.value]
                    if not var.type.is_pointer:
                        casted_value = cast_ops(self, var, var_type, node)
                        self.alloc_define_store(casted_value, var_name, var_type)
                    else:  # TODO: Not able currently to deal with pointers, such as functions
                        self.alloc_define_store(var, var_name, var.type)
            elif isinstance(node.left, DotAccess):
                obj = self.search_scopes(node.left.obj)
                obj_type = self.search_scopes(obj.type.pointee.name.split('.')[-1])
                idx = -1
                for i, v in enumerate(obj_type.fields):
                    if v == node.left.field:
                        idx = i
                        break

                elem = self.builder.gep(obj, [self.const(0, width=INT32), self.const(idx, width=INT32)], inbounds=True)
                self.builder.store(self.visit(node.right), elem)
            elif isinstance(node.left, CollectionAccess):
                right = self.visit(node.right)
                array_type = str(self.search_scopes(node.left.collection.value).type.pointee.elements[-1].pointee)
                self.call('{}.array.set'.format(array_type), [self.search_scopes(node.left.collection.value), self.const(node.left.key.value), right])
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
        obj_type = self.search_scopes(obj.name)
        return self.builder.extract_value(self.load(node.obj), obj_type.fields.index(node.field))

    def class_assign(self, node):
        class_type = self.search_scopes(node.name)
        _class = self.builder.alloca(class_type)

        for func in class_type.methods:
            if func.name.split(".")[-1] == 'new':
                self.methodcall(node, func, _class)

        return _class

    def struct_assign(self, node):
        struct_type = self.search_scopes(node.name)
        struct = self.builder.alloca(struct_type)

        fields = set()
        for index, field in struct_type.defaults.items():
            val = self.visit(field)
            pos = struct_type.fields.index(index)
            fields.add(index)
            elem = self.builder.gep(struct, [self.const(0, width=INT32), self.const(pos, width=INT32)], inbounds=True)
            self.builder.store(val, elem)

        for index, field in enumerate(node.named_arguments.values()):
            val = self.visit(field)
            pos = struct_type.fields.index(list(node.named_arguments.keys())[index])
            fields.add((list(node.named_arguments.keys())[index]))
            elem = self.builder.gep(struct, [self.const(0, width=INT32), self.const(pos, width=INT32)], inbounds=True)
            self.builder.store(val, elem)

        if len(fields) < len(struct_type.fields):
            error('file={} line={} Syntax Error: struct declaration doesn\'t initialize all fields ({})'.format(
                self.file_name, node.line_num, ','.join(fields.symmetric_difference(set(struct_type.fields)))))

        struct.name = node.name
        return struct

    def visit_dotaccess(self, node):
        obj = self.search_scopes(node.obj)
        if obj.type == ENUM:
            enum = self.builder.alloca(obj)
            idx = obj.fields.index(node.field)
            val = self.builder.gep(enum, [self.const(0, width=INT32), self.const(0, width=INT32)], inbounds=True)
            self.builder.store(self.const(idx, width=INT8), val)
            return enum

        obj_type = self.search_scopes(obj.type.pointee.name.split('.')[-1])
        return self.builder.extract_value(self.load(node.obj), obj_type.fields.index(node.field))

    def visit_opassign(self, node):
        right = self.visit(node.right)
        collection_access = None
        key = None
        if isinstance(node.left, CollectionAccess):
            collection_access = True
            var_name = self.search_scopes(node.left.collection.value)
            array_type = str(self.search_scopes(node.left.collection.value).type.pointee.elements[-1].pointee)
            key = self.const(node.left.key.value)
            var = self.call('{}.array.get'.format(array_type), [var_name, key])
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
            self.call('{}.array.set'.format(array_type), [var_name, key, res])
        else:
            self.store(res, var_name)

    def visit_constant(self, node):
        if node.value == TRUE:
            return self.const(1, BOOL)
        elif node.value == FALSE:
            return self.const(0, BOOL)
        elif node.value == INF:
            return self.const(inf, DOUBLE)
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
        if hasattr(node.items[0], 'val_type'):
            array_type = type_map[node.items[0].val_type]
        else:
            array_type = self.visit(node.items[0]).type
        array_ptr = self.create_array(array_type)
        for element in elements:
            self.call('{}.array.append'.format(str(array_type)), [array_ptr, element])
        return self.load(array_ptr)

    def create_array(self, array_type):
        dyn_array_type = self.module.context.get_identified_type('{}.array'.format(str(array_type)))
        if self.search_scopes('{}.array'.format(str(array_type))) is None:
            dyn_array_type.name = '{}.array'.format(str(array_type))
            dyn_array_type.type = CLASS
            dyn_array_type.set_body(type_map[INT], type_map[INT], array_type.as_pointer())
            self.define('{}.array'.format(str(array_type)), dyn_array_type)

        array = dyn_array_type([self.const(0), self.const(0), self.const(0).inttoptr(array_type.as_pointer())])
        array = self.alloc_and_store(array, dyn_array_type)
        create_dynamic_array_methods(self, array_type)
        self.call('{}.array.init'.format(str(array_type)), [array])
        return array

    def define_tuple(self, node, elements):
        if hasattr(node.items[0], 'val_type'):
            array_type = type_map[node.items[0].val_type]
        else:
            array_type = self.visit(node.items[0]).type
        array_ptr = self.create_array(array_type)
        for element in elements:
            self.call('{}.array.append'.format(str(array_type)), [array_ptr, element])
        return self.load(array_ptr)

    def visit_hashmap(self, node):
        raise NotImplementedError

    def visit_collectionaccess(self, node):
        key = self.visit(node.key)
        collection = self.search_scopes(node.collection.value)
        for typ in array_types:
            if collection.type.pointee == self.search_scopes('{}.array'.format(typ)):
                return self.call('{}.array.get'.format(typ), [collection, key])

        return self.builder.extract_value(self.load(collection.name), [key])

    def visit_str(self, node):
        array = self.create_array(type_map[INT])
        string = node.value.encode('utf-8')
        for char in string:
            self.call('i64.array.append', [array, self.const(char)])
        return array

    def visit_print(self, node):
        if node.value:
            val = self.visit(node.value)
        else:
            self.call('putchar', [ir.Constant(type_map[INT32], 10)])
            return
        if isinstance(val.type, ir.IntType):
            if val.type.width == 1:
                array = self.create_array(type_map[INT])
                self.call('@bool_to_str', [array, val])
                val = array
            else:
                if int(str(val.type).split("i")[1]) == 8:
                    self.print_num("%c", val)
                elif val.type.signed:
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

    @staticmethod
    def typeToFormat(typ):
        fmt = None

        if isinstance(typ, ir.IntType):
            if int(str(typ).split("i")[1]) == 8:
                fmt = "%c"
            elif typ.signed:
                if int(str(typ).split("i")[1]) <= 32:
                    fmt = "%d"
                else:
                    fmt = "%lld"
            else:
                if int(str(typ).split("i")[1]) <= 32:
                    fmt = "%u"
                else:
                    fmt = "%llu"
        elif isinstance(typ, ir.FloatType):
            fmt = "%f"
        elif isinstance(typ, ir.DoubleType):
            fmt = "%lf"
        else:
            fmt = "%s"

        return fmt

    def visit_input(self, node):
        if isinstance(node.value, Str):  # Print text if it exists
            self.print_string(node.value.value)

        percent_d = self.stringz(self.typeToFormat(type_map[node.type.value]))
        percent_ptr = self.alloc_and_store(percent_d, ir.ArrayType(percent_d.type.element, percent_d.type.count))
        percent_ptr_gep = self.gep(percent_ptr, [self.const(0), self.const(0)])
        percent_ptr_gep = self.builder.bitcast(percent_ptr_gep, type_map[INT8].as_pointer())
        var = self.allocate(type_map[node.type.value])
        self.call('scanf', [percent_ptr_gep, var])
        return self.builder.load(var)

    def get_args(self, parameters):
        args = []
        for param in parameters.values():
            if param.value == FUNC:
                if param.func_ret_type.value in type_map:
                    func_ret_type = type_map[param.func_ret_type.value]
                elif self.search_scopes(param.func_ret_type.value) is not None:
                    func_ret_type = self.search_scopes(param.func_ret_type.value).as_pointer()
                func_parameters = self.get_args(param.func_params)
                func_ty = ir.FunctionType(func_ret_type, func_parameters, None).as_pointer()
                args.append(func_ty)
            elif param.value == LIST:
                array_type = self.get_type(param.func_params['0'])
                self.create_array(array_type)
                typ = self.search_scopes('{}.array'.format(array_type))
                args.append(typ)
            else:
                if param.value in type_map:
                    args.append(type_map[param.value])
                elif list(parameters.keys())[list(parameters.values()).index(param)] == SELF:
                    args.append(self.search_scopes(param.value).as_pointer())
                elif self.search_scopes(param.value) is not None:
                    args.append(self.search_scopes(param.value))
                else:
                    error("Parameter type not recognized: {}".format(param.value))

        return args

    def get_type(self, param):
        typ = None
        if param.value == FUNC:
            if param.func_ret_type.value in type_map:
                func_ret_type = type_map[param.func_ret_type.value]
            elif self.search_scopes(param.func_ret_type.value) is not None:
                func_ret_type = self.search_scopes(param.func_ret_type.value).as_pointer()
            func_parameters = self.get_args(param.func_params)
            func_ty = ir.FunctionType(func_ret_type, func_parameters, None).as_pointer()
            typ = func_ty
        elif param.value == LIST:
            array_type = self.get_type(param.func_params['0'])
            self.create_array(array_type)
            typ = self.search_scopes('{}.array'.format(array_type))
        else:
            if param.value in type_map:
                typ = type_map[param.value]
            elif self.search_scopes(param.value) is not None:
                typ = self.search_scopes(param.value)
            else:
                error("Type not recognized: {}".format(param.value))

        return typ

    def func_decl(self, name, return_type, parameters, parameter_defaults=None, varargs=None, linkage=None):
        ret_type = self.get_type(return_type)
        args = self.get_args(parameters)
        func_type = ir.FunctionType(ret_type, args, varargs)
        func_type.parameters = parameters
        if parameter_defaults:
            func_type.parameter_defaults = parameter_defaults
        func = ir.Function(self.module, func_type, name)
        func.linkage = linkage
        self.define(name, func, 1)

    def implement_func_body(self, name):
        self.function_stack.append(self.current_function)
        self.block_stack.append(self.builder.block)
        self.new_scope()
        self.defer_stack.append([])
        for f in self.module.functions:
            if f.name == name:
                func = f
                break
        self.current_function = func
        entry = self.add_block('entry')
        self.exit_blocks.append(self.add_block('exit'))
        self.position_at_end(entry)

    def start_function(self, name, return_type, parameters, parameter_defaults=None, varargs=None, linkage=None):
        self.function_stack.append(self.current_function)
        self.block_stack.append(self.builder.block)
        self.new_scope()
        self.defer_stack.append([])
        ret_type = self.get_type(return_type)
        args = self.get_args(parameters)
        func_type = ir.FunctionType(ret_type, args, varargs)
        func_type.parameters = parameters
        if parameter_defaults:
            func_type.parameter_defaults = parameter_defaults

        func = ir.Function(self.module, func_type, name)
        func.linkage = linkage
        self.define(name, func, 1)
        self.current_function = func
        entry = self.add_block('entry')
        self.exit_blocks.append(self.add_block('exit'))
        self.position_at_end(entry)

    def end_function(self, returned=False):
        for stat in self.defer_stack[-1]:
            self.visit(stat)
        self.defer_stack.pop()
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
        var_addr = self.builder.alloca(typ, name=name)
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

        scanf_ty = ir.FunctionType(type_map[INT], [type_map[INT8].as_pointer()], var_arg=True)
        ir.Function(self.module, scanf_ty, 'scanf')

        getchar_ty = ir.FunctionType(ir.IntType(8), [])
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
            "producer": "Lesma v0.4.0",
            "runtimeVersion": 1,
            "isOptimized": optimize,
        }, is_distinct=True)

        self.module.name = os.path.basename(os.path.abspath(filename))
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

        # self.add_debug_info(optimize, filename)
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
