# Examples

Everyone likes some short bits of code to taste the syntax and semantics.

For more in depth code examples and explaination, check the feature pages.

!!! warning
	Some of the examples shown below are non-functional. Please consult the rest of the documentation for more information

```py
# Hello World
print('Hello World')
print('🍌')
print('夜のコンサートは最高でした。')

a_number: int # Initialize an Integer

# Binary, Hex and Octal numbers supported
bin_num = 0b101010
octo_num = 0o1272
hex_num = 0x1272

π: float = 3.14 # Support for utf-8 variable names
number = 23 # Type Inference, int in this case
number = number + 5 // 2 ^ 3 # Number operations
number+=5 # Operating Assignment

still_inf = inf - 999999 # Still infinity

question = 'what\'s going on' # Escaping

things = [1, 2, 3] # List, mutable
same_things = 0..4 # Same as before, defaults as a list
other_things = (1.5, 9.5) # Tuple, immutable
stuff = {'first_name': 'Samus', 'last_name': 'Aran'} # Dictionary
other_stuff: list<int> = [] # Empty Array of ints

print(things[1 + 1])

if number > 23
	print('greater than 23')
else if number == 23
	print('equals 23')
else
	print('less than 23')

if false \ # Continuing statement onto next line
	and true

	print('They are not the same')

for x in 0..40 # For loop using a range
	print(x * 2)

for item in things # Iterate over objects
	print(item)

while number > 1
	number -= 1
	print(number)

if 2 in things
	print('yes')

if 2 not in things
	print('no')

odd_even = 1

# No implicit fallthrough (in other words, implicit break)
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

# Function Return notation
def fib(n: int) -> int
	a = 0
	b = 1
	for _ in 0..n
		prev_a = a
		a = b
		b = prev_a + b
	return a

def fib_rec(n: int) -> int
	if n == 0
		return 0
	if n == 1
		return 1
	return fib_rec(n - 1) + fib_rec(n - 2)

def factorial(n: int = 5) -> int
	if n <= 1
		return 1
	return n * factorial(n - 1)

# Assign anonymous function to a variable
myfunc = def (x: int, y: int) -> int
	if x > y
		return x + y
	else
		return x * y

print(myfunc(2, 3))
bar = myfunc
print(bar(3,4))

# Type operators using `as` and `is`
my_var: int128 = 101
my_another_var: int64 = my_var as int64

if my_var is int64
	print("That's not true")
else if my_var as int64 is int64
	print("That works")

# Type Declaration
type fInt = func<int> -> int

def do_stuff(x: int, callback: fInt) -> int
	x ^= 2
	x = callback(x)
	return x

num = do_stuff(3,
	def (y: int) -> int
		y += 7
		return y
)

print(
	num
)

# Closure
def start_at(x: int) -> fInt
	def increment_by(y: int) -> int
		return x + y
	return increment_by

start_at_5 = start_at(5)
start_at_27 = start_at(27)

print(start_at_5(4))
print(start_at_27(15))

# User input
age: int = input('How old are you?')

# String Interpolation
print('Wow! You are {age} years old?!')

# Operator Overloading
def operator - (x: int, y:int) -> int  # Two parameters overloads binary operations
	return x + 3

def operator - (x: int) -> int  # One parameters overloads binary operations
	return 0 - x + 1

# Extern functions (FFI)
def extern abs(x: int) -> int # from C's stdlib

print(abs(-5.0 as int)) # ints are int64 by default in Lesma, they're int32 in C

# or you can just let Lesma convert between "compatible" types such as numbers
print(abs(-5.0))

# Named parameters and defaults
def optional_params(x: int, y: int32 = 5, z: double = 9) -> int
	# Lesma takes care of casting the return type between "compatible" types
	return x + z

optional_params(5, z=11)

def defer_demo()
    defer print("World!")
    print("Hello")

defer_demo() # prints Hello World!

# Enums
enum Color
	GREEN
	RED
	BLUE
	YELLOW

x: Colors = Color.GREEN
print(x == Color.GREEN)

# Structs
struct Circle
	radius: int
	x: int
	y: int = 4

cir: Circle = Circle(radius=5, x=2)

print(cir.radius)

# Classes
class Vehicle
	# Constructor
	def new(year: int, color: str)
		self.year = year
		self._color = color

# Inheritance
class Car: Vehicle
	def new(year: int, color='green', hatchback=false)
		self.hatchback = hatchback
		super.Vehicle(year, color)

	def print_year() -> void
		print('This car was made in {self.year}')

ford = Car(1992)

print(ford.hatchback)
ford.print_year()
```
