## While loops 

The evaluation expression is required to be of type bool.

```py
x = 5
while(x < 10)
	x += 1
```

## For loops

They can be used to iterate over ranges or lists.

```py
for x in 0..10
	print(x)

my_list = [5,8,2]
for num in my_list
	print(x)
```

## If else statements

The evaluation expression is required to be of type bool.

```py
if true
	print("Then do this")
else if true
	print("Never reached")
else
	print("Not even")
```

## Switch statement

**No implicit fallthrough**, this means that in comparison with languages like C, the equivalent to a break statement is implicit in Lesma, therefore you need to specify the `fallthrough` keyword for the flow to go downstream to the other cases. Break statements are not allowed inside a switch statement.

```py
odd_even = 1

switch odd_even
	case 1
		fallthrough # Go to the next case
	case 3
		print('Odd number')
	default
		print("Any number")
		print(odd_even)
	case 4
		print('Even number')
```