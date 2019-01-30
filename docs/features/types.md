Types are optional in Lesma, you can choose whether you specify them or not. Unspecified variable types are inferred at compile time from the value of the assignment.

Operations between different types will either be casted to the larger type if the two types are compatible, or give an error otherwise. Two types are compatible if they are different sizes of the same group type (such as ints or floating points).

The type must be either a user-defined type, a struct, enum, class, or a built-in type.

!!! warning
	Types that are not specified are inferred, this is fundamentally different in comparison to dynamic types!

---

## Built-in Types

### Any

Any types can receive any kind of value, so it can receive any kind of value at any moment.

```py
x: any = 5
x = "Hey there"
```

!!! warning
    Any type is not implemented yet!

### Int
There are multiple types of ints available based on width and signed/unsigned. They can get a minimum of 8 bits width and a maximum of 128. If the width is not specified, it's by default 64.
  - Signed: `int`, `int8`, `int16`, `int32`, `int64`, `int128`
  - Unsigned: `uint`, `uint8`, `uint16`, `uint32`, `uint64`, `uint128`

```py
x: int = 5
x += 27

large_num: int128 = 5
```
!!! info
	In Lesma, int and uint are by default 64 bits wide, and they will enlarge by themselves to 128 bits wide if needed. This is not the default behaviour if you specify the size yourself!

### Float
Float is floating-point real number.

```py
x: float = 0.5
```

### Double
Double is double-precision floating-point real number.

```py
x: double = 172312.41923
my_inf = inf # inf is infinity as specified by IEEE 754
```

### Str
Str is Lesma's implementation of strings/char lists. All Lesma strings support UTF-8.

```py
x: str = "Hello World!"
x = '🍌'
x = '夜のコンサートは最高でした。'
```

### Bool
Bools occupy only 1 bit, and can be either `true` or `false`.
```py
x: bool = true
```

### List
Lists are mutable by default, are declared using square paranthesis, have dynamic size, start from 0, and the members are accessed using the their index around square paranthesis. The element can be declared between square braces. If the type is omitted, the list will have the type of the elements contained. 

```py
x = [1,2,3,4]
y: list[double] = [1.5,5.5]
print(x[2])
```

### Tuple
Tuples are like lists, but immutable, and declared using round paranthesis.
The element type can be declared between square braces. If the type is omitted, the list will have the type of the elements contained. 

```py
x = (1,5,20)
y: tuple[double] = (1.5,5.5)
print(x[0])
```

### Dict
Dictionaries are lists of key-value pairs (similar to hashmaps), and they're mutable

```py
x = {'first_name': 'Samus', 'last_name': 'Aran'}
print(x['first_name'])
```


!!! warning
	Dicts are not yet implemented!

### Range
Ranges are similar to Python's ranges, defined using `start..end` kind of syntax, and they're especially used for loops

```py
for x in 0..100
	print(x)
```

!!! warning
	Ranges can not currently be assigned to variables

----

### Func
Lesma supports first class functions, meaning that variables can be assigned functions, and the type func is meant to annotate the type of the function.
Parameter types are included between square braces `[]` separated by comma `,`, and the return type with arrow `->`.

```py
x: func[int, int] -> int = def (x: int, y: int) -> int
	if x > y
		return x + y
	else
		return x * y

y = def (x: int, y: int) -> int
	if x > y
		return x + y
	else
		return x * y

z: func = def()
    print(5)
```

### Void
Void is used only for function return types and are used to illustrate that the function does not return a value. If the return type of a function is omitted, void will be used by default. 

```py
def example() -> void
	pass

def example2()	# Here the return type is omitted
	pass

```

## Type Operations

### Is
`Is` binary operator checks if the left operand's type matches the right operand and returns a bool as a result

```py
x: int = 5
print(x is int)
```

### As
`As` binary operator casts the left operand to the right operand type and returns the casted value

```py
x: float = 5.5
print(x as int) # Should print 5
```
