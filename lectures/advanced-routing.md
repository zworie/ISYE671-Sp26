# ISYE 671: Linear Optimization and Network Flows
# Lecture Notes — Advanced Routing and Combinatorial Models

**Northern Illinois University — Spring 2026**
**Instructor: Dr. Ziteng Wang**

---

## 1. Introduction and Motivation

In earlier lectures, we studied network flow models — shortest path, max flow, MCNF, transportation, and assignment — where the underlying structure is a flow on arcs. We also studied integer programming models for facility location, set covering, capital budgeting, and scheduling.

In this lecture, we turn to a family of **combinatorial optimization problems** that combine integer programming with network structure: *routing problems*. These problems ask us to find optimal tours or routes through a network, subject to various operational constraints. They arise naturally in logistics, supply chain, manufacturing, and healthcare.

The central models are:

- **Travelling Salesman Problem (TSP)**: Find the shortest tour visiting every city exactly once.
- **Vehicle Routing Problem (VRP)**: Partition customers among vehicles and route each vehicle optimally.
- **Variants**: Time windows, pickup-and-delivery, capacitated routing, split deliveries.

These problems are among the most studied in operations research and combinatorial optimization. They are NP-hard in general, meaning no known polynomial-time algorithm exists. Yet, modern MIP solvers (such as Gurobi, invoked through AMPL) can solve practical instances of moderate size, and understanding the formulations is essential for modeling real systems.

> **Connection to prior material**: TSP can be viewed as an *assignment problem* (which we studied in network flows) with additional constraints that prevent disconnected subtours. VRP extends TSP by incorporating *capacity constraints* similar to those in our facility location models.

---

## 2. The Travelling Salesman Problem (TSP)

### 2.1 Problem Statement

Given a set of $n$ cities and a distance (or cost) matrix $c_{ij}$ representing the cost of travelling from city $i$ to city $j$, find a **Hamiltonian cycle** — a tour that visits every city exactly once and returns to the starting city — of minimum total cost.

**Example (Rardin-style)**: A medical equipment service technician based in Chicago must visit hospitals in Rockford, DeKalb, Aurora, Joliet, and Kankakee for quarterly maintenance. Each trip must start and end in Chicago. The technician wants to minimize total driving distance.

| From\To   | Chicago | Rockford | DeKalb | Aurora | Joliet | Kankakee |
|-----------|---------|----------|--------|--------|--------|----------|
| Chicago   | —       | 89       | 66     | 41     | 46     | 60       |
| Rockford  | 89      | —        | 52     | 72     | 108    | 141      |
| DeKalb    | 66      | 52       | —      | 35     | 80     | 112      |
| Aurora    | 41      | 72       | 35     | —      | 48     | 85       |
| Joliet    | 46      | 108      | 80     | 48     | —      | 42       |
| Kankakee  | 60      | 141      | 112    | 85     | 42     | —        |

### 2.2 Assignment-Based Formulation (with Subtour Elimination)

**Decision Variables:**

$$x_{ij} = \begin{cases} 1 & \text{if the tour travels directly from city } i \text{ to city } j \\ 0 & \text{otherwise} \end{cases}$$

for all $i, j \in \{1, 2, \ldots, n\}$, $i \neq j$.

**Formulation:**

$$\min \sum_{i=1}^{n} \sum_{\substack{j=1 \\ j \neq i}}^{n} c_{ij} \, x_{ij}$$

Subject to:

$$\sum_{\substack{j=1 \\ j \neq i}}^{n} x_{ij} = 1 \quad \forall \, i = 1, \ldots, n \qquad \text{(leave each city exactly once)}$$

$$\sum_{\substack{i=1 \\ i \neq j}}^{n} x_{ij} = 1 \quad \forall \, j = 1, \ldots, n \qquad \text{(enter each city exactly once)}$$

$$x_{ij} \in \{0, 1\} \quad \forall \, i \neq j$$

**Why this is not enough**: Without additional constraints, the formulation is simply an *assignment problem* on a bipartite graph. The optimal solution may contain **subtours** — disconnected cycles that cover all cities but do not form a single connected tour.

For instance, with 6 cities, the assignment solution might return two separate loops: $(1 \to 3 \to 5 \to 1)$ and $(2 \to 4 \to 6 \to 2)$. Each city is visited once, but the solution is not a valid tour.

### 2.3 Subtour Elimination Constraints

There are two classical approaches to eliminating subtours.

**Approach 1: Dantzig–Fulkerson–Johnson (DFJ) Subtour Elimination**

For every proper subset $S \subset \{1, \ldots, n\}$ with $2 \leq |S| \leq n - 2$:

$$\sum_{i \in S} \sum_{j \in S, \, j \neq i} x_{ij} \leq |S| - 1$$

This says: within any subset of cities, the number of arcs used cannot form a complete cycle through that subset. An equivalent form requires at least one arc leaving every proper subset:

$$\sum_{i \in S} \sum_{j \notin S} x_{ij} \geq 1 \quad \forall \, S \subset \{1, \ldots, n\}, \; 2 \leq |S| \leq n-2$$

**Disadvantage**: The number of subsets grows exponentially ($2^n - 2n - 2$ constraints). For even moderate $n$, we cannot enumerate all of them upfront. In practice, these are added *lazily* — solve without them, check for subtours, add the violated constraint, and re-solve. This is called a **cutting plane** or **callback** approach.

**Approach 2: Miller–Tucker–Zemlin (MTZ) Formulation**

Introduce auxiliary variables $u_i$ for $i = 2, \ldots, n$ representing the *position* of city $i$ in the tour:

$$u_i - u_j + n \cdot x_{ij} \leq n - 1 \quad \forall \, i, j \in \{2, \ldots, n\}, \; i \neq j$$

$$1 \leq u_i \leq n - 1 \quad \forall \, i = 2, \ldots, n$$

**Interpretation**: If city $i$ is visited immediately before city $j$ (i.e., $x_{ij} = 1$), then $u_i - u_j \leq -1$, forcing $u_j \geq u_i + 1$. This imposes a sequencing order that prevents subtours not passing through city 1. City 1 is the designated depot and does not need a $u$ variable.

**Advantage**: Polynomial number of constraints ($O(n^2)$), so the model can be written out completely.

**Disadvantage**: The LP relaxation of MTZ is typically much weaker than DFJ, leading to slower solution times for larger instances.

> **For this course**: We will use the MTZ formulation for computational exercises because it is self-contained and can be directly implemented in AMPL without callbacks. Be aware that for large instances, DFJ with lazy constraints (or specialized TSP solvers) is preferred in practice.

### 2.4 Complete MTZ-TSP Formulation

$$\min \sum_{i=1}^{n} \sum_{\substack{j=1 \\ j \neq i}}^{n} c_{ij} \, x_{ij}$$

Subject to:

$$\sum_{\substack{j=1 \\ j \neq i}}^{n} x_{ij} = 1 \quad \forall \, i$$

$$\sum_{\substack{i=1 \\ i \neq j}}^{n} x_{ij} = 1 \quad \forall \, j$$

$$u_i - u_j + n \cdot x_{ij} \leq n - 1 \quad \forall \, i, j \in \{2, \ldots, n\}, \; i \neq j$$

$$1 \leq u_i \leq n - 1 \quad \forall \, i = 2, \ldots, n$$

$$x_{ij} \in \{0, 1\} \quad \forall \, i \neq j$$

### 2.5 Worked Example: Illinois Service Tour

Applying the MTZ formulation to our 6-city example:

- **Variables**: $6 \times 5 = 30$ binary $x_{ij}$ variables, plus 5 continuous $u_i$ variables.
- **Constraints**: 6 outflow + 6 inflow + $5 \times 4 = 20$ MTZ + 5 bound constraints = 37 constraints.
- **Optimal tour**: Chicago → Aurora → DeKalb → Rockford → (return via) Chicago, then Joliet → Kankakee (exact tour depends on data). The solver finds the minimum-distance Hamiltonian cycle.

*(The full AMPL implementation is provided in the companion Colab notebook.)*

---

## 3. The Vehicle Routing Problem (VRP)

### 3.1 Problem Statement

The VRP generalizes the TSP to multiple vehicles. Given:

- A depot (node 0) and $n$ customer nodes $\{1, 2, \ldots, n\}$
- A fleet of $K$ vehicles, each with capacity $Q$
- Customer demands $d_i$ for each customer $i$
- Travel costs $c_{ij}$ between all pairs of nodes

Find $K$ routes, each starting and ending at the depot, such that every customer is visited exactly once, no vehicle exceeds its capacity, and total travel cost is minimized.

**Example**: A regional food bank operates 3 delivery trucks, each capable of carrying 2,000 lbs. There are 12 partner pantries across northern Illinois, each requesting between 200 and 600 lbs of food. The food bank wants to minimize total fuel costs while ensuring every pantry is served.

### 3.2 Capacitated VRP (CVRP) Formulation

**Sets:**

- $V = \{0, 1, \ldots, n\}$: all nodes (0 = depot)
- $V' = \{1, \ldots, n\}$: customer nodes only
- $K$: number of vehicles (indexed by $k = 1, \ldots, K$)

**Parameters:**

- $c_{ij}$: travel cost from node $i$ to node $j$
- $d_i$: demand of customer $i$ (with $d_0 = 0$)
- $Q$: vehicle capacity

**Decision Variables:**

$$x_{ijk} = \begin{cases} 1 & \text{if vehicle } k \text{ travels directly from } i \text{ to } j \\ 0 & \text{otherwise} \end{cases}$$

**Formulation:**

$$\min \sum_{k=1}^{K} \sum_{i \in V} \sum_{\substack{j \in V \\ j \neq i}} c_{ij} \, x_{ijk}$$

Subject to:

$$\sum_{k=1}^{K} \sum_{\substack{j \in V \\ j \neq i}} x_{ijk} = 1 \quad \forall \, i \in V' \qquad \text{(each customer visited once)}$$

$$\sum_{j \in V'} x_{0jk} = 1 \quad \forall \, k = 1, \ldots, K \qquad \text{(each vehicle leaves depot)}$$

$$\sum_{i \in V'} x_{i0k} = 1 \quad \forall \, k = 1, \ldots, K \qquad \text{(each vehicle returns to depot)}$$

$$\sum_{\substack{i \in V \\ i \neq j}} x_{ijk} - \sum_{\substack{i \in V \\ i \neq j}} x_{jik} = 0 \quad \forall \, j \in V', \; \forall \, k \qquad \text{(flow conservation)}$$

$$\sum_{i \in V'} d_i \left( \sum_{\substack{j \in V \\ j \neq i}} x_{ijk} \right) \leq Q \quad \forall \, k \qquad \text{(capacity)}$$

$$x_{ijk} \in \{0, 1\} \quad \forall \, i, j, k$$

Plus subtour elimination constraints (MTZ-style with position variables per vehicle, or DFJ-style subset constraints).

**Note on symmetry**: If vehicles are identical, the formulation has symmetry — swapping the routes assigned to vehicles $k_1$ and $k_2$ gives an equivalent solution. This symmetry can slow down branch-and-bound. A common fix is to add symmetry-breaking constraints, such as requiring that vehicle 1 serves the lowest-indexed customer among all vehicles.

### 3.3 Relationship Between TSP and VRP

| Feature | TSP | VRP |
|---------|-----|-----|
| Number of vehicles | 1 | $K \geq 1$ |
| Depot | Optional (any start) | Required (node 0) |
| Capacity | None | $Q$ per vehicle |
| Core structure | Single Hamiltonian cycle | $K$ depot-rooted cycles covering all customers |
| Special case | VRP with $K=1$, $Q = \infty$ | — |

The TSP is a special case of VRP. Conversely, VRP can be decomposed into a partitioning phase (assign customers to vehicles) and a routing phase (solve a TSP per vehicle), though this decomposition is suboptimal in general.

---

## 4. VRP Variants

Real logistics problems rarely match the basic CVRP exactly. Several practically important variants extend the base model.

### 4.1 VRP with Time Windows (VRPTW)

Each customer $i$ has a time window $[a_i, b_i]$ during which service must begin. A vehicle arriving before $a_i$ must wait; arriving after $b_i$ is infeasible.

**Additional variables**: $t_{ik}$ = time at which vehicle $k$ begins service at customer $i$.

**Additional constraints**:

$$a_i \leq t_{ik} \leq b_i \quad \forall \, i \in V', \; \forall \, k$$

$$t_{ik} + s_i + \tau_{ij} - M(1 - x_{ijk}) \leq t_{jk} \quad \forall \, i, j \in V, \; \forall \, k$$

where $s_i$ is the service time at customer $i$, $\tau_{ij}$ is the travel time from $i$ to $j$, and $M$ is a sufficiently large constant. The second constraint links arrival times: if vehicle $k$ goes from $i$ to $j$, it cannot arrive at $j$ before finishing service at $i$ plus travel time.

**Application**: Home healthcare scheduling — nurses must visit patients within preferred time slots while minimizing total driving.

### 4.2 Pickup and Delivery Problem (PDP)

Each request $r$ has an origin (pickup node $p_r$) and a destination (delivery node $d_r$). A vehicle must pick up the load at $p_r$ before delivering it to $d_r$, and both nodes must be served by the same vehicle.

**Additional constraints** (precedence and pairing):

$$\sum_{\substack{j \in V \\ j \neq p_r}} x_{p_r, j, k} = \sum_{\substack{j \in V \\ j \neq d_r}} x_{d_r, j, k} \quad \forall \, r, \; \forall \, k \qquad \text{(same vehicle)}$$

$$u_{p_r} < u_{d_r} \quad \forall \, r \qquad \text{(pickup before delivery)}$$

**Application**: Ride-sharing and on-demand transit systems — passengers must be picked up before being dropped off, using shared vehicles.

### 4.3 Split Delivery VRP

In the standard VRP, each customer is served by exactly one vehicle. The **split delivery** variant allows a customer's demand to be split across multiple vehicles. This can reduce total cost when some customers have demands close to vehicle capacity.

The formulation replaces the binary assignment constraint with:

$$\sum_{k=1}^{K} y_{ik} = d_i \quad \forall \, i \in V'$$

where $y_{ik} \geq 0$ is the quantity delivered to customer $i$ by vehicle $k$, and the linking constraints ensure that a vehicle visits customer $i$ only if $y_{ik} > 0$.

---

## 5. Modeling Considerations and Practical Tips

### 5.1 Model Size and Tractability

| Problem | Binary Variables | Constraints (approx.) | Typical solvable size (Gurobi, minutes) |
|---------|-----------------|----------------------|----------------------------------------|
| TSP (MTZ) | $n^2$ | $O(n^2)$ | $n \leq 30\text{–}50$ |
| CVRP | $n^2 K$ | $O(n^2 K)$ | $n \leq 20\text{–}30$ with $K \leq 5$ |
| VRPTW | $n^2 K + nK$ | $O(n^2 K)$ | $n \leq 15\text{–}25$ with $K \leq 5$ |

For larger instances, heuristics (nearest-neighbor, savings algorithm) and metaheuristics (genetic algorithms, simulated annealing, tabu search) are used in practice. Commercial solvers like Gurobi increasingly support these through built-in heuristic callbacks.

### 5.2 Strengthening Formulations

Several techniques tighten the LP relaxation and speed up branch-and-bound:

- **Tighter MTZ bounds**: Replace $u_i - u_j + n \cdot x_{ij} \leq n-1$ with $u_i - u_j + (n-1) x_{ij} + (n-3) x_{ji} \leq n - 2$ (the *lifted MTZ* inequality).
- **Capacity cuts**: For CVRP, require that the number of vehicles entering any subset $S$ is at least $\lceil \sum_{i \in S} d_i / Q \rceil$.
- **Symmetry breaking**: Order vehicles by their first customer index.

### 5.3 Connecting to Earlier Material

The routing formulations in this lecture draw on concepts from earlier weeks:

| Concept | Earlier Lecture | Role in Routing |
|---------|----------------|-----------------|
| Assignment problem | Network flows | TSP without subtour elimination is an assignment |
| Big-M constraints | IP modeling | MTZ subtour elimination, time window linking |
| Binary variables for selection | IP modeling (set covering, facility location) | Arc selection, vehicle-customer assignment |
| Network flow conservation | MCNF | Flow balance at each node in VRP |

---

## 6. Exercises

**Exercise 1 (TSP Formulation)**. A courier must visit 8 offices in the Chicago suburbs. Write the complete MTZ formulation. How many binary variables and constraints does the model have? *(Do not solve; just formulate.)*

**Exercise 2 (TSP Implementation)**. Using the Illinois service tour data from Section 2.5, implement and solve the TSP in AMPL with Gurobi. Report the optimal tour and its total distance. Verify that no subtours exist in your solution.

**Exercise 3 (VRP Modeling)**. The food bank from Section 3.1 has 12 pantries with the following demands (in lbs): 450, 300, 550, 200, 400, 350, 600, 250, 500, 300, 400, 350. Each truck has capacity 2,000 lbs. Formulate the CVRP. What is the minimum number of trucks needed?

**Exercise 4 (Time Windows)**. Extend your VRP formulation from Exercise 3 by adding the constraint that pantries 1–4 must be served between 8:00 AM and 11:00 AM, pantries 5–8 between 10:00 AM and 1:00 PM, and pantries 9–12 between 12:00 PM and 3:00 PM. Write the additional constraints. Discuss: do overlapping windows make the problem easier or harder? Why?

**Exercise 5 (Modeling Judgment)**. A hospital system wants to route visiting nurses to patients' homes. Each nurse has a maximum shift of 8 hours, can carry limited medical supplies, and some patients require specific nurse certifications. Which VRP variant is most appropriate? Describe the sets, parameters, and constraints you would add to the base CVRP formulation. *(Formulate; do not solve.)*

---

## References

- Rardin, R.L. *Optimization in Operations Research*, 2nd edition. Chapter 11 (integer programming models), Chapter 10 (network models).
- Toth, P. and Vigo, D. *The Vehicle Routing Problem*. SIAM, 2002.
- Miller, C.E., Tucker, A.W., and Zemlin, R.A. "Integer programming formulation of traveling salesman problems." *Journal of the ACM*, 7(4):326–329, 1960.
- Dantzig, G.B., Fulkerson, D.R., and Johnson, S.M. "Solution of a large-scale traveling-salesman problem." *Operations Research*, 2(4):393–410, 1954.
