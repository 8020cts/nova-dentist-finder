import streamlit as st
import requests
import datetime

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="NOVA Pediatric Dentistry Finder",
    page_icon="🦷",
    layout="centered"
)

st.title("r/nova Pediatric Dentistry Finder")
st.markdown("Find recent pediatric dental recommendations in Northern Virginia.")

# 2. Sidebar Filters
st.sidebar.header("Search Filters")

# Map readable options to Reddit's API timeframe parameters
timeframe_options = {
    "Past 24 Hours": "day",
    "Past Week": "week",
    "Past Month": "month",
    "Past Year": "year",
    "All Time": "all"
}

selected_label = st.sidebar.selectbox("Select Timeframe", list(timeframe_options.keys()), index=2)
timeframe = timeframe_options[selected_label]

# 3. Search Execution
if st.button("Search r/nova", type="primary"):
    subreddit = "nova"
    query = 'pediatric "dentist" OR "dentistry"'
    url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=on&sort=new&t={timeframe}"
    
    # Custom User-Agent to avoid Reddit API rate-limiting blocks
    headers = {"User-Agent": "StreamlitPediatricDentistryFinder/1.0"}
    
    with st.spinner("Searching Reddit..."):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                
                if not posts:
                    st.info(f"No recent posts found within the **{selected_label}**.")
                else:
                    st.success(f"Found {len(posts)} posts from the {selected_label.lower()}!")
                    
                    # 4. Render Results
                    for post in posts:
                        post_data = post["data"]
                        title = post_data["title"]
                        permalink = post_data["permalink"]
                        post_url = f"https://reddit.com{permalink}"
                        author = post_data["author"]
                        score = post_data["score"]
                        comments = post_data["num_comments"]
                        
                        # Convert UTC timestamp to readable date
                        created_date = datetime.datetime.fromtimestamp(post_data["created_utc"]).strftime('%Y-%m-%d')
                        
                        # Display each post inside a clean card-style container
                        with st.container(border=True):
                            st.markdown(f"### [{title}]({post_url})")
                            st.markdown(
                                f"📅 **Posted:** {created_date} | "
                                f"👤 **By:** u/{author} | "
                                f"👍 **Score:** {score} | "
                                f"💬 **Comments:** {comments}"
                            )
            else:
                st.error(f"Failed to fetch data from Reddit. (Error Code: {response.status_code})")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
