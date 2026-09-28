# ISYE 671: Linear Optimization and Network Flows
# Lecture Notes — Optimization under Uncertainty

**Northern Illinois University — Spring 2026**
**Instructor: Dr. Ziteng Wang**

---

## 1. Introduction: Why Uncertainty Matters

Every optimization model we have studied so far in this course — LP, IP, network flows — assumes that all data (costs, capacities, demands, travel times) are **known with certainty**. In practice, this assumption is rarely true:

- Demand for products is uncertain when production decisions must be made.
- Travel times fluctuate due to weather and traffic.
- Supply quantities from vendors may be unreliable.
- Patient arrivals at an emergency department are stochastic.

How should we make optimal decisions when the data is uncertain? This is the central question of **optimization under uncertainty**. There are two major paradigms, distinguished by how they represent and respond to uncertainty:

- **Stochastic programming** assumes we have (or can estimate) a *probability distribution* over the uncertain parameters. We optimize the *expected* outcome, possibly with recourse actions taken after uncertainty is revealed.
- **Robust optimization** assumes we only know that uncertain parameters lie within some *uncertainty set*, without probabilities. We optimize against the *worst case* within that set.

These are complementary, not competing, approaches. The right choice depends on what you know about the uncertainty and what guarantees you need.

> **Connection to prior material**: The LP and IP models from earlier lectures become the *building blocks* of both stochastic and robust programs. If you can formulate a deterministic LP, you can extend it to handle uncertainty using either paradigm.

This lecture covers four major approaches, organized by paradigm:

**Stochastic programming** (Sections 2–4):

1. **Two-stage stochastic programming** — the workhorse: decide now, adjust later.
2. **Chance-constrained programming** — controlling the probability of constraint violation.

**Robust optimization** (Section 5):

3. **Robust counterparts** — protecting against worst-case uncertainty without probabilities.

**Synthesis** (Section 6–7):

4. **Stochastic integer programming** — combining IP with uncertainty.
5. **Comparison and guidance** — when to use which approach.

---

## 2. Uncertainty Modeling: Scenarios

### 2.1 The Scenario Approach

The most common way to represent uncertainty in optimization is through **discrete scenarios**. Let $\Omega = \{\omega_1, \omega_2, \ldots, \omega_S\}$ be a finite set of scenarios, each occurring with probability $p_s$ (where $\sum_{s=1}^{S} p_s = 1$). Each scenario $\omega_s$ specifies a realization of all uncertain parameters.

**Example**: A brewery must decide how much grain to purchase *before* knowing next month's beer demand. Demand could be Low (4,000 barrels, probability 0.3), Medium (6,000 barrels, probability 0.5), or High (9,000 barrels, probability 0.2).

| Scenario | Demand (barrels) | Probability |
|----------|-----------------|-------------|
| $\omega_1$: Low | 4,000 | 0.3 |
| $\omega_2$: Medium | 6,000 | 0.5 |
| $\omega_3$: High | 9,000 | 0.2 |

### 2.2 When Are Decisions Made?

The key modeling question is: *which decisions must be made before uncertainty is revealed, and which can wait?*

- **Here-and-now decisions** (first stage): Committed before observing the random outcome. Examples: capacity investment, raw material purchases, facility locations.
- **Wait-and-see decisions** (second stage): Made after the scenario is revealed. Examples: production quantities, overtime scheduling, emergency procurement.

This timing distinction is the foundation of two-stage stochastic programming.

### 2.3 Where Do Scenarios Come From?

In practice, scenarios are derived from:

- **Historical data**: Past demand records, weather patterns, or failure rates.
- **Expert judgment**: Domain experts estimate a small number of representative outcomes.
- **Monte Carlo simulation**: Sample from a known probability distribution (e.g., normal demand) and use the samples as scenarios.
- **Scenario reduction**: Start with many simulated scenarios and reduce to a manageable set that preserves the distribution's key properties.

For this course, we assume scenarios are given. The focus is on how to formulate and solve the resulting optimization problems.

---

## 3. Two-Stage Stochastic Linear Programming

### 3.1 General Structure

A two-stage stochastic LP has the form:

**First stage:**

$$\min_{x} \; c^\top x + \mathbb{E}_\omega \left[ Q(x, \omega) \right]$$

subject to:

$$Ax = b, \quad x \geq 0$$

where $Q(x, \omega)$ is the **recourse function** — the optimal value of the second-stage problem given first-stage decision $x$ and scenario $\omega$:

**Second stage** (for each scenario $\omega_s$):

$$Q(x, \omega_s) = \min_{y_s} \; q_s^\top y_s$$

subject to:

$$W y_s = h_s - T_s x, \quad y_s \geq 0$$

**Interpretation of the components:**

| Symbol | Meaning | Example |
|--------|---------|---------|
| $x$ | First-stage decisions | Grain purchased |
| $c$ | First-stage costs | Purchase price |
| $y_s$ | Second-stage decisions under scenario $s$ | Production, overtime |
| $q_s$ | Second-stage costs | Production and penalty costs |
| $T_s$ | Technology matrix linking stages | How grain converts to beer |
| $h_s$ | Right-hand side under scenario $s$ | Demand realization |
| $W$ | Recourse matrix | Production technology |

### 3.2 A Recipe for Formulating Two-Stage Stochastic LPs

When facing a new problem, follow these steps:

**Step 1 — Identify the timing.** Ask: *"What must I decide before I learn the uncertain information?"* These are first-stage variables ($x$). Then ask: *"What can I decide after?"* These are second-stage variables ($y_s$).

**Step 2 — Identify what is uncertain.** Which parameters change across scenarios? Common choices: demand, supply, costs, yields. These become scenario-indexed parameters.

**Step 3 — Write the deterministic version.** Formulate the problem as if all parameters were known. This gives you the constraint structure.

**Step 4 — Replicate for scenarios.** Copy the second-stage constraints for each scenario $s$, with scenario-specific parameters. Index all second-stage variables by $s$.

**Step 5 — Set the objective.** First-stage cost (not scenario-dependent) + probability-weighted sum of second-stage costs.

**Step 6 — Count variables and constraints.** Verify the model size: if the deterministic model has $n_1$ first-stage variables, $n_2$ second-stage variables, and $m_2$ second-stage constraints, then the extensive form has $n_1 + S \cdot n_2$ variables and $m_1 + S \cdot m_2$ constraints, where $m_1$ is the number of first-stage constraints.

### 3.3 The Deterministic Equivalent (Extensive Form)

For a finite number of scenarios, the two-stage stochastic LP can be reformulated as a single large LP called the **deterministic equivalent** or **extensive form**:

$$\min \; c^\top x + \sum_{s=1}^{S} p_s \, q_s^\top y_s$$

subject to:

$$Ax = b$$

$$T_s x + W y_s = h_s \quad \forall \, s = 1, \ldots, S$$

$$x \geq 0, \quad y_s \geq 0 \quad \forall \, s$$

This is a *standard LP* — it can be solved directly with any LP solver, including AMPL/Gurobi. The structure is block-angular: the first-stage variables $x$ link all scenarios, while the second-stage variables $y_s$ are scenario-specific.

$$\begin{bmatrix} A & & & \\ T_1 & W & & \\ T_2 & & W & \\ \vdots & & & \ddots \\ T_S & & & & W \end{bmatrix} \begin{bmatrix} x \\ y_1 \\ y_2 \\ \vdots \\ y_S \end{bmatrix} = \begin{bmatrix} b \\ h_1 \\ h_2 \\ \vdots \\ h_S \end{bmatrix}$$

> **Key insight**: The extensive form grows linearly with the number of scenarios. With 3 scenarios, the model is roughly 3× the size of the deterministic version. With 1,000 scenarios, the model can become very large — motivating the decomposition methods covered in the large-scale methods lecture.

### 3.4 Worked Example 1: Brewery Grain Purchase

**Problem**: Prairie Wind Brewing must purchase grain *now* (first stage) for next month's production. Grain costs \$50/unit. Each unit of grain yields 500 barrels of beer, which sells for \$25/barrel. If demand exceeds production capacity, the brewery can buy emergency grain at \$80/unit. Unsold beer is wasted (no salvage).

**Scenarios:**

| Scenario $s$ | Demand $d_s$ (barrels) | Probability $p_s$ |
|---|---|---|
| 1 (Low) | 4,000 | 0.3 |
| 2 (Medium) | 6,000 | 0.5 |
| 3 (High) | 9,000 | 0.2 |

**Applying the recipe:**

*Step 1 (Timing)*: Grain purchase ($x$) must happen now. Production, emergency purchasing, and waste ($y_s$) happen after demand is known.

*Step 2 (Uncertainty)*: Demand $d_s$ varies by scenario.

*Step 3 (Deterministic version)*: If demand were known to be $d$:

$$\min \; 50x + 80y^{\text{emerg}} - 25y^{\text{prod}}$$

subject to: $y^{\text{prod}} \leq d$, $y^{\text{prod}} + y^{\text{waste}} = 500(x + y^{\text{emerg}})$, all variables $\geq 0$.

*Step 4 (Replicate)*: Index second-stage variables and demand by scenario.

*Step 5 (Objective)*: Weight second-stage costs by probabilities.

**Complete formulation:**

$$\min \; 50x + \sum_{s=1}^{3} p_s \left[ 80 \, y_s^{\text{emerg}} - 25 \, y_s^{\text{prod}} \right]$$

subject to:

$$y_s^{\text{prod}} \leq d_s \quad \forall \, s \qquad \text{(cannot sell more than demand)}$$

$$y_s^{\text{prod}} + y_s^{\text{waste}} = 500(x + y_s^{\text{emerg}}) \quad \forall \, s \qquad \text{(production balance)}$$

$$x \geq 0, \quad y_s^{\text{prod}}, y_s^{\text{emerg}}, y_s^{\text{waste}} \geq 0 \quad \forall \, s$$

*Step 6 (Size)*: 1 first-stage variable + $3 \times 3 = 9$ second-stage variables = 10 variables. 0 first-stage constraints + $3 \times 2 = 6$ second-stage constraints = 6 constraints. This is a small LP.

*(Full AMPL implementation is provided in the companion Colab notebook.)*

### 3.5 Worked Example 2: Community Clinic Staffing

**Problem**: A community health clinic must decide how many nurses to hire for next month *before* knowing patient volume. Each nurse costs \$5,000/month and can serve 150 patients. If patient demand exceeds capacity, the clinic must hire temporary nurses at \$8,000 each (also serving 150 patients). If there is excess capacity, nurses can be assigned to administrative tasks (no additional cost or benefit).

**Scenarios:**

| Scenario | Patients | Probability |
|----------|----------|-------------|
| Flu outbreak | 1,200 | 0.20 |
| Normal winter | 800 | 0.50 |
| Mild season | 500 | 0.30 |

**Applying the recipe:**

*Step 1 (Timing)*: Number of permanent nurses to hire ($x$) — first stage. Number of temporary nurses ($y_s^{\text{temp}}$) and patients served ($y_s^{\text{served}}$) — second stage.

*Step 2 (Uncertainty)*: Patient volume $d_s$ varies by scenario.

**Formulation:**

$$\min \; 5000x + \sum_{s=1}^{3} p_s \left[ 8000 \, y_s^{\text{temp}} \right]$$

subject to:

$$y_s^{\text{served}} \leq d_s \quad \forall \, s \qquad \text{(cannot serve more than demand)}$$

$$y_s^{\text{served}} \leq 150(x + y_s^{\text{temp}}) \quad \forall \, s \qquad \text{(capacity from hired + temp nurses)}$$

$$y_s^{\text{served}} = d_s \quad \forall \, s \qquad \text{(all patients must be served — clinic policy)}$$

$$x \geq 0, \; x \in \mathbb{Z}, \quad y_s^{\text{temp}} \geq 0, \; y_s^{\text{temp}} \in \mathbb{Z} \quad \forall \, s$$

Note that the "all patients must be served" policy converts the $\leq d_s$ constraint into equality: $y_s^{\text{served}} = d_s$. Substituting:

$$\min \; 5000x + \sum_{s=1}^{3} p_s \left[ 8000 \, y_s^{\text{temp}} \right]$$

subject to:

$$d_s \leq 150(x + y_s^{\text{temp}}) \quad \forall \, s \qquad \text{(must have enough nurses for all patients)}$$

$$x \geq 0, \quad y_s^{\text{temp}} \geq 0 \quad \forall \, s$$

This simplifies to: in each scenario, the temporary nurses make up the shortfall: $y_s^{\text{temp}} \geq \lceil d_s / 150 \rceil - x$. The trade-off is clear: hiring more permanent nurses (cheaper per unit) reduces the expected need for expensive temps.

*Size*: 1 first-stage variable + 3 second-stage variables = 4 variables. 3 constraints. Tiny LP (or IP if integrality is enforced).

### 3.6 Worked Example 3: Agricultural Crop Planning (Multi-Product)

**Problem**: A farmer has 500 acres and must decide *before the growing season* how many acres to plant with wheat, corn, and soybeans. Yields (tons/acre) depend on weather. After harvest, the farmer sells crops at market prices but must also meet minimum feed requirements (200 tons of wheat and 240 tons of corn for livestock). Any shortfall must be purchased at a 40% premium over selling price. Excess production is sold.

**Scenarios:**

| Scenario | Wheat yield | Corn yield | Soybean yield | Probability |
|----------|-----------|-----------|-------------|-------------|
| Good weather | 3.0 | 3.6 | 4.0 | 0.3 |
| Average | 2.5 | 3.0 | 3.2 | 0.4 |
| Poor weather | 2.0 | 2.4 | 2.4 | 0.3 |

**Prices**: Wheat sells at \$170/ton, corn at \$150/ton, soybeans at \$36/ton. Purchase prices for shortfall (40% premium): wheat \$238/ton, corn \$210/ton.

**Planting costs**: Wheat \$150/acre, corn \$230/acre, soybeans \$260/acre.

**Applying the recipe:**

*Step 1 (Timing)*: Planting decisions (acres of each crop) — first stage. Sales, purchases, and shortfalls — second stage.

*Step 2 (Uncertainty)*: Yields vary by scenario. Prices are known.

**Sets and variables:**

- First stage: $x_w, x_c, x_b$ = acres planted (wheat, corn, soybeans)
- Second stage (per scenario $s$): $w_s, c_s, b_s$ = tons sold; $p_s^w, p_s^c$ = tons purchased to meet feed requirements

**Formulation:**

$$\min \; 150 x_w + 230 x_c + 260 x_b + \sum_{s=1}^{3} p_s \left[ 238 p_s^w + 210 p_s^c - 170 w_s - 150 c_s - 36 b_s \right]$$

subject to:

$$x_w + x_c + x_b \leq 500 \qquad \text{(total acreage)}$$

$$\text{yield}_s^w \cdot x_w + p_s^w - w_s \geq 200 \quad \forall \, s \qquad \text{(wheat feed requirement)}$$

$$\text{yield}_s^c \cdot x_c + p_s^c - c_s \geq 240 \quad \forall \, s \qquad \text{(corn feed requirement)}$$

$$b_s \leq \text{yield}_s^b \cdot x_b \quad \forall \, s \qquad \text{(can only sell what you grow)}$$

$$w_s \leq \text{yield}_s^w \cdot x_w - 200 + p_s^w \quad \forall \, s \qquad \text{(wheat sales ≤ surplus)}$$

$$c_s \leq \text{yield}_s^c \cdot x_c - 240 + p_s^c \quad \forall \, s \qquad \text{(corn sales ≤ surplus)}$$

$$x_w, x_c, x_b \geq 0, \quad w_s, c_s, b_s, p_s^w, p_s^c \geq 0 \quad \forall \, s$$

*Size*: 3 first-stage variables + $3 \times 5 = 15$ second-stage variables = 18 variables. 1 first-stage constraint + $3 \times 5 = 15$ second-stage constraints = 16 constraints. A moderate LP.

**What makes this example pedagogically valuable:**

- **Multiple first-stage decisions** (three crops, not just one purchase quantity).
- **Multiple uncertain parameters** (three yields change simultaneously across scenarios).
- **Recourse involves both buying and selling** — the second stage has richer structure.
- **Constraints link both stages** — the feed requirements couple planting decisions with post-harvest actions.
- **The high purchase penalty** (40% premium) makes it expensive to skip planting and rely on buying, forcing diversification across crops.

This is adapted from the classic farmer problem in Birge & Louveaux (1997).

### 3.7 Worked Example 4: Emergency Supply Pre-Positioning

**Problem**: A regional disaster relief agency must decide how many emergency supply kits to pre-position at each of 3 warehouses *before hurricane season*. Each kit costs \$200 to pre-position. After a hurricane strikes, kits are shipped from warehouses to affected zones. Shipping costs depend on which zones are hit (uncertain). Unmet demand incurs a penalty of \$500/kit (representing human cost of unserved need). Unused kits have a salvage value of \$50.

**Warehouses and zones:**

| | Zone A | Zone B | Zone C |
|---|---|---|---|
| Warehouse 1 (shipping \$/kit) | 20 | 40 | 60 |
| Warehouse 2 (shipping \$/kit) | 50 | 15 | 35 |
| Warehouse 3 (shipping \$/kit) | 45 | 30 | 10 |

Each warehouse has capacity for 500 kits.

**Scenarios:**

| Scenario | Zone A demand | Zone B demand | Zone C demand | Probability |
|----------|-------------|-------------|-------------|-------------|
| S1: Cat-1 (mild) | 100 | 80 | 50 | 0.40 |
| S2: Cat-3 (moderate) | 300 | 200 | 150 | 0.35 |
| S3: Cat-5 (severe) | 500 | 400 | 350 | 0.15 |
| S4: No hurricane | 0 | 0 | 0 | 0.10 |

**Applying the recipe:**

*Step 1 (Timing)*: Pre-positioning quantities $x_i$ at each warehouse $i = 1, 2, 3$ — first stage. Shipping allocations $y_{ij,s}$ from warehouse $i$ to zone $j$ in scenario $s$, plus shortfall $u_{j,s}$ and salvage $v_{i,s}$ — second stage.

*Step 2 (Uncertainty)*: Demand at each zone varies by scenario. Four scenarios, some with zero demand.

**Formulation:**

$$\min \; \sum_{i=1}^{3} 200 \, x_i + \sum_{s=1}^{4} p_s \left[ \sum_{i=1}^{3} \sum_{j=1}^{3} c_{ij} \, y_{ij,s} + 500 \sum_{j=1}^{3} u_{j,s} - 50 \sum_{i=1}^{3} v_{i,s} \right]$$

subject to:

$$x_i \leq 500 \quad \forall \, i \qquad \text{(warehouse capacity)}$$

$$\sum_{j=1}^{3} y_{ij,s} + v_{i,s} = x_i \quad \forall \, i, s \qquad \text{(ship out or salvage everything pre-positioned)}$$

$$\sum_{i=1}^{3} y_{ij,s} + u_{j,s} = d_{j,s} \quad \forall \, j, s \qquad \text{(meet demand or record shortfall)}$$

$$x_i \geq 0, \quad y_{ij,s}, u_{j,s}, v_{i,s} \geq 0 \quad \forall \, i, j, s$$

*Size*: 3 first-stage variables + $4 \times (9 + 3 + 3) = 60$ second-stage variables = 63 variables. 3 first-stage constraints + $4 \times (3 + 3) = 24$ second-stage constraints = 27 constraints.

**What makes this example pedagogically valuable:**

- **Multiple first-stage decisions across locations** (spatial pre-positioning).
- **Transportation structure** in the second stage (warehouse-to-zone shipping).
- **Penalty for unmet demand** — models the real-world cost of under-preparation.
- **Salvage value** — unused resources have economic value, creating a non-trivial trade-off.
- **The "no hurricane" scenario** (S4) is critical: it shows that pre-positioned kits are not wasted — they have salvage value, which limits the cost of over-preparation.
- **This connects to network flow** models from earlier in the course.

### 3.8 The Extensive Form in AMPL: A General Pattern

All four examples above follow the same AMPL pattern. The key is indexing second-stage variables and constraints by scenario:

```
set SCENARIOS;
param prob{SCENARIOS} >= 0;

# ---- First-stage variables (not indexed by scenario) ----
var x{...} >= 0;

# ---- Second-stage variables (indexed by scenario) ----
var y{..., SCENARIOS} >= 0;

# ---- Objective: first-stage cost + expected second-stage cost ----
minimize total_cost:
    (first-stage cost terms)
    + sum{s in SCENARIOS} prob[s] * (second-stage cost terms for s);

# ---- First-stage constraints ----
subject to first_stage_constraint{...}: ... ;

# ---- Second-stage constraints (one copy per scenario) ----
subject to second_stage_constraint{..., s in SCENARIOS}: ... ;
```

This is the **explicit extensive form** approach. For modest numbers of scenarios (up to hundreds), this works well with Gurobi through AMPL. For thousands of scenarios, decomposition methods (Benders decomposition, covered in the large-scale methods lecture) are needed.

> **Modeling tip**: When writing the AMPL model, start with the deterministic version (no scenarios). Then add `s in SCENARIOS` to the second-stage variables, constraints, and objective. This mechanical process mirrors the recipe from Section 3.2.

### 3.9 Value of the Stochastic Solution (VSS)

How much do we gain by modeling uncertainty explicitly? The **value of the stochastic solution** quantifies this.

**Definitions:**

1. **Expected Value (EV) solution**: Replace all random parameters with their expected values, solve the resulting deterministic model, and obtain decision $x^{EV}$.
2. **Expected result of the EV solution (EEV)**: Evaluate $x^{EV}$ across all scenarios: $EEV = c^\top x^{EV} + \sum_s p_s \, Q(x^{EV}, \omega_s)$.
3. **Recourse Problem (RP) solution**: Solve the full stochastic program to get optimal $x^{RP}$ with objective $RP$.

Then:

$$VSS = EEV - RP$$

The VSS measures the expected cost savings from using the stochastic model instead of the naive expected-value approach. A large VSS indicates that uncertainty significantly impacts the optimal decision, justifying the added modeling complexity.

### 3.10 Wait-and-See (WS) and Expected Value of Perfect Information (EVPI)

If we could know the future perfectly, we would solve each scenario independently:

$$WS = \sum_{s=1}^{S} p_s \, z_s^*$$

where $z_s^*$ is the optimal objective for scenario $s$ alone (choosing both $x$ and $y_s$ optimally).

The **expected value of perfect information** is:

$$EVPI = RP - WS$$

The EVPI represents the maximum amount we should pay for a perfect forecast. It provides an upper bound on the value of any information-gathering activity (market research, better sensors, etc.).

**Summary of key quantities:**

$$WS \leq RP \leq EEV$$

$$EVPI = RP - WS \geq 0, \qquad VSS = EEV - RP \geq 0$$

**Numerical illustration** (from the brewery example, solved in the companion notebook):

| Quantity | Value | Interpretation |
|----------|-------|----------------|
| WS | Best possible cost with perfect foresight | Lower bound on achievable cost |
| RP | Optimal stochastic solution | What we actually achieve |
| EEV | Cost if we ignore uncertainty | What happens with the naive approach |
| EVPI = RP − WS | Value of a perfect forecast | Maximum worth of better information |
| VSS = EEV − RP | Benefit of stochastic modeling | Savings from modeling uncertainty |

---

## 4. Chance-Constrained Programming

### 4.1 Motivation

Sometimes, rather than optimizing the expected cost of recourse, we want to ensure that constraints are satisfied with high probability. This leads to **chance-constrained programming**.

**Example**: A hospital must staff enough nurses so that patient demand is met at least 95% of the time. We do not want to build an explicit recourse model — we simply want the schedule to be feasible in 95% of scenarios.

### 4.2 Individual Chance Constraints

An individual chance constraint has the form:

$$\Pr\left( a(\omega)^\top x \leq b(\omega) \right) \geq 1 - \epsilon$$

where $\epsilon$ is the allowed probability of violation (e.g., $\epsilon = 0.05$ for 95% reliability).

**Scenario-based reformulation**: With discrete scenarios $\{1, \ldots, S\}$, introduce binary indicator variables $z_s \in \{0, 1\}$:

$$a_s^\top x \leq b_s + M z_s \quad \forall \, s = 1, \ldots, S$$

$$\sum_{s=1}^{S} p_s \, z_s \leq \epsilon$$

$$z_s \in \{0, 1\}$$

Here, $z_s = 1$ means the constraint is violated in scenario $s$, and the second constraint ensures the total probability of violation does not exceed $\epsilon$. This converts the chance constraint into a **mixed-integer program**.

### 4.3 Joint Chance Constraints

A joint chance constraint requires that *all* constraints in a system are satisfied simultaneously with high probability:

$$\Pr\left( A(\omega) x \leq b(\omega) \right) \geq 1 - \epsilon$$

The scenario-based reformulation uses a single indicator per scenario:

$$A_s x \leq b_s + M z_s \cdot \mathbf{1} \quad \forall \, s$$

$$\sum_{s=1}^{S} p_s \, z_s \leq \epsilon$$

This is more restrictive than individual chance constraints (it requires all constraints to hold simultaneously in $1-\epsilon$ fraction of scenarios).

### 4.4 Worked Example: Food Bank Warehouse Leasing

A food bank must decide how many square feet of warehouse space to lease for the coming month. Monthly donation volumes are uncertain — the food bank has 10 historical monthly records. The lease costs \$5/sq ft per month. The food bank wants to ensure that donations can be stored without overflow in at least 90% of scenarios.

**Data** (10 equally likely historical donation volumes, in sq ft):

| S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|----|----|----|----|----|----|----|----|----|-----|
| 3,200 | 4,100 | 3,800 | 5,200 | 4,500 | 3,600 | 6,100 | 4,800 | 5,500 | 4,000 |

Each scenario has probability $p_s = 0.1$.

**Formulation**: Let $x$ = warehouse space leased (sq ft). Let $z_s \in \{0, 1\}$ indicate whether the storage constraint is violated in scenario $s$. Let $\epsilon = 0.10$ (allowing 10% violation probability for 90% reliability).

$$\min \; 5x$$

subject to:

$$\text{donations}_s \leq x + M z_s \quad \forall \, s = 1, \ldots, 10$$

$$\sum_{s=1}^{10} 0.1 \cdot z_s \leq 0.10$$

$$z_s \in \{0, 1\}, \quad x \geq 0$$

**Interpretation**: The reliability constraint $\sum_s 0.1 \cdot z_s \leq 0.10$ means at most 1 of the 10 scenarios can be violated ($0.1 \times 1 = 0.10 \leq 0.10$). The model will therefore choose $x$ large enough to cover 9 out of 10 scenarios, allowing the single worst-case scenario (S7: 6,100 sq ft) to be violated. The optimal space is the **second-largest** donation volume: $x^* = 5,500$ sq ft, with monthly cost \$27,500.

If we increase reliability to 95% ($\epsilon = 0.05$), no scenarios can be violated ($0.1 \times 1 = 0.10 > 0.05$), so the model must cover all 10 scenarios: $x^* = 6,100$ sq ft, costing \$30,500/month. The 5 percentage-point increase in reliability costs an additional \$3,000/month.

*(Full implementation with multiple reliability levels is provided in the companion Colab notebook.)*

### 4.5 Comparison of Approaches

| Feature | Two-Stage Recourse | Chance Constraints |
|---------|-------------------|-------------------|
| Philosophy | Optimize expected cost of corrective actions | Ensure feasibility with high probability |
| Decision structure | First and second stage | Single stage |
| Model type | LP (extensive form) | MIP (binary indicators) |
| Output | Decisions + recourse plan per scenario | Decisions + reliability guarantee |
| When to use | When corrective actions exist and have known costs | When hard feasibility is required |

---

## 5. Paradigm II: Robust Optimization

### 5.1 Motivation — A Different Philosophy

Stochastic programming requires probability distributions for uncertain parameters. When these distributions are unknown or unreliable — for example, when facing a novel disruption with no historical precedent — we need a different approach.

**Robust optimization** does not use probabilities at all. Instead, it assumes the uncertain parameters lie within a defined **uncertainty set** and optimizes against the *worst-case* realization within that set. The result is a solution that is guaranteed feasible for any outcome in the uncertainty set.

This is a fundamentally different philosophy from stochastic programming:

- **Stochastic programming** asks: *"What decision minimizes expected cost, given a probability distribution over outcomes?"*
- **Robust optimization** asks: *"What decision performs best in the worst case, given a set of possible outcomes?"*

### 5.2 The Robust Counterpart

Consider the LP:

$$\min \; c^\top x \quad \text{subject to} \quad a_i^\top x \leq b_i, \; i = 1, \ldots, m$$

If the constraint coefficients $a_i$ are uncertain and lie in an uncertainty set $\mathcal{U}_i$, the robust counterpart requires feasibility for *all* realizations:

$$\min \; c^\top x \quad \text{subject to} \quad a_i^\top x \leq b_i \quad \forall \, a_i \in \mathcal{U}_i, \; i = 1, \ldots, m$$

The shape of $\mathcal{U}_i$ determines the tractability and conservatism of the robust model.

### 5.3 Common Uncertainty Sets

**Box uncertainty** (interval): Each coefficient varies independently within an interval.

$$\mathcal{U}_i = \{ a_i : | a_{ij} - \bar{a}_{ij} | \leq \hat{a}_{ij}, \; \forall j \}$$

The robust counterpart replaces each constraint with:

$$\bar{a}_i^\top x + \sum_j \hat{a}_{ij} |x_j| \leq b_i$$

For $x \geq 0$, this simplifies to $(\bar{a}_i + \hat{a}_i)^\top x \leq b_i$, which is a *single linear constraint*. This is the most conservative: it protects against all coefficients being at their worst simultaneously.

**Ellipsoidal uncertainty**: Coefficients are correlated and lie within an ellipsoid.

$$\mathcal{U}_i = \{ a_i : \| \Sigma_i^{-1/2} (a_i - \bar{a}_i) \|_2 \leq \Gamma_i \}$$

The robust counterpart introduces a second-order cone constraint:

$$\bar{a}_i^\top x + \Gamma_i \| \Sigma_i^{1/2} x \|_2 \leq b_i$$

This is a **second-order cone program (SOCP)**, which Gurobi can solve natively.

**Budget uncertainty** (Bertsimas–Sim): At most $\Gamma_i$ coefficients deviate from their nominal values simultaneously.

$$\mathcal{U}_i = \left\{ a_i : a_{ij} = \bar{a}_{ij} + \hat{a}_{ij} \zeta_{ij}, \; |\zeta_{ij}| \leq 1, \; \sum_j |\zeta_{ij}| \leq \Gamma_i \right\}$$

The parameter $\Gamma_i \in [0, n]$ controls the degree of conservatism. When $\Gamma_i = 0$, the model reduces to the nominal (deterministic) LP. When $\Gamma_i = n$, it is equivalent to box uncertainty. The budget robust counterpart is an LP, making it both tractable and flexible:

$$\bar{a}_i^\top x + \max_{\zeta \in \mathcal{Z}_i} \sum_j \hat{a}_{ij} \zeta_{ij} x_j \leq b_i$$

which can be reformulated with auxiliary variables as:

$$\bar{a}_i^\top x + \Gamma_i \lambda_i + \sum_j \mu_{ij} \leq b_i$$

$$\lambda_i + \mu_{ij} \geq \hat{a}_{ij} |x_j| \quad \forall \, j$$

$$\lambda_i, \mu_{ij} \geq 0$$

### 5.4 Worked Example: Warehouse Leasing with Budget Uncertainty

Revisiting the food bank warehouse from Section 4.4, suppose we do not have discrete scenarios. Instead, we know that donations come from 5 sources — Retail (nominal 1,200 sq ft), Wholesale (900), Corporate (1,000), Individual (800), and Events (600) — and each source may deviate by up to ±20% from its nominal value. We want to lease enough space to handle all plausible donation volumes.

**Data**:

| Source | Nominal $\bar{a}_j$ | Deviation $\hat{a}_j$ (±20%) |
|--------|---------------------|------------------------------|
| Retail | 1,200 | 240 |
| Wholesale | 900 | 180 |
| Corporate | 1,000 | 200 |
| Individual | 800 | 160 |
| Events | 600 | 120 |
| **Total** | **4,500** | **900** |

Lease cost: \$5/sq ft. The robust constraint is: $x \geq \sum_j a_j$ for all $(a_1, \ldots, a_5)$ in the uncertainty set.

**Budget uncertainty formulation** with parameter $\Gamma$ (at most $\Gamma$ sources deviate simultaneously):

$$\min \; 5x$$

subject to:

$$x \geq 4500 + \Gamma \lambda + \sum_{j=1}^{5} \mu_j$$

$$\lambda + \mu_j \geq \hat{a}_j \quad \forall \, j = 1, \ldots, 5$$

$$\lambda, \mu_j \geq 0$$

**Results** for different values of $\Gamma$:

| $\Gamma$ | Interpretation | Space (sq ft) | Monthly Cost |
|-----------|---------------|---------------|-------------|
| 0 | Nominal (no uncertainty) | 4,500 | \$22,500 |
| 1 | At most 1 source deviates | 4,740 | \$23,700 |
| 2 | At most 2 sources deviate | 4,940 | \$24,700 |
| 3 | At most 3 sources deviate | 5,100 | \$25,500 |
| 5 | All sources deviate (box) | 5,400 | \$27,000 |

The $\Gamma = 5$ case (box uncertainty) gives the most conservative solution — all sources at their worst simultaneously. With $\Gamma = 2$, we hedge against 2 sources deviating, a more practical middle ground. The difference between $\Gamma = 0$ and $\Gamma = 5$ is \$4,500/month — the **price of robustness**.

*(Full implementation with visualization is provided in the companion Colab notebook.)*

### 5.5 Comparison: Stochastic vs. Robust

| Feature | Stochastic Programming | Robust Optimization |
|---------|----------------------|-------------------|
| Uncertainty model | Probability distribution (scenarios) | Uncertainty set (no probabilities) |
| Objective | Minimize expected cost | Minimize worst-case cost |
| Conservatism | Moderate (averages over scenarios) | Higher (protects against worst case) |
| Data requirement | Scenario probabilities | Uncertainty set bounds |
| Model size | Grows with number of scenarios | Grows with size of uncertainty set |
| Tractability | LP (extensive form) | LP, SOCP, or MIP depending on set |

> **Practical guidance**: Use stochastic programming when reliable probability data is available (historical demand records, simulation). Use robust optimization when you know the range of uncertainty but not its distribution (new product launch, novel supply chain disruption). In many applications, both approaches are applied and their solutions compared to inform the final decision.

---

## 6. Choosing the Right Paradigm

The choice between stochastic and robust optimization is a modeling decision, much like choosing between LP and IP. Here is a decision guide:

**Use stochastic programming when:**
- You have historical data or simulation models that provide credible scenario probabilities.
- Recourse actions (corrective decisions after uncertainty is revealed) exist and have known costs.
- You want an *expected-cost-optimal* decision that performs well on average.
- Example: ordering inventory when demand follows a known seasonal pattern.

**Use chance-constrained programming when:**
- Hard feasibility is required with a specified confidence level (e.g., "meet demand 95% of the time").
- You have discrete scenarios but care about reliability rather than expected cost.
- Example: hospital staffing to ensure adequate nurse coverage.

**Use robust optimization when:**
- Probability data is unavailable, unreliable, or hard to estimate.
- You need guaranteed feasibility for *any* plausible outcome (safety-critical applications).
- The uncertainty set is easier to define than the probability distribution.
- Example: infrastructure design for uncertain climate conditions.

**Hybrid approaches** are increasingly common: use robust optimization for constraints where feasibility is critical, and stochastic programming for the objective where expected performance matters.

---

## 7. Stochastic Integer Programming (Brief Overview)

When first-stage decisions are integer (e.g., facility location under uncertain demand), the problem becomes a **stochastic integer program**. The extensive form is a large MIP:

$$\min \; c^\top x + \sum_{s=1}^{S} p_s \, q_s^\top y_s$$

subject to:

$$Ax = b, \quad T_s x + W y_s = h_s \; \forall \, s, \quad x \in \mathbb{Z}^{n_1}, \; y_s \geq 0$$

This is computationally much harder than the LP case. The block-angular structure can be exploited by decomposition methods (Benders decomposition, L-shaped method) — topics covered in the large-scale methods lecture.

### 7.1 Worked Example: Stochastic Facility Location

**Problem**: A company is deciding which of 3 potential warehouses to open (binary, first stage) to serve demand in 4 customer zones across 5 demand scenarios (continuous allocation, second stage). If demand cannot be met from open warehouses, there is a penalty of \$50/unit for unmet demand.

**Data:**

| Warehouse | Fixed Cost | Capacity |
|-----------|-----------|----------|
| W1 | \$10,000 | 500 units |
| W2 | \$8,000 | 400 units |
| W3 | \$12,000 | 600 units |

**Shipping costs** (\$/unit):

| | Zone 1 | Zone 2 | Zone 3 | Zone 4 |
|---|---|---|---|---|
| W1 | 5 | 8 | 12 | 15 |
| W2 | 10 | 4 | 7 | 11 |
| W3 | 14 | 11 | 3 | 6 |

**Demand scenarios:**

| | S1 (p=0.15) | S2 (p=0.25) | S3 (p=0.30) | S4 (p=0.20) | S5 (p=0.10) |
|---|---|---|---|---|---|
| Zone 1 | 200 | 250 | 300 | 350 | 400 |
| Zone 2 | 150 | 200 | 250 | 300 | 350 |
| Zone 3 | 180 | 220 | 280 | 320 | 380 |
| Zone 4 | 120 | 160 | 200 | 250 | 300 |

**Formulation:**

$$\min \; \sum_{w} f_w \, z_w + \sum_{s} p_s \left[ \sum_{w,c} t_{wc} \, y_{wcs} + 50 \sum_{c} u_{cs} \right]$$

subject to:

$$\sum_{w} y_{wcs} + u_{cs} \geq d_{cs} \quad \forall \, c, s \qquad \text{(demand satisfaction)}$$

$$\sum_{c} y_{wcs} \leq Q_w \, z_w \quad \forall \, w, s \qquad \text{(capacity only if open)}$$

$$z_w \in \{0, 1\}, \quad y_{wcs}, u_{cs} \geq 0$$

where $z_w$ is the binary opening decision (first stage), $y_{wcs}$ is the shipping allocation (second stage), and $u_{cs}$ is the unmet demand (second stage).

*Size*: 3 binary first-stage variables + $5 \times (12 + 4) = 80$ continuous second-stage variables = 83 variables. 3 first-stage constraints (implicit in binary) + $5 \times (4 + 3) = 35$ second-stage constraints = 35 constraints. This is a moderate MIP.

**Key insight**: Unlike the stochastic LPs in Section 3, the first-stage here involves discrete (open/close) decisions. The optimal choice of which warehouses to open depends on the *entire distribution* of demand scenarios, not just the expected demand. A warehouse that seems unnecessary for average demand might be critical for high-demand scenarios.

*(Full AMPL implementation is provided in the companion Colab notebook.)*

---

## 8. Exercises

**Exercise 1 (Two-Stage Formulation)**. A regional clinic must order flu vaccines in September (cost: \$12/dose) before knowing the severity of flu season. Unused vaccines expire worthless. If demand exceeds supply, emergency doses cost \$28 each. Revenue per administered dose is \$20. Scenarios: Mild (5,000 doses needed, prob. 0.4), Moderate (8,000 doses, prob. 0.4), Severe (12,000 doses, prob. 0.2). Formulate the two-stage stochastic LP. Identify the first-stage and second-stage decisions.

**Exercise 2 (Extensive Form and Solution)**. Write the deterministic equivalent of Exercise 1 as a single LP. Implement and solve in AMPL. Report the optimal order quantity and expected total cost.

**Exercise 3 (VSS and EVPI)**. For the flu vaccine problem: (a) Compute the EV solution and the EEV. (b) Compute the WS bound. (c) Calculate VSS and EVPI. Interpret both values in the context of the clinic's decision.

**Exercise 4 (Chance Constraints)**. A food bank must decide how much warehouse space to lease. Monthly donation volumes are uncertain across 10 scenarios (given in data). The food bank wants to ensure that donations can be stored without overflow in at least 90% of scenarios. Formulate this as a chance-constrained program. How does the solution change if the reliability target increases to 95%?

**Exercise 5 (Robust Optimization)**. Revisit the food bank warehouse problem from Exercise 4. Instead of using scenarios, suppose you only know that monthly donations lie within $\pm 20\%$ of their expected value. Formulate the robust counterpart using box uncertainty. Compare the leased space to the stochastic solution from Exercise 4. Which approach is more conservative, and why?

**Exercise 6 (Modeling Judgment)**. A manufacturing company is deciding whether to build a new plant (binary decision, \$5M cost) to serve demand that could be Low, Medium, or High over the next 5 years. If the plant is built, production is cheap (\$10/unit). If not built, they outsource at \$25/unit. (a) Is this a two-stage stochastic LP or a stochastic IP? Why? (b) Formulate the problem. (c) Discuss whether decomposition might help solve larger versions of this problem.

---

## References

- Rardin, R.L. *Optimization in Operations Research*, 2nd edition. Chapter 16 (stochastic programming overview).
- Birge, J.R. and Louveaux, F. *Introduction to Stochastic Programming*, 2nd edition. Springer, 2011.
- Ben-Tal, A., El Ghaoui, L., and Nemirovski, A. *Robust Optimization*. Princeton University Press, 2009.
- Bertsimas, D. and Sim, M. "The price of robustness." *Operations Research*, 52(1):35–53, 2004.
