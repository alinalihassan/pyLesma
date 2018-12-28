Lesma offers the standard mathematical and boolean operators

## General/Specific operators

|Name|Symbol|Info|
|--|--|--|
|Dot| `.` | Member accessing operator|
|Range| `..` | Range defining operator|

## Mathematical operators
|Name|Symbol|Info|
|--|--|--|
|Plus| `+`| Mathematical plus|
|Minus| `-`| Mathematical minus or Unary minus|
|Multiplication| `*`| Mathematical multiplication|
|Divide| `/` |Mathematical division|
|Integer divide| `//` | Floor value or mathematical division|
|Modulo| `%` | Mathematical modulo|
|Power| `^` | Mathematical power|

## Boolean operators
|Name|Symbol|Info|
|--|--|--|
|And| `and`| And|
|Or| `or`| Or|
|Xor| `xor`| Exclusive Or|
|Is| `is` | Is type operator|
|As| `as` | Casting operator|
|Not| `not` | Not bool operator|
|Equals| `==` | Value equality|
|Not Equals| `!=` | Value inequality|
|Less Than| `<` | Less than value|
|Less Or Equal Than| `<=` | Less or equal than value|
|Greater Than| `<` | Greater than value|
|Greater Or Equal Than| `>=` | Greater or equal than value|

## Assignment operators

|Name|Symbol|Info|
|--|--|--|
|Assignment| `=`| Assignment of value to variable|
|Incremental Assignment| `++`| Increments the value of a variable|
|Decrement Assignment| `--`| Decrements the value of a variable|
|Addition Assignment| `+=`| Assignment of value plus current value assigned|
|Substraction Assignment| `-=`|Assignment of value minus current value assigned|
|Multiplication Assignment| `*=`|Assignment of value multiplied by the current value assigned|
|Division Assignment| `/=`|Assignment of value divided by the value assigned|
|Integer Division Assignment| `//=`|Assignment of value floor divided by current value assigned|
|Modulo Assignment| `%=`|Assignment of value modulo current value assigned|
|Power Assignment| `^=`|Assignment of assigned value to the power of value|


## Operator Overloading

Operators can be user-defined by defining functions using the keyword `operator` followed by the specified operator, and with one (for unary operators) or two (for binary operators)

```py
def operator + (x: int, y:int) -> int
	return 42

def operator - (x: int) -> int
	return 0

print(3+5)  # Prints 42
print(-20)  # Prints 0
```