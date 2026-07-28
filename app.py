import json
import os
import io
import streamlit as st
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="AI Personal Learning Mentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stButton>button {
            background-color: #FF4B4B;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
        }
        .card {
            background-color: #1E232A;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #30363D;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

class WeeklyPlan(BaseModel):
    week_number: int = Field(description="The week index")
    focus_area: str = Field(description="Main topic or focus for the week")
    topics_to_cover: list[str] = Field(description="List of specific sub-topics")
    practical_action: str = Field(description="Hands-on exercise or task for the week")

class RecommendedResource(BaseModel):
    title: str = Field(description="Name of the resource or platform")
    resource_type: str = Field(description="Type of resource")
    description: str = Field(description="Brief explanation of why it is useful")

class RoadmapSchema(BaseModel):
    student_name: str
    target_role: str
    summary: str = Field(description="Overview of the learning strategy and path")
    recommended_skills: list[str] = Field(description="Key skills required to bridge the gap")
    weekly_study_plan: list[WeeklyPlan] = Field(description="Structured weekly breakdown")
    suggested_projects: list[str] = Field(description="Portfolio project ideas to build")
    learning_resources: list[RecommendedResource] = Field(description="Curated learning materials")
    career_tips: list[str] = Field(description="Practical tips to prepare for job applications")
    interview_questions: list[str] = Field(description="Top practice interview questions for this role")

def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY is not configured.")
        st.stop()
    return genai.Client(api_key=api_key)

def generate_roadmap(name: str, skills: str, goal: str, hours: int, weeks: int) -> RoadmapSchema:
    client = get_gemini_client()
    
    system_instruction = """
    You are an expert EdTech AI Career & Learning Mentor. Your role is to build highly practical, 
    personalized learning roadmaps for students. You carefully bridge the gap between their current skills 
    and target career goals based on their weekly time commitment.
    """
    
    prompt = f"""
    Create a detailed, step-by-step learning roadmap for a student with the following profile:
    - Name: {name}
    - Current Skills: {skills}
    - Target Career Goal: {goal}
    - Daily Study Commitment: {hours} hours/day
    - Target Timeline: {weeks} weeks

    Ensure the weekly study plan explicitly spans {weeks} weeks and scales appropriately with their daily commitment.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=RoadmapSchema,
        ),
    )
    
    return RoadmapSchema.model_validate_json(response.text)

def create_pdf(roadmap: RoadmapSchema) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1E293B'))
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))

    elements = []
    
    elements.append(Paragraph(f"<b>Personalized Learning Roadmap: {roadmap.target_role}</b>", title_style))
    elements.append(Paragraph(f"Prepared for: <b>{roadmap.student_name}</b>", body_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

    elements.append(Paragraph("<b>Overview</b>", heading_style))
    elements.append(Paragraph(roadmap.summary, body_style))

    elements.append(Paragraph("<b>Recommended Skills to Acquire</b>", heading_style))
    elements.append(Paragraph(", ".join(roadmap.recommended_skills), body_style))

    elements.append(Paragraph("<b>Weekly Study Plan</b>", heading_style))
    for week in roadmap.weekly_study_plan:
        elements.append(Paragraph(f"<b>Week {week.week_number}: {week.focus_area}</b>", body_style))
        for topic in week.topics_to_cover:
            elements.append(Paragraph(f"• {topic}", body_style))
        elements.append(Paragraph(f"<i>Action: {week.practical_action}</i>", body_style))
        elements.append(Spacer(1, 6))

    elements.append(Paragraph("<b>Portfolio Projects</b>", heading_style))
    for proj in roadmap.suggested_projects:
        elements.append(Paragraph(f"• {proj}", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.sidebar.title("👤 Student Profile")

    name = st.sidebar.text_input("Full Name", value="Fahad")
    skills = st.sidebar.text_area("Current Skills", value="Basic Python, HTML/CSS, SQL")
    goal = st.sidebar.text_input("Target Career Goal", value="Junior AI Engineer")
    hours = st.sidebar.slider("Daily Study Commitment (Hours)", 1, 12, 2)
    weeks = st.sidebar.slider("Target Timeline (Weeks)", 1, 12, 4)

    st.title("🎓 AI Personal Learning Mentor")

    if st.sidebar.button("🚀 Generate Roadmap"):
        if "roadmap" in st.session_state:
            del st.session_state["roadmap"]
            
        with st.spinner("Generating your updated personalized plan..."):
            try:
                roadmap = generate_roadmap(name, skills, goal, hours, weeks)
                st.session_state["roadmap"] = roadmap
                st.rerun()
            except Exception as e:
                st.error(f"Error generating roadmap: {e}")

    if "roadmap" in st.session_state:
        roadmap: RoadmapSchema = st.session_state["roadmap"]

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"📍 Roadmap for {roadmap.student_name}: {roadmap.target_role}")
        with col2:
            pdf_bytes = create_pdf(roadmap)
            st.download_button(
                label="📄 Export as PDF",
                data=pdf_bytes,
                file_name=f"{roadmap.student_name.lower().replace(' ', '_')}_roadmap.pdf",
                mime="application/pdf"
            )

        st.markdown(f"**Overview:** {roadmap.summary}")
        st.divider()

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("### 🎯 Key Skills to Master")
            for skill in roadmap.recommended_skills:
                st.markdown(f"- **{skill}**")

        with col_right:
            st.markdown("### 🛠️ Portfolio Projects")
            for project in roadmap.suggested_projects:
                st.markdown(f"- {project}")

        st.divider()

        st.markdown("### 📅 Weekly Study Plan")
        week_tabs = st.tabs([f"Week {w.week_number}" for w in roadmap.weekly_study_plan])
        
        for tab, week in zip(week_tabs, roadmap.weekly_study_plan):
            with tab:
                st.markdown(f"#### Focus: {week.focus_area}")
                st.markdown("**Topics to Cover:**")
                for topic in week.topics_to_cover:
                    st.markdown(f"- {topic}")
                st.info(f"💡 **Practical Task:** {week.practical_action}")

        st.divider()

        col_res, col_tips = st.columns(2)
        with col_res:
            st.markdown("### 📚 Recommended Resources")
            for res in roadmap.learning_resources:
                st.markdown(f"**[{res.resource_type}] {res.title}**")
                st.caption(res.description)

        with col_tips:
            st.markdown("### 💡 Career & Interview Preparation")
            st.markdown("**Career Tips:**")
            for tip in roadmap.career_tips:
                st.markdown(f"- {tip}")
            
            st.markdown("**Sample Interview Questions:**")
            for q in roadmap.interview_questions:
                st.markdown(f"- *\"{q}\"*")

        st.divider()
        with st.expander("🔍 View Raw JSON Response"):
            st.json(roadmap.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
