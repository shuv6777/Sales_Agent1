from data_loader import load_dataset
from preprocessor import preprocess_query
from router import route_query
from relative_engine import process_relative_query
from exact_engine import process_exact_query
from preview import preview_selection
from extractor import extract_data
from festival_engine import process_festival_query


def main():
    # Load dataset
    csv_path = "sales.csv"   # Change if needed
    dataset_info = load_dataset(csv_path)

    print("\n===== DATASET LOADED SUCCESSFULLY =====")
    print(f"Dataset Start Date : {dataset_info['dataset_start_date'].date()}")
    print(f"Dataset End Date   : {dataset_info['dataset_end_date'].date()}")
    print(f"Reference Date     : {dataset_info['reference_date'].date()}")

    while True:
        print("\n==============================")
        user_query = input("Enter your sales query (or type 'exit'): ")

        if user_query.lower() == "exit":
            print("Exiting Sales Agent...")
            break

        # =========================
        # PREPROCESS
        # =========================
        cleaned_query = preprocess_query(user_query)

        print(f"\nPreprocessed Query: {cleaned_query}")

        # =========================
        # ROUTER
        # =========================
        route_result = route_query(cleaned_query)

        print("\n===== ROUTER OUTPUT =====")
        for key, value in route_result.items():
            print(f"{key}: {value}")

        # =========================
        # RELATIVE ENGINE
        # =========================
        if route_result["query_class"] in ["relative", "relative_exact"]:
            relative_result = process_relative_query(route_result, dataset_info)

            print("\n===== RELATIVE ENGINE OUTPUT =====")
            for key, value in relative_result.items():
                print(f"{key}: {value}")

            confirmed = preview_selection(relative_result)

            if confirmed:
                extracted_df = extract_data(relative_result, dataset_info)

                print("\n===== EXTRACTION SUCCESS =====")
                print(f"Rows Extracted: {len(extracted_df)}")
                print(extracted_df.head())

            else:
                print("\nSelection cancelled.")

        # =========================
        # EXACT ENGINE
        # =========================
        elif route_result["query_class"] in ["exact", "exact_multi"]:
            exact_result = process_exact_query(route_result, dataset_info)

            print("\n===== EXACT ENGINE OUTPUT =====")
            for key, value in exact_result.items():
                print(f"{key}: {value}")

            confirmed = preview_selection(exact_result)

            if confirmed:
                extracted_df = extract_data(exact_result, dataset_info)

                print("\n===== EXTRACTION SUCCESS =====")
                print(f"Rows Extracted: {len(extracted_df)}")
                print(extracted_df.head())

            else:
                print("\nSelection cancelled.")

                # =========================
        # FESTIVAL ENGINE
        # =========================
        elif route_result["query_class"] == "festival":
            festival_result = process_festival_query(
                route_result,
                cleaned_query,
                dataset_info
            )

            print("\n===== FESTIVAL ENGINE OUTPUT =====")
            for key, value in festival_result.items():
                print(f"{key}: {value}")

            confirmed = preview_selection(festival_result)

            if confirmed:
                extracted_df, file_path = extract_data(festival_result, dataset_info)

                print("\n===== EXTRACTION SUCCESS =====")
                print(f"Rows Extracted: {len(extracted_df)}")
                print(f"Saved File: {file_path}")
                print(extracted_df.head())

            else:
                print("\nSelection cancelled.")

        # =========================
        # SEASONAL / UNKNOWN
        # =========================
        else:
            print("\nAdvanced engine for this query type is not built yet.")


if __name__ == "__main__":
    main()