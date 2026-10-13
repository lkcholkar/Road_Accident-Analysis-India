import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

df = pd.read_csv('RA2019_A2.csv')
df.columns = df.columns.str.strip()

print('First 5 rows:')
print(df.head())

print('\nColumn names:')
print(df.columns.tolist())

print('\nDataset shape:')
print(df.shape)

print('\nDataset Information:')
print(df.info())

print('\nMissing Values:')
print(df.isnull().sum())

print("\nRoad Accidents by Year:")

for year in range(2016, 2020):
    matches = [
        col for col in df.columns
        if "Total Number of Road Accidents during" in col
        and str(year) in col
        and "Rank" not in col
    ]

    if matches:
        column = matches[0]
        print(year, ":", df[column].sum())
    else:
        print(year, ": Column not found")

print("\nTop 10 States/UTs with Most Road Accidents in 2019:")

column = [
    col for col in df.columns
    if "Total Number of Road Accidents during 2019" in col
    and "Rank" not in col
    and "Numbers" in col
]

if column:
    column = column[0]

    df['States/UTs'] = df['States/UTs'].str.strip()

    top_states = df[df["States/UTs"] != "Total"][
        ["States/UTs", column]
    ].sort_values(
        by=column, ascending=False
    ).head(10)

    print(top_states)

    print('\nTop State with Most Road Accidents in 2019:')
    print(top_states.iloc[0, 0], '-',
          top_states.iloc[0, 1])

    print('\nStates with Least Accidents among Top 10:')
    print(top_states.iloc[-1, 0], '-',
          top_states.iloc[-1, 1])

    plt.figure(figsize=(12, 6))

    bars = plt.bar(
        top_states["States/UTs"],
        top_states[column]
    )

    plt.title("Top 10 States/UTs with Most Road Accidents in 2019")
    plt.xlabel("States/UTs")
    plt.ylabel("Number of Accidents")
    plt.xticks(rotation=45, ha="right")

    plt.bar_label(bars, fmt="%.0f")
    plt.tight_layout()

    plt.savefig("graphs/top_10_states.png")
    plt.show()

else:
    print("2019 accident column not found")

print("\nYear-wise Percentage Change in Road Accidents:")

years = []
accidents = []

for year in range(2016, 2020):
    matches = [
        col for col in df.columns
        if "Total Number of Road Accidents during" in col
        and str(year) in col
        and "Rank" not in col
    ]

    if matches:
        years.append(year)
        accidents.append(df[matches[0]].sum())

for i in range(1, len(years)):
    change = (
        (accidents[i] - accidents[i - 1])
        / accidents[i - 1]
    ) * 100

    print(f"{years[i-1]} to {years[i]}: {change:.2f}%")

# Actual dataset values will be used for the graph
# years and accidents are already calculated above

plt.figure(figsize=(9, 5))

bars = plt.bar(years, accidents)

plt.title("Road Accidents in India (2016-2019)")
plt.xlabel("Year")
plt.xticks([2016, 2017, 2018, 2019])
plt.ylabel("Number of Accidents")

plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{int(x):,}'))
plt.bar_label(bars, fmt="%.0f")
plt.tight_layout()
plt.savefig("graphs/road.png")
plt.show()