import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from statsmodels.tsa.api import VAR

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


from FAVARx import load_data
df, dflog, FinalGroup, endog, growth_rate = load_data()


def favarx_forecast():
    st.title("FAVARx Forecast")
    st.write(""" #### Forecast GDP """)

    quarters = (
    "1","2","3","4"
    )

    st.sidebar.write("Select Exogenous Values")

    # quarter = st.sidebar.number_input("Number of Quarters", 1, 4, 4)
    COP = st.sidebar.slider("Crude Oil Price", 0, 120, 50)
    GXP = st.sidebar.slider("GXP", 1000000, 99999999, 4024610)
    MPMIS = st.sidebar.slider("MPMIS", 0, 100, 51)

    exoginputdata = {'COP':[COP, COP, COP, COP],
    'GXP': [GXP, 4281500, 4367130, 4452760],
    'MPMIS': [MPMIS, 52, 52, 53]}

    exog = dflog[['COP', 'MPMIS', 'GXP']]
    exog.drop(exog.tail(4).index,inplace=True) # drop last n rows
    # print(exog)

    input_exog = pd.DataFrame(exoginputdata, index=df[-4:].index)
    input_exog = np.log(input_exog)
    # print(input_exog)

    frames = [exog, input_exog]
    exogOI = pd.concat(frames)
    # print(exogOI)

    shiftofgxp = exogOI['GXP'] - exogOI['GXP'].shift(4)
    #print(shiftofgxp)

    exogOI = exogOI[['COP', 'MPMIS']]
    exogOI = pd.merge(exogOI, shiftofgxp, on=['date'])
    # print(exogOI)

    exogModel = exogOI.loc['2017-03-31':'2021-12-31', ['COP', 'GXP', 'MPMIS']]
    # print(exogModel)

    exogForecast = exogOI.loc['2022-03-31':'2022-12-31', ['COP', 'GXP', 'MPMIS']]
    # print(exogForecast)

    var = VAR(endog, exogModel)
    results = var.fit(1)

    forecast = results.forecast(endog.values[-1:], steps=4, exog_future=exogForecast)
    forecastdf = pd.DataFrame(data = forecast, columns = ['pc1', 'pc2', 'pc3', 'pc4', 'pc5', 'dlRY'], index=df[-4:].index)

    col1, col2 = st.columns([3, 2])
    # col1.subheader("Line chart of forecast values")
    col1.line_chart(forecastdf['dlRY'])
    # col2.subheader("Forecast values DataFrame")
    col2.dataframe(forecastdf['dlRY'])

    st.write( "Quarters: ", quarter)
    # "ExogFuture:", exogForecast,

    gg = growth_rate['RY']
    gg.drop(gg.tail(4).index,inplace=True)
    frames = [gg, forecastdf['dlRY']]
    print(frames)
    forecastfull = pd.concat(frames)
    # st.write("""
    #             GDP With Forecast Values
    #     """)
    st.line_chart(forecastfull)
