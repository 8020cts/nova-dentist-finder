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
st.markdown('<div class="sub-title">Instantly scan Northern Virginia\'s subreddit for the most recommended kids\' dental practices.</div>', unsafe_allow_html=True)

# Sidebar UI
st.sidebar.header("🔍 Search Filters")

# 1. Date Range Selector (Days back)
days_back = st.sidebar.slider(
    "How fresh should the recommendations be?",
    min_value=14,
    max_value=365 * 3,  # Up to 3 years
    value=365,         # Default to last 1 year
    step=14,
    help="Select how far back to search. Pediatric dentist names remain highly relevant even if a post is up to a year old."
)
cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

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
    "💡 *Tip: Northern Virginia (r/nova) is incredibly active. Post history from the last 180 to 365 days usually yields the most up-to-date regional feedback.*"
)

# Fetch Action
if st.button("Search Subreddit", type="primary"):
    with st.spinner("Scanning r/nova..."):
        # Reddit Search JSON Endpoint
        url = "https://www.reddit.com/r/nova/search.json"
        params = {
            "q": search_query,
            "restrict_sr": "on",
            "sort": "new",      # Fetch newest first so we can filter down to our target date range
            "limit": 100        # Max results Reddit allows per request
        }
        
        # We must use a authentic-looking User-Agent to bypass standard scraper blockers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                
                matching_posts = []
                for post in posts:
                    pdata = post["data"]
                    created_utc = pdata.get("created_utc")
                    
                    if created_utc:
                        post_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)
                        if post_date >= cutoff_date:
                            matching_posts.append({
                                "title": pdata.get("title"),
                                "url": f"https://www.reddit.com{pdata.get('permalink')}",
                                "author": pdata.get("author"),
                                "score": pdata.get("score"),
                                "comments": pdata.get("num_comments"),
                                "date_str": post_date.strftime("%B %d, %Y"),
                                "text": pdata.get("selftext", "")
                            })
                
                # Render Results
                if matching_posts:
                    st.success(f"Found {len(matching_posts)} highly-relevant threads from the last {days_back} days!")
                    
                    for i, post in enumerate(matching_posts, 1):
                        snippet = post['text'][:300] + "..." if len(post['text']) > 300 else post['text']
                        
                        card_html = f"""
                        <div class="post-card">
                            <a class="post-title" href="{post['url']}" target="_blank">{i}. {post['title']}</a>
                            <div class="post-meta">
                                📅 Posted on: <b>{post['date_str']}</b> &nbsp;|&nbsp; 
                                💬 Comments: <b>{post['comments']}</b> &nbsp;|&nbsp; 
                                👤 User: u/{post['author']} &nbsp;|&nbsp; 
                                👍 Score: {post['score']}
                            </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        if snippet:
                            st.markdown(f'<div class="post-snippet"><i>"{snippet}"</i></div>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                else:
                    st.warning("No recent threads matched. Try adjusting the slider in the sidebar to search further back!")
            
            elif response.status_code == 429:
                st.error("Too Many Requests: Reddit's public feed is temporarily rate-limiting us. Try again in 60 seconds.")
            else:
                st.error(f"Could not connect to Reddit (Status Code: {response.status_code}).")
                
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
else:
    # Landing instructions
    st.info("👈 Set your date range and search keywords on the left, then click 'Search Subreddit' to load recommendations.")
