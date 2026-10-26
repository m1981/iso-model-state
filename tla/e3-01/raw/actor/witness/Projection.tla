---- MODULE Projection ----
EXTENDS Integers
\* Lokalny, syntetyczny test relacji; nie pełny model procesu.
LocalAction(before, after, actor) ==
    /\ actor \in {"A"}
    /\ before.state \in {"verified"}
    /\ (before.rejections < 2)
    /\ after = LET s0 == [before EXCEPT !.state = "draft"]
                   s1 == [s0 EXCEPT !.rejections = (s0.rejections + 1)]
               IN s1
Seeds == <<
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 1]
>>
Actors == <<
    "A"
>>
ExpectedEnabled == <<
    TRUE
>>
ExpectedAfter == <<
    [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 1, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 1]
>>
VARIABLES case_id, phase, item
Init == \E i \in 1..1: /\ case_id = i /\ phase = 0 /\ item = Seeds[i]
Next == /\ phase = 0 /\ LocalAction(item, item', Actors[case_id])
        /\ phase' = 1 /\ UNCHANGED case_id
Availability == (phase = 0) => ((ENABLED Next) = ExpectedEnabled[case_id])
Successor == (phase = 1) => (item = ExpectedAfter[case_id])
====
