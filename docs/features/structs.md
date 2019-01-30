**Structs** fill a similar role to Python's dataclasses, which you can describe as "mutable namedtuples with defaults", but they're stricter in the sense that **they're not disguised classes**, you can not define methods or other class-specific behaviour, but they can still be extended by overloading operators and they are still defined as a type in Lesma. Struct members can be accessed using the dot `.`.

All the fields of a struct are required arguments on initialization unless a default is provided.

## Example
```py
struct Circle
	radius: int
	x: int
	y: int = 4

cir: Circle = Circle(radius=5, x=2)

print(cir.radius)  # Members of a struct are accessed using a dot.
```