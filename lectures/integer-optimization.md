# ISYE 671: Linear Optimization and Network Flows — Lecture Notes

## Integer (Discrete) Optimization Models

**Instructor:** Dr. Ziteng Wang | **Date:** February 9, 2026 | **Reading:** Rardin, Chapter 11

---

## 1. Why Integer Optimization?

Linear programming assumes all decision variables are continuous — we can choose any fractional quantity. In practice, many decisions are inherently discrete:

- You either build a warehouse or you don't (binary).
- You assign 3 trucks to a route, not 2.7 (integer).
- You select a project or reject it — no partial funding (binary).

Integer optimization adds integrality constraints to what might otherwise be a linear program. This seemingly small change has profound consequences: problems that LP solves in polynomial time can become NP-hard. Yet the modeling power gained is enormous.

**Key taxonomy:**

- **Pure Integer Linear Program (ILP):** All decision variables are integer.
- **Mixed-Integer Linear Program (MILP):** Some variables are integer, others continuous.
- **Binary (0–1) Integer Program:** Integer variables restricted to 0 or 1.

Today we develop fluency in *formulating* integer optimization models. We will cover six model families, each illustrated with an application from Rardin's Chapter 11, and each followed by an extension exercise for you to try.

---

## 2. Lumpy Linear Programs and Fixed Charges — Swedish Steel Application

### 2.1 Context and Motivation

Recall the Swedish Steel blending problem from our LP lectures. The original LP chooses a minimum-cost mix of 7 ingredients (scraps and pure additives) to produce a 1000 kg charge of steel, subject to chemical composition constraints on carbon, nickel, chromium, and molybdenum.

**Original LP formulation (Model 11.1 in Rardin):**

$$\min \quad 16x_1 + 10x_2 + 8x_3 + 9x_4 + 48x_5 + 60x_6 + 53x_7$$

subject to:

$$x_1 + x_2 + x_3 + x_4 + x_5 + x_6 + x_7 = 1000 \quad \text{(weight)}$$

$$6.5 \leq 0.0080x_1 + 0.0070x_2 + 0.0085x_3 + 0.0040x_4 \leq 7.5 \quad \text{(carbon)}$$

$$30 \leq 0.180x_1 + 0.032x_2 + 1.0x_5 \leq 35 \quad \text{(nickel)}$$

$$10 \leq 0.120x_1 + 0.011x_2 + 1.0x_6 \leq 12 \quad \text{(chromium)}$$

$$11 \leq 0.001x_2 + 1.0x_7 \leq 13 \quad \text{(molybdenum)}$$

$$x_1 \leq 75, \quad x_2 \leq 250, \quad x_j \geq 0 \; \forall j$$

**LP optimal cost:** 9,953.7 kroner.

### 2.2 Modeling Technique 1: All-or-Nothing Variables

**Real-world complication:** Scraps 1 and 2 are large, indivisible blocks. Either the entire block is used, or none of it.

> **Principle (All-or-Nothing):** A requirement $x_j = 0 \text{ or } u_j$ can be modeled by substituting $x_j = u_j \, y_j$, where $y_j \in \{0,1\}$.

With $u_1 = 75$ and $u_2 = 250$, replace $x_1$ with $75 y_1$ and $x_2$ with $250 y_2$ throughout. The resulting ILP has:

- **Objective:** $\min\; 1200 y_1 + 2500 y_2 + 8x_3 + 9x_4 + 48x_5 + 60x_6 + 53x_7$
- **Weight:** $75 y_1 + 250 y_2 + x_3 + x_4 + x_5 + x_6 + x_7 = 1000$
- All composition constraints updated analogously.
- $y_1, y_2 \in \{0,1\}$; remaining $x_j \geq 0$.

**ILP optimal cost:** 9,967.1 kroner (higher due to the loss of fractional flexibility).

**Optimal solution:** $y_1^* = 1$, $y_2^* = 0$, $x_3^* = 736.44$, $x_4^* = 160.06$, $x_5^* = 16.50$, $x_6^* = 1.00$, $x_7^* = 11.00$.

### 2.3 Modeling Technique 2: Fixed-Charge Variables and Switching Constraints

**Real-world complication:** Ingredients 1–4 require a setup cost of 350 kroner each before they can be used at any nonzero level.

The cost structure becomes:

$$\text{cost}_j(x_j) = \begin{cases} f_j + c_j x_j & \text{if } x_j > 0 \\ 0 & \text{if } x_j = 0 \end{cases}$$

> **Principle (Fixed Charges):** Introduce binary $y_j \in \{0,1\}$ with $y_j = 1$ if $x_j > 0$. Add the fixed cost $f_j y_j$ to the objective. Link $x_j$ and $y_j$ via a **switching constraint**: $x_j \leq u_j \, y_j$, where $u_j$ is a valid upper bound on $x_j$.

**Key modeling insight — Deriving valid upper bounds:** For $x_1 \leq 75$ and $x_2 \leq 250$, the bounds are given. For $x_3$ and $x_4$, observe from the weight constraint that $x_3, x_4 \leq 1000$ (crude but valid). Tighter bounds yield a tighter LP relaxation.

**Swedish Steel fixed-charge model (Model 11.4 in Rardin):**

$$\min \quad 16x_1 + 10x_2 + 8x_3 + 9x_4 + 48x_5 + 60x_6 + 53x_7 + 350(y_1 + y_2 + y_3 + y_4)$$

subject to all original LP constraints, plus:

$$x_1 \leq 75 y_1, \quad x_2 \leq 250 y_2, \quad x_3 \leq 1000 y_3, \quad x_4 \leq 1000 y_4$$

$$y_1, y_2, y_3, y_4 \in \{0,1\}$$

**Optimal solution:** Opens setups for ingredients 1, 3, 4 ($y_1^* = y_3^* = y_4^* = 1$). Total cost = 11,017.1 kroner.

### 2.4 Student Exercise — Swedish Steel Extension

> **Extension Problem:** Suppose Swedish Steel is considering a *premium* contract that offers a bonus of 2,000 kroner if the final steel charge contains at least 5% nickel content by weight (i.e., at least 50 kg of nickel in the 1000 kg charge), but this premium requires a one-time testing fee of 500 kroner regardless of whether the nickel threshold is met or not — the testing fee is paid only if the company *opts in* to the premium contract.
>
> Modify the fixed-charge version of the Swedish Steel model to incorporate this optional premium contract. Define any new variables and constraints needed.
>
> *Hint:* You need a new binary variable $z \in \{0,1\}$ for the opt-in decision, and you must link the nickel content to $z$ using big-M or switching logic.

---

## 3. Capital Budgeting — NASA Application

### 3.1 Context

NASA must select missions from 14 proposals over a 25-year planning horizon divided into 5 stages, each with a limited budget. The decision variables are:

$$x_j = \begin{cases} 1 & \text{if mission } j \text{ is selected} \\ 0 & \text{otherwise} \end{cases} \quad j = 1, \ldots, 14$$

**Data from Table 11.2 in Rardin** (budget requirements in $billions, and mission values):

| j | Mission | Stg 1 | Stg 2 | Stg 3 | Stg 4 | Stg 5 | Value | Not With | Depends On |
|---|---------|-------|-------|-------|-------|-------|-------|----------|------------|
| 1 | Communications satellite | 6 | — | — | — | — | 200 | — | — |
| 2 | Orbital microwave | 2 | 3 | — | — | — | 3 | — | — |
| 3 | Io lander | 3 | 5 | — | — | — | 20 | — | — |
| 4 | Uranus orbiter 2020 | — | — | — | — | 10 | 50 | 5 | 3 |
| 5 | Uranus orbiter 2010 | — | 5 | 8 | — | — | 70 | 4 | 3 |
| 6 | Mercury probe | — | — | 1 | 8 | 4 | 20 | — | 3 |
| 7 | Saturn probe | 1 | 8 | — | — | — | 5 | — | 3 |
| 8 | Infrared imaging | — | — | — | 5 | — | 10 | 11 | — |
| 9 | Ground-based SETI | 4 | 5 | — | — | — | 200 | 14 | — |
| 10 | Large orbital structures | — | 8 | 4 | — | — | 150 | — | — |
| 11 | Color imaging | — | — | 2 | 7 | — | 18 | 8 | 2 |
| 12 | Medical technology | 5 | 7 | — | — | — | 8 | — | — |
| 13 | Polar orbital platform | — | 1 | 4 | 1 | 1 | 300 | — | — |
| 14 | Geosynchronous SETI | — | 4 | 5 | 3 | 3 | 185 | 9 | — |

**Stage budgets:** 10, 12, 14, 14, 14 ($B).

### 3.2 Modeling Technique 3: Budget Constraints

Each stage's total expenditure must not exceed the available budget:

$$\sum_{j: a_{tj} > 0} a_{tj} \, x_j \leq b_t \quad \text{for each stage } t = 1, \ldots, 5$$

For example, Stage 1: $6x_1 + 2x_2 + 3x_3 + x_7 + 4x_9 + 5x_{12} \leq 10$.

### 3.3 Modeling Technique 4: Mutually Exclusive Choices

If at most one of a group of projects can be selected:

$$\sum_{j \in S} x_j \leq 1$$

NASA conflicts: missions 4 & 5 (alternative timings), missions 8 & 11 (incompatible tech), missions 9 & 14 (alternative SETI approaches):

$$x_4 + x_5 \leq 1, \quad x_8 + x_{11} \leq 1, \quad x_9 + x_{14} \leq 1$$

### 3.4 Modeling Technique 5: Dependency Constraints

If project $j$ depends on project $i$ (can't select $j$ without $i$):

$$x_j \leq x_i$$

Mission 11 depends on mission 2; missions 4, 5, 6, 7 each depend on mission 3:

$$x_{11} \leq x_2, \quad x_4 \leq x_3, \quad x_5 \leq x_3, \quad x_6 \leq x_3, \quad x_7 \leq x_3$$

### 3.5 Complete NASA Model (Model 11.7)

$$\max \quad 200x_1 + 3x_2 + 20x_3 + 50x_4 + 70x_5 + 20x_6 + 5x_7 + 10x_8 + 200x_9 + 150x_{10} + 18x_{11} + 8x_{12} + 300x_{13} + 185x_{14}$$

subject to all budget, mutual exclusivity, and dependency constraints above, and $x_j \in \{0,1\}$ for all $j$.

### 3.6 Student Exercise — NASA Extension

> **Extension Problem:** NASA's budget committee is considering two policy changes:
>
> **(a)** A new "balanced portfolio" requirement: at least 3 of the selected missions must have budgetary activity in Stage 3 or later (i.e., missions that require funding in Stage 3, 4, or 5). Formulate this as an additional constraint.
>
> **(b)** A synergy bonus: if *both* the Communications Satellite (mission 1) and the Large Orbital Structures (mission 10) are selected, an additional value of 75 is gained due to shared infrastructure. Modify the objective function and add any necessary variables/constraints to capture this.
>
> *Hint for (b):* Introduce a new binary variable $z \in \{0,1\}$ with $z = 1$ only when both $x_1 = 1$ and $x_{10} = 1$. What constraints enforce this?

---

## 4. Set Covering — EMS Location Application

### 4.1 Context

Austin, Texas must position Emergency Medical Service (EMS) vehicles. The city is divided into 20 service districts, and there are 10 candidate station locations. Each station can serve all adjacent districts (coverage data from Figure 11.1 in Rardin).

**Decision variables:**

$$x_j = \begin{cases} 1 & \text{if station } j \text{ is opened} \\ 0 & \text{otherwise} \end{cases} \quad j = 1, \ldots, 10$$

### 4.2 Key Definitions

- **Set Covering Constraint** (at least one must serve each district): $\displaystyle\sum_{j \in N_i} x_j \geq 1$

- **Set Packing Constraint** (at most one): $\displaystyle\sum_{j \in N_i} x_j \leq 1$

- **Set Partitioning Constraint** (exactly one): $\displaystyle\sum_{j \in N_i} x_j = 1$

where $N_i$ is the set of stations that can cover district $i$.

### 4.3 Minimum Cover Model (Model 11.8)

Minimize the number of stations so that every district is covered:

$$\min \quad \sum_{j=1}^{10} x_j$$

subject to one covering constraint per district (20 constraints). For example:

- District 1: $x_2 \geq 1$ (only station 2 covers it)
- District 7: $x_2 + x_4 \geq 1$
- District 12: $x_4 + x_5 + x_6 \geq 1$
- District 20: $x_{10} \geq 1$

**Optimal solution:** 6 stations — sites 2, 3, 4, 6, 8, and 10.

### 4.4 Maximum Coverage Model with Limited Budget (Model 11.9)

Now suppose we can afford only **4 stations**. We want to minimize the total importance of *uncovered* districts.

**New variables:** $y_i \in \{0,1\}$, where $y_i = 1$ if district $i$ is uncovered.

**District importance values** (from Rardin):

| Dist. | Value | Dist. | Value | Dist. | Value | Dist. | Value |
|-------|-------|-------|-------|-------|-------|-------|-------|
| 1 | 5.2 | 6 | 5.7 | 11 | 30.4 | 16 | 25.6 |
| 2 | 4.4 | 7 | 10.0 | 12 | 30.9 | 17 | 11.0 |
| 3 | 7.1 | 8 | 12.2 | 13 | 12.0 | 18 | 5.3 |
| 4 | 9.0 | 9 | 7.6 | 14 | 9.3 | 19 | 7.9 |
| 5 | 6.1 | 10 | 20.3 | 15 | 15.5 | 20 | 9.9 |

**Formulation:**

$$\min \quad \sum_{i=1}^{20} v_i \, y_i$$

subject to:

$$\sum_{j \in N_i} x_j + y_i \geq 1 \quad \forall \, i = 1, \ldots, 20$$

$$\sum_{j=1}^{10} x_j \leq 4$$

$$x_j, y_i \in \{0,1\}$$

**Optimal with 4 stations:** sites 3, 4, 5, 9. Districts 1, 2, 6, 9, 20 are left uncovered.

### 4.5 Student Exercise — EMS Extension

> **Extension Problem:** The city council has passed two new policies:
>
> **(a)** *Double coverage requirement:* Districts 11 and 12 (the most populated) must each be covered by at least **two** stations. Modify the minimum cover model accordingly.
>
> **(b)** *Equity constraint for the maximum coverage model:* No more than 5 districts may be left uncovered. Add this constraint to the 4-station maximum coverage model (11.9). Does this change the problem structure?
>
> **(c)** *New problem:* Suppose the city adds an 11th candidate station location that can cover districts 9, 14, 18, and 19. Write the updated covering constraints for these four districts and re-examine the minimum cover model.

---

## 5. Facility Location — Tmark Application

### 5.1 Context

Tmark (based on an AT&T telemarketing application) must choose which of 8 possible call-center sites to open and how to route calls from 14 geographic zones to minimize total cost (variable calling charges + fixed operating costs).

**Two types of decision variables:**

- $y_i \in \{0,1\}$: whether facility $i$ is opened ($i = 1, \ldots, 8$)
- $x_{ij} \geq 0$: fraction of zone $j$'s demand served from facility $i$

**Data (from Table 11.9 in Rardin):**

- $r_{ij}$: unit call charge from zone $j$ to center $i$
- $d_j$: demand (call units) at zone $j$
- $f_i$: fixed daily cost of operating center $i$
- Each center, if opened, must handle between **1,500 and 5,000** call units/day

Fixed costs: $f_1 = 2400$, $f_2 = 7000$, $f_3 = 3600$, $f_4 = 1600$, $f_5 = 3000$, $f_6 = 4600$, $f_7 = 9000$, $f_8 = 2000$.

### 5.2 Facility Location Model Structure

> **General facility location model:**
>
> $$\min \quad \sum_i \sum_j c_{ij} d_j x_{ij} + \sum_i f_i y_i$$
>
> $$\text{s.t.} \quad \sum_i x_{ij} = 1 \quad \forall \, j \quad \text{(fulfill all demand)}$$
>
> $$\sum_j d_j x_{ij} \leq u_i \, y_i \quad \forall \, i \quad \text{(capacity switching)}$$
>
> $$x_{ij} \geq 0, \quad y_i \in \{0,1\}$$

### 5.3 Tmark Model (Model 11.20)

$$\min \quad \sum_{i=1}^{8} \sum_{j=1}^{14} r_{ij} \, d_j \, x_{ij} + \sum_{i=1}^{8} f_i \, y_i$$

subject to:

$$\sum_{i=1}^{8} x_{ij} = 1 \quad \forall \, j = 1, \ldots, 14 \quad \text{(carry zone } j \text{ load)}$$

$$1500 \, y_i \leq \sum_{j=1}^{14} d_j \, x_{ij} \quad \forall \, i = 1, \ldots, 8 \quad \text{(minimum operating level)}$$

$$\sum_{j=1}^{14} d_j \, x_{ij} \leq 5000 \, y_i \quad \forall \, i = 1, \ldots, 8 \quad \text{(maximum capacity)}$$

$$x_{ij} \geq 0, \quad y_i \in \{0,1\}$$

**Key modeling point:** The minimum operating level constraint ($1500 y_i \leq \sum_j d_j x_{ij}$) ensures that if a facility is open, it handles a meaningful workload.

**Optimal solution:** Open centers 4 and 8 ($y_4^* = y_8^* = 1$). Zones 1, 2, 4, 5, 6, 7 served from center 4; the rest from center 8. Daily cost = $10,153.

### 5.4 Student Exercise — Tmark Extension

> **Extension Problem:** Tmark's management imposes two new requirements:
>
> **(a)** *Regional presence:* At least one center must be opened in the "western region" (sites 5, 6, 7, or 8) AND at least one in the "eastern region" (sites 1, 2, 3, or 4). Formulate these constraints.
>
> **(b)** *Single-source assignment:* Management now requires that each zone's entire call volume must be handled by a single center (no splitting). What changes in the model?
>
> **(c)** *Budget cap on fixed costs:* The total fixed cost across all opened centers must not exceed $12,000 per day. Write this constraint. Does this conflict with part (a)?

---

## 6. Network Design — Wastewater Application

### 6.1 Context

A regional wastewater system must be designed for 8 population centers (nodes 1–8) with a supersink node 9 representing treatment plant outflows. Arcs represent possible collector sewers; node 9 arcs model treatment plant costs. The design must route all wastewater to treatment while minimizing total construction cost (fixed + variable per unit flow).

**Two types of decision variables:**

- $x_{ij} \geq 0$: flow (population units, in thousands) on arc $(i,j)$
- $y_{ij} \in \{0,1\}$: whether arc $(i,j)$ is constructed

**Data (from Figure 11.8 in Rardin):**

Node supplies (population in thousands): node 1 = 27, node 2 = 3, node 3 = 14, node 4 = 36, node 5 = 21, node 6 = 8, node 7 = 13, node 8 = 0 (relay only). Total flow to supersink node 9 = 122.

| Arc | Fixed Cost | Variable Cost | | Arc | Fixed Cost | Variable Cost |
|-----|-----------|--------------|---|-----|-----------|--------------|
| (1,2) | 240 | 21 | | (5,6) | 620 | 44 |
| (1,3) | 350 | 30 | | (5,7) | 800 | 51 |
| (2,3) | 200 | 22 | | (6,7) | 500 | 56 |
| (2,4) | 750 | 58 | | (6,8) | 630 | 94 |
| (3,4) | 610 | 43 | | (7,4) | 1120 | 82 |
| (3,9) | 3800 | 1 | | (7,9) | 3800 | 1 |
| (4,3) | 1840 | 49 | | (8,9) | 2500 | 2 |
| (4,8) | 780 | 63 | | | | |

### 6.2 Fixed-Charge Network Flow Model Structure

> **Network design model:**
>
> $$\min \quad \sum_{(i,j) \in A} c_{ij} x_{ij} + \sum_{(i,j) \in A} f_{ij} y_{ij}$$
>
> $$\text{s.t.} \quad \sum_{(i,k) \in A} x_{ik} - \sum_{(k,j) \in A} x_{kj} = b_k \quad \forall \, k \in V \quad \text{(flow conservation)}$$
>
> $$0 \leq x_{ij} \leq u_{ij} \, y_{ij} \quad \forall \, (i,j) \in A \quad \text{(switching)}$$
>
> $$y_{ij} \in \{0,1\}$$

**Deriving arc capacities:** Since no explicit capacities are given, we derive valid upper bounds. For example, $u_{2,3} = 27 + 3 = 30$ (max possible flow is the total supply from nodes 1 and 2).

### 6.3 Wastewater Model (Model 11.21)

**Flow conservation constraints** (supply is negative, demand is positive):

$$-x_{1,2} - x_{1,3} = -27 \quad \text{(node 1)}$$
$$x_{1,2} - x_{2,3} - x_{2,4} = -3 \quad \text{(node 2)}$$
$$x_{1,3} + x_{2,3} + x_{4,3} - x_{3,4} - x_{3,9} = -14 \quad \text{(node 3)}$$
$$x_{2,4} + x_{3,4} + x_{7,4} - x_{4,3} - x_{4,8} = -36 \quad \text{(node 4)}$$
$$-x_{5,6} - x_{5,7} = -21 \quad \text{(node 5)}$$
$$x_{5,6} - x_{6,7} - x_{6,8} = -8 \quad \text{(node 6)}$$
$$x_{5,7} + x_{6,7} - x_{7,4} - x_{7,9} = -13 \quad \text{(node 7)}$$
$$x_{4,8} + x_{6,8} - x_{8,9} = 0 \quad \text{(node 8)}$$
$$x_{3,9} + x_{7,9} + x_{8,9} = 122 \quad \text{(node 9: supersink)}$$

Plus switching constraints on all 15 arcs, and binary requirements on all $y_{ij}$.

**Optimal solution:** Construct arcs (1,3), (2,3), (4,3), (5,7), (6,7), plus treatment plant at node 7 (arc (7,9)). No plant at nodes 3 or 8. Total cost = $15,571,000.

### 6.4 Student Exercise — Wastewater Extension

> **Extension Problem:** The regional planning authority is considering two modifications:
>
> **(a)** *Redundancy requirement:* At least **two** treatment plants must be built (i.e., at least two of arcs (3,9), (7,9), (8,9) must be constructed). Add this constraint.
>
> **(b)** *Pumped-line avoidance:* The pumped line (4,3) is costly to operate. The authority wants to add a penalty: if arc (4,3) is built, an additional annual maintenance cost of 500 (thousand dollars) is incurred. How do you modify the objective?
>
> **(c)** *New development:* A new population center (node 10, population = 15 thousand) is added. It can connect to node 4 via arc (10,4) with fixed cost 400 and variable cost 35, or to node 8 via arc (10,8) with fixed cost 900 and variable cost 20. Write the new flow conservation constraint for node 10 and the switching constraints for both new arcs. What changes at node 9?

---

## 7. Processor Scheduling and Sequencing — Custom Metalworking Application

### 7.1 Context: Single-Machine Scheduling

Before the job shop, consider the simpler Nifty Notes single-machine problem: 6 binding jobs, each with a process time $p_j$, release time $r_j$, and due date $d_j$.

| Job $j$ | 1 | 2 | 3 | 4 | 5 | 6 |
|---------|---|---|---|---|---|---|
| $p_j$ | 12 | 8 | 3 | 10 | 4 | 18 |
| $r_j$ | -20 | -15 | -12 | -10 | -3 | 2 |
| $d_j$ | 10 | 2 | 72 | -8 | -6 | 60 |

### 7.2 Modeling Technique 6: Time Variables and Disjunctive (Conflict) Constraints

**Start-time variables:** $x_j$ = time at which job $j$ begins processing.

**Release constraints:** $x_j \geq \max(0, r_j)$ for all $j$.

**Conflict constraints — The Big-M disjunction:** For each pair $(j, j')$ that share a processor, exactly one must finish before the other starts:

> **Disjunctive conflict constraints:**
>
> $$x_j + p_j \leq x_{j'} + M(1 - y_{j,j'})$$
> $$x_{j'} + p_{j'} \leq x_j + M \, y_{j,j'}$$
>
> where $y_{j,j'} \in \{0,1\}$ equals 1 if job $j$ is scheduled before $j'$, and $M$ is a sufficiently large constant.

**How it works:** If $y_{j,j'} = 1$ (job $j$ first), the first constraint is binding and the second is relaxed by $M$. If $y_{j,j'} = 0$ (job $j'$ first), the roles reverse.

### 7.3 Scheduling Objective Functions

Common objectives (all can be combined with the conflict constraints above):

| Objective | Formula |
|-----------|---------|
| Makespan (max completion) | $\min \; \max_j (x_j + p_j)$ |
| Mean completion time | $\min \; \frac{1}{n} \sum_j (x_j + p_j)$ |
| Maximum lateness | $\min \; \max_j (x_j + p_j - d_j)$ |
| Mean tardiness | $\min \; \frac{1}{n} \sum_j \max(0, x_j + p_j - d_j)$ |

**Linearizing minmax objectives:** Introduce variable $f$ and replace:

$$\min \; f \quad \text{s.t.} \quad f \geq x_j + p_j - d_j \quad \forall j$$

**Linearizing tardiness:** Introduce $t_j \geq 0$ for each job:

$$t_j \geq x_j + p_j - d_j, \quad t_j \geq 0$$

Then minimize $\frac{1}{n} \sum_j t_j$.

**Equivalence results:**
- Minimizing mean completion time, mean flow time, and mean lateness all yield the same optimal schedule.
- An optimal schedule for max lateness is also optimal for max tardiness.

### 7.3a Student Exercise — Single-Machine Scheduling (Nifty Notes)

> **Exercise:** Using the Nifty Notes data above (6 jobs on a single binding machine), formulate the complete ILP for **minimizing maximum tardiness**.
>
> **(a)** Write the release constraints for all 6 jobs. (Recall: $x_j \geq \max(0, r_j)$, and jobs with $r_j < 0$ are already available, so their release constraint is simply $x_j \geq 0$.)
>
> **(b)** How many disjunctive variable pairs $y_{j,j'}$ are needed? Write the conflict constraint pair for jobs 2 and 6.
>
> **(c)** Introduce tardiness variables $t_j \geq 0$ for each job and a variable $T$ representing the maximum tardiness. Write all constraints needed to define $T$ and formulate the complete objective.
>
> **(d)** Suppose the shop acquires a second binding machine, so that **two** jobs can be processed simultaneously. How would you modify the conflict constraints? (*Hint:* Not all pairs of jobs need conflict constraints anymore — only sets of three or more overlapping jobs create conflicts. In fact, with two machines, a simpler approach is to partition the 6 jobs into two groups and schedule each group on its own machine. Think about how to model the machine assignment with new binary variables.)

### 7.4 Job Shop Scheduling — Custom Metalworking (Model 11.28)

**Three jobs**, each requiring a specific sequence of workstations:

- **Job 1 (Die):** WS1 (3 min) → WS2 (10) → WS3 (8) → WS4 (45) → WS6 (1)
- **Job 2 (Cam shaft):** WS7 (50) → WS1 (6) → WS2 (11) → WS3 (6)
- **Job 3 (Fuel Injector):** WS2 (5) → WS3 (9) → WS5 (2) → WS6 (1) → WS4 (25)

**Decision variables:** $x_{j,k}$ = start time of job $j$ on workstation $k$.

**Objective (makespan):** $\min \; \max\{x_{1,6} + 1, \; x_{2,3} + 6, \; x_{3,4} + 25\}$

Linearized: $\min \; f$ with $f \geq x_{1,6} + 1$, $f \geq x_{2,3} + 6$, $f \geq x_{3,4} + 25$.

**Precedence constraints** (within each job):

- Job 1: $x_{1,1} + 3 \leq x_{1,2}$, $\;x_{1,2} + 10 \leq x_{1,3}$, $\;x_{1,3} + 8 \leq x_{1,4}$, $\;x_{1,4} + 45 \leq x_{1,6}$
- Job 2: $x_{2,7} + 50 \leq x_{2,1}$, $\;x_{2,1} + 6 \leq x_{2,2}$, $\;x_{2,2} + 11 \leq x_{2,3}$
- Job 3: $x_{3,2} + 5 \leq x_{3,3}$, $\;x_{3,3} + 9 \leq x_{3,5}$, $\;x_{3,5} + 2 \leq x_{3,6}$, $\;x_{3,6} + 1 \leq x_{3,4}$

**Conflict constraints** (for each pair of jobs sharing a workstation):

Workstations 1, 2, 3, 4, 6 each have potential conflicts. For each conflict pair, we add disjunctive variables $y_{j,j',k}$ and constraint pairs per Principle 11.43. For example:

- **WS1**, jobs 1 & 2: $x_{1,1} + 3 \leq x_{2,1} + M(1-y_{1,2,1})$ and $x_{2,1} + 6 \leq x_{1,1} + My_{1,2,1}$
- **WS2**, jobs 1, 2 & 3: three pairs — (1,2), (1,3), (2,3) — each producing two constraints.
- **WS3**, jobs 1, 2 & 3: three pairs, six constraints.
- **WS4**, jobs 1 & 3: one pair, two constraints.
- **WS6**, jobs 1 & 3: one pair, two constraints.

**Total disjunctive variables:** 10 binary $y_{j,j',k}$ variables.

**Optimal schedule:** All 3 jobs complete in **88 minutes**.

### 7.5 Student Exercise — Scheduling Extension

> **Extension Problem:** Custom Metalworking receives a rush order — a 4th job (Turbine Blade):
>
> - **Job 4:** WS1 (8 min) → WS3 (12) → WS4 (20)
>
> **(a)** Write all new **precedence constraints** for Job 4.
>
> **(b)** Identify all new **conflict pairs** introduced by Job 4 on workstations 1, 3, and 4. Write the disjunctive constraint pair for the conflict between Jobs 2 and 4 on WS1.
>
> **(c)** How does the makespan objective change? Write the updated linearized formulation.
>
> **(d)** How many total binary disjunctive variables does the full 4-job model require?

---

## 8. Summary of Integer Modeling Techniques

| Technique | Variables | Key Constraint Pattern | Example |
|-----------|-----------|----------------------|---------|
| All-or-nothing | $y_j \in \{0,1\}$; substitute $x_j = u_j y_j$ | Replaces continuous variables | Swedish Steel |
| Fixed charges | $y_j \in \{0,1\}$; $f_j y_j$ in objective | Switching: $x_j \leq u_j y_j$ | Swedish Steel |
| Budget limits | $x_j \in \{0,1\}$ | $\sum a_{tj} x_j \leq b_t$ | NASA |
| Mutual exclusivity | $x_j \in \{0,1\}$ | $\sum_{j \in S} x_j \leq 1$ | NASA |
| Dependencies | $x_j \in \{0,1\}$ | $x_j \leq x_i$ | NASA |
| Set covering/packing | $x_j \in \{0,1\}$ | $\sum_{j \in N_i} x_j \geq 1$ (or $\leq$ or $=$) | EMS |
| Penalizing uncovered | $y_i \in \{0,1\}$ slack | $\sum x_j + y_i \geq 1$; min $\sum v_i y_i$ | EMS max coverage |
| Facility location | $y_i \in \{0,1\}$, $x_{ij} \geq 0$ | Demand fulfillment + capacity switching | Tmark |
| Network design | $y_{ij} \in \{0,1\}$, $x_{ij} \geq 0$ | Flow conservation + $x_{ij} \leq u_{ij} y_{ij}$ | Wastewater |
| Scheduling conflicts | $y_{j,j'} \in \{0,1\}$ | Big-M disjunction pairs | Custom Metalworking |
| Linearize minmax | New variable $f$ | $f \geq$ each element | Scheduling objectives |

---

## 9. Looking Ahead

Next lecture: **Chapter 12 — Exact Methods for Integer Optimization**, including LP relaxation, branch and bound, and branch and cut. The models we formulated today will serve as our test cases.
