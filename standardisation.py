"""Appendix B. Standardise the process variables used to fit PCA."""
import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURES = ["tbl_speed", "fom", "main_comp", "tbl_fill", "SREL", "pre_comp",
            "cyl_main", "cyl_pre", "stiffness", "ejection"]
OUTCOMES = ["produced", "waste"]


def standardise(cleaned):
    scaled = StandardScaler().fit_transform(cleaned[FEATURES])
    return pd.DataFrame(scaled, index=cleaned.index, columns=FEATURES)
