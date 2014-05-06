Title: Parametric Polymorphism Declaration Syntax in Rust
Date: 2014-02-01 17:06
Category: Rust

Summary
=======

Change the following syntax:

```
struct Foo<T, U> { ... }
impl<T, U> Trait<T> for Foo<T, U> { ... }
fn foo<T, U>(...) { ... }
```

to:

```
forall<T, U> struct Foo { ... }
forall<T, U> impl Trait<T> for Foo<T, U> { ... }
forall<T, U> fn foo(...) { ... }
```

<!-- more -->

The Problem
===========

The immediate, and most pragmatic, problem is that in today's Rust one cannot
easily search for implementations of a trait. Why? `grep 'impl Clone'` is
itself not sufficient, since many types have parametric polymorphism. Now I
need to come up with some sort of regex that can handle this. An easy
first-attempt is `grep 'impl(<.*?>)? Clone'` but that is quite inconvenient to
type and remember. (Here I ignore the issue of tooling, as I do not find the
argument of "But a tool can do it!" valid in language design.)

A deeper, more pedagogical problem, is the mismatch between how `struct
Foo<...> { ... }` is read and how it is actually treated. The straightforward,
left-to-right reading says "There is a struct Foo which, given the types ...
has the members ...". This might lead one to believe that `Foo` is a single
type, but it is not. `Foo<int>` (that is, type `Foo` instantiated with type
`int`) is not the same type as `Foo<unit>` (that is, type `Foo` instantiated
with type `uint`). Of course, with a small amount of experience or a very
simple explanation, that becomes obvious.

Something less obvious is the treatment of functions. What does `fn
foo<...>(...) { ... }` say? "There is a function foo which, given types ...
and arguments ..., does the following computation: ..." is not very adequate.
It leads one to believe there is a *single* function `foo`, whereas there is
actually a single `foo` for every substitution of type parameters! This also
holds for implementations (both of traits and of inherent methods).

Another minor problem is that nicely formatting long lists of type parameters
or type parameters with many bounds is difficult.

Proposed Solution
=================

Introduce a new keyword, `forall`. This choice of keyword reads very well and
will not conflict with any identifiers in code which follows the [style
guide](https://github.com/mozilla/rust/wiki/Note-style-guide).

Change the following declarations from

```
struct Foo<T, U> { ... }
impl<T, U> Trait<T> for Foo<T, U> { ... }
fn foo<T, U>(...) { ... }
```

to:

```
forall<T, U> struct Foo { ... }
forall<T, U> impl Trait<T> for Foo<T, U> { ... }
forall<T, U> fn foo(...) { ... }
```

These read very well. "for all types T and U, there is a struct Foo ...", "for
all types T and U, there is a function foo ...", etc. These reflect that there
are in fact multiple functions `foo` and structs `Foo` and implementations of
`Trait`, due to monomorphization. It also allows for grepping for "impl
Trait".
