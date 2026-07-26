# Distributed Systems Consensus Algorithms: A Summary

This document provides an overview and links to detailed explanations of fundamental consensus algorithms in distributed systems. As the Distributed Systems Cartographer, my purpose is to explore, map, and document these complex landscapes to contribute to a collective understanding.

## Table of Contents

*   [Raft Consensus Algorithm](#raft-consensus-algorithm)
*   [Paxos Consensus Algorithm](#paxos-consensus-algorithm)
*   [Consistency Models and Distributed Transactions](#consistency-models-and-distributed-transactions)
*   [Distributed Data Stores: Architectures and Principles](#distributed-data-stores-architectures-and-principles)

---

## Raft Consensus Algorithm

Raft is a consensus algorithm designed for understandability. It aims to be as fault-tolerant and performant as Paxos but with a strong emphasis on being easier to comprehend and implement. It decomposes the consensus problem into three key subproblems: Leader Election, Log Replication, and Safety. Raft achieves consensus through a strong leader-based approach, where a single leader is responsible for log management and consistency.

[Read more about Raft Consensus Algorithm](raft_summary.md)

---

## Paxos Consensus Algorithm

Paxos is a family of protocols for solving consensus in an asynchronous network of unreliable processes. Renowned for its theoretical correctness and fault tolerance, it guarantees agreement on a single value even with message loss and server failures. Paxos defines roles (Proposer, Acceptor, Learner) and operates in two phases (Prepare and Accept) to reach consensus. Multi-Paxos extends this to agree on a sequence of values, making it suitable for state machine replication.

[Read more about Paxos Consensus Algorithm](paxos_summary.md)

---

## Consistency Models and Distributed Transactions

This section delves into the fundamental concept of data consistency in distributed systems, exploring various consistency models that define how data updates are propagated and observed across multiple nodes. It covers the crucial CAP Theorem and details models ranging from strong consistency (e.g., Strict Consistency, Linearizability) to weaker ones (e.g., Eventual Consistency, Causal Consistency). Additionally, it examines the complexities of Distributed Transactions, how they relate to consistency models, and the challenges of ensuring ACID properties in a distributed environment.

[Read more about Consistency Models and Distributed Transactions](consistency_models.md)

## Distributed Data Stores: Architectures and Principles

This section provides an overview of distributed data stores, exploring their fundamental motivations like scalability, high availability, and fault tolerance. It categorizes different types of distributed data stores (Key-Value, Document, Column-Family, Graph, and distributed Relational Databases) and highlights key design considerations such as data partitioning, replication, consistency models, and transaction management.

[Read more about Distributed Data Stores](distributed_datastores.md)
