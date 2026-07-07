from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from app.tools.industry_map import infer_industry, load_industry_knowledge
from app.tools.job_signals import extract_job_signals
from app.tools.privacy import redact_personal_info


APP_TITLE = "CareerProof Agent"
APP_SUBTITLE = "AI Career Concierge for Evidence-Based Interview Strategy"
DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-flash-latest"


st.set_page_config(
    page_title="CareerProof Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
:root {
  --careerproof-blue: #2563eb;
  --careerproof-purple: #7c3aed;
  --careerproof-teal: #06b6d4;
  --careerproof-bg: #0f172a;
}
.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1280px;
}
.hero-card {
  padding: 1.5rem 1.75rem;
  border-radius: 24px;
  background: radial-gradient(circle at top left, rgba(37,99,235,.28), transparent 34%),
              radial-gradient(circle at top right, rgba(124,58,237,.25), transparent 34%),
              linear-gradient(135deg, #0f172a 0%, #111827 52%, #0f172a 100%);
  color: white;
  border: 1px solid rgba(255,255,255,.12);
  box-shadow: 0 20px 60px rgba(15, 23, 42, .20);
}
.hero-title {
  font-size: 2.35rem;
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: -0.04em;
  margin-bottom: .35rem;
}
.hero-subtitle {
  font-size: 1.05rem;
  color: rgba(255,255,255,.82);
  max-width: 840px;
}
.pill {
  display: inline-block;
  margin-right: .4rem;
  margin-top: .45rem;
  padding: .25rem .7rem;
  border-radius: 999px;
  background: rgba(255,255,255,.11);
  border: 1px solid rgba(255,255,255,.15);
  color: rgba(255,255,255,.9);
  font-size: .82rem;
}
.metric-card {
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid rgba(148,163,184,.25);
  background: rgba(248,250,252,.72);
}
.small-muted {
  color: #64748b;
  font-size: .9rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def cached_industries() -> dict[str, Any]:
    return load_industry_knowledge()


def get_secret(name: str, default: str | None = None) -> str | None:
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)


def has_api_key() -> bool:
    return bool(get_secret("GOOGLE_API_KEY") or get_secret("GEMINI_API_KEY"))


def build_prompt(
    target_role: str,
    company: str,
    industry: str,
    job_description: str,
    candidate_profile: str,
    output_depth: str,
) -> tuple[str, dict[str, Any]]:
    clean_jd = redact_personal_info(job_description)
    clean_profile = redact_personal_info(candidate_profile)
    signals = extract_job_signals(clean_jd)
    industry_context = infer_industry(clean_jd, industry if industry != "Auto-detect" else None)

    prompt = f"""
You are CareerProof Agent, a personal AI career concierge.

Your goal is not to fabricate interview answers.
Your goal is to help a job seeker build credible, evidence-based interview strategy.

Target role: {target_role}
Company: {company or "Unknown"}
Requested industry: {industry}
Output depth: {output_depth}

Detected job signals:
{json.dumps(signals, indent=2)}

Industry intelligence:
{json.dumps(industry_context, indent=2)}

Job description:
{clean_jd}

Candidate profile:
{clean_profile}

Create a structured career intelligence report with exactly these sections:

1. Executive Summary
2. Role Problem Map
- What business problem is this role likely hired to solve?
- What decisions will this person influence?
- What does the hiring manager likely care about?

3. Industry Context
- Business model
- Key metrics
- Common role-specific interview angles

4. Hiring Evidence Matrix
Create a markdown table with:
- Hiring signal
- What the hiring manager needs proof of
- Candidate evidence
- Confidence: strong / medium / weak
- Missing proof or risk

5. Candidate Proof Mapping
Map only the candidate's real experience to this role. Do not invent experience.

6. Interview Story Bank
Create 4 stories using:
- Situation
- Business problem
- Action
- Tools / analysis
- Result
- Why it matters for this role

7. Likely Interview Questions
Include behavioral, business case, analytics case, and technical questions where relevant.

8. Gap Analysis
Be honest about weak or missing evidence.

9. 7-Day Prep Plan
Give a practical day-by-day plan.

10. Questions to Ask Interviewer
Suggest 5 thoughtful questions.

Rules:
- Never invent experience.
- If evidence is missing, say it is missing.
- Avoid generic advice.
- Be industry-specific.
- Be useful to Business, Data, BI, Product, Ops, Strategy, and Consulting candidates.
""".strip()

    metadata = {
        "signals": signals,
        "industry_context": industry_context,
        "clean_jd": clean_jd,
        "clean_profile": clean_profile,
    }
    return prompt, metadata


def deterministic_report(
    target_role: str,
    company: str,
    industry: str,
    job_description: str,
    candidate_profile: str,
    output_depth: str,
) -> tuple[str, dict[str, Any]]:
    prompt, metadata = build_prompt(
        target_role,
        company,
        industry,
        job_description,
        candidate_profile,
        output_depth,
    )
    signals = metadata["signals"]
    ctx = metadata["industry_context"]
    knowledge = ctx["knowledge"]
    tools = ", ".join(signals.get("tools", [])) or "not explicitly detected"
    responsibilities = ", ".join(signals.get("responsibilities", [])) or "not explicitly detected"
    metrics = ", ".join(knowledge.get("metrics", [])[:8])
    problems = knowledge.get("business_problems", [])[:4]
    cases = knowledge.get("interview_cases", [])[:4]
    hiring_signals = knowledge.get("hiring_signals", [])[:5]

    report = f"""
## Executive Summary

CareerProof detected **{ctx['matched_industry']}** as the most relevant industry context and **{signals.get('role_family')}** as the likely role family. This report is running in deterministic demo mode because no Gemini API key is configured in Streamlit secrets.

## Role Problem Map

This role is likely hired to solve problems such as:

{chr(10).join(f'- {p}' for p in problems)}

The hiring manager will likely care about whether the candidate can translate ambiguous business needs into metrics, analysis, stakeholder-ready recommendations, and credible execution.

## Industry Context

**Business model signals:** {', '.join(knowledge.get('business_model', [])[:6])}

**Common metrics:** {metrics}

**Detected JD tools:** {tools}

**Detected responsibilities:** {responsibilities}

## Hiring Evidence Matrix

| Hiring signal | What they need proof of | Candidate evidence to look for | Confidence |
|---|---|---|---|
{chr(10).join(f'| {signal} | Can demonstrate this capability in a business context | Map a real project, metric, or stakeholder example from the profile | Medium |' for signal in hiring_signals)}

## Candidate Proof Mapping

Use the candidate profile to identify concrete examples with metrics. Strong examples should include business context, action, tools, and measurable result.

## Interview Story Bank

1. **Business ambiguity story** — Describe a situation where the candidate clarified a messy business problem.
2. **Dashboard / insight story** — Explain how the candidate turned data into stakeholder action.
3. **Process improvement story** — Show operational impact with before/after metrics.
4. **Cross-functional story** — Demonstrate communication across business and technical teams.

## Likely Interview Questions

{chr(10).join(f'- {c}' for c in cases)}

## Gap Analysis

- Add more measurable outcomes where possible.
- Prepare one story for stakeholder conflict or ambiguity.
- Prepare one technical example using SQL / analytics logic.
- Connect every story to the business model and metrics of {ctx['matched_industry']}.

## 7-Day Prep Plan

| Day | Focus |
|---|---|
| 1 | Decode JD and company business model |
| 2 | Build evidence matrix |
| 3 | Draft 4 interview stories |
| 4 | Practice role-specific analytics questions |
| 5 | Prepare technical / SQL examples |
| 6 | Mock interview and refine weak answers |
| 7 | Final polish and interviewer questions |

## Questions to Ask Interviewer

1. What business problem is this role expected to solve in the first 6 months?
2. Which metrics define success for this team?
3. What stakeholder groups does this role work with most often?
4. What data or process challenges make this role difficult?
5. What separates strong candidates from average candidates for this role?
""".strip()
    return report, metadata


def gemini_report(prompt: str, model_name: str) -> str:
    api_key = get_secret("GOOGLE_API_KEY") or get_secret("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY or GEMINI_API_KEY.")
    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        return getattr(response, "text", "") or str(response)
    except Exception as exc:  # noqa: BLE001
        if model_name != FALLBACK_MODEL:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model=FALLBACK_MODEL, contents=prompt)
            return getattr(response, "text", "") or str(response)
        raise exc


def get_industry_options() -> list[str]:
    return ["Auto-detect", *sorted(cached_industries().keys())]


def sample_inputs() -> dict[str, dict[str, str]]:
    return {
        "Healthcare BA": {
            "target_role": "Business Analyst",
            "company": "Healthcare operations company",
            "industry": "Healthcare Operations / HealthTech",
            "job_description": "We are looking for a Business Analyst to build dashboards, define KPIs, work with stakeholders, improve reporting processes, and translate data into recommendations. SQL, Excel, Power BI, and stakeholder communication are required.",
            "candidate_profile": "Candidate has experience at Uber Taiwan in operations, ERP implementation, cross-functional coordination with Product, Sales, CRM, PR, Legal, SKU expansion from 1000 to 3000, complaint rate reporting from 5% to 1%, and VisualSoft dashboard work using Python and Power BI improving decision efficiency by 30%.",
        },
        "FinTech Risk Analyst": {
            "target_role": "Risk Analyst",
            "company": "FinTech lending company",
            "industry": "FinTech / Credit / Lending",
            "job_description": "Analyze approval rate, default rate, fraud risk, and repayment behavior. SQL and Python preferred. Build dashboards for credit risk and portfolio monitoring.",
            "candidate_profile": "Candidate has operations analytics experience, defect reporting, Power BI dashboarding, Python automation, and cross-functional stakeholder work, but limited direct credit-risk experience.",
        },
        "Marketplace Analyst": {
            "target_role": "Marketplace Analyst",
            "company": "Two-sided marketplace",
            "industry": "Marketplace Platforms",
            "job_description": "Analyze supply-demand balance, match rate, GMV, cancellation rate, and repeat transactions. Work with operations and product teams to improve marketplace liquidity.",
            "candidate_profile": "Candidate worked on Uber Eats operations, merchant onboarding, SKU expansion, process automation, and complaint analysis from 5% to 1%.",
        },
    }


def render_sidebar() -> None:
    with st.sidebar:
        st.title("🎯 CareerProof")
        st.caption("AI career concierge for evidence-based interview strategy.")
        st.divider()
        st.subheader("Model")
        st.session_state.model_name = st.selectbox(
            "Gemini model",
            [DEFAULT_MODEL, FALLBACK_MODEL, "gemini-1.5-flash"],
            index=0,
            help="If the selected model is unavailable, the app falls back to gemini-flash-latest.",
        )
        if has_api_key():
            st.success("API key detected")
        else:
            st.warning("No API key detected. The app will run in deterministic demo mode.")
        st.caption("On Streamlit Cloud, add GOOGLE_API_KEY in App settings → Secrets.")
        st.divider()
        st.subheader("Platform vision")
        st.markdown(
            """
- Personal career graph
- Hiring signal database
- 25-industry interview graph
- Coach marketplace
- University career center version
- API / agent marketplace
"""
        )


def tab_strategy() -> None:
    st.subheader("Generate an evidence-based interview strategy")

    examples = sample_inputs()
    selected_example = st.selectbox("Load sample", ["Custom", *examples.keys()])
    default = examples.get(selected_example, {})

    col1, col2 = st.columns([1, 1])
    with col1:
        target_role = st.text_input("Target role", value=default.get("target_role", "Business Analyst"))
        company = st.text_input("Company / organization", value=default.get("company", ""))
    with col2:
        industry = st.selectbox(
            "Industry context",
            get_industry_options(),
            index=get_industry_options().index(default.get("industry", "Auto-detect")) if default.get("industry") in get_industry_options() else 0,
        )
        output_depth = st.selectbox("Output depth", ["Executive", "Detailed", "Deep-dive"], index=1)

    job_description = st.text_area(
        "Job description",
        value=default.get("job_description", ""),
        height=180,
        placeholder="Paste the JD here...",
    )
    candidate_profile = st.text_area(
        "Candidate profile / resume summary",
        value=default.get("candidate_profile", ""),
        height=180,
        placeholder="Paste candidate experience, projects, skills, and measurable results...",
    )

    if st.button("Generate CareerProof Strategy", type="primary", use_container_width=True):
        if not job_description.strip() or not candidate_profile.strip():
            st.error("Please provide both a job description and candidate profile.")
            return
        with st.spinner("Analyzing role, industry, hiring signals, and candidate proof..."):
            prompt, metadata = build_prompt(
                target_role,
                company,
                industry,
                job_description,
                candidate_profile,
                output_depth,
            )
            if has_api_key():
                try:
                    report = gemini_report(prompt, st.session_state.get("model_name", DEFAULT_MODEL))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Gemini call failed: {exc}")
                    report, metadata = deterministic_report(
                        target_role,
                        company,
                        industry,
                        job_description,
                        candidate_profile,
                        output_depth,
                    )
            else:
                report, metadata = deterministic_report(
                    target_role,
                    company,
                    industry,
                    job_description,
                    candidate_profile,
                    output_depth,
                )

            st.session_state.last_report = report
            st.session_state.last_context = metadata
            st.session_state.last_inputs = {
                "target_role": target_role,
                "company": company,
                "industry": industry,
                "job_description": job_description,
                "candidate_profile": candidate_profile,
            }

    if st.session_state.get("last_report"):
        st.success("Strategy report generated")
        metadata = st.session_state.get("last_context", {})
        signals = metadata.get("signals", {})
        ctx = metadata.get("industry_context", {})
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Role family", signals.get("role_family", "Unknown"))
        with m2:
            st.metric("Matched industry", ctx.get("matched_industry", "Unknown"))
        with m3:
            st.metric("Industry confidence", ctx.get("confidence", "Unknown"))
        st.markdown(st.session_state.last_report)
        st.download_button(
            "Download report as Markdown",
            st.session_state.last_report,
            file_name="careerproof_report.md",
            mime="text/markdown",
        )


def tab_copilot() -> None:
    st.subheader("Interactive CareerProof Copilot")
    st.caption("Ask follow-up questions about your generated report, role fit, stories, gaps, or interview prep.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi, I’m CareerProof Copilot. Generate a strategy report first, then ask me how to improve your stories, evidence, or interview plan."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_msg = st.chat_input("Ask CareerProof Copilot...")
    if not user_msg:
        return

    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    context = st.session_state.get("last_report", "No strategy report has been generated yet.")
    inputs = st.session_state.get("last_inputs", {})

    copilot_prompt = f"""
You are CareerProof Copilot, a concise but strategic career advisor.

User question:
{user_msg}

Current candidate / role context:
{json.dumps(inputs, indent=2)}

Current CareerProof report:
{context}

Answer with practical, evidence-based guidance. Do not fabricate experience. If information is missing, ask for it or state the gap.
""".strip()

    with st.chat_message("assistant"):
        with st.spinner("CareerProof Copilot is thinking..."):
            if has_api_key():
                try:
                    answer = gemini_report(copilot_prompt, st.session_state.get("model_name", DEFAULT_MODEL))
                except Exception as exc:  # noqa: BLE001
                    answer = f"I could not call Gemini right now: {exc}\n\nTry asking me after adding a valid GOOGLE_API_KEY in Streamlit secrets."
            else:
                answer = (
                    "Demo mode: I can help you refine the generated report once an API key is configured. "
                    "For now, focus on strengthening proof with measurable outcomes, connecting each story to the role's business problem, "
                    "and preparing one example for ambiguity, stakeholder communication, analytics method, and measurable impact."
                )
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})


def tab_industry() -> None:
    st.subheader("25-Industry Interview Knowledge Graph")
    industries = cached_industries()
    selected = st.selectbox("Choose an industry", sorted(industries.keys()))
    info = industries[selected]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Common roles")
        st.write(info.get("roles", []))
    with c2:
        st.markdown("### Key metrics")
        st.write(info.get("metrics", []))
    with c3:
        st.markdown("### Hiring signals")
        st.write(info.get("hiring_signals", []))

    st.markdown("### Business model")
    st.write(info.get("business_model", []))
    st.markdown("### Common business problems")
    st.write(info.get("business_problems", []))
    st.markdown("### Interview case patterns")
    st.write(info.get("interview_cases", []))

    df = pd.DataFrame(
        [
            {"Industry": name, "Roles": len(v.get("roles", [])), "Metrics": len(v.get("metrics", [])), "Cases": len(v.get("interview_cases", []))}
            for name, v in industries.items()
        ]
    )
    st.markdown("### Coverage dashboard")
    st.dataframe(df, use_container_width=True, hide_index=True)


def tab_research() -> None:
    st.subheader("Market Research Analyzer")
    st.caption("Upload your survey CSV/XLSX to summarize target users, pain points, and product signals.")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if uploaded is None:
        st.info("Upload your market research file to generate a quick qualitative summary.")
        return

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.write("Preview")
    st.dataframe(df.head(20), use_container_width=True)
    st.metric("Responses", len(df))
    st.write("Columns", list(df.columns))

    combined = "\n".join(df.astype(str).fillna("").head(100).agg(" | ".join, axis=1).tolist())
    prompt = f"""
You are analyzing early market research for CareerProof Agent.

Summarize the survey responses into:
1. Target user segments
2. Top pain points
3. Desired features
4. Concerns / objections
5. Product positioning implications
6. Recommended MVP scope

Responses:
{combined}
""".strip()

    if st.button("Generate research summary", type="primary"):
        with st.spinner("Analyzing market research..."):
            if has_api_key():
                try:
                    summary = gemini_report(prompt, st.session_state.get("model_name", DEFAULT_MODEL))
                except Exception as exc:  # noqa: BLE001
                    summary = f"Gemini call failed: {exc}"
            else:
                summary = (
                    "Demo mode summary: Look for repeated role families, recurring interview-prep pain points, "
                    "concerns about generic AI output, willingness to beta test, and pricing sensitivity."
                )
            st.markdown(summary)


def main() -> None:
    render_sidebar()
    st.markdown(
        f"""
<div class="hero-card">
  <div class="hero-title">{APP_TITLE}</div>
  <div class="hero-subtitle">{APP_SUBTITLE}. Turn job descriptions into hiring signals, candidate proof, interview stories, and skill-gap plans.</div>
  <div>
    <span class="pill">Concierge Agents</span>
    <span class="pill">25 Industries</span>
    <span class="pill">Evidence Matrix</span>
    <span class="pill">Interview Copilot</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.write("")

    tabs = st.tabs(["🎯 Strategy Builder", "💬 Copilot", "🧭 Industry Graph", "📊 Market Research"])
    with tabs[0]:
        tab_strategy()
    with tabs[1]:
        tab_copilot()
    with tabs[2]:
        tab_industry()
    with tabs[3]:
        tab_research()


if __name__ == "__main__":
    main()
