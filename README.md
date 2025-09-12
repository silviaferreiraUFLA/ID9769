# Modeling and Analysis of Distribution Power System at UFLA Using OpenDSS

**Manuscript ID:** IEEE LATAM Submission ID: 9769 
**Authors:**  

- Sílvia Costa Ferreira 
- Ronnielli Chagas de Oliveira
- Alexandre de Araújo
- Alexandre Luiz da Silva
- Marcelo Arriel Rezende
- João Paulo de Carvalho Pedroso
- Joaquim Paulo da Silva

---

## 📁 Included Files

This repository contains all scripts required to reproduce the simulation and numerical results presented in the article.

| File | Related Figure(s) | Description |
|--------|-------------------|-------------|
| `https://www.google.com/maps/d/u/0/edit?mid=1TxKzTqwEfGx__l0Tg8phycSTLsyf0gA&usp=sharing` | Fig. 1 | Google My Maps link containing the geographical coordinates of poles and transformers at UFLA. |
| `script_UFLA_OpenDSS_deterministic_power_flow.py` | Table II and Fig 5 | This routine performs a deterministic (snapshot) power flow analysis in OpenDSS. It uses the OpenDSS input files located in the folder XX as the system model, including the master circuit, load profiles, and distributed generation data. The routine automatically solves the power flow for different scenarios (e.g., minimum/maximum demand, with or without distributed generation), calculates key system metrics such as total active and reactive power, bus voltage magnitudes, losses, and power factor, and saves the results in an Excel file. |
| `senales.m` | Fig. 9 (a, b, c, d) | Loads waveform data from `Graf-KERs.xlsx` and plots four time-domain signals: input current, inductor currents, output current, and output voltage. |

---

## 📂 Required Database

- `Graf-KERs.xlsx`: Required for `senales.m`. Place it in the same folder as the script.
- `flywheel.m` and `TransferFunctions_KERS.m` are standalone and do not require additional files.

---

## 💻 Requirements

- MATLAB R2018b or later.
- OpenDSS Version 9.8.0.1 or later.
- No additional toolboxes are required.

---

## ✉️ Contact

For questions or replication of results:  
silvia.ferreira@ufla.br


Dora Castro
Saúl Méndez
Luis Carreto
