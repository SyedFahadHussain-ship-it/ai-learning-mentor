import os
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini Client
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Missing GEMINI_API_KEY in .env file.")
        st.stop()
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# --- 1. PYDANTIC SCHEMAS ---
class Resource(BaseModel):
    title: str = Field(description="Name of course or documentation")
    type: str = Field(description="Type: Free Course, Paid Course, Book, Doc, Video")
    link: str = Field(description="URL or search query")

class Project(BaseModel):
    title: str = Field(description="Project title")
    description: str = Field(description="Short summary of project and skills applied")

class WeeklyPlan(BaseModel):
    week_number: int = Field(description="Week index (e.g., 1)")
    focus_topic: str = Field(description="Main topic for the week")
    daily_breakdown: List[str] = Field(description="List of daily tasks for this week")

class LearningRoadmap(BaseModel):
    student_name: str
    target_role: str
    recommended_skills: List[str] = Field(description="Key skills to acquire")
    weekly_plan: List[WeeklyPlan] = Field(description="Chronological weekly plan")
    suggested_projects: List[Project] = Field(description="Portfolio projects")
    learning_resources: List[Resource] = Field(description="Learning links/materials")
    career_tips: List[str] = Field(description="Advice for landing the role")

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="AI Personal Learning Mentor", page_icon="🎓", layout="wide")

st.title("🎓 AI Personal Learning Mentor")
st.caption("Generate tailored learning roadmaps aligned with your career goals.")

with st.sidebar:
    st.header("👤 Profile & Preferences")
    name = st.text_input("Full Name", value="fahad")
    current_skills = st.text_area("Current Skills", value="Basic Python, HTML/CSS, SQL")
    career_goal = st.text_input("Target Career Goal", value="Junior AI Engineer")
    daily_hours = st.slider("Daily Study Commitment (Hours)", min_value=1, max_value=8, value=2)
    weeks_duration = st.slider("Target Duration (Weeks)", min_value=2, max_value=12, value=4)
    
    submit_btn = st.button("🚀 Generate Roadmap", type="primary", use_container_width=True)

if submit_btn:
    if not current_skills or not career_goal:
        st.warning("Please fill in both current skills and career goal.")
    else:
        with st.spinner("Analyzing skill gaps and generating roadmap..."):
            prompt = f"""
            Generate a personalized learning roadmap for:
            - Student Name: {name}
            - Current Skills: {current_skills}
            - Career Goal: {career_goal}
            - Available Study Time: {daily_hours} hours per day
            - Target Duration: {weeks_duration} weeks
            """

            try:
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LearningRoadmap,
                        temperature=0.3,
                        system_instruction="You are an expert EdTech Career Mentor and Technical Curriculum Designer."
                    )
                )

                # Direct object parsing from Gemini SDK
                st.session_state['roadmap'] = response.parsed

            except Exception as e:
                st.error(f"Error generating roadmap: {e}")

if 'roadmap' in st.session_state:
    roadmap = st.session_state['roadmap']

    st.success(f"Roadmap Generated for **{roadmap.student_name}**! Target Role: **{roadmap.target_role}**")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Weekly Plan", "🛠️ Key Skills", "🚀 Projects", "📚 Resources", "💡 Career Tips"])

    with tab1:
        st.subheader("Weekly Study Schedule")
        for week in roadmap.weekly_plan:
            with st.expander(f"Week {week.week_number}: {week.focus_topic}", expanded=True):
                for day_task in week.daily_breakdown:
                    st.write(f"- {day_task}")

    with tab2:
        st.subheader("Recommended Skills to Learn")
        cols = st.columns(3)
        for idx, skill in enumerate(roadmap.recommended_skills):
            cols[idx % 3].info(f"✔ **{skill}**")

    with tab3:
        st.subheader("Suggested Portfolio Projects")
        for proj in roadmap.suggested_projects:
            st.markdown(f"### 📌 {proj.title}")
            st.write(proj.description)
            st.divider()

    with tab4:
        st.subheader("Curated Learning Resources")
        for res in roadmap.learning_resources:
            st.markdown(f"- **[{res.type}]** [{res.title}]({res.link})")

    with tab5:
        st.subheader("Career & Interview Tips")
        for tip in roadmap.career_tips:
            st.write(f"💡 {tip}")