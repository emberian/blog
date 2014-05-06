Title: Simple Type-Based Alias Analysis for Rust
Date: 2014-04-01 05:48
Category: Rust

This post examines type-based alias analysis and how a simple one can be
implemented for [Rust](http://www.rust-lang.org/).

<!-- more -->

Background
----------

[Alias analysis][aa], in the context of LLVM, is an analysis which determines
whether two pointers can point to the same data, or "alias". [More
specifically][llaa], two pointers `a` and `b` alias if uses of a pointer
"based" on `a` can ever have a dependence on use of a pointer based on `b`. In
practice, this means that any valid use of the pointers cannot influence the
contents of the other. The LLVM Language Reference has a [more precise
definition of aliasing][alias].

Type-based alias analysis (TBAA) is a specific kind of analysis which uses type
information from the frontend to determine whether two pointers can alias. It
is a very coarse analysis, but is very easy and fast to do (linear time with
respect to the number of types, constant time with respect to the size of the
code). [LLVM's TBAA][tbaa] metadata describe a tree of types. Loads, stores,
and calls can then be annotated with which type they use:

    store %struct.Foo { ... }, %struct.Foo* %42, !tbaa !0
    %val = load %struct.Foo* %42, !tbaa !0
    call void @foo(i32* %p), !tbaa !1

The metadata node referenced has the form:


    !0 = metadata !{ metadata !"root node" }
    !1 = metadata !{ metadata !"a type", metadata !0 }
    !2 = metadata !{ metadata !"another type", metadata !0, i64 1}
    !3 = metadata !{ metadata !"root node two" }
    !4 = metadata !{ metadata !"yet another type", metadata !3 }


The first field is the name of the type, the second field is the parent node
in the tree, and the third field is 1 if the pointer "pointsToConstantMemory".
A pointer to a type may alias with a pointer to any type which is either an
ancestor or descendent of it in the TBAA tree, or if the types exist in
different TBAA trees. In the above example, pointers of type !1 and !2 can
never alias, whereas pointers of type !1 and !4 may alias, because they exist
in different trees.

Rust's Aliasing Rules
---------------------

Rust's [type
system](http://static.rust-lang.org/doc/master/rust.html#type-system) has some
guarantees about pointer aliasing.

The simplest rule is that raw pointers (`*T` and `*mut T`) may alias with
anything and everything. `*T` and `*mut T` are not segregated, to avoid
punishing misusers of raw pointers with very hard to debug bugs. `*T` and `*U`
(raw pointers to unrelated types) may alias freely.

More complexly, `&mut T`, and `&T` cannot alias with each other, nor with `&U`
etc. This is not strictly true, according to [LLVM's definition][alias] of
"alias". However, a `&mut T` and a `&T`, if aliasing, can never impose a
memory dependence on each other. The borrow checker will guarantee this. If a
`&mut T` is live, there cannot be a `&T` which aliases with it, and vice
versa. Consider the following program:

    fn foo(mut x: int) {
        let y = &mut x;
        let z: &int = &*y;
        *y = 32;
    }

This is rejected with the error "cannot assign to `*y` because it is
borrowed". If we instead put the borrow in its own scope:

    fn foo(mut x: int) {
        let y = &mut x;
        { let z: &int = &*y; }
        *y = 32;
    }

Compilation will succeed, but any use of `y` cannot possibly influence any use
of `z`.

Owning pointers (`~T`) are a curious case. They are never used directly, but
rather borrowed as `&T` or `&mut T`. I believe they can be safely omitted from
this analysis.

Trait objects and closures are somewhat more complicated. They consist of two
pointers, one of which is pointsToConstantMemory (the function pointer), and
the other which obeys the aliasing rules above. I will omit metadata for those
(though see the "Moving Forward" section)

Implementing TBAA
-----------------

We must define a tree of types, which indicates their aliasability. The
broadest part of the tree is:

    digraph "rust tbaa" {
        "simple rust tbaa" -> "raw pointer";
        "raw pointer" -> "reference";
    }

All raw pointers are simply given the "raw pointer" type, with no additional
discrimination between types. When a owning pointer or reference is
encountered, we will create new metadata nodes for the referenced type:

    !N   = metadata !{ metadata !"&T", metadata !REFERENCE }
    !N+1 = metadata !{ metadata !"&mut T", metadata !REFERENCE }

These metadata nodes are then cached in the crate context:

    tbaa_nodes: RefCell<HashMap<ty::t, ValueRef>>

Creation of the metadata nodes is uninteresting. Once they exist, however,
they can be attached to the results from a load/store. For maximum utility,
every possible load/store should be annotated, since unannotated load/stores
are considered MayAlias.

Store
-----

The following functions can be modified for Stores:

- `datum::load`
- `Datum::shallow_copy`
- `glue::drop_ty_immediate`
- `foreign::trans_native_call`
- `foreign::trans_rust_fn_with_foreign_abi`
- `intrinsic::trans_intrinsic`

The following are somewhat interesting cases, because they handle the
translation of primitives. I believe some meaningful TBAA metadata could be
created for them, but I am not sure of the utility, and will omit them for
now:

- `tvec::set_fill`
- `tvec::alloc_raw`
- `tvec::trans_slice_vstore`
- `tvec::trans_lit_str`
- `tvec::iter_vec_loop`
- `expr::auto_slice`
- `expr::trans_def_dps_unadjusted`

These are like above, but somewhat less obvious how to handle:

- `CleanupHelperMethods::get_or_create_landing_pad`
- `asm::trans_inline_asm`
- `closure::store_environment`
- `closure::fill_fn_pair`

The Store in `callee::trans_call_inner` does not need TBAA, the retpointer is
already marked noalias in the function args.

Load
----
- `datum::load`
- `base::load_if_immediate`

These handle primitives:

- `tvec::get_fill`
- `tvec::get_alloc`
- `tvec::get_base_and_byte_len`
- `tvec::get_base_and_len`
- `tvec::iter_vec_loop`

These are less obvious how to handle:

- `glue::call_visit_glue`
- `glue::trans_struct_drop_flag`
- `glue::make_drop_glue`
- `adt::nullable_bitdiscr`
- `adt::load_discr`
- `_match::store_non_ref_bindings`
- `_match::compile_submatch_continue`
- `closure::load_environment`
- `CleanupHelperMethods::trans_cleanup_to_exit_scope`
- `callee::trans_call_inner`
- `meth::trans_trait_callee_from_llval`

Moving Forward
--------------

Once this basic TBAA is done, tbaa.struct metadata can be emitted for memcpy.
There is also a "struct-path tbaa" which I do not understand yet, but provides
more precise information. After that, a further custom Rust-specific
AliasAnalysis pass can be created which knows, for example, that two separate
`&mut T` cannot alias. References to statics, and in particular `&'static T`
are also of interest because they will always be `pointsToConstantMemory`.
Further investigation waits for another day.


[aa]: https://en.wikipedia.org/wiki/Alias_analysis
[llaa]: http://llvm.org/docs/AliasAnalysis.html
[alias]: http://llvm.org/docs/LangRef.html#pointeraliasing
[tbaa]: http://llvm.org/docs/LangRef.html#tbaa-metadata

