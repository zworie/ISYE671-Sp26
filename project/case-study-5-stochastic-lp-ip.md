# Case Study 5: Stochastic LP

## Agricultural Cooperative Crop Planning Under Weather and Market Uncertainty

### ISYE 671 — Linear Optimization and Network Flows

---

## Background

The Prairie Growers Cooperative (PGC) is an agricultural cooperative of 12 member farms in north-central Illinois with a combined 18,000 acres of cropland. Each spring, PGC must decide how many acres of each crop to plant across its member farms. These planting decisions must be made **before** the growing season, when two critical factors remain uncertain: (1) weather conditions (which affect crop yields) and (2) commodity market prices at harvest time.

PGC has historically relied on rules of thumb and individual farmer judgment. After a disastrous 2024 season in which over-commitment to a single crop led to significant losses, the cooperative's board has engaged you to develop a **two-stage stochastic linear programming model** that explicitly accounts for uncertainty in yields and prices, and determines a planting plan that maximizes expected profit.

---

## Problem Data

### Crops

PGC considers four crops for the upcoming season:

| Crop | Abbreviation | Planting Cost ($/acre) | Harvest Cost ($/acre) | Min Acreage | Max Acreage |
|---|:---:|:---:|:---:|:---:|:---:|
| Corn | CR | 420 | 65 | 4,000 | 10,000 |
| Soybeans | SB | 280 | 45 | 3,000 | 9,000 |
| Winter Wheat | WW | 210 | 45 | 1,000 | 5,000 |
| Cover Crop (conservation) | CC | 90 | 0 | 500 | 4,000 |

Total available acreage: 18,000 acres. All acreage must be planted (fallow land is not permitted under conservation compliance requirements).

Cover crops generate no harvest revenue. Instead, they provide a **soil health credit** of $45/acre regardless of weather (a government conservation payment).

**Crop rotation constraint**: To maintain soil health, no more than 55% of total acreage can be planted in corn (CR). Soybeans (SB) must occupy at least 20% of total acreage.

### Uncertainty: Scenarios

PGC's agronomist and market analyst have developed **6 scenarios** representing combinations of weather and market conditions:

**Weather conditions** (3 levels):

| Weather | Probability | Description |
|---|:---:|---|
| Favorable (W1) | 0.30 | Adequate rainfall, no extreme heat |
| Normal (W2) | 0.45 | Typical conditions, minor stress periods |
| Adverse (W3) | 0.25 | Drought or excessive rain, pest pressure |

**Market conditions** (2 levels):

| Market | Probability | Description |
|---|:---:|---|
| Strong (M1) | 0.40 | High commodity prices, strong export demand |
| Weak (M2) | 0.60 | Lower prices, adequate domestic supply |

Weather and market conditions are assumed **independent**, giving 6 scenarios:

| Scenario | Weather | Market | Probability |
|:---:|:---:|:---:|:---:|
| s1 | W1 (Favorable) | M1 (Strong) | 0.12 |
| s2 | W1 (Favorable) | M2 (Weak) | 0.18 |
| s3 | W2 (Normal) | M1 (Strong) | 0.18 |
| s4 | W2 (Normal) | M2 (Weak) | 0.27 |
| s5 | W3 (Adverse) | M1 (Strong) | 0.10 |
| s6 | W3 (Adverse) | M2 (Weak) | 0.15 |

**Yield by crop and weather** (bushels per acre):

| Crop | W1 (Favorable) | W2 (Normal) | W3 (Adverse) |
|---|:---:|:---:|:---:|
| CR | 210 | 180 | 120 |
| SB | 62 | 52 | 35 |
| WW | 78 | 65 | 50 |

**Market price by crop and market condition** ($/bushel):

| Crop | M1 (Strong) | M2 (Weak) |
|---|:---:|:---:|
| CR | 6.80 | 4.20 |
| SB | 15.50 | 10.20 |
| WW | 8.20 | 5.40 |

### Second-Stage (Recourse) Decisions

After the growing season, once weather and market conditions are known, PGC must decide how to sell its production. There are two selling options:

1. **Immediate sale**: Sell all production at the realized spot market price. Revenue = yield × acres × price.

2. **Contract sale at a discount**: Before the season, PGC can commit a portion of expected production (up to 50% of normal-weather expected production) to a **pre-season contract** at a guaranteed price equal to **85% of the average market price** (average of Strong and Weak). The contract volume is a first-stage decision. If actual production falls short of the contracted amount, PGC must purchase on the spot market at 115% of the realized price to fulfill the contract.

Any production beyond the contract volume is sold at the realized spot price.

### Additional Costs

- **Handling and transport**: $0.20/bushel for all crops sold (applies to both contract and spot sales).

---

## Your Assignment

### Part 1: Model Formulation

Formulate a **two-stage stochastic linear programming** model.

1. **Stage structure**: Clearly define:
   - **First-stage decisions** (before uncertainty is resolved): acreage allocation for each crop, contract sale volumes.
   - **Second-stage decisions** (after scenario realization): spot market sales, any shortfall purchases to fulfill contracts.

2. **Decision variables**: Define all variables with appropriate indices. First-stage variables have no scenario index; second-stage variables are indexed by scenario $s$.

3. **Objective function**: Maximize expected profit across all scenarios:
   $$\max \quad -(\text{first-stage costs}) + \sum_{s} p_s \cdot (\text{second-stage net revenue in scenario } s)$$
   Write out each cost and revenue component explicitly.

4. **Constraints**:
   - Acreage allocation: total = 18,000; individual crop bounds; rotation constraints
   - Contract limits: cannot contract more than 50% of normal-weather expected production
   - Production by scenario: $\text{production}_{c,s} = \text{yield}_{c,w(s)} \times \text{acres}_c$
   - Sales balance: contract delivery + spot sales = production + shortfall purchase (per crop, per scenario)
   - Shortfall definition: shortfall ≥ contract volume − production (per crop, per scenario)
   - Non-negativity

5. **Linearity**: Confirm that this formulation is a linear program (no binary or integer variables). How many variables and constraints does the model have?

6. **Assumptions**: Document all assumptions, particularly the independence of weather and market, and the contract mechanism.

### Part 2: Implementation and Solution

Implement the model in AMPL/Gurobi in a Google Colab notebook.

1. **Solve the stochastic model** and report:
   - Optimal first-stage decisions: acreage by crop, contract volumes.
   - Expected total profit.
   - Second-stage decisions for each of the 6 scenarios.

2. **Value of the Stochastic Solution (VSS)**:
   - Solve the **expected-value (EV) problem**: replace all random parameters (yields and prices) with their probability-weighted expectations. Record the EV first-stage decisions.
   - Compute the **EEV**: fix the first-stage variables to the EV solution and re-solve under the original 6 scenarios. Report the expected profit.
   - VSS = (Stochastic solution objective) − EEV. Interpret the result.

3. **Expected Value of Perfect Information (EVPI)**:
   - Compute the **wait-and-see (WS) solution**: solve a separate deterministic problem for each of the 6 scenarios (as if you knew the outcome in advance), then compute the probability-weighted average profit.
   - EVPI = WS − (Stochastic solution objective). Interpret: what is the maximum PGC should pay for a perfect forecast?

### Part 3: Scenario Analysis and Recommendations

1. **Profit distribution**: Compute the profit for each of the 6 scenarios under the optimal stochastic solution. Create a bar chart showing the profit distribution. What is the worst-case scenario profit?

2. **Weather sensitivity**: Re-solve the model with the adverse weather probability increased from 0.25 to 0.40 (reducing favorable to 0.15 and normal to 0.45). How does the optimal planting plan change? How much does expected profit decline?

3. **Contract strategy analysis**: Solve the model with no contracts allowed (all sales at spot price). Compare expected profit and profit variability to the baseline model. Is the contract mechanism valuable?

4. **Advisory memo**: Write a 1-page memo to the PGC board that includes:
   - The recommended planting plan and contract strategy.
   - Key risks and how the plan manages them.
   - The value of improved weather forecasting (EVPI) and whether it is worth investing in.
   - Recommendations in accessible language — board members are farmers, not optimization specialists.

---

## Deliverables

- A written formulation document (PDF or markdown) with the two-stage stochastic LP model.
- A Google Colab notebook (`.ipynb`) with AMPL/Gurobi implementation, VSS/EVPI calculations, scenario analysis, and the advisory memo.
