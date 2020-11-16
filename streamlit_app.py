import streamlit as st
import numpy as np
import pandas as pd
import datetime
import altair as alt
import copy

@st.cache(persist=True)

def load_data(path):
    data=pd.read_csv(path)
    return data

#load in data
fb_mask_original=load_data("fb_mask.csv")
fb_sympton_original=load_data("fb_sympton.csv")
fb_sympton=copy.deepcopy(fb_sympton_original)
fb_mask=copy.deepcopy(fb_mask_original)
fb_mask['time_value']= pd.to_datetime(fb_mask['time_value'], format='%Y/%m/%d')
fb_sympton['time_value']= pd.to_datetime(fb_sympton['time_value'], format='%Y/%m/%d')
fb_mask.rename(columns={'value':'mask_percentage'}, inplace=True)
fb_sympton.rename(columns={'value':'sympton_percentage'}, inplace=True)

fb_all=fb_mask.merge(fb_sympton, on=['time_value','geo_value'])
fb_all=fb_all[['geo_value','time_value','mask_percentage','sympton_percentage']]

states=fb_all.geo_value.str.upper().unique()

#first plot: correlation between wearing mask and having symptons
st.title("Let`s see the correlation between wearing mask and having symptons.")

state_choice = st.sidebar.multiselect(
    "Which state are you interested in?",
    states.tolist(), default=['AK','AL','AR','AZ','CA','CO']
)

date_range = st.sidebar.date_input("Which range of date are you interested in? Choose between %s and %s"% (min(fb_all['time_value']).strftime('%Y/%m/%d'),  max(fb_all['time_value']).strftime('%Y/%m/%d')), [min(fb_all['time_value']), max(fb_all['time_value'])])

fb_temp = fb_all[fb_all['geo_value'].str.upper().isin(state_choice)]

if len(date_range)==2:
    fb_selected = fb_temp[(fb_temp['time_value']>=pd.to_datetime(date_range[0])) & (fb_temp['time_value']<=pd.to_datetime(date_range[1]))]
else:
    fb_selected = fb_temp[(fb_temp['time_value']>=pd.to_datetime(date_range[0]))]

scatter_chart = alt.Chart(fb_selected).mark_circle().encode(
    x=alt.X('mask_percentage', scale=alt.Scale(zero=False), axis=alt.Axis(title='percentage of wearing masks')), 
    y=alt.Y('sympton_percentage', scale=alt.Scale(zero=False), axis=alt.Axis(title='percentage of having covid symptons'))
)
scatter_chart + scatter_chart.transform_regression('mask_percentage', 'sympton_percentage').mark_line()
