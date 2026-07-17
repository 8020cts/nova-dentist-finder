import streamlit as st
import requests
from datetime import datetime, timezone, timedelta

# Page configurations
st.set_page_config(
    page_title="r/nova Pediatric Dentist Finder",
    page_icon="🦷",
    layout="wide"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-title { font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem; }
    .post-card { 
        padding: 1.5rem; 
        border-radius: 10px; 
        border: 1px solid #E5E7EB; 
        background-color: #F9FAFB; 
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .post-title { font-size: 1.2rem; font-weight: 600; color: #2563EB !important; text-decoration: none; }
    .post-title:hover { text-decoration: underline; }
    .post-meta { font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem; margin-bottom: 0.8rem; }
    .post-snippet { font-size: 0.95rem; color: #374151; background: #FFF; padding: 0.8rem; border-left: 3px solid #3B82F6; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<div class="main-title">🦷 r/nova Pediatric Dentist Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Instantly scan Northern Virginia\'s subreddit via Google Indexing for kids\' dental practices.</div>', unsafe_allow_html=True)

# Sidebar UI
st.sidebar.header("🔍 Search Filters")

# 1. Date Range Selector
days_back = st.sidebar.slider(
    "How fresh should the recommendations be?",
    min_value=30,
    max_value=365 * 3,  
    value=365,          
    step=30,
    help="Select how far back Google should look for relevant threads."
)

# Translate days back into a Google search timeline parameter (e.g., 'm12' for 12 months)
if days_back <= 30:
    date_param = "m1"
elif days_back <= 180:
    date_param = "m6"
elif days_back <= 365:
    date_param = "y1"
else:
    date_param = "y3"

# 2. Query Configuration
query_options = [
    "pediatric dentist OR pediatric dentistry OR kid dentist",
    "dentist recommendation kids OR toddler dentist",
    "custom"
]
selected_query = st.sidebar.selectbox("Choose search keywords:", query_options)

if selected_query == "custom":
    search_query = st.sidebar.text_input("Custom Search Query:", "pediatric dentist")
else:
    search_query = selected_query

st.sidebar.markdown("---")
st.sidebar.markdown(
    "💡 *Cloud Note: This app routes through Google's open indexes to safely bypass Reddit's corporate cloud blocking.*"
)

# Fetch Action
if st.button("Search Subreddit", type="primary"):
    with st.spinner("Searching Reddit index via cloud gateway..."):
        
        # We target Reddit r/nova specifically using Google syntax
        full_query = f"site:reddit.com/r/nova {search_query}"
        
        # Using a reliable public search wrapper that won't give a 403 on Streamlit Cloud
        url = "https://html.duckduckgo.com/html/"
        params = {"q": full_query}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('div', class_='result__body')
                
                matching_posts = []
                for res in results:
                    title_a = res.find('a', class_='result__url')
                    snippet_div = res.find('a', class_='result__snippet')
                    
                    if title_a and snippet_div:
                        title = title_a.text.strip()
                        raw_link = title_a['href']
                        
                        # Clean up redirect URLs to point directly to Reddit
                        if "uddg=" in raw_link:
                            actual_url = urllib.parse.unquote(raw_link.split("uddg=")[1].split("&")[0])
                        else:
                            actual_url = raw_link
                            
                        snippet = snippet_div.text.strip()
                        
                        # Make sure it's actually an r/nova thread link
                        if "reddit.com/r/nova" in actual_url and "/comments/" in actual_url:
                            matching_posts.append({
                                "title": title.replace(" : r/nova", "").replace(" - Reddit", ""),
                                "url": actual_url,
                                "snippet": snippet
                            })
                
                # Render Results UI
                if matching_posts:
                    st.success(f"Found {len(matching_posts)} indexed threads matching your criteria!")
                    
                    for i, post in enumerate(matching_posts, 1):
                        card_html = f"""
                        <div class="post-card">
                            <a class="post-title" href="{post['url']}" target="_blank">{i}. {post['title']}</a>
                            <div class="post-meta">
                                🔗 Source: Reddit r/nova
                            </div>
                            <div class="post-snippet"><i>"{post['snippet']}"</i></div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.warning("No clear threads found in the search index. Try changing your search keywords!")
                    
            else:
                st.error(f"Search gateway returned status code: {response.status_code}")
                
        except Exception as e:
            st.error(f"An error occurred while connecting to the cloud gateway: {str(e)}")
else:
    st.info("👈 Set your search keywords on the left, then click 'Search Subreddit' to safely load recommendations.")
