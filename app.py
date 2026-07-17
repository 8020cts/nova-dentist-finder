import streamlit as st
import urllib.parse

# 1. Page Configuration
st.set_page_config(
    page_title="NOVA Pediatric Dentistry Finder",
    page_icon="🦷",
    layout="centered"
)

st.title("r/nova Pediatric Dentistry Finder")
st.markdown("Select a timeframe below to search **r/nova** directly for pediatric dentist recommendations.")

# 2. Timeframe Selection
timeframe_options = {
    "Past 24 Hours": "day",
    "Past Week": "week",
    "Past Month": "month",
    "Past Year": "year",
    "All Time": "all"
}

selected_label = st.selectbox("Choose Timeframe:", list(timeframe_options.keys()), index=2)
timeframe = timeframe_options[selected_label]

st.markdown("---")

# 3. Build the Redirect Link
# This uses Reddit's native exact-match syntax for /r/nova
query = 'pediatric ("dentist" OR "dentistry")'
encoded_query = urllib.parse.quote(query)

# Native web search URL layout
reddit_search_url = f"https://www.reddit.com/r/nova/search/?q={encoded_query}&restrict_sr=1&sort=new&t={timeframe}"

# 4. Interactive Call-to-Action Card
with st.container(border=True):
    st.subheader("🚀 Ready to Search")
    st.write(f"This will launch an unfiltered search inside **r/nova** tracking posts from the **{selected_label.lower()}**.")
    
    # Render a clean button that opens in a new tab safely
    st.link_button("Open Search on Reddit ↗", reddit_search_url, type="primary", use_container_width=True)

st.info("💡 **Why this method?** Because your browser opens the link directly, Reddit will never throw a 403 or 400 error, ensuring you always see the freshest, real-time results.")
