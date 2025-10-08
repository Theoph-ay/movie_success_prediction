#import libraries
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

#Set page configuration
st.set_page_config(page_title="MOVIE DATA DASHBOARD", layout="wide")
st.title(" :bar_chart: MOVIE DATA DASHBOARD")
#to make the title shift upwards
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)


#File uploader 
fl = st.file_uploader(':file_folder: upload a file', type = (["csv", "txt", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(f"Uploaded file: {filename}")
    try:
        if filename.endswith('.csv') or filename.endswith('.txt'):
            df = pd.read_csv(fl)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(fl, engine='openpyxl')
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    data_path = os.path.join(base_dir, "..", "data", "processed", "cleaned_movies_data.csv")
    df = pd.read_csv(data_path)


#set filter in a sidebar
st.sidebar.header("Choose your filter")
genre = st.sidebar.multiselect("Pick Genre", df["genre"].unique())
if not genre:
    df2 = df.copy()
else:
    df2 = df[df["genre"].isin(genre)]
movie_cert = st.sidebar.multiselect("Pick Movie Certification", df2["movie_certification"].unique())
if not movie_cert:
    df3 = df2.copy()
else:
    df3 = df2[df2["movie_certification"].isin(movie_cert)]
year = st.sidebar.multiselect("Pick year", df3["year"].unique())

#filter data based on the filters
filtered_df = df.copy()

if genre:
    filtered_df = filtered_df[filtered_df["genre"].isin(genre)]

if movie_cert:
    filtered_df = filtered_df[filtered_df["movie_certification"].isin(movie_cert)]

if year:
    filtered_df = filtered_df[filtered_df["year"].isin(year)]

st.subheader(" :bar_chart: METRICS")
col1, col2, col3, col4 = st.columns(4)
with col1:
    num_movies = filtered_df.shape[0]
    st.metric(label="Total Number Of Movies", value=f"{num_movies:,}")

with col2:
    avg_ratings = filtered_df["ratings"].mean() if "ratings" in filtered_df.columns else 0
    st.metric(label="Average Rating", value=f"{avg_ratings:,.2f}")

with col3:
    total_votes = filtered_df["vote_count"].sum() if "vote_count" in filtered_df.columns else 0
    st.metric(label="Total Votes", value=f"{total_votes:,}")
    
with col4:
    st.markdown("<h3 style='text-align: center;'> Top Rated Movie</h3>", unsafe_allow_html=True)
    #top 10 movies by rating
    top_10 = filtered_df.sort_values("ratings", ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x="ratings", y="name", data=top_10, hue="name", palette="viridis")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Movie")
    st.pyplot(fig)
   
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<h3 style='text-align: center;'>Average Ratings Over Time</h3>", unsafe_allow_html=True) #Some Html and CSS to make the text centralized else st.subheader() is okay
    yearly = filtered_df.groupby("year").agg({
    "ratings":"mean",
    }).reset_index()

    # Average Rating per Years
    # Create figure and axes
    fig, ax = plt.subplots()
    sns.lineplot(x="year", y="ratings", data=yearly, marker="o", color="purple", ax=ax)
    ax.set_ylabel("Average Rating")
    st.pyplot(fig, use_container_width=True)

with col2:
    st.markdown("<h3 style='text-align: center;'>Distribution Of Vote Count By Genre</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    sns.boxplot(x="genre", y='vote_count', data=filtered_df, log_scale=True, hue="genre", palette="viridis")
    ax.set_xlabel("Genre")
    ax.set_ylabel("Vote Count")
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

with col3:
    st.markdown("<h3 style='text-align: center;'>Average Ratings By Genre</h3>", unsafe_allow_html=True)
    genre_rating = filtered_df.groupby("genre")['ratings'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots()
    sns.barplot(x=genre_rating.index, y=genre_rating.values, hue=genre_rating.index,palette="viridis", legend=False)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Rating")
    plt.xticks(rotation=70)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True) #note that from 2025-12-31 use_container_width will be removed

with col4:
    st.markdown("<h3 style='text-align: center;'>Ratings By Vote Count</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    sns.scatterplot(x="vote_count", y="ratings", hue="genre", data=filtered_df, palette="viridis", alpha=0.7)
    plt.xscale("log")
    plt.legend(title="Genre", bbox_to_anchor=(1.05, 1), loc="upper left")
    st.pyplot(fig, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<h3 style='text-align: center;'>Average Vote Count By Genre</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    genre_votes = filtered_df.groupby("genre")['vote_count'].mean().sort_values(ascending=False)
    sns.barplot(x=genre_votes.index, y=genre_votes.values, hue=genre_votes.index, palette="viridis", legend=False)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Votes")
    plt.xticks(rotation=70)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
 
with col2:
    st.markdown("<h3 style='text-align: center;'>Average Ratings By Movie Certification</h3>", unsafe_allow_html=True)
    avg_rate_cert = filtered_df.groupby("movie_certification")['ratings'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots()
    sns.barplot(x=avg_rate_cert.index, y=avg_rate_cert.values, hue=avg_rate_cert.index, palette="viridis", legend=False)
    ax.set_xlabel("Movie_Certification")
    ax.set_ylabel("Average Rating")
    plt.xticks(rotation=90)
    st.pyplot(fig)

with col3:
    st.markdown("<h3 style='text-align: center;'>Ratings By Movie Duration (< 300m)</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    # Scatter plot (cap at 300 minutes for clarity, data is skewed a movie with 51,420 minutes duration)
    sns.scatterplot(x="movie_duration", y="ratings", data=filtered_df[filtered_df['movie_duration'] <= 300],
                    alpha=0.7, color="purple")
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Rating")
    st.pyplot(fig)

with col4:
    st.markdown("<h3 style='text-align: center;'>Total Votes Per Year</h3>", unsafe_allow_html=True)
    yearly2 = filtered_df.groupby("year").agg({
    "vote_count":"sum"
    }).reset_index()
    fig, ax = plt.subplots()
    # Vote Count per Year
    sns.lineplot(x="year", y="vote_count", data=yearly2, marker="o", color="purple")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Vote Count")
    st.pyplot(fig)