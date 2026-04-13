#!/usr/bin/env python3
"""
LearnBuddy - Streamlit Web Interface

Personalized learning plan generation with conditional routing,
proficiency classification, and multi-stage validation.
"""

import streamlit as st
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from workflow import workflow_instance

try:
    from ml.evaluation.evaluate_models import evaluate_all_models
except ImportError:
    pass

load_dotenv()

st.set_page_config(
    page_title="LearnBuddy",
    page_icon="book",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    # TODO: IMPLEMENTATION REQUIRED
    # Initialize 5 session state variables (run_evaluation, eval_results, sample_profile, analysis_result, run_analysis).
    # Render UI: title, disclaimer, sidebar with learner profile selection and file loading, 4-column workflow steps, main "Generate Plan" button.
    # On button click: call workflow_instance.run_workflow(sample_profile) and store result in session_state.analysis_result.
    # Display results in 5 tabs: Analysis (proficiency, gaps), Generated Plan (topics, milestones, resources), Validation Results (time, difficulty, budget),
    # Coaching & Report (personalized guidance + detailed report), Download (JSON export). Handle model evaluation trigger and render evaluation section.
    # Returns: None (Streamlit app state management)
    # Initialize session state
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "sample_profile" not in st.session_state:
        st.session_state.sample_profile = None

    # Header
    st.title("📚 LearnBuddy - Personalized Learning Path Generator")

    # Sidebar - Profile Loading
    st.sidebar.header("📋 Learner Profile")
    profile_source = st.sidebar.radio("Select profile source:", ["Sample Profile", "Upload JSON File"])

    if profile_source == "Sample Profile":
        sample_files = list(Path("data/input").glob("learn_*.json"))
        if sample_files:
            selected_file = st.sidebar.selectbox("Choose a sample profile:", sorted(sample_files), format_func=lambda x: x.name)
            with open(selected_file, 'r') as f:
                st.session_state.sample_profile = json.load(f)

    # Generate Plan Button
    if st.session_state.sample_profile:
        if st.button("🚀 Generate Learning Plan", use_container_width=True):
            with st.spinner("🔄 Generating personalized learning plan..."):
                result = workflow_instance.run_workflow(st.session_state.sample_profile)
                st.session_state.analysis_result = result
                
                if result.get("status") == "success":
                    st.success("✅ Learning plan generated successfully!")


    # Display Results in Tabs
    if st.session_state.analysis_result and st.session_state.analysis_result.get("status") == "success":
        data = st.session_state.analysis_result.get("data", {})
        
        # Check for error in data
        if data.get("error_occurred"):
            st.error("❌ Error occured while generating learning plan")
            if data.get("error_message"):
                st.error(f"**Error Details:** {data.get('error_message')}")
            if data.get("error_messages"):
                for err_msg in data.get("error_messages", []):
                    st.error(f"• {err_msg}")
            return  # Stop execution here - don't show tabs
        
        learner_id = data.get("learner_id", "Unknown")
        
        st.header(f"📊 Results - Learner ID: {learner_id}")
        
        # DEBUG SECTION - Show what we got back
        with st.expander("🔧 DEBUG: Response Data Keys"):
            st.write(f"**All available keys in response:** {list(data.keys())}")
            st.json(data)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Analysis", "📚 Generated Plan", "✅ Validation", "🎯 Coaching", "💾 Download"])
        
        data = st.session_state.analysis_result.get("data", {})
        
        with tab1:
            st.subheader("👤 Learner Profile & Analysis")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Proficiency Level", data.get("learner_proficiency_level", "N/A"), 
                          delta=f"Confidence: {int(data.get('proficiency_confidence', 0)*100)}%")
            with col2:
                analyzed = data.get("analyzed_profile", {})
                st.metric("Current Score", f"{analyzed.get('current_proficiency', {}).get('score', 'N/A')}/100")
            with col3:
                st.metric("Learning Pace", analyzed.get('learning_characteristics', {}).get('learning_pace', 'N/A'))
            with col4:
                st.metric("Available Hours/Week", analyzed.get('learning_characteristics', {}).get('hours_available_per_week', 'N/A'))
            
            st.divider()
            
            # Demographics and Goals
            col_demo1, col_demo2 = st.columns(2)
            
            with col_demo1:
                st.markdown("### 📊 Demographics")
                st.write(f"**Learner ID:** {data.get('learner_id', 'N/A')}")
                demographics = analyzed.get('demographics', {})
                st.write(f"**Age:** {demographics.get('age', 'N/A')}")
                st.write(f"**Education Level:** {demographics.get('education_level', 'N/A').title()}")
                st.write(f"**Employment Status:** {demographics.get('employment_status', 'N/A').title()}")
            
            with col_demo2:
                st.markdown("### 🎯 Goals & Timeline")
                st.write(f"**Primary Goal:** {analyzed.get('goals', {}).get('primary_goal', 'N/A').title()}")
                st.write(f"**Career Aspiration:** {analyzed.get('goals', {}).get('career_aspiration', 'N/A').title()}")
                st.write(f"**Target Timeline:** {analyzed.get('goals', {}).get('target_timeline_months', 'N/A')} months")
            
            st.divider()
            
            # Constraints & Challenges
            st.markdown("### ⚠️ Challenges & Constraints")
            constraints = analyzed.get('constraints', {})
            col_c1, col_c2 = st.columns(2)
            
            with col_c1:
                st.write("**Challenges:**")
                challenges = constraints.get('challenges_faced', [])
                if challenges:
                    for challenge in challenges:
                        st.write(f"• {challenge.title()}")
                else:
                    st.write("No challenges identified")
            
            with col_c2:
                st.write("**Support Needed:**")
                support = constraints.get('previous_support_needed', [])
                if support:
                    for item in support:
                        st.write(f"• {item.title()}")
                else:
                    st.write("No specific support required")
            
            st.divider()
            
            # Gaps and Difficulty Prediction
            st.markdown("### 📍 Identified Gaps & Difficulty")
            col_gd1, col_gd2 = st.columns(2)
            
            with col_gd1:
                st.write("**Identified Learning Gaps:**")
                gaps = data.get("identified_gaps", [])
                if gaps:
                    for gap in gaps:
                        st.write(f"• {gap}")
                else:
                    st.write("✅ No major gaps identified - Ready to start!")
            
            with col_gd2:
                st.write(f"**Predicted Difficulty:** {data.get('predicted_difficulty', 'N/A').title()}")
                st.write(f"**Difficulty Confidence:** {int(data.get('difficulty_confidence', 0)*100)}%")
                st.write(f"**Gap Urgency:** {data.get('gap_urgency', 'N/A').title()}")
        
        with tab2:
            st.subheader("📚 Your Personalized Learning Plan")
            plan = data.get("generated_plan", {})
            
            # Plan Overview Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Plan Type", plan.get("plan_type", "N/A"))
            with col2:
                st.metric("Duration", f"{plan.get('duration_weeks', 0)} weeks")
            with col3:
                st.metric("Weekly Hours", f"{plan.get('hours_per_week', 0)}h")
            with col4:
                st.metric("Intensity", plan.get("intensity", "N/A"))
            
            st.divider()
            
            # Topics to Cover
            st.markdown("### 📖 Topics to Cover")
            topics = plan.get("topics", [])
            if topics:
                for i, topic in enumerate(topics, 1):
                    st.write(f"{i}. {topic}")
            else:
                st.info("No topics specified")
            
            st.divider()
            
            # Learning Milestones
            st.markdown("### 🎯 Learning Milestones")
            milestones = plan.get("milestones", [])
            if milestones:
                for i, milestone in enumerate(milestones, 1):
                    st.write(f"**{i}. {milestone}**")
            else:
                st.info("No milestones specified")
            
            st.divider()
            
            # Focus Areas
            st.markdown("### 🔍 Focus Areas")
            focus_areas = plan.get("focus_areas", [])
            if focus_areas:
                col_focus1, col_focus2 = st.columns([1, 1])
                for i, area in enumerate(focus_areas):
                    if i % 2 == 0:
                        col_focus1.write(f"✨ {area}")
                    else:
                        col_focus2.write(f"✨ {area}")
            else:
                st.info("No focus areas specified")
            
            st.divider()
            
            # Recommended Resources
            st.markdown("### 📚 Recommended Learning Resources")
            resources = plan.get("resources", [])
            if resources:
                for i, resource in enumerate(resources, 1):
                    st.write(f"{i}. {resource}")
            else:
                st.info("No resources recommended")
        
        with tab3:
            st.subheader("✅ Plan Feasibility Validation Results")
            
            # Overall Validation Status
            validation_passed = data.get("validation_passed", False)
            if validation_passed:
                st.success("✅ All validations PASSED")
            else:
                st.warning("⚠️ Some validations need attention")
            
            st.divider()
            
            # Time Validation
            st.markdown("### ⏱️ Time Management Validation")
            time_result = data.get("time_validation_result", {})
            col_time1, col_time2 = st.columns([1, 2])
            with col_time1:
                if time_result.get("passed"):
                    st.success("✅ PASSED")
                else:
                    st.error("❌ FAILED")
            with col_time2:
                errors = time_result.get("issues", [])
                if errors:
                    for error in errors:
                        st.write(f"⚠️ {error}")
                else:
                    st.write("No time constraints issues detected")
            
            st.divider()
            
            # Difficulty Alignment Validation
            st.markdown("### 🎓 Difficulty Alignment Validation")
            diff_result = data.get("difficulty_validation_result", {})
            col_diff1, col_diff2 = st.columns([1, 2])
            with col_diff1:
                if diff_result.get("passed"):
                    st.success("✅ PASSED")
                else:
                    st.error("❌ FAILED")
            with col_diff2:
                errors = diff_result.get("issues", [])
                if errors:
                    for error in errors:
                        st.write(f"⚠️ {error}")
                else:
                    st.write("Difficulty level is well-aligned with learner profile")
            
            st.divider()
            
            # Budget/Resource Validation
            st.markdown("### 💰 Budget & Resource Validation")
            budget_result = data.get("resource_validation_result", {})
            col_budget1, col_budget2 = st.columns([1, 2])
            with col_budget1:
                if budget_result.get("passed"):
                    st.success("✅ PASSED")
                else:
                    st.error("❌ FAILED")
            with col_budget2:
                errors = budget_result.get("issues", [])
                if errors:
                    for error in errors:
                        st.write(f"⚠️ {error}")
                else:
                    st.write("Budget and resources are adequate")
            
            st.divider()
            
            # Overall Summary
            st.markdown("### 📋 Validation Summary")
            validation_issues = data.get("validation_issues", [])
            if validation_issues:
                st.info("Issues found during validation:")
                for issue in validation_issues:
                    st.write(f"• {issue}")
            else:
                st.success("All validations completed successfully!")
        
        with tab4:
            st.subheader("🎯 Personalized Coaching & Guidance")
            
            # Coaching guidance
            coaching = data.get("personalized_coaching", "")
            if coaching:
                st.info(coaching)
            else:
                st.write("No coaching guidance available")
            
            st.divider()
            
            # Additional insights from analysis
            st.markdown("### 💡 Key Insights")
            analyzed = data.get("analyzed_profile", {})
            
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                st.markdown("**Learning Patterns:**")
                patterns = analyzed.get('learning_patterns', [])
                if patterns:
                    for pattern in patterns:
                        st.write(f"• {pattern}")
            
            with col_insight2:
                st.markdown("**Goal Clarity:**")
                goal_clarity = analyzed.get('goal_clarity_score', 0)
                st.metric("Goal Clarity Score", f"{goal_clarity}%")
            
            st.divider()
            
            # Budget Information
            st.markdown("### 💼 Budget & Certification Info")
            constraints = analyzed.get('constraints', {})
            col_budget1, col_budget2 = st.columns(2)
            
            with col_budget1:
                budget = constraints.get('budget_limit_usd', 'N/A')
                st.write(f"**Budget Limit:** ${budget}")
            
            with col_budget2:
                cert = constraints.get('certification_needed', False)
                st.write(f"**Certification Needed:** {'Yes ✅' if cert else 'No ❌'}")
        
        with tab5:
            st.subheader("💾 Export & Download Options")
            
            # Full Report Download
            st.markdown("### 📥 Download Full Report")
            json_str = json.dumps(data, indent=2, default=str)
            st.download_button(
                label="📥 Download Full Report (JSON)",
                data=json_str,
                file_name=f"learnbuddy_report_{data.get('learner_id', 'unknown')}.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.divider()
            
            # Learning Plan Summary
            st.markdown("### 📄 Plan Summary")
            plan = data.get("generated_plan", {})
            
            summary_text = f"""
# Learning Plan Summary for {data.get('learner_id', 'Unknown Learner')}

## Plan Details
- **Plan Type:** {plan.get('plan_type', 'N/A')}
- **Duration:** {plan.get('duration_weeks', 'N/A')} weeks
- **Weekly Hours:** {plan.get('hours_per_week', 'N/A')} hours
- **Intensity:** {plan.get('intensity', 'N/A')}

## Topics to Cover
{chr(10).join([f'- {topic}' for topic in plan.get('topics', [])])}

## Milestones
{chr(10).join([f'- {milestone}' for milestone in plan.get('milestones', [])])}

## Focus Areas
{chr(10).join([f'- {area}' for area in plan.get('focus_areas', [])])}
"""
            
            st.download_button(
                label="📄 Download Plan Summary (Markdown)",
                data=summary_text,
                file_name=f"learning_plan_{data.get('learner_id', 'unknown')}.md",
                mime="text/markdown",
                use_container_width=True
            )

def render_model_evaluation_section(eval_results):
    """Render ML model evaluation metrics on the main page."""
    # TODO: IMPLEMENTATION REQUIRED
    # Render section header and description. If no eval_results, display info message and return.
    # Create 2-column layout for gap detection and difficulty prediction models. For each model: extract eval_results (accuracy, hamming_loss/cv_score, test samples),
    # display metrics or error message. Add divider and expander to view raw JSON eval_results data.
    # Returns: None (renders Streamlit UI elements)

AIzaSyDZ9EHzXTXH7uSKh5n4w7gG09yPGQWP4wg
AIzaSyAGR_VZCbVPy5ckRgG03sPl7PXkRXV3REM


if __name__ == "__main__":
    main()
