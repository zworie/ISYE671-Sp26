# ISYE 671: Linear Optimization and Network Flows

# Lecture — What Now? From Optimization to Continued Learning

**Spring 2026 | Northern Illinois University**
**Instructor: Dr. Ziteng Wang**

---

## 1. Where We Have Been

Over the course of this semester, you have built a substantial foundation in optimization — one of the most powerful and versatile methodological toolkits in engineering, business, and the sciences. Let us briefly recall the arc of what we covered:

- **Linear programming**: Formulating real-world problems as linear programs, understanding feasibility, optimality, and the interpretation of LP solutions.
- **Integer programming**: Moving beyond continuous relaxations to model discrete decisions — binary variables, logical constraints, branch-and-bound, cutting planes, and solver behavior.
- **Network flow models**: Minimum-cost network flow, maximum flow, shortest path, transportation, assignment, and matching — exploiting graph structure for computational efficiency.
- **Large-scale optimization**: Column generation, Dantzig-Wolfe decomposition, Benders decomposition, and Lagrangian relaxation — techniques for tackling problems too large for direct solution.

Throughout, you learned to use AMPL with the Gurobi solver to translate mathematical models into working code, interpret solver output, and make decisions based on optimization results. This is a strong foundation — but it is only the beginning.

The purpose of this final lecture is to answer a simple question: **What now?**

---

## 2. Deepening the Theory of Linear Optimization

In this course, we focused on modeling and computation. The theoretical foundations of linear programming are deep and elegant, and further study will sharpen your intuition and expand your capabilities.

### 2.1 The Geometry of Linear Programming

Every LP has a geometric interpretation. The feasible region of a linear program is a **polyhedron** — the intersection of finitely many halfspaces. Optimal solutions, when they exist, occur at **vertices** (extreme points) of this polyhedron. Understanding this geometry illuminates why LP algorithms work and provides intuition for degeneracy, alternative optima, and unboundedness.

Key topics for further study include the theory of convex sets and polyhedra, the representation of polyhedra via vertices and extreme rays (the Minkowski-Weyl theorem), and the relationship between the geometry of the feasible region and the structure of optimal solutions.

**Where to learn more:**

- Bertsimas and Tsitsiklis, *Introduction to Linear Optimization* (1997) — Chapters 2–3 provide a rigorous geometric treatment.
- Chvátal, *Linear Programming* (1983) — An accessible classic with excellent geometric intuition.

### 2.2 The Simplex Method

The simplex method, developed by George Dantzig in 1947, remains one of the most important algorithms in all of computational mathematics. It moves along the edges of the feasible polyhedron from vertex to vertex, improving the objective at each step. Although we used solvers to handle the computation, understanding the simplex method — pivoting, basis selection, and the algebra of the simplex tableau — gives you insight into what the solver is actually doing.

Further study should cover: the revised simplex method (the computationally practical form), anti-cycling rules (Bland's rule, lexicographic pivoting), and the question of simplex complexity (worst-case exponential, but remarkably efficient in practice).

**Where to learn more:**

- Bertsimas and Tsitsiklis, *Introduction to Linear Optimization* (1997) — Chapters 3–4.
- Rardin, *Optimization in Operations Research* (2016) — Chapter 5 (our textbook).

### 2.3 Interior Point Methods

Interior point methods take a fundamentally different approach: rather than walking along the boundary of the feasible region, they move through the interior. Karmarkar's 1984 algorithm showed that LPs could be solved in polynomial time using this approach, and modern interior point methods (particularly primal-dual path-following methods) are competitive with — and sometimes superior to — the simplex method, especially for large-scale problems.

**Where to learn more:**

- Wright, *Primal-Dual Interior-Point Methods* (1997) — The standard reference.
- Nocedal and Wright, *Numerical Optimization* (2006) — Chapter 14.
- Bertsimas and Tsitsiklis, *Introduction to Linear Optimization* (1997) — Chapter 9.

### 2.4 Duality Theory

We touched on duality in this course, but the theory goes much deeper. Every LP has a dual LP, and the relationship between primal and dual problems is one of the most profound ideas in optimization. Strong duality, complementary slackness, and the economic interpretation of dual variables (shadow prices) are foundational. Farkas' lemma provides the theoretical underpinning for duality and has far-reaching consequences throughout optimization and game theory.

**Where to learn more:**

- Bertsimas and Tsitsiklis, *Introduction to Linear Optimization* (1997) — Chapter 4.
- Rardin, *Optimization in Operations Research* (2016) — Chapter 6.
- Vanderbei, *Linear Programming: Foundations and Extensions* (2020) — Chapters 5–6.

---

## 3. Sensitivity Analysis: Understanding the Value of Information

Sensitivity analysis answers a critical practical question: **How does the optimal solution change when the data change?** In practice, data are rarely known exactly — costs fluctuate, demands are uncertain, capacities shift. Understanding sensitivity is what separates a modeler who can build a model from one who can draw actionable insights from it.

### 3.1 Theory of Sensitivity Analysis

The theoretical basis of sensitivity analysis is rooted in LP duality. Ranging analysis examines how much a single coefficient (objective function coefficient or right-hand-side value) can change before the current optimal basis changes. The dual variables (shadow prices) directly quantify the marginal value of relaxing constraints.

Key concepts include: allowable ranges for objective coefficients and RHS values, reduced costs and their interpretation, the 100% rule for simultaneous changes, and parametric programming for systematic sensitivity exploration.

**Where to learn more:**

- Rardin, *Optimization in Operations Research* (2016) — Chapter 6.
- Bradley, Hax, and Magnanti, *Applied Mathematical Programming* (1977) — Chapter 4 (freely available online from MIT).

### 3.2 Solver-Based Sensitivity Analysis

Modern solvers (Gurobi, CPLEX, AMPL) provide sensitivity information automatically. Gurobi, for example, reports shadow prices (dual values), reduced costs, and basis status for every variable and constraint. Learning to read and interpret solver sensitivity output is an essential practical skill.

In AMPL, the `.dual` suffix on constraints gives shadow prices, and the `.rc` suffix on variables gives reduced costs. These can be combined with ranging analysis to quickly assess the robustness of an optimal solution.

**Where to learn more:**

- Gurobi documentation: [Attributes — Sensitivity Information](https://www.gurobi.com/documentation/)
- AMPL documentation: [Sensitivity Analysis](https://ampl.com/resources/the-ampl-book/)
- Fourer, Gay, and Kernighan, *AMPL: A Modeling Language for Mathematical Programming* (2003) — Chapter 17.

---

## 4. Beyond Linear: Nonlinear and Convex Optimization

Linear programming is powerful, but many real-world problems have nonlinear objectives or constraints. The field of nonlinear optimization is vast, and the key distinction is between **convex** and **non-convex** problems.

### 4.1 Convex Optimization

A convex optimization problem has a convex objective function and a convex feasible set. The defining property is that any local optimum is also a global optimum — this makes convex problems tractable and well-understood. LP is a special case of convex optimization.

Important classes of convex problems include: quadratic programming (QP), second-order cone programming (SOCP), semidefinite programming (SDP), and general convex programming. These arise in portfolio optimization, robust optimization, signal processing, machine learning (support vector machines, regularized regression), and control systems.

**Where to learn more:**

- Boyd and Vandenberghe, *Convex Optimization* (2004) — The definitive textbook, freely available at [https://web.stanford.edu/~boyd/cvxbook/](https://web.stanford.edu/~boyd/cvxbook/). This is perhaps the single most important book to read next.
- Lectures by Stephen Boyd (Stanford) are available free on YouTube.

### 4.2 Non-Convex Optimization

When convexity fails, optimization becomes fundamentally harder. Local optima may not be global, and finding the global optimum may be computationally intractable. Yet non-convex problems are everywhere: deep learning training, many engineering design problems, and combinatorial optimization are all non-convex.

Approaches to non-convex optimization include: global optimization methods (branch-and-bound for nonlinear problems), heuristics and metaheuristics (simulated annealing, genetic algorithms, particle swarm), convex relaxations (replacing non-convex problems with tractable convex approximations), and gradient-based methods with careful initialization.

**Where to learn more:**

- Nocedal and Wright, *Numerical Optimization* (2006) — The standard reference for gradient-based methods.
- Bertsekas, *Nonlinear Programming* (2016) — Comprehensive and rigorous.
- Kochenderfer and Wheeler, *Algorithms for Optimization* (2019) — Excellent modern treatment accessible to engineers.

---

## 5. Optimization Under Uncertainty

Real-world decision-making almost always involves uncertainty. Extending optimization to handle uncertain data is one of the most active and practically important areas of operations research.

### 5.1 Stochastic Programming

Stochastic programming models uncertainty through probability distributions over scenarios. Two-stage stochastic programs make some decisions now (first stage) and recourse decisions later (second stage) once uncertainty is resolved. This framework is natural for supply chain planning, energy systems, and financial portfolio management.

### 5.2 Robust Optimization

Robust optimization takes a worst-case approach: it seeks solutions that perform well under any realization of uncertain parameters within a specified uncertainty set, without requiring probability distributions. This approach is particularly appealing when distributional information is limited.

**Where to learn more:**

- Birge and Louveaux, *Introduction to Stochastic Programming* (2011).
- Ben-Tal, El Ghaoui, and Nemirovski, *Robust Optimization* (2009).
- Bertsimas and Sim, "The Price of Robustness," *Operations Research* 52(1), 2004.

---

## 6. Contemporary Applications of Optimization

Optimization is not an abstract academic exercise — it is a living, breathing methodology deployed across virtually every industry. The professional community around INFORMS (the Institute for Operations Research and the Management Sciences) is an excellent gateway to seeing optimization in action.

### 6.1 Where Optimization Is Making an Impact Today

Consider just a few domains where the techniques you have learned are being applied at scale:

- **Supply chain and logistics**: Vehicle routing, facility location, inventory management, and distribution network design. Companies like Amazon, UPS, and FedEx rely on optimization at the core of their operations.
- **Healthcare**: Operating room scheduling, nurse staffing, organ transplant matching, radiation therapy planning, and pandemic response resource allocation.
- **Energy systems**: Unit commitment, economic dispatch, renewable energy integration, grid planning, and electricity market design.
- **Finance**: Portfolio optimization, risk management, algorithmic trading, and credit scoring.
- **Transportation**: Airline crew scheduling, fleet assignment, railway timetabling, and ride-sharing platform optimization.
- **Manufacturing**: Production scheduling, process optimization, quality control, and supply chain coordination.
- **Telecommunications**: Network design, spectrum allocation, and routing.
- **Machine learning**: Many ML training procedures are optimization problems — regularized regression, support vector machines, and neural network training all minimize a loss function subject to constraints.

### 6.2 INFORMS Resources

INFORMS is the leading professional society for operations research, analytics, and management science. As you continue in your career, the following INFORMS resources are valuable:

- **INFORMS Journals**: *Operations Research*, *Management Science*, *INFORMS Journal on Computing*, *INFORMS Journal on Optimization*, and *INFORMS Journal on Applied Analytics* (formerly *Interfaces*) publish cutting-edge research and real-world applications. The *INFORMS Journal on Applied Analytics* is particularly useful for seeing how optimization is deployed in practice — it features the annual Franz Edelman Award finalists, which showcase some of the most impactful OR applications in the world.
- **TutORials in Operations Research**: Published annually, these provide accessible introductions to advanced topics by leading researchers. The 2024 volume covers topics including large language models, machine learning, and mathematical optimization.
- **INFORMS Annual Meeting**: The largest gathering of OR professionals, with hundreds of sessions on optimization, analytics, and their applications.
- **INFORMS Student Chapters and Competitions**: If you continue in research or graduate studies, INFORMS student membership gives you access to the community, competitions (including the INFORMS Undergraduate Operations Research Prize and the Doing Good with Good OR competition), and career resources.

**Explore**: [https://www.informs.org](https://www.informs.org)

---

## 7. Generative AI and LLMs: Empowering the OR Professional

We are at an inflection point. Large language models (LLMs) and generative AI are transforming how optimization problems are formulated, coded, debugged, and interpreted. As OR professionals, you should not view AI as a replacement for your expertise — you should view it as an amplifier.

### 7.1 What LLMs Can Do for OR Right Now

Today, LLMs can assist with several stages of the optimization workflow:

**Problem formulation**: Given a natural language description of a business problem, LLMs can draft mathematical formulations — defining decision variables, objective functions, and constraints. This is not perfect, and expert review is essential, but it dramatically accelerates the modeling process.

**Code generation**: LLMs can generate solver code (Python/Gurobi, AMPL, PuLP, OR-Tools) from mathematical formulations, including data processing, model construction, and solution extraction. In this course, you experienced this firsthand using Claude as a coding assistant.

**Debugging and interpretation**: When a model is infeasible or produces unexpected results, LLMs can help diagnose the issue, suggest constraint relaxations, and explain solver output in plain language.

**Literature review and learning**: LLMs can summarize research papers, explain unfamiliar techniques, and help you navigate the vast OR literature.

### 7.2 Emerging Research: LLM-Powered Optimization Systems

The research community is actively building systems that integrate LLMs with traditional solvers:

- **OptiMUS** (Ahmaditeshnizi, Gao, and Udell, 2024): An LLM-based agent that formulates and solves mixed-integer linear programs from natural language descriptions. OptiMUS uses a modular architecture — separate agents for formulation, code generation, and solution evaluation — and has demonstrated significant performance gains over basic prompting approaches.
- **OR-LLM-Agent** (Zhang et al., 2025): A framework built on reasoning LLMs (e.g., DeepSeek-R1) that decomposes OR problem-solving into mathematical modeling, code generation, and debugging stages, with dedicated sub-agents for each task.
- **ORLM** (Tang et al., 2024): A framework for training open-source LLMs specifically for optimization modeling, introducing the IndustryOR benchmark for evaluating LLMs on practical OR problems.
- **Large Language Models as Optimizers** (Yang et al., 2023): The OPRO framework uses LLMs directly as optimizers by describing the optimization task in natural language and iteratively generating and evaluating new solutions.
- **PaMOP** (IJCAI 2025): A framework that uses tree-structured decomposition to guide LLMs in modeling complex optimization problems, generating AMPL code via partition-based prompting.

### 7.3 What LLMs Cannot (Yet) Do

It is equally important to understand the current limitations:

- **Mathematical rigor**: LLMs can produce plausible-looking formulations that are subtly wrong — missing constraints, incorrect index sets, or violated problem structure. Human verification remains essential.
- **Algorithmic understanding**: LLMs do not "understand" algorithms the way a trained OR professional does. They pattern-match from training data, which means they can fail on novel or unusual problem structures.
- **Scalability and efficiency**: For large-scale problems, choosing the right decomposition method, exploiting problem structure, and tuning solver parameters require expertise that LLMs cannot reliably provide.
- **Domain context**: LLMs lack the contextual understanding of specific industries, regulations, and stakeholder preferences that shape real-world optimization.

**The takeaway**: Your optimization expertise becomes *more* valuable in the age of AI, not less. LLMs lower the barrier to entry for basic optimization tasks, but the demand for people who can formulate complex models correctly, interpret results critically, and make sound decisions based on those results is only growing.

---

## 8. Working with Data in Operations Research

Optimization models do not exist in a vacuum — they require data. The quality, availability, and processing of data are often the bottleneck in applied OR work. The integration of data science and operations research is one of the most important trends in the field.

### 8.1 The Data-to-Decision Pipeline

A typical applied OR project involves a pipeline: raw data → data cleaning and processing → parameter estimation → model formulation → solution → implementation and monitoring. The optimization model is one component of this larger system.

Skills you will need include: data wrangling (pandas, SQL), statistical estimation (demand forecasting, cost estimation), data visualization (matplotlib, seaborn, Plotly), and connecting optimization models to live data systems.

### 8.2 Data-Driven Optimization

Several active research areas sit at the intersection of data science and optimization:

- **Predict-then-optimize**: Use machine learning to estimate uncertain parameters (e.g., demand forecasts), then plug those estimates into an optimization model. Recent work explores training ML models to directly optimize downstream decision quality rather than prediction accuracy alone (Elmachtoub and Grigas, "Smart Predict, then Optimize," *Management Science*, 2022).
- **Online optimization and learning**: Make sequential decisions under uncertainty, learning from observed outcomes. Multi-armed bandits, online convex optimization, and reinforcement learning are key frameworks.
- **Data-driven robust optimization**: Construct uncertainty sets directly from historical data, rather than assuming parametric distributions.

### 8.3 Practical Tools

Beyond the AMPL/Gurobi environment you used in this course, the optimization ecosystem is broad:

- **Python solvers and interfaces**: Gurobi (`gurobipy`), Google OR-Tools, PuLP, CVXPY (for convex optimization), Pyomo.
- **Commercial solvers**: Gurobi, CPLEX (IBM), FICO Xpress, MOSEK (for conic optimization).
- **Open-source solvers**: HiGHS (LP/MIP), GLPK, CBC (COIN-OR), SCIP.
- **Data tools**: pandas, NumPy, scikit-learn, and the broader Python data science stack.

---

## 9. Living, Studying, Working, and Competing with AI

Let me speak directly about something I believe is essential for your careers. We are living through a period of profound technological change. AI — and large language models in particular — is reshaping every profession, including engineering, analytics, and operations research.

### 9.1 AI Is Already Here

This is not a future prediction. AI is already being used to write code, draft reports, analyze data, generate designs, and assist with decision-making in organizations of every size. In this course, some of you used AI tools to help understand concepts, debug code, or explore alternative formulations. This is not cheating — it is the emerging reality of professional practice.

### 9.2 What This Means for You

The professionals who will thrive are those who can:

1. **Formulate problems precisely**. AI can generate code, but someone must define *what* problem to solve. The ability to translate a messy real-world situation into a clean mathematical formulation is a deeply human skill that AI assists but does not replace.

2. **Evaluate and validate AI output critically**. AI-generated solutions must be checked. Understanding the theory and methodology behind optimization gives you the ability to spot errors that AI cannot catch itself.

3. **Combine domain knowledge with technical tools**. Knowing optimization methodology is necessary but not sufficient. The most impactful OR professionals are those who also understand the domain — healthcare, logistics, energy, manufacturing — deeply enough to ask the right questions.

4. **Learn continuously**. The tools, methods, and best practices in optimization are evolving rapidly. The ability to learn new methods, adapt to new software, and stay current with the literature is essential.

5. **Communicate results effectively**. An optimal solution that cannot be explained, trusted, and implemented is worthless. Translating mathematical results into actionable recommendations is a skill that AI assists but does not replace.

### 9.3 Your Competitive Advantage

You now have something that most professionals do not: a rigorous understanding of optimization — how to formulate problems, what makes a formulation correct, how solvers work, and how to interpret results. This knowledge is your competitive advantage. It allows you to use AI tools more effectively than someone without this background, and it allows you to contribute to problems that AI alone cannot solve.

Do not think of optimization as a course you took. Think of it as a **way of thinking** — a systematic approach to decision-making under constraints that you will carry with you into every role you hold.

---

## 10. Recommended Resources for Continued Learning

### 10.1 Textbooks

| Topic | Book | Authors |
|-------|------|---------|
| LP theory and geometry | *Introduction to Linear Optimization* | Bertsimas and Tsitsiklis (1997) |
| LP (accessible introduction) | *Linear Programming* | Chvátal (1983) |
| General optimization | *Optimization in Operations Research* | Rardin (2016) |
| Convex optimization | *Convex Optimization* | Boyd and Vandenberghe (2004) |
| Nonlinear optimization | *Numerical Optimization* | Nocedal and Wright (2006) |
| Integer programming | *Integer Programming* | Conforti, Cornuéjols, and Zambelli (2014) |
| Network flows | *Network Flows* | Ahuja, Magnanti, and Orlin (1993) |
| Stochastic programming | *Introduction to Stochastic Programming* | Birge and Louveaux (2011) |
| Robust optimization | *Robust Optimization* | Ben-Tal, El Ghaoui, and Nemirovski (2009) |
| Interior point methods | *Primal-Dual Interior-Point Methods* | Wright (1997) |
| Algorithms for optimization | *Algorithms for Optimization* | Kochenderfer and Wheeler (2019) |
| AMPL modeling | *AMPL: A Modeling Language for Mathematical Programming* | Fourer, Gay, and Kernighan (2003) |

### 10.2 Online Courses and Lectures

- **Stephen Boyd's Convex Optimization (Stanford, EE364a)** — Lectures freely available on YouTube. The companion textbook is free online.
- **MIT OpenCourseWare — Introduction to Mathematical Programming (15.053)** — Freely available lecture notes and problem sets.
- **Coursera / edX** — Several universities offer optimization courses, including discrete optimization (University of Melbourne) and operations research (Georgia Tech).

### 10.3 Professional Resources

- **INFORMS** ([https://www.informs.org](https://www.informs.org)) — Professional society for OR, analytics, and management science.
- **INFORMS TutORials in Operations Research** ([https://pubsonline.informs.org/series/educ](https://pubsonline.informs.org/series/educ)) — Annual volumes of accessible tutorials.
- **INFORMS Journal on Applied Analytics** — Real-world optimization case studies, including Edelman Award finalists.
- **INFORMS Journal on Optimization** — Research on data-driven optimization and optimization methods in machine learning.
- **OR/MS Today** — INFORMS magazine covering industry trends and applications.

### 10.4 Solver Documentation and Communities

- **Gurobi** ([https://www.gurobi.com](https://www.gurobi.com)) — Extensive documentation, examples, and free academic licenses.
- **AMPL** ([https://ampl.com](https://ampl.com)) — Modeling language resources and the AMPL book.
- **CVXPY** ([https://www.cvxpy.org](https://www.cvxpy.org)) — Python-embedded modeling language for convex optimization.
- **OR Stack Exchange** ([https://or.stackexchange.com](https://or.stackexchange.com)) — Community Q&A for operations research.
- **COIN-OR** ([https://www.coin-or.org](https://www.coin-or.org)) — Open-source optimization software.

### 10.5 Key Papers at the Intersection of AI and OR

- Ahmaditeshnizi, A., Gao, W., and Udell, M. (2024). "OptiMUS: Scalable Optimization Modeling with (MI)LP Solvers and Large Language Models." *Proceedings of the 41st International Conference on Machine Learning (ICML)*, PMLR 235:577–596.
- Zhang, B. et al. (2025). "OR-LLM-Agent: Automating Modeling and Solving of Operations Research Optimization Problems with Reasoning LLM." *arXiv preprint arXiv:2503.10009*.
- Tang, Z. et al. (2024). "ORLM: A Customizable Framework in Training Large Models for Automated Optimization Modeling." *arXiv preprint arXiv:2405.17743*.
- Yang, C. et al. (2023). "Large Language Models as Optimizers." *arXiv preprint arXiv:2309.03409*.
- Elmachtoub, A. N. and Grigas, P. (2022). "Smart 'Predict, then Optimize.'" *Management Science* 68(1):9–26.
- Da Ros, F., Soprano, M., Di Gaspero, L., and Roitero, K. (2026). "Large Language Models for Combinatorial Optimization: A Systematic Review." *ACM Computing Surveys*.

---

## 11. Final Thoughts

Optimization is one of the most powerful frameworks for rational decision-making ever developed. In a world of limited resources, competing objectives, and complex constraints, the ability to formulate a problem mathematically, solve it rigorously, and translate the solution into action is extraordinarily valuable.

You have spent a semester building this capability. The models you formulated, the code you wrote, the problems you solved — these are not just homework. They are the foundation of a way of thinking that will serve you in research, in industry, and in life.

The field is evolving fast. New methods are being developed, new applications are being discovered, and new tools — including AI — are changing how optimization is practiced. Stay curious. Keep learning. Use the tools available to you, including AI, but always bring your own judgment, your domain knowledge, and your commitment to rigor.

Optimization is not just a course. It is a methodology, a mindset, and a career. Go use it.

---

*ISYE 671 — Spring 2026 — Northern Illinois University*
