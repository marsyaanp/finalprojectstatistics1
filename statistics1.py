import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Survey Data Analysis", layout="wide")

# ================= LANGUAGE ====================
lang = st.sidebar.selectbox("Language / Bahasa", ["English", "Indonesia"])

TEXT = {
    "English": {
        "title": "Survey Data Analysis Web App",
        "desc": "This web app performs descriptive and association analysis on survey data.",
        "upload": "Upload CSV File",
        "x": "Select X Variables",
        "y": "Select Y Variables",
        "desc_stat": "Descriptive Statistics",
        "assoc": "Association Analysis",
        "method": "Correlation Method",
        "scatter": "Scatter Plot"
    },
    "Indonesia": {
        "title": "Aplikasi Analisis Data Survei",
        "desc": "Aplikasi ini melakukan analisis deskriptif dan analisis asosiasi pada data survei.",
        "upload": "Unggah File CSV",
        "x": "Pilih Variabel X",
        "y": "Pilih Variabel Y",
        "desc_stat": "Statistik Deskriptif",
        "assoc": "Analisis Asosiasi",
        "method": "Metode Korelasi",
        "scatter": "Diagram Pencar"
    }
}

# ================= FUNCTIONS ===================
def pearson_corr(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    return np.corrcoef(x, y)[0, 1]


def spearman_corr(x, y):
    rx = pd.Series(x).rank()
    ry = pd.Series(y).rank()
    return pearson_corr(rx, ry)

# ================= UI ==========================
st.title(TEXT[lang]["title"])
st.write(TEXT[lang]["desc"])

file = st.file_uploader(TEXT[lang]["upload"], type=["csv"])

# ================= MAIN ========================
if file is not None:
    try:
        df = pd.read_csv(file, sep=None, engine="python")

        # 🔧 TAMBAHAN PENTING
        # Paksa semua kolom yang bisa jadi angka → numerik
        df = df.apply(
            lambda col: pd.to_numeric(
                col.astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            )
        )

    except Exception as e:
        st.error(f"Gagal membaca file CSV: {e}")
        st.stop()

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # ✅ SEKARANG ANGKA TERDETEKSI
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        st.error("File CSV tidak mengandung kolom numerik.")
        st.stop()

    x_cols = st.multiselect(TEXT[lang]["x"], numeric_cols)
    y_cols = st.multiselect(TEXT[lang]["y"], numeric_cols)

    if x_cols and y_cols:

        df["X_total"] = df[x_cols].mean(axis=1)
        df["Y_total"] = df[y_cols].mean(axis=1)

        # -------- DESCRIPTIVE --------
        st.subheader(TEXT[lang]["desc_stat"])

        desc = pd.DataFrame({
            "Mean": df[x_cols + y_cols].mean(),
            "Median": df[x_cols + y_cols].median(),
            "Min": df[x_cols + y_cols].min(),
            "Max": df[x_cols + y_cols].max(),
            "Std": df[x_cols + y_cols].std()
        })

        st.dataframe(desc.round(3))

        # -------- ASSOCIATION --------
        st.subheader(TEXT[lang]["assoc"])

        method = st.radio(TEXT[lang]["method"], ["Pearson", "Spearman"])

        if method == "Pearson":
            r = pearson_corr(df["X_total"], df["Y_total"])
        else:
            r = spearman_corr(df["X_total"], df["Y_total"])

        st.write(f"**Correlation (r):** {r:.3f}")

        # -------- SCATTER --------
        st.subheader(TEXT[lang]["scatter"])
        fig, ax = plt.subplots()
        ax.scatter(df["X_total"], df["Y_total"])
        ax.set_xlabel("X_total")
        ax.set_ylabel("Y_total")
        st.pyplot(fig)

    else:
        st.warning("Pilih minimal satu variabel X dan satu variabel Y.")

else:
    st.info("Upload file CSV untuk memulai analisis.")


