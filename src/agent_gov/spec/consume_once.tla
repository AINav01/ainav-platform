--------------------------- MODULE consume_once ---------------------------
(* Compact Job C sketch. Catalog formal.claimed=false. Not formally verified.

   Two distinct seats bind one action_hash. The grant is consumed once.
   Replay does not change the consumed set. Missing either seat is a no-op.
*)
EXTENDS Naturals

VARIABLES consumed

Init == consumed = {}

Admit(h) ==
  /\ h \notin consumed
  /\ consumed' = consumed \union {h}

Replay(h) ==
  /\ h \in consumed
  /\ consumed' = consumed

MissingSeat ==
  UNCHANGED consumed

Next ==
  \/ \E h : Admit(h)
  \/ \E h : Replay(h)
  \/ MissingSeat

Inv == consumed \subseteq STRING
=============================================================================
