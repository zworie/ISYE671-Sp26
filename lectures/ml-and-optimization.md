# ISYE 671: Linear Optimization and Network Flows
# Lecture Notes — Machine Learning and Optimization

**Northern Illinois University — Spring 2026**
**Instructor: Dr. Ziteng Wang**

---

## 1. Introduction: Two Fields, Deeply Connected

Machine learning (ML) and mathematical optimization are not separate disciplines — they are deeply intertwined. At the core of virtually every ML method is an optimization problem: finding model parameters that minimize a loss function over training data.

This lecture explores the intersection from two complementary perspectives:

1. **Optimization as the engine of ML**: How LP, IP, and convex optimization formulations underlie classification, regression, clustering, and other ML tasks.
2. **ML-assisted optimization**: How ML techniques can improve the performance of optimization algorithms (solver tuning, warm starting, learning to cut/branch).

Our goal is not to cover ML comprehensively — that is a separate course — but to show that the optimization modeling skills you have developed in ISYE 671 are *directly applicable* to ML problems, and that the two fields increasingly inform each other.

> **Connection to prior material**: You will see LP duality reappear in support vector machines, integer programming in optimal classification trees, and network flow structure in clustering. The formulation and solver skills from earlier lectures carry over directly.

---

## 2. Regression as Optimization

### 2.1 Ordinary Least Squares (Review)

The most familiar ML/statistics model — linear regression — is an optimization problem:

$$\min_{\beta} \; \sum_{i=1}^{n} (y_i - x_i^\top \beta)^2$$

where $y_i$ are observed responses, $x_i \in \mathbb{R}^p$ are feature vectors, and $\beta \in \mathbb{R}^p$ are the model parameters. This is an unconstrained *convex quadratic program* with a closed-form solution $\beta^* = (X^\top X)^{-1} X^\top y$.

### 2.2 Regularized Regression

When there are many features (large $p$) or correlated predictors, regularization improves generalization. The two most common forms are both optimization problems:

**LASSO (L1 regularization):**

$$\min_{\beta} \; \sum_{i=1}^{n} (y_i - x_i^\top \beta)^2 + \lambda \sum_{j=1}^{p} |\beta_j|$$

The L1 penalty encourages **sparsity** — many coefficients are driven exactly to zero, performing automatic feature selection. This problem is a **quadratic program (QP)** that can be reformulated as an LP or solved with specialized solvers.

**LP reformulation of LASSO**: Introduce variables $\beta_j = \beta_j^+ - \beta_j^-$ with $\beta_j^+, \beta_j^- \geq 0$, and auxiliary variables for the absolute residuals. The LASSO can then be expressed as:

$$\min_{\beta^+, \beta^-, t} \; \sum_{i} t_i + \lambda \sum_j (\beta_j^+ + \beta_j^-)$$

subject to constraints linking $t_i$ to the squared residuals (or, using the L1 loss variant, as a pure LP).

**Ridge (L2 regularization):**

$$\min_{\beta} \; \sum_{i=1}^{n} (y_i - x_i^\top \beta)^2 + \lambda \sum_{j=1}^{p} \beta_j^2$$

This is an unconstrained convex QP with closed-form solution $\beta^* = (X^\top X + \lambda I)^{-1} X^\top y$.

### 2.3 Robust Regression

Ordinary least squares is sensitive to outliers. **Least absolute deviations (LAD)** regression minimizes the L1 norm of residuals:

$$\min_{\beta} \; \sum_{i=1}^{n} |y_i - x_i^\top \beta|$$

This is a **linear program**. Using the standard absolute-value linearization (introduce $t_i \geq 0$ with $t_i \geq y_i - x_i^\top \beta$ and $t_i \geq -(y_i - x_i^\top \beta)$):

$$\min_{\beta, t} \; \sum_{i} t_i$$

subject to:

$$t_i \geq y_i - x_i^\top \beta \quad \forall \, i$$

$$t_i \geq -(y_i - x_i^\top \beta) \quad \forall \, i$$

$$t_i \geq 0 \quad \forall \, i$$

This is a standard LP that can be solved directly with AMPL/Gurobi. The LAD estimator is more robust to outliers because it penalizes large residuals linearly rather than quadratically.

> **Modeling connection**: The absolute-value linearization technique is the same one we used for modeling deviations in goal programming and blending problems earlier in the course.

---

## 3. Classification as Optimization

### 3.1 Support Vector Machines (SVM)

The support vector machine is one of the clearest examples of ML-as-optimization. Given labeled training data $(x_i, y_i)$ where $y_i \in \{-1, +1\}$, the SVM finds a separating hyperplane $w^\top x + b = 0$ that maximizes the **margin** — the distance between the hyperplane and the nearest data points.

**Hard-margin SVM** (linearly separable case):

$$\min_{w, b} \; \frac{1}{2} \|w\|^2$$

subject to:

$$y_i (w^\top x_i + b) \geq 1 \quad \forall \, i = 1, \ldots, n$$

This is a convex **quadratic program (QP)**. The constraints ensure every point is on the correct side of the margin boundary.

**Soft-margin SVM** (allows misclassification):

$$\min_{w, b, \xi} \; \frac{1}{2} \|w\|^2 + C \sum_{i=1}^{n} \xi_i$$

subject to:

$$y_i (w^\top x_i + b) \geq 1 - \xi_i \quad \forall \, i$$

$$\xi_i \geq 0 \quad \forall \, i$$

Here, $\xi_i$ are **slack variables** (exactly as in our LP formulations!) measuring the degree of misclassification, and $C > 0$ is a penalty parameter controlling the trade-off between margin width and classification accuracy.

### 3.2 SVM Dual and LP Duality

The dual of the soft-margin SVM is:

$$\max_{\alpha} \; \sum_{i=1}^{n} \alpha_i - \frac{1}{2} \sum_{i,j} \alpha_i \alpha_j y_i y_j x_i^\top x_j$$

subject to:

$$\sum_{i=1}^{n} \alpha_i y_i = 0, \quad 0 \leq \alpha_i \leq C \quad \forall \, i$$

This is the same LP/QP duality we studied for linear programs, applied to a QP. The dual variables $\alpha_i$ (analogous to shadow prices) are nonzero only for the **support vectors** — the data points on or inside the margin boundary. This sparsity is analogous to how only binding constraints have nonzero duals in LP.

### 3.3 Linear SVM as an LP

If we replace the quadratic $\|w\|^2$ term with the L1 norm $\|w\|_1 = \sum_j |w_j|$ (which also promotes sparsity in the weight vector), the SVM becomes a **linear program**:

$$\min_{w^+, w^-, b, \xi} \; \sum_{j=1}^{p} (w_j^+ + w_j^-) + C \sum_{i=1}^{n} \xi_i$$

subject to:

$$y_i \left( \sum_j (w_j^+ - w_j^-) x_{ij} + b \right) \geq 1 - \xi_i \quad \forall \, i$$

$$w_j^+, w_j^- \geq 0 \; \forall \, j, \quad \xi_i \geq 0 \; \forall \, i$$

This can be solved with AMPL/Gurobi as a standard LP. The LP-SVM simultaneously classifies data and selects features (the features with $w_j^+ = w_j^- = 0$ are irrelevant).

---

## 4. Clustering as Optimization

### 4.1 K-Means as an Optimization Problem

K-means clustering assigns $n$ data points to $K$ clusters to minimize the total within-cluster sum of squared distances:

$$\min \; \sum_{k=1}^{K} \sum_{i \in C_k} \|x_i - \mu_k\|^2$$

where $C_k$ is the set of points assigned to cluster $k$ and $\mu_k$ is the centroid of cluster $k$. This is a combinatorial optimization problem (assigning points to clusters) and is NP-hard in general.

### 4.2 Clustering via Integer Programming

We can formulate clustering as an IP. Let:

- $z_{ik} = 1$ if point $i$ is assigned to cluster $k$
- $d_{ij}$ = distance between points $i$ and $j$

**Minimum-sum-of-distances clustering:**

$$\min \; \sum_{i=1}^{n} \sum_{j=1}^{n} \sum_{k=1}^{K} d_{ij} \, z_{ik} \, z_{jk}$$

This is a *quadratic* integer program. A linearizable alternative is the **K-medians** formulation, which selects $K$ points as cluster centers:

**K-Medians:**

$$\min \; \sum_{i=1}^{n} \sum_{j=1}^{n} d_{ij} \, x_{ij}$$

subject to:

$$\sum_{j=1}^{n} x_{ij} = 1 \quad \forall \, i \qquad \text{(each point assigned to one center)}$$

$$x_{ij} \leq y_j \quad \forall \, i, j \qquad \text{(can only assign to an open center)}$$

$$\sum_{j=1}^{n} y_j = K \qquad \text{(exactly $K$ centers)}$$

$$x_{ij} \in \{0, 1\}, \quad y_j \in \{0, 1\}$$

> **Modeling connection**: This is precisely the **facility location** formulation we studied in integer programming, with customers = data points, facilities = potential cluster centers, and the objective = total assignment distance. The same modeling techniques (and AMPL/Gurobi implementations) apply directly.

---

## 5. Decision Trees and Integer Programming

### 5.1 Optimal Classification Trees

Traditional decision tree algorithms (CART, C4.5) use greedy, top-down heuristics — they split one node at a time, choosing the locally best feature and threshold. These methods are fast but produce suboptimal trees.

**Optimal classification trees** use MIP to find the tree that minimizes misclassification over the entire training set simultaneously, rather than greedily.

### 5.2 MIP Formulation (Simplified)

For a binary classification tree of depth $D$ with $T = 2^D - 1$ internal (branch) nodes and $2^D$ leaf nodes:

**Decision variables:**

- $a_{jt} \in \{0, 1\}$: feature $j$ is used for splitting at branch node $t$
- $b_t \in [0, 1]$: threshold at branch node $t$
- $z_{it} \in \{0, 1\}$: data point $i$ is routed to leaf $t$
- $c_{kt}$: leaf $t$ predicts class $k$

**Objective**: Minimize total misclassification:

$$\min \; \sum_{i=1}^{n} \sum_{t \in \text{leaves}} z_{it} (1 - c_{y_i, t})$$

**Key constraints:**

- At each branch node, exactly one feature is selected: $\sum_j a_{jt} = 1$
- Data points are routed left or right based on the split: if the selected feature value is below the threshold, go left; otherwise, go right.
- Each data point reaches exactly one leaf: $\sum_{t \in \text{leaves}} z_{it} = 1$
- Each leaf predicts one class: $\sum_k c_{kt} = 1$

**Complexity control**: To prevent overfitting, add a regularization term penalizing tree complexity (number of active branch nodes):

$$+ \alpha \sum_{t \in \text{branches}} \sum_j a_{jt}$$

where $\alpha > 0$ is the complexity penalty.

> **Why this matters**: Optimal trees can significantly outperform greedy trees, especially when the dataset is small and every split matters. The MIP formulation uses the same binary variable modeling and big-M techniques from our IP lectures. The trade-off is computational cost — optimal trees for large datasets can be very expensive to solve.

### 5.3 Practical Considerations

- For depth $D = 3$ with $p = 10$ features and $n = 200$ data points, the MIP has roughly $200 \times 8 + 7 \times 10 + 7 + 8 \times 2 \approx 1,700$ binary variables. Gurobi can handle this in seconds.
- For depth $D = 5$ and $n = 10,000$, the problem becomes much larger. Heuristics (warm starts from CART), symmetry breaking, and cutting planes are essential.
- The library `interpretableai` and the method OCT (Bertsimas & Dunn, 2017) implement production-grade optimal trees.

---

## 6. ML-Assisted Optimization

So far, we have seen optimization *inside* ML. The reverse direction — using ML to *improve* optimization — is a rapidly growing research frontier.

### 6.1 Learning to Configure Solvers

Modern solvers like Gurobi have hundreds of parameters (branching strategies, cut selection, heuristic frequency). The best configuration depends on the problem instance. ML can learn mappings from **problem features** (size, density, constraint types) to **good parameter settings**:

- Extract features from the MIP (number of variables, constraint matrix density, objective coefficient distribution).
- Train a regression or classification model on historical solve times.
- Predict good parameters for new instances.

### 6.2 Learning to Branch

In branch-and-bound (which we studied in the IP solving lecture), the choice of which variable to branch on dramatically affects solve time. Traditional rules (most infeasible, strong branching) are handcrafted. ML-based branching:

- Collects data from many branch-and-bound runs (features of each candidate variable, which choice led to smaller trees).
- Trains a classifier or ranking model to predict the best branching variable.
- Applies the learned policy during future solves.

This approach, pioneered by Khalil et al. (2016) and Gasse et al. (2019), has shown significant speedups on structured MIP families.

### 6.3 Predicting Warm Starts

For families of similar optimization problems (e.g., daily production scheduling, weekly routing), ML can predict a good starting solution based on the current instance's features:

- Train a model on past (instance, optimal solution) pairs.
- For a new instance, predict an approximate solution.
- Feed this prediction as a warm start to the MIP solver.

This reduces the time to find a first feasible solution and can tighten the initial gap.

### 6.4 Learning Cuts and Valid Inequalities

Cutting planes are central to solving IPs (as we discussed in the IP solving lecture). ML can learn which cuts are most effective:

- For a family of problems, record which generated cuts were binding at optimality.
- Train a classifier to predict whether a candidate cut will be useful.
- Apply the filter during solve to reduce the number of cuts added, focusing on high-impact ones.

---

## 7. Predict-Then-Optimize: The Integration Frontier

### 7.1 The Classical Pipeline

In many decision-making systems, ML and optimization are used sequentially:

1. **Predict**: Use ML to forecast uncertain parameters (demand, travel times, prices).
2. **Optimize**: Feed the predictions into an optimization model to make decisions.

**Example**: A delivery company uses ML to predict next-day demand at each warehouse, then solves a VRP to plan routes.

The problem: the ML model is trained to minimize *prediction error* (e.g., mean squared error), not *decision quality*. A prediction that is slightly wrong in a way that doesn't affect the optimal decision is fine, while a prediction that is accurate on average but wrong at a critical threshold can lead to poor decisions.

### 7.2 Decision-Focused Learning

**Decision-focused learning** (also called *smart predict-then-optimize* or *SPO*) trains the ML model to minimize the downstream optimization cost directly:

$$\min_{\theta} \; \sum_{i=1}^{n} \ell\left( z^*(\hat{c}_\theta(x_i)), \; z^*(c_i) \right)$$

where $\hat{c}_\theta(x_i)$ is the ML model's prediction of the cost vector given features $x_i$, $z^*(c)$ is the optimal solution of the optimization problem with cost $c$, and $\ell$ measures the decision quality gap (regret).

**Challenge**: The optimal solution $z^*(c)$ is a piecewise-constant function of $c$ (it changes only at breakpoints where the optimal basis changes), so differentiating through the optimization is non-trivial. Recent methods address this via:

- **Surrogate loss functions** (SPO+ loss, Elmachtoub & Grigas, 2022)
- **Differentiable optimization layers** (using KKT conditions or perturbation)
- **Blackbox differentiation** (sampling-based gradient estimates)

### 7.3 Practical Implications

For practitioners (including industrial and systems engineers), the predict-then-optimize paradigm suggests:

- When building forecasting models for optimization inputs, evaluate them by *decision quality*, not just prediction accuracy.
- Small improvements in forecast accuracy may not translate to better decisions — focus on the parameters that most affect the optimal solution.
- Joint training of prediction and optimization is an active area; for now, using the SPO+ loss is a practical starting point.

---

## 8. Summary: Optimization ↔ ML Connections

| ML Task | Optimization Formulation | Type | ISYE 671 Connection |
|---------|------------------------|------|---------------------|
| Linear regression (LAD) | $\min \sum |y_i - x_i^\top \beta|$ | LP | Absolute value linearization |
| LASSO | $\min \|y - X\beta\|^2 + \lambda \|\beta\|_1$ | QP / LP reformulation | Feature selection via sparsity |
| SVM (L1) | $\min \|w\|_1 + C \sum \xi_i$ | LP | Slack variables, duality |
| SVM (L2) | $\min \|w\|^2 + C \sum \xi_i$ | QP | LP duality generalization |
| K-Medians clustering | Facility location IP | IP | Facility location model |
| Optimal decision tree | MIP with binary routing | MIP | Binary variables, big-M |
| Predict-then-optimize | Nested ML + LP/IP | Bilevel | Sensitivity analysis, duality |

---

## 9. Exercises

**Exercise 1 (LAD Regression)**. The following data gives patient recovery time ($y$, days) vs. drug dosage ($x_1$, mg) and patient age ($x_2$, years):

| Patient | $x_1$ | $x_2$ | $y$ |
|---------|--------|--------|------|
| 1 | 10 | 30 | 15 |
| 2 | 20 | 45 | 22 |
| 3 | 15 | 55 | 28 |
| 4 | 25 | 35 | 18 |
| 5 | 30 | 60 | 32 |
| 6 | 5  | 40 | 20 |
| 7 | 35 | 25 | 12 |
| 8 | 40 | 50 | 25 |

Formulate the LAD regression as an LP. Implement and solve in AMPL. Compare the LAD coefficients to the OLS coefficients (which you may compute in Python using `numpy.linalg.lstsq`).

**Exercise 2 (LP-SVM)**. Using the patient data from Exercise 1, create a binary classification label: $y_i = +1$ if recovery time $\leq 20$ days, $y_i = -1$ otherwise. Formulate and solve the L1-norm SVM as an LP in AMPL with $C = 10$. Report the separating hyperplane and identify the support vectors. Visualize the decision boundary.

**Exercise 3 (Clustering as Facility Location)**. A health department wants to place $K = 3$ mobile vaccination clinics to serve 15 communities. Community locations (coordinates) and populations are given. Formulate the problem as a K-medians IP (weighted by population). Solve in AMPL. How does the solution change if $K = 4$?

**Exercise 4 (Optimal Decision Tree)**. For the patient data from Exercise 1 (with the binary label from Exercise 2), formulate a depth-2 optimal classification tree as a MIP. You may restrict splits to axis-aligned (single feature) thresholds. How many binary variables does your formulation have? Solve in AMPL and compare the classification accuracy to a greedy tree (which you may build using `sklearn.tree.DecisionTreeClassifier` in Python).

**Exercise 5 (Conceptual — ML-Assisted Optimization)**. Consider a hospital that solves a nurse scheduling IP every week. The problem structure is similar each week but patient demand varies. Describe how you would use ML to: (a) predict a good warm-start solution for each week's IP, (b) decide which cuts to add during branch-and-bound, and (c) evaluate the quality of the demand forecast by decision quality rather than prediction accuracy. For each, describe the training data, features, and ML model you would use.

---

## References

- Rardin, R.L. *Optimization in Operations Research*, 2nd edition.
- Bertsimas, D. and Dunn, J. "Optimal classification trees." *Machine Learning*, 106(7):1039–1082, 2017.
- Elmachtoub, A.N. and Grigas, P. "Smart 'predict, then optimize'." *Management Science*, 68(1):9–26, 2022.
- Khalil, E.B. et al. "Learning to branch in mixed integer programming." *AAAI*, 2016.
- Gasse, M. et al. "Exact combinatorial optimization with graph convolutional neural networks." *NeurIPS*, 2019.
- Boyd, S. and Vandenberghe, L. *Convex Optimization*. Cambridge University Press, 2004.
