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
| `senales.m` | Fig. 9 (a, b, c, d) | Loads waveform data from `Graf-KERs.xlsx` and plots four time-domain signals: input current, inductor currents, output current, and output voltage. |

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
