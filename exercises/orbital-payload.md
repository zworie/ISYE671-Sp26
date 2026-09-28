# In-Class Exercise: The Orbital Payload

Time Limit: 15 Minutes

Tools Allowed: Pen & Paper, Excel, Calculator, Python, AI, or Guesswork.

### The Scenario

You are the Lead Mission Engineer for a new CubeSat satellite launch. Your team has developed **5 distinct scientific instruments** (Modules), but the rocket has strict limits on **Weight** and **Power Supply**.

Your goal is to select which subset of instruments to include on the manifest to maximize the total **Scientific Value (Score)**.

### The Data

The Constraints (The Limits)

The satellite bus has the following hard capacities:

1.  **Maximum Weight:** 60 kg

2.  **Maximum Power Draw:** 50 Watts

The Candidates (The Instruments)

You can choose to include (1) or exclude (0) each instrument. You cannot take partial instruments, and you have only one of each.

| **Instrument Name** | **Weight (kg)** | **Power Draw (Watts)** | **Scientific Value (Score)** |
|----|----|----|----|
| **A. Alpha Imager** | 30 kg | 10 W | **60** |
| **B. Beta Sensor** | 20 kg | 20 W | **45** |
| **C. Gamma Ray Detector** | 15 kg | 15 W | **40** |
| **D. Delta Comm Array** | 10 kg | 30 W | **50** |
| **E. Epsilon Magnetometer** | 5 kg | 5 W | **10** |

### Your Task

Answer the following questions:

1.  **The Manifest:** Which instruments are you loading onto the satellite? (e.g., "A, C, and E")

2.  **The Check:** What is the Total Weight and Total Power of your selection? (Must be \$\le\$ 60kg and \$\le\$ 50W)

3.  **The Result:** What is your Total Scientific Value?

4.  **The Method:**

    - Did you try to pick the highest value items first? Did that work?

    - Did you calculate "Value per kg"?

    - If you used AI, did it understand that you can only take **one** of each (Binary constraint)?
