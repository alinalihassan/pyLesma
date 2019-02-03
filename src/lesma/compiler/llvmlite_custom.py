from llvmlite import ir

# Vectors


def extract_element(self, vector, idx, name=''):
    """
    Returns the value at position idx.
    """
    instr = ir.instructions.ExtractElement(self.block, vector, idx, name=name)
    self._insert(instr)
    return instr


def insert_element(self, vector, value, idx, name=''):
    """
    Returns vector with vector[idx] replaced by value.
    The result id undefined if the idx is larger or euqal the vector length.
    """
    instr = ir.instructions.InsertElement(self.block, vector, value, idx, name=name)
    self._insert(instr)
    return instr


def shuffle_vector(self, vector1, vector2, mask, name=''):
    """
    Concatenate vectors and extract elements into new vector.
    Elements in the combined vector are numbered left to right,
    starting at 0.
    """
    instr = ir.instructions.ShuffleVector(self.block, vector1, vector2, mask, name=name)
    self._insert(instr)
    return instr


class ExtractElement(ir.instructions.Instruction):
    def __init__(self, parent, vector, index, name=''):
        if not isinstance(vector.type, ir.types.VectorType):
            raise TypeError("vector needs to be of VectorType.")
        if not isinstance(index.type, ir.types.IntType):
            raise TypeError("index needs to be of IntType.")
        typ = vector.type.elementtype
        super(ExtractElement, self).__init__(parent, typ, "extractelement",
                                             [vector, index], name=name)

    def descr(self, buf):
        operands = ", ".join("{0} {1}".format(
                   op.type, op.get_reference()) for op in self.operands)
        buf.append("{opname} {operands}\n".format(
                   opname=self.opname, operands=operands))


class InsertElement(ir.instructions.Instruction):
    def __init__(self, parent, vector, value, index, name=''):
        if not isinstance(vector.type, ir.types.VectorType):
            raise TypeError("vector needs to be of VectorType.")
        if not value.type == vector.type.elementtype:
            raise TypeError("value needs to be of type %s not %s."
                            % (vector.type.elementtype, value.type))
        if not isinstance(index.type, ir.types.IntType):
            raise TypeError("index needs to be of IntType.")
        typ = vector.type
        super(InsertElement, self).__init__(parent, typ, "insertelement",
                                            [vector, value, index], name=name)

    def descr(self, buf):
        operands = ", ".join("{0} {1}".format(
                   op.type, op.get_reference()) for op in self.operands)
        buf.append("{opname} {operands}\n".format(
                   opname=self.opname, operands=operands))


class ShuffleVector(ir.instructions.Instruction):
    def __init__(self, parent, vector1, vector2, mask, name=''):
        if not isinstance(vector1.type, ir.types.VectorType):
            raise TypeError("vector1 needs to be of VectorType.")
        if vector2 != ir.Undefined:
            if vector2.type != vector1.type:
                raise TypeError("vector2 needs to be Undefined or of the same type as vector1.")
        if (not isinstance(mask, ir.Constant) or not
           isinstance(mask.type, ir.types.VectorType) or not
           mask.type.elementtype != ir.types.IntType(32)):
            raise TypeError("mask needs to be a constant i32 vector.")
        typ = ir.types.VectorType(vector1.type.elementtype, mask.type.count)
        index_range = range(vector1.type.count if vector2 == ir.Undefined else 2 * vector1.type.count)
        if not all(ii.constant in index_range for ii in mask.constant):
            raise IndexError("mask values need to be in {0}".format(index_range))
        super(ShuffleVector, self).__init__(parent, typ, "shufflevector",
                                            [vector1, vector2, mask], name=name)

    def descr(self, buf):
        buf.append("shufflevector {0} {1}\n".format(
                   ", ".join("{0} {1}".format(op.type, op.get_reference())
                             for op in self.operands),
                   self._stringify_metadata(leading_comma=True),
                   ))


class VectorType(ir.Type):
    """
    The type for vectors of primitive data items (e.g. "<4 x f32>").
    """

    def __init__(self, elementtype, count):
        self.elementtype = elementtype
        self.count = count

    @property
    def elements(self):
        return ir._Repeat(self.elementtype, self.count)

    def __len__(self):
        return self.count

    def _to_string(self):
        return "<%d x %s>" % (self.count, str(self.elementtype))

    def __eq__(self, other):
        if isinstance(other, VectorType):
            return self.elementtype == other.elementtype and self.count == other.count
        else:
            return False

    @property
    def intrinsic_name(self):
        return str(self)

    def __hash__(self):
        return hash(VectorType)

    def format_constant(self, value):
        itemstring = ", " .join(["{0} {1}".format(x.type, x.get_reference())
                                for x in value])
        return "<{0}>".format(itemstring)

    def wrap_constant_value(self, values):
        if not isinstance(values, (list, tuple)):
            if isinstance(values, ir.Constant):
                if values.type != self.elementtype:
                    raise TypeError("expected %s for %s"
                                    % (self.elementtype, values.type))
                return (values, ) * self.count
            return (ir.Constant(self.elementtype, values), ) * self.count
        if len(values) != len(self):
            raise ValueError("wrong constant size for %s: got %d elements"
                             % (self, len(values)))
        return [ir.Constant(ty, val) if not isinstance(val, ir.Value) else val
                for ty, val in zip(self.elements, values)]


ir.builder.extract_element = extract_element
ir.builder.insert_element = insert_element
ir.builder.shuffle_vector = shuffle_vector
ir.instructions.ExtractElement = ExtractElement
ir.instructions.InsertElement = InsertElement
ir.instructions.ShuffleVector = ShuffleVector
ir.ExtractElement = ExtractElement
ir.InsertElement = InsertElement
ir.ShuffleVector = ShuffleVector
ir.VectorType = VectorType
ir.types.VectorType = VectorType


# Int

Old_IntType = ir.types.IntType


class _IntType(Old_IntType):
    """
    The type for integers.
    """
    null = '0'
    _instance_cache = {}
    signed = True

    def __new__(cls, bits, signed=True):
        signature = (bits, signed)
        if 0 <= bits <= 128:
            try:
                return cls._instance_cache[signature]
            except KeyError:
                inst = cls._instance_cache[signature] = cls.__new(*signature)
                return inst
        return cls.__new(*signature)

    @classmethod
    def __new(cls, bits, signed):
        assert isinstance(bits, int) and bits >= 0
        self = super(Old_IntType, cls).__new__(cls)  # pylint: disable=E1003
        self.width = bits
        self.signed = signed
        self.v_id = f'{"i" if self.signed else "u"}{self.width}'
        return self


ir.types.IntType = _IntType
ir.IntType = _IntType
