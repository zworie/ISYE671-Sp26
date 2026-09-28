# AMPL Quick Reference Guide

**Graduate Optimization Course** | Northern Illinois University

---

## Table of Contents

1. [Core Syntax](#1-core-syntax)
2. [Data File Patterns](#2-data-file-patterns)
3. [Mathematical Notation to AMPL Translation](#3-mathematical-notation-to-ampl-translation)
4. [Common Modeling Patterns](#4-common-modeling-patterns)
5. [Python Integration with amplpy](#5-python-integration-with-amplpy)
6. [Debugging Guide](#6-debugging-guide)
7. [Quick Reference Tables](#7-quick-reference-tables)

---

## 1. Core Syntax

### 1.1 Sets

Sets define the indices used throughout your model.

```ampl
# Basic set (members defined in .dat file)
set PRODUCTS;

# Ordered set (enables prev, next, first, last)
set MONTHS ordered;

# Set with inline members
set DAYS := {Mon, Tue, Wed, Thu, Fri};

# Set of pairs (arcs in a network)
set ARCS within {NODES, NODES};

# Derived set with condition
set ACTIVE := {j in PRODUCTS: demand[j] > 0};

# Cross product
set ROUTES := ORIGINS cross DESTINATIONS;
```

**Key Functions for Sets:**

- `card(S)` - Number of elements in set S
- `ord(i)` - Position of element i in ordered set (1-based)
- `first(S)` - First element of ordered set S
- `last(S)` - Last element of ordered set S
- `prev(i)` - Previous element before i in ordered set
- `next(i)` - Next element after i in ordered set
- `member(k,S)` - The k-th element of ordered set S

### 1.2 Parameters

Parameters are known constants (input data).

```ampl
# Scalar parameter
param budget;

# Indexed parameter
param demand {PRODUCTS};

# Two-dimensional parameter
param cost {ORIGINS, DESTINATIONS};

# Parameter with default value
param min_order {PRODUCTS} default 0;

# Parameter with inline definition
param num_products := card(PRODUCTS);
param total_demand := sum {j in PRODUCTS} demand[j];

# Parameter with bounds check
param capacity {MACHINES} > 0;
```

### 1.3 Decision Variables

Variables are what the solver determines.

```ampl
# Non-negative continuous variable
var Produce {PRODUCTS} >= 0;

# Variable with upper bound
var Ship {ORIGINS, DESTINATIONS} >= 0, <= capacity;

# Variable with parameter bounds
var Make {j in PRODUCTS} >= min_prod[j], <= max_prod[j];

# Integer variable
var Assign {WORKERS, TASKS} >= 0 integer;

# Binary variable
var Select {PROJECTS} binary;

# Free variable (can be negative)
var Deviation {GOALS};
```

### 1.4 Objective Function

Every model has exactly one objective.

```ampl
# Maximization
maximize Total_Profit:
    sum {j in PRODUCTS} profit[j] * Produce[j];

# Minimization
minimize Total_Cost:
    sum {i in ORIGINS, j in DESTINATIONS} cost[i,j] * Ship[i,j];

# Multi-term objective
minimize Total:
    production_cost + inventory_cost + shortage_penalty;
```

### 1.5 Constraints

Use `subject to` (or `s.t.`) to define constraints.

```ampl
# Single constraint
subject to Budget_Limit:
    sum {j in PRODUCTS} cost[j] * Produce[j] <= budget;

# Family of constraints (one per index)
subject to Capacity {i in MACHINES}:
    sum {j in PRODUCTS} time[i,j] * Produce[j] <= available[i];

# Equality constraint
subject to Balance:
    sum {i in ORIGINS} Supply[i] = sum {j in DESTINATIONS} Demand[j];

# Constraint with conditional indexing
subject to Min_Production {j in PRODUCTS: required[j] = 1}:
    Produce[j] >= min_qty[j];

# Range constraint
subject to Quality:
    0.10 <= sum {i in INGREDIENTS} protein[i] * Use[i] / total <= 0.20;
```

### 1.6 Ordered Set Functions

For time-based or sequential models:

```ampl
set PERIODS ordered;

subject to Init_Balance:
    Inventory[first(PERIODS)] = init_inv + Produce[first(PERIODS)] - demand[first(PERIODS)];

subject to Balance {t in PERIODS: ord(t) > 1}:
    Inventory[t] = Inventory[prev(t)] + Produce[t] - demand[t];

subject to Final_Inventory:
    Inventory[last(PERIODS)] >= safety_stock;
```

---

## 2. Data File Patterns

### 2.1 Set Definitions

```ampl
# Simple set
set PRODUCTS := Chairs Tables Desks;

# Set on multiple lines
set MONTHS := 
    Jan Feb Mar Apr May Jun
    Jul Aug Sep Oct Nov Dec;

# Set of pairs
set ARCS := (A,B) (A,C) (B,C) (B,D) (C,D);
```

### 2.2 Scalar Parameters

```ampl
param budget := 50000;
param tax_rate := 0.08;
param planning_horizon := 12;
```

### 2.3 One-Dimensional Parameters

```ampl
# List format
param demand :=
    Chairs   100
    Tables   50
    Desks    75;

# Alternative: single line
param supply := Seattle 400  Denver 300  Chicago 500;
```

### 2.4 Two-Dimensional Parameters

**Table Format (preferred for dense data):**

```ampl
param cost:         Chicago  Denver  Seattle :=
    Portland        2.5      1.8     1.2
    Sacramento      2.8      2.0     1.5
    LosAngeles      2.2      1.9     2.1;
```

**List Format (preferred for sparse data):**

```ampl
param distance :=
    [Portland, Chicago]     2000
    [Portland, Denver]      1200
    [Portland, Seattle]     175
    [Sacramento, Chicago]   1850
    [Sacramento, Denver]    1100;
```

**Transposed Table:**

```ampl
param revenue (tr):   Q1    Q2    Q3    Q4 :=
    ProductA          100   120   115   130
    ProductB          200   180   195   210;
```

### 2.5 Multiple Parameters in One Table

```ampl
# Define multiple parameters sharing the same indices
param:          demand    price    min_order :=
    Chairs      100       45       10
    Tables      50        120      5
    Desks       75        200      5;
```

### 2.6 Sets and Parameters Together

```ampl
# Define set members and parameter values together
param: PRODUCTS: profit  cost :=
    Chairs         25      15
    Tables         60      40
    Desks          50      35;
```

---

## 3. Mathematical Notation to AMPL Translation

### 3.1 Summations

| Mathematical Notation | AMPL Code |
|:----------------------|:----------|
| Sum of c_j * x_j over all j in J | `sum {j in J} c[j] * x[j]` |
| Sum from i=1 to n of a_i | `sum {i in 1..n} a[i]` |
| Conditional sum (only where d_j > 0) | `sum {j in J: d[j] > 0} x[j]` |
| Double sum over i in I and j in J | `sum {i in I, j in J} c[i,j] * x[i,j]` |
| Sum over arc pairs | `sum {(i,j) in ARCS} x[i,j]` |

### 3.2 Constraints

| Mathematical Form | AMPL Code |
|:------------------|:----------|
| Sum of a_ij * x_j <= b_i for all i | `subject to Con {i in I}: sum {j in J} a[i,j]*x[j] <= b[i];` |
| x_j >= 0 for all j | `var x {J} >= 0;` |
| Sum of x_j = 1 | `subject to Total: sum {j in J} x[j] = 1;` |
| l_j <= x_j <= u_j | `var x {j in J} >= l[j], <= u[j];` |
| x_j is binary (0 or 1) | `var x {J} binary;` |
| x_j is non-negative integer | `var x {J} >= 0 integer;` |

### 3.3 Common Formulation Patterns

**Resource Constraint:**

```ampl
# Math: sum_{j in J} a_ij * x_j <= b_i for all i in I
subject to Resource {i in RESOURCES}:
    sum {j in PRODUCTS} usage[i,j] * Produce[j] <= available[i];
```

**Demand Satisfaction:**

```ampl
# Math: sum_{i in I} x_ij >= d_j for all j in J
subject to Demand {j in CUSTOMERS}:
    sum {i in SUPPLIERS} Ship[i,j] >= demand[j];
```

**Flow Balance:**

```ampl
# Math: sum_{j:(i,j) in A} x_ij - sum_{j:(j,i) in A} x_ji = b_i for all i
subject to Balance {i in NODES}:
    sum {(i,j) in ARCS} Flow[i,j] - sum {(j,i) in ARCS} Flow[j,i] = supply[i];
```

**Inventory Balance:**

```ampl
# Math: I_t = I_{t-1} + P_t - D_t for all t > 1
subject to Inv_Balance {t in PERIODS: ord(t) > 1}:
    Inventory[t] = Inventory[prev(t)] + Production[t] - demand[t];
```

**Big-M Constraint (Linking):**

```ampl
# Math: x_j <= M * y_j (if y=0, then x must be 0)
subject to Linking {j in FACILITIES}:
    Production[j] <= big_M * Open[j];
```

---

## 4. Common Modeling Patterns

### 4.1 Resource Allocation

```ampl
set PRODUCTS;
set RESOURCES;
param profit {PRODUCTS};
param usage {RESOURCES, PRODUCTS};
param available {RESOURCES};

var Produce {PRODUCTS} >= 0;

maximize Total_Profit:
    sum {j in PRODUCTS} profit[j] * Produce[j];

subject to Capacity {i in RESOURCES}:
    sum {j in PRODUCTS} usage[i,j] * Produce[j] <= available[i];
```

### 4.2 Blending / Mixing

```ampl
set INGREDIENTS;
set QUALITIES;
param cost {INGREDIENTS};
param composition {QUALITIES, INGREDIENTS};
param min_quality {QUALITIES};
param max_quality {QUALITIES};
param total_amount;

var Use {INGREDIENTS} >= 0;

minimize Total_Cost:
    sum {i in INGREDIENTS} cost[i] * Use[i];

subject to Total:
    sum {i in INGREDIENTS} Use[i] = total_amount;

subject to Min_Qual {q in QUALITIES}:
    sum {i in INGREDIENTS} composition[q,i] * Use[i] >= min_quality[q] * total_amount;

subject to Max_Qual {q in QUALITIES}:
    sum {i in INGREDIENTS} composition[q,i] * Use[i] <= max_quality[q] * total_amount;
```

### 4.3 Transportation

```ampl
set ORIGINS;
set DESTINATIONS;
param supply {ORIGINS};
param demand {DESTINATIONS};
param cost {ORIGINS, DESTINATIONS};

var Ship {ORIGINS, DESTINATIONS} >= 0;

minimize Total_Cost:
    sum {i in ORIGINS, j in DESTINATIONS} cost[i,j] * Ship[i,j];

subject to Supply {i in ORIGINS}:
    sum {j in DESTINATIONS} Ship[i,j] <= supply[i];

subject to Demand {j in DESTINATIONS}:
    sum {i in ORIGINS} Ship[i,j] >= demand[j];
```

### 4.4 Assignment

```ampl
set WORKERS;
set TASKS;
param cost {WORKERS, TASKS};

var Assign {WORKERS, TASKS} binary;

minimize Total_Cost:
    sum {w in WORKERS, t in TASKS} cost[w,t] * Assign[w,t];

subject to One_Task_Per_Worker {w in WORKERS}:
    sum {t in TASKS} Assign[w,t] = 1;

subject to One_Worker_Per_Task {t in TASKS}:
    sum {w in WORKERS} Assign[w,t] = 1;
```

### 4.5 Multi-Period Production Planning

```ampl
set PERIODS ordered;
param demand {PERIODS};
param prod_cost {PERIODS};
param hold_cost {PERIODS};
param max_production {PERIODS};
param init_inventory;

var Produce {t in PERIODS} >= 0, <= max_production[t];
var Inventory {PERIODS} >= 0;

minimize Total_Cost:
    sum {t in PERIODS} (prod_cost[t] * Produce[t] + hold_cost[t] * Inventory[t]);

subject to Init_Balance:
    Inventory[first(PERIODS)] = init_inventory + Produce[first(PERIODS)] - demand[first(PERIODS)];

subject to Balance {t in PERIODS: ord(t) > 1}:
    Inventory[t] = Inventory[prev(t)] + Produce[t] - demand[t];
```

### 4.6 Facility Location

```ampl
set FACILITIES;
set CUSTOMERS;
param fixed_cost {FACILITIES};
param variable_cost {FACILITIES, CUSTOMERS};
param demand {CUSTOMERS};
param capacity {FACILITIES};

var Open {FACILITIES} binary;
var Serve {FACILITIES, CUSTOMERS} >= 0;

minimize Total_Cost:
    sum {i in FACILITIES} fixed_cost[i] * Open[i] +
    sum {i in FACILITIES, j in CUSTOMERS} variable_cost[i,j] * Serve[i,j];

subject to Meet_Demand {j in CUSTOMERS}:
    sum {i in FACILITIES} Serve[i,j] >= demand[j];

subject to Facility_Capacity {i in FACILITIES}:
    sum {j in CUSTOMERS} Serve[i,j] <= capacity[i] * Open[i];
```

---

## 5. Python Integration with amplpy

### 5.1 Setup in Google Colab

```python
# Install
!pip install -q amplpy

from amplpy import AMPL, ampl_notebook

# Initialize with license and solvers
ampl_notebook(
    modules=["highs"],  # Add "gurobi", "cplex" if available
    license_uuid="your-license-uuid"
)
```

### 5.2 Basic Workflow

```python
# Create model instance
model = AMPL()

# Load model and data files
model.read('mymodel.mod')
model.read_data('mydata.dat')

# Set solver and solve
model.option['solver'] = 'highs'
model.solve()

# Check status
status = model.get_value('solve_result')
print(f"Status: {status}")
```

### 5.3 Accessing Results

```python
# Objective value
obj_value = model.obj['Total_Cost'].value()

# Variable values
x = model.var['Produce']
for j in model.set['PRODUCTS'].members():
    print(f"{j}: {x[j].value()}")

# Get as pandas DataFrame
df = model.var['Ship'].get_values().to_pandas()

# Constraint dual values (shadow prices)
shadow = model.con['Capacity']['Labor'].dual()

# Constraint body (LHS value)
used = model.con['Capacity']['Labor'].body()
```

### 5.4 Injecting Data from Python

```python
# Set members
model.set['PRODUCTS'] = ['A', 'B', 'C']

# Scalar parameter
model.param['budget'] = 50000

# Indexed parameter (dict)
model.param['demand'] = {'A': 100, 'B': 150, 'C': 200}

# Two-dimensional parameter
costs = {
    ('Plant1', 'Customer1'): 10,
    ('Plant1', 'Customer2'): 15,
    ('Plant2', 'Customer1'): 12,
    ('Plant2', 'Customer2'): 8,
}
model.param['cost'] = costs
```

### 5.5 Modifying and Re-solving

```python
# Change a parameter value
model.param['budget'] = 60000

# Re-solve (no need to reload model)
model.solve()

# Reset to clear everything
model.reset()
```

### 5.6 Sensitivity Analysis Loop

```python
results = []
for budget in [40000, 50000, 60000, 70000]:
    scenario = AMPL()
    scenario.read('model.mod')
    scenario.read_data('data.dat')
    scenario.param['budget'] = budget
    scenario.option['solver'] = 'highs'
    scenario.solve()
    
    results.append({
        'budget': budget,
        'profit': scenario.obj['Profit'].value(),
        'status': scenario.get_value('solve_result')
    })

df_results = pd.DataFrame(results)
```

---

## 6. Debugging Guide

### 6.1 Common Syntax Errors

| Error Message | Likely Cause | Fix |
|:--------------|:-------------|:----|
| `syntax error` | Missing semicolon | Add `;` at end of statement |
| `X is not defined` | Using before declaring | Move declaration before use |
| `X is already defined` | Duplicate declaration | Remove duplicate |
| `invalid subscript` | Wrong indices | Check set membership |
| `no value for X` | Missing data | Add to .dat file |

### 6.2 Model Errors

**Infeasible Problem:**
- Check for conflicting constraints (e.g., demand > supply)
- Verify data values are correct
- Look for typos in constraint definitions
- Add slack variables to identify which constraints conflict

**Unbounded Problem:**
- Missing constraints (e.g., no capacity limit)
- Variable bounds missing
- Objective coefficient sign error

### 6.3 Data File Errors

| Error | Cause | Fix |
|:------|:------|:----|
| `unexpected end of file` | Missing semicolon | Add `;` after data block |
| `X is not a member` | Typo in set member | Match exact spelling |
| `too few values` | Missing data rows | Complete the table |
| `too many values` | Extra data | Remove duplicates |

### 6.4 Debugging Commands

```ampl
# Display model structure
display PRODUCTS;
display demand;
display Produce;

# Show expanded constraints
expand Capacity;
expand Capacity['Labor'];

# Show current variable values
display {j in PRODUCTS} Produce[j];

# Check constraint values
display {i in RESOURCES} Capacity[i].body, Capacity[i].slack;
```

### 6.5 Python Debugging

```python
# Check if data loaded correctly
print(list(model.set['PRODUCTS'].members()))
print(model.param['demand']['A'])

# Examine solve output
model.option['solver_msg'] = 1  # Enable solver messages
model.solve()

# Get solve status details
print(model.get_value('solve_result'))
print(model.get_value('solve_message'))
```

---

## 7. Quick Reference Tables

### 7.1 Arithmetic Operators

| Operator | Description | Example |
|:---------|:------------|:--------|
| `+` | Addition | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `^` | Exponentiation | `a ^ 2` |
| `mod` | Modulo | `a mod b` |
| `div` | Integer division | `a div b` |

### 7.2 Built-in Functions

| Function | Description |
|:---------|:------------|
| `abs(x)` | Absolute value |
| `max(a,b)` | Maximum of two values |
| `min(a,b)` | Minimum of two values |
| `round(x)` | Round to nearest integer |
| `floor(x)` | Round down |
| `ceil(x)` | Round up |
| `sqrt(x)` | Square root |
| `exp(x)` | Exponential |
| `log(x)` | Natural logarithm |
| `log10(x)` | Base-10 logarithm |

### 7.3 Comparison Operators

| Operator | Description |
|:---------|:------------|
| `=` | Equal |
| `<>` or `!=` | Not equal |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |

### 7.4 Logical Operators

| Operator | Description |
|:---------|:------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

### 7.5 Set Operations

| Operation | Syntax | Description |
|:----------|:-------|:------------|
| Union | `A union B` | All elements in A or B |
| Intersection | `A inter B` | Elements in both A and B |
| Difference | `A diff B` | Elements in A but not B |
| Symmetric diff | `A symdiff B` | Elements in exactly one |
| Cross product | `A cross B` | All pairs (a,b) |
| Membership | `i in A` | True if i is in A |
| Subset | `A within B` | A is subset of B |

### 7.6 Solver Status Codes

| Status | Meaning | Action |
|:-------|:--------|:-------|
| `solved` | Optimal solution found | Extract results |
| `infeasible` | No feasible solution | Check constraints |
| `unbounded` | Objective unbounded | Add constraints |
| `limit` | Hit iteration/time limit | Increase limits |
| `failure` | Solver error | Check model/data |

### 7.7 Common Solver Options

```python
# Solver selection
model.option['solver'] = 'highs'

# Time limit (seconds)
model.option['highs_options'] = 'timelimit=300'

# Optimality tolerance
model.option['highs_options'] = 'mip_rel_gap=0.01'

# Display level
model.option['solver_msg'] = 1
```

---

## Additional Resources

- **AMPL Book (Free PDF)**: https://ampl.com/wp-content/uploads/BOOK.pdf
- **AMPL Documentation**: https://dev.ampl.com
- **amplpy Python API**: https://amplpy.ampl.com
- **Free Academic License**: https://ampl.com/ce or https://ampl.com/courses
- **Support Forum**: https://discuss.ampl.com

---

*Last updated: February 2026*
