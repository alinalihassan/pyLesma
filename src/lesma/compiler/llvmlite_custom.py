from llvmlite import ir

Old_IntType = ir.types.IntType
Old_IdentifiedStructType = ir.IdentifiedStructType


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


class _IdentifiedStructType(Old_IdentifiedStructType):
    def gep(self, i):
        """
        Resolve the type of the i-th element (for getelementptr lookups).
        *i* needs to be a LLVM constant, so that the type can be determined
        at compile-time.
        """
        if not isinstance(i.type, ir.IntType):
            raise TypeError(i.type)
        
        return self.elements[i.constant]

    def set_body(self, elems):
        if not self.is_opaque:
            raise RuntimeError("{name} is already defined".format(
                name=self.name))
    
        if not isinstance(elems, list) and not isinstance(elems, tuple):
            self.elements = tuple(elems)
        else:
            self.elements = elems



ir.types.IntType = _IntType
ir.IntType = _IntType
ir.types.IdentifiedStructType = _IdentifiedStructType
ir.IdentifiedStructType = _IdentifiedStructType