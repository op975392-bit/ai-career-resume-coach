import os
import json
import re

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AI Career & Resume Coach",
    page_icon="🚀",
    layout="wide"
)

CUSTOM_CSS = """
<style>
    .main {
        background-color: #f7f9fc;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(135deg, #1d4ed8, #7c3aed);
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        margin-bottom: 8px;
        font-size: 42px;
    }

    .hero p {
        font-size: 18px;
        margin-bottom: 0;
    }

    .result-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-bottom: 16px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.04);
    }

    .score {
        font-size: 42px;
        font-weight: 800;
        color: #2563eb;
    }

    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background-color: #dbeafe;
        color: #1d4ed8;
        font-weight: 700;
        margin: 4px;
    }

    .warning {
        padding: 14px;
        border-left: 5px solid #f59e0b;
        background: #fffbeb;
        border-radius: 8px;
    }

    .success {
        padding: 14px;
        border-left: 5px solid #16a34a;
        background: #f0fdf4;
        border-radius: 8px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <h1>🚀 AI Career & Resume Coach</h1>
        <p>Get AI-powered resume feedback, keyword gap analysis, and personalized interview preparation.</p>
    </div>
    """,
    unsafe_allow_html=True
)

if not API_KEY:
    st.error(
        "GEMINI_API_KEY nahi mili. `.env` file mein API key add karke app restart karo."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

st.sidebar.header("Candidate Details")

candidate_name = st.sidebar.text_input(
    "Your name",
    placeholder="e.g. Rahul Sharma"
)

target_role = st.sidebar.text_input(
    "Target job role",
    placeholder="e.g. Cybersecurity Analyst"
)

experience_level = st.sidebar.selectbox(
    "Experience level",
    [
        "Student / Fresher",
        "Intern",
        "Entry-level",
        "Mid-level",
        "Experienced"
    ]
)

job_description = st.sidebar.text_area(
    "Job description",
    placeholder="Paste the job description here for better keyword matching...",
    height=180
)

resume_text = st.text_area(
    "Paste your resume text",
    placeholder=(
        "Paste your complete resume here...\n\n"
        "Example:\n"
        "Skills: Python, Linux, Wireshark...\n"
        "Projects: Built a phishing detection tool..."
    ),
    height=330
)

analyze_button = st.button(
    "🔍 Analyze My Resume",
    type="primary",
    use_container_width=True
)


def clean_json_text(text: str) -> str:
    """
    Removes markdown code fences if Gemini returns ```json ... ```.
    """
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def analyze_resume(resume, role, level, jd, name):
    prompt = f"""
You are an expert career coach, technical recruiter, and resume reviewer.

Analyze the candidate's resume for the target role.

Candidate name:
{name}

Target role:
{role}

Experience level:
{level}

Job description:
{jd if jd.strip() else "No job description provided. Infer the common requirements for the target role."}

Resume:
{resume}

Important instructions:
1. Do not invent experience, certifications, projects, or achievements.
2. Give practical and honest feedback.
3. Identify missing keywords only when they are relevant to the target role.
4. For every recommendation, explain how the candidate can improve.
5. Generate interview questions specific to the resume and target role.
6. Return only valid JSON matching the requested schema.
"""

    schema = {
        "type": "OBJECT",
        "properties": {
            "overall_score": {
                "type": "INTEGER",
                "description": "Resume score from 0 to 100"
            },
            "one_line_summary": {
                "type": "STRING"
            },
            "strengths": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "weaknesses": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "missing_keywords": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "role_alignment": {
                "type": "STRING"
            },
            "improvement_plan": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "priority": {
                            "type": "STRING",
                            "enum": ["High", "Medium", "Low"]
                        },
                        "area": {
                            "type": "STRING"
                        },
                        "recommendation": {
                            "type": "STRING"
                        },
                        "example": {
                            "type": "STRING"
                        }
                    },
                    "required": [
                        "priority",
                        "area",
                        "recommendation",
                        "example"
                    ]
                }
            },
            "interview_questions": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "question": {
                            "type": "STRING"
                        },
                        "why_asked": {
                            "type": "STRING"
                        },
                        "what_good_answer_should_include": {
                            "type": "STRING"
                        }
                    },
                    "required": [
                        "question",
                        "why_asked",
                        "what_good_answer_should_include"
                    ]
                }
            }
        },
        "required": [
            "overall_score",
            "one_line_summary",
            "strengths",
            "weaknesses",
            "missing_keywords",
            "role_alignment",
            "improvement_plan",
            "interview_questions"
        ]
    }

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.25,
            response_mime_type="application/json",
            response_schema=schema
        )
    )

    response_text = clean_json_text(response.text)
    return json.loads(response_text)


def show_bullets(items):
    if not items:
        st.write("No items found.")
        return

    for item in items:
        st.markdown(f"- {item}")


if analyze_button:
    if not candidate_name.strip():
        st.warning("Please enter your name.")
        st.stop()

    if not target_role.strip():
        st.warning("Please enter a target job role.")
        st.stop()

    if not resume_text.strip():
        st.warning("Please paste your resume text.")
        st.stop()

    if len(resume_text.strip()) < 100:
        st.warning("Resume thoda detailed paste karo, at least 100 characters.")
        st.stop()

    with st.spinner("Gemini is analyzing your resume..."):
        try:
            result = analyze_resume(
                resume=resume_text,
                role=target_role,
                level=experience_level,
                jd=job_description,
                name=candidate_name
            )

            st.session_state["analysis_result"] = result

        except json.JSONDecodeError:
            st.error(
                "Gemini response valid JSON format mein nahi aaya. Dobara try karo."
            )
            st.stop()

        except Exception as error:
            st.error(f"Analysis failed: {error}")
            st.stop()


if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]

    st.success("Resume analysis complete!")

    st.subheader(f"Analysis for {candidate_name}")

    score_col, summary_col = st.columns()[1][3]

    with score_col:
        st.markdown(
            f"""
            <div class="result-card">
                <div>Resume Score</div>
                <div class="score">{result["overall_score"]}/100</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col:
        st.markdown(
            f"""
            <div class="result-card">
                <h3>Quick Summary</h3>
                <p>{result["one_line_summary"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "💪 Strengths",
            "⚠️ Gaps",
            "🎯 Role Alignment",
            "🛠 Improvement Plan",
            "🎤 Interview Questions"
        ]
    )

    with tab1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("What you are doing well")
        show_bullets(result["strengths"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("Areas to improve")
        show_bullets(result["weaknesses"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("Missing or weak keywords")

        keywords = result.get("missing_keywords", [])

        if keywords:
            for keyword in keywords:
                st.markdown(
                    f'<span class="badge">{keyword}</span>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div class="success">No major keyword gaps detected.</div>',
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader(f"Alignment with {target_role}")
        st.write(result["role_alignment"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        for item in result["improvement_plan"]:
            priority = item["priority"]

            if priority == "High":
                box_class = "warning"
            else:
                box_class = "result-card"

            st.markdown(
                f"""
                <div class="{box_class}">
                    <h3>{item["area"]} — {priority} Priority</h3>
                    <p><b>Recommendation:</b> {item["recommendation"]}</p>
                    <p><b>Example:</b> {item["example"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    with tab5:
        for index, question in enumerate(
            result["interview_questions"],
            start=1
        ):
            with st.expander(f"{index}. {question['question']}"):
                st.write(
                    f"**Why this may be asked:** "
                    f"{question['why_asked']}"
                )
                st.write(
                    f"**A strong answer should include:** "
                    f"{question['what_good_answer_should_include']}"
                )

    st.download_button(
        label="⬇️ Download Analysis as JSON",
        data=json.dumps(result, indent=2),
        file_name="resume_analysis.json",
        mime="application/json",
        use_container_width=True
    )

else:
    st.info(
        "Apna resume paste karo, target role enter karo, aur analysis start karo."
    )

st.divider()

st.caption(
    "Built for Campulsy Hack Days | Gemini API powers resume analysis and interview preparation."
)