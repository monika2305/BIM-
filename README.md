# 🏗️ IFC Semantic Data-Loss Analyzer

A prototype tool developed to detect **semantic data loss** in IFC (Industry Foundation Classes) files during BIM data exchange.

---

## 📌 Overview

Building Information Modeling (BIM) depends on accurate data exchange between different software platforms. However, during IFC export and import, important semantic information such as:

- Element classifications  
- Property sets  
- Metadata  
- Object types  

may be lost or converted into generic proxy elements.

This project provides an automated solution to analyze IFC files, detect semantic inconsistencies, and generate a structured quality assessment report.

---

## 🎯 Problem Statement

During BIM model exchange:

- Semantic data may be lost
- Elements may be converted into proxy objects
- Required property sets may be missing
- There is no clear quality scoring mechanism

These issues reduce model reliability and affect downstream construction workflows.

---

## 💡 Solution

The **IFC Semantic Data-Loss Analyzer** automatically:

- Parses IFC files
- Detects proxy and misclassified elements
- Validates required property sets
- Identifies missing or inconsistent data
- Calculates a semantic quality score
- Generates a structured PDF report

---

## 🛠 Tech Stack

- **Python 3.8+**
- **IfcOpenShell** – IFC parsing
- **Pandas** – Data processing
- **Streamlit / Flask** – Web interface
- **FPDF** – PDF report generation

---

## ⚙️ How It Works

1. User uploads an IFC file  
2. System parses the file using IfcOpenShell  
3. Elements are classified and validated  
4. Semantic checks are performed  
5. Quality score is calculated  
6. PDF report and dashboard output are generated  

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ifc-semantic-analyzer.git

# Navigate to project folder
cd ifc-semantic-analyzer

# Install dependencies
pip install -r requirements.txt


#Run the Application
streamlit run app.py


#System Architecture
User → Upload IFC → Parse → Analyze → Validate → Score → Generate Report → Dashboard Output
