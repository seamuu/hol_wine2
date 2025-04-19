import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches  # For legend handles
from oauth2client.service_account import ServiceAccountCredentials

# --- Gemini AI (older approach) ---
import google.generativeai as genai

# --------------------------------------------
#            GOOGLE SHEETS SETUP
# --------------------------------------------
SHEET_NAME = "hol_wine_tasting"  # Replace if your sheet is named differently
creds_dict = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)


# Set up scope and authorize gspread
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
gc = gspread.authorize(credentials)
sheet = gc.open(SHEET_NAME).sheet1

# Ensure headers exist
headers = sheet.row_values(1)
expected_headers = ["Name", "Wine", "Rating", "Category", "Taste"]
if headers != expected_headers:
    sheet.insert_row(expected_headers, 1)

# --------------------------------------------
#            GEMINI / GENAI SETUP
# --------------------------------------------
# 🔑 Provide your Gemini API key directly
GEMINI_API_KEY = "AIzaSyDyCYpojKC3jcMD7YFG44_KiMhj-vpMUnA"
genai.configure(api_key=GEMINI_API_KEY)

def generate_summary(prompt):
    """Calls Google Gemini AI (old `genai` style) to generate a summary."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        if response.text:
            return response.text.strip()
        return "No response generated."
    except Exception as e:
        return f"Could not generate a summary due to an error: {e}"

# --------------------------------------------
#            STREAMLIT MAIN APP
# --------------------------------------------
st.set_page_config(
    page_title="Wine Tasting & Ratings",
    page_icon="🍷",
    layout="centered"
)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Lora&display=swap" rel="stylesheet">

<style>
/* Use Lora font for everything */
html, body, [data-testid="stAppViewContainer"], [class*="css"] {
    font-family: 'Lora', serif !important;
}

/* Full background to beige */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #fdf6e3 !important;
}

/* Remove dark Streamlit top bar */
header {
    background-color: transparent !important;
}

/* Text color to grey */
* {
    color: #4b4b4b !important;
}

/* Inputs, dropdowns, sliders etc. */
input, textarea, select, .stTextInput > div > div > input, .stSlider, .stSelectbox {
    background-color: #fff8e1 !important;
    color: #4b4b4b !important;
    border: 1px solid #d3cfc5 !important;
    border-radius: 6px !important;
}

/* Multiselect pills */
.css-1n76uvr, .css-1wa3eu0-MultiValue {
    background-color: #fcebd6 !important;
    color: #4b4b4b !important;
    border-radius: 20px !important;
}

/* Expander background */
details {
    background-color: #f8f1dc !important;
}

/* Form submit button styling */
button[kind="primary"] {
    background-color: #8b0000 !important;
    color: white !important;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
}
</style>
""", unsafe_allow_html=True)


st.title("Cindy's Wine Bar 🍇")
st.markdown("You're a team of professional wine tasters. Cindy has hired your consultancy to help her build a new wine bar menu. "
           "She's flown you to her new bar in the Amalfi coast and today your assignment begins. " \
           "You will taste wines and rate them, tell her what price she should charge and help her write the tasting notes.")

st.image("cindy_wine_bar.jpg", caption="Help Cindy taste wines and build her new wine bar menu 🍇",  use_container_width=True)
# Create two tabs
tab1, tab2 = st.tabs(["Help Cindy", "Cindy's mainframe"])

# --------------------------
#           TAB 1
# --------------------------
import streamlit as st

with tab1:
    # Show Cindy at the top

    #  st.subheader("Rate a Wine & Add Tasting Notes")
    st.markdown("---")

    wine_options = ["Pinot Gris", "Gewürztraminer", "Riesling"]

    with st.form("input_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            name_options = ["Seamus", "Aleks", "Beth", "Becky",
                            "Ella", "Hannah", "Knut", "Moon"
                            "Jack", "Maria", "Guro", "Chris",
                            "Luke", "Olwyn"]  # or load dynamically
            name = st.selectbox("Select Your Name", name_options, key="user_name_input")

        with col2:
            wine_options = ["Prosecco", "Cremant", "Italian natrual", "Bolly"]
            wine = st.selectbox("Select a Wine", wine_options)

        col3, col4 = st.columns([1, 2])
        with col3:
            rating = st.slider("Rate the wine (1–10)", 1, 10, 5)

            price = st.slider("How much € would you pay for a glass at Cindy's wine bar?", 0, 30, 10)

        with col4:
            st.markdown("### Tasting Notes")

            # Categories and their options
            categories = {
                "Fruits": ["Green Apple", "Pear", "Lemon", "Lime", "White Peach", "Apricot"],
                "Floral": ["Elderflower", "Honeysuckle", "Acacia", "Chamomile"],
                "Yeasty / Bready": ["Brioche", "Toast", "Biscuit", "Pastry", "Bread Dough"],
                "Mineral": ["Chalk", "Flint", "Wet Stone", "Saline"],
                "Other": ["Honey", "Almond", "Marzipan", "Cream", "Vanilla"]
            }


            selected_notes = []

            for cat, options in categories.items():
                with st.expander(cat):
                    st.markdown(f"**{cat} aromas**")
                    cols = st.columns(3)  # Split options across 3 columns

                    for i, option in enumerate(options):
                        col = cols[i % 3]
                        with col:
                            if st.checkbox(option, key=f"{cat}_{option}"):
                                selected_notes.append(option)
            custom_notes = st.text_area(
    "Anything else you tasted?",
    placeholder="Type your own tasting notes here…"
)

        submit_button = st.form_submit_button("Submit")

if submit_button:
    if not name.strip():
        st.warning("Please enter a valid name before submitting.")
    else:
        # Save rating
        sheet.append_row([name.strip(), wine, rating, "Rating", ""])

        # Save price
        sheet.append_row([name.strip(), wine, price, "Price", ""])

        # Save selected tasting notes (from checkboxes)
        for taste in selected_notes:
            sheet.append_row([name.strip(), wine, "", "Taste", taste.strip()])

        # Save custom tasting notes (each line as a new row)
        if custom_notes.strip():
            for line in custom_notes.splitlines():
                if line.strip():
                    sheet.append_row([name.strip(), wine, "", "Taste", line.strip()])

        st.success(f"Thank you, {name.strip()}! Your inputs for {wine} have been recorded. 🍷")
        st.rerun()

import pandas as pd
import plotly.graph_objects as go

# Load data from Google Sheet into a DataFrame
records = sheet.get_all_records()
df = pd.DataFrame(records)

with tab2:
    st.subheader("Wine Rating Insights 📊")

    # Load raw data
    df = pd.DataFrame(sheet.get_all_records())

    # Drop duplicates
    df = df.drop_duplicates()

    # Keep last entry per person/wine/category
    df = df.sort_values(by=["Name", "Wine", "Category"]).drop_duplicates(
        subset=["Name", "Wine", "Category"], keep="last"
    )

    # Only keep Rating and Price categories
    df_filtered = df[df["Category"].isin(["Rating", "Price"])].copy()

    # Store the value (from the Rating column) as numeric
    df_filtered["Value"] = pd.to_numeric(df_filtered["Rating"], errors="coerce")

    # Group directly per wine + category
    avg_summary = (
        df_filtered.groupby(["Wine", "Category"])["Value"]
        .mean()
        .unstack()
        .round(2)
        .reset_index()
        .rename(columns={"Rating": "Avg Rating", "Price": "Avg Price"})
    )

    # Display 2x2 grid
    st.markdown("### Wine Overview")
    cols = st.columns(2)
    for i, row in avg_summary.iterrows():
        with cols[i % 2]:
            st.markdown(f"""
            <div style='border: 1px solid #ccc; border-radius: 10px; padding: 16px; background-color: #fff8e1; margin-bottom: 20px;'>
                <h4 style='margin-bottom: 0;'>{row['Wine']}</h4>
                <p style='margin: 4px 0;'>⭐ Avg. Rating: <strong>{row['Avg Rating']}</strong></p>
                <p style='margin: 4px 0;'>💶 Avg. Price: <strong>{row['Avg Price']} €</strong></p>
            </div>
            """, unsafe_allow_html=True)

    import plotly.express as px

    # Get only rows with Rating or Price
    df_plot = df[df["Category"].isin(["Rating", "Price"])].copy()

    # Ensure values are numeric
    df_plot["Value"] = pd.to_numeric(df_plot["Rating"], errors="coerce")

    # Pivot: one row per (Name, Wine) with Rating and Price
    scatter_data = df_plot.pivot_table(
        index=["Name", "Wine"],
        columns="Category",
        values="Value",
        aggfunc="first"
    ).reset_index()

    # Drop incomplete rows
    scatter_data = scatter_data.dropna(subset=["Rating", "Price"])

    # Create scatter plot
    fig = px.scatter(
        scatter_data,
        x="Rating",
        y="Price",
        color="Wine",
        hover_data=["Name"],
        template="simple_white",
        height=500
    )

    fig.update_layout(
        title="How Much People Would Pay vs How Much They Liked It",
        xaxis_title="Rating (1–10)",
        yaxis_title="Price (€)",
    )

    st.plotly_chart(fig, use_container_width=True)

    # specific wine analysis

    import plotly.express as px

    # Filter to selected wine
    st.markdown("### Dive Into a Specific Wine")
    wine_list = sorted(df["Wine"].dropna().unique())
    selected_wine = st.selectbox("Choose a wine", wine_list)
    wine_df = df[df["Wine"] == selected_wine]

    # Filter only Rating and Price rows
    filtered = wine_df[wine_df["Category"].isin(["Rating", "Price"])].copy()
    filtered["Value"] = pd.to_numeric(filtered["Rating"], errors="coerce")

    # Pivot: one row per user with both rating and price
    scatter_data = filtered.pivot_table(
        index="Name",
        columns="Category",
        values="Value",
        aggfunc="first"
    ).reset_index()

    # Remove rows missing either
    scatter_data = scatter_data.dropna(subset=["Rating", "Price"])

    # Build figure
    fig = px.scatter(
        scatter_data,
        x="Rating",
        y="Price",
        hover_name="Name",
        marginal_x="histogram",
        marginal_y="histogram",
        template="simple_white",
        title=f"{selected_wine} — Ratings vs Price"
    )

    # Force one bin per integer for rating, and wide bins for price
    fig.update_traces(
        selector=dict(type='histogram'),
        xbins=dict(start=0.5, end=10.5, size=1),  # 1 bin per rating
        ybins=dict(start=0, end=30, size=5),      # bins of 5 for price
    )

    fig.update_layout(
        xaxis_title="Rating (1–10)",
        yaxis_title="Price (€)",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


    from collections import Counter
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    # Re-fetch raw data to get all tasting notes (not deduplicated)
    df_raw = pd.DataFrame(sheet.get_all_records())

    # Filter tasting notes for the selected wine
    taste_notes = df_raw[
        (df_raw["Category"] == "Taste") & (df_raw["Wine"] == selected_wine)
    ]["Taste"].dropna().tolist()

    # Clean and normalize notes
    cleaned_notes = [
        note.replace("\u00a0", " ")       # Fix non-breaking spaces
            .replace(" ", " ")            # Extra invisible space
            .strip()
            .title()
        for note in taste_notes
        if isinstance(note, str) and note.strip()
    ]

    # Count frequencies
    note_freq = Counter(cleaned_notes)

    # Generate and show word cloud
    if note_freq:
        wc = WordCloud(
            width=800,
            height=400,
            background_color="#fdf6e3",
            colormap="Dark2"
        ).generate_from_frequencies(note_freq)

        st.markdown("### Tasting Notes Word Cloud")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info(f"No tasting notes for {selected_wine} yet.")
