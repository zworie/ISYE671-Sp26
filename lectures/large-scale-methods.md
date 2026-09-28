# ISYE 671: Linear Optimization and Network Flows
# Lecture Notes — Large-Scale Optimization Methods

**Northern Illinois University — Spring 2026**
**Instructor: Dr. Ziteng Wang**

---

## 1. Introduction: When Standard Solvers Are Not Enough

Throughout this course, we have formulated LP, IP, and network flow models and solved them directly using AMPL with Gurobi. For problems of moderate size, this works remarkably well — modern solvers can handle LPs with hundreds of thousands of variables routinely, and well-structured sparse LPs with millions of variables are often tractable. Integer programs with thousands of binary variables frequently solve in seconds, though solution time is highly problem-dependent.

However, many real-world problems have structural features that make direct solution impractical:

- **Too many variables to enumerate**: A cutting stock problem may have thousands of feasible cutting patterns. A vehicle routing problem with 200 customers has billions of potential routes. We cannot list all possible columns upfront.
- **Block structure with linking constraints**: A multi-period supply chain has independent subproblems per period, linked by inventory balance constraints. A stochastic program has independent scenarios, linked by first-stage decisions. The constraint matrix is mostly block-diagonal — almost decomposable, but not quite.
- **Complicating constraints**: An otherwise easy problem (e.g., a collection of independent knapsacks) is made hard by a handful of constraints that couple all the variables. Removing those constraints would make the problem trivial.

This lecture introduces four methods that exploit such structure:

1. **Column generation** (Section 2) — an algorithm for LPs with too many variables to enumerate.
2. **Dantzig-Wolfe decomposition** (Section 3) — a reformulation that converts block-structured LPs with many constraints into LPs with many variables, then solves them with column generation.
3. **Benders decomposition** (Section 4) — the "dual" of Dantzig-Wolfe: projects out a subset of variables, replacing them with iteratively generated constraints (cuts).
4. **Lagrangian relaxation** (Section 5) — a general technique for obtaining bounds by moving complicating constraints into the objective function. Not a decomposition method; not limited to large-scale problems.

> **Connection to prior material**: These methods do not replace what we have learned — they *build upon it*. Each method solves sequences of smaller LPs or IPs using the same solvers (Gurobi through AMPL) we have been using all semester. The insight is in how to break big problems into manageable pieces.

### 1.1 Do We Still Need These Methods? (The Computing Power Question)

Dantzig-Wolfe decomposition was published in 1960. Benders decomposition in 1962. Lagrangian relaxation gained prominence in the 1970s. These methods were developed when a "large" LP had a few hundred variables and solving it could take hours on a mainframe. Today, commercial solvers like Gurobi can handle LPs with hundreds of thousands of variables routinely, and well-structured sparse problems with millions of variables are often tractable. So a natural question arises: **with modern computing power, do we still need decomposition methods?**

The answer is emphatically **yes**, for several reasons:

**Problem sizes have grown faster than computing power.** Moore's Law gave us roughly a $10^6$-fold increase in computing speed over 50 years. But the problems we want to solve have grown even faster. A stochastic supply chain model with 1,000 scenarios, 500 products, and 200 locations generates billions of variables. An airline crew scheduling problem with 5,000 flights has more feasible crew pairings than atoms in the universe. No amount of raw computing power can enumerate these.

**The structure is the point, not the size.** Decomposition methods don't just make big problems solvable — they make them *understandable*. A Benders decomposition of a stochastic program separates the strategic decision ("which warehouses to open") from the operational response ("how to allocate demand in each scenario"). A Dantzig-Wolfe decomposition separates the global coordination ("how much total production") from the local optimization ("how each factory schedules its machines"). This structural insight is valuable even when the problem *could* be solved as a single formulation.

**Modern applications *require* decomposition.** Many contemporary optimization problems are inherently distributed: different data owners control different parts of the model (e.g., hospitals in a regional health network, airlines in an alliance). Decomposition methods enable **privacy-preserving optimization** where each party solves its own subproblem without sharing proprietary data. The master only sees aggregated outputs.

**Decomposition enables parallelism.** Modern hardware has shifted from faster single cores to more parallel cores (GPUs, cloud computing). Decomposition methods are naturally parallel — Benders subproblems and Lagrangian subproblems can be distributed across thousands of processors. This is increasingly how the largest optimization problems are solved in practice.

**Machine learning integration requires structure.** As discussed in the ML & Optimization lecture, modern approaches use ML to improve optimization (learning to branch, predicting warm starts, selecting cuts). These ML methods work best when the optimization has *structure* that ML can learn — exactly the structure that decomposition methods exploit.

In short: decomposition methods are more relevant today than when they were invented. The methods themselves are timeless; what changes is the scale and context of their application.

### 1.2 How Large Can Optimization Problems Get?

To appreciate why large-scale methods matter, consider the scale of real-world optimization problems:

**Airline crew scheduling.** A major airline operates 3,000–5,000 daily flights with 10,000+ crew members across multiple crew types (pilots, first officers, flight attendants). Each feasible crew schedule (a "pairing") is a multi-day sequence of flights respecting duty-time regulations, rest requirements, base constraints, and union rules. The number of feasible pairings is astronomically large — easily $10^{15}$ or more. The optimization selects a minimum-cost subset of pairings that covers every flight exactly once. This is solved daily via column generation (each column = a crew pairing, pricing subproblem = shortest path with resource constraints). Without column generation, the problem is intractable.

**Electricity grid unit commitment.** An independent system operator (ISO) must decide which power plants to turn on (binary) and how much each produces (continuous) for each hour of the next day or week, across hundreds of generators and thousands of transmission lines. A typical day-ahead market clears a MIP with 500,000+ variables and 1,000,000+ constraints. With stochastic versions incorporating renewable energy uncertainty (wind/solar forecasts across 50–100 scenarios), the problem grows to tens of millions of variables. Benders decomposition and Lagrangian relaxation are standard tools.

**Telecommunications network design.** A telecom company must route data traffic across a network with thousands of nodes and tens of thousands of links, satisfying bandwidth demands for millions of origin-destination pairs. The multicommodity flow formulation has variables indexed by (commodity × link), easily reaching $10^8$ variables. Capacity expansion decisions (which links to upgrade) add integer variables. Dantzig-Wolfe decomposition by commodity and Lagrangian relaxation of linking capacity constraints are standard approaches.

**Supply chain and logistics.** A global retailer manages 100,000+ products across 5,000+ stores, 50+ distribution centers, and 500+ suppliers, with decisions about inventory, replenishment, transportation, and pricing over 52 weekly periods. The deterministic model alone has hundreds of millions of variables. Adding demand uncertainty with scenarios creates stochastic programs with billions of variables. These are decomposed by product, by region, or by time period.

**Vehicle routing at scale.** Amazon, UPS, and FedEx solve vehicle routing problems daily with 100,000+ packages, 10,000+ vehicles, and time windows. The number of feasible routes is combinatorially explosive. Column generation over route variables, combined with branch-and-price, is the state of the art. Even with the most powerful solvers, these problems cannot be solved as a single formulation.

**Radiation therapy planning.** As we saw in the IMRT example (Section 2.5), a realistic treatment plan involves hundreds of beam angles, each with hundreds of beamlets, delivering dose to thousands of tissue voxels. The number of feasible apertures (beamlet subsets) is exponential in the number of beamlets. Column generation selects the small number of apertures actually needed.

**Healthcare operations.** A hospital network scheduling nurses, surgeons, operating rooms, and patient admissions across 20 hospitals, 52 weeks, and multiple shift types generates integer programs with millions of binary variables. Stochastic versions incorporating patient demand uncertainty and pandemic scenarios multiply the size by 100×. Decomposition by hospital (Dantzig-Wolfe) or by scenario (Benders) is essential.

The common thread: these problems are large not because someone chose to make them large, but because the underlying system *is* large — many facilities, many time periods, many products, many scenarios, many possible configurations. The structure of the real system (facilities are independent except through shared resources; scenarios are independent except through first-stage decisions; time periods are independent except through inventory) is exactly the structure that decomposition methods exploit.

---

## 2. Column Generation

### 2.1 The Core Idea

Many optimization problems involve **selecting or combining from an enormous set of candidates**:

- Which **cutting patterns** should we use to cut raw material into requested sizes?
- Which **beam configurations** should we use in radiation therapy?
- Which **vehicle routes** should we assign to serve all customers?
- Which **crew schedules** should we assign to cover all flights?

In each case, the number of candidates (columns/variables) is so large that we cannot enumerate them all upfront. But most candidates will not be used in the optimal solution. **Column generation** exploits this: start with a small subset of columns, solve the LP, and then intelligently generate only those new columns that can improve the objective.

### 2.2 The Restricted Master Problem and Pricing

Consider an LP with far more columns than we can enumerate:

$$\min \; c^\top x \quad \text{subject to} \quad Ax = b, \quad x \geq 0$$

We solve a **restricted master problem (RMP)** that includes only a manageable subset of columns:

$$\min \; c_B^\top x_B \quad \text{subject to} \quad A_B x_B = b, \quad x_B \geq 0$$

After solving the RMP, we obtain **dual variables** $\pi$ (one per constraint). From LP optimality theory, a column $j$ not currently in the RMP can improve the objective if and only if its **reduced cost** is negative:

$$\bar{c}_j = c_j - \pi^\top a_j < 0$$

The **pricing subproblem** searches for the column with the most negative reduced cost:

$$\min_{j \notin B} \; c_j - \pi^\top a_j$$

If the minimum reduced cost is non-negative, the current RMP solution is optimal for the *full* problem — even though we never enumerated all columns. If a negative reduced-cost column exists, we add it to the RMP and re-solve.

### 2.3 The Column Generation Algorithm

```
1. Initialize: Create a feasible RMP with a small set of columns.
2. Solve RMP: Solve the restricted master as an LP → obtain dual values π.
3. Pricing: Solve the pricing subproblem to find the column with minimum reduced cost.
4. Check: If minimum reduced cost ≥ 0 → STOP. Current solution is optimal.
5. Add: Add the new column to the RMP. Return to Step 2.
```

**Key properties:**

- **Finite convergence**: The algorithm terminates because there are finitely many extreme points, and each iteration strictly improves the objective (or terminates).
- **Efficiency**: We only generate columns that are *needed* — typically a tiny fraction of all possible columns.
- **The pricing subproblem inherits problem structure**: For cutting stock, pricing is a knapsack problem. For VRP, it is a shortest path with resource constraints. The structure of the pricing subproblem is what makes column generation practical.

### 2.4 Worked Example 1: Cutting Stock Problem

**Problem**: A steel mill cuts standard bars of length $W = 100$ inches into requested widths. Customer orders:

| Width $w_i$ | Demand $d_i$ |
|---|---|
| 25" | 40 rolls |
| 30" | 50 rolls |
| 45" | 30 rolls |

**Goal**: Minimize the total number of standard bars used.

**Pattern definition**: A cutting pattern $p$ is a vector $(a_{1p}, a_{2p}, a_{3p})$ specifying how many pieces of each width are cut from one bar:

$$25 a_{1p} + 30 a_{2p} + 45 a_{3p} \leq 100, \quad a_{ip} \in \mathbb{Z}_+$$

**Master problem**: Let $x_p$ = number of bars cut using pattern $p$:

$$\min \sum_{p \in P} x_p$$

subject to:

$$\sum_{p \in P} a_{ip} \, x_p \geq d_i \quad \forall \, i = 1, 2, 3 \qquad \text{(meet demand for each width)}$$

$$x_p \geq 0 \quad \forall \, p$$

The number of feasible patterns grows combinatorially with the number of widths and the bar length. For realistic instances with dozens of widths and large bar lengths, there can be millions of patterns.

**Initial patterns** (one dedicated pattern per width — always feasible):

| Pattern | 25" | 30" | 45" | Material used |
|---------|-----|-----|-----|---------------|
| $p_1$: (4, 0, 0) | 4 | 0 | 0 | 100" |
| $p_2$: (0, 3, 0) | 0 | 3 | 0 | 90" |
| $p_3$: (0, 0, 2) | 0 | 0 | 2 | 90" |

**Pricing subproblem** (knapsack): Given dual values $\pi = (\pi_1, \pi_2, \pi_3)$ from the RMP:

$$\max \; \pi_1 a_1 + \pi_2 a_2 + \pi_3 a_3 \qquad \text{subject to} \quad 25 a_1 + 30 a_2 + 45 a_3 \leq 100, \; a_i \in \mathbb{Z}_+$$

If the optimal value exceeds 1 (the cost of using one bar), the reduced cost of the new pattern is negative, and it enters the RMP. The algorithm iterates — typically converging in far fewer iterations than there are total patterns.

*(Full computational walkthrough is provided in the companion Colab notebook.)*

### 2.5 Worked Example 2: Radiation Therapy Planning (Rardin Application 13.1)

#### The Clinical Setting

Cancer treatment with radiation therapy begins with medical imaging (CT scans) that produce cross-sectional images of the patient's body. A physician identifies the **tumor target** and the surrounding **healthy tissues** (e.g., liver, kidneys, spinal cord, bowel). The goal: deliver enough radiation to destroy the tumor while limiting radiation to healthy tissues below safe thresholds.

A linear accelerator rotates around the patient and can fire radiation beams from multiple **angles** (e.g., 3–7 angles around the body). Using multiple angles spreads the healthy-tissue damage across different regions while concentrating dose on the tumor where the beams overlap.

#### Beamlets, Apertures, and the Multileaf Collimator

Each beam from the accelerator is relatively large (roughly 10 cm × 10 cm). To achieve precise dose control, **Intensity Modulated Radiation Therapy (IMRT)** treats each beam as composed of many small **beamlets** — sub-regions of the beam that can have different intensities (roughly, different exposure times).

The beamlets are not physically separate beams. Instead, intensity modulation is achieved using a **multileaf collimator** — a device with moving metal "leaves" (fingers) that slide in from both sides of the beam opening to create a shaped opening called an **aperture**. Think of it like adjustable window blinds: the leaves block some beamlets and let others through.

An **aperture** is a specific configuration of the leaves — a subset of beamlets that are "open" (receiving radiation) at a given intensity. The total radiation delivered from one beam angle is the sum of contributions from multiple apertures, each applied for a certain duration (intensity).

**Why are there so many apertures?** Each aperture is a subset of beamlets, and a beam with 9 beamlets has $2^9 = 512$ possible subsets — but not all are physically feasible. The leaves can only slide in from the edges, so "holes" in the middle of the opening are impossible (a leaf on the left and a leaf on the right cannot leave a gap between them without covering the middle). Even with these physical constraints, the number of feasible apertures grows very rapidly with the number of beamlets. A realistic beam with 100 beamlets may have millions of feasible apertures.

This is exactly the setting for column generation: we have **too many candidate apertures to enumerate**, but only a handful will be used in the optimal plan.

#### The IMRT Optimization Model

**Data** (from Rardin, Table 13.1 — a small instance with 2 beam angles):

- 2 beam angles, each with 9 beamlets
- 6 tumor points (discrete points within the tumor where dose is measured)
- 3 healthy tissues, each with 6 measurement points (18 healthy points total)
- Dose parameters: $t_{i,q,k}$ = dose deposited at tumor point $i$ by beamlet $q$ of angle $k$; $d_{i,q,k}^h$ = dose at point $i$ of healthy tissue $h$ by beamlet $q$ of angle $k$
- Dose limits: Healthy tissue 1 $\leq 50$, Healthy tissue 2 $\leq 65$, Healthy tissue 3 $\leq 70$ per point

**From beamlets to apertures**: Once an aperture $m$ (a subset of beamlets $Q_{m,k}$) is chosen for angle $k$, its dose coefficients are computed by summing over the included beamlets:

$$t_{m,k} = \sum_{q \in Q_{m,k}} \sum_{i} t_{i,q,k} \qquad \text{(total tumor dose from aperture $m$ at angle $k$)}$$

$$d_{i,m,k}^h = \sum_{q \in Q_{m,k}} d_{i,q,k}^h \qquad \text{(dose to point $i$ of healthy tissue $h$)}$$

**Decision variables:** $x_{m,k} \geq 0$ = the intensity (exposure time) applied to aperture $m$ of angle $k$.

**Formulation** (Rardin's IMRT formulation):

$$\max \; \sum_{m,k} t_{m,k} \, x_{m,k} \qquad \text{(maximize total tumor dose)}$$

subject to:

$$\sum_{m,k} d_{i,m,k}^h \, x_{m,k} \leq b^h \quad \forall \, i, \, \forall \, h \qquad \text{(healthy tissue point $i$ in tissue $h$ stays below limit)}$$

$$x_{m,k} \geq 0 \quad \forall \, m, k$$

This is an LP — continuous intensity variables, linear dose accumulation. But the number of columns (apertures) is enormous. Each column corresponds to one aperture at one angle, with its objective coefficient being the total tumor dose and its constraint coefficients being the healthy-tissue doses at each measurement point.

#### Column Generation for IMRT

**Master problem**: An LP over the currently known apertures, maximizing tumor dose subject to healthy-tissue limits.

**Pricing subproblem**: For each beam angle $k$, find a new aperture (subset of beamlets) that would improve the objective. The key insight from Rardin: the reduced cost of an aperture is the sum of **mini-reduced costs** of its individual beamlets:

$$\bar{c}_{m,k} = \sum_{q \in Q_{m,k}} \bar{c}_{q,k} \qquad \text{where} \quad \bar{c}_{q,k} = \sum_i t_{i,q,k} - \sum_{h,i} \pi_{i}^h \, d_{i,q,k}^h$$

Here $\pi_i^h$ are the dual values on the healthy-tissue constraints. Each beamlet $q$ has a mini-reduced cost $\bar{c}_{q,k}$ that measures how "valuable" it is: high tumor dose contribution (good) minus dual-weighted healthy dose (bad). The pricing subproblem selects the subset of beamlets with positive mini-reduced costs, subject to physical aperture feasibility (no holes, no collisions).

**Why this is different from cutting stock pricing**: In cutting stock, the pricing subproblem is a knapsack — a well-defined optimization problem with a clear optimal solution and a proof of optimality. In IMRT, the pricing subproblem involves physical aperture constraints that are hard to model as a clean optimization problem. The practical approach is **heuristic**: select beamlets with the highest mini-reduced costs that form a physically feasible aperture. This works well because we don't need the *best* new aperture — any aperture with a positive reduced cost will improve the solution.

#### Comparison: Cutting Stock vs. IMRT

| Feature | Cutting Stock | IMRT Radiation Therapy |
|---------|--------------|----------------------|
| What is a "column"? | A cutting pattern (how many of each width) | An aperture (which beamlets are open) |
| Objective | Minimize bars used | Maximize tumor dose |
| Constraints | Meet demand for each width | Healthy tissue dose limits |
| Column generation | Unlimited (any combination of widths) | Restricted (physical aperture rules) |
| Pricing subproblem | Knapsack (exact, optimal) | Beamlet selection (heuristic, feasible) |
| Number of candidates | Thousands | Millions+ |
| Columns in optimal solution | ~5–10 patterns | ~5–15 apertures |

The same column generation framework applies to both. The difference is in the *pricing* subproblem — not in the master problem or the algorithm.

*(Full computational implementation with Rardin's data is provided in the companion Colab notebook.)*

### 2.6 Column Generation for Vehicle Routing

Column generation is the foundation of the most effective exact methods for vehicle routing problems (from our routing lecture):

- Each **column** = a complete feasible route for one vehicle.
- The **master problem** = a set partitioning problem: select minimum-cost routes covering all customers.
- The **pricing subproblem** = shortest path with resource constraints: find a new route with negative reduced cost.

This is the foundation of **branch-and-price** algorithms (column generation embedded within branch-and-bound for IP).

---

## 3. Dantzig-Wolfe Decomposition

### 3.1 Motivation: Block-Structured Problems with Too Many Rows

Column generation (Section 2) is an algorithm for LPs with too many variables. But where do these "too many variables" come from in the first place?

In many cases, they arise from a **reformulation** of a problem that originally had too many *constraints* (rows). The idea: take a large LP with block structure and many rows, and **transform it** into an LP with few rows but many columns — then solve it with column generation.

### 3.2 Block-Angular Structure

Consider a large LP with **block-angular structure**: independent subproblems linked by a few coupling constraints.

$$\min \; c_1^\top x_1 + c_2^\top x_2 + \cdots + c_K^\top x_K$$

subject to:

$$A_1 x_1 + A_2 x_2 + \cdots + A_K x_K = b_0 \qquad \text{(linking constraints — few rows)}$$

$$D_k x_k = d_k, \; x_k \geq 0 \quad \forall \, k = 1, \ldots, K \qquad \text{(block constraints — many rows each)}$$

The constraint matrix looks like:

$$\begin{bmatrix} A_1 & A_2 & \cdots & A_K \\ D_1 & & & \\ & D_2 & & \\ & & \ddots & \\ & & & D_K \end{bmatrix}$$

The total number of rows can be enormous (sum of all block rows plus linking rows), but the blocks are *independent* except through the linking rows. Without the linking constraints, the problem would decompose into $K$ independent subproblems.

**Where does this structure arise?**

- **Multi-period planning**: Each period is a block; inventory-balance constraints link them.
- **Multi-facility production**: Each facility is a block; shared resource budgets are the linking constraints.
- **Stochastic programming**: Each scenario is a block; first-stage decisions link them.

### 3.3 The Reformulation: Represent Each Block by Its Extreme Points

The key insight is the **Minkowski-Weyl theorem**: any bounded polyhedron equals the convex hull of its extreme points.

Let $P_k = \{x_k : D_k x_k = d_k, \, x_k \geq 0\}$ be the feasible region of block $k$. If $P_k$ is bounded, any $x_k \in P_k$ can be written as:

$$x_k = \sum_{j=1}^{J_k} \lambda_k^j \, v_k^j, \qquad \sum_{j=1}^{J_k} \lambda_k^j = 1, \qquad \lambda_k^j \geq 0$$

where $\{v_k^1, \ldots, v_k^{J_k}\}$ are the extreme points of $P_k$.

**What this achieves**: All the block constraints $D_k x_k = d_k$ (many rows) are replaced by a single **convexity constraint** $\sum_j \lambda_k^j = 1$ per block (one row). The many rows vanish; in their place, we get many columns (one per extreme point).

### 3.4 The Dantzig-Wolfe Master Problem

Substituting the extreme-point representation:

$$\min \; \sum_{k=1}^{K} \sum_{j=1}^{J_k} (c_k^\top v_k^j) \, \lambda_k^j$$

subject to:

$$\sum_{k=1}^{K} \sum_{j=1}^{J_k} (A_k v_k^j) \, \lambda_k^j = b_0 \qquad \text{(linking constraints — unchanged)}$$

$$\sum_{j=1}^{J_k} \lambda_k^j = 1 \quad \forall \, k = 1, \ldots, K \qquad \text{(one convexity constraint per block)}$$

$$\lambda_k^j \geq 0 \quad \forall \, k, j$$

**The trade-off:**

| | Original LP | DW Master |
|---|---|---|
| Rows | Linking rows + all block rows (many) | Linking rows + $K$ convexity rows (few) |
| Columns | Original variables (manageable) | One per extreme point per block (many) |

The DW master has **far fewer rows** but **far more columns** — exactly the setting where column generation applies. The pricing subproblem for block $k$ optimizes over $P_k$ with modified costs:

$$\min_{x_k \in P_k} \; (c_k^\top - \pi^\top A_k) x_k$$

This is block $k$'s own LP/IP with modified objective coefficients. The optimal $x_k^*$ is a new extreme point (column) to add to the master.

### 3.5 DW Provides Tighter LP Bounds for Integer Programs

When the blocks contain integer variables, the DW reformulation takes convex combinations of *integer* extreme points — preserving integrality within each block. The standard LP relaxation drops integrality everywhere. This means the DW LP bound is at least as tight:

$$z_{LP}^{\text{standard}} \leq z_{LP}^{\text{DW}} \leq z_{IP}^*$$

This tighter bound is one of the main practical motivations for DW decomposition in integer programming (branch-and-price).

### 3.6 Worked Example: Multi-Factory Production with Shared Warehouse

**Problem**: A company operates 3 factories (F1, F2, F3), each producing three products (A, B, C). Each factory has its own machine capacity, labor capacity, and per-product production limits. All factories ship to a shared warehouse with limited storage per product. The company must also meet minimum total production targets for each product.

**Data:**

Production cost (\$/unit):

| | Product A | Product B | Product C |
|---|---|---|---|
| F1 | 8 | 20 | 14 |
| F2 | 18 | 7 | 16 |
| F3 | 15 | 15 | 6 |

Machine hours per unit and capacity:

| | A | B | C | Capacity |
|---|---|---|---|---|
| F1 | 2.0 | 3.5 | 2.5 | 400 hrs |
| F2 | 3.0 | 1.5 | 3.0 | 380 hrs |
| F3 | 2.5 | 2.5 | 1.5 | 420 hrs |

Labor hours per unit and capacity:

| | A | B | C | Capacity |
|---|---|---|---|---|
| F1 | 3.0 | 1.5 | 2.0 | 450 hrs |
| F2 | 1.5 | 3.0 | 2.5 | 400 hrs |
| F3 | 2.0 | 2.0 | 3.5 | 400 hrs |

Per-product upper bounds:

| | A | B | C |
|---|---|---|---|
| F1 | 100 | 80 | 70 |
| F2 | 70 | 90 | 60 |
| F3 | 80 | 70 | 100 |

Linking constraints:

| Product | Warehouse capacity | Minimum total production |
|---|---|---|
| A | 180 | 100 |
| B | 170 | 90 |
| C | 160 | 80 |

Note the asymmetric specialization: F1 is cheapest for A (\$8), F2 for B (\$7), F3 for C (\$6).

#### Original Formulation

**Variables:** $x_{fp}$ = units of product $p$ produced at factory $f$.

$$\min \; 8x_{1A} + 20x_{1B} + 14x_{1C} + 18x_{2A} + 7x_{2B} + 16x_{2C} + 15x_{3A} + 15x_{3B} + 6x_{3C}$$

**Linking constraints** (6 rows):

$$x_{1A} + x_{2A} + x_{3A} \leq 180, \quad x_{1B} + x_{2B} + x_{3B} \leq 170, \quad x_{1C} + x_{2C} + x_{3C} \leq 160$$

$$x_{1A} + x_{2A} + x_{3A} \geq 100, \quad x_{1B} + x_{2B} + x_{3B} \geq 90, \quad x_{1C} + x_{2C} + x_{3C} \geq 80$$

**Block constraints for F1** (5 rows):

$$2.0 x_{1A} + 3.5 x_{1B} + 2.5 x_{1C} \leq 400, \quad 3.0 x_{1A} + 1.5 x_{1B} + 2.0 x_{1C} \leq 450$$

$$x_{1A} \leq 100, \quad x_{1B} \leq 80, \quad x_{1C} \leq 70$$

**Block constraints for F2** (5 rows):

$$3.0 x_{2A} + 1.5 x_{2B} + 3.0 x_{2C} \leq 380, \quad 1.5 x_{2A} + 3.0 x_{2B} + 2.5 x_{2C} \leq 400$$

$$x_{2A} \leq 70, \quad x_{2B} \leq 90, \quad x_{2C} \leq 60$$

**Block constraints for F3** (5 rows):

$$2.5 x_{3A} + 2.5 x_{3B} + 1.5 x_{3C} \leq 420, \quad 2.0 x_{3A} + 2.0 x_{3B} + 3.5 x_{3C} \leq 400$$

$$x_{3A} \leq 80, \quad x_{3B} \leq 70, \quad x_{3C} \leq 100$$

$$x_{fp} \geq 0 \quad \forall \, f, p$$

**Total: 6 linking + 15 block = 21 rows**, 9 variables. The constraint matrix has block-angular structure — the blocks $D_1, D_2, D_3$ (each $5 \times 3$) are independent, coupled only by the 6 linking rows.

#### Dantzig-Wolfe Reformulation

Let $P_k$ = the feasible production region for factory $k$ (defined by its 5 block constraints). Each $P_k$ is a bounded polyhedron with extreme points $\{v_k^1, v_k^2, \ldots, v_k^{J_k}\}$. Any feasible $(x_{kA}, x_{kB}, x_{kC}) \in P_k$ can be written as:

$$(x_{kA}, x_{kB}, x_{kC}) = \sum_{j=1}^{J_k} \lambda_k^j \, v_k^j, \qquad \sum_{j} \lambda_k^j = 1, \quad \lambda_k^j \geq 0$$

Substituting into the original LP, the **DW master** becomes:

$$\min \; \sum_{k=1}^{3} \sum_{j=1}^{J_k} \underbrace{\left( \sum_{p} c_{kp} \, v_{kp}^j \right)}_{\text{cost of plan } j} \lambda_k^j$$

subject to:

$$\sum_{k=1}^{3} \sum_{j} v_{kA}^j \, \lambda_k^j \leq 180, \quad \sum_{k=1}^{3} \sum_{j} v_{kB}^j \, \lambda_k^j \leq 170, \quad \sum_{k=1}^{3} \sum_{j} v_{kC}^j \, \lambda_k^j \leq 160$$

$$\sum_{k=1}^{3} \sum_{j} v_{kA}^j \, \lambda_k^j \geq 100, \quad \sum_{k=1}^{3} \sum_{j} v_{kB}^j \, \lambda_k^j \geq 90, \quad \sum_{k=1}^{3} \sum_{j} v_{kC}^j \, \lambda_k^j \geq 80$$

$$\sum_{j=1}^{J_k} \lambda_k^j = 1 \quad \text{for } k = 1, 2, 3 \qquad \text{(convexity)}$$

$$\lambda_k^j \geq 0 \quad \forall \, k, j$$

**Total: 6 linking + 3 convexity = 9 rows** — the 15 block constraints have vanished. Each column $(v_k^j)$ represents a complete feasible production plan for factory $k$. The number of columns can be large (one per extreme point per factory), but we generate them on demand via column generation.

#### The Pricing Subproblem

Given duals $\pi_p^{wh}$ (warehouse), $\pi_p^{min}$ (min production), and $\sigma_k$ (convexity), the pricing subproblem for factory $k$ is:

$$\min_{(x_{kA}, x_{kB}, x_{kC}) \in P_k} \; \sum_{p \in \{A,B,C\}} \left( c_{kp} - \pi_p^{wh} - \pi_p^{min} \right) x_{kp}$$

This is factory $k$'s own LP with **modified costs**. The reduced cost of the resulting column is the pricing objective minus $\sigma_k$. If negative, the column enters the master.

**Key insight**: The master never sees factory-internal constraints. It only sees production plans and their impact on the shared warehouse and production targets. Each factory's complexity is hidden inside its pricing subproblem.

*(Full computational implementation is provided in the companion Colab notebook.)*

### 3.7 The Relationship: CG and DW

$$\text{Block-structured LP} \xrightarrow[\text{extreme-point representation}]{\text{DW reformulation}} \text{Master LP (few rows, many columns)} \xrightarrow{\text{solved by}} \text{Column Generation}$$

Column generation is the **algorithm**. Dantzig-Wolfe decomposition is the **reformulation** that creates the setting where column generation is needed. Column generation can also be applied *directly* (as in cutting stock, radiation therapy) without an explicit DW reformulation — whenever the problem naturally has too many variables.

---

## 4. Benders Decomposition

### 4.1 Motivation: Too Many Variables in One Group

Dantzig-Wolfe decomposition handles problems with **too many rows** by reformulating them into problems with **too many columns**, then using column generation.

**Benders decomposition** addresses the opposite situation: problems with **too many columns** (variables) in one group. It **projects out** those variables, replacing them with a single new variable in the objective, bounded by iteratively generated **constraints (cuts)**.

### 4.2 The Dual Relationship with Dantzig-Wolfe

DW and Benders are two sides of the same coin:

- **DW** generates *columns* (extreme points of subproblem polyhedra) and adds them to the master.
- **Benders** generates *cuts* (from dual extreme points of subproblem polyhedra) and adds them to the master.

Applying DW to the *dual* of an LP yields the same algorithm as applying Benders to the *primal*. The choice depends on which perspective gives better structure.

| | Dantzig-Wolfe | Benders |
|---|---|---|
| Starts with problem having | Too many rows | Too many columns |
| Reformulates into | Too many columns | Too many rows |
| Generates | Columns (primal extreme points) | Cuts (dual extreme points) |
| Master shrinks in | Rows | Columns |

### 4.3 The Setting: Complicating Variables

Consider an LP partitioned into **complicating variables** $x$ and **easy variables** $y$:

$$\min \; c^\top x + q^\top y \quad \text{s.t.} \quad Ax = b, \; Tx + Wy = h, \; x, y \geq 0$$

Once $x$ is **fixed**, the remaining problem in $y$ is easy to solve (and may decompose into independent pieces). The idea: represent the *effect* of $y$ on the objective as a function of $x$, then optimize over $x$ directly.

### 4.4 The Benders Approach

**Subproblem**: For fixed $\hat{x}$, solve:

$$Q(\hat{x}) = \min_{y} \; q^\top y \quad \text{s.t.} \quad Wy = h - T\hat{x}, \; y \geq 0$$

By LP duality: $Q(\hat{x}) = \max_{\lambda} \; (h - T\hat{x})^\top \lambda$ subject to $W^\top \lambda \leq q$.

The dual feasible region $\{\lambda : W^\top \lambda \leq q\}$ does not depend on $\hat{x}$. So $Q(x)$ is a piecewise-linear convex function of $x$ — the maximum of finitely many linear functions, one per dual extreme point.

**Master problem**: Approximate $Q(x)$ using a variable $\theta$ and linear cuts:

$$\min \; c^\top x + \theta \quad \text{s.t.} \quad Ax = b, \; x \geq 0, \; \theta \geq (h - Tx)^\top \lambda^{(k)} \; \forall k$$

Each cut corresponds to a dual solution $\lambda^{(k)}$ obtained from solving a subproblem.

### 4.5 The Benders Algorithm

```
1. Initialize: Solve master with no cuts → obtain x⁰. Set LB = master objective.
2. Subproblem: Fix x = x⁰, solve the subproblem → obtain dual λ* and cost Q(x⁰).
   - If infeasible: add a feasibility cut, return to Step 1.
   - If feasible: continue.
3. Upper bound: UB = c'x⁰ + Q(x⁰).
4. Check: If UB - LB < ε → STOP (optimal).
5. Cut: Add optimality cut θ ≥ (h - Tx)'λ* to the master.
6. Re-solve master → new x, new LB. Return to Step 2.
```

**Convergence**: Finite — there are finitely many dual extreme points, and each cut eliminates the current solution.

### 4.6 Natural Application: Two-Stage Stochastic Programming

Benders decomposition is the natural algorithm for two-stage stochastic programs (from the Optimization under Uncertainty lecture):

$$\min \; c^\top x + \sum_{s=1}^{S} p_s \, q_s^\top y_s \quad \text{s.t.} \quad Ax = b, \; T_s x + W y_s = h_s \; \forall s, \; x, y_s \geq 0$$

The first-stage variables $x$ are the complicating variables. Once $x$ is fixed, the $S$ scenario subproblems in $y_s$ are **independent** and can be solved in parallel. Each generates a cut. In the stochastic programming literature, this is called the **L-shaped method**.

**Advantages over the extensive form:**

- The master has only $x$ variables plus $\theta_s$ per scenario (small).
- The $S$ subproblems are independent and parallelizable.
- Only cuts that are *active at optimality* are generated — far fewer than the number of scenarios.

### 4.7 Worked Example: Emergency Supply Pre-Positioning

**Problem** (from the Optimization under Uncertainty lecture): A disaster relief agency must pre-position supply kits at 3 warehouses before hurricane season. After a hurricane, kits are shipped to 3 affected zones. Unmet demand costs \$500/kit (penalty); unused kits have \$50 salvage value. Pre-positioning costs \$200/kit. Each warehouse can hold up to 500 kits.

**Data:**

Shipping cost (\$/kit):

| | Zone A | Zone B | Zone C |
|---|---|---|---|
| W1 | 20 | 40 | 60 |
| W2 | 50 | 15 | 35 |
| W3 | 45 | 30 | 10 |

Demand scenarios:

| Scenario | Zone A | Zone B | Zone C | Probability |
|---|---|---|---|---|
| Cat-1 (mild) | 100 | 80 | 50 | 0.40 |
| Cat-3 (moderate) | 300 | 200 | 150 | 0.35 |
| Cat-5 (severe) | 500 | 400 | 350 | 0.15 |
| None | 0 | 0 | 0 | 0.10 |

#### Extensive Form (Original Formulation)

**Complicating variables** (first stage): $x_w$ = kits pre-positioned at warehouse $w$.

**Easy variables** (second stage, per scenario $s$): $y_{wz}^s$ = kits shipped from $w$ to zone $z$; $u_z^s$ = shortfall at zone $z$; $v_w^s$ = unused kits at warehouse $w$.

$$\min \; 200(x_1 + x_2 + x_3) + \sum_{s} p_s \left[ \sum_{w,z} c_{wz} \, y_{wz}^s + 500 \sum_z u_z^s - 50 \sum_w v_w^s \right]$$

subject to:

$$x_w \leq 500 \quad \forall \, w \qquad \text{(warehouse capacity)}$$

$$\sum_z y_{wz}^s + v_w^s = x_w \quad \forall \, w, s \qquad \text{(warehouse balance — links stages)}$$

$$\sum_w y_{wz}^s + u_z^s = d_z^s \quad \forall \, z, s \qquad \text{(zone demand)}$$

$$x_w, y_{wz}^s, u_z^s, v_w^s \geq 0$$

**Size**: 3 first-stage variables + $4 \times (9 + 3 + 3) = 60$ second-stage variables = **63 variables**. 3 capacity + $4 \times (3 + 3) = 24$ second-stage constraints = **27 constraints**. This is small enough to solve directly, but the structure illustrates Benders perfectly.

**Key observation**: Once the first-stage decisions $x = (x_1, x_2, x_3)$ are **fixed**, the 4 scenario subproblems are **completely independent** — each is a small transportation LP. This is the two-stage structure that Benders exploits.

#### Benders Master Problem

Replace the 60 second-stage variables with 4 approximation variables $\theta_s$ (one per scenario):

$$\min \; 200(x_1 + x_2 + x_3) + \sum_{s} p_s \, \theta_s$$

subject to:

$$x_w \leq 500 \quad \forall \, w$$

$$\theta_s \geq \alpha_s^{(k)} + \beta_{s,1}^{(k)} x_1 + \beta_{s,2}^{(k)} x_2 + \beta_{s,3}^{(k)} x_3 \quad \forall \, s, \; k = 1, \ldots, K \qquad \text{(Benders cuts)}$$

$$x_w \geq 0, \quad \theta_s \text{ free}$$

**Size**: 3 + 4 = **7 variables**, 3 capacity + $4K$ cuts = **3 + 4K constraints** (grows with iterations, not with problem size). Initially ($K = 0$), the master has no cuts and will set $\theta_s = -\infty$ (or a large negative lower bound), choosing $x_w = 0$. Each iteration adds 4 cuts (one per scenario).

#### Benders Subproblem (for scenario $s$)

Given fixed $\hat{x} = (\hat{x}_1, \hat{x}_2, \hat{x}_3)$ from the master:

$$Q_s(\hat{x}) = \min \; \sum_{w,z} c_{wz} \, y_{wz} + 500 \sum_z u_z - 50 \sum_w v_w$$

subject to:

$$\sum_z y_{wz} + v_w = \hat{x}_w \quad \forall \, w \qquad \text{(warehouse balance)}$$

$$\sum_w y_{wz} + u_z = d_z^s \quad \forall \, z \qquad \text{(zone demand)}$$

$$y_{wz}, u_z, v_w \geq 0$$

This is a transportation LP with 15 variables and 6 constraints. Its **dual** has variables $\lambda_w$ (warehouse balance duals) and $\mu_z$ (zone demand duals).

#### Cut Generation

From the dual solution $(\lambda_w^*, \mu_z^*)$ of the subproblem, the Benders optimality cut is:

$$\theta_s \geq \underbrace{\left[ Q_s(\hat{x}) - \sum_w \lambda_w^* \hat{x}_w \right]}_{\alpha_s} + \underbrace{\lambda_1^*}_{\ \beta_{s,1}} x_1 + \underbrace{\lambda_2^*}_{\beta_{s,2}} x_2 + \underbrace{\lambda_3^*}_{\beta_{s,3}} x_3$$

**Interpretation**: The dual $\lambda_w^*$ measures the marginal value of an additional pre-positioned kit at warehouse $w$ in scenario $s$. The cut says: the recourse cost in scenario $s$ is at least a linear function of the pre-positioning quantities, with slopes given by the warehouse duals.

#### The Benders Iteration

| Iteration | Master decides | Subproblems compute | Cuts added |
|---|---|---|---|
| 1 | $\hat{x} = (0, 0, 0)$ (no cuts yet) | $Q_s(0)$ for each $s$ — all demand unmet, heavy penalties | 4 cuts forcing $\theta_s$ up |
| 2 | $\hat{x}$ increases (master sees penalty costs) | $Q_s(\hat{x})$ — some demand met, less penalty | 4 more cuts refining the approximation |
| ... | $\hat{x}$ converges | Subproblem costs stabilize | Cuts tighten until UB ≈ LB |

The lower bound (master objective) increases with each cut. The upper bound ($200 \sum_w \hat{x}_w + \sum_s p_s Q_s(\hat{x})$) is the true cost of the current $\hat{x}$. Convergence occurs when the gap closes.

**Why Benders helps here**: The extensive form has 63 variables and 27 constraints. For a realistic version with 50 warehouses, 100 zones, and 500 scenarios, the extensive form would have $3 \times 50 + 500 \times (50 \times 100 + 100 + 50) = 2{,}575{,}150$ variables. The Benders master would still have only $50 + 500 = 550$ variables, with 500 independent subproblems solvable in parallel.

*(Full Benders implementation with convergence tracking is provided in the companion Colab notebook.)*

---

## 5. Lagrangian Relaxation

### 5.1 A Fundamentally Different Approach

The three methods above — column generation, DW decomposition, and Benders decomposition — are all **exact methods**: they converge to the optimal LP solution (or provide exact LP bounds for IP). They exploit specific structural features (too many variables, block structure, two-stage structure).

**Lagrangian relaxation** is fundamentally different in several ways:

- It is **not a decomposition method** — though decomposition may arise as a byproduct.
- It is **not an exact solution method** — it produces *bounds*, not optimal solutions.
- It is **not limited to large-scale problems** — it applies whenever a problem has "complicating" constraints, regardless of size.
- It works for **LP, IP, nonconvex problems, and beyond** — unlike the decomposition methods, which require LP substructure.

The core idea: some constraints make a problem hard. Moving them into the objective as **penalties** creates a relaxed problem that is easier to solve — and whose optimal value provides a bound on the original problem.

### 5.2 What Makes a Constraint "Complicating"?

Consider the IP:

$$z^* = \min \; c^\top x \quad \text{s.t.} \quad Ax \leq b, \; Dx \leq e, \; x \in \mathbb{Z}_+^n$$

The constraints $Ax \leq b$ are **complicating** if removing them would make the problem significantly easier. Specifically:

- **They link variables from different subproblems**: A shared budget across facilities, a total demand constraint across plants, a coupling constraint between time periods.
- **Removing them induces decomposition**: Without $Ax \leq b$, the remaining problem $\{Dx \leq e, \, x \in \mathbb{Z}_+\}$ decomposes into independent blocks, or becomes a well-known tractable problem (knapsack, network flow, assignment).
- **They prevent the use of efficient algorithms**: The easy constraints $Dx \leq e$ have special structure (e.g., totally unimodular, network structure) that is disrupted by the complicating constraints.

Importantly, "complicating" is relative to the rest of the problem. A constraint that is complicating in one formulation may be easy in another.

### 5.3 The Lagrangian Relaxation

For any vector of **Lagrange multipliers** $\mu \geq 0$, the **Lagrangian relaxation** is:

$$L(\mu) = \min_{x} \; c^\top x + \mu^\top (Ax - b) \quad \text{s.t.} \quad Dx \leq e, \; x \in \mathbb{Z}_+^n$$

The complicating constraints $Ax \leq b$ have been moved into the objective as penalties. The multiplier $\mu_i$ controls how harshly violation of constraint $i$ is penalized.

**Key properties:**

1. **$L(\mu)$ is a valid lower bound**: $L(\mu) \leq z^*$ for all $\mu \geq 0$. Any feasible solution to the original problem satisfies $Ax \leq b$, so the penalty $\mu^\top(Ax - b) \leq 0$, making the Lagrangian objective no larger than the true cost.

2. **Often tighter than the LP relaxation**: The Lagrangian preserves integrality ($x \in \mathbb{Z}_+$) and the easy constraints ($Dx \leq e$), while only relaxing the complicating constraints. The LP relaxation drops *both* integrality and replaces $Ax \leq b$ with a weaker continuous formulation.

3. **The relaxed problem may decompose**: If $Dx \leq e$ is block-diagonal (e.g., per-plant constraints), then with $Ax \leq b$ removed, the Lagrangian problem decomposes into independent subproblems. But this decomposition is a *consequence*, not a requirement — Lagrangian relaxation is useful even when the relaxed problem does not decompose.

4. **Works for non-LP problems**: Unlike CG, DW, and Benders, Lagrangian relaxation does not require LP structure. It applies to IPs, MIPs, nonlinear programs, and any problem where some constraints can be penalized.

### 5.4 The Lagrangian Dual and Subgradient Optimization

The tightest bound is obtained by solving the **Lagrangian dual**:

$$z_{LD} = \max_{\mu \geq 0} \; L(\mu)$$

Since $L(\mu)$ is a pointwise minimum of linear functions in $\mu$, it is **concave** — even for non-convex original problems. The standard algorithm for solving the Lagrangian dual is **subgradient optimization**:

```
1. Initialize: Choose μ⁰ ≥ 0. Set best LB = -∞.
2. Solve Lagrangian: Compute L(μᵗ) → obtain solution x*.
3. Update bound: LB = max(LB, L(μᵗ)).
4. Subgradient: g = Ax* - b.
5. Step size: αₜ = λₜ(z_UB - L(μᵗ)) / ‖g‖²
6. Update: μᵢᵗ⁺¹ = max(0, μᵢᵗ + αₜ gᵢ)
7. Return to Step 2.
```

The step size uses a known upper bound $z_{UB}$ (from a heuristic) and a parameter $\lambda_t \in (0, 2]$ that is halved periodically without improvement.

### 5.5 From Bounds to Feasible Solutions

The Lagrangian solution $x^*$ typically violates the complicating constraints $Ax \leq b$. To get a feasible solution:

- **Heuristic repair**: Adjust $x^*$ to satisfy $Ax \leq b$ (e.g., reduce production at some plants to meet a shared budget).
- **Primal recovery**: Use the sequence of Lagrangian solutions to construct feasible solutions via convex combination or rounding.

The gap between the best feasible solution (upper bound) and the Lagrangian dual (lower bound) provides a **quality guarantee**.

### 5.6 Worked Example: Multi-Plant Production

**Problem**: Five plants produce a common product. Each plant $i$ has production cost $c_i$, capacity $u_i$, and fixed setup cost $f_i$. Total demand is $D = 400$ units. All plants share a raw material budget of $B = 1{,}600$ units, where plant $i$ uses $r_i$ units per unit produced.

| Plant | Unit cost $c_i$ | Setup cost $f_i$ | Capacity $u_i$ | Material/unit $r_i$ |
|-------|----------------|------------------|----------------|---------------------|
| P1    | 10             | 1,500            | 140            | 5                   |
| P2    | 16             | 1,200            | 100            | 3                   |
| P3    | 12             | 1,800            | 120            | 6                   |
| P4    | 20             | 900              | 110            | 2                   |
| P5    | 8              | 1,400            | 130            | 7                   |

**Complicating constraints**: Demand ($\sum_i x_i \geq D$) and budget ($\sum_i r_i x_i \leq B$) — these link all plants.

**Easy constraints**: Per-plant capacity ($0 \leq x_i \leq u_i z_i$, $z_i \in \{0,1\}$) — independent by plant.

**Lagrangian relaxation** (relax demand and budget): For multipliers $\mu_1 \geq 0$ (demand) and $\mu_2 \geq 0$ (budget):

$$L(\mu_1, \mu_2) = \min_{x, z} \sum_{i=1}^{5} \left[ (c_i + \mu_2 r_i - \mu_1) x_i + f_i z_i \right] + \mu_1 D - \mu_2 B$$

subject to: $0 \leq x_i \leq u_i z_i, \; z_i \in \{0, 1\} \quad \forall \, i$

This **decomposes** into 5 independent subproblems, one per plant. Each is trivial: the modified unit cost is $\tilde{c}_i = c_i + \mu_2 r_i - \mu_1$. If $\tilde{c}_i < 0$ and $|\tilde{c}_i| \cdot u_i > f_i$, open plant $i$ at full capacity. Otherwise, close it.

**Why Lagrangian outperforms LP relaxation here**: The LP relaxation allows fractional $z_i$ (e.g., $z_i = 0.6$), paying only 60% of the setup cost. The Lagrangian subproblems preserve the binary nature of $z_i$ — each plant is either fully open or fully closed — giving a tighter bound. The high setup costs (\$900–\$1,800) create a meaningful LP-IP gap that the Lagrangian bound partially closes.

*(Full subgradient implementation with convergence plots comparing LP relaxation and Lagrangian bounds is provided in the companion Colab notebook.)*

---

## 6. Comparing the Four Methods

| | Column Generation | Dantzig-Wolfe | Benders | Lagrangian Relaxation |
|---|---|---|---|---|
| **Nature** | Algorithm | Reformulation + CG | Algorithm | Relaxation + bound |
| **Structural need** | Too many variables | Block structure, too many rows | Complicating variables (two-stage) | Complicating constraints |
| **What it generates** | Columns (variables) | Extreme-point columns | Cuts (constraints) | Bounds via multiplier updates |
| **Exactness** | Exact (LP) | Exact (LP); tighter bounds for IP | Exact (LP) | Bound only; heuristic for feasible solution |
| **Subproblem** | Pricing (inherits application structure) | Block LP/IP (one per block) | Recourse LP (one per scenario) | Relaxed problem (may decompose) |
| **Scope** | LP with many candidates | Block-angular LP/IP | Two-stage LP/MIP | Any problem with complicating constraints |

### When to use which method

**Column generation**: The problem naturally has too many candidate variables (patterns, routes, schedules, beams) but a manageable number of constraints. You can solve the pricing subproblem efficiently.

**Dantzig-Wolfe decomposition**: The problem has block-angular structure with many constraints that can be absorbed into block subproblems. The linking constraints are few. You want an exact LP solution or tighter IP bounds. *Use CG to solve the DW master.*

**Benders decomposition**: The problem has a natural two-stage or master-subproblem partition. Once the complicating variables are fixed, the remaining problem is easy (and may decompose). The second stage must be an LP for classical Benders.

**Lagrangian relaxation**: The problem has complicating constraints that, when removed, make it much easier. You want strong bounds quickly. The problem may be IP, nonconvex, or otherwise hard. Lagrangian is the most general method but produces bounds, not exact solutions.

---

## 7. Implementation Considerations

### 7.1 Warm Starting

All four methods solve sequences of related LPs or IPs. Modern solvers like Gurobi support **warm starting**:

```
option gurobi_options 'warmstart=1';
```

### 7.2 Parallel Computation

Both Benders and Lagrangian relaxation involve solving **independent subproblems** per iteration. These can be solved in parallel — a major advantage for problems with many scenarios or blocks.

### 7.3 Practical Solver Support

Gurobi natively supports **lazy constraints** (Benders cuts via callbacks) and **column generation** through its column-wise modeling API. For this course, we implement the algorithms explicitly in Python/AMPL to understand the mechanics.

---

## 8. Exercises

**Exercise 1 (Column Generation — Cutting Stock)**. A steel mill cuts standard bars of length 12 meters into requested lengths: 3m (demand: 80), 5m (demand: 60), and 7m (demand: 40). (a) Enumerate all feasible cutting patterns. How many are there? (b) Formulate the cutting stock master LP. (c) Implement column generation in AMPL/Python: start with three single-width patterns, solve the RMP, solve the pricing knapsack, and iterate until optimal. Report the optimal number of bars, the patterns used, and the number of iterations. (d) Round the LP solution to obtain an integer solution. What is the optimality gap?

**Exercise 2 (Benders — Stochastic Facility Location)**. A company must decide which of 3 potential warehouses to open (first-stage binary) to serve demand across 5 scenarios (second-stage continuous allocation). (Use the stochastic facility location data from the Optimization under Uncertainty notebook.) (a) Formulate as a two-stage stochastic IP. What is the master problem? What are the subproblems? (b) Implement Benders decomposition. Track and plot the lower and upper bounds over iterations. (c) Compare the number of iterations and total solve time to solving the extensive form directly.

**Exercise 3 (Lagrangian Relaxation — Bound Quality)**. Consider the multi-plant production problem from Section 5.6 with 5 plants (data given in the section). (a) Solve the full IP directly in AMPL to obtain the optimal cost. (b) Implement subgradient optimization relaxing **both** the demand and budget constraints. Run 20 iterations and plot the lower bound. (c) Now implement a variant relaxing **only** the demand constraint (keeping the budget constraint in the subproblem). Run 20 iterations and plot the lower bound on the same figure. (d) Which relaxation gives a tighter bound? Explain why in terms of what information the subproblem retains.

**Exercise 4 (Conceptual)**. For each of the following problems, identify which large-scale method (column generation, Dantzig-Wolfe, Benders, or Lagrangian relaxation) is most appropriate and explain why:
- (a) Scheduling airline crews to cover 500 flights, where each crew has work-time and rest regulations.
- (b) Designing a supply chain network (facility locations) under 200 demand scenarios.
- (c) A multi-factory production system where each factory has complex internal scheduling, and all factories share a single raw material supplier with limited capacity.
- (d) A portfolio optimization problem with a cardinality constraint (at most 20 stocks), where the cardinality constraint makes the problem NP-hard but removing it gives a simple QP.

**Exercise 5 (Benders — Extended Emergency Supply)**. Extend the emergency supply pre-positioning problem from Section 4.7 by adding 2 more warehouses and 2 more zones, and increasing to 6 scenarios. Implement Benders decomposition for this larger instance. (a) How many iterations are needed compared to the 3-warehouse, 4-scenario case? (b) Compare the Benders solve time to the extensive form solve time. At what problem size does Benders become faster?

---

## References

- Rardin, R.L. *Optimization in Operations Research*, 2nd edition. Chapter 15 (large-scale methods).
- Gilmore, P.C. and Gomory, R.E. "A linear programming approach to the cutting-stock problem." *Operations Research*, 9(6):849–859, 1961.
- Dantzig, G.B. and Wolfe, P. "Decomposition principle for linear programs." *Operations Research*, 8(1):101–111, 1960.
- Benders, J.F. "Partitioning procedures for solving mixed-variables programming problems." *Numerische Mathematik*, 4:238–252, 1962.
- Fisher, M.L. "The Lagrangian relaxation method for solving integer programming problems." *Management Science*, 27(1):1–18, 1981.
- Desrosiers, J. and Lübbecke, M. "Branch-price-and-cut algorithms." In *Wiley Encyclopedia of Operations Research and Management Science*, 2011.
