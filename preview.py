from datetime import datetime


def preview_selection(result):

    print("\n===== PREVIEW =====")

    # =========================
    # INVALID
    # =========================
    if not result.get("valid"):
        print("Selection Invalid.")
        print(result.get("message"))

        if "dataset_start" in result and "dataset_end" in result:
            dataset_start_display = datetime.strptime(
                result["dataset_start"],
                "%Y-%m-%d"
            ).strftime("%d-%b-%Y")

            dataset_end_display = datetime.strptime(
                result["dataset_end"],
                "%Y-%m-%d"
            ).strftime("%d-%b-%Y")

            print(
                f"Dataset available: {dataset_start_display} → {dataset_end_display}"
            )

        if "suggestion" in result:
            print(f"Suggested query: {result['suggestion']}")

        return False

    # =========================
    # FORMAT DATES
    # =========================
    start_display = datetime.strptime(
        result["start_date"],
        "%Y-%m-%d"
    ).strftime("%d-%b-%Y")

    end_display = datetime.strptime(
        result["end_date"],
        "%Y-%m-%d"
    ).strftime("%d-%b-%Y")

    # =========================
    # DISPLAY CORE INFO
    # =========================
    if "festival_name" in result:
        print(f"Festival   : {result['festival_name'].title()}")

    if "festival_date" in result:
        festival_display = datetime.strptime(
            result["festival_date"],
            "%Y-%m-%d"
        ).strftime("%d-%b-%Y")

        print(f"Festival Date : {festival_display}")

    print(f"Start Date : {start_display}")
    print(f"End Date   : {end_display}")
    print(f"Message    : {result['message']}")

    # =========================
    # USER CONFIRMATION
    # =========================
    while True:
        print("\nProceed?")
        print("1. Yes")
        print("2. Cancel")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            return True

        elif choice == "2":
            return False

        else:
            print("Invalid choice. Please select 1 or 2.")