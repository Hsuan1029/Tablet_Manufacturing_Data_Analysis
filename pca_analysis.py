"""Appendix D. Run the four appendix stages and export the figures."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2
from sklearn.decomposition import PCA

from cleaning import clean_data, distribution_plots, save_plot
from standardisation import FEATURES, OUTCOMES, standardise
from visualisation import plot_standardised


def score_plot(scores, variance, axis, outcome, label, directory, filename):
    points = scores[:, [0, axis]]
    fig, ax = plt.subplots(figsize=(8, 7))
    dots = ax.scatter(*points.T, c=outcome, s=6, cmap="viridis")
    fig.colorbar(dots, ax=ax, label=label)
    # Gaussian reference contour for individual scores in this projection.
    values, vectors = np.linalg.eigh(np.cov(points.T))
    theta = np.linspace(0, 2 * np.pi, 200)
    circle = np.stack([np.cos(theta), np.sin(theta)])
    radii = np.sqrt(np.maximum(values, 0) * chi2.ppf(0.95, df=2))
    ellipse = points.mean(axis=0)[:, None] + vectors @ (radii[:, None] * circle)
    ax.plot(*ellipse, "k--", lw=1, label="95% reference ellipse")
    ax.axhline(0, linestyle=":", color="grey")
    ax.axvline(0, linestyle=":", color="grey")
    ax.set(xlabel=f"PC1 ({variance[0]:.1f}%)",
           ylabel=f"PC{axis + 1} ({variance[axis]:.1f}%)")
    ax.legend()
    save_plot(fig, directory, filename)


def plot_components(model, directory):
    variance = model.explained_variance_ratio_ * 100
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar([f"PC{i+1}" for i in range(len(variance))], variance, color="skyblue")
    ax.bar_label(bars, fmt="%.1f%%")
    ax.margins(y=0.12)
    ax.set(ylabel="Explained variance (%)", xlabel="Principal component")
    save_plot(fig, directory, "scree")

    weights = model.components_
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 8), layout="constrained")
    for idx, (ax, colour) in enumerate(zip(axes, ["steelblue", "mediumseagreen", "tomato"])):
        ax.plot(FEATURES, weights[idx], marker="o", color=colour)
        ax.set_ylabel(f"PC{idx+1} loading")
        ax.grid(alpha=0.3)
    axes[-1].tick_params(axis="x", rotation=45)
    save_plot(fig, directory, "loadings")

    fig, ax = plt.subplots(figsize=(8, 8))
    for name, (x, y) in zip(FEATURES, weights[:2].T):
        ax.annotate("", xy=(x, y), xytext=(0, 0), arrowprops={"arrowstyle": "->"})
        ax.annotate(name, (x, y), xytext=(3, 4), textcoords="offset points")
    ax.axhline(0, color="grey", linestyle=":")
    ax.axvline(0, color="grey", linestyle=":")
    ax.set(xlabel="PC1 loading", ylabel="PC2 loading", aspect="equal",
           xlim=(-1, 1), ylim=(-1, 1))
    save_plot(fig, directory, "loading-vectors")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Semicolon-delimited tablet press CSV")
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    cleaned = clean_data(args.csv)
    scaled = standardise(cleaned)
    if len(scaled) < 9:
        parser.error("Nine-component PCA requires at least nine retained observations.")
    distribution_plots(cleaned, args.output, "before", "steelblue")
    plot_standardised(scaled, args.output)
    model = PCA(n_components=9, svd_solver="full")
    scores = model.fit_transform(scaled)
    plot_components(model, args.output)
    variance = model.explained_variance_ratio_ * 100
    for label in OUTCOMES:
        score_plot(scores, variance, 1, cleaned[label], label, args.output, f"scores-{label}")
    score_plot(scores, variance, 2, cleaned["produced"], "produced", args.output,
               "scores-pc3-produced")


if __name__ == "__main__":
    main()
