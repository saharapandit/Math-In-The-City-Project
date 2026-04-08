from pathlib import Path

import pandas as pd


INPUT_PATH = Path("master_2020.csv")
OUTPUT_PATH = Path("master_2020_clean.csv")


def main() -> None:
    df_raw = pd.read_csv(INPUT_PATH)
    df_clean = df_raw.copy(deep=True)

    institutional_mask = df_clean["median_household_income"] == -666666666
    df_clean = df_clean.loc[~institutional_mask].copy()

    tract6_mask = df_clean["NAME"].str.contains("Census Tract 6,", regex=False, na=False)
    df_clean.loc[tract6_mask, "elderly_living_alone_pct"] = df_clean.loc[
        tract6_mask, "elderly_living_alone_pct"
    ].fillna(0)

    remaining_nans = int(df_clean.isna().sum().sum())
    negative_income_count = int((df_clean["median_household_income"] < 0).sum())

    print(f"Cleaned dataframe shape: {df_clean.shape}")
    print(f"Remaining NaN values: {remaining_nans}")
    print(f"Negative median_household_income values remaining: {negative_income_count}")

    df_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved cleaned data to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
