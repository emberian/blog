Title: Rust's Memory Management
Date: 2013-08-13 01:14
Category: Rust

**Note:** I accidentally published this. I won't take it down, but it is
incomplete and I do not guarantee its correctness.

**Note 2:** I don't think this post is necessary anymore, as the tutorial has
been updated significantly, and is quite understandable. As such I don't plan
on finishing this post. Email me if you'd like to see it finished.

Rust seems to intimidate newcomers, as its memory model is fairly complex. I
think part of the problem is that the language tutorial introduces the memory
model by feature.  Rather, I'll introduce it by concept, showing examples of
code that breaks memory safety in C, and how Rust's memory model prevents the
error. Hopefully I can convince you that Rust isn't as complex as it looks,
and that the extra syntax is well-worth the zero-cost memory safety. I'll be
comparing Rust code to equivalent C idioms using the [`zeromq
library`](http://zeromq.org/) because it has a very clean API in both
languages. As such, I assume basic familiarity with C. Rust is not a very
suitable language for new programmers, and neither is this tutorial.

<!-- more -->

The core concepts driving Rust's memory management are, in reverse order of
simplicity, *ownership*, *mutability*, and *lifetime*. It's not that other
languages don't have them, it's just that they're implicit or convention. I
won't be using many fancy features of Rust here. They aren't needed to explain
the memory management, variables and functions suffice.

# Ownership

Ownership is simply who is responsibile for freeing an object. If you own an
object, you are ensured it is valid.

An example in C would be:

```
void *context = zmq_ctx_new(); // zeromq owns the context, you just get to use it
// ...
zmq_ctx_destroy(context); // you need to tell zeromq to free it, you aren't allowed to do so
```

In Rust:

```
let context: ~Context = zmq_ctx_new();
// ....
// context implicitly freed when no one owns it anymore
```

Notice that the C uses an opaque `void*` and that Rust uses
the explicitly-named `~Context`. In C, you often use opaque types because the
language offers no control over visibility of struct members. In Rust, you can
mark the fields of a struct `priv`, which will disallow users of the library
from using those fields. This is a bit nuanced, and I'll explain it in a later
tutorial on privacy and the module system.

The tilde means "owned pointer", in that if you have an owned pointer to an
object, you are the owner. Creating an owned pointer involves a heap
allocation (malloc). I use an owned pointer in these examples to mirror the C,
but idiomatic Rust uses values on the stack much more frequently than values
on the heap.

## Taking ownership

Rust goes one step further with ownership. The compiler asserts that an object
cannot be owned multiple times. An object can be owned by a stack frame
(locals and function arguments), a scope, or a struct. For lack of a better
term, I'll call these "owners." You transfer ownership by "moving" into an
owner. Once an owner loses ownership, the compiler will error if you try to
use the object again through that owner.  This disallows dangling pointers and
prevents an entire class of error (and potentially vulnerability), "use after
free."

In C, it's perfectly valid to do:

```
void *context = zmq_ctx_new();
zmq_ctx_destroy(context);
use_context(context); // compiles fine, but clearly incorrect
```

Whereas in Rust:

```
let context: ~Context = zmq_ctx_new();
{ // introduce a scope
	let context2: ~Context = context; // context moved into the variable in this scope
} // context2 freed at scope close
use_context(context); // error: use of moved value: `context`
```

## Not taking ownership

Most functions that take arguments don't need to take ownership. To express
this, Rust has the "borrowed pointer." For example, in C you would write this:

```
int length(some_large_struct_t *datum) {
	return datum->x - datum->padding;
}
```

The function does not care who owns the object, it doesn't need to free it, as
there's no reason the object can't be used again after this computation. In
Rust, it's:

```
fn length(datum: &some_large_struct) -> int {
	datum.x - datum.padding
}
```

The first thing you'll notice is that there is no dereference to be found in
the source. In C, `->` is the dereferencing struct member extraction operator.
In Rust, `.` will dereference if it needs to. You'll also notice that Rust
uses `&` rather than `*` to indicate this type of a pointer. It's the same
operator used to take a pointer (address-of), as in C. C, however, doesn't
enforce the non-transfer of ownership. It's perfectly valid to do:

```
int length(some_large_struct_t *datum) {
	int l = datum->x - datum->padding;
	free(datum);
	return l;
}
```

`length` has now incorrectly taken ownership of `datum`, by `free`ing it. Any
code which had a pointer to `datum` has now been rendered incorrect. In Rust,
there is no way to safely free memory. It is automatically free'd.

## Multiple ownership

There are situations when ownership isn't so black and white, and for that
Rust has the "managed pointer." The type of a managed pointer is `@'static T`.
The `'static` means "this type cannot contain any borrowed pointers." The
shorthand for `@'static T` is just `@T`: it's impossible to have a managed
pointer to a type that doesn't fulfill `'static`. Using only owned and
borrowed pointers, ownership forms a DAG. Managed pointers allow cycles. They
are GC-managed, and allow multiple pointers to the same object. The way this
is enabled is that the pointer's contents (the pointee) are immutable. If
they were allowed to be mutable, data races would occur. In the next section
I'll show the mutable version.

These have no direct comparison in C. The closest comparison is probably
GObject's memory management API. Managed pointers aren't explicit memory
management. As the name suggests, the runtime manages it for you. Managed
pointers are usually considered as a "last resort". Even though GC in Rust can
be fast because all managed pointers are task-local, no GC is always faster
than some GC.

# Mutability

Mutability is whether you are allowed to mutate, or modify, some data. There
are two pieces to mutability: mutability of things an object owns (inherited
mutability), and mutability of data through a pointer.

## Inherited Mutability

Say you have a point on the stack:

```
struct Point {
	x: int,
	y: int
}
let value: Point = Point { x: 24, y: 42 };
```

If you try to mutate the point by, say, changing the `x` field, the compiler
will complain:

```
value.x = 42; //~ ERROR: cannot assign to immutable field
```

The error message is actualy a bit misleading: there is no such thing as a
mutable field! "Point" is said to have inherited mutability; its mutability is
determined by the mutability of the thing that holds it. So, to fix this
example, we'd use:

```
let mut value: Point = Point { x: 24, y: 42 };
value.x = 42;
```

Inherited mutability inherits throughout the ownership tree: the value, and
everything the value owns, recursively.
