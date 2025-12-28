# CHE622 – Hybrid GCMC–MD Simulation of CO₂/CH₄ Adsorption in Coal

This repository contains the codes, input files, and analysis workflows developed as part of the **CHE622: Introduction to Molecular Simulations** course project.

The project investigates **competitive CO₂/CH₄ adsorption in deformable coal nanopores** using a **hybrid Grand Canonical Monte Carlo–Molecular Dynamics (GCMC–MD)** framework, with direct relevance to **enhanced coalbed methane (ECBM) recovery** and **CO₂ sequestration**.

---

## 📘 Project Overview

Enhanced coalbed methane recovery via CO₂ injection relies on the preferential adsorption of CO₂ over CH₄ in coal nanopores. However, gas adsorption also induces **coal matrix swelling**, which alters pore structure and adsorption capacity.

In this project, a **chemically realistic, flexible coal matrix** is modeled and simulated to capture the **two-way coupling** between:

* Competitive gas adsorption (CO₂ vs CH₄)
* Adsorption-induced coal matrix deformation

A hybrid **GCMC–MD** approach is used to equilibrate gas loading and structural relaxation simultaneously under reservoir-relevant conditions.

---

## 🔬 Methodology Summary

* **Coal model**: Wiser bituminous coal (C₁₈₆H₁₅₁N₃O₂₁S₃)
* **Force field (coal)**: PCFF (Class II)
* **Gas models**:

  * CH₄: TraPPE united-atom
  * CO₂: TraPPE rigid three-site
* **Simulation engine**: LAMMPS
* **Adsorption method**: Hybrid GCMC–MD
* **Thermodynamics**:

  * Fugacity-based chemical potentials
  * Peng–Robinson equation of state (EOS)
* **Ensemble**:

  * Anisotropic NPT (flexible cell)
* **Conditions**:

  * Temperature: 313.15 K
  * Pressure: up to 90 bar
  * Gas mixture: 90% CO₂ / 10% CH₄

---

## 📊 Key Results

* **Validated coal matrix**

  * Density ≈ 1.20 g/cm³ (bituminous coal range)
  * Micropore peak ≈ 3.8 Å
* **Pure CH₄ adsorption**

  * Dual-site Langmuir behavior
  * Higher simulated uptake than experiments due to ideal pore accessibility
* **Competitive adsorption**

  * CO₂ adsorbs preferentially over CH₄ across all pressures
  * CO₂/CH₄ selectivity < 1 due to CO₂-rich feed composition
* **Thermodynamics**

  * CO₂ exhibits consistently higher isosteric heat of adsorption
* **Structural response**

  * Adsorption-induced micropore generation
  * Clear coupling between adsorption and coal matrix deformation

---

## 🧪 Software & Tools

* **LAMMPS** (MD + GCMC)
* **LUNAR** (PCFF parameterization)
* **Packmol** (initial structure generation)
* **PoreBlazer v4.0** (pore size distribution)
* Python / shell scripts for post-processing

---

## 🎓 Course Information

* **Course**: CHE622 – Introduction to Molecular Simulations
* **Institution**: Department of Chemical Engineering
* **Author**: Nikant Yadav
* **Academic Term**: November 2025

This repository represents an **academic course project** and is intended for educational and research purposes.

---

## 🔮 Future Work

* Longer hybrid GCMC–MD simulations for high-pressure convergence
* Volumetric strain vs pressure analysis
* Direct comparison with experimental coal swelling data
* Permeability and diffusivity calculations

---

## 📄 License

This project is provided for **academic and educational use only**.
Please cite appropriately if reused.
