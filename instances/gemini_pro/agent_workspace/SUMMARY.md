# Distributed Systems Consensus Algorithms: A Summary

This document provides an overview and links to detailed explanations of fundamental consensus algorithms in distributed systems. As the Distributed Systems Cartographer, my purpose is to explore, map, and document these complex landscapes to contribute to a collective understanding.

## Table of Contents

*   [Raft Consensus Algorithm](#raft-consensus-algorithm)
*   [Paxos Consensus Algorithm](#paxos-consensus-algorithm)
*   [Consistency Models and Distributed Transactions](#consistency-models-and-distributed-transactions)

---

## Raft Consensus Algorithm

Raft is a consensus algorithm designed for understandability. It aims to be as fault-tolerant and performant as Paxos but with a strong emphasis on being easier to comprehend and implement. It decomposes the consensus problem into three key subproblems: Leader Election, Log Replication, and Safety. Raft achieves consensus through a strong leader-based approach, where a single leader is responsible for log management and consistency.

[Read more about Raft Consensus Algorithm](raft_summary.md)

---

## Paxos Consensus Algorithm

Paxos is a family of protocols for solving consensus in an asynchronous network of unreliable processes. Renowned for its theoretical correctness and fault tolerance, it guarantees agreement on a single value even with message loss and server failures. Paxos defines roles (Proposer, Acceptor, Learner) and operates in two phases (Prepare and Accept) to reach consensus. Multi-Paxos extends this to agree on a sequence of values, making it suitable for state machine replication.

[Read more about Paxos Consensus Algorithm](paxos_summary.md)
