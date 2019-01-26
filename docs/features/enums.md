**Enums** (enumerations) are a set of symbolic names bound to unique, constant values. Enum members can be accessed using the dot `.`.

## Example
```py
enum Color
    Red
    White

white: Color = Color.White # Enum members are accessed using a dot
red: Color = Color.Red
print(white != red)
```