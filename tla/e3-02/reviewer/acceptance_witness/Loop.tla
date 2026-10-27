---- MODULE Loop ----
EXTENDS Integers, Sequences
Dependencies == [p1 |-> [depends_on |-> {}, id |-> "p1", predecessor |-> "none", rejections |-> 0, state |-> "approved", suspect |-> FALSE, type |-> "PLAN", version |-> 1]]
Types == [AT |-> [requires_approval |-> TRUE], CODE |-> [requires_approval |-> FALSE], DES |-> [requires_approval |-> FALSE], PLAN |-> [requires_approval |-> TRUE], REQ |-> [requires_approval |-> TRUE]]
Deps(e) == {Dependencies[id] : id \in e.depends_on}
Op1(before, after, actor, checks, evidence) ==
    /\ actor \in {"A"}
    /\ before.state \in {"draft"}
    /\ ((~(before.suspect) /\ checks) /\ (\A dep \in Deps(before): (dep.state \in {"approved", "baselined"})))
    /\ after = LET s0 == [before EXCEPT !.state = "verified"]
               IN s0
Op2(before, after, actor, checks, evidence) ==
    /\ actor \in {"U"}
    /\ before.state \in {"verified"}
    /\ (Types[before.type].requires_approval /\ ~(before.suspect))
    /\ evidence
    /\ after = LET s0 == [before EXCEPT !.state = "approved"]
               IN s0
Op3(before, after, actor, checks, evidence) ==
    /\ actor \in {"U"}
    /\ before.state \in {"verified"}
    /\ (before.rejections < 2)
    /\ after = LET s0 == [before EXCEPT !.state = "draft"]
                   s1 == [s0 EXCEPT !.rejections = (s0.rejections + 1)]
               IN s1
RawAction(before, after, command) ==
    CASE command.operation = 1 -> Op1(before, after, command.actor, command.checks, command.evidence)
      [] command.operation = 2 -> Op2(before, after, command.actor, command.checks, command.evidence)
      [] command.operation = 3 -> Op3(before, after, command.actor, command.checks, command.evidence)
      [] OTHER -> FALSE
Seed == [depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 2]
Commands == <<[actor |-> "A", checks |-> TRUE, evidence |-> FALSE, operation |-> 1],
[actor |-> "U", checks |-> FALSE, evidence |-> FALSE, operation |-> 3],
[actor |-> "A", checks |-> TRUE, evidence |-> FALSE, operation |-> 1],
[actor |-> "U", checks |-> FALSE, evidence |-> FALSE, operation |-> 3],
[actor |-> "A", checks |-> TRUE, evidence |-> FALSE, operation |-> 1],
[actor |-> "U", checks |-> FALSE, evidence |-> TRUE, operation |-> 2]>>
ExpectedStates == <<[depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 2],
[depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 0, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 2],
[depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 1, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 2],
[depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 1, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 2],
[depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 2, state |-> "draft", suspect |-> FALSE, type |-> "REQ", version |-> 2],
[depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 2, state |-> "verified", suspect |-> FALSE, type |-> "REQ", version |-> 2],
[depends_on |-> {"p1"}, id |-> "r1", predecessor |-> "none", rejections |-> 2, state |-> "approved", suspect |-> FALSE, type |-> "REQ", version |-> 2]>>
VARIABLES item, depth
Init == /\ item = Seed /\ depth = 0
Next == /\ depth < Len(Commands) /\ RawAction(item, item', Commands[depth+1]) /\ depth' = depth+1
Availability == (depth < Len(Commands)) => ENABLED Next
Successor == item = ExpectedStates[depth+1]
====
