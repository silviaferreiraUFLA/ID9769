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
| `flywheel.m` | Fig. 6 (a, b, c) | Calculates mass, moment of inertia, and stored kinetic energy for five flywheel design cases. Generates bar plots comparing steel and aluminum options. |
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
