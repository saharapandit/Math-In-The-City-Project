
# Visualization - using master_2020.csv


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 1. SETTINGS

INPUT_FILE = "master_2020.csv"
OUTPUT_FOLDER = "part4_outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")


# 2. LOAD DATA

df = pd.read_csv(INPUT_FILE)

print("Dataset loaded.")
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())


# 3. KEEP ONLY COLUMNS NEEDED

viz_cols = [
    "GEOID",
    "NAME",
    "LST_C",
    "NDVI",
    "NDBI",
    "median_household_income",
    "poverty_rate_pct",
    "renter_occupied_pct"
]

df_viz = df[viz_cols].copy()


# 4. CLEAN NUMERIC COLUMNS

numeric_cols = [
    "LST_C",
    "NDVI",
    "NDBI",
    "median_household_income",
    "poverty_rate_pct",
    "renter_occupied_pct"
]

for col in numeric_cols:
    df_viz[col] = pd.to_numeric(df_viz[col], errors="coerce")

# Remove impossible values
df_viz.loc[(df_viz["NDVI"] < -1) | (df_viz["NDVI"] > 1), "NDVI"] = np.nan
df_viz.loc[(df_viz["NDBI"] < -1) | (df_viz["NDBI"] > 1), "NDBI"] = np.nan
df_viz.loc[(df_viz["poverty_rate_pct"] < 0) | (df_viz["poverty_rate_pct"] > 100), "poverty_rate_pct"] = np.nan
df_viz.loc[(df_viz["renter_occupied_pct"] < 0) | (df_viz["renter_occupied_pct"] > 100), "renter_occupied_pct"] = np.nan
df_viz.loc[df_viz["median_household_income"] < 0, "median_household_income"] = np.nan

# Drop rows missing needed values
df_viz = df_viz.dropna(subset=numeric_cols).copy()

print("\nCleaned visualization dataset shape:", df_viz.shape)
print("\nMissing values after cleaning:")
print(df_viz[numeric_cols].isna().sum())

# Save cleaned visualization dataset
df_viz.to_csv(os.path.join(OUTPUT_FOLDER, "master_2020_viz_cleaned.csv"), index=False)


# 5. SUMMARY STATISTICS

summary_stats = df_viz[numeric_cols].describe().T
summary_stats["median"] = df_viz[numeric_cols].median()
summary_stats = summary_stats[["count", "mean", "median", "std", "min", "max"]]

print("\nSummary statistics:")
print(summary_stats)

summary_stats.to_csv(os.path.join(OUTPUT_FOLDER, "summary_statistics_part4.csv"))


# 6. SCATTER PLOT FUNCTION

def make_scatterplot(data, x_var, y_var, hue_var, title, filename, palette="viridis"):
    plt.figure(figsize=(10, 7))

    sns.scatterplot(
        data=data,
        x=x_var,
        y=y_var,
        hue=hue_var,
        palette=palette,
        s=90,
        edgecolor="black",
        alpha=0.85
    )

    sns.regplot(
        data=data,
        x=x_var,
        y=y_var,
        scatter=False,
        color="red",
        line_kws={"linewidth": 2}
    )

    plt.title(title, fontsize=16, weight="bold")
    plt.xlabel(x_var.replace("_", " ").title())
    plt.ylabel("Land Surface Temperature (°C)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, filename), dpi=300, bbox_inches="tight")
    plt.show()


# 7. CREATE SCATTER PLOTS


# 1. LST vs NDVI
make_scatterplot(
    data=df_viz,
    x_var="NDVI",
    y_var="LST_C",
    hue_var="poverty_rate_pct",
    title="LST vs NDVI (colored by Poverty Rate)",
    filename="lst_vs_ndvi.png",
    palette="viridis"
)

# 2. LST vs Income
make_scatterplot(
    data=df_viz,
    x_var="median_household_income",
    y_var="LST_C",
    hue_var="poverty_rate_pct",
    title="LST vs Median Household Income (colored by Poverty Rate)",
    filename="lst_vs_income.png",
    palette="viridis"
)

# 3. LST vs Poverty Rate
make_scatterplot(
    data=df_viz,
    x_var="poverty_rate_pct",
    y_var="LST_C",
    hue_var="renter_occupied_pct",
    title="LST vs Poverty Rate (colored by Renter Occupancy)",
    filename="lst_vs_poverty.png",
    palette="magma"
)

# 4. LST vs Renter Occupancy
make_scatterplot(
    data=df_viz,
    x_var="renter_occupied_pct",
    y_var="LST_C",
    hue_var="median_household_income",
    title="LST vs Renter Occupancy (colored by Income)",
    filename="lst_vs_renters.png",
    palette="coolwarm"
)


# 8. PEARSON CORRELATION HEATMAP

corr_vars = [
    "LST_C",
    "NDVI",
    "NDBI",
    "median_household_income",
    "poverty_rate_pct",
    "renter_occupied_pct"
]

pearson_corr = df_viz[corr_vars].corr(method="pearson")
pearson_corr.to_csv(os.path.join(OUTPUT_FOLDER, "pearson_correlation_matrix.csv"))

plt.figure(figsize=(10, 8))
sns.heatmap(
    pearson_corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5,
    square=True
)
plt.title("Pearson Correlation Heatmap", fontsize=16, weight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "pearson_correlation_heatmap.png"), dpi=300, bbox_inches="tight")
plt.show()


# 9. SPEARMAN CORRELATION HEATMAP

spearman_corr = df_viz[corr_vars].corr(method="spearman")
spearman_corr.to_csv(os.path.join(OUTPUT_FOLDER, "spearman_correlation_matrix.csv"))

plt.figure(figsize=(10, 8))
sns.heatmap(
    spearman_corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5,
    square=True
)
plt.title("Spearman Correlation Heatmap", fontsize=16, weight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "spearman_correlation_heatmap.png"), dpi=300, bbox_inches="tight")
plt.show()


# 10. OPTIONAL: HISTOGRAMS

for col in numeric_cols:
    plt.figure(figsize=(8, 6))
    sns.histplot(df_viz[col], kde=True, bins=15)
    plt.title(f"Distribution of {col.replace('_', ' ').title()}", fontsize=14, weight="bold")
    plt.xlabel(col.replace("_", " ").title())
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, f"hist_{col}.png"), dpi=300, bbox_inches="tight")
    plt.show()

print("\nDone. All Part 4 outputs were saved in the folder:")
print(OUTPUT_FOLDER)