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
st.markdown("Find recent pediatric dental recommendations in Northern Virginia via Google's Reddit index.")

# 2. Sidebar Filters
st.sidebar.header("Search Filters")

# Map human-readable selections to Google's date-range query parameters
timeframe_options = {
    "Past 24 Hours": "qdr:d",
    "Past Week": "qdr:w",
    "Past Month": "qdr:m",
    "Past Year": "qdr:y",
    "All Time": ""
}

selected_label = st.sidebar.selectbox("Select Timeframe", list(timeframe_options.keys()), index=2)
tbs_param = timeframe_options[selected_label]

# 3. Search Execution
if st.button("Search r/nova", type="primary"):
    # Target pediatric dentists strictly within r/nova
    query = 'site:reddit.com/r/nova "pediatric" (dentist OR dentistry)'
    
    # We use Google's RSS search feed which bypasses the Reddit 403 blocks completely
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}&tbm=blg&output=rss"
    if tbs_param:
        url += f"&tbs={tbs_param}"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    with st.spinner("Searching for recommendations..."):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Parse the XML response from the RSS feed
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                if not items:
                    st.info(f"No recent threads found matching within the **{selected_label}**.")
                else:
                    st.success(f"Found matches via index from the {selected_label.lower()}!")
                    
                    for item in items:
                        # Extract and clean data fields
                        raw_title = item.find("title").text if item.find("title") is not None else "No Title"
                        # Strip extra " - Reddit" trailing tags Google adds
                        clean_title = raw_title.split(" : nova")[0].split(" - reddit")[0].split(" - Reddit")[0]
                        
                        post_url = item.find("link").text if item.find("link") is not None else "#"
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else "Unknown Date"
                        snippet = item.find("description").text if item.find("description") is not None else ""
                        
                        # Format dates into a cleaner readable string
                        if pub_date != "Unknown Date" and "," in pub_date:
                            pub_date = " ".join(pub_date.split(" ")[1:4])

                        # Render Results Card
                        with st.container(border=True):
                            st.markdown(f"### [{unescape(clean_title)}]({post_url})")
                            st.markdown(f"📅 **Indexed Date:** {pub_date}")
                            if snippet:
                                # Clean up HTML tags if any are embedded in the search snippet
                                clean_snippet = unescape(snippet).replace("<b>", "**").replace("</b>", "**")
                                st.markdown(f"*{clean_snippet}*")
            else:
                st.error(f"Failed to pull results. Google Search index returned: {response.status_code}")
                
        except Exception as e:
            st.error(f"An unexpected parsing error occurred: {e}")
