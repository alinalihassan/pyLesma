Types are optional in Lesma, you can choose whether you specify them or not. Unspecified variable types are inferred at compile time.

The type must be either a user-defined alias, struct or class, or a built-in type such as:

- `Any`
- `Int`
- `Double`
- `Float`
- `Str`
- `Bool`
- `Array`
- `List`
- `Dict`
- `Range`


## Any

Any types can receive any kind of value, so it can receive any kind of value at any moment.

```py
x: any = 5
x = "Hey there"
```

!!! warning
    Any not implemented yet!

## Int
There are multiple types of ints available based on width and signed/unsigned. They can get a minimum of 8 bits width and a maximum of 128. If the width is not specified, it's by default 64.
  - Signed: `int`, `int8`, `int16`, `int32`, `int64`, `int128`
  - Unsigned: `uint`, `uint8`, `uint16`, `uint32`, `uint64`, `uint128`

```py
x: int = 5
x += 27
```
!!! info
	In Lesma, int and uint are by default 64 bits wide, and they will enlarge by themselves to 128 bits wide if needed. This is not the default behaviour if you specify the size yourself!

!!! warning
	Unsigned Integers not implemented yet

## Float
Double is floating-point real number.

```py
x: float = 0.5
```

## Double
Double is double-precision, floating-point, real number.

```py
x: double = 172312.41923
```

## Str
Str is Lesma's implementation of strings/char arrays. All Lesma strings support UTF-8.

```py
x: str = "Hello World!"
x = '🍌'
x = '夜のコンサートは最高でした。'
```

## Bool
Bools occupy only 1 bit, and can be either `true` or `false`.
```py
x: bool = true
```

## Array
Arrays are mutable by default, are declared using square paranthesis, have dynamic size, start from 0, and the members are accessed using the their index around square paranthesis.

```py
x = [1,2,3,4]
print(x[2])
```

!!! warning
	Arrays currently only support integers, no other types!

## List
Lists are like arrays, but immutable, and declared using round paranthesis.

```py
x = (1,5,20)
print(x[0])
```

!!! warning
	Lists are not yet implemented!

## Dict
Dictionaries are lists of key-value pairs (similar to hashmaps), and they're mutable

```py
x = {'first_name': 'Samus', 'last_name': 'Aran'}
print(x['first_name'])
```


!!! warning
	Dicts are not yet implemented!

## Range
Ranges are similar to Python's ranges, defined using `start..end` kind of syntax, and they're especially used for loops

```py
for x in 0..100
	print(x)
```

!!! warning
	Ranges can not currently be assigned to variables