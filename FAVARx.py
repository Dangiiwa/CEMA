import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

# from favarx_forecast import show_forecast_page
# from favarx_forecast import favarx_forecast

# @st.cache
def load_data():
    df = pd.read_excel("favardata1105.xlsx")
    df = df.set_index('date')

    dflog = np.log(df[[ 'ABCPI', 'ARY', 'ASI', 'BLAG', 'BLMF', 'BLOG', 'BLPS', 'BLSM', 'BLTL', 'BLUS', 'BLXP', 'C1CPI', 'C2CPI',
                    'CCPI', 'CCPS', 'CFCPI', 'CGRY', 'COP', 'CPD', 'CPS', 'COS', 'CRY', 'ECPI', 'ER', 'EUR', 'EXR', 'FCPI',
                    'FHCPI', 'FNCPI', 'FRY', 'GBP', 'GRV', 'GXP', 'HHCPI', 'HRY', 'HWCPI', 'IEP', 'IIP', 'IMAP', 'IMIP',
                    'IMP', 'IRY', 'M1', 'M2', 'MCPI', 'MRY', 'NDC', 'NFA', 'NORY', 'PRY', 'QM', 'RCCPI', 'RHCPI', 'RINV',
                    'RPC', 'RPDI', 'RR', 'RRY', 'RUCPI', 'RY', 'SD', 'SMRY', 'SRY', 'TCPI', 'TD', 'TRY', 'URCPI', 'URY',
                    'USD', 'EXP', 'MPMIS' ]])

    dflogdiff = dflog[[ 'C1CPI','C2CPI','FCPI','FNCPI','ABCPI','CFCPI','HWCPI','FHCPI','HHCPI','TCPI','CCPI','RCCPI','ECPI',
                   'RHCPI','MCPI','URCPI','RUCPI','CPD','EXP','IMP','GXP','IRY','SMRY','MRY','SRY','TRY','CRY','URY','PRY',
                   'RINV','IMAP','IMIP','IEP','IIP','COP','GBP','EUR','ASI','M1','QM','CCPS','COS','SD','TD','RR','ER','NFA',
                   'NDC','EXR','BLPS','BLAG','BLSM','BLXP','BLMF','BLUS','BLOG','BLTL','USD' ]]
    dflogdiff = dflogdiff - dflogdiff.shift(4)

    dfonlydiff = df[['MDR1','MDR3','MDR6','MDR12','PLR','MLR','IBCR','TBR','CRR']]
    dfonlydiff = dfonlydiff - dfonlydiff.shift(4)

    grdfn = df[['HCPI','RY','ARY','ICRY','TTRY','RRY','ERY','HRY','M2','CGRY','NORY']]
    growth_rate = ((grdfn - grdfn.shift(4)) / grdfn.shift(4)) * 100

    groupL = dflog[[ 'ABCPI', 'GRV', 'RPC', 'RPDI']]
    groupDL = dflogdiff[[ 'C1CPI','C2CPI','FCPI','FNCPI','CFCPI','HWCPI','FHCPI','HHCPI','TCPI','CCPI','RCCPI','ECPI','RHCPI',
                     'MCPI','URCPI','RUCPI','CPD','EXP','IMP','GXP','RINV','IMAP','IMIP','IEP','IIP','GBP','EUR','ASI',
                     'QM','CCPS','COS','SD','TD','ER','NFA','NDC','EXR','BLTL' ]]
    groupGR = growth_rate[['HCPI', 'M2','CGRY', 'NORY']]

    SubGroup = pd.merge(pd.merge(groupL, groupDL, on=['date']), pd.merge(dfonlydiff, groupGR, on=['date']), on=['date'])
    FinalGroup = pd.merge(SubGroup, df['SDR'],  on=['date'])

    FinalGroup = FinalGroup.dropna()

    pca5 = PCA(n_components=5)
    principalComponents = pca5.fit_transform(FinalGroup)
    Dfpc = pd.DataFrame(data = principalComponents, columns = ['pc1', 'pc2', 'pc3', 'pc4', 'pc5'], index=FinalGroup.index)

    DfpcDiff = Dfpc - Dfpc.shift()
    DfpcDiff.dropna(inplace=True)

    df_sub = growth_rate["RY"].iloc[3:]
    df_pcsRY = DfpcDiff.assign(dlRY=df_sub)

    endog = df_pcsRY.loc['2017-03-31':'2021-12-31', ['pc1','pc2','pc3','pc4','pc5','dlRY']]

    return df, dflog, FinalGroup, endog, growth_rate

def favarx_explore():
    st.write(""" # Factor-Augmented VARx Model """)

    with st.expander("See explanation"):
        st.write("""
        A collaboration between **Research** and **IT** Department

        Factor-Augmented VARs

        """)

# st.set_page_config(page_title="Netflix Shows", layout="wide")
# st.title("Data")
    st.write("""
    #### Dataset
    """)


    data = pd.read_excel('favardata1105.xlsx')
    # AgGrid(data)

    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    # gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
    gridOptions = gb.build()


    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=False,
        theme='streamlit', #Add theme color to the table
        enable_enterprise_modules=True,
        height=350,
        width='100%',
        reload_data=True
    )

    data = grid_response['data']
    selected = grid_response['selected_rows']
    df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df



    st.subheader("Plot of RY (growth rate)")
    st.caption("Growth rate formula applied")

    dataindex = data.set_index('date')
    # st.dataframe(dataindex)

    grdfn = dataindex[['HCPI', 'RY']]
    growth_rate = ((grdfn - grdfn.shift(4)) / grdfn.shift(4)) * 100
    # growth_rate

    st.line_chart(growth_rate['RY'])


# with st.form("my_form"):
#     st.write("Inside the form")
#     slider_val = st.slider("Form slider")
#     checkbox_val = st.checkbox("Form checkbox")
#
#     # Every form must have a submit button.
#     submitted = st.form_submit_button("Submit")
#     if submitted:
#         st.write("slider", slider_val, "checkbox", checkbox_val)
#
# st.write("Outside the form")


# show_forecast_page()
# favarx_forecast()



# st.metric("My metric", 42)
