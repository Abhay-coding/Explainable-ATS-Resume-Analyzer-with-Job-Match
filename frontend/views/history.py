import requests
import streamlit as st

from frontend.services import api_client


def _show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Is it running on port 8000?")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        st.error(f"Backend returned {exc.response.status_code}: {exc.response.text}")
    else:
        st.error(f"Unexpected error: {exc}")


def render() -> None:
    st.title("📊 Analysis History")
    st.markdown("Past analyses saved against your account.")

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.warning("⚠️ Sign in from the sidebar to view your history.")
        return

    try:
        history = api_client.get_history(access_token)
    except requests.RequestException as exc:
        _show_backend_error(exc)
        return

    # Handle different response types
    if isinstance(history, dict):
        # If dict returned, convert to list
        history = list(history.values())
    elif not isinstance(history, list):
        history = []
    
    # Filter out non-dict items
    history = [item for item in history if isinstance(item, dict)]
    
    if not history:
        st.info("📝 No analyses yet for this account.")
        st.markdown("""
        **How to get started:**
        1. Go to the **ATS Scorer** page (click the button below)
        2. Upload a resume (PDF, DOCX, or TXT)
        3. Add a job description (optional)
        4. Click **Analyze Resume**
        5. Your analysis will appear here automatically!
        
        *Note: History requires Supabase configuration. If not set up, analyses won't be saved.*
        """)
        if st.button("🎯 Go to ATS Scorer"):
            st.session_state.current_view = "scorer"
            st.rerun()
        return

    st.markdown(f"**Total analyses:** {len(history)}")
    st.markdown("---")

    for idx, entry in enumerate(history):
        # Safety check: skip if entry is not a dict
        if not isinstance(entry, dict):
            st.warning(f"⚠️ Skipping invalid entry #{idx + 1}: got {type(entry).__name__}")
            continue
        
        try:
            filename = entry.get("filename", "resume")
            ats_score = float(entry.get("ats_score", 0))
            created_at = entry.get("created_at", "")
            analysis = entry.get("analysis_result", {}) or {}

            component_scores = analysis.get("component_scores", {}) or {}
            jd_comparison = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")

            with st.expander(f"📄 {filename} — Score: {ats_score:.0f}/100 — {created_at}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Overall", f"{ats_score:.0f}/100")
                    st.metric("Formatting", f"{component_scores.get('formatting', 0):.0f}/20")
                with c2:
                    st.metric("Keywords", f"{component_scores.get('keywords', 0):.0f}/25")
                    st.metric("Content", f"{component_scores.get('content', 0):.0f}/25")
                with c3:
                    st.metric("Skill Validation", f"{component_scores.get('skill_validation', 0):.0f}/15")
                    st.metric("ATS Compatibility", f"{component_scores.get('ats_compatibility', 0):.0f}/15")

                if jd_comparison:
                    st.markdown(f"**JD Match:** {jd_comparison.get('match_percentage', 0):.0f}%")

                entry_id = entry.get("id")
                if entry_id:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        try:
                            api_client.delete_history_entry(str(entry_id), access_token)
                            st.success("Deleted.")
                            st.rerun()
                        except requests.RequestException as exc:
                            _show_backend_error(exc)
        except Exception as e:
            st.error(f"Error processing entry #{idx + 1}: {e}")
