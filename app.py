import streamlit as st
import os
import tempfile
import pandas as pd
import altair as alt
import io
from gtts import gTTS
from services.analyzer import analyze_film
from services.nyc_data import find_nyc_communities
from services.storyteller import generate_discovery_story
from services.marketing import generate_marketing_strategies
from services.marketing_video import generate_marketing_video

# Set Streamlit Page Config for Theme
st.set_page_config(
    page_title="CinemaMatch NYC", 
    page_icon="🎬", 
    layout="wide"
)

st.title("🎬 CinemaMatch NYC")
st.subheader("Discover your film’s genuine multi-faceted audience and the NYC venues where they gather.")
st.divider()

# Layout Setup - Clean columns relying natively on the new TOML theme!
left_col, right_col = st.columns([1, 1.6], gap="large")

with left_col:
    st.header("🎞️ Film Intake", divider="red")
    st.write("Upload your vision and metadata.")
    
    title = st.text_input("Film Title *")
    genre = st.selectbox("Primary Genre *", ["Action", "Drama", "Comedy", "Thriller", "Documentary", "Sci-Fi", "Horror", "Romance", "Foreign"])
    synopsis = st.text_area("Synopsis *", height=120)
    director_notes = st.text_area("Director Notes (Optional)", height=80, placeholder="Add context on your creative vision or specific communities you want to reach.")
    trailer_url = st.text_input("YouTube Trailer Link (Optional)")
    uploaded_poster = st.file_uploader("Upload Movie Poster *", type=["jpg", "jpeg", "png"])
    
    # Using type primary taps into our new TOML theme primaryColor
    submitted = st.button("Analyze & Match Communities", use_container_width=True, type="primary")

with right_col:
    if submitted:
        if not title or not genre or not synopsis or not uploaded_poster:
            st.error("Please fill in all the required fields (Title, Genre, Synopsis, Poster).")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(uploaded_poster.getbuffer())
                poster_path = tmp_file.name

            try:
                # Sequence 1: Analyzer
                with st.spinner('🧬 Extracting Multi-Dimensional Audience DNA...'):
                    dna = analyze_film(title, genre, synopsis, poster_path, trailer_url, director_notes)
                
                if dna:
                    st.header("🧠 Audience Profile Identified", divider="blue")
                    st.info(f"**Vibe & Tone:** {dna.get('tone', 'Not identified')}", icon="💡")
                    
                    themes = dna.get("community_themes", [])
                    if themes:
                        st.markdown("**Intersecting Communities:**")
                        for t in themes:
                            st.markdown(f"- {t}")

                    # Sequence 2: NYC Data
                    with st.spinner('🏙️ Cross-referencing Open NYC Venues...'):
                        orgs = find_nyc_communities(dna)
                        
                    # Sequence 3: Storyteller
                    with st.spinner('✍️ Synthesizing Discovery Story...'):
                        story, visual_prompt = generate_discovery_story(title, dna, orgs)
                    
                    # Sequence 4: Marketing Strategies
                    with st.spinner('🚀 Architecting Go-To-Market & Revenue Projections...'):
                        marketing_plan = generate_marketing_strategies(title, dna, orgs)
                    
                    # Story Presentation
                    st.header("📖 The Discovery Narrative", divider="green")
                    
                    # P1 Feature: Voice Storyteller
                    if story:
                        with st.spinner('🎙️ Narrating Discovery Story...'):
                            try:
                                tts = gTTS(text=story, lang='en')
                                audio_io = io.BytesIO()
                                tts.write_to_fp(audio_io)
                                st.audio(audio_io, format="audio/mp3")
                                st.caption("🔊 Listen to your film's discovery story.")
                            except Exception as e:
                                st.error(f"Could not generate voice narration: {e}")

                    st.write(story)
                    
                    # P0 Feature: Interleaved Visuals
                    st.info(f"🎨 **AI Visual Scene:** {visual_prompt}")
                    community_img_path = "assets/community_scene.png"
                    if os.path.exists(community_img_path):
                        st.image(community_img_path, caption="[AI Community Scene Preview]")
                    else:
                        st.image("https://images.unsplash.com/photo-1485846234645-a62644ef7467?q=80&w=2000&auto=format&fit=crop", caption="[AI Community Scene Preview]")
                    
                    # Venue Presentation
                    if orgs:
                        st.header("📍 Recommended Premier Venues", divider="orange")
                        
                        map_data = []
                        for org in orgs:
                            # Relying on native streamlist markdown formatting for speed and reliability
                            st.markdown(f"**{org['name']}**  \n🏢 {org['address']}, {org['borough']}")
                            st.write("") # Tiny spacer
                            
                            if org.get("latitude") and org.get("longitude"):
                                map_data.append({"name": org["name"], "lat": org["latitude"], "lon": org["longitude"]})
                                
                        if map_data:
                            st.subheader("🗺️ Local Operations Map")
                            df_map = pd.DataFrame(map_data)
                            st.map(df_map, zoom=10, use_container_width=True)
                            
                    # Marketing Presentation
                    if marketing_plan:
                        st.header("🚀 Go-To-Market Campaigns", divider="violet")
                        campaigns = marketing_plan.get("campaigns", [])
                        
                        for camp in campaigns:
                            with st.expander(f"**{camp.get('title', 'Campaign')}** — Est. Cost: ${camp.get('estimated_cost_usd', 0):,}"):
                                st.write(camp.get("description", ""))
                                st.markdown("**Execution Steps:**")
                                for step in camp.get("execution_steps", []):
                                    st.markdown(f"- {step}")

                        timeline = marketing_plan.get("revenue_timeline", [])
                        if timeline:
                            st.subheader("📈 6-Month Projected Revenue (USD)")
                            df_rev = pd.DataFrame(timeline)
                            if "month" in df_rev.columns and "revenue" in df_rev.columns:
                                df_rev.set_index("month", inplace=True)
                                st.area_chart(df_rev, use_container_width=True)

                        # New Side-by-Side Analytics Dashboards
                        demo_data = marketing_plan.get("demographic_engagement", [])
                        budget_data = marketing_plan.get("budget_breakdown", [])
                        
                        if demo_data and budget_data:
                            col1, col2 = st.columns(2, gap="large")
                            
                            with col1:
                                st.subheader("📊 Age Bracket Engagement")
                                df_demo = pd.DataFrame(demo_data)
                                if not df_demo.empty and "age_group" in df_demo.columns:
                                    df_demo.set_index("age_group", inplace=True)
                                    st.bar_chart(df_demo, use_container_width=True)
                                    
                            with col2:
                                st.subheader("🍩 Capital Allocation")
                                df_budget = pd.DataFrame(budget_data)
                                if not df_budget.empty and "category" in df_budget.columns:
                                    # Manually construct beautiful hollow donut graphic with Altair
                                    donut = alt.Chart(df_budget).mark_arc(innerRadius=60).encode(
                                        theta=alt.Theta(field="percentage", type="quantitative"),
                                        color=alt.Color(field="category", type="nominal", legend=alt.Legend(title="Medium", labelColor="#E2E8F0", titleColor="#4ECDC4", orient="bottom")),
                                        tooltip=[alt.Tooltip("category", title="Category"), alt.Tooltip("percentage", title="Allocation (%)")]
                                    ).properties(
                                        height=350,
                                        background="transparent"
                                    ).configure_view(strokeWidth=0)
                                    
                                    st.altair_chart(donut, use_container_width=True)

                        # Sequence 5: Final AI Marketing Video
                        st.divider()
                        st.header("🎬 Final AI Marketing Pitch", divider="rainbow")
                        with st.spinner('🎞️ Rendering AI Cinema Studio Short...'):
                            try:
                                video_path = generate_marketing_video(title, dna, orgs)
                                if os.path.exists(video_path):
                                    st.video(video_path)
                                    st.caption("📽️ AI-Generated Marketing Ad (Gemini + Imagen 3 + FFmpeg)")
                            except Exception as e:
                                st.error(f"Could not generate marketing video: {e}")

                else:
                    st.error("Failed to generate Audience DNA.")

            except Exception as e:
                st.error(f"Pipeline Error: {e}")
                
            finally:
                if os.path.exists(poster_path):
                    os.remove(poster_path)
    else:
        st.info("Upload your film materials on the left and hit Analyze to see the magic happen.", icon="🎬")
