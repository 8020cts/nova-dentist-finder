import streamlit as st
import requests
from html import unescape

# 1. Dashboard Layout
st.set_page_config(page_title="NOVA Pediatric Dentist Search", page_icon="🦷")
st.title("🦷 r/nova Pediatric Dentistry Finder")
st.markdown("Displays recent live Reddit recommendation threads right here inside your dashboard.")

# 2. Assign Google Credentials
# Paste the keys you generated in Step 1 here
API_KEY = "AIzaSyDnIYU1_2cYeIy3eKr6b2AHO1N-mzwBwDI"
SEARCH_ENGINE_ID = "649b30909dff740e0"

# 3. Choose Date Range Filter
st.sidebar.header("Search Adjustments")
timeframe_options = {
    "Past 24 Hours": "d",
    "Past Week": "w",
    "Past Month": "m",
    "Past Year": "y",
    "All Historical Data": ""
}
selected_label = st.sidebar.selectbox("Select Timeframe", list(timeframe_options.keys()), index=2)
date_filter = timeframe_options[selected_label]

# 4. Pull and Display Live Data
if st.button("Fetch Live Recommendations", type="primary"):
    if API_KEY == "YOUR_GOOGLE_API_KEY_HERE" or SEARCH_ENGINE_ID == "YOUR_SEARCH_ENGINE_ID_HERE":
        st.warning("Please input your actual Google API Key and Search Engine ID into the app script first!")
        st.stop()

    # Formulate precise logic targeted exactly to r/nova's index
    search_query = '"pediatric" (dentist OR dentistry)'
    
    # Official API Endpoint
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": search_query
    }
    # Append Google's structural time filter parameter if selected
    if date_filter:
        params["sort"] = f"date:r:20200101:20261231" # Date range capability
        params["dateRestrict"] = date_filter

    with st.spinner("Retrieving live threads from index..."):
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                results_data = response.json()
                items = results_data.get("items", [])
                
                if not items:
                    st.info(f"No specific matches found matching that query within the **{selected_label.lower()}**.")
                else:
                    st.success(f"Successfully loaded the most relevant matches found on r/nova!")
                    
                    for item in items:
                        # Format the text segments natively
                        title = item.get("title", "Reddit Thread").split(" : nova")[0].split(" - reddit")[0]
                        link = item.get("link")
                        snippet = item.get("snippet", "")
                        
                        # Render inside a neat border container directly on your screen
                        with st.container(border=True):
                            st.markdown(f"### [{unescape(title)}]({link})")
                            if snippet:
                                st.markdown(f"👉 *{unescape(snippet)}*")
            else:
                st.error(f"Google Search API returned an error frame: {response.status_code}")
                st.json(response.json()) # Diagnostic log output
                
        except Exception as e:
            st.error(f"Could not connect to the search container index: {e}")
