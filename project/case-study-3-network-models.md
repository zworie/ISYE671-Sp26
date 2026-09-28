# Case Study 3: Network Models

## Municipal Water Distribution System Optimization

### ISYE 671 — Linear Optimization and Network Flows

---

## Background

The city of Riverton (a fictional mid-sized midwestern city, population 185,000) is upgrading its municipal water distribution system. The city's water utility draws from three source types — a river intake plant, a reservoir, and a set of deep wells — and distributes treated water through a network of pumping stations, storage tanks, and transmission mains to residential, commercial, and industrial customers distributed across the city.

The utility's Chief Engineer has asked you to develop a minimum-cost flow model to determine the optimal daily water routing plan. The network must satisfy all customer demands, respect pipeline capacities and pressure constraints, and minimize the combined cost of water sourcing, treatment, and pumping. A secondary concern is system resilience: the city council wants to understand what happens if a key pipeline segment is taken offline for maintenance.

---

## Network Description

The water distribution network consists of **24 nodes** and **43 arcs**. Nodes represent sources, treatment plants, pumping stations, storage tanks, and demand zones. Arcs represent pipeline segments with associated capacities and costs.

### Node Data

**Source Nodes** (supply):

| Node | Type | Max Daily Supply (million gallons/day, MGD) | Source Cost ($/1000 gal) |
|:---:|---|:---:|:---:|
| S1 | River Intake | 28.0 | 0.35 |
| S2 | Reservoir | 18.0 | 0.20 |
| S3 | Well Field A | 8.0 | 0.55 |
| S4 | Well Field B | 6.0 | 0.60 |

Total source capacity: 60 MGD.

**Treatment Plant Nodes** (transshipment with processing cost):

| Node | Type | Max Throughput (MGD) | Treatment Cost ($/1000 gal) |
|:---:|---|:---:|:---:|
| T1 | Main Treatment Plant | 30.0 | 0.80 |
| T2 | Secondary Treatment Plant | 20.0 | 0.95 |
| T3 | Well Water Treatment (chlorination) | 12.0 | 0.40 |

**Pumping Station Nodes** (transshipment with pumping cost):

| Node | Type | Max Throughput (MGD) | Pumping Cost ($/1000 gal) |
|:---:|---|:---:|:---:|
| P1 | High-Lift Station (downtown) | 20.0 | 0.15 |
| P2 | Booster Station (east) | 18.0 | 0.18 |
| P3 | Booster Station (west) | 10.0 | 0.20 |
| P4 | Booster Station (south) | 8.0 | 0.22 |
| P5 | Hilltop Station (elevated zones) | 6.0 | 0.30 |

**Storage Tank Nodes** (transshipment with no cost, but bounded inventory):

| Node | Type | Max Storage (MG) | Min Storage (MG) |
|:---:|---|:---:|:---:|
| K1 | Central Reservoir Tank | 5.0 | 1.5 |
| K2 | East Elevated Tank | 2.0 | 0.5 |
| K3 | West Ground Tank | 3.0 | 0.8 |
| K4 | South Elevated Tank | 1.5 | 0.4 |

Storage tanks begin and end the day at their minimum level (steady-state assumption for daily planning). They can receive and discharge water during the day; the net daily flow must be zero.

**Demand Nodes** (demand):

| Node | Zone Description | Daily Demand (MGD) | Priority |
|:---:|---|:---:|:---:|
| D1 | Downtown commercial district | 5.2 | Critical |
| D2 | University campus | 3.8 | Critical |
| D3 | East residential | 6.5 | Standard |
| D4 | West residential | 5.0 | Standard |
| D5 | South residential | 4.2 | Standard |
| D6 | North residential | 3.5 | Standard |
| D7 | Industrial park (east) | 7.8 | Critical |
| D8 | Hospital / medical campus | 2.0 | Emergency |
| D9 | Commercial corridor (west) | 3.5 | Standard |
| D10 | New development (south) | 2.0 | Standard |
| D11 | Airport and surrounding area | 1.5 | Critical |

Total daily demand: 45.0 MGD.

**Priority classifications** will be used in the resilience analysis (Part 3).

### Arc Data

Each arc has a capacity (max flow in MGD), a per-unit flow cost ($/1000 gallons, representing pumping energy and pipeline maintenance), and a minimum flow (to maintain water quality — stagnant water in pipes is a health concern).

| Arc | From | To | Capacity (MGD) | Min Flow (MGD) | Cost ($/1000 gal) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| A1 | S1 | T1 | 28.0 | 2.0 | 0.05 |
| A2 | S1 | T2 | 20.0 | 1.0 | 0.08 |
| A3 | S2 | T1 | 15.0 | 1.0 | 0.06 |
| A4 | S2 | T2 | 10.0 | 0.5 | 0.07 |
| A5 | S3 | T3 | 8.0 | 0.5 | 0.04 |
| A6 | S4 | T3 | 6.0 | 0.3 | 0.04 |
| A7 | T1 | P1 | 22.0 | 1.0 | 0.10 |
| A8 | T1 | P2 | 12.0 | 0.5 | 0.12 |
| A9 | T1 | P3 | 10.0 | 0.5 | 0.11 |
| A10 | T2 | P2 | 10.0 | 0.5 | 0.10 |
| A11 | T2 | P4 | 8.0 | 0.3 | 0.13 |
| A11b | T2 | P1 | 18.0 | 0.0 | 0.14 |
| A12 | T3 | P2 | 6.0 | 0.2 | 0.09 |
| A13 | T3 | P4 | 5.0 | 0.2 | 0.10 |
| A14 | P1 | K1 | 15.0 | 0.0 | 0.03 |
| A15 | P1 | D1 | 8.0 | 0.5 | 0.04 |
| A16 | P1 | D2 | 6.0 | 0.3 | 0.05 |
| A17 | P1 | P5 | 5.0 | 0.0 | 0.08 |
| A18 | P2 | K2 | 8.0 | 0.0 | 0.04 |
| A19 | P2 | D3 | 10.0 | 0.5 | 0.05 |
| A20 | P2 | D7 | 12.0 | 0.5 | 0.06 |
| A21 | P3 | K3 | 6.0 | 0.0 | 0.04 |
| A22 | P3 | D4 | 8.0 | 0.3 | 0.05 |
| A23 | P3 | D9 | 5.0 | 0.2 | 0.06 |
| A24 | P4 | K4 | 4.0 | 0.0 | 0.04 |
| A25 | P4 | D5 | 6.0 | 0.3 | 0.05 |
| A26 | P4 | D10 | 4.0 | 0.0 | 0.06 |
| A27 | P5 | D6 | 4.0 | 0.2 | 0.07 |
| A28 | P5 | D11 | 3.0 | 0.0 | 0.08 |
| A29 | K1 | D1 | 5.0 | 0.0 | 0.02 |
| A30 | K1 | D2 | 4.0 | 0.0 | 0.03 |
| A31 | K1 | P5 | 3.0 | 0.0 | 0.06 |
| A32 | K2 | D3 | 5.0 | 0.0 | 0.02 |
| A33 | K2 | D7 | 10.0 | 0.0 | 0.03 |
| A34 | K3 | D4 | 4.0 | 0.0 | 0.02 |
| A35 | K3 | D9 | 3.0 | 0.0 | 0.03 |
| A36 | K4 | D5 | 3.0 | 0.0 | 0.02 |
| A37 | K4 | D10 | 2.0 | 0.0 | 0.03 |
| A38 | P1 | D8 | 3.0 | 0.5 | 0.04 |
| A39 | K1 | D8 | 2.0 | 0.0 | 0.03 |
| A40 | P2 | D11 | 3.0 | 0.0 | 0.09 |
| A41 | P3 | D6 | 3.0 | 0.0 | 0.07 |
| A42 | K2 | P5 | 2.0 | 0.0 | 0.05 |

### Cost Summary

The total cost of delivering water has three components:
1. **Source cost**: incurred at each source node based on volume drawn.
2. **Treatment cost**: incurred at each treatment plant based on volume processed.
3. **Pumping/pipeline cost**: incurred on each arc based on flow volume.

All costs are in $/1000 gallons.

---

## Your Assignment

### Part 1: Model Formulation

Formulate this as a **minimum-cost network flow** (MCNF) problem.

1. **Network representation**: Formally define the graph $G = (N, A)$. Classify each node as a supply node, demand node, or transshipment node. Specify the supply/demand value $b_i$ for each node.

2. **Handling node costs**: The standard MCNF has costs only on arcs. Describe how you transform node costs (source costs, treatment costs, pumping station costs) into arc costs so the problem fits the MCNF framework. Show the transformation explicitly.

3. **Storage tank modeling**: Explain how the storage tanks fit into the network flow model given the steady-state (net-zero daily flow) assumption. What role do they play in routing flexibility?

4. **Complete formulation**: Write the full MCNF formulation with objective function and all constraints (flow balance, capacity bounds, minimum flow requirements).

5. **Problem structure**: Verify that this problem has the structure required for an MCNF — is the constraint matrix totally unimodular? Will the LP relaxation yield integer solutions? Discuss briefly.

### Part 2: Implementation and Solution

Implement and solve the model in a Google Colab notebook using AMPL/Gurobi. Also implement and visualize the network using NetworkX.

1. **AMPL model**: Implement the MCNF model. Report the optimal total daily cost and the optimal flow on every arc.

2. **Flow decomposition**: Identify the major flow paths from sources to demand zones. Present the dominant paths (e.g., "S1 → T1 → P1 → D1 carries 4.8 MGD").

3. **Network visualization**: Create a NetworkX diagram of the network. Use node colors to distinguish node types (sources, treatment, pumping, storage, demand). Use edge widths proportional to optimal flow. Label key flows.

4. **Source utilization**: What fraction of each source's capacity is used? Which sources are most and least cost-effective?

### Part 3: Resilience Analysis

The city council is concerned about system resilience. Analyze the following disruption scenarios:

1. **Pipeline failure**: For each of the following arc removals (one at a time), re-solve the model and report whether all demand can still be met, and at what additional cost:
   - Arc A7 (T1 → P1, the main trunk line)
   - Arc A20 (P2 → D7, the industrial park feed)
   - Arc A1 (S1 → T1, the primary river intake line)

2. **Source disruption**: The river intake (S1) is shut down due to contamination for an extended period. Can the remaining sources meet total demand? If not, how much demand must be curtailed, and which demand zones should be curtailed first? Use the priority classifications (Emergency > Critical > Standard) to develop a **prioritized curtailment plan** by modifying the model to allow unmet demand with a penalty cost structure:
   - Emergency nodes: $50/1000 gal penalty for unmet demand
   - Critical nodes: $20/1000 gal penalty
   - Standard nodes: $5/1000 gal penalty

3. **Capacity expansion**: Based on your resilience analysis, recommend the single most impactful infrastructure investment the city could make (e.g., a new pipeline segment, expanded source capacity, additional storage). Justify with quantitative evidence from your models.

4. **Summary report**: Prepare a technical memorandum (1–2 pages) for the Chief Engineer summarizing the optimal operating plan, key vulnerabilities identified, and your top infrastructure recommendation.

---

## Deliverables

- A written formulation document (PDF or markdown) with the MCNF model and network transformation details.
- A Google Colab notebook (`.ipynb`) with AMPL/Gurobi implementation, NetworkX visualization, resilience analysis, and the technical memorandum.
