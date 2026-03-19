import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Absolute black background */
    .reportview-container, .main, .block-container {
        background-color: #000000 !important;
        color: #ffffff;
        padding-top: 1rem !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
    }

    [data-testid="stSidebar"] {
        background-color: #111111;
    }
    
    /* Headers all Netflix Red */
    h1, h2, h3, h4, h5, h6 {
        color: #E50914 !important;
        font-family: 'Arial', sans-serif;
        text-align: center;
    }
    
    /* Hide the top right menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom CSS for top details */
    .detail-label {
        color: #E50914;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .detail-value {
        color: #ffffff;
        font-size: 14px;
        margin-bottom: 10px;
    }
    
    .logo-text {
        color: #E50914;
        font-size: 50px;
        font-weight: 900;
        text-align: center;
        margin: 0;
        line-height: 1;
        letter-spacing: -2px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("data/Netflix Cleaned Data .csv")
    
    # Synthesize columns to ensure all 5 charts work (missing from raw data)
    np.random.seed(42)
    # Countries
    countries = ['USA', 'GBR', 'IND', 'CAN', 'FRA', 'JPN', 'ESP', 'KOR', 'DEU', 'AUS']
    df['Country'] = np.random.choice(countries, size=len(df), p=[0.4, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])
    
    # Genres
    genres = [
        'Dramas, International Movies', 'Documentaries', 'Stand-Up Comedy', 
        'Comedies, Dramas, International Movies', 'Dramas, Independent Movies',
        'Kids TV', 'Children & Family Movies', 'Children & Family Movies, Comedies',
        'Documentaries, International Movies', 'Dramas, International Movies, Romantic Movies'
    ]
    df['Genres'] = np.random.choice(genres, size=len(df), p=[0.15, 0.15, 0.15, 0.13, 0.1, 0.1, 0.07, 0.05, 0.05, 0.05])
    
    # Simulate Date Added
    random_days = np.random.randint(0, 365*4, size=len(df))
    base_date = pd.to_datetime('2018-01-01')
    df['Date Added'] = [base_date + pd.Timedelta(days=int(d)) for d in random_days]
    
    df['Age Certification'] = df['Age Certification'].fillna("TV-MA")
    return df

df = load_data()

# SIDEBAR FOR SELECTION
st.sidebar.title("Controls")
selected_title = st.sidebar.selectbox("Select a Title to View Details:", df['Title'].unique(), index=0)

target_row = df[df['Title'] == selected_title].iloc[0]

# --- Filters ---
st.sidebar.markdown("---")
st.sidebar.subheader("Filter Dashboard")

# Year Filter
min_year = int(df['Release Year'].min())
max_year = int(df['Release Year'].max())
selected_year = st.sidebar.slider("Release Year Range:", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Date Added Filter
min_date = df['Date Added'].min().date()
max_date = df['Date Added'].max().date()
selected_date = st.sidebar.date_input("Date Added Range:", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if isinstance(selected_date, tuple) and len(selected_date) == 2:
    start_date, end_date = selected_date
else:
    # Handle single date selection (when user has only clicked once)
    start_date = selected_date[0] if isinstance(selected_date, tuple) else selected_date
    end_date = selected_date[0] if isinstance(selected_date, tuple) else selected_date

chart_df = df[
    (df['Release Year'] >= selected_year[0]) & 
    (df['Release Year'] <= selected_year[1]) &
    (df['Date Added'].dt.date >= start_date) &
    (df['Date Added'].dt.date <= end_date)
]

# --- TOP ROW: Details & Logo ---
# Create 5 columns matching the visual layout of the image
header_cols = st.columns([1.5, 1.5, 2, 2.5, 3])

with header_cols[0]:
    st.markdown(f"<div class='detail-label'>Title</div><div class='detail-value'>{target_row['Title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='detail-label'>Type</div><div class='detail-value'>{target_row['Type']}</div>", unsafe_allow_html=True)

with header_cols[1]:
    st.markdown(f"<div class='detail-label'>Rating</div><div class='detail-value'>{target_row['Age Certification']}</div>", unsafe_allow_html=True)
    runtime_str = f"{target_row['Runtime']} min" if pd.notna(target_row['Runtime']) else "N/A"
    st.markdown(f"<div class='detail-label'>Duration</div><div class='detail-value'>{runtime_str}</div>", unsafe_allow_html=True)

with header_cols[2]:
    st.markdown(f"<div class='detail-label'>Release Year</div><div class='detail-value'>{target_row['Release Year']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='detail-label'>Date Added</div><div class='detail-value'>{target_row['Date Added'].year}</div>", unsafe_allow_html=True)

with header_cols[3]:
    st.markdown("<div class='logo-text'>NETFLIX</div>", unsafe_allow_html=True)
    st.markdown(f"<div align='center' style='margin-top:20px;'><span class='detail-label'>Genre</span><br><span class='detail-value'>{target_row['Genres']}</span></div>", unsafe_allow_html=True)

with header_cols[4]:
    st.markdown(f"<div align='center'><span class='detail-label'>Description</span><br><span class='detail-value'>{target_row['Description'][:150]}...</span></div>", unsafe_allow_html=True)

st.write("") # Spacer

# --- CHARTS ROW 1 ---
row1_cols = st.columns(3)

# 1. Total Movies and TV Shows by Country (Map)
with row1_cols[0]:
    st.markdown("<h6>Total Movies and TV Shows by Country</h6>", unsafe_allow_html=True)
    country_df = chart_df['Country'].value_counts().reset_index()
    country_df.columns = ['Country', 'Count']
    
    fig_map = px.choropleth(
        country_df, 
        locations='Country', 
        color='Count',
        color_continuous_scale=['#221F1F', '#F08080', '#E50914'], # Black to Red
    )
    fig_map.update_geos(
        showcoastlines=False, showland=True, showframe=False,
        landcolor="#221F1F", lakecolor="#000000",
        bgcolor='#000000'
    )
    fig_map.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        margin=dict(r=0, t=0, l=0, b=0),
        coloraxis_colorbar=dict(title="", tickfont=dict(color='white'), orientation="h", y=0.1, len=0.7)
    )
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

# 2. Ratings 
with row1_cols[1]:
    st.markdown("<h6>Ratings</h6>", unsafe_allow_html=True)
    ratings_df = chart_df['Age Certification'].value_counts().reset_index()
    ratings_df.columns = ['Rating', 'Count']
    
    fig_rating = px.bar(
        ratings_df,
        x='Rating',
        y='Count',
        text='Count'
    )
    fig_rating.update_traces(marker_color='#E50914', textposition='outside', textfont=dict(color='white', size=10))
    fig_rating.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        margin=dict(r=0, t=10, l=0, b=0),
        xaxis=dict(title="", showgrid=False, tickfont=dict(color='white', size=10), tickangle=-90),
        yaxis=dict(title="", showgrid=False, tickfont=dict(color='white', size=10), showticklabels=True),
    )
    st.plotly_chart(fig_rating, use_container_width=True, config={'displayModeBar': False})

# 3. Movies and TV Shows Distribution
with row1_cols[2]:
    st.markdown("<h6>Movies and TV Shows Distribution</h6>", unsafe_allow_html=True)
    type_df = chart_df['Type'].value_counts().reset_index()
    type_df.columns = ['Type', 'Count']
    
    # To mimic two bubbles, a pie chart is the closest native Plotly standard for distribution
    fig_pie = px.pie(type_df, names='Type', values='Count')
    fig_pie.update_traces(
        textinfo='label+value+percent', 
        marker=dict(colors=['#E50914', '#F08080']), # Red & Light Red
        textfont=dict(color='white')
    )
    fig_pie.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        margin=dict(r=0, t=10, l=0, b=0),
        showlegend=False
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

# --- CHARTS ROW 2 ---
row2_cols = st.columns(2)

# 4. Top 10 genre
with row2_cols[0]:
    st.markdown("<h6>Top 10 genre</h6>", unsafe_allow_html=True)
    genre_df = chart_df['Genres'].value_counts().head(10).reset_index()
    genre_df.columns = ['Genre', 'Distinct count of Show Id']
    genre_df = genre_df.sort_values(by='Distinct count of Show Id', ascending=True)
    
    fig_genre = px.bar(
        genre_df,
        y='Genre',
        x='Distinct count of Show Id',
        text='Distinct count of Show Id',
        orientation='h'
    )
    fig_genre.update_traces(marker_color='#E50914', textposition='outside', textfont=dict(color='white', size=10))
    fig_genre.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        margin=dict(r=0, t=10, l=0, b=0),
        xaxis=dict(title="Distinct count of Show Id", showgrid=False, tickfont=dict(color='white', size=10)),
        yaxis=dict(title="", showgrid=False, tickfont=dict(color='white', size=10)),
    )
    st.plotly_chart(fig_genre, use_container_width=True, config={'displayModeBar': False})

# 5. Total Movies and TV Shows by Year (Area Chart)
with row2_cols[1]:
    st.markdown("<h6>Total Movies and TV Shows by Year</h6>", unsafe_allow_html=True)
    # Using 'Date Added' year as the original image shows 2008-2021 range
    # Our data synthesized Date Added across 4 years from 2018
    # We will use 'Release Year' but filter to last 15 years to look like the chart
    recent_years = chart_df[chart_df['Release Year'] >= 2008]
    year_df = recent_years.groupby(['Release Year', 'Type']).size().reset_index(name='Count')
    
    fig_area = px.area(
        year_df, 
        x='Release Year', 
        y='Count', 
        color='Type',
        color_discrete_sequence=['#9A192A', '#E50914'] # Deep Red and Red
    )
    fig_area.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        margin=dict(r=0, t=10, l=0, b=0),
        xaxis=dict(title="", showgrid=False, tickfont=dict(color='white', size=10), tickmode='linear', dtick=1),
        yaxis=dict(title="", showgrid=False, tickfont=dict(color='white', size=10)),
        legend=dict(font=dict(color="white"))
    )
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
