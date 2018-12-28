# TODO

## Fixes
- [x] Fix **break** and **continue** not branching if the parent block is not the loop
- [x] Fix constant declaration not allowing types
- [ ] Fix Type declaration not expecting square brackets (for lists)
- [ ] Fix input function
- [x] Should not allow declaring the type to an existing variable
- [ ] Fix not being able to return user-defined structs and classes
- [ ] Fix not being able to overload operators on user-defined structs and classes
- [x] Fix Python error on empty input
- [ ] Unicode doesn't work on Windows platforms
- [ ] Fix string and list type declaration not working

## Improvements
- [ ] Allow any type for lists/tuples (currently only int)
- [ ] Allow any type for range (currently only int)
- [x] Allow any type for casting
- [x] Change casting syntax
- [ ] Allow more operators on different types such as strings
- [ ] Improve warning messages
- [ ] Add indentation related errors
- [ ] Add docs for as and is
- [ ] Remove clang as a dependency
- [x] Change from anonymous structs to identified (to allow proper struct types)

## Features
- [ ] Implement Null (maybe)
- [ ] Implement Tuples
- [ ] Implement Dictionary
- [ ] Implement Empty lists
- [ ] Implement 'in' as a boolean result
- [ ] Implement anonymous functions
- [x] Implement alias
- [ ] Implement Closure
- [ ] Implement string interpolation
- [ ] Implement Enums
- [x] Implement unsigned numbers
- [x] Implement operator overloading