import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned dataset
df = pd.read_csv('master_2020_2025.csv')

# Key Variables for summary statistics
key_vars = [
    'LST_C', 'NDVI', 'NDBI',
    'median_household_income', 'poverty_rate_pct', 'renter_occupied_pct'
]

# Compute summary statistics (mean, median, std, min, max)
summary_stats = df[key_vars].agg(['mean', 'median', 'std', 'min', 'max']).transpose()

# Print summary statistics nicely
print("\nSummary Statistics for Key Variables:\n")
print(summary_stats)

# Set up the matplotlib figure size for histograms
plt.figure(figsize=(15, 10))


for i, var in enumerate(key_vars, 1):
    plt.subplot(2, 3, i)
    
    # 1. Define the data for this specific variable
    data_to_plot = df[var].dropna()
    
    # 2. Apply filtering ONLY to socioeconomic variables (Income, Poverty, Renter %)
    # This leaves LST, NDVI, and NDBI alone so their negative values stay!
    if var in ['median_household_income', 'poverty_rate_pct', 'renter_occupied_pct']:
        data_to_plot = data_to_plot[data_to_plot >= 0]
    
    # 3. Plot the result
    sns.histplot(data_to_plot, kde=True, color='skyblue')
    plt.title(f'Histogram of {var}')
    plt.xlabel(var)
    plt.ylabel('Frequency')

plt.tight_layout()
# Increase hspace (height) and wspace (width) between plots
plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.6)
plt.show()
plt.show()
