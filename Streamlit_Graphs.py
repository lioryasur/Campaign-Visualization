# %%
import dash
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import time as time_pck
import os
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from app import app
import streamlit as st
from datetime import time
from Filters import filter_CD, filter_E
import plotly.subplots as sp
st.set_page_config(layout="wide")



#os.chdir(r"C:\Users\Freddie\Desktop\personal\Information-Visualization")
os.chdir(r"C:\Users\Lior\Desktop\Information-Visualization")

df = pd.read_csv('data/processed_data.csv')
df.sort_values(by=['id', 'year'], inplace=True)


# Filter the DataFrame based on the campaign goal
df_CD = filter_CD(df)  # Replace 'Your Campaign Goal' with your filter

# Create a temporary 'count' column to use for the pie chart values
df_CD['count'] = 1

# Create a pie chart for each combination of state reaction and violence level
fig_CD = px.pie(df_CD, values='count', names='success',
             facet_col='repression_names', facet_row='resistance method',
             color='success',
             color_discrete_map={'Success':'#00FF7F', 'Failure':'salmon'},
            title='Violence and State Reaction Analysis',
        category_orders={"repression_names": ["extreme repression", "moderate repression", "mild repression", "none"],
                         "resistance": ["always violent", "never violent", "sometimes violent"]})






for a in fig_CD.layout.annotations:
    a.text = a.text.split("=")[1]

# Customize the layout
fig_CD.update_layout(
    autosize=False,
    width=800,
    height=500,
    title_text="Violence and State Reaction Analysis",
)

for i, a in enumerate(fig_CD['layout']['annotations']):
    if a['text'] in  ["always violent", "never violent", "sometimes violent"]:
        a["textangle"] = 50
        a["xref"] = "paper"
        a["yref"] = "paper"
        # a["x"] = 0.02
        # a["y"] = 1 - (i / 2)
        a['align'] = "left"
        #incrase font size
    a['font'] = dict(size=15)



df_E = filter_E(df)
# Combine goal, intervention, and progress to create unique nodes
df_E['goal_intervention'] = df_E['goal_names'] + '_' + df_E['ab_internat']
df_E['intervention_progress'] = df_E['ab_internat'] + '_' + df_E['progress_names']

# Create unique mappings for your categories
goal_intervention_mapping = {goal_intervention: i for i, goal_intervention in enumerate(df_E['goal_intervention'].unique())}
intervention_progress_mapping = {intervention_progress: i + len(goal_intervention_mapping) for i, intervention_progress in enumerate(df_E['intervention_progress'].unique())}

# Apply the mappings to your columns
df_E['goal_intervention_codes'] = df_E['goal_intervention'].map(goal_intervention_mapping)
df_E['intervention_progress_codes'] = df_E['intervention_progress'].map(intervention_progress_mapping)

# Rest of the code...

progress_order = ['complete success', 'significant concessions achieved', 'limited concession achieved', 'visible gains short of concessions',
                  'status quo', 'ends in failure']
# Iterate over each goal
df_E = filter_E(df)
# Combine goal, intervention, and progress to create unique nodes
df_E['goal_intervention'] = df_E['goal_names'] + '_' + df_E['ab_internat']
df_E['intervention_progress'] = df_E['ab_internat'] + '_' + df_E['progress_names']

# Create unique mappings for your categories
goal_intervention_mapping = {goal_intervention: i for i, goal_intervention in enumerate(df_E['goal_intervention'].unique())}
intervention_progress_mapping = {intervention_progress: i + len(goal_intervention_mapping) for i, intervention_progress in enumerate(df_E['intervention_progress'].unique())}

# Apply the mappings to your columns
df_E['goal_intervention_codes'] = df_E['goal_intervention'].map(goal_intervention_mapping)
df_E['intervention_progress_codes'] = df_E['intervention_progress'].map(intervention_progress_mapping)

# Rest of the code...

progress_order = ['complete success', 'significant concessions achieved', 'limited concession achieved', 'visible gains short of concessions',
                  'status quo', 'ends in failure']
# Iterate over each goal
E_figs = []
color_dict = {
    'No Intervention': '#FFA07A',
    'Material Reprucussions': '#4682B4',
    'complete success': '#006400',  # Darker green
    'limited concession achieved': '#A2CD5A',  # Darker yellowgreen
    'status quo': 'orange',  # Gold
    'significant concessions achieved': '#6E8B3D',  # Lighter yellowgreen
    'ends in failure': '#8B0000',  # Dark red
    'visible gains short of concessions': '#FFD700',  # YellowGreen
    'greater autonomy': '#808080'  # Gray
}
for goal, df_goal in df_E.groupby('goal_names'):
    # Create unique mappings for your categories
    intervention_mapping = {name: i for i, name in enumerate(df_goal['ab_internat'].unique())}
    progress_mapping = {name: i + len(intervention_mapping) for i, name in enumerate(df_goal['progress_names'].unique())}

    # Apply the mappings to your columns
    df_goal['intervention_codes'] = df_goal['ab_internat'].map(intervention_mapping)
    df_goal['progress_codes'] = df_goal['progress_names'].map(progress_mapping)

    # Create source, target and value lists
    source = df_goal['intervention_codes'].tolist()
    target = df_goal['progress_codes'].tolist()
    values = [1 for _ in range(len(source))]
    sankey_data = pd.DataFrame({'source': source, 'target': target, 'values': values}).sort_values(['source', 'target'])
    # Create colors for each source node
    colors = df_goal['intervention_codes'].map({code: color for code, color in enumerate(['#4682B4','#FFA07A'])}).tolist()
    node_positions = {
        'Material Reprucussions': [0.001, 0.001],
        'No Intervention': [0.001, 0.7],
        'complete success': [0.999, 0.001],
        'significant concessions achieved': [0.999, 0.2],
        'limited concession achieved': [0.999, 0.4],
        'visible gains short of concessions': [0.999, 0.6],
        'status quo': [0.999, 0.8],
        'ends in failure': [.999, .999]
    }
    # Create the label list with counts included
    label_counts = df_goal['ab_internat'].value_counts().to_dict()
    label = [f'{name} ({label_counts[name]})' if name in label_counts else name for name in
             list(intervention_mapping.keys()) + list(progress_mapping.keys())]
    # Create a list of all unique nodes in the correct order
    #all_nodes_E = df_goal['goal_names'].unique().tolist() + df_goal['ab_internat'].unique().tolist()

    # Add progress nodes in the correct order
    all_nodes_E = df_goal['ab_internat'].unique().tolist() + df_goal['progress_names'].unique().tolist()
    #print(all_nodes_E)

    # Manually order the labels based on desired_order
    ordered_labels = [label for label in all_nodes_E if label not in progress_order] + [label for label in progress_order if label in all_nodes_E]
    print(ordered_labels)
    # Create a Sankey plot
    fig_E = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=ordered_labels,
            color=[color_dict.get(node, '#808080') for node in ordered_labels],
            x = [node_positions.get(node, [0.01, 0.01])[0] for node in ordered_labels],
            y = [node_positions.get(node, [0.01, 0.01])[1] for node in ordered_labels]
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=colors,  # Add the colors
        )
    )])

    # Display the plot

    # Set the layout options
    fig_E.update_layout(title_text=f'{goal}', font_size=10)
    E_figs.append(fig_E)

st.title('Campaign Size Distribution')
st.write('''
This histogram shows the the success rate of campaigns based on the percentage of the population involved in the campaign.
''')
st.plotly_chart(fig_CD)



st.title('International Intervention Analysis')
st.write('''
# Explanation of the Plot
This Sankey plot shows the relationship between international intervention and success in different types of campaigns. The plot is faceted by campaign goal, with each facet representing a different campaign goal. The first split is by international intervention, and each "tube" is further split by progress. The width of each tube represents the number of examples.
''')
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(E_figs[0])
with col2:
    st.plotly_chart(E_figs[1])

# appointment = st.slider(
#     "Schedule your appointment:",
#     value=(time(11, 30), time(12, 45)))
# st.write("You're scheduled for:", appointment)
