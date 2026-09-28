# Case Study 6: Large-Scale LP/IP

## Airline Crew Scheduling via Column Generation

### ISYE 671 — Linear Optimization and Network Flows

---

## Background

MidwestAir is a regional airline operating a hub-and-spoke network centered at Chicago O'Hare (ORD). The airline operates 40 daily flight legs across 6 spoke cities in the upper Midwest. Each flight leg requires a crew (a captain and first officer operating as a unit). MidwestAir needs to construct **crew pairings** — sequences of flight legs that begin and end at the crew base (ORD) within a single duty day — such that every flight leg is covered by exactly one pairing, while minimizing total crew cost.

This is a classic **set covering** problem that, in its natural formulation, has a very large number of variables (one per feasible pairing). You will use **column generation** to solve the LP relaxation efficiently, and then obtain an integer solution.

---

## Problem Data

### Crew Base

All crews are based at ORD. Every pairing must begin with a flight departing ORD and end with a flight arriving at ORD, all within one duty day.

### Spoke Cities

| Code | City |
|:---:|---|
| MKE | Milwaukee |
| MSN | Madison |
| STL | St. Louis |
| IND | Indianapolis |
| DSM | Des Moines |
| PIA | Peoria |

### Flight Schedule

MidwestAir operates 40 daily flight legs. All times are Central Time.

| Flt | From | To | Depart | Arrive | | Flt | From | To | Depart | Arrive |
|:---:|:---:|:---:|:---:|:---:|---|:---:|:---:|:---:|:---:|:---:|
| 101 | ORD | MKE | 6:30 | 7:15 | | 102 | MKE | ORD | 8:00 | 8:45 |
| 103 | ORD | MKE | 10:00 | 10:45 | | 104 | MKE | ORD | 11:30 | 12:15 |
| 105 | ORD | MKE | 14:00 | 14:45 | | 106 | MKE | ORD | 15:30 | 16:15 |
| 107 | ORD | MKE | 18:00 | 18:45 | | 108 | MKE | ORD | 19:30 | 20:15 |
| 201 | ORD | MSN | 7:00 | 7:40 | | 202 | MSN | ORD | 8:30 | 9:10 |
| 203 | ORD | MSN | 11:00 | 11:40 | | 204 | MSN | ORD | 12:30 | 13:10 |
| 205 | ORD | MSN | 15:00 | 15:40 | | 206 | MSN | ORD | 16:30 | 17:10 |
| 207 | ORD | MSN | 19:00 | 19:40 | | 208 | MSN | ORD | 20:30 | 21:10 |
| 301 | ORD | STL | 6:30 | 7:45 | | 302 | STL | ORD | 8:30 | 9:45 |
| 303 | ORD | STL | 11:00 | 12:15 | | 304 | STL | ORD | 13:00 | 14:15 |
| 305 | ORD | STL | 15:30 | 16:45 | | 306 | STL | ORD | 17:30 | 18:45 |
| 307 | ORD | STL | 19:30 | 20:45 | | 308 | STL | ORD | 21:30 | 22:45 |
| 401 | ORD | IND | 7:00 | 8:05 | | 402 | IND | ORD | 9:00 | 10:00 |
| 403 | ORD | IND | 12:00 | 13:05 | | 404 | IND | ORD | 14:00 | 15:00 |
| 405 | ORD | IND | 17:00 | 18:05 | | 406 | IND | ORD | 19:00 | 20:00 |
| 501 | ORD | DSM | 7:00 | 8:20 | | 502 | DSM | ORD | 9:15 | 10:30 |
| 503 | ORD | DSM | 12:00 | 13:20 | | 504 | DSM | ORD | 14:15 | 15:30 |
| 505 | ORD | DSM | 17:30 | 18:50 | | 506 | DSM | ORD | 19:45 | 21:00 |
| 601 | ORD | PIA | 8:00 | 8:40 | | 602 | PIA | ORD | 9:30 | 10:10 |
| 603 | ORD | PIA | 13:00 | 13:40 | | 604 | PIA | ORD | 14:30 | 15:10 |
| 605 | ORD | PIA | 18:00 | 18:40 | | 606 | PIA | ORD | 19:30 | 20:10 |

### Crew Rules (Simplified)

A **feasible pairing** is a sequence of flight legs satisfying:

1. **Base rule**: The pairing begins with a flight departing ORD and ends with a flight arriving at ORD.

2. **Connection time**: Between consecutive flight legs, the minimum sit time is **30 minutes** and the maximum sit time is **3 hours** (at any city, including ORD).

3. **Duty period**: A duty period begins 45 minutes before the first departure and ends 15 minutes after the last arrival. Total duty time must not exceed **12 hours**.

4. **Flight time limit**: Total flight time (block time) within the pairing cannot exceed **8 hours**.

5. **Maximum legs**: A pairing contains at most **4 flight legs**.

There are no multi-day pairings and no deadheading in this simplified version.

### Cost Structure

The cost of a pairing is:

$$\text{Pairing Cost} = \max\left(\text{Flight Time Pay},\ \text{Daily Guarantee}\right) + \text{Per Diem}$$

| Component | Rate |
|---|---|
| Flight time pay | $300 per flight hour |
| Daily guarantee | $1,100 per duty day |
| Per diem | $2.00 per hour of duty time |

A crew is paid the **greater of** flight time pay or the daily guarantee, plus per diem for the full duty period.

---

## Your Assignment

### Part 1: Problem Structure and Formulation

1. **Master problem**: Formulate the **set covering** master problem. Let $\mathcal{P}$ be the set of all feasible pairings, $x_p \in \{0,1\}$ for each pairing, $a_{fp} = 1$ if pairing $p$ covers flight $f$, and $c_p$ the cost of pairing $p$. Write the formulation.

2. **Problem scale**: How many feasible pairings could exist? Explain why column generation is useful even though enumeration may be possible for this smaller instance.

3. **Column generation framework**: Describe:
   - What is the **restricted master problem (RMP)**?
   - What is the **pricing subproblem**? Given dual values $\pi_f$ from the RMP, define the reduced cost of a pairing and explain how to find the pairing with the most negative reduced cost.
   - When does the algorithm terminate?

### Part 2: Implementation

Implement the column generation algorithm in a Google Colab notebook. Use AMPL/Gurobi for the RMP and Python for pairing generation.

1. **Enumerate all feasible pairings**: With 40 flights, 6 cities, and max 4 legs per pairing, full enumeration is tractable. Write a Python function that generates all feasible pairings by exploring sequences of flights that satisfy the crew rules. Report how many feasible pairings exist.

2. **Initial columns**: Start the RMP with simple 2-leg out-and-back pairings (one outbound + one return for each city pair). Add artificial variables with cost $100,000 for any uncovered flights.

3. **Column generation loop**: Implement the loop:
   - Solve the RMP LP relaxation.
   - Extract dual values $\pi_f$.
   - From the enumerated pairing pool, find the pairing with the most negative reduced cost.
   - Add it to the RMP.
   - Repeat until no negative reduced cost exists.
   - Log the objective value and column count at each iteration.

4. **Convergence plot**: Create a plot of the RMP objective value vs. iteration number.

### Part 3: Integer Solution and Analysis

1. **IP solution**: After column generation converges, solve the final RMP as an integer program (binary $x_p$). Report the LP and IP objectives, the LP-IP gap, and the number of pairings used.

2. **Solution details**: For each pairing in the integer solution, list the flight sequence, flight time, duty time, and cost.

3. **Crew utilization**: What is the average number of legs per pairing? What is the average crew utilization (flight time / duty time)?

4. **Comparison with full enumeration**: Solve the set covering IP using the complete set of enumerated pairings (without column generation). Compare the objective and solve time to the column generation approach. Discuss the trade-off.

5. **Executive summary**: Write a 1-page summary for MidwestAir's VP of Flight Operations covering the recommended crew schedule, total daily crew cost, and key efficiency metrics.

---

## Hints and Guidance

- **Start with 2-leg pairings**: The simplest pairings are out-and-back (ORD → city → ORD). These cover most flights and give you a working initial RMP quickly.
- **Enumeration approach**: Use a depth-first search that builds pairing sequences leg by leg, pruning whenever a connection is infeasible (wrong city, sit time out of range, duty/flight time exceeded, too many legs). This keeps the enumeration manageable.
- **Pairing cost**: Compute flight time in hours by summing (arrival − departure) for each leg. Duty time = (last arrival + 15 min) − (first departure − 45 min). Pay = max(300 × flight_hours, 1100) + 2.00 × duty_hours.
- **Adding columns in AMPL**: You can rebuild the RMP data each iteration by writing new data, or use AMPL's programmatic interface to add columns incrementally.

---

## Deliverables

- A written formulation document (PDF or markdown) covering the master problem, subproblem, and column generation framework.
- A Google Colab notebook (`.ipynb`) with the enumeration code, column generation implementation, convergence plot, IP solution, analysis, and executive summary.
