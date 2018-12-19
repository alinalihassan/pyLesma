<p align="center">
<img src="docs/img/logo.png" height="180px" alt="Lesma Programming Language" title="Lesma Programming Language">
</p>

___
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/Version-0.1.0-brightgreen.svg)](https://github.com/hassanalinali/Lesma/blob/master/LICENSE.md)

**Lesma** is a compiled, gradually typed, imperative and object oriented programming language with a focused on expressiveness, elegancy, and simplicity, while not sacrificing on performance. The compiler is written in Python using LLVM as a backend.

Currently an early Work in Progress, and **many thanks** to [Ayehavgunne](https://github.com/Ayehavgunne) and his [Mythril](https://github.com/Ayehavgunne/Mythril) project for helping me by showcasing advanced examples of llvmlite and providing a base code.

## Features
- **it's fast**, because it should be so, but it won't ever oblige you to make an extra effort for the sake of performance 
- **it's compiled**, so you can finally distribute your projects without dependencies, and because binary size also matters, a Hello World example would be around 8kb
- **it's statically typed** so you don't need to guess the type of the variable if your coworker didn't spend the time to use meaningful names
- **it's simple and expressive** because the code should be easily readable and it shouldn't make you guess what it does

## Influences
- Python
- Typescript
- Lua
- Swift

## Installing
Currently if you want to test it, you need to build it on your own. In the future I might consider
publishing the binary to the Release Page.

## Documentation

- [Language Documentation](https://hassanalinali.github.io/Lesma)
- [Lesma code samples](https://hassanalinali.github.io/Lesma/examples/)

## Build

In order to build Lesma, you need to have [Python 3.7](https://www.python.org/) installed. Currently it's tested only on Linux. It makes use of clang to compile the resulting object file currently, so you need it installed, but only running a file doesn't require clang.

Clone the repo:
```bash
git clone https://github.com/hassanalinali/Lesma
```

Install the requirements
```bash
sudo apt install clang -y
pip install -r requirements.txt
```

Done! Now you can run the compiler or the interpreter, make a test file and hack your way around. Remember there are examples in the documentation.
```bash
python les.py run test.les
python les.py compile test.les
```

Or run the unit tests using nosetests
```bash
nosetests
```

For advanced usage or help, consult the CLI help menu
```bash
python les.py -h
```