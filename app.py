import streamlit as st
import requests
import xml.etree.ElementTree as ET
from html import unescape

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="NOVA Pediatric Dentistry Finder",
    page_icon="🦷",
    layout="centered"
)

st.title("r/nova Pediatric Dentistry Finder")
st.markdown("Find recent pediatric dental recommendations in Northern Virginia safely via Google News Index.")

# 2. Sidebar Filters
st.sidebar.header("Search Filters")

# Google News RSS uses the "when:" operator directly inside the query string
timeframe_options = {
    "Past 24 Hours": "when:1d",
    "Past Week": "when:7d",
    "Past Month": "when:30d",
    "Past Year": "when:1y",
    "All Time": ""
}

selected_label = st.sidebar.selectbox("Select Timeframe", list(timeframe_options.keys()), index=2)
timeframe_query = timeframe_options[selected_label]

# 3. Search Execution
if st.button("Search r/nova", type="primary"):
    # Target pediatric dentists strictly within r/nova
    base_query = 'site:reddit.com/r/nova "pediatric" (dentist OR dentistry)'
    
    # Append the modern timeline constraint if selected
    full_query = f"{base_query} {timeframe_query}".strip()
    
    # Use the stable Google News RSS endpoint
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(full_query)}&hl=en-US&gl=US&ceid=US:en"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    with st.spinner("Searching for recommendations..."):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Parse the XML response
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                if not items:
                    st.info(f"No recent threads found matching within the **{selected_label}**.")
                else:
                    st.success(f"Found matches via index from the {selected_label.lower()}!")
                    
                    for item in items:
                        raw_title = item.find("title").text if item.find("title") is not None else "No Title"
                        # Clean up Google's source tags appended to the titles
                        clean_title = raw_title.split(" - ")[0].split(" : ")[0]
                        
                        post_url = item.find("link").text if item.find("link") is not None else "#"
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else "Unknown Date"
                        
                        if pub_date != "Unknown Date" and "," in pub_date:
                            pub_date = " ".join(pub_date.split(" ")[1:4])

                        # Render Results Card
                        with st.container(border=True):
                            st.markdown(f"### [{unescape(clean_title)}]({post_url})")
                            st.markdown(f"📅 **Indexed Date:** {pub_date}")
            else:
                st.error(f"Failed to pull results. Google Index returned status code: {response.status_code}")
                st.info("Tip: If running frequently from the cloud, the hosting platform's IP may be temporarily throttled.")
                
        except Exception as e:
            st.error(f"An unexpected parsing error occurred: {e}")
