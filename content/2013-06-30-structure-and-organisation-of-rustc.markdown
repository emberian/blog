Title: Structure and organisation of rustc
Date: 2013-06-30 16:03
Category: rust

*This is the second part of a planned series about `rustc`, the Rust compiler*

This post is going to discuss the structure and organisation of `rustc`,
covering the major moving parts and how they interact. I'll start, of course,
where it starts, and ending, of course, where it ends.

<!-- more -->

`rustc` is a fairly large, complex beast. Unless otherwise mentioned, all
paths are relative to `src/librustc`. If you're unfamiliar with Rust, a
"crate" is a compilation unit: a library or an executable.

## Beginning

The entry point, `run_compiler` in `rustc.rs`, does argument parsing, using
`extra::getopts` and calls into the driver, in `driver/driver.rs`, which
coordinates the various pieces of the compiler and the rest of the argument
parsing. The key data structure here is the `Session`, which you can find
(along with a bunch of other things like the option context) in
`driver/session.rs`. Back to the driver, the function `compile_input` is where
most of the magic happens. This function runs all the various passes over the
crate. It starts with parsing and macro expansion and moves onto various
static analysis of the code to make sure it is correct, finally generating
LLVM IR (intermediate representation), running LLVM optimizations, and linking
the final binary.

## An interlude

If you're not familiar with compilers, you might find this process a
labyrinthine fractal of complexity. Which it is, don't get me wrong. But the
various pieces of the rust compiler are fairly well separated, even if they
are complex. The basic structure of a compiler is operations on a tree data
structure representing the crate called an AST or Abstract Syntax Tree. An AST
is the output of parsing, and everything in the compiler is transforms or
analysis of this tree. Once everything is done, it takes this AST and
translates it into LLVM IR. This is probably the most hairy part of the
compiler, and it lives in `middle/trans`. LLVM IR is a representation of code
that the LLVM library can operate on to optimize and generate native machine
code. LLVM does most of the heavy lifting that a traditional compiler would
need to do (optimization and codegen), so the rest of `rustc` is largely
dedicated to actually dealing with Rust programs.

## Parsing + expansion

Parsing and macro expansion happen in `src/libsyntax`, so all paths in this
section will be relative to that. This corresponds to `phase_1_parse_input`
and `phase_2_configure_and_expand`. Phase 1 does the parsing, and results in
an AST. If you want, you can look into `parse/parser.rs` for the
`parse_crate_mod` method. Very rarely will one have to modify the parser. The
most important part of the parser, from an outsider's perspective, is in
`codemap.rs`. The codemap has the concept of a "span", which is a piece of
source code, represented by a start and an end. Whenever you see an error and
a squiggly line underneath where the error happenes, that is the result of a
span. Almost everything in the AST has a span.

After phase 1 comes, of course, phase 2. Phase 2 is what does macro expansion,
deriving implementations, and removal of items which are conditionally
included with the `cfg` attribute. This all happens in the `ext` directory.
Personally I haven't poked around too much at how macros work, but things to
note are `cfg.rs`, `asm.rs`, `ifmt.rs`, and the `deriving` directory. These do
`cfg!`, `asm!`, `format!` (and friends), and `#[deriving(...)]`,
respectively.

If you're curious how a syntax extension works, `env.rs` is a good example. In
the `expand_env` function, it takes the syntax extension context (cx), a
span of the macro invocation, and the "token tree" that the macro was invoked
with.  When you do `foo!(....)`, the `....` is the token tree. It checks the
structure of the token tree (it expects either one or two arguments), and then
returns the environment variable referenced by constructing an `ast::Expr`,
using the ExtCtxt to mark that the expression came from the given span. This
is so the compiler can track which span a piece of macro-generated code
initially came from, for better error reporting.

You might notice that phase 2 actually runs the configuration step twice. This
is so that macros that expand to items with a `cfg` attribute also get removed
from the final output.

## Analysis

Phase 3, the analysis phases, is the real meat of rustc. All of this code
lives in `middle`. The most important passes are probably typeck, the type
checker; resolve, the name resolver; borrowck, the borrow checker; and lint,
the lint runner. Not to say the other passes aren't important, but they're
less frequently worked or worried about by mere mortals such as myself.

## Trans(lation)

trans is the part of the compiler that takes the AST from syntax as
well as the tables created by analysis and outputs LLVM IR. All of this
happens in `middle/trans`. There is a lot of code, and I've never actually
been able to figure out which piece generates what.

## Conclusion

That's my basic overview of how the compiler is structured. If you want
something added, or as questions get asked, I'll fill in more information. The
analysis and trans sections are sparse as I've little experience with them.
