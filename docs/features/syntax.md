- Whitespace is signifiant, indentation uses either Tabs or exactly 4 spaces
- Flow control statements, structs, classes and functions require an indentation
- Lesma's Checker will report any invalid syntax or unrecommended behaviour, such incompatible types for operations, or unused variables.
- `_` variable name is used as an ignored result, and is treated differently by the compiler (similar to golang)


```py
def do_that()
	pass

if true
	do_that()
else if false
	if true
		pass
	do_that()
else
	do_that()

for _ in 0..20
	do_that()

while(false)
	do_that()

struct thing
	x: int
	y: str
	z: double

class Example
	new(x: int)
		this.x = x
```

