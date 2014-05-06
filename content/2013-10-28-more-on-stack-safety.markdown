Title: More On Stack Safety
Date: 2013-10-28 17:58
Category: Rust

I got a lot of great feedback on my [previous
post](http://cmr.github.io/blog/2013/10/21/on-stack-safety/), and I've done
some thinking and come up with what I think is a better proposal, and a solid
way forward.

<!-- more -->

1. Teach the task API to allow spawning a task with a fixed stack size.
2. Add the ability to query stack size from LLVM. This lets us implement stack
   guard zones precisely.
3. Add a way to use the result of #2 in a clean way. This is probably the
   trickiest to get right.

You'll note that this doesn't seem to support segmented stacks *or* omission
of stack safety! I'm now of the opinion that segmented stacks have no future.
They currently only allow aborting on stack overflow, not unwinding, and their
only other benefit (the ability to "grow" the stack) is niche. If someone
really thinks growable stacks is desirable, and has valid, convincing
usecases, they should contact me by email or IRC.  Otherwise, the guarantees
they provide are the same as guard zones (abort on overflow).

Omission of stack safety seems missing. But, it isn't needed when using guard
zones! Since guard zones impose nothing on a function's generated code (ie,
there's no prelude that looks into TLS, no need for a `__morestack`), an
environment which can't provide guard zones simply does nothing special when
setting up a task's stack.

You'll also note that this ditches the static analysis I was so fond of. This
sort of analysis really belongs in a lint pass, rather than as a core part of
the safety feature. A crate can say `#[max_stack_size = "64K"];` or
`#[deny(unbounded_stack)]` if it wants static stack size checking (which
people
[seem](http://www.reddit.com/r/rust/comments/1owhwi/on_stack_safety/ccwke1l)
[to](http://www.reddit.com/r/rust/comments/1owhwi/on_stack_safety/ccwjhpn)
[want](http://www.reddit.com/r/programming/comments/1owjmi/on_stack_safety_in_rust/ccwei0c)).

Requiring fixed-sized stacks seems like a step backwards, but I don't see a
better path forward. Solving this problem can be left to a less-rusty, perhaps
research, language.
