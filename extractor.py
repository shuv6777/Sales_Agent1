import os


def extract_data(result, dataset_info):
    if not result.get("valid"):
        return None, None

    df = dataset_info["df"]

    start_date = result["start_date"]
    end_date = result["end_date"]

    filtered_df = df[
        (df["order_date"] >= start_date) &
        (df["order_date"] <= end_date)
    ]

    # Create exports folder
    export_folder = "exports"
    os.makedirs(export_folder, exist_ok=True)

    # File name
    if "festival_name" in result:
        file_name = f"{result['festival_name']}_{result['year']}_sales.csv"

    else:
        file_name = f"extracted_{start_date}_to_{end_date}.csv"
    file_path = os.path.join(export_folder, file_name)

    # Save CSV
    filtered_df.to_csv(file_path, index=False)

    return filtered_df, file_path