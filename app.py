import streamlit as st
import pandas as pd

from data_loader import load_dataset
from preprocessor import preprocess_query
from router import route_query
from relative_engine import process_relative_query
from exact_engine import process_exact_query
from festival_engine import process_festival_query
from extractor import extract_data


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Sales Navigator",
    layout="wide"
)


# =========================
# HEADER
# =========================
st.title("📊 Sales Navigator")
st.write(
    "Upload your sales CSV and query by exact dates, relative dates or festivals."
)


# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "Upload Sales CSV",
    type=["csv"]
)


# =========================
# MAIN FLOW
# =========================
if uploaded_file:

    # =========================
    # SAFE CSV LOAD
    # =========================
    try:
        uploaded_file.seek(0)

        df = pd.read_csv(
            uploaded_file,
            encoding="utf-8-sig",
            sep=",",
            on_bad_lines="skip",
            low_memory=False
        )

    except Exception:

        try:
            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                encoding="latin1",
                sep=",",
                on_bad_lines="skip",
                low_memory=False
            )

        except Exception:

            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                encoding="cp1252",
                sep=",",
                on_bad_lines="skip",
                low_memory=False
            )

    # =========================
    # NORMALIZE COLUMNS
    # =========================
    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    # =========================
    # DEBUG OUTPUT
    # =========================
    st.write(
        "Detected Columns:",
        list(df.columns)
    )

    # =========================
    # VALIDATE DATE COLUMN
    # =========================
    possible_date_cols = [
        "order_date",
        "date",
        "created_at",
        "createdat",
        "transaction_date"
    ]

    detected_date_col = None

    for col in possible_date_cols:
        if col in df.columns:
            detected_date_col = col
            break

    if not detected_date_col:
        st.error(
            f"No valid date column found. Available columns: {list(df.columns)}"
        )
        st.stop()

    # =========================
    # STANDARDIZE DATE COLUMN
    # =========================
    if detected_date_col != "order_date":
        df["order_date"] = df[detected_date_col]

    # =========================
    # TEMP SAVE
    # =========================
    temp_path = "temp_uploaded_sales.csv"

    df.to_csv(
        temp_path,
        index=False
    )

    # =========================
    # LOAD DATASET
    # =========================
    dataset_info = load_dataset(
        temp_path
    )

    st.success(
        "Dataset Loaded Successfully"
    )

    # =========================
    # DATASET METRICS
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Dataset Start",
            str(
                dataset_info["dataset_start_date"].date()
            )
        )

    with col2:
        st.metric(
            "Dataset End",
            str(
                dataset_info["dataset_end_date"].date()
            )
        )

    with col3:
        st.metric(
            "Reference Date",
            str(
                dataset_info["reference_date"].date()
            )
        )

    # =========================
    # QUERY INPUT
    # =========================
    user_query = st.text_input(
        "Enter your sales query",
        placeholder=(
            "e.g. diwali 2025 sales / "
            "last month sales / jan 2025"
        )
    )

    # =========================
    # RUN QUERY
    # =========================
    if st.button("Run Query") and user_query:

        # =========================
        # PREPROCESS
        # =========================
        cleaned_query = preprocess_query(
            user_query
        )

        st.subheader(
            "Preprocessed Query"
        )

        st.write(
            cleaned_query
        )

        # =========================
        # ROUTER
        # =========================
        route_result = route_query(
            cleaned_query
        )

        st.subheader(
            "Router Output"
        )

        st.json(
            route_result
        )

        final_result = None

        # =========================
        # RELATIVE ENGINE
        # =========================
        if route_result["query_class"] in [
            "relative",
            "relative_exact"
        ]:

            final_result = process_relative_query(
                route_result,
                dataset_info
            )

        # =========================
        # EXACT ENGINE
        # =========================
        elif route_result["query_class"] in [
            "exact",
            "exact_multi"
        ]:

            final_result = process_exact_query(
                route_result,
                dataset_info
            )

        # =========================
        # FESTIVAL ENGINE
        # =========================
        elif route_result["query_class"] == "festival":

            final_result = process_festival_query(
                route_result,
                cleaned_query,
                dataset_info
            )

        # =========================
        # UNKNOWN QUERY
        # =========================
        else:

            st.error(
                "Advanced engine for this query type is not built yet."
            )

        # =========================
        # DISPLAY ENGINE RESULT
        # =========================
        if final_result:

            st.subheader(
                "Engine Output"
            )

                        # =========================
            # HUMAN READABLE DATE FORMAT
            # =========================
            display_result = final_result.copy()

            for date_key in [
                "festival_date",
                "start_date",
                "end_date",
                "dataset_start",
                "dataset_end"
            ]:

                if (
                    date_key in display_result and
                    display_result[date_key]
                ):

                    try:
                        display_result[date_key] = pd.to_datetime(
                            display_result[date_key]
                        ).strftime(
                            "%d-%b-%Y"
                        )

                    except Exception:
                        pass

            st.json(
                display_result
            )

            # =========================
            # VALID RESULT
            # =========================
            if final_result.get(
                "valid"
            ):

                extracted_df, file_path = extract_data(
                    final_result,
                    dataset_info
                )

                st.success(
                    f"Extraction successful | Rows Extracted: {len(extracted_df)}"
                )

                st.subheader(
                    "Preview Data"
                )

                st.dataframe(
                    extracted_df.head(50),
                    use_container_width=True
                )

                # =========================
                # DOWNLOAD BUTTON
                # =========================
                with open(
                    file_path,
                    "rb"
                ) as file:

                    st.download_button(
                        label="📥 Download Extracted CSV",
                        data=file,
                        file_name=file_path.split("/")[-1],
                        mime="text/csv"
                    )

            # =========================
            # INVALID RESULT
            # =========================
            else:

                st.warning(
                    final_result.get(
                        "message"
                    )
                )

                if (
                    "dataset_start" in final_result and
                    "dataset_end" in final_result
                ):

                    st.info(
                        f"Dataset available: {final_result['dataset_start']} → {final_result['dataset_end']}"
                    )

                if (
                    "suggestion" in final_result
                ):

                    st.info(
                        f"Suggested query: {final_result['suggestion']}"
                    )