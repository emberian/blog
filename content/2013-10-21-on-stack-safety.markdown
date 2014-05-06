Title: On Stack Safety
Date: 2013-10-21 00:42
Category: Rust

Stack safety is a sticky topic in Rust right now. There are multiple
conflicting tensions. My goal is to lay them bare, untangle the mess, and see
if there's a better way forward (spoiler: there is!).

<!-- more -->

When a program is "stack safe", the [stack
pointer](http://en.wikipedia.org/wiki/Call_stack#Structure) never points
outside of allocated memory specifically dedicated to the stack. The
most interesting violation of stack safety as it applies to Rust is the [stack
overflow](http://en.wikipedia.org/wiki/Stack_overflow). (In fact, given
safe code, or even unsafe code as long as it doesn't putz with the stack
pointer or the stack frame, it is the *only* possible violation of stack
safety). Stack overflow happens when the stack does not have enough space to
store the full stack frame.

There are three basic ways of dealing with stack overflow:

1. Give up and accept the potential memory unsafety and resulting bugs.
2. Do static analysis to determine the maximum stack size, and make sure
   that the stack is at least that large.
3. Do runtime checks to make sure that there is always enough space on the
   stack for a function to proceed, and handle violation of that condition
   somehow.

(*Note*: in what follows, I conflate "language" with "implementation of a
given language" for clarity)

Examples of languages that take strategy #1 are C, C++, Nimrod, and
Objective-C. Stack overflow usually manifests as a segmentation fault or bus
error, though more colorful errors are possible when a thread runs into
another thread's stack, or onto the heap, causing heap corruption or threads
stomping on each others' stack. Clearly this is not a viable solution for
Rust: the very act of calling a function becomes unsafe.

Strategy #2 is tempting, but cannot be used in the general case. The
[research](http://dl.acm.org/citation.cfm?id=1113833&bnc=1)
[I](http://dl.acm.org/citation.cfm?id=1631721)
[found](http://dl.acm.org/citation.cfm?doid=1375634.1375656) investigate stack
depth in the case of no recursion (so the call graph is actually a call
(directed-)acyclic graph) but with asynchronous interrupt handlers. Indeed, it's
trivial to show that when recursion is disallowed, a conservative stack limit
can be calculated just by taking the longest path through the call graph with
the nodes being weighted by the size that function's stack frame needs (this
is a slightly different construction than most weighted graphs). This solution
is not viable either: recursion is perfectly valid, rejecting it would make
Rust very crippled as a language. To my knowledge, no languages rely on this
for stack safety, though in practice I am sure many applications apply this
technique.

This leaves us with strategy #3, dynamic checks. Dynamic checking is fairly
easy to do. The size of a function's stack frame is easy to calculate. One
need only increment/decrement some global (or, rather, thread-local) counter
by the stack frame size. When it becomes negative, there is no more stack.
Almost every language I've used (the exceptions are noted above) use this
technique. Java, Python, Lua, Ruby, Go, the list goes on. The only differences
between the languages is what they do when the stack does overflow. Most throw
an exception. Another method of implementing dynamic checks is to leave a
"guard zone" after the stack. This zone is mapped in a way that accessing it
causes a page fault, which sends a signal or kills the process. (The exact
implementation of this strategy differs; some allocate a stack frame for a
function on the heap. Things get blurry with the interpreted languages, but
they generally prevent stack overflow in a memory safe way.)

Rust currently uses strategy #3, with tweaks. The current implementation
heavily depends on LLVM's [segmented
stack](http://llvm.org/releases/3.0/docs/SegmentedStacks.html) feature. On x86
(and I assume other platforms as well), a pointer to the end of the stack is
stored in thread-local storage. The prelude to every function call compares
that value to the value of the stack pointer, and calls a special function
`__morestack` which will allocate a new stack segment for the function call to
take place on. The stack segment is freed afterwards. The kink comes when
using the FFI to call C code. C assumes a single, large stack. In order to
fulfill that expectation, we have the `fixed_stack_segment` attribute to
give a function a large stack segment: hopefully large enough that the C
function doesn't overflow the stack.

Segmented stacks are of questionable utility. On large systems, such as x64,
address space is practically boundless, so lazily allocating stack segments is
going to be slower than just requesting a very large mmap'd stack that the OS
will lazily allocate. On small, resource-constrained systems, the overhead of
stack size checking (it requires TLS *and* stack size checks) is too much.
Segmented stacks only optimize for mid-sized address spaces. And the entire
purpose of segmented stacks (conservative but growable stack sizes) is moot if
one is not using many tasks with small stacks.
([Previously](https://mail.mozilla.org/pipermail/rust-dev/2013-July/004686.html),
[previously](https://github.com/mozilla/rust/issues/8345))

All of the solutions so far are inadequate. They're inflexible and have poor
composability in the case where a crate wants custom stack safety. I propose a
hybrid:

1. If there is no recursion or other sources of stack size uncertainty, the
   maximum stack size is decidable and is used as the only stack size, like
   strategy #2. Every function would be annotated with the total stack size it
   could possibly use, given static function calls. This fails at the first
   introduction of function pointers: it is impossible to know how much stack
   they need until runtime. However, this is not as limiting as it may sound,
   as long as one only tries to achieve a conservative estimate of maximum
   stack size. Since function pointers only come from trait objects and
   closures, the compiler can take the max of the stack frame for *every
   implemention* of the trait. I would assume closures could work in a similar
   way, in limited cases. There will always be cases where this analysis
   fails.
2. If the analysis in step 1 results in indeterminate stack sizes, rustc will
   check a crate attribute. This crate attribute indicates which stack safety
   strategy should be used: either guard zones, stack size checks, segmented
   stacks, or no stack safety at all (note that stack size checks is segmented
   stacks minus expanding the stack with `__morestack`).  Disabling stack
   safety "taints" a crate, and any use of its functions requires `unsafe`,
   like calling C code, and they cannot be coerced to closures (this would
   lose the "taint" bit). Note that when the maximum stack size is decidable,
   this attribute won't be checked.

All of the trickiness comes from compiling libraries with this. Executables
are easy: since they define the execution context, they can decide how they
want the stack to be secured. Libraries, being embedded in other contexts,
need to obey their execution environment. At the very least, no-stack-safety
will make it possible to implement libraries exposing a native ABI in Rust
without requiring weirdness in the FFI, as well as implement custom stack
safety when it's desired.

By allowing crates to chose how they want stack safety to be implemented, we
retain flexibility to fit any situation. By making it a crate attribute, we
can handle combination of crates using different stack safety schemes in a
sane way. There are still some niggling details with combining crates using
different stack safety schemes (propagating the taint bit is quite difficult
in the face of trait objects, but for now we could simply disallow
combinations and work them out later (it's a backwards compatible change). I
think this is a good stack safety strategy, superior to the current one, and
worth implementing.

Please email me any comments, or see the [discussion on
reddit](http://www.reddit.com/r/rust/comments/1owhwi/on_stack_safety/).
