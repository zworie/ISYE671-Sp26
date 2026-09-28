# Case Study 2: Integer Programming

## Distribution Network Design for a Regional Food Bank

### ISYE 671 — Linear Optimization and Network Flows

---

## Background

The Northern Illinois Community Food Bank (NICFB) serves 11 counties across northern Illinois. The organization currently operates out of a single aging warehouse in Rockford and distributes food to 85 partner agencies (pantries, shelters, soup kitchens, after-school programs). Over the past five years, demand for food assistance has grown 40%, and the existing facility is at capacity. NICFB has received a $12 million capital grant from a foundation, and the board has decided to redesign its distribution network by opening new warehouse/distribution centers and potentially closing or downsizing the existing one.

You have been hired as a consultant to determine the optimal network configuration: which facilities to open, what capacity to build, which agencies to serve from each facility, and what vehicle fleet to acquire — all while respecting budget constraints, service-level requirements, and the unique operational realities of food banking.

---

## Problem Data

### Candidate Facility Locations

NICFB has identified 7 candidate locations for warehouse/distribution centers. Each location can be built at one of three capacity tiers (Small, Medium, Large). The existing Rockford facility can be retained at its current size or closed.

| ID | Location | Small (sq ft / cost) | Medium (sq ft / cost) | Large (sq ft / cost) |
|:---:|----------|:---:|:---:|:---:|
| F1 | Rockford (existing) | 15,000 / $0 (retain) | — | — |
| F2 | DeKalb | 8,000 / $1.2M | 15,000 / $2.1M | 25,000 / $3.5M |
| F3 | Sterling | 8,000 / $1.0M | 15,000 / $1.8M | 25,000 / $3.0M |
| F4 | Oregon | 6,000 / $0.8M | 12,000 / $1.5M | — |
| F5 | Freeport | 8,000 / $1.1M | 15,000 / $1.9M | 25,000 / $3.2M |
| F6 | Belvidere | 6,000 / $0.7M | 12,000 / $1.4M | 20,000 / $2.5M |
| F7 | Sycamore | 6,000 / $0.8M | 12,000 / $1.5M | — |
| F8 | Mendota | 6,000 / $0.9M | 12,000 / $1.6M | — |

If the Rockford facility (F1) is closed, there is a one-time closure cost of $200,000 (lease termination, moving equipment). The existing facility has fixed annual operating costs of $180,000 regardless of utilization. If F1 is retained, it can additionally be renovated to Medium capacity (15,000 sq ft) for $1.5M or Large (25,000 sq ft) for $3.8M.

**Annual operating costs** per facility (includes utilities, insurance, basic staffing):

| Tier | Annual Operating Cost |
|:---:|:---:|
| Small | $120,000 |
| Medium | $200,000 |
| Large | $310,000 |

Each square foot of warehouse space can support approximately 25 pounds of food throughput per week.

### Partner Agencies

The 85 partner agencies are grouped into 18 demand zones based on geographic proximity. Each zone has the following attributes:

| Zone | Counties | Number of Agencies | Weekly Demand (lbs) | Max Acceptable Distance to Facility (miles) |
|:---:|----------|:---:|---:|:---:|
| Z1 | Winnebago (urban) | 12 | 42,000 | 20 |
| Z2 | Winnebago (rural) | 4 | 11,000 | 30 |
| Z3 | Boone | 5 | 14,500 | 25 |
| Z4 | McHenry (west) | 4 | 12,000 | 30 |
| Z5 | DeKalb (urban) | 8 | 28,000 | 20 |
| Z6 | DeKalb (rural) | 3 | 8,500 | 35 |
| Z7 | Lee (north) | 4 | 10,000 | 30 |
| Z8 | Lee (south) | 3 | 7,500 | 35 |
| Z9 | Ogle | 5 | 13,000 | 30 |
| Z10 | Whiteside | 5 | 15,500 | 25 |
| Z11 | Stephenson | 5 | 16,000 | 30 |
| Z12 | Jo Daviess | 3 | 6,500 | 40 |
| Z13 | Carroll | 3 | 5,500 | 35 |
| Z14 | LaSalle (north) | 4 | 11,500 | 30 |
| Z15 | LaSalle (south) | 3 | 8,000 | 40 |
| Z16 | Bureau | 4 | 9,000 | 35 |
| Z17 | Kendall | 5 | 18,000 | 25 |
| Z18 | Putnam | 2 | 3,500 | 40 |

Total weekly demand: approximately 240,000 lbs.

### Distance Matrix (miles, facility to zone centroid)

|  | Z1 | Z2 | Z3 | Z4 | Z5 | Z6 | Z7 | Z8 | Z9 | Z10 | Z11 | Z12 | Z13 | Z14 | Z15 | Z16 | Z17 | Z18 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 | 5 | 18 | 15 | 38 | 52 | 45 | 42 | 55 | 25 | 58 | 30 | 62 | 48 | 72 | 85 | 78 | 68 | 90 |
| F2 | 55 | 48 | 32 | 22 | 5 | 15 | 28 | 40 | 30 | 52 | 65 | 80 | 60 | 48 | 62 | 55 | 20 | 65 |
| F3 | 62 | 55 | 58 | 65 | 50 | 42 | 18 | 22 | 38 | 12 | 55 | 65 | 35 | 32 | 45 | 38 | 60 | 48 |
| F4 | 28 | 22 | 30 | 42 | 35 | 28 | 15 | 30 | 8 | 35 | 42 | 55 | 32 | 48 | 62 | 55 | 48 | 65 |
| F5 | 28 | 30 | 35 | 55 | 68 | 60 | 48 | 62 | 38 | 52 | 12 | 32 | 35 | 75 | 88 | 80 | 82 | 95 |
| F6 | 18 | 22 | 8 | 20 | 35 | 30 | 38 | 52 | 22 | 55 | 45 | 68 | 52 | 58 | 72 | 65 | 48 | 75 |
| F7 | 48 | 42 | 28 | 18 | 10 | 18 | 32 | 45 | 28 | 48 | 60 | 78 | 58 | 52 | 65 | 58 | 22 | 68 |
| F8 | 82 | 75 | 72 | 70 | 58 | 52 | 35 | 25 | 52 | 32 | 72 | 82 | 48 | 18 | 22 | 20 | 62 | 25 |

### Vehicle Fleet

NICFB must also decide what delivery vehicles to acquire. Vehicles are purchased (one-time capital cost from the $12M grant) and have annual operating costs:

| Vehicle Type | Capacity (lbs) | Purchase Cost | Annual Operating Cost | Max Deliveries/Week |
|---|:---:|:---:|:---:|:---:|
| Cargo Van | 3,000 | $45,000 | $18,000 | 12 |
| Box Truck (16 ft) | 6,000 | $65,000 | $25,000 | 10 |
| Refrigerated Truck (24 ft) | 10,000 | $110,000 | $38,000 | 8 |

**Fleet constraints:**
- Each facility must have at least 1 refrigerated truck (cold chain requirements).
- Total fleet size across all open facilities cannot exceed 25 vehicles (driver availability).
- Vehicles are assigned to (home-based at) specific facilities.
- Each delivery from a facility to a zone requires one round trip. A vehicle serving a zone within 20 miles can make the round trip and do another delivery the same day (counts as 1 delivery toward its weekly max). Beyond 20 miles, a delivery consumes an entire half-day (counts as 1.5 deliveries toward its weekly max).

### Budget and Planning Horizon

The $12 million capital grant must cover all facility construction/renovation, closure costs, and vehicle purchases. NICFB wants to **minimize total annual operating cost** (facility operating costs + vehicle operating costs + transportation cost) over the planning horizon.

**Transportation cost**: $2.50 per mile per delivery trip (round-trip distance = 2 × one-way distance from distance matrix).

The planning horizon for evaluating operating costs is 5 years. The objective should account for both one-time capital expenditures and the present value of 5 years of annual operating costs (use a discount rate of 4%).

### Service Requirements

1. **Coverage**: Every demand zone must be served by exactly one facility.
2. **Distance**: No zone may be assigned to a facility beyond its maximum acceptable distance.
3. **Capacity**: Total weekly demand assigned to a facility must not exceed its throughput capacity.
4. **Delivery feasibility**: Each facility must have sufficient vehicle capacity (total lbs per week across its fleet) to deliver all assigned demand, and sufficient delivery slots per week.
5. **Equity**: No single facility may serve more than 40% of total system demand (to avoid single-point-of-failure risk).
6. **Minimum facilities**: At least 2 facilities must be open (for redundancy).

---

## Your Assignment

### Part 1: Model Formulation

Formulate a mixed-integer programming model. Your formulation should clearly define:

1. **Sets and indices** for facilities, capacity tiers, zones, and vehicle types.
2. **Parameters** with clear notation matching the data above.
3. **Decision variables**: You will need binary variables for facility location and tier selection, integer variables for vehicle fleet composition, and continuous or integer variables for zone assignments and delivery logistics.
4. **Objective function**: Minimize total cost (capital + discounted annual operating costs). Write out the NPV calculation explicitly.
5. **Constraints**: All service requirements, budget constraints, capacity constraints, fleet constraints, and logical constraints (e.g., at most one tier per facility, can only assign zones to open facilities).
6. **Modeling choices**: Document any assumptions. In particular, address how you handle the fixed-charge nature of facility costs, the conditional renovation/closure logic for F1, and the delivery counting rule for distances beyond 20 miles.

### Part 2: Implementation and Solution

Implement your model in AMPL with Gurobi in a Google Colab notebook.

1. Solve the model and report: which facilities open at which tier, the zone-to-facility assignment map, the vehicle fleet at each facility, and the total cost breakdown (capital vs. annual operating vs. transportation).

2. Produce a clear summary table and, if possible, a simple visualization (e.g., a map or network diagram using matplotlib/networkx) showing the recommended network.

3. Report the MIP gap achieved and solve time. If the model does not solve to optimality within a reasonable time, discuss what tightening strategies you might employ (e.g., valid inequalities, symmetry breaking).

### Part 3: Analysis and Recommendations

1. **What-if analysis**: Test at least three of the following scenarios:
   - Demand grows 25% across all zones.
   - The capital budget is reduced to $9 million.
   - Maximum acceptable distances are reduced by 5 miles for all zones (stricter service level).
   - One candidate location (your choice) becomes unavailable.
   - The Rockford facility must be retained (political/community pressure).

2. **Robustness discussion**: How sensitive is the optimal network design to the demand forecasts? If demand shifts geographically (e.g., rural zones grow faster), would the recommended network still perform well? Discuss qualitatively.

3. **Board presentation**: Write a concise recommendation memo (1–2 pages) suitable for the NICFB board of directors. Include the recommended network design, total investment required, projected annual costs, key trade-offs considered, and risks. Use non-technical language appropriate for a board audience.

---

## Deliverables

- A written formulation document (PDF or markdown).
- A Google Colab notebook (`.ipynb`) with working AMPL/Gurobi code, results, scenario analysis, and the board memo.
