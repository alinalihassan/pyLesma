from llvmlite import ir
from lesma.compiler import type_map
from lesma.grammar import *
import lesma.compiler.llvmlite_custom

ARRAY_INITIAL_CAPACITY = ir.Constant(type_map[INT], 16)

zero = ir.Constant(type_map[INT], 0)
one = ir.Constant(type_map[INT], 1)
two = ir.Constant(type_map[INT], 2)
eight = ir.Constant(type_map[INT], 8)
ten = ir.Constant(type_map[INT], 10)
zero_32 = ir.Constant(type_map[INT32], 0)
one_32 = ir.Constant(type_map[INT32], 1)
two_32 = ir.Constant(type_map[INT32], 2)

array_types = [INT]


def define_builtins(self):
    # 0: int size
    # 1: int capacity
    # 2: int *data
    str_struct = ir.LiteralStructType([type_map[INT], type_map[INT], type_map[INT].as_pointer()])
    self.define('Str', str_struct)
    str_struct_ptr = str_struct.as_pointer()
    self.define('Str_ptr', str_struct_ptr)
    type_map[STR] = str_struct

    dynamic_array_init(self, str_struct_ptr, INT)
    dynamic_array_double_if_full(self, str_struct_ptr, INT)
    dynamic_array_append(self, str_struct_ptr, INT)
    dynamic_array_get(self, str_struct_ptr, INT)
    dynamic_array_set(self, str_struct_ptr, INT)
    dynamic_array_length(self, str_struct_ptr, INT)

    define_create_range(self, str_struct_ptr, INT)

    define_int_to_str(self, str_struct_ptr)
    define_bool_to_str(self, str_struct_ptr)
    define_print(self, str_struct_ptr)


def create_dynamic_array_methods(self, array_type):
    if array_type in array_types:
        return
    array = self.search_scopes('{}_Array'.format(array_type))
    array_ptr = array.as_pointer()

    current_block = self.builder.block

    dynamic_array_init(self, array_ptr, array_type)
    dynamic_array_double_if_full(self, array_ptr, array_type)
    dynamic_array_append(self, array_ptr, array_type)
    dynamic_array_get(self, array_ptr, array_type)
    dynamic_array_set(self, array_ptr, array_type)
    dynamic_array_length(self, array_ptr, array_type)

    array_types.append(array_type)

    self.position_at_end(current_block)


def define_create_range(self, dyn_array_ptr, array_type):
    create_range_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr, type_map[INT], type_map[INT]])
    create_range = ir.Function(self.module, create_range_type, 'create_range')
    create_range_entry = create_range.append_basic_block('entry')
    builder = ir.IRBuilder(create_range_entry)
    self.builder = builder
    create_range_test = create_range.append_basic_block('test')
    create_range_body = create_range.append_basic_block('body')
    create_range_exit = create_range.append_basic_block('exit')

    builder.position_at_end(create_range_entry)
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(create_range.args[0], array_ptr)
    start_ptr = builder.alloca(type_map[INT])
    builder.store(create_range.args[1], start_ptr)
    stop_ptr = builder.alloca(type_map[INT])
    builder.store(create_range.args[2], stop_ptr)

    num_ptr = builder.alloca(type_map[INT])
    builder.store(builder.load(start_ptr), num_ptr)
    builder.branch(create_range_test)

    builder.position_at_end(create_range_test)
    cond = builder.icmp_signed(LESS_THAN, builder.load(num_ptr), builder.load(stop_ptr))
    builder.cbranch(cond, create_range_body, create_range_exit)

    builder.position_at_end(create_range_body)
    builder.call(self.module.get_global('{}_array_append'.format(array_type)), [builder.load(array_ptr), builder.load(num_ptr)])
    builder.store(builder.add(one, builder.load(num_ptr)), num_ptr)

    builder.branch(create_range_test)

    builder.position_at_end(create_range_exit)
    builder.ret_void()


def dynamic_array_init(self, dyn_array_ptr, array_type):
    # START
    dyn_array_init_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr])
    dyn_array_init = ir.Function(self.module, dyn_array_init_type, '{}_array_init'.format(array_type))
    dyn_array_init_entry = dyn_array_init.append_basic_block('entry')
    builder = ir.IRBuilder(dyn_array_init_entry)
    self.builder = builder
    dyn_array_init_exit = dyn_array_init.append_basic_block('exit')
    builder.position_at_end(dyn_array_init_entry)
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(dyn_array_init.args[0], array_ptr)

    # BODY
    size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
    builder.store(zero, size_ptr)

    capacity_ptr = builder.gep(builder.load(array_ptr), [zero_32, one_32], inbounds=True)
    builder.store(ARRAY_INITIAL_CAPACITY, capacity_ptr)

    data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)
    size_of = builder.mul(builder.load(capacity_ptr), eight)
    mem_alloc = builder.call(self.module.get_global('malloc'), [size_of])
    mem_alloc = builder.bitcast(mem_alloc, type_map[array_type].as_pointer())
    builder.store(mem_alloc, data_ptr)

    builder.branch(dyn_array_init_exit)

    # CLOSE
    builder.position_at_end(dyn_array_init_exit)
    builder.ret_void()


def dynamic_array_double_if_full(self, dyn_array_ptr, array_type):
    # START
    dyn_array_double_capacity_if_full_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr])
    dyn_array_double_capacity_if_full = ir.Function(self.module, dyn_array_double_capacity_if_full_type, '{}_array_double_capacity_if_full'.format(array_type))
    dyn_array_double_capacity_if_full_entry = dyn_array_double_capacity_if_full.append_basic_block('entry')
    builder = ir.IRBuilder(dyn_array_double_capacity_if_full_entry)
    self.builder = builder
    dyn_array_double_capacity_if_full_exit = dyn_array_double_capacity_if_full.append_basic_block('exit')
    dyn_array_double_capacity_block = dyn_array_double_capacity_if_full.append_basic_block('double_capacity')
    builder.position_at_end(dyn_array_double_capacity_if_full_entry)
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(dyn_array_double_capacity_if_full.args[0], array_ptr)

    # BODY
    size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
    size_val = builder.load(size_ptr)

    capacity_ptr = builder.gep(builder.load(array_ptr), [zero_32, one_32], inbounds=True)
    capacity_val = builder.load(capacity_ptr)

    data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

    compare_size_to_capactiy = builder.icmp_signed(GREATER_THAN_OR_EQUAL_TO, size_val, capacity_val)

    builder.cbranch(compare_size_to_capactiy, dyn_array_double_capacity_block, dyn_array_double_capacity_if_full_exit)

    builder.position_at_end(dyn_array_double_capacity_block)

    capacity_val = builder.mul(capacity_val, two)
    builder.store(capacity_val, capacity_ptr)
    capacity_val = builder.load(capacity_ptr)
    size_of = builder.mul(capacity_val, eight)

    data_ptr_8 = builder.bitcast(builder.load(data_ptr), type_map[INT8].as_pointer())
    re_alloc = builder.call(self.module.get_global('realloc'), [data_ptr_8, size_of])
    re_alloc = builder.bitcast(re_alloc, type_map[array_type].as_pointer())
    builder.store(re_alloc, data_ptr)

    builder.branch(dyn_array_double_capacity_if_full_exit)

    # CLOSE
    builder.position_at_end(dyn_array_double_capacity_if_full_exit)
    builder.ret_void()


def dynamic_array_append(self, dyn_array_ptr, array_type):
    # START
    dyn_array_append_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr, type_map[array_type]])
    dyn_array_append = ir.Function(self.module, dyn_array_append_type, '{}_array_append'.format(array_type))
    dyn_array_append_entry = dyn_array_append.append_basic_block('entry')
    builder = ir.IRBuilder(dyn_array_append_entry)
    self.builder = builder
    dyn_array_append_exit = dyn_array_append.append_basic_block('exit')
    builder.position_at_end(dyn_array_append_entry)
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(dyn_array_append.args[0], array_ptr)
    value_ptr = builder.alloca(type_map[array_type])
    builder.store(dyn_array_append.args[1], value_ptr)

    # BODY
    builder.call(self.module.get_global('{}_array_double_capacity_if_full'.format(array_type)), [builder.load(array_ptr)])

    size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
    size_val = builder.load(size_ptr)

    size_val = builder.add(size_val, one)
    builder.store(size_val, size_ptr)

    data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

    data_element_ptr = builder.gep(builder.load(data_ptr), [size_val], inbounds=True)

    builder.store(builder.load(value_ptr), data_element_ptr)

    builder.branch(dyn_array_append_exit)

    # CLOSE
    builder.position_at_end(dyn_array_append_exit)
    builder.ret_void()


def dynamic_array_get(self, dyn_array_ptr, array_type):
    # START
    dyn_array_get_type = ir.FunctionType(type_map[array_type], [dyn_array_ptr, type_map[INT]])
    dyn_array_get = ir.Function(self.module, dyn_array_get_type, '{}_array_get'.format(array_type))
    dyn_array_get_entry = dyn_array_get.append_basic_block('entry')
    builder = ir.IRBuilder(dyn_array_get_entry)
    self.builder = builder
    dyn_array_get_exit = dyn_array_get.append_basic_block('exit')
    dyn_array_get_index_out_of_bounds = dyn_array_get.append_basic_block('index_out_of_bounds')
    dyn_array_get_is_index_less_than_zero = dyn_array_get.append_basic_block('is_index_less_than_zero')
    dyn_array_get_negative_index = dyn_array_get.append_basic_block('negative_index')
    dyn_array_get_block = dyn_array_get.append_basic_block('get')
    builder.position_at_end(dyn_array_get_entry)
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(dyn_array_get.args[0], array_ptr)
    index_ptr = builder.alloca(type_map[INT])
    builder.store(dyn_array_get.args[1], index_ptr)

    # BODY
    index_val = builder.load(index_ptr)
    size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
    size_val = builder.load(size_ptr)

    compare_index_to_size = builder.icmp_signed(GREATER_THAN_OR_EQUAL_TO, index_val, size_val)

    builder.cbranch(compare_index_to_size, dyn_array_get_index_out_of_bounds, dyn_array_get_is_index_less_than_zero)

    builder.position_at_end(dyn_array_get_index_out_of_bounds)
    self.print_string('Array index out of bounds')
    builder.call(self.module.get_global('exit'), [one_32])
    builder.unreachable()

    builder.position_at_end(dyn_array_get_is_index_less_than_zero)

    compare_index_to_zero = builder.icmp_signed(LESS_THAN, index_val, zero)

    builder.cbranch(compare_index_to_zero, dyn_array_get_negative_index, dyn_array_get_block)

    builder.position_at_end(dyn_array_get_negative_index)

    add = builder.add(size_val, index_val)
    builder.store(add, index_ptr)
    builder.branch(dyn_array_get_block)

    builder.position_at_end(dyn_array_get_block)

    data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

    add_1 = builder.add(one, index_val)
    builder.store(add_1, index_ptr)
    index_val = builder.load(index_ptr)
    data_element_ptr = builder.gep(builder.load(data_ptr), [index_val], inbounds=True)

    builder.branch(dyn_array_get_exit)

    # CLOSE
    builder.position_at_end(dyn_array_get_exit)
    builder.ret(builder.load(data_element_ptr))


def dynamic_array_set(self, dyn_array_ptr, array_type):
    # START
    dyn_array_set_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr, type_map[INT], type_map[array_type]])
    dyn_array_set = ir.Function(self.module, dyn_array_set_type, '{}_array_set'.format(array_type))
    dyn_array_set_entry = dyn_array_set.append_basic_block('entry')
    builder = ir.IRBuilder(dyn_array_set_entry)
    self.builder = builder
    dyn_array_set_exit = dyn_array_set.append_basic_block('exit')
    dyn_array_set_index_out_of_bounds = dyn_array_set.append_basic_block('index_out_of_bounds')
    dyn_array_set_is_index_less_than_zero = dyn_array_set.append_basic_block('is_index_less_than_zero')
    dyn_array_set_negative_index = dyn_array_set.append_basic_block('negative_index')
    dyn_array_set_block = dyn_array_set.append_basic_block('set')
    builder.position_at_end(dyn_array_set_entry)
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(dyn_array_set.args[0], array_ptr)
    index_ptr = builder.alloca(type_map[INT])
    builder.store(dyn_array_set.args[1], index_ptr)
    value_ptr = builder.alloca(type_map[array_type])
    builder.store(dyn_array_set.args[2], value_ptr)

    # BODY
    index_val = builder.load(index_ptr)

    size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)
    size_val = builder.load(size_ptr)

    compare_index_to_size = builder.icmp_signed(GREATER_THAN_OR_EQUAL_TO, index_val, size_val)

    builder.cbranch(compare_index_to_size, dyn_array_set_index_out_of_bounds, dyn_array_set_is_index_less_than_zero)

    builder.position_at_end(dyn_array_set_index_out_of_bounds)
    self.print_string('Array index out of bounds')
    builder.call(self.module.get_global('exit'), [one_32])
    builder.unreachable()

    builder.position_at_end(dyn_array_set_is_index_less_than_zero)

    compare_index_to_zero = builder.icmp_signed(LESS_THAN, index_val, zero)

    builder.cbranch(compare_index_to_zero, dyn_array_set_negative_index, dyn_array_set_block)

    builder.position_at_end(dyn_array_set_negative_index)

    add = builder.add(size_val, index_val)
    builder.store(add, index_ptr)
    builder.branch(dyn_array_set_block)

    builder.position_at_end(dyn_array_set_block)

    data_ptr = builder.gep(builder.load(array_ptr), [zero_32, two_32], inbounds=True)

    add_1 = builder.add(one, index_val)
    builder.store(add_1, index_ptr)
    index_val = builder.load(index_ptr)

    data_element_ptr = builder.gep(builder.load(data_ptr), [index_val], inbounds=True)

    builder.store(builder.load(value_ptr), data_element_ptr)

    builder.branch(dyn_array_set_exit)

    # CLOSE
    builder.position_at_end(dyn_array_set_exit)
    builder.ret_void()


def dynamic_array_length(self, dyn_array_ptr, array_type):
    # START
    dyn_array_length_type = ir.FunctionType(type_map[INT], [dyn_array_ptr])
    dyn_array_length = ir.Function(self.module, dyn_array_length_type, '{}_array_length'.format(array_type))
    dyn_array_length_entry = dyn_array_length.append_basic_block('entry')
    builder = ir.IRBuilder(dyn_array_length_entry)
    self.builder = builder
    builder.position_at_end(dyn_array_length_entry)
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(dyn_array_length.args[0], array_ptr)

    size_ptr = builder.gep(builder.load(array_ptr), [zero_32, zero_32], inbounds=True)

    # CLOSE
    builder.ret(builder.load(size_ptr))

# TODO: add the following functions for dynamic array
# extend(iterable)
# insert(item, index)
# remove(item)
# pop([index])
# clear()
# index(x[, start[, end]])
# count(item)
# sort(key=None, reverse=False)
# reverse()


def define_print(self, dyn_array_ptr):
    # START
    func_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr])
    func = ir.Function(self.module, func_type, 'print')
    entry_block = func.append_basic_block('entry')
    builder = ir.IRBuilder(entry_block)
    self.builder = builder
    builder.position_at_end(entry_block)
    zero_length_check_block = func.append_basic_block('zero_length_check')
    non_zero_length_block = func.append_basic_block('non_zero_length')
    cond_block = func.append_basic_block('check_if_done')
    body_block = func.append_basic_block('print_it')
    exit_block = func.append_basic_block('exit')
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(func.args[0], array_ptr)

    # BODY
    builder.position_at_end(entry_block)
    length = builder.call(self.module.get_global('int_array_length'), [builder.load(array_ptr)])
    builder.branch(zero_length_check_block)

    builder.position_at_end(zero_length_check_block)
    cond = builder.icmp_signed(LESS_THAN_OR_EQUAL_TO, zero, length)
    builder.cbranch(cond, non_zero_length_block, exit_block)

    builder.position_at_end(non_zero_length_block)
    position_ptr = builder.alloca(type_map[INT])
    builder.store(zero, position_ptr)
    builder.branch(cond_block)

    builder.position_at_end(cond_block)
    cond = builder.icmp_signed(LESS_THAN, builder.load(position_ptr), length)
    builder.cbranch(cond, body_block, exit_block)

    builder.position_at_end(body_block)
    char = builder.call(self.module.get_global('int_array_get'), [builder.load(array_ptr), builder.load(position_ptr)])
    builder.call(self.module.get_global('putchar'), [char])
    add_one = builder.add(one, builder.load(position_ptr))
    builder.store(add_one, position_ptr)
    builder.branch(cond_block)

    # CLOSE
    builder.position_at_end(exit_block)
    builder.call(self.module.get_global('putchar'), [ten])
    builder.ret_void()


def define_int_to_str(self, dyn_array_ptr):
    # START
    func_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr, type_map[INT]])
    func = ir.Function(self.module, func_type, 'int_to_str')
    entry_block = func.append_basic_block('entry')
    builder = ir.IRBuilder(entry_block)
    self.builder = builder
    builder.position_at_end(entry_block)
    exit_block = func.append_basic_block('exit')
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(func.args[0], array_ptr)
    n_addr = builder.alloca(type_map[INT])
    builder.store(func.args[1], n_addr)
    x_addr = builder.alloca(type_map[INT])

    # BODY
    fourtyeight = ir.Constant(type_map[INT], 48)

    div_ten = builder.sdiv(builder.load(n_addr), ten)
    greater_than_zero = builder.icmp_signed(GREATER_THAN, div_ten, zero)
    mod_ten = builder.srem(builder.trunc(builder.load(n_addr), type_map[INT]), ten)
    builder.store(mod_ten, x_addr)
    with builder.if_then(greater_than_zero):
        builder.call(self.module.get_global('int_to_str'), [builder.load(array_ptr), div_ten])

    char = builder.add(fourtyeight, builder.load(x_addr))
    builder.call(self.module.get_global('int_array_append'), [builder.load(array_ptr), char])
    builder.branch(exit_block)

    # CLOSE
    builder.position_at_end(exit_block)
    builder.ret_void()


def define_bool_to_str(self, dyn_array_ptr):
    # START
    func_type = ir.FunctionType(type_map[VOID], [dyn_array_ptr, type_map[BOOL]])
    func = ir.Function(self.module, func_type, 'bool_to_str')
    entry_block = func.append_basic_block('entry')
    builder = ir.IRBuilder(entry_block)
    self.builder = builder
    exit_block = func.append_basic_block('exit')
    array_ptr = builder.alloca(dyn_array_ptr)
    builder.store(func.args[0], array_ptr)

    # BODY
    equalszero = builder.icmp_signed(EQUALS, func.args[1], ir.Constant(type_map[BOOL], 0))
    dyn_array_append = self.module.get_global('int_array_append')

    with builder.if_else(equalszero) as (then, otherwise):
        with then:
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 102)])
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 97)])
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 108)])
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 115)])
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 101)])
        with otherwise:
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 116)])
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 114)])
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 117)])
            builder.call(dyn_array_append, [builder.load(array_ptr), ir.Constant(type_map[INT], 101)])

    builder.branch(exit_block)

    # CLOSE
    builder.position_at_end(exit_block)
    builder.ret_void()
