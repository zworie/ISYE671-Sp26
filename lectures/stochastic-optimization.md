# ISYE 671: Linear Optimization and Network Flows
# Lecture Notes — Stochastic Optimization

**Northern Illinois University — Spring 2026**
**Instructor: Dr. Ziteng Wang**

---

## 1. Introduction: Why Uncertainty Matters

Every optimization model we have studied so far in this course — LP, IP, network flows — assumes that all data (costs, capacities, demands, travel times) are **known with certainty**. In practice, this assumption is rarely true:

- Demand for products is uncertain when production decisions must be made.
- Travel times fluctuate due to weather and traffic.
- Supply quantities from vendors may be unreliable.
- Patient arrivals at an emergency department are stochastic.

**Stochastic optimization** extends the LP/IP framework to incorporate uncertainty explicitly. Rather than optimizing for a single scenario, we optimize over a *distribution* of possible scenarios, balancing the quality of decisions against the risk of bad outcomes.

> **Connection to prior material**: The LP and IP models from earlier lectures become the *building blocks* of stochastic programs. If you can formulate a deterministic LP, you can extend it to a stochastic LP by replicating the model across scenarios and linking the copies through shared first-stage decisions.

This lecture covers three major paradigms:

1. **Two-stage stochastic programming** — the workhorse of stochastic optimization.
2. **Chance-constrained programming** — controlling the probability of constraint violation.
3. **Robust optimization** — protecting against worst-case uncertainty.

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

### 3.2 The Deterministic Equivalent (Extensive Form)

For a finite number of scenarios, the two-stage stochastic LP can be reformulated as a single large LP called the **deterministic equivalent** or **extensive form**:

$$\min \; c^\top x + \sum_{s=1}^{S} p_s \, q_s^\top y_s$$

subject to:

$$Ax = b$$

$$T_s x + W y_s = h_s \quad \forall \, s = 1, \ldots, S$$

$$x \geq 0, \quad y_s \geq 0 \quad \forall \, s$$

This is a *standard LP* — it can be solved directly with any LP solver, including AMPL/Gurobi. The structure is block-angular: the first-stage variables $x$ link all scenarios, while the second-stage variables $y_s$ are scenario-specific.

$$\begin{bmatrix} A & & & \\ T_1 & W & & \\ T_2 & & W & \\ \vdots & & & \ddots \\ T_S & & & & W \end{bmatrix} \begin{bmatrix} x \\ y_1 \\ y_2 \\ \vdots \\ y_S \end{bmatrix} = \begin{bmatrix} b \\ h_1 \\ h_2 \\ \vdots \\ h_S \end{bmatrix}$$

> **Key insight**: The extensive form grows linearly with the number of scenarios. With 3 scenarios, the model is roughly 3× the size of the deterministic version. With 1,000 scenarios, the model can become very large — motivating the decomposition methods covered in Lecture 3 (large-scale methods).

### 3.3 Worked Example: Brewery Grain Purchase

**Problem**: Prairie Wind Brewing must purchase grain *now* (first stage) for next month's production. Grain costs \$50/unit. Each unit of grain yields 500 barrels of beer, which sells for \$25/barrel. If demand exceeds production capacity, the brewery can buy emergency grain at \$80/unit. Unsold beer is wasted (no salvage).

**Scenarios** (from Section 2.1):

| Scenario $s$ | Demand $d_s$ (barrels) | Probability $p_s$ |
|---|---|---|
| 1 (Low) | 4,000 | 0.3 |
| 2 (Medium) | 6,000 | 0.5 |
| 3 (High) | 9,000 | 0.2 |

**First-stage decision**: $x$ = units of grain purchased now.

**Second-stage decisions** (per scenario $s$):
- $y_s^{\text{prod}}$ = barrels produced and sold
- $y_s^{\text{emerg}}$ = units of emergency grain purchased
- $y_s^{\text{waste}}$ = barrels of beer produced but unsold

**Formulation:**

$$\min \; 50x + \sum_{s=1}^{3} p_s \left[ 80 \, y_s^{\text{emerg}} - 25 \, y_s^{\text{prod}} \right]$$

subject to:

$$y_s^{\text{prod}} \leq d_s \quad \forall \, s \qquad \text{(cannot sell more than demand)}$$

$$y_s^{\text{prod}} \leq 500(x + y_s^{\text{emerg}}) \quad \forall \, s \qquad \text{(production limited by total grain)}$$

$$y_s^{\text{waste}} = 500(x + y_s^{\text{emerg}}) - y_s^{\text{prod}} \quad \forall \, s \qquad \text{(waste = excess production)}$$

$$x \geq 0, \quad y_s^{\text{prod}}, y_s^{\text{emerg}}, y_s^{\text{waste}} \geq 0 \quad \forall \, s$$

This is a single LP with $1 + 3 \times 3 = 10$ variables and can be solved directly in AMPL.

*(Full AMPL implementation is provided in the companion Colab notebook.)*

### 3.4 Value of the Stochastic Solution (VSS)

How much do we gain by modeling uncertainty explicitly? The **value of the stochastic solution** quantifies this.

**Definitions:**

1. **Expected Value (EV) solution**: Replace all random parameters with their expected values, solve the resulting deterministic model, and obtain decision $x^{EV}$.
2. **Expected result of the EV solution (EEV)**: Evaluate $x^{EV}$ across all scenarios: $EEV = c^\top x^{EV} + \sum_s p_s \, Q(x^{EV}, \omega_s)$.
3. **Recourse Problem (RP) solution**: Solve the full stochastic program to get optimal $x^{RP}$ with objective $RP$.

Then:

$$VSS = EEV - RP$$

The VSS measures the expected cost savings from using the stochastic model instead of the naive expected-value approach. A large VSS indicates that uncertainty significantly impacts the optimal decision, justifying the added modeling complexity.

### 3.5 Wait-and-See (WS) and Expected Value of Perfect Information (EVPI)

If we could know the future perfectly, we would solve each scenario independently:

$$WS = \sum_{s=1}^{S} p_s \, z_s^*$$

where $z_s^*$ is the optimal objective for scenario $s$ alone (choosing both $x$ and $y_s$ optimally).

The **expected value of perfect information** is:

$$EVPI = RP - WS$$

The EVPI represents the maximum amount we should pay for a perfect forecast. It provides an upper bound on the value of any information-gathering activity (market research, better sensors, etc.).

**Summary of key quantities:**

$$WS \leq RP \leq EEV$$

$$EVPI = RP - WS \geq 0, \qquad VSS = EEV - RP \geq 0$$

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

### 4.4 Comparison of Approaches

| Feature | Two-Stage Recourse | Chance Constraints |
|---------|-------------------|-------------------|
| Philosophy | Optimize expected cost of corrective actions | Ensure feasibility with high probability |
| Decision structure | First and second stage | Single stage |
| Model type | LP (extensive form) | MIP (binary indicators) |
| Output | Decisions + recourse plan per scenario | Decisions + reliability guarantee |
| When to use | When corrective actions exist and have known costs | When hard feasibility is required |

---

## 5. Robust Optimization

### 5.1 Motivation

Stochastic programming requires probability distributions for uncertain parameters. When these distributions are unknown or unreliable, **robust optimization** provides an alternative: optimize against the *worst case* within an **uncertainty set**.

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

### 5.4 Comparison: Stochastic vs. Robust

| Feature | Stochastic Programming | Robust Optimization |
|---------|----------------------|-------------------|
| Uncertainty model | Probability distribution (scenarios) | Uncertainty set (no probabilities) |
| Objective | Minimize expected cost | Minimize worst-case cost |
| Conservatism | Moderate (averages over scenarios) | Higher (protects against worst case) |
| Data requirement | Scenario probabilities | Uncertainty set bounds |
| Model size | Grows with number of scenarios | Grows with size of uncertainty set |
| Tractability | LP (extensive form) | LP, SOCP, or MIP depending on set |

> **Practical guidance**: Use stochastic programming when reliable probability data is available (historical demand records, simulation). Use robust optimization when you know the range of uncertainty but not its distribution (new product launch, novel supply chain disruption).

---

## 6. Stochastic Integer Programming (Brief Overview)

When first-stage decisions are integer (e.g., facility location under uncertain demand), the problem becomes a **stochastic integer program**. The extensive form is a large MIP:

$$\min \; c^\top x + \sum_{s=1}^{S} p_s \, q_s^\top y_s$$

subject to:

$$Ax = b, \quad T_s x + W y_s = h_s \; \forall \, s, \quad x \in \mathbb{Z}^{n_1}, \; y_s \geq 0$$

This is computationally much harder than the LP case. The block-angular structure can be exploited by decomposition methods (Benders decomposition, L-shaped method) — topics we will discuss in the next lecture on large-scale methods.

**Example**: Deciding where to build warehouses (integer, first stage) to serve stochastic regional demands (continuous, second stage) is a stochastic facility location problem. We studied the deterministic version earlier; the stochastic extension replicates the demand-serving constraints across scenarios.

---

## 7. Modeling Stochastic Programs in AMPL

Stochastic programs with discrete scenarios can be modeled directly in AMPL by indexing over scenarios. The key pattern is:

```
set SCENARIOS;
param prob{SCENARIOS};

# First-stage variables (not indexed by scenario)
var x >= 0;

# Second-stage variables (indexed by scenario)
var y{SCENARIOS} >= 0;

# Objective: first-stage cost + expected second-stage cost
minimize total_cost:
    c * x + sum{s in SCENARIOS} prob[s] * q[s] * y[s];

# First-stage constraints
subject to first_stage_constraint: ...;

# Second-stage constraints (one per scenario)
subject to second_stage{s in SCENARIOS}: ... ;
```

This is the **explicit extensive form** approach. For modest numbers of scenarios (up to hundreds), this works well with Gurobi through AMPL. For thousands of scenarios, decomposition methods or specialized stochastic programming solvers (such as PySP or SMPS-format solvers) are needed.

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
