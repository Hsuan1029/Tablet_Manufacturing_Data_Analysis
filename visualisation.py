"""Appendix C. Inspect the distributions after z-score standardisation."""
from cleaning import distribution_plots


def plot_standardised(scaled, directory):
    distribution_plots(scaled, directory, "standardised", "orange")
