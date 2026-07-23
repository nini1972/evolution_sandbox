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

