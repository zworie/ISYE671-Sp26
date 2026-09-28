# Case Study 1: Linear Programming

## Regional Hospital System Staffing and Resource Planning

### ISYE 671 — Linear Optimization and Network Flows

---

## Background

Prairie Health Partners (PHP) operates a network of four hospitals across northern Illinois. As the newly hired Director of Operations Analytics, you have been asked to develop a comprehensive quarterly staffing and resource allocation plan for the upcoming quarter (Q4: October–December).

The health system is under financial pressure: reimbursement rates from government payers have declined, labor costs have risen, and the board has mandated a 6% reduction in operating costs compared to Q3 while maintaining quality-of-care metrics. Your task is to formulate and solve a linear programming model that determines optimal staffing levels, patient routing preferences, and resource utilization across all four facilities.

---

## System Description

### Facilities

| Hospital | Location | Licensed Beds | Operating Rooms | ICU Beds | ED Bays |
|----------|----------|:---:|:---:|:---:|:---:|
| Prairie Central Medical Center (PCMC) | DeKalb | 320 | 12 | 40 | 30 |
| Kishwaukee Community Hospital (KCH) | Sycamore | 180 | 6 | 18 | 16 |
| Heartland Regional Hospital (HRH) | Rochelle | 140 | 4 | 12 | 12 |
| Valley View Medical Center (VVMC) | Dixon | 200 | 8 | 22 | 20 |

### Staffing Categories

PHP employs staff in six categories, each with different cost structures and scheduling constraints:

| Category | Abbreviation | Avg. Hourly Cost (Regular) | Overtime Multiplier | Min. Staff Ratio |
|----------|:---:|:---:|:---:|:---|
| Registered Nurses | RN | $42 | 1.5× | 1 per 4 patients (med-surg), 1 per 2 (ICU) |
| Licensed Practical Nurses | LPN | $28 | 1.5× | 1 per 8 patients (med-surg only) |
| Certified Nursing Assistants | CNA | $18 | 1.5× | 1 per 10 patients (med-surg) |
| Physicians (Hospitalists) | MD | $125 | N/A (salaried) | 1 per 15 patients |
| Surgical Technicians | ST | $35 | 1.5× | 2 per operating room in use |
| Respiratory Therapists | RT | $38 | 1.5× | 1 per 6 ICU patients |

Each staff member works 36 hours per week (three 12-hour shifts). Overtime is permitted up to 12 additional hours per week per employee. Each facility currently has the following full-time equivalent (FTE) staff:

| Category | PCMC | KCH | HRH | VVMC |
|----------|:---:|:---:|:---:|:---:|
| RN | 260 | 130 | 95 | 155 |
| LPN | 80 | 45 | 35 | 50 |
| CNA | 100 | 55 | 40 | 60 |
| MD | 28 | 14 | 10 | 16 |
| ST | 30 | 14 | 10 | 18 |
| RT | 18 | 8 | 6 | 10 |

Hiring new FTEs costs $5,000 per person (recruitment, onboarding, training), and laying off staff costs $8,000 per person (severance, unemployment insurance costs). Both hiring and layoff decisions apply for the entire quarter. In addition, PHP can bring in travel nurses (RN only) at $85/hour with no overtime limit, but travel nurse contracts require a minimum commitment of 360 hours over the quarter.

### Patient Demand

Patient volumes are forecasted by service line for each hospital. The table below shows **average daily census** (ADC) by service line for Q4:

| Service Line | PCMC | KCH | HRH | VVMC | Total |
|---|:---:|:---:|:---:|:---:|:---:|
| Medical-Surgical (Med-Surg) | 185 | 95 | 70 | 110 | 460 |
| ICU / Critical Care | 32 | 14 | 9 | 17 | 72 |
| Surgical (inpatient, post-op) | 55 | 22 | 14 | 28 | 119 |
| Emergency Department (daily visits) | 210 | 95 | 65 | 115 | 485 |
| Outpatient Surgery (daily cases) | 18 | 8 | 5 | 10 | 41 |

**Important notes on demand:**

- Up to 15% of Med-Surg and Surgical patients can be **redirected** between hospitals (patient steering through referral networks), but ICU and ED patients cannot be redirected.
- Patient redirection incurs a transportation/coordination cost of $120 per patient-day redirected.
- Seasonal flu surge: In December, ICU and ED volumes are expected to increase by 20% above the ADC shown.

### Operating Room Scheduling

Each operating room can support a maximum of 4 surgical cases per day (8-hour block schedule, average 2 hours per case including turnover). Inpatient surgeries require 1 OR-day per surgical patient admission on average. Outpatient surgeries require 0.5 OR-days per case.

### Revenue and Cost Structure

Average **daily revenue per patient** by service line:

| Service Line | Revenue per Patient-Day |
|---|:---:|
| Med-Surg | $2,800 |
| ICU | $6,500 |
| Surgical | $4,200 |
| ED Visit | $1,400 |
| Outpatient Surgery Case | $3,600 |

**Operating costs** (non-labor, per patient-day): Med-Surg $950, ICU $2,400, Surgical $1,500, ED $600, Outpatient Surgery $1,200 per case.

### Quality Constraints

PHP must maintain the following quality thresholds to keep accreditation and payer contracts:

1. **Bed occupancy** must not exceed 90% at any facility in any month.
2. **Nurse-to-patient ratios** (RN) must meet the minimums specified above at all times.
3. **ICU occupancy** must not exceed 85%.
4. **Average ED wait time proxy**: the ratio of ED daily visits to ED bays must not exceed 12 at any facility.

### Q3 Operating Cost Baseline

Total Q3 labor costs across all facilities were $48.2 million. Total Q3 non-labor operating costs were $31.5 million. The board requires **total Q4 operating costs** (labor + non-labor + hiring/layoff + redirection + travel nurse costs) to be at most 94% of Q3 total operating costs.

---

## Your Assignment

### Part 1: Model Formulation

Formulate a linear programming model for this problem. Your formulation must include:

1. **Decision variables**: Define all decision variables clearly, including their indices and domains. You will need to make decisions about staffing levels (hiring, layoffs, overtime, travel nurses), patient redirection volumes, and potentially which service lines to prioritize at each facility.

2. **Objective function**: Construct an appropriate objective. Consider whether you should maximize profit, minimize cost, or use a different objective. Justify your choice.

3. **Constraints**: Formulate all constraints, including:
   - Staffing ratio requirements by service line
   - Bed capacity and occupancy limits
   - OR capacity constraints
   - Budget/cost reduction mandate
   - Overtime limits
   - Travel nurse minimum commitment
   - Patient redirection limits
   - December surge adjustments
   - Non-negativity and any other bound constraints

4. **Assumptions**: State clearly any assumptions you make to keep the model linear and tractable. Where data is ambiguous or incomplete, document your assumption and justify it.

### Part 2: Implementation and Solution

Implement your model in AMPL using Gurobi as the solver in a Google Colab notebook. Your implementation should:

1. Use separate `.mod` and `.dat` structures (can be embedded in notebook cells using `%%writefile` or AMPL string commands).
2. Solve the model and report the optimal objective value.
3. Present the solution in clear, well-formatted tables showing:
   - Recommended staffing levels (hires, layoffs, overtime hours, travel nurses) by facility
   - Patient redirection plan (which patients move, from where to where, how many)
   - Facility utilization rates (beds, ORs, ICU)
   - Total cost breakdown by category

### Part 3: Analysis and Recommendations

1. **Binding constraints**: Identify which constraints are binding at optimality. What do these tell management about system bottlenecks?

2. **Scenario analysis**: Solve the model under the following alternative scenarios and compare results:
   - *Scenario A*: The December flu surge is 30% instead of 20%.
   - *Scenario B*: Travel nurses are unavailable (e.g., national shortage).
   - *Scenario C*: The board relaxes the cost reduction target to 3% instead of 6%.

3. **Managerial report**: Write a 1–2 page executive summary (within your notebook or as a separate markdown cell) advising the PHP leadership team. Your report should translate the optimization results into actionable recommendations, discuss risks and limitations of the model, and identify what additional data or model extensions would improve decision-making.

---

## Deliverables

- A written formulation document (PDF or markdown) with all sets, parameters, variables, objective, and constraints.
- A Google Colab notebook (`.ipynb`) with working AMPL/Gurobi code, solution output, scenario analysis, and the managerial report.
