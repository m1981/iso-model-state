---- MODULE Smoke ----
EXTENDS Integers
CONSTANT Limit
VARIABLE x
Init == x = 0
Next == /\ x = 0
        /\ x' = 1
WithinLimit == x <= Limit
====
