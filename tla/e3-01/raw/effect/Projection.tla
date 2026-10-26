---- MODULE Projection ----
EXTENDS Integers
\* Lokalny, syntetyczny test relacji; nie pełny model procesu.
LocalAction(before, after, actor) ==
    /\ actor \in {"U"}
    /\ before.state \in {"verified"}
    /\ (before.rejections < 2)
    /\ after = LET s0 == [before EXCEPT !.state = "draft"]
               IN s0
Seeds == <<
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 1, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 2, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "approved", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "r2", rejections |-> 1, state |-> "verified", suspect |-> TRUE, type |-> "REQ", version |-> 2]
>>
Actors == <<
    "U",
    "U",
    "U",
    "A",
    "R",
    "U",
    "U",
    "U"
>>
ExpectedEnabled == <<
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    TRUE
>>
ExpectedAfter == <<
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 1, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 2, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 2, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "approved", suspect |-> FALSE, type |-> "REQ", version |-> 1],
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "r2", rejections |-> 2, state |-> "draft", suspect |-> TRUE, type |-> "REQ", version |-> 2]
>>
VARIABLES case_id, phase, item
Init == \E i \in 1..8: /\ case_id = i /\ phase = 0 /\ item = Seeds[i]
Next == /\ phase = 0 /\ LocalAction(item, item', Actors[case_id])
        /\ phase' = 1 /\ UNCHANGED case_id
Availability == (phase = 0) => ((ENABLED Next) = ExpectedEnabled[case_id])
Successor == (phase = 1) => (item = ExpectedAfter[case_id])
====
