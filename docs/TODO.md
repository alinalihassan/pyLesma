# TODO

## Fixes
- [x] Fix operator overloading going through an infinite loop if used in def function
- [x] Fix not being able to have user-defined type lists
- [ ] Fix parser error when using class fields/methods from a list
- [ ] Fix unicode on windows
- [ ] Fix type comparing `is` with lists and str

## Improvements
- [ ] Improve warning messages
- [ ] Add indentation related errors
- [ ] Remove clang as a dependency
- [ ] Add support for functions with same name but different parameters (name mangling)
- [ ] Fix local - global variable behaviour, currently there's an implicit main func
- [ ] String/Lists are currently unsupported on: input function, operators, etc.
- [ ] Find a way to use pointers and null for FFI but restrict or disallow it in normal Lesma
- [x] Allow functions to be used as return types
- [ ] Implement type checking for function return types
- [x] Allow ranges to be used as list expressions

## Features
- [x] Implement Class inheritance
- [ ] Implement multiple inheritance
- [ ] Implement Dictionary
- [ ] Implement 'in' as a boolean result
- [ ] Implement Closure
- [ ] Implement string interpolation
- [ ] Implement string operators

## Ecosystem
- [x] Implement a functional Visual Studio Code plugin
- [x] Implement syntax highlighting
- [ ] Implement autocomplete
- [ ] Implement go to definition, etc

## Documentation
- [ ] Add docs for mixed arithmetic
- [ ] Improve docs as much as possible for v0.5

## Source Code
- [ ] Use dataclasses and static typing as much as possible
- [ ] Move error messages from source files to typechecker