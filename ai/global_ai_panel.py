import streamlit as st
from ai.gemini_image import generate_with_gemini
from io import BytesIO

def render_global_ai_panel(data):
    """
    Global AI Assistant – visible on all pages
    """

    # Persistent state
    st.session_state.setdefault("ai_open", False)

    # Toggle button (fixed bottom-right feel)
    col1, col2, col3 = st.columns([8, 1, 1])
    with col3:
        if st.button("🤖 AI", help="Open AI Assistant"):
            st.session_state.ai_open = not st.session_state.ai_open

    if not st.session_state.ai_open:
        return

    st.markdown("---")
    st.markdown("## 🤖 AI Assistant")

    tab_chat, tab_image = st.tabs(["💬 Ask Data", "🎨 Generate Image"])

    # ---------------- CHAT (future-ready) ----------------
    with tab_chat:
        query = st.text_input("Ask a question using dashboard data only")
        if query:
            st.info("🔒 Chat model integration comes next (data-restricted)")

    # ---------------- IMAGE GENERATOR ----------------
    with tab_image:
        prompt = st.text_area(
            "Describe the image (data-driven only)",
            placeholder="Create an infographic of India's GDP growth trend post-2020"
        )

        col1, col2 = st.columns(2)
        with col1:
            aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "1:1", "9:16"])
        with col2:
            image_size = st.selectbox("Quality", ["4K", "HD", "SD"])

        if st.button("🎨 Generate Image", type="primary", use_container_width=True):
            if not prompt:
                st.warning("Please enter a prompt")
                return

            context = f"""
GDP Latest: {data['gdp'].iloc[-1]['GDP_growth']}%
Inflation Latest: {data['inflation'].iloc[-1]['CPI_inflation_yoy']}%
"""

            image = generate_with_gemini(
                prompt=prompt,
                context_data=context,
                aspect_ratio=aspect_ratio,
                image_size=image_size
            )

            if image:
                st.image(image, use_container_width=True)

                buf = BytesIO()
                image.save(buf, format="PNG")

                st.download_button(
                    "📥 Download Image",
                    buf.getvalue(),
                    file_name="india_economic_pulse.png",
                    mime="image/png",
                    use_container_width=True
                )
