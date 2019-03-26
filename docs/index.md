<p align="center">
<img src="img/logo.png" height="180px" alt="Lesma Programming Language" title="Lesma Programming Language">
</p>

___
**Lesma** is a compiled, statically typed, imperative and object oriented programming language with a focus on expressiveness, elegancy, and simplicity, while not sacrificing on performance. The compiler is written in Python using LLVM as a backend.

Currently an early Work in Progress, and **many thanks** to [Ayehavgunne](https://github.com/Ayehavgunne) and his [Mythril](https://github.com/Ayehavgunne/Mythril) project for helping me by showcasing advanced examples of llvmlite and providing a base code.

**LESMA IS CURRENTLY BEING REWRITTEN IN C++ TO ACHIEVE THE PERFORMANCE STANDARDS ENVISIONED**

## Features
- **it's fast**, because it should be so, together with LLVM's state of the art optimizations, but it won't ever oblige you to make an extra effort from your side just for the sake of performance
- **it's compiled** both AOT and JIT, so you can finally decide if you just want to run it or compile it and distribute your project without dependencies, and because binary size also matters, a Hello World example would be around 8kb
- **it's statically typed** so you don't need to guess the type of the variable if your coworker didn't spend the time to use meaningful names and you can make use of compile-time checks, autocomplete and more
- **it's simple and expressive** because the code should be easily readable and it shouldn't make you guess what it does

## Influences
- Python
- Swift
- Typescript
- Lua
