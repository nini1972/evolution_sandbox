# Raft Consensus Algorithm: Core Concepts

Raft is a consensus algorithm that is designed to be understandable, while also being equivalent to Paxos in fault-tolerance and performance. The primary motivation behind Raft was to make consensus algorithms more accessible and easier to implement for a wider audience, addressing the perceived complexity of Paxos.

## Key Design Principles:
*   **Decomposition:** Raft decomposes the consensus problem into three relatively independent subproblems:
    *   **Leader Election:** How a new leader is chosen when an existing one fails.
    *   **Log Replication:** How the leader manages and replicates log entries to maintain consistency across servers.
    *   **Safety:** Ensuring that all state machines execute the same sequence of commands and that a leader's log eventually becomes consistent with other leaders.


## Terms:
Raft divides time into arbitrarily long segments called *terms*, identified by monotonically increasing integers. Each term begins with an election in which one or more candidates attempt to become leader. If a candidate wins the election, then it serves as leader for the rest of the term. In some cases, an election will result in a split vote; in this case, the term will end with no leader, and a new election (and thus a new term) will begin with a higher term number.

*   **Term Numbers:** Act as a logical clock in Raft and are exchanged with every RPC (Remote Procedure Call).
*   **Consistency:** Each server stores its current term number. If one server's term number is smaller than another's, it updates its current term to the larger value.

## Leader Election:
Raft uses a heartbeat mechanism to trigger leader elections. Leaders send periodic heartbeats to all followers to maintain their authority. If a follower does not receive a heartbeat for a certain period (election timeout), it assumes the leader has failed and initiates an election.

**Election Process:**
1.  **Follower to Candidate:** A follower increments its current Term and transitions to the Candidate state.
2.  **Vote Request:** The Candidate votes for itself and then issues `RequestVote` RPCs in parallel to all other servers in the cluster.
3.  **Voting:** Other servers, upon receiving a `RequestVote` RPC:
    *   Grant their vote if their current term is less than or equal to the candidate's term, and they haven't voted for another candidate in the current term.
    *   They also check if the candidate's log is at least as up-to-date as their own (this is a safety mechanism).
4.  **Election Outcome:**
    *   **Becomes Leader:** If a candidate receives votes from a majority of the servers in the cluster for the same term, it becomes the new Leader. It then sends `AppendEntries` RPCs (heartbeats) to all other servers to establish its authority and prevent new elections.
    *   **Returns to Follower:** If a candidate receives an `AppendEntries` RPC from another server claiming to be leader (and whose term is >= its own current term), it recognizes the new leader and reverts to Follower state.
    *   **New Election:** If neither of the above happens (e.g., due to a split vote or no candidate receiving a majority), the election times out, the candidate increments its term, and starts a new election.

## Log Replication:
Once a leader has been elected, it is responsible for managing the replicated log. Client requests that modify the system's state are appended as new entries to the leader's log, and then the leader replicates these entries to its followers. The log is a sequence of commands that are executed by the state machine on each server.

**Process of Log Replication:**
1.  **Client Request:** A client sends a command to the leader.
2.  **Append to Leader's Log:** The leader appends the command as a new entry to its own log.
3.  **AppendEntries RPC:** The leader issues `AppendEntries` RPCs in parallel to all followers, asking them to replicate the new log entry.
4.  **Follower Response:** Followers receive the `AppendEntries` RPC and, if their logs are consistent with the leader's, they append the entry to their own logs and reply positively to the leader.
5.  **Commitment:** An entry is considered *committed* once it has been replicated to a majority of servers. Once committed, the leader applies the command to its state machine, and followers will eventually do the same.

**Consistency Check:** `AppendEntries` RPCs also perform a consistency check. When sending an `AppendEntries` RPC, the leader includes the index and term of the log entry immediately preceding the new entries. If a follower does not find an entry at that index with that specific term in its own log, it rejects the `AppendEntries` request. This mechanism ensures that logs remain consistent across the cluster.

## Safety Mechanisms:
Raft implements several safety mechanisms to ensure that the distributed state machine operates correctly and consistently, even in the event of failures.

1.  **Election Restriction (Leader Completeness Property):**
    *   To be elected leader, a candidate must have a log that is "at least as up-to-date" as those of the majority of servers it contacts.
    *   This usually means having all committed entries from previous terms.
    *   This ensures that the leader always has all committed log entries, and data is never lost due to a leader election.

2.  **Commit Rule:**
    *   A log entry is committed only when it has been safely stored on a majority of servers.
    *   Only committed entries are applied to the state machine.
    *   This guarantees that committed entries are durable and will eventually be applied by all healthy servers.

3.  **Leader Transition:** When a new leader takes over, it forces the followers' logs to converge with its own authoritative log. It does this by finding the latest log entry where its log and a follower's log match, and then deleting any conflicting entries in the follower's log and sending its own entries from that point onward.

## Comparison with Paxos (Simplified View):
Raft aims to achieve the same fault-tolerance and safety as Paxos but through a more understandable and simplified mechanism. While Paxos often allows for independent choices by individual acceptors leading to complex recovery scenarios, Raft's leader-centric approach simplifies log management and consistency. The strong leadership model in Raft reduces the number of states to consider and makes reasoning about the algorithm more straightforward.

## Cluster Membership Changes:
Raft supports changing the set of servers in the cluster during runtime. This is crucial for maintenance, scaling, and fault recovery. Direct changes to membership are unsafe because the cluster could split, with two leaders being elected in different majorities of the old and new configurations.

**Joint Consensus:** To ensure safety, Raft implements a two-phase approach called Joint Consensus:

1.  **Transition to Joint Consensus (C_old,new):** The leader first proposes a configuration entry that includes both the old set of servers (C_old) and the new set of servers (C_new). Once this log entry is committed, the cluster operates under a "joint consensus" rule:
    *   Any decision (e.g., for elections or log commitment) requires separate majorities from both C_old and C_new.
    *   At this stage, servers that are part of C_new but not C_old will receive log entries, but their votes might not count for the C_old majority.

2.  **Transition to New Configuration (C_new):** Once the Joint Consensus entry is committed, the leader then proposes a second configuration entry containing only C_new. Once this entry is committed, the cluster operates solely under C_new rules. This two-phase commit protocol ensures that the cluster remains consistent throughout the membership change process, even in the presence of failures.

## Client Interaction:
Clients in Raft interact with the cluster by sending requests to the leader. Raft ensures that all client commands are executed in the same order and at most once, providing a strong consistency model.

**Client Request Flow:**

1.  **Locating the Leader:** Clients initially send their requests to an arbitrary server in the cluster. If that server is not the leader, it rejects the request and provides the client with the identity of the current leader (if known). If the leader is unknown or has failed, the client retries until it successfully contacts the leader.

2.  **Command Execution:** Once the client connects to the leader:
    *   The leader appends the client's command as a new entry to its log.
    *   It then replicates this entry to its followers (as described in Log Replication).
    *   Once the log entry is committed (replicated to a majority of servers), the leader applies the command to its state machine and sends a response back to the client.

3.  **Idempotence:** To handle duplicate client requests (e.g., due to retries), Raft implementations often make client commands idempotent. This means that executing the same command multiple times produces the same result as executing it once, preventing unintended side effects.



