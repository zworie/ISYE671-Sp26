# ISYE 671: Advanced Topics — Bilevel Optimization

**Northern Illinois University — Spring 2026**
**Instructor: Dr. Ziteng Wang**

---

## 1. Motivation: When Two Decision-Makers Interact

All optimization problems studied so far have a single decision-maker: one objective, one set of constraints, one solver. But many real-world settings involve **two decision-makers acting sequentially**, where the second player reacts optimally to whatever the first player decides.

**Motivating Example — Toll Road Pricing:**
A highway authority (the *leader*) sets tolls on a road network. Commuters (collectively, the *follower*) then choose routes to minimize their own travel cost, using or avoiding the toll roads accordingly. The authority wants to maximize revenue, but it cannot ignore how drivers will react — setting tolls too high drives commuters to alternate routes, reducing revenue. The authority must *anticipate the followers' optimal response* when making its own decision.

This is the structure of a **bilevel optimization problem**: the leader's decision space is constrained by the condition that the follower is solving their own optimization problem.

Other natural examples:

- **Competitive pricing**: A company sets prices; consumers choose suppliers to minimize cost.
- **Network interdiction**: A defender allocates resources to protect a network; an attacker then disrupts it optimally.
- **Facility location with strategic customers**: A firm opens warehouses; customers independently choose the nearest (cheapest) facility.
- **Hyperparameter tuning in machine learning**: An outer optimizer selects hyperparameters; an inner optimizer trains the model.
- **Tax policy design**: A government sets tax rates; firms respond by relocating, investing, or restructuring.

---

## 2. Problem Formulation

### 2.1 General Bilevel Program

Let $x \in \mathbb{R}^n$ be the **leader's decision** and $y \in \mathbb{R}^m$ be the **follower's decision**. The general bilevel program is:

$$
\begin{aligned}
\min_{x,\, y} \quad & F(x, y) \\
\text{subject to} \quad & G(x, y) \leq 0 \\
& y \in \arg\min_{y'} \bigl\{ f(x, y') : g(x, y') \leq 0 \bigr\}
\end{aligned}
$$

The key element is the **lower-level constraint**: $y$ must be an *optimal solution* to the follower's problem given $x$. This is not a standard feasibility constraint — it requires $y$ to solve an entire optimization problem parametrized by $x$.

**Notation:**
- $F(x, y)$: leader's objective (upper level)
- $G(x, y) \leq 0$: leader's constraints
- $f(x, y)$: follower's objective (lower level)
- $g(x, y) \leq 0$: follower's constraints

### 2.2 The Toll Road Problem (Formal)

Let $A$ be the set of toll arcs, $P$ the set of paths, $c_p$ the free travel cost on path $p$, and $\delta_{ap} = 1$ if arc $a$ is on path $p$. The leader charges toll $t_a \geq 0$ on each arc.

**Leader (authority):**
$$\max_{t \geq 0} \sum_{a \in A} t_a \sum_{p} \delta_{ap} f_p^*
$$

where $f_p^*$ is determined by the follower's response.

**Follower (commuters):**
$$\min_{f \geq 0} \sum_p \left(c_p + \sum_a t_a \delta_{ap}\right) f_p \quad \text{s.t. flow conservation, demand satisfaction}$$

The follower solves a shortest-path / min-cost flow problem for fixed $t$. The leader must set $t$ before observing $f^*$.

---

## 3. Mathematical Structures and Solution Approaches

### 3.1 The Core Difficulty

Bilevel programs are, in general, **NP-hard** — even when both levels are linear programs. The difficulty comes from the lower-level optimality condition, which is:
- Non-convex (the feasible set of $x, y$ pairs satisfying the lower-level optimality is generally non-convex)
- Discontinuous (small changes in $x$ can cause the follower's optimal $y$ to jump)

The optimistic convention: when the follower has multiple optimal solutions, the leader assumes the most favorable one is chosen (standard in theory; not always realistic).

### 3.2 Single-Level Reformulation via KKT Conditions

When the **lower-level problem is a linear program or convex program**, it can be replaced by its **KKT optimality conditions**, converting the bilevel program into a single-level (but nonconvex) mathematical program with complementarity constraints (MPCC).

For a lower-level LP:
$$\min_y \ c^\top y \quad \text{s.t.} \quad Ay \geq b(x), \; y \geq 0$$

The KKT conditions are:
$$A^\top \lambda = c, \quad \lambda \geq 0, \quad y \geq 0, \quad \lambda^\top (Ay - b(x)) = 0$$

The **complementarity condition** $\lambda_i (a_i^\top y - b_i) = 0$ means either the dual variable is zero or the constraint is active — but not both can be strictly positive. This is a **nonlinear constraint** and is the source of computational difficulty.

**Linearizing complementarity with binary variables:** For bounded variables, complementarity $0 \leq u \perp v \geq 0$ can be linearized as:
$$u \leq M(1 - z), \quad v \leq Mz, \quad z \in \{0, 1\}$$

using a big-M constant $M$. This transforms the bilevel LP into a **mixed-integer linear program (MILP)**, solvable by Gurobi — but at the cost of introducing binary variables for each complementarity pair.

> **Connection to ISYE 671**: The KKT linearization uses exactly the big-M techniques from our integer programming unit. The follower's LP duality (strong duality) is also central: at optimality, the primal and dual objectives are equal, providing an additional linear constraint that tightens the reformulation.

### 3.3 Network Interdiction as a Bilevel MIP

**Problem**: A defender can remove (interdict) up to $B$ arcs from a network. An attacker then finds the shortest path through the remaining network. The defender wants to maximize the shortest path length the attacker must travel.

**Leader (defender):**
$$\max_{z \in \{0,1\}^{|A|}} \quad d^*(z) \quad \text{s.t.} \quad \sum_a z_a \leq B$$

where $z_a = 1$ means arc $a$ is interdicted (removed), and $d^*(z)$ is the attacker's shortest path length.

**Follower (attacker):**
$$d^*(z) = \min_{f} \sum_a (1 - z_a) c_a f_a \quad \text{s.t. shortest-path flow constraints}$$

Applying LP duality to the follower (shortest path LP is a min-cost flow LP), the follower's optimal value equals the maximum over dual variables. This converts the problem into a **single-level integer program** solvable in AMPL/Gurobi.

**Example data:** Five-node network with arcs, capacities, and costs. Budget $B = 2$.

| Arc | From | To | Cost | Interdicted? |
|-----|------|----|------|-------------|
| 1 | S | 1 | 3 | — |
| 2 | S | 2 | 5 | — |
| 3 | 1 | T | 4 | — |
| 4 | 2 | T | 2 | — |
| 5 | 1 | 2 | 1 | — |

Without interdiction, the shortest path S→1→2→T has length 7. With $B = 2$ optimal interdictions (arcs 3 and 4), the attacker is forced to a path of length 12.

---

## 4. Key Properties and Complexity

| Property | Detail |
|----------|--------|
| Complexity | NP-hard in general; $\Sigma_2^p$-hard (harder than NP) for integer leaders |
| Special cases | LP-LP bilevel: polynomial with strong duality; convex-convex: KKT reformulation |
| Optimal solution | May not exist if follower's problem is unbounded or infeasible for some $x$ |
| Reformulation | KKT + big-M → MILP (exact but weak bounds); penalty methods (approximate) |
| Software | GAMS/MPEC libraries; Gurobi (after manual KKT reformulation); specialized solvers (PAVER, MiBS) |

---

## 5. Practical Applications

**Supply chain and pricing:**
A manufacturer sets wholesale prices; retailers independently optimize their own purchasing and selling decisions. The manufacturer must anticipate retail behavior. Solved as a bilevel LP or bilevel MIP depending on the retailer's problem structure.

**Energy markets:**
Electricity generators bid into a market; a market operator clears the market to minimize cost subject to grid constraints. Generators choose bids anticipating the clearing mechanism. Bilevel models are used to study strategic bidding and market power.

**Transportation and infrastructure:**
Urban planners design road networks or transit systems; commuters then choose routes. The classic *network design problem* is bilevel: the designer maximizes social welfare, the users minimize personal cost (Wardrop equilibrium conditions). Used by the Chicago Metropolitan Agency for Planning and similar bodies.

**Adversarial robustness and cybersecurity:**
A defender allocates security resources across a network; an attacker then chooses the most damaging attack vector. The defender must anticipate the attacker's optimal response. Critical infrastructure protection (power grids, water networks) uses this framework.

**Machine learning — hyperparameter optimization:**
Outer problem: choose hyperparameters $\lambda$ to minimize validation loss. Inner problem: train model weights $\theta$ to minimize training loss given $\lambda$. Bilevel structure is explicit; gradient-based bilevel methods (implicit differentiation through the inner optimization) are the state of the art in meta-learning and neural architecture search.

---

## 6. Recent Progress and Open Frontiers

**Exact algorithms:** Branch-and-bound algorithms designed for bilevel MIPs (e.g., Fischetti et al., 2017; Tahernejad et al., 2020) incorporate cuts valid for the bilevel feasible set. Gurobi's general-purpose MILP engine can solve KKT-reformulated bilevel LPs to optimality.

**Gradient-based bilevel optimization:** When both levels are smooth (e.g., neural network training), implicit differentiation allows computing $\nabla_x F$ through the inner optimum without unrolling the inner solver. This underpins meta-learning (MAML), neural architecture search (DARTS), and data poisoning attacks.

**Data-driven bilevel programs:** The follower's behavior is not fully known but can be estimated from data (inverse optimization). This integrates statistical learning into the bilevel framework.

**Distributionally robust bilevel programs:** Combining bilevel structure with distributional uncertainty — a tri-level problem (leader, nature, follower). Active research area with applications in robust market design and infrastructure protection under uncertainty.

---

## 7. Summary

| Dimension | Bilevel Optimization |
|-----------|---------------------|
| **Setting** | Two decision-makers: leader acts first, follower reacts optimally |
| **Key constraint** | $y \in \arg\min$ (follower's problem) — not a standard linear constraint |
| **Math tools** | KKT conditions, LP duality, big-M linearization, complementarity |
| **Computation** | Reformulate to MILP (KKT + big-M) for LP lower levels; gradient methods for smooth lower levels |
| **Hardness** | NP-hard in general; harder than single-level MIP |
| **Applications** | Pricing, network design, interdiction, adversarial ML, energy markets |
| **Connection to ISYE 671** | LP duality, big-M, network flows — all directly used in reformulation |

> **Key insight**: Bilevel optimization is not a niche subfield — it is the natural formulation whenever an optimizer must anticipate the rational response of another agent. The tools to solve it are largely the LP and IP tools already in your toolkit.

---

## References

- Dempe, S. *Foundations of Bilevel Programming*. Springer, 2002.
- Colson, B., Marcotte, P., and Savard, G. "An overview of bilevel optimization." *Annals of Operations Research*, 153(1):235–256, 2007.
- Fischetti, M., Ljubić, I., Monaci, M., and Sinnl, M. "A new general-purpose algorithm for mixed-integer bilevel linear programs." *Operations Research*, 65(6):1615–1637, 2017.
- Smith, J.C. and Lim, C. "Algorithms for network interdiction and fortification games." In *Pardalos and Rassia (eds.), Optimization Theory, Decision Making, and OR Applications*, 2012.
- Franceschi, L. et al. "Bilevel programming for hyperparameter optimization and meta-learning." *ICML*, 2018.
