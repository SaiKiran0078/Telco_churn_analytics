"""Shared chart style so every figure in the project looks the same."""
import matplotlib.pyplot as plt

BLUE, RED, GREY, INK, GREEN, ORANGE = "#2A78D6", "#E34948", "#8C9AAE", "#1F2937", "#1BAF7A", "#EB6834"
plt.rcParams.update({
    "figure.dpi": 100, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#E6E9EE",
    "axes.edgecolor": "#B8C0CC", "axes.titleweight": "bold", "axes.titlesize": 12, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": "#465061", "ytick.color": "#465061", "font.size": 10, "axes.axisbelow": True, "figure.facecolor": "white",
})
