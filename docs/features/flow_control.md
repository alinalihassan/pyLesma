## While loops 

The expression is required to be of type bool.

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

The expression is required to be of type bool.

```py
if true
	print("Then do this")
else if true
	print("Never reached")
else
	print("Not even")
```

## Switch statement

**Every case needs a break** if you don't want to continue the flow to the next case, only the last case doesn't need a break, this means that the default would still need one if it's not the last case of the switch statement.
```py
coins = 5

switch coins
	case 1
		print('You got only one?')
	case 2
		print('Now we\'re talking')
		break
	default
		print(coins)
		print("You got a lot of coins in there")
	case 3
		print('I guess 3 is enough')
```