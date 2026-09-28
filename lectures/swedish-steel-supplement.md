# ISYE 671: Linear Optimization and Network Flows — Supplemental Note

## Revised Exercise 2.4: Swedish Steel — Standard vs. Premium Product Selection

**Instructor:** Dr. Ziteng Wang | **Date:** February 9, 2026

---

## Motivation: Why the Original Exercise Needs Revision

In the Swedish Steel fixed-charge model (Section 2.3 of the lecture notes), the standard product requires nickel content between 30 and 35 kg (3.0%--3.5% of the 1000 kg charge). If we naively add a "premium" option requiring at least 50 kg of nickel ($\geq$ 5%), we face a contradiction: the standard upper bound ($N \leq 35$) and the premium lower bound ($N \geq 50$) cannot hold simultaneously. A simple bonus variable cannot resolve this --- we need to model a genuine **either-or product selection** using disjunctive constraints.

This revised exercise illustrates a powerful and broadly applicable IP technique: using Big-M constraints to activate one of several mutually exclusive specification sets.

---

## Revised Problem Statement

Swedish Steel can produce one of two product grades from the same furnace charge:

- **Standard grade:** Nickel content between 30 and 35 kg (as in the original model). Sells at the base price.
- **Premium grade:** Nickel content at least 50 kg. Earns a bonus of 2,000 kroner but incurs a testing/certification fee of 500 kroner.

All other chemical specifications (carbon, chromium, molybdenum) remain identical for both grades. The fixed-charge setup structure for ingredients 1--4 also remains unchanged.

**Task:** Modify the fixed-charge Swedish Steel model to allow the company to choose which grade to produce, and determine the optimal decision.

---

## Solution

### Step 1: Define New Decision Variables

We introduce two new binary variables, consistent with the notation in the Exercise Solutions document:

$$z = \begin{cases} 1 & \text{if the company opts into the premium contract} \\ 0 & \text{otherwise} \end{cases}$$

$$w = \begin{cases} 1 & \text{if the premium nickel specification is active (i.e., premium is both chosen and met)} \\ 0 & \text{otherwise} \end{cases}$$

The variable $z$ represents the **business decision** to pursue the premium contract. The variable $w$ represents the **technical outcome** that the premium specification is actually enforced. We require $w \leq z$: the premium specification can only be active if the company has opted in.

**Why two variables?** The testing fee of 500 kroner is paid whenever the company opts in ($z = 1$), regardless of whether the nickel target is achieved. The bonus of 2,000 kroner is earned only when the premium specification is met ($w = 1$). Separating the opt-in decision from the specification enforcement allows the objective to capture these distinct cost/benefit components.

### Step 2: Replace the Nickel Constraints with Disjunctive Constraints

Let $N$ denote the nickel content of the charge:

$$N = 0.180x_1 + 0.032x_2 + x_5$$

The original model has two nickel constraints: $N \geq 30$ and $N \leq 35$. We must replace these with constraints that enforce *either* the standard specification $[30, 35]$ (when $w = 0$) or the premium specification $N \geq 50$ with no upper bound (when $w = 1$).

Let $M$ be a sufficiently large constant. Since $N$ cannot exceed the total charge weight, $M = 1000$ is valid (though tighter values are preferable in practice --- see Discussion Point 1 below).

**Standard nickel lower bound (active when $w = 0$, relaxed when $w = 1$):**

$$N \geq 30 - Mw$$

**Standard nickel upper bound (active when $w = 0$, relaxed when $w = 1$):**

$$N \leq 35 + Mw$$

**Premium nickel lower bound (active when $w = 1$, relaxed when $w = 0$):**

$$N \geq 50 - M(1 - w)$$

Note that the premium grade has **no upper bound** on nickel content, so there is no fourth constraint. This is an asymmetric disjunction: one side has two bounds, the other has one.

**Verification that these work correctly:**

| $w$ | Std lower | Std upper | Prem lower |
|:---:|:---------:|:---------:|:----------:|
| 0 (standard) | $N \geq 30$ (binds) | $N \leq 35$ (binds) | $N \geq 50 - M$ (trivial) |
| 1 (premium) | $N \geq 30 - M$ (trivial) | $N \leq 35 + M$ (trivial) | $N \geq 50$ (binds) |

These four constraints **replace** the original two nickel constraints. All other constraints in the model (weight, carbon, chromium, molybdenum, switching, setup) remain unchanged.

### Step 3: Link $w$ and $z$

The premium specification can only be active if the company has opted in:

$$w \leq z$$

This constraint ensures that if $z = 0$ (no opt-in), then $w = 0$ (standard specification is enforced).

### Step 4: Modify the Objective Function

The objective captures two separate financial effects:

- **Testing fee:** 500 kroner, paid whenever $z = 1$ (opt-in), regardless of outcome.
- **Premium bonus:** 2,000 kroner, earned whenever $w = 1$ (premium spec met and opted in).

$$\min \quad \underbrace{16x_1 + 10x_2 + 8x_3 + 9x_4 + 48x_5 + 60x_6 + 53x_7}_{\text{variable ingredient costs}} + \underbrace{350(y_1 + y_2 + y_3 + y_4)}_{\text{setup costs}} + \underbrace{500z}_{\text{testing fee}} - \underbrace{2000w}_{\text{premium bonus}}$$

**Key modeling insight:** Since we are minimizing and $w$ carries a negative coefficient ($-2000$), the optimizer *wants* to set $w = 1$ whenever possible. This means:

- We do not need constraints that *force* $w = 1$ when premium conditions are met --- the optimizer does it automatically.
- We only need constraints that *prevent* $w = 1$ when conditions are not met: the four disjunctive nickel constraints and the linking constraint $w \leq z$.

Conversely, $z$ carries a positive coefficient ($+500$), so the optimizer prefers $z = 0$. It will set $z = 1$ only when the benefit from $w = 1$ (bonus of 2,000) outweighs the testing fee (500) plus any additional ingredient cost.

### Step 5: Complete Revised Model

$$\min \quad \sum_{j=1}^{7} c_j x_j + \sum_{j=1}^{4} 350 y_j + 500z - 2000w$$

subject to:

$$\sum_{j=1}^{7} x_j = 1000 \quad \text{(weight)}$$

$$6.5 \leq 0.0080x_1 + 0.0070x_2 + 0.0085x_3 + 0.0040x_4 \leq 7.5 \quad \text{(carbon, unchanged)}$$

$$N \geq 30 - Mw \quad \text{(standard nickel lower)}$$

$$N \leq 35 + Mw \quad \text{(standard nickel upper)}$$

$$N \geq 50 - M(1 - w) \quad \text{(premium nickel lower)}$$

where $N = 0.180x_1 + 0.032x_2 + x_5$

$$10 \leq 0.120x_1 + 0.011x_2 + x_6 \leq 12 \quad \text{(chromium, unchanged)}$$

$$11 \leq 0.001x_2 + x_7 \leq 13 \quad \text{(molybdenum, unchanged)}$$

$$x_j \leq u_j y_j \quad \text{for } j = 1, \ldots, 4 \quad \text{(switching/setup)}$$

$$w \leq z \quad \text{(premium spec requires opt-in)}$$

$$x_j \geq 0, \quad y_j \in \{0,1\} \; (j = 1,\ldots,4), \quad z \in \{0,1\}, \quad w \in \{0,1\}$$

---

## Discussion Points for Class

### 1. Tightening Big-M Values

The value of $M$ must be large enough to fully relax the inactive constraints. Here $M = 1000$ works because the nickel content is bounded by the total charge weight. However:

- **Too small** an $M$ may cut off feasible solutions.
- **Too large** an $M$ weakens the LP relaxation, making the problem harder for branch-and-bound.
- **Best practice:** Use the tightest valid $M$. For the standard lower bound $N \geq 30 - Mw$, we need $30 - M \leq 0$ when $w = 1$, so $M \geq 30$ suffices. For the standard upper bound $N \leq 35 + Mw$, we need the right-hand side to exceed the maximum feasible $N$ when $w = 1$; since the premium spec pushes $N \geq 50$, a value of $M$ such that $35 + M$ exceeds the maximum possible nickel content is needed --- $M \geq 1000 - 35 = 965$ in the worst case, though tighter analysis using ingredient availabilities can reduce this. Students can derive the tightest valid $M$ for each of the three constraints as a follow-up exercise.

### 2. The Relationship between $z$ and $w$

In this model, the optimal solution will always have $z = w$ (either both 0 or both 1). Why? If $z = 1$ and $w = 0$, the company pays the testing fee but earns no bonus and still must meet the standard spec --- strictly worse than $z = 0, w = 0$. The optimizer will never choose this.

So why keep both variables? Because the problem *statement* distinguishes the business decision (opt-in) from the technical outcome (spec met). In a more complex variant --- for example, if the testing fee were paid upfront and the bonus depended on a stochastic yield --- $z$ and $w$ could take different values. The two-variable formulation is the more general and extensible approach.

### 3. Generalization: Multiple Product Grades

If the company could choose among $K$ grades (e.g., standard, premium, ultra-premium), we would introduce $w_k \in \{0,1\}$ for $k = 1, \ldots, K$ with:

$$\sum_{k=1}^{K} w_k = 1 \quad \text{(exactly one grade produced)}$$

Each element's bounds would be controlled by the corresponding $w_k$ via Big-M. This pattern arises frequently in process engineering and product design optimization.

### 4. Connection to Other Lecture Topics

This exercise ties together three techniques from the lecture:

- **Fixed-charge variables and switching constraints** (Section 2.3) --- the setup costs for ingredients.
- **Mutual exclusivity** (Section 3.3, NASA) --- exactly one product grade must be chosen.
- **Big-M disjunctive constraints** (Section 7.2, scheduling) --- the either-or specification logic.

Students should recognize that the Big-M disjunction used here for product specifications is structurally identical to the Big-M disjunction used in scheduling for conflict constraints. The underlying principle is the same: use a binary variable and a large constant to activate exactly one of two constraint sets.
