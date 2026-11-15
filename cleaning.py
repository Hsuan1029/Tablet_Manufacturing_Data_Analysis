"""Appendix A. Load tablet press observations and inspect their distributions."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BOX_COLUMNS = ["tbl_speed", "fom", "main_comp", "tbl_fill", "SREL",
               "pre_comp", "cyl_main", "stiffness"]


def clean_data(path):
    raw = pd.read_csv(path, sep=";")
    measurements = raw.drop(columns=["timestamp", "campaign", "batch", "code"])
    complete = measurements.dropna()
    cleaned = complete.drop_duplicates().reset_index(drop=True)
    print("Raw rows:", len(raw), "| Incomplete:", len(raw) - len(complete),
          "| Duplicate measurements:", len(complete) - len(cleaned),
          "| Retained:", len(cleaned))
    print("Missing values by column:\n", measurements.isna().sum())
    print(cleaned.describe().T)
    return cleaned


def save_plot(fig, directory, name):
    Path(directory).mkdir(parents=True, exist_ok=True)
    fig.savefig(Path(directory) / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def distribution_plots(data, directory, stage, colour):
    fig, axes = plt.subplots(3, 3, figsize=(13, 9), layout="constrained")
    for name, ax in zip(BOX_COLUMNS, axes.flat):
        ax.boxplot(data[name], patch_artist=True, boxprops={"facecolor": colour})
        ax.set_title(name)
        ax.set_xticks([])
    fig.delaxes(axes.flat[-1])
    save_plot(fig, directory, f"boxplots-{stage}")

    axes = pd.plotting.scatter_matrix(data[BOX_COLUMNS[:4]], figsize=(10, 10),
                                      color=colour, alpha=0.5, diagonal="hist",
                                      hist_kwds={"bins": 20, "color": colour})
    save_plot(axes[0, 0].figure, directory, f"scatter-{stage}")
