import pandas as pd
import argparse
from datetime import datetime, timedelta

# Load the data into a DataFrame
df = pd.read_csv("data/search_results.csv")

# Convert 'date' column to datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Create new columns based on the job titles and descriptions
df["Remote"] = df["title"].str.contains("Remote", case=False)
df["Software Engineer"] = df["title"].str.contains("Engineer", case=False)
df["Developer"] = df["title"].str.contains("Developer", case=False)
df["Experience Level"] = df["title"].apply(
    lambda x: (
        "Junior"
        if "Junior" in x
        else ("Senior" if "Senior" in x else ("Staff" if "Staff" in x else "All"))
    )
)
df["Job Type"] = df["title"].apply(
    lambda x: (
        "Cloud"
        if "Cloud" in x
        else (
            "AI"
            if "AI" in x
            else ("Data Scientist" if "Data Scientist" in x else "All")
        )
    )
)


# Function to filter DataFrame in ascending order
def filter_asc(column_name):
    return df.sort_values(by=column_name, ascending=True)


# Function to filter DataFrame in descending order
def filter_desc(column_name):
    return df.sort_values(by=column_name, ascending=False)


def main():
    parser = argparse.ArgumentParser(description="Filter and sort job listings.")
    parser.add_argument(
        "--remote",
        choices=["yes", "no", "all"],
        default="all",
        help="Filter for remote jobs",
    )
    parser.add_argument(
        "--role",
        choices=["Software Engineer", "Developer", "all"],
        default="all",
        help="Filter by role",
    )
    parser.add_argument(
        "--experience",
        choices=["Junior", "Senior", "Staff", "all"],
        default="all",
        help="Filter by experience level",
    )
    parser.add_argument(
        "--job_type",
        choices=["Cloud", "AI", "Data Scientist", "all"],
        default="all",
        help="Filter by job type",
    )
    parser.add_argument(
        "--sort",
        choices=["date", "title", "none"],
        default="none",
        help="Column to sort by",
    )
    parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default="desc",
        help="Sort order (default: descending)",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit the number of results"
    )
    parser.add_argument(
        "--date_after",
        type=str,
        default=None,
        help="Filter jobs after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--days_ago", type=int, default=None, help="Filter jobs from the last N days"
    )

    args = parser.parse_args()

    # Apply filters
    filtered_df = df.copy()
    if args.remote != "all":
        filtered_df = filtered_df[filtered_df["Remote"] == (args.remote == "yes")]
    if args.role != "all":
        filtered_df = filtered_df[filtered_df[args.role]]
    if args.experience != "all":
        filtered_df = filtered_df[
            filtered_df["Experience Level"].isin([args.experience, "All"])
        ]
    if args.job_type != "all":
        filtered_df = filtered_df[filtered_df["Job Type"].isin([args.job_type, "All"])]

    # Apply date filter
    if args.date_after:
        date_after = datetime.strptime(args.date_after, "%Y-%m-%d")
        filtered_df = filtered_df[filtered_df["date"] >= date_after]
    elif args.days_ago:
        date_after = datetime.now() - timedelta(days=args.days_ago)
        filtered_df = filtered_df[filtered_df["date"] >= date_after]

    # Sort the DataFrame
    if args.sort != "none":
        filtered_df = filtered_df.sort_values(
            by=args.sort, ascending=(args.order == "asc")
        )

    # Limit the number of results if specified
    if args.limit:
        filtered_df = filtered_df.head(args.limit)

    # Display results
    print(filtered_df[["title", "date", "description", "link"]])

    # Optionally, save the filtered results to a new CSV file
    filtered_df.to_csv("data/filtered_results.csv", index=False)
    print(f"Filtered results saved to 'data/filtered_results.csv'")


if __name__ == "__main__":
    main()
