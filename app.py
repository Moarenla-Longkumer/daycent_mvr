cat > app.py <<'PY'
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(layout="wide")
st.title("DayCent QA/QC Dashboard")

inv_path = Path("qaqc_inventory.csv")
if not inv_path.exists():
    st.error("Missing qaqc_inventory.csv. Run inventory step first.")
    st.stop()

df = pd.read_csv(inv_path).fillna("")
sites = sorted(df["site"].tolist())

c1, c2 = st.columns([2,1])
site = c1.selectbox("Select site", sites)
show_failed = c2.checkbox("Show only failed rows", value=False)

view = df[df["site"] == site].copy()
row = view.iloc[0]

st.subheader(f"Site: {site}")
st.write({
    "SOMSC": row["somsc_result"],
    "Biomass": row["biomass_result"],
    "N2O": row["n2o_result"],
    "Biomass livec plots": int(row["biomass_livec_plot_count"]) if str(row["biomass_livec_plot_count"]).isdigit() else row["biomass_livec_plot_count"],
    "N2O summary plots": int(row["n2o_summary_plot_count"]) if str(row["n2o_summary_plot_count"]).isdigit() else row["n2o_summary_plot_count"],
})

def show_img(path_str, label):
    p = Path(path_str)
    if p.exists():
        st.image(str(p), caption=label, use_container_width=True)
    else:
        st.info(f"{label}: not found")

tab1, tab2, tab3 = st.tabs(["SOMSC", "Biomass", "N2O"])

with tab1:
    show_img(row["somsc_spinup_png"], "somsc_timeseries_spinup.png")
    show_img(row["somsc_exp_png"], "somsc_timeseries_exp.png")
    show_img(row["somsc_scatter_png"], "observed_vs_modeled_somsc.png")
    if Path(row["somsc_summary"]).exists():
        st.text(Path(row["somsc_summary"]).read_text(encoding="utf-8", errors="replace"))

with tab2:
    show_img(row["biomass_scatter_png"], "observed_vs_modeled_biomass.png")
    if Path(row["biomass_summary"]).exists():
        st.text(Path(row["biomass_summary"]).read_text(encoding="utf-8", errors="replace"))

with tab3:
    show_img(row["n2o_scatter_png"], "observed_vs_modeled_n2o.png")
    if Path(row["n2o_summary"]).exists():
        st.text(Path(row["n2o_summary"]).read_text(encoding="utf-8", errors="replace"))
