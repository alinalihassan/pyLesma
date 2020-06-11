<p align="center">
<img src="docs/img/logo.svg" height="180px" alt="Lesma Programming Language" title="Lesma Programming Language">
<br><b style="font-size: 24px;">Lesma</b>
</p>

___
[![License: GPL v3](https://img.shields.io/badge/license-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-0.4.1-brightgreen.svg)](https://github.com/hassanalinali/Lesma/blob/master/LICENSE.md)
[![CircleCI](https://circleci.com/gh/hassanalinali/Lesma/tree/master.svg?style=shield)](https://circleci.com/gh/hassanalinali/Lesma/tree/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/90fcc06be70d4dd98f54f1bb2713d70c)](https://www.codacy.com/app/hassanalinali/Lesma?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hassanalinali/Lesma&amp;utm_campaign=Badge_Grade)

**Lesma** is a compiled, statically typed, imperative and object-oriented programming language with a focus on expressiveness, elegancy, and simplicity, while not sacrificing on performance. 

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

## Installing
You can pick up the latest release in [**Releases**](https://github.com/hassanalinali/Lesma/releases) and start using it. Lesma is currently being tested and provides binaries only for Unix. Compatibility between operating systems and architectures is not hard to achieve, but simply not a priority at the moment. 

Windows is also supported but you need to do additional work if you want to compile Lesma code (need to install clang, but this is not properly tested at the moment) and there are issues with Unicode characters, but all the tests pass and everything else seems to work.

In the case that your platform is not oficially supported, you need to build it on your own.

## Documentation

- [Language Documentation](https://hassanalinali.github.io/Lesma)
- [Lesma code samples](https://hassanalinali.github.io/Lesma/examples/)

## Build

In order to build Lesma, you need to have at least [Python 3.5](https://www.python.org/) installed. It's currently tested only on Linux. It makes use of clang to compile the resulting object file currently, so you need it installed, but only running a file doesn't require clang.

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
python src/les.py run test.les
python src/les.py compile test.les
```

Or install pytest and run the unit tests yourself
```bash
pytest
```

For advanced usage or help, consult the CLI help menu
```bash
python src/les.py -h
```