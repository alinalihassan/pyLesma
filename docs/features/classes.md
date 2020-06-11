**Classes** are objects that bundle fields and methods to provide additional functionality that you can further use as a type for any variable, which can then be further expanded using operator overloading and other type-specific behaviour. Classes members can be accessed using a dot `.`.

If a Class constructor is not provided, a built-in constructor is then created, for which all the fields of a class are required arguments on initialization unless a default is provided.

## Example
```py
class Circle
	radius: int
	x: int
	y: int = 4

cir: Circle = Circle(radius=5, x=2)

print(cir.radius)

class Vehicle
	year: int
	color: str

	# Constructor
	def new(year: int, color: str)
		this.year = year
		this.color = color  

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