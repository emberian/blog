Title: "TBAA Revisited"
Date: 2014-04-04 02:32
Category: Rust

My original [post about alias analysis][orig] had some issues, which I clarify
and modify the algorithm to handle.

<!-- more -->

The Problem
-----------

There are two major issues with the algorithm I described. The first is that
LLVM's TBAA is not flow-sensitive. This means that given two non-aliasing
pointers, it assumes that they *never*, ever impose or imposed a memory
dependence on each other. On the other hand, Rust's borrowing rules *are* flow
sensitive. In practice, this means that loads and stores with non-aliasing
TBAA tags can be freely reordered with respect to each other. I could not
convince LLVM to misoptimize some simple examples of TBAA, but it supposedly
does some extra analysis to make sure TBAA-annotated load/stores don't actually
alias so that incorrect C programs don't misoptimize. This was pointed out [by
a kind soul on reddit][reddit].

Another problem is that the algorithm ignores types which have an unsafe
interior. The `Unsafe<T>` type can be used to get a mutable reference out of
an immutable one. The `RefCell` type wraps this to provide the same semantics
that the borrow checker usually provides, but it *does* return a `&mut` from a
`&` that can then modify the contents of the previous `&`. This is fine, but
violates the TBAA rules I laid out earlier. A previous revision of them
handled this, but got lost during one of the redesigns.

New Rules
---------

Given this, we need only change the rules slightly:

    !N   = metadata !{ metadata !"&T", metadata !REFERENCE }
    !N+1 = metadata !{ metadata !"&mut T", metadata !N }

That is, `&mut T` and `&T` may alias. In practice, I think us putting
`noalias` on `&mut T` function arguments will recover most of the aliasing
information. A custom AliasAnalysis pass will be needed for precise aliasing
information, but as cwzwarich pointed out, it will be difficult to retain the
original type-system information across IR transformations. A quest for
another day.

[orig]: http://cmr.github.io/blog/2014/04/01/type-based-alias-analysis-in-rust/
[reddit]: http://www.reddit.com/r/rust/comments/21wu1c/simple_typebased_alias_analysis_for_rust/cghh0ga
