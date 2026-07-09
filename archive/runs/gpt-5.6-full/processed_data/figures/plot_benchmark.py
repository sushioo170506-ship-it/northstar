# Optional plotting script for benchmark_table.csv
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("section_3/benchmark_table.csv")
plt.bar(df["metric"], df["value"])
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("figures/benchmark_bar.png", dpi=200)
