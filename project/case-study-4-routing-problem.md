# Case Study 4: Routing Problem

## Delivery Route Optimization for a Regional Grocery E-Commerce Service

### ISYE 671 — Linear Optimization and Network Flows

---

## Background

FreshCart Midwest is a regional online grocery delivery service operating in the greater Champaign-Urbana metropolitan area. The company operates a single fulfillment center (depot) and delivers grocery orders to residential customers using a fleet of delivery vans. Business has grown rapidly, and the operations team needs a systematic approach to daily route planning.

You have been brought in as an operations research consultant to develop and solve a vehicle routing model that minimizes total delivery cost while respecting vehicle capacity and customer time windows. The problem is a **Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)**.

---

## Problem Data

### Depot

The FreshCart fulfillment center (node 0) is located at coordinates (40.0, 40.0) on a grid representing the delivery area (each grid unit ≈ 0.5 miles). The depot opens at 6:00 AM and all vehicles must return by 4:00 PM (a 10-hour operating window, i.e., 600 minutes from 6:00 AM).

### Customers

On the day being planned, there are **15 customers** with confirmed delivery orders. Each customer has a delivery location, an order size (in standard tote equivalents), a delivery time window, and a service time.

| Cust. | X | Y | Demand (totes) | Window Open | Window Close | Service (min) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 22 | 58 | 5 | 8:00 | 11:00 | 10 |
| 2 | 35 | 72 | 7 | 8:00 | 12:00 | 12 |
| 3 | 50 | 65 | 4 | 9:00 | 13:00 | 8 |
| 4 | 62 | 50 | 6 | 8:00 | 11:30 | 10 |
| 5 | 18 | 45 | 8 | 9:00 | 13:00 | 15 |
| 6 | 55 | 38 | 5 | 9:00 | 12:00 | 10 |
| 7 | 28 | 30 | 7 | 10:00 | 14:00 | 14 |
| 8 | 45 | 22 | 4 | 8:00 | 12:00 | 8 |
| 9 | 70 | 42 | 6 | 9:00 | 13:00 | 10 |
| 10 | 15 | 65 | 5 | 9:00 | 12:30 | 10 |
| 11 | 38 | 48 | 4 | 12:00 | 15:00 | 10 |
| 12 | 60 | 28 | 8 | 8:00 | 11:00 | 15 |
| 13 | 25 | 18 | 3 | 11:00 | 15:00 | 8 |
| 14 | 48 | 55 | 6 | 10:00 | 13:30 | 10 |
| 15 | 33 | 35 | 7 | 8:00 | 11:00 | 12 |

Total demand: 85 totes.

### Vehicle Fleet

FreshCart operates a **homogeneous fleet** of 5 identical delivery vans:

| Parameter | Value |
|---|:---:|
| Number of vans | 5 |
| Capacity per van | 25 totes |
| Fixed cost per trip | $65 |
| Variable cost | $1.00 per mile |
| Maximum route duration | 540 minutes (9 hours) |

Not all vehicles must be used. A vehicle incurs its fixed cost only if dispatched.

### Travel Times and Distances

Travel between any two locations uses Euclidean distance (in grid units). Convert to miles by multiplying by 0.5 (each grid unit = 0.5 miles). Travel speed is 25 mph in urban/residential areas, so travel time in minutes between locations $i$ and $j$ is:

$$t_{ij} = \frac{d_{ij} \times 0.5}{25} \times 60 = 1.2 \times d_{ij} \text{ minutes}$$

where $d_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}$ is the Euclidean distance in grid units.

---

## Your Assignment

### Part 1: Model Formulation

Formulate a mixed-integer programming model for this CVRPTW.

1. **Decision variables**: Define binary routing variables $x_{ijk}$ (whether vehicle $k$ travels directly from node $i$ to node $j$), continuous time variables $w_{ik}$ (arrival time of vehicle $k$ at node $i$), and any auxiliary variables needed.

2. **Objective function**: Minimize total delivery cost = fixed vehicle costs + variable travel costs.

3. **Constraints**: Formulate all of the following:
   - Each customer is visited exactly once by exactly one vehicle.
   - Route continuity (flow conservation at each customer node for each vehicle).
   - Vehicle capacity constraints.
   - Time window constraints with arrival time tracking.
   - Depot departure and return constraints.
   - Subtour elimination (choose and justify your approach: MTZ or flow-based).
   - Maximum route duration.

4. **Variable and constraint counts**: Count the number of binary variables and constraints in your formulation. Is this problem tractable for an exact MIP solver?

5. **Assumptions**: Document any simplifying assumptions (e.g., symmetric travel times, no traffic variability).

### Part 2: Implementation and Solution

Implement the model in AMPL/Gurobi in a Google Colab notebook.

1. **Solve the model**: Solve the MIP formulation. Set a time limit (e.g., 10 minutes) and report the best solution found, the MIP gap, and solve time.

2. **Solution visualization**: Create a plot (using matplotlib) showing all customer locations, the depot, and each vehicle's route as a differently colored path.

3. **Route summary table**: For each vehicle used, report the ordered sequence of customers visited, total distance, total totes delivered, departure/arrival times, and route cost.

### Part 3: Operational Analysis

1. **Fleet utilization**: How many vehicles are used in the optimal solution? What is the average vehicle utilization (totes delivered / capacity)?

2. **Time window analysis**: Identify which customers have the tightest time windows. For the 3 tightest-window customers, solve the model with their windows widened by 1 hour and report any cost savings.

3. **Capacity sensitivity**: If FreshCart upgraded to larger vans (30-tote capacity) at a higher fixed cost of $80/trip, would it reduce total cost? Solve the modified model and compare.

4. **Operations memo**: Write a 1-page operational brief for FreshCart's VP of Logistics summarizing the recommended daily routing plan, fleet utilization findings, and your recommendation on van capacity upgrades.

---

## Deliverables

- A written formulation document (PDF or markdown) with the CVRPTW model.
- A Google Colab notebook (`.ipynb`) with AMPL/Gurobi implementation, visualizations, analysis, and the operations memo.
