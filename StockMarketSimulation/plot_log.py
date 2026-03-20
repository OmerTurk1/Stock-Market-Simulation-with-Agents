import matplotlib.pyplot as plt
import globals

logs = globals.read_portfolio_log()

fig, axs = plt.subplots(1, 3, figsize=(15, 5))

days = list(logs.keys())
cash_values = [v['cash'] for v in logs.values()]
total_values = [v['total_value'] for v in logs.values()]
stock_counts = [v['diff_stock_number'] for v in logs.values()]

# --- Cash Change ---
axs[0].plot(days, cash_values, marker='o', color='blue')
axs[0].set_title("Cash Change")
axs[0].set_xlabel("Days")
axs[0].set_ylabel("Amount (TL)")
axs[0].grid(True, linestyle='--', alpha=0.7)

# --- Total Value ---
axs[1].plot(days, total_values, marker='s', color='green')
axs[1].set_title("Total Portfolio Value")
axs[1].set_xlabel("Days")
axs[1].set_ylabel("Value (TL)")
axs[1].grid(True, linestyle='--', alpha=0.7)

# --- Different Stock Number ---
axs[2].plot(days, stock_counts, marker='x', color='red')
axs[2].set_title("Diff Stock Number")
axs[2].set_xlabel("Days")
axs[2].set_ylabel("Count")
axs[2].grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig("simulation_results.png")
plt.show()