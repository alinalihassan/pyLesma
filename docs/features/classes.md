**Classes** are objects that bundle fields and methods to provide additional functionality that you can further use as a type for any variable, which can then be further expanded using operator overloading and other type-specific behaviour. Classes members can be accessed using a dot `.`.

Classes **require a constructor to be specified**.

## Example
```py
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