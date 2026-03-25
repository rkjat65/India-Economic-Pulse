import streamlit as st
from .ai_chat import handle_chat_query
from .ai_image import handle_image_generation

# CSS to pin the AI panel to the right
AI_PANEL_CSS = """
<style>
.ai-panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 380px;
    height: 100vh;
    background: #0a0f24;
    border-left: 1px solid #2a2a2a;
    padding: 10px;
    z-index: 9999;
    overflow-y: auto;
}
.ai-toggle-btn {
    position: fixed;
    top: 20px;
    right: 380px;
    background: #0e2a5e;
    color: white;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 16px;
    border-radius: 5px;
    z-index: 9999;
}
</style>
"""

def render_global_ai_panel(data):
    st.markdown(AI_PANEL_CSS, unsafe_allow_html=True)

    if "ai_open" not in st.session_state:
        st.session_state.ai_open = False

    # Toggle button
    if st.button("🤖 AI Assistant", key="ai_toggle"):
        st.session_state.ai_open = not st.session_state.ai_open

    if st.session_state.ai_open:
        with st.container():
            st.markdown('<div class="ai-panel">', unsafe_allow_html=True)

            st.header("AI Assistant")

            # Model selector
            model = st.selectbox(
                "Select Model",
                ["Gemini", "OpenAI DALL·E", "Claude"],
                key="ai_model"
            )

            # Chat input
            user_query = st.text_input("Ask a question about the data")
            if st.button("📩 Submit Query", key="chat_submit"):
                if user_query.strip():
                    answer = handle_chat_query(model, user_query, data)
                    st.markdown(f"**Q:** {user_query}")
                    st.markdown(f"**A:** {answer}")

            st.markdown("---")
            st.subheader("Image Generation")

            prompt = st.text_area("Enter image prompt (data only)")
            aspect_ratio = st.selectbox("Aspect Ratio", ["16:9","1:1","9:16"], key="ai_ratio")
            quality = st.selectbox("Quality", ["4K","HD","SD"], key="ai_quality")

            if st.button("🎨 Generate Image", key="img_submit"):
                if prompt.strip():
                    img, caption = handle_image_generation(
                        model, prompt, data,
                        aspect_ratio=aspect_ratio,
                        quality=quality
                    )
                    if img:
                        st.image(img, use_container_width=True)
                        st.markdown("#### ✍️ Caption")
                        st.code(caption)
                        buffer = BytesIO()
                        img.save(buffer, format="PNG")
                        st.download_button("📥 Download Image",
                                            buffer.getvalue(),
                                            file_name="ai_image.png",
                                            mime="image/png")

            st.markdown("</div>", unsafe_allow_html=True)
