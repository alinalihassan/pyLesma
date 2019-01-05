# TODO

## Fixes
- [ ] Fix Type declaration not expecting square brackets (for lists)
- [ ] Fix input function
- [ ] Fix not being able to return user-defined structs and classes
- [ ] Fix not being able to overload operators on user-defined structs and classes
- [ ] Unicode doesn't print properly on Windows platforms
- [ ] Fix string and list type declaration not working
- [ ] Fix base unary operators being applied before user defined ones

## Improvements
- [ ] Allow any type for lists/tuples (currently only int)
- [ ] Allow more operators on different types such as strings
- [ ] Improve warning messages
- [ ] Add indentation related errors
- [x] Add docs for as and is
- [ ] Remove clang as a dependency
- [ ] Move error messages from source files to typechecker
- [ ] Fix array types not working and empty lists
- [ ] Catch struct/class used parameters that are not initialized
- [ ] Add support for functions with same name but different parameters
- [ ] Fix local - global variable behaviour, currently there's an implicit main func

## Features
- [ ] Implement Null (maybe someday)
- [ ] Implement Tuples
- [ ] Implement Dictionary
- [ ] Implement 'in' as a boolean result
- [x] Implement anonymous functions
- [ ] Implement Closure
- [ ] Implement string interpolation
- [ ] Implement Enums
- [ ] Implement defer keyword
- [x] Implement fallthrough and change switch's behaviour