# 🧠 AI-Powered Insurance Claims Triage

A simple AI-driven workflow that supports insurance claims operations by structuring claims, checking coverage against policy wording, and recommending operational decisions (approve / escalate / reject) with human review built in.

---

## 🎯 What this project does

This project demonstrates how AI can assist claims handling workflows by:

- Structuring unstructured claim inputs (FNOL)
- Mapping claim facts against policy wording
- Identifying coverage vs exclusions
- Recommending triage decisions
- Supporting (not replacing) human decision-making

---

## ⚙️ Workflow Overview

Claim input → structured intake → policy coverage check → decision recommendation → human validation

---

## 🧱 Agents

### Intake Agent
Extracts structured claim data:
- type of claim
- cause of loss
- estimated loss
- coverage clues

### Policy Agent
Maps claim facts against policy wording:
- identifies relevant coverage sections
- flags applicable exclusions
- assesses coverage plausibility

### Decision Agent
Recommends:
- APPROVE
- ESCALATE
- REJECT

Includes:
- reasoning
- confidence level
- human review requirement
- next operational step

---

## 🧪 Example Scenario

Claim:
Water damage caused by pipe burst due to corrosion

Policy:
Covers water damage but excludes wear and tear, corrosion, and gradual deterioration

Result:
Pending investigation / escalate, with human review required

---

## 🖥️ Interface

This project includes a simple Streamlit interface where a user can:

- paste claim text
- paste policy wording
- run the triage workflow
- review intake, policy, and decision outputs

---

## 🛠️ Tech Stack

- Claude API (Anthropic)
- Python
- Streamlit
- Jupyter Notebook

---

## 💡 Key Design Principles

- Human-in-the-loop by design
- Separation of responsibilities across agents
- Structured and auditable outputs
- Decision support, not automation of final judgement

---

## ⚠️ Disclaimer

This project is a proof of concept.

It is designed to support human review and does not replace claims, legal, compliance, or underwriting judgement.

All claims and policy examples are synthetic and created for demonstration purposes.  
No real client or proprietary data is used.

---

## 🚀 Next Steps

- Add PDF ingestion for claims and policies
- Add risk scoring
- Improve audit logs and output standardisation
- Integrate with claims systems

---

## 👤 Author

Marc Planas Callico  
AI-Enabled Insurance Operations  
MGA · Lloyd’s · Delegated Authority
