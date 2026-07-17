import streamlit as st
import urllib.parse

st.title("🦷 NOVA Pediatric Dentist Finder")
st.write("Find recent recommendations from r/nova.")

# User inputs
timeframe = st.selectbox("How recent?", ["day", "week", "month", "year", "all"])
query = 'pediatric ("dentist" OR "dentistry")'

# Build the URL that Reddit natively supports
# This is NOT scraping; it's just a standard web link.
base_url = "https://www.reddit.com/r/nova/search/"
params = {
    "q": query,
    "restrict_sr": "1",
    "sort": "new",
    "t": timeframe
}
search_url = f"{base_url}?{urllib.parse.urlencode(params)}"

if st.button("Search on Reddit"):
    # st.link_button makes the user's browser handle the request
    st.link_button("View Results on Reddit", search_url)
