# TODO

## Fixes
- [x] Fix type declaration for lists and tuples
- [x] Fix input function
- [x] Fix not being able to return user-defined structs and classes
- [x] Fix not being able to overload operators on user-defined structs and classes
- [ ] Fix base unary operators being applied before user defined ones
- [x] Fix structs and classes types not being implicitly defined on assignment
- [x] Fix pytest for windows
- [ ] Fix unicode on windows bash

## Improvements
- [ ] Improve warning messages
- [ ] Add indentation related errors
- [x] Add docs for as and is
- [x] Add docs for classes and structs
- [ ] Add docs for mixed arithmetic
- [ ] Remove clang as a dependency
- [ ] Move error messages from source files to typechecker
- [x] Fix array types not working on empty lists
- [x] Catch struct/class used parameters that are not initialized
- [ ] Add support for functions with same name but different parameters
- [ ] Fix local - global variable behaviour, currently there's an implicit main func
- [x] Allow default values for struct and class fields
- [ ] Use dataclasses and static typing as much as possible in source code
- [x] Allow any type for lists/tuples (currently only int)
- [ ] String/Lists are currently unsupported on: input function, operators, etc.
- [ ] Find a way to use pointers and null for FFI but restrict or not allow it in normal Lesma
- [x] Add basic operators for Enums

## Features
- [x] Implement Tuples
- [x] Implement Classes
- [ ] Implement Class inheritance
- [ ] Implement Dictionary
- [ ] Implement 'in' as a boolean result
- [x] Implement anonymous functions
- [ ] Implement Closure
- [ ] Implement string interpolation
- [x] Implement Enums
- [ ] Implement lambda functions
- [x] Implement inf
- [x] Implement defer keyword
- [x] Implement fallthrough and change switch's behaviour