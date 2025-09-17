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
| `script_UFLA_OpenDSS_deterministic_power_flow.py` | Table II and Fig 5 | This routine performs a deterministic (snapshot) power flow analysis in OpenDSS. It uses the OpenDSS input files located in the folder `OpenDSS_Files - UFLA` as the system model. The routine solves the power flow for different scenarios (minimum/maximum demand, with or without distributed generation) and saves the results in an Excel file. |
| `script_UFLA_OpenDSS_daily_power_flow.py` | Fig. 6 (a, b, c, d, e f, g, h) | This routine performs a daily time-series power flow analysis in OpenDSS, located in the folder OpenDSS_Files - UFLA. In addition to solving the power flow for different scenarios the routine implements an optimization algorithm to determine the optimal capacitor bank size. All simulation results, including voltage profiles, total active and reactive power, and power factor, are saved in an Excel file. |

---

## 📂 How to use

| File | Adjustments |
|------|-------------|
| `script_UFLA_OpenDSS_deterministic_power_flow.py` | Update the file paths to match your computer. 
||`circuito = r"C:\Users\User\Desktop\ModelingUFLA\Master_A.dss"`|
||`arquivo_cargas_min = r"C:\Users\User\Desktop\ModelingUFLA\Loads_A.txt"`|
||`arquivo_cargas_max = r"C:\Users\User\Desktop\ModelingUFLA\Loads_B.txt"`|
||`pv1 = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem1.txt"`|
||`pv2 = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem2.txt"`|
||#Save results to Excel  `df.to_excel(r"C:\Users\User\Desktop\resultados_cenarios.xlsx", index=False)`|



---

## 💻 Softwares

- Phyton 3.13.
- OpenDSS Version 9.8.0.1 or later.
- All simulation codes were executed using the Spyder IDE.

---

## ✉️ Contact

For questions or replication of results:  
silvia.ferreira@ufla.br

The data used in this work, including model data, were collected from the distribution system of the Federal University of Lavras. For any use of these data in other works, please contact the authors
silvia.ferreira@ufla.br
joaquim@ufla.br
marcelo.rezende@ufla.br

