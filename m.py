import streamlit as st
import ifcopenshell
import pandas as pd
from fpdf import FPDF

# -------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_context" not in st.session_state:
    st.session_state.user_context = {}

st.set_page_config(page_title="IFC Semantic Analyzer", layout="wide")

# =====================================================
# LOGIN / CONTEXT PAGE
# =====================================================
if not st.session_state.logged_in:

    st.title("Login")

    name = st.text_input("Your name (optional)")

    role = st.selectbox(
        "Your role",
        [
            "Select an option",
            "Architect",
            "Structural Engineer",
            "BIM Manager",
            "Contractor",
            "Facility Manager",
            "Student / Researcher"
        ]
    )

    domain = st.selectbox(
        "Project domain",
        [
            "Select an option",
            "Architecture",
            "Structural",
            "MEP",
            "Infrastructure",
            "Facility Management"
        ]
    )

    purpose = st.selectbox(
        "Purpose of IFC",
        [
            "Select an option",
            "Design coordination",
            "Compliance",
            "Construction",
            "Handover / FM",
            "Academic / Research"
        ]
    )

    if st.button("Continue"):
        if (
            role == "Select an option"
            or domain == "Select an option"
            or purpose == "Select an option"
        ):
            st.error("Please select all fields.")
        else:
            st.session_state.user_context = {
                "name": name,
                "role": role,
                "domain": domain,
                "purpose": purpose
            }
            st.session_state.logged_in = True
            st.rerun()

    st.stop()   # ⛔ BLOCK ACCESS UNTIL LOGIN

# =====================================================
# IFC UPLOAD & BIM ANALYZER PAGE
# =====================================================

context = st.session_state.user_context

st.title("🏗️ IFC Semantic Data-Loss Analyzer")

st.write("**Role:**", context["role"])
st.write("**Domain:**", context["domain"])
st.write("**Purpose:**", context["purpose"])

# -------------------------------
# FILE UPLOAD
# -------------------------------
uploaded_file = st.file_uploader("Upload IFC file", type=["ifc"])

if uploaded_file:
    with open("temp.ifc", "wb") as f:
        f.write(uploaded_file.getbuffer())

    model = ifcopenshell.open("temp.ifc")
    st.success("IFC file uploaded successfully!")

    # -------------------------------
    # ELEMENT COLLECTION
    # -------------------------------
    walls = model.by_type("IfcWall")
    standard_walls = model.by_type("IfcWallStandardCase")
    doors = model.by_type("IfcDoor")
    windows = model.by_type("IfcWindow")
    proxies = model.by_type("IfcBuildingElementProxy")
    all_elements = model.by_type("IfcProduct")

    total_elements = len(all_elements)
    total_walls = len(walls) + len(standard_walls)
    semantic_elements = total_walls + len(doors) + len(windows)
    proxy_elements = len(proxies)
    other_semantic = max(total_elements - semantic_elements - proxy_elements, 0)

    semantic_pct = (semantic_elements / total_elements) * 100 if total_elements else 0
    proxy_pct = (proxy_elements / total_elements) * 100 if total_elements else 0
    other_pct = (other_semantic / total_elements) * 100 if total_elements else 0

    # -------------------------------
    # SUMMARY METRICS
    # -------------------------------
    st.header("📊 Summary Metrics")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Elements", total_elements)
    c2.metric("Semantic (%)", f"{semantic_pct:.2f}%")
    c3.metric("Proxy (%)", f"{proxy_pct:.2f}%")
    c4.metric("Other Semantic (%)", f"{other_pct:.2f}%")

    # -------------------------------
    # ELEMENT-WISE CLASSIFICATION TABLE
    # -------------------------------
    st.subheader("🧱 Element-wise Classification")
    df_elements = pd.DataFrame({
        "Element Type": ["Walls", "Doors", "Windows", "Proxy Elements", "Other Semantic Elements"],
        "Count": [total_walls, len(doors), len(windows), proxy_elements, other_semantic]
    })
    st.dataframe(df_elements, use_container_width=True)

    # -------------------------------
    # AUTOMATED CONCLUSION & SEVERITY
    # -------------------------------
    st.subheader("🧠 Automated Conclusion")
    if proxy_pct <= 10:
        severity = "LOW"
        st.success("The IFC model preserves semantic representation across all analyzed elements. No semantic degradation detected.")
    elif proxy_pct < 20:
        severity = "MEDIUM"
        st.info("The IFC model largely preserves semantic meaning, with minor semantic degradation observed in a small subset of elements.")
    elif proxy_pct < 50:
        severity = "HIGH"
        st.warning("The IFC model exhibits mixed semantic representation. Several building components are represented as proxy elements.")
    else:
        severity = "CRITICAL"
        st.error("The IFC model shows significant semantic degradation. A large portion of elements are represented as generic proxy objects.")

    st.write("Severity level:", severity)

    # -------------------------------
    # ELEMENT-LEVEL TRACING (PROXY ELEMENTS)
    # -------------------------------
    st.subheader("🔍 Element‑Level Tracing (Proxy Elements)")
    if proxies:
        proxy_data = []
        for proxy in proxies:
            proxy_data.append({
                "Name": proxy.Name if proxy.Name else "Unnamed",
                "GlobalId": proxy.GlobalId,
                "IFC Type": proxy.is_a(),
                "Issue": "Semantic meaning lost (generic proxy)"
            })
        st.dataframe(pd.DataFrame(proxy_data), use_container_width=True)
    else:
        st.write("No proxy elements detected.")

    # -------------------------------
    # WALLS MISSING PSET_WALLCOMMON
    # -------------------------------
    walls_objects = model.by_type("IfcWall")
    walls_missing_pset = []
    for wall in walls_objects:
        has_pset = False
        if hasattr(wall, "IsDefinedBy"):
            for definition in wall.IsDefinedBy:
                if definition.is_a("IfcRelDefinesByProperties"):
                    prop_set = definition.RelatingPropertyDefinition
                    if prop_set and prop_set.is_a("IfcPropertySet"):
                        if prop_set.Name == "Pset_WallCommon":
                            has_pset = True
        if not has_pset:
            walls_missing_pset.append(wall)

    missing_pset_count = len(walls_missing_pset)
    st.subheader("Walls Missing Pset_WallCommon")
    st.write("Count:", missing_pset_count)

    if missing_pset_count == 0:
        st.success("All walls contain Pset_WallCommon.")
    else:
        pset_data = []
        for wall in walls_missing_pset:
            pset_data.append({
                "Wall Name": wall.Name if wall.Name else "Unnamed",
                "GlobalId": wall.GlobalId,
                "Issue": "Pset_WallCommon missing"
            })
        st.dataframe(pd.DataFrame(pset_data), use_container_width=True)

    # -------------------------------
    # PDF REPORT FUNCTION
    # -------------------------------
    def generate_pdf(file_path="IFC_Analysis_Report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "IFC Semantic Analysis Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, f"User Name: {context.get('name', 'N/A')}")
        pdf.multi_cell(0, 8, f"Role: {context.get('role', 'N/A')}")
        pdf.multi_cell(0, 8, f"Domain: {context.get('domain', 'N/A')}")
        pdf.multi_cell(0, 8, f"Purpose: {context.get('purpose', 'N/A')}")
        pdf.ln(5)

        pdf.multi_cell(0, 8, "Summary Metrics:")
        pdf.multi_cell(0, 8, f"Total Elements: {total_elements}")
        pdf.multi_cell(0, 8, f"Semantic Elements: {semantic_elements}")
        pdf.multi_cell(0, 8, f"Proxy Elements: {proxy_elements}")
        pdf.multi_cell(0, 8, f"Other Semantic Elements: {other_semantic}")
        pdf.multi_cell(0, 8, f"Semantic %: {semantic_pct:.2f}%")
        pdf.multi_cell(0, 8, f"Proxy %: {proxy_pct:.2f}%")
        pdf.multi_cell(0, 8, f"Other %: {other_pct:.2f}%")
        pdf.multi_cell(0, 8, f"Severity Level: {severity}")
        pdf.ln(5)

        if proxies:
            pdf.multi_cell(0, 8, "Proxy Elements Detail:")
            for i, proxy in enumerate(proxies, start=1):
                name = proxy.Name if proxy.Name else "Unnamed"
                pdf.multi_cell(0, 8,
                    f"{i}. Name: {name} | Type: {proxy.is_a()} | GlobalId: {proxy.GlobalId} | Issue: Semantic meaning lost (generic proxy)")
            pdf.ln(5)

        if missing_pset_count > 0:
            pdf.multi_cell(0, 8, "Walls Missing Pset_WallCommon:")
            for i, wall in enumerate(walls_missing_pset, start=1):
                pdf.multi_cell(0, 8,
                    f"{i}. Wall Name: {wall.Name if wall.Name else 'Unnamed'} | GlobalId: {wall.GlobalId} | Issue: Pset_WallCommon missing")

        pdf.output(file_path)
        return file_path

    # -------------------------------
    # PDF DOWNLOAD BUTTON
    # -------------------------------
    if st.button("📄 Download PDF Report"):
        pdf_path = generate_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Click to download PDF",
                data=f,
                file_name="IFC_Analysis_Report.pdf",
                mime="application/pdf"
            )
