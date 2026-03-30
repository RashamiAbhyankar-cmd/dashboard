import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from io import BytesIO
import numpy as np
import plotly.graph_objects as go
warnings.filterwarnings('ignore')
# s:\Operations\13) CPE ECU\1.Returns......ECU Return Tracker
st.set_page_config(page_title="CDashB!!!", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: C DashBoard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

st.subheader("Enter the File Path ")
file_path = st.text_input("Enter the File Path ", "")
if not os.path.exists(file_path):
    print("Error: File not found at this path.")
elif os.path.isdir(file_path):
    print("Error: The path points to a directory, not a file.")
else:
    try:
        dfpath = pd.read_excel(file_path)
        print("Success! File loaded.")
        st.dataframe(dfpath)
    except PermissionError:
        print("Still getting PermissionError. Is the file open in Excel?")
    


fl = st.file_uploader(":file_folder:Upload a file", type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    #df = pd.read_csv(filename, encoding= "ISO-8859-1") 
    # for csv...^....
    xl=pd.ExcelFile(filename)
    df = pd.read_excel(filename)
    # for eXCEL FILES...^....
else:
    filename = "SCRDataExcel.xlsx"
    #os.chdir(r"C:\Users\Acer\OneDrive\Desktop\SNA\Python\CDashB")
    #os.chdir(r"!git clone https://github.com/RashamiAbhyankar-cmd/dashboard")
    #df = pd.read_csv("SCRData.csv", encoding="ISO-8859-1")
    xl= pd.ExcelFile(filename)
    df = pd.read_excel("SCRDataExcel.xlsx")



#select Tab
sheet_name = st.selectbox("Select a tab", xl.sheet_names)

df=pd.read_excel(filename, sheet_name=sheet_name)
st.subheader(f"Tab selected: {sheet_name}")

col1, col2 = st.columns((2))
df["Date Received"] = pd.to_datetime(df["Date Received"])
# Getting the min and max date
startDate = pd.to_datetime(df["Date Received"]).min()
endDate = pd.to_datetime(df["Date Received"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start date", startDate))
    
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))
    
df = df[(df["Date Received"] >= date1) & (df["Date Received"] <= date2)].copy()
#st.dataframe(df)

# Create Selection for Status
st.sidebar.header ("Select 'Status':")
status = st.sidebar.multiselect("Select Status Open or Closed", df["Status"].unique())
if not status:
    df2 = df.copy()
else:
    df2 = df[df["Status"].isin(status)]

# Create Selection for Plant or Field Return
st.sidebar.header("Select 'Return Type':")
plantorfield = st.sidebar.multiselect ("Select Plant or Filed Return", df["Plant / Field return"].unique()) 
if not plantorfield:
    df3 = df2.copy()
else:
    df3 = df2[df2["Plant / Field return"].isin(plantorfield)]
#st.dataframe(df3)
   
#Create Selection for Model Type
st.sidebar.header("Select 'Model':")
model = st.sidebar.multiselect ("Select Model", df["Model"].unique())
if not model:
    df4 = df3.copy()
else:
    df4 = df3[df3["Model"].isin(model)]
st.dataframe(df4)

# Filter Data Based on Status, Plant or Field
if not status and not plantorfield:
	filtered_df=df
elif status and not plantorfield:
	filtered_df=df2[df["Status"].isin(status)]
elif not status and plantorfield:
	filtered_df=df2[df["Plant / Field return"].isin(plantorfield)]
else:
	filtered_df=df2[df["Plant / Field return"].isin(plantorfield) & df["Status"].isin(status)]

#st.dataframe(filtered_df)

 
# Status Open / Closed : Return Units
status_df = (df4.groupby(by =["Status"], as_index=False).size().rename(columns={"size" : "Count"}))
#st.dataframe(status_df)
with col1:
    st.subheader("Status-wise Return Analysis")
    fig = px.bar(status_df, x = "Status", y = "Count",  template="seaborn")
    st.plotly_chart(fig,use_container_width=True, height= 300)
    
# Plant or Field Returns    
plantorfield_df = (df4.groupby(by = ["Plant / Field return"], as_index=False).size().rename(columns={"size":"Countpf"}))
#st.dataframe(plantorfield_df)
with col2:
    st.subheader("Plant or Field Return Numbers")
    fig = px.bar(plantorfield_df, x = "Plant / Field return", y = "Countpf", template="seaborn")
    st.plotly_chart(fig,use_container_width=True, height=300)

#col1, col2 = st.columns((2))   
# Line Chart by Date    

df4["month_year"] = df4["Date Received"].dt.to_period("M")
df4["months_year_str"] = df4["month_year"].dt.strftime("%Y : %b")
st.subheader("Time Series analysis")
#linechart = (df4.groupby(df4["month_year"].dt.strftime("%Y : %b")).size().rename("Countunits").reset_index())
linechart = (df4.groupby("month_year").size().rename("Countunits").reset_index().sort_values("month_year"))
linechart["month_year_str"] = linechart["month_year"].dt.strftime("%Y : %b")
#fig3 = px.line(linechart, x = "month_year", y = "Countunits", labels= {"size": "Number of Units"}, height=500, width=1000, template="gridon")
fig3 = px.line(linechart, x = "month_year_str", y = "Countunits", labels= {"size": "Number of Units"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig3, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name="TimeSeries.csv", mime = 'text/csv')


# Line Chart for Aging as per Month
df4["Date Received"] = pd.to_datetime(df4["Date Received"])
df4["month_year"] = df4["Date Received"].dt.to_period("M")
df4["months_year_str"] = df4["month_year"].dt.strftime("%Y : %b") # newly added
df4['Aging'] = pd.to_numeric(df['Aging'], errors='coerce')
st.subheader ("Aging average for units Received perMonth")
#linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b")) ["Sales"].sum()).reset_index()....does not work
#linechart = (df4.groupby(df4["month_year"].dt.strftime("%Y : %b"))["Aging"].mean().reset_index().sort_values("month_year"))
linechart = (df4.groupby("month_year")["Aging"].mean().reset_index().sort_values("month_year")) #newly added
linechart["month_year_str"] = linechart["month_year"].dt.strftime("%Y : %b") #newly added
#fig4 = px.line(linechart, x = "month_year", y = "Aging", labels= {"Aging":"Avg Aging"}, height=500,
#width=1000, template="gridon")
fig4 = px.line(linechart, x = "month_year_str", y = "Aging", labels= {"Aging":"Avg Aging"}, height=500,
width=1000, template="gridon")
st.plotly_chart(fig4, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Oranges"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name="TimeSeriesAging.csv", mime = 'text/csv')
# Search by Keyword for Tracking Number
st.subheader("Search by Keyword by Tracking Number")
df['Tracking No'] = df['Tracking No'].astype(str).str.replace(',', '')
search_query = st.text_input("Enter Tracking Number to Search", "")
if search_query:
    search_df = df[df["Tracking No"].str.contains(search_query, case=False, na=False)]
else:
    search_df = df[df["Tracking No"].str.contains("E-W", case=False, na=False)]
st.write(f"Showing {len(search_df)} results:")
st.dataframe(search_df, use_container_width=True)

#Search by Keyword for Failure by Defective part Number or Model Number
df['Defective component  P/No'] = df['Defective component  P/No'].astype(str).str.replace(',', '')
df["End Model Number"] = df["End Model Number"].astype(str).str.replace(',','')
#df4["Defective component  P/No"] = pd.to_numeric(df4["Defective component  P/No"], errors='coerce')
st.subheader("Search by Keyword for Failure by part Number or End Model Number")
search_query = st.text_input("Enter part number or End Model Number to Search", "")
#search_query = pd.to_numeric(search_query)
if search_query:
    search_df = df[ df["Defective component  P/No"].str.contains(search_query, case=False, na=False) |
    df["End Model Number"].str.contains(search_query, case=False, na=False)]
else:
    #search_df = df
    search_df = df[ df["Defective component  P/No"].str.contains("123456789", case=False, na=False) |
    df["End Model Number"].str.contains("123456789", case=False, na=False)]   
st.write(f"Showing {len(search_df)} results:")  
st.dataframe(search_df, use_container_width=True)

#Search by Keyword for Failure by Supplier or Root Cause
#df['Defective component  P/No'] = df['Defective component  P/No'].astype(str).str.replace(',', '')
#df4["Defective component  P/No"] = pd.to_numeric(df4["Defective component  P/No"], errors='coerce')
st.subheader("Search by Keyword for Failure by Supplier or Root Cause ")
search_query = st.text_input("Enter Supplier Name or Root Cauase to Search", "")
#search_query = pd.to_numeric(search_query)
if search_query:
    srch_df = df[ df["Supplier"].str.contains(search_query, case=False, na=False) |
    df["Root Cause"].str.contains(search_query, case=False, na=False)]
else:
    #search_df = df
    srch_df = df[ df["Supplier"].str.contains("FET", case=False, na=False) |
    df["Root Cause"].str.contains("FET", case=False, na=False)] 
st.write(f"Showing {len(srch_df)} results:")  
st.dataframe(srch_df, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Warranty Returns Units Summary")
with st.expander("Summary_Table"):
    #df_sample = df[0:5][["ï»¿Tracking No","Date Received","Aging","Status","Plant / Field return","End Model Number","Root Cause"]] 
    # ^ above of rcsv files
    df_sample = df[0:5][["Tracking No","Date Received","Aging","Status","Plant / Field return","End Model Number","Root Cause"]]
    fig5 = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig5, use_container_width=True)
    
st.markdown("### Month-wise Aging Table")

df4["month"] = df4["Date Received"].dt.month_name()

sub_category_Year = pd.pivot_table(
    data=df4,
    values="Aging",
    index=["Model"],
    columns="month"
)

styled = sub_category_Year.style.background_gradient(cmap="Blues")

# Render styled HTML table
st.markdown(styled.to_html(), unsafe_allow_html=True)

#  Create a Scatter Plot                                 
data1 = px.scatter(df4, x = "Date Received", y = "Aging")
fig.update_layout(
    title = dict(
        text=" Date Received and Aging using Scatter Plot", 
        font = dict(size=20)
    )
)  
fig.update_xaxes(
    title = dict(text = "Date Received", font=dict(size=19))
) 
fig.update_yaxes(
    title = dict(text= "Aging", font = dict(size=19))
)   
st.plotly_chart(data1, use_container_width=True) 
 
# data view
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))                         

#Bar Chart

# 1. Prepare Data
df4["Date Received"] = pd.to_datetime(df4["Date Received"])
df4_sorted = df4.sort_values(by="Date Received", ascending=True, ignore_index=True)
df4_sorted["DateText"] = df4_sorted["Date Received"].dt.strftime("%Y-%m-%d")
#df4_reset = df4_sorted.reset_index()
st.dataframe(df4_sorted)
# 2. Create the Bar Chart (Assigning to 'fig')
#fig8 = px.bar(df4_sorted, x="Date Received", y="Aging")
#fig8 = px.bar(df4_sorted, x="Date Received", y="Aging")
color_map={'Open':'blue', 'Closed':'green'}
#fig8 = px.bar(df4_sorted, x="DateText", y="Aging", color="Status", color_discrete_map=color_map) #change this one
fig8 = px.bar(df4_sorted, x="DateText", y="Aging")
# 3. Calculate Trendline
# Note: np.arange (one 'r') and ensure you use df4_reset consistently
x_numeric = np.arange(len(df4_sorted))
z = np.polyfit(x_numeric, df4_sorted["Aging"], 1)
p = np.poly1d(z)
trendline_values = p(x_numeric)

# 4. Add Trendline Trace
fig8.add_trace(go.Scatter(
    #x=df4_sorted["Date Received"], 
    x=df4_sorted["DateText"],
    y=trendline_values, 
    mode='lines', 
    name='Trendline', 
    line=dict(color='Orange', width=2, dash="dash")
))

# 5. Update Layout & Labels
fig8.update_layout(
    title=dict(text="Date Received and Aging", font=dict(size=20)),
    xaxis_title="Date Received",
    yaxis_title="Aging",
    font=dict(size=14)
)
fig8.update_xaxes(type='category')
color_map={'Open':'blue', 'Closed':'green'}

# 6. Render in Streamlit

st.plotly_chart(fig8, use_container_width=True)

# Horizintal Bar Chart
#st.subheader("Bar Chart - Aging Time Analysis")..# this worked...
#fig8 = px.bar(df4_sorted, x="DateText", y="Aging", horizontal = True)
#fig8.update_xaxes (type = 'category')
color_map={'Open':'#0000FF', 'Closed':'#008000'}
#fig9 = px.bar(df4_sorted, x="DateText", y="Aging", color="Status", color_discrete_map=color_map, orientation='v' )
#fig9 = px.bar(df4_sorted, x="Aging", y="DateText", color="Status", color_discrete_map=color_map, orientation='h' )
#fig9.update_yaxes(type='category')
#st.bar_chart(df4_sorted, x="DateText", y="Aging", color= "Status",horizontal=True ) #..this worked

# Compute averages and targets
avg_aging = df4_sorted["Aging"].mean()
aging_target = 30

extra_rows = pd.DataFrame({
    "Tracking No": ["Average Aging", "Aging Target"],
    "Aging": [avg_aging, aging_target],
    "Status": ["Average", "Target"]
})
df4_sorted = pd.concat([df4_sorted, extra_rows], ignore_index=True)

# Color map
color_map = {
    "Open": "#0000FF",
    "Closed": "#00FF00",
    "Average": "#F6BE00",
    "Target": "#F0D884"
}

# --- Build Figure ---
fig10 = go.Figure()


# 1) Main Aging bars

fig10.add_trace(go.Bar(
    x=df4_sorted["Aging"],
    y=df4_sorted["Tracking No"],
    name="Open" if df4_sorted["Status"].iloc[0] == "Open" else "Closed",
    marker_color=[color_map.get(s, "#3CF213") for s in df4_sorted["Status"]],
    orientation='h',
    opacity=1.0,
    text=df4_sorted["Aging"],
    textposition='outside'
))

fig10.add_trace(go.Bar(
    #x=df4_sorted["Aging"],
    x = [None] * len(df4_sorted),  # No bars for this trace, just for legend
    #y=df4_sorted["Tracking No"],
    y = [None] * len(df4_sorted),  # No bars for this trace, just for legend
    name="Open",
    marker_color="blue",
    orientation='h',
    opacity=1.0,
    text=df4_sorted["Aging"],
    textposition='outside'
))

# 2) Average Aging bar (single horizontal line)

#fig10.add_trace(go.Bar(
#    x=[avg_aging] * len(df4_sorted),
#    y=df4_sorted["Tracking No"],
#    name="Average Aging",
#    marker_color=color_map["Average"],
#    orientation='h',
#    opacity=0.4
#))

# 3) Aging Target bar (single horizontal line)
fig10.add_trace(go.Bar(
    x=[aging_target] * len(df4_sorted),
    y=df4_sorted["Tracking No"],
    name="Aging Target=30 days",
    marker_color=color_map["Target"],
    #color_continuous_scale=px.colors.sequential.Viridis,
    orientation='h',
    opacity=0.4,  
    showlegend=True
    #text= df4_sorted["Aging"].apply(lambda x: f"{x:.1f}"),  # Add text labels with one decimal place
    
))
fig10.add_vline(
    x=aging_target,
    line_width=3,
    line_dash="dash",
    line_color="#F7C203",
    annotation_text="Target",
    annotation_position="top right"
)



# Layout
fig10.update_layout(
    barmode='overlay',
    title="Aging by Tracking No. with Average and Target",
    xaxis_title="Aging (Days)",
    yaxis_title="Tracking No.",
    font=dict(size=14),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.subheader("Bar Chart - Aging Time Analysis")
st.plotly_chart(fig10, use_container_width=True)
# Dataset Table
st.subheader("Data Table - Aging Time Analysis")
fig10.update_layout(bargap=0.75) 
st.dataframe(df4_sorted[["Tracking No", "Aging", "Status"]],use_container_width=True,
    column_config={
        "Tracking No": st.column_config.TextColumn(),
        "Aging": st.column_config.NumberColumn(),
        "Status": st.column_config.TextColumn(),
    }
)

# Another Way for same Chart...Now using st.bar_chart for horizontal bars with color by Status
st.subheader("Bar Chart - Aging Time Analysis.....another way using st.bar_chart")
st.bar_chart(df4_sorted, x="Tracking No", y="Aging", color="Status", horizontal=True)

buffer = BytesIO()

with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)

buffer.seek(0)

st.download_button(
    label="Download data",
    data=buffer,
    file_name="output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
