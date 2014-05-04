Title: "How I got started hacking rustc, and how you can too!"
Date: 2013-06-23 08:06
Category: Rust

*This is the first part of a planned series about `rustc`, the Rust compiler*

I remember first hearing about Rust during the summer of 2011. In fact, I
remember the exact moment. I was at MIT, doing their Junction program. It was
during a seminar about semiconductors. I remember browsing through the source on github,
getting lost, and going home.

<!-- more -->

Fast forward to two months ago. A [slashdot post][sdot] appears, bringing Rust
back to the forefront of my consciousness. By this point I'd actually gained
some programming chops, gotten a job, etc. I read through the Wikipedia
article, though "hey, this looks like it has potential," and forgot about it.

Fast forward a week or two. The [matasano crypto challenges][mata] were linked
on HN. "Our friend Maciej says these challenges are a good way to learn a new
language, so maybe now's the time to pick up Clojure or Rust." And pick up
Rust I did. Rust was a pretty easy language to get started with, with my
predominantly Python, C, and Lua background. Especially for the crypto
challenges, which start off fairly basic.

# First, some warnings:

Rust is pre-alpha software. Backwards incompatible changes happen *weekly*,
either in the libraries, or in the language.  It's probably best to not write
any "serious" code in Rust right now, unless you plan on fixing it every few
weeks to keep up with the language. The nice part about contributing code to
the compiler is that when someone changes the language or a library, it is
their job to fix the code that uses it.

Make sure to use the `master` branch, and **use the doc links under "Trunk".
It will save you pain.** Nothing is worse than accidentally using the 0.6
documentation and finding that a method has been renamed or removed, and
getting confused when the build fails halfway through.

**The Rust compiler is poorly written.** This is an artifact of being written
in Rust, which, as stated, changes rapidly. Some code is very old, and uses
very old idioms, or doesn't use newer language features that would be cleaner
and easier to read. If you notice this, try and fix it! If you notice it, that
means you already more-or-less know what needs to be done to clean it up a
bit. If the change is very invasive, it's probably best to open an issue and
let an experienced dev deal with it. An example of a cleanup is [pull request
7315](https://github.com/mozilla/rust/pull/7315), which cleaned up indentation
and replaced some `if`s with `match`es.

Do not, repeat, *not*, use the `rustc` code as a source of "how to write
Rust." Almost all of it is bad code. I don't even know where to tell you to
look to find consistently good code.  The upside is that generally reviewers
will catch suboptimal code, and suggest improvements.  [This pull request, for
example](https://github.com/mozilla/rust/pull/7207), used some old Rust
idioms, which the reviewers suggested fixes for. So feel free to get
elbow-deep in code without worrying *too* much about whether the code you're
writing is good or bad. General guidelines: avoid `@` always, avoid `~`
usually, use `Option` and `Result`, handle errors. That will guide you
straight most of the time, and by the time you know when to ignore those, you
probably already know what good Rust code is.

# Getting started

The first thing I did was, of course, go to the [home page][home]. I read the
feature summary (which seemed mostly unchanged from when I first saw it.
Indeed, looking in the wayback machine, it is mostly unchanged). I read the
example, and clicked ["tutorial"][tut] over on the left. I built the compiler
while doing this. There are instructions for building Rust over at [the wiki](https://github.com/mozilla/rust/wiki/Note-getting-started-developing-Rust).
It's a lot easier to get started if you're using Linux or Mac, though not
impossible on Windows (just a bit more setup and waiting).

The tutorial left me confused and alone, and I'm sure it did the same to
you. But it gave me enough information that I could write a base64 encode and
decoder, although I constantly referenced the tutorial. By this point I had
moved on to the second matasano challenge, and I found my first compiler bug:
[really poor error messages][first pr]. Of course I had to fix this! Error
messages are easy, right?

Yes and no. With a codebase as large and complex as a compiler, there are many
layers of stuff you need to pick apart to figure out the cause and fix of an
issue. In my case, it was easy, just grep for the error message. The fix,
however, was more complex. I had to figure out how to turn a "span" (the
compiler's way of matching up an AST node with a chunk of source code) in a
string. Often you'll need to go digging through other files to figure out what
you can do, what data structures there are, etc.

**Rust makes this easy!** There are no IDEs or any fancy tools, but Rust
source is insanely `grep`able. You see a method call like
`parser.parse_ident(...)`, you just need to grep for `fn parse_ident`.
Of course, actually understanding what the method does is a whole new can of
worms...

# Picking an issue to fix

I think the best way to pick an issue to fix is to fix a bug you encounter
yourself. Ask in IRC about it, often someone will be online that either knows
about it and can point you in the right direction, or at the very least help
reproduce, debug, and sift through the issue trcker.

There is the [`E-easy`](https://github.com/mozilla/rust/issues?labels=E-easy)
label on certain issues. This are issues that shouldn't take too much trickery
to get done, though they might take some time to get "acclimated" to the
codebase. `E-easy` doesn't mean fast, it means easy. It might be tedius or
take non-trivial amounts of effort, but it shouldn't require overarching
design issues or a lot of knowledge about rust or rust internals.

Documentation always needs writing. Open a random file from libstd or
libextra, look for functions, structs, enums, and traits that aren't
documented. You'll get to see a bunch of Rust code, probably using features
you wouldn't otherwise see writing "normal" code.

# After you fix it

Once you fix the issue, open a pull request. See [GitHub's
help](https://help.github.com/articles/using-pull-requests) for how to do
this. If you get stuck or need additional help, jump onto IRC
([webchat](http://chat.mibbit.com/?server=irc.mozilla.org&channel=%23rust))
and ask. Someone will have to review your changes, ask "r?
$link_to_pull_request" in IRC to expedite the process.

Feel free to ping me (cmr) on IRC if you have any questions or problem.

[sdot]: http://tech.slashdot.org/story/13/04/03/1646234/mozilla-and-samsung-collaborating-to-bring-new-browser-engine-to-android
[mata]: http://www.matasano.com/articles/crypto-challenges/
[home]: http://www.rust-lang.org/
[tut]: http://static.rust-lang.org/doc/tutorial.html
[first pr]: https://github.com/mozilla/rust/pull/6072
