import numpy as np
import pandas as pd
import streamlit as st

@st.cache
def build_admissions_df(n_days, hosp, icu, vent) -> pd.DataFrame:
    days = np.array(range(0, n_days + 1))
    data_dict = dict(zip(["day", "hosp", "icu", "vent"], [days, hosp, icu, vent]))
    projection = pd.DataFrame.from_dict(data_dict)
    # New cases
    projection_admits = projection.iloc[:-1, :] - projection.shift(1)
    projection_admits[projection_admits < 0] = 0
    projection_admits["day"] = range(projection_admits.shape[0])
    return projection_admits

@st.cache
def build_census_df(projection_admits, hosp_los, icu_los, vent_los) -> pd.DataFrame:
    """ALOS for each category of COVID-19 case (total guesses)"""
    n_days = np.shape(projection_admits)[0]
    los_dict = {
        "hosp": hosp_los,
        "icu": icu_los,
        "vent": vent_los,
    }

    census_dict = dict()
    for k, los in los_dict.items():
        census = (
            projection_admits.cumsum().iloc[:-los, :]
            - projection_admits.cumsum().shift(los).fillna(0)
        ).apply(np.ceil)
        census_dict[k] = census[k]

    census_df = pd.DataFrame(census_dict)
    census_df["day"] = census_df.index
    census_df = census_df[["day", "hosp", "icu", "vent"]]
    census_df = census_df.head(n_days)
    return census_df
