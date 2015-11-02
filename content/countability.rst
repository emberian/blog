Countability and Enumerability
==============================

:date: 2015-11-01 20:50
:category: Mathematics
:slug: countability-vs-enumerability

I've sometimes conflated the ideas of a set being countable (a set
:math:`S` is countable iff :math:`\exists I : \mathbb{N} \to S`) and a set
being enumerable (you can write a program that lists them).  However, they are
very distinct concepts. Here's an example, appealing to the widely-used proof
in computability theory that Turing Machines (TMs) can not recognize
if another arbitrary TM will halt on a specific input.  Let's define a total
ordering on TMs. Brainfuck programs are equivalent to TMs, so let's use that.
Any lexicographic ordering on the program will do.  There is a least element
(the empty string), and we can "increment" a TM under this ordering, as if it
were a base-8 number (8 being the number of instructions in brainfuck). Thus,
TMs are countable. Now, let's take the set of TMs that halt on all of their
inputs, call it HTMs. Since HTMs is a subset of all TMs, HTMs is also
countable.  However, while you can list the TMs, you cannot list the HTMs!
Why?  Well, to find the *least* element of that set, you would need to
enumerate the TMs and find the first that halts on all inputs. This would
solve the halting problem, which is not possible. Put another way,
countability is invariant under subset, but enumerability is not. So
countability and enumerability are not the same. This isn't a new insight by
any means, and there's a reason that the class of languages that TMs can
recognize is called "recursively enumerable".

.. _Church-Turing thesis: https://en.wikipedia.org/wiki/Church%E2%80%93Turing_thesis
