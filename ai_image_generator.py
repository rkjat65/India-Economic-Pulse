"""
AI Image Generator for India Economic Pulse Dashboard
Generates economic data visualizations and infographics using multiple AI providers:
- Google Gemini (Nano Banana Pro) - Primary recommendation
- Anthropic Claude - Alternative
- OpenAI DALL-E - High-quality option
"""

import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import requests

# AI Provider imports (with error handling for missing packages)
try:
    from google import genai
    from google.genai import types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def generate_with_gemini(prompt, context_data=None, aspect_ratio="16:9", image_size="4K"):
    """
    Generate image using Google Gemini Nano Banana Pro API
    
    Args:
        prompt: User's description for the image
        context_data: Optional economic data context
        aspect_ratio: Image aspect ratio (16:9, 1:1, 9:16)
        image_size: Image quality (4K, HD, SD)
    
    Returns:
        PIL Image or None if generation fails
    """
    
    if not GOOGLE_AVAILABLE:
        st.error("⚠️ Google Gemini library not installed. Install with: pip install google-genai")
        return None
    
    # Get API key from Streamlit secrets
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    
    if not api_key:
        st.error("⚠️ Google API key not found. Please add GOOGLE_API_KEY to your Streamlit secrets.")
        return None
    
    try:
        # Initialize Google Gemini client
        client = genai.Client(api_key=api_key)
        
        # Enhance prompt with economic context
        enhanced_prompt = prompt
        if context_data:
            enhanced_prompt = f"""
            Create a professional economic visualization for India Economic Pulse Dashboard:
            
            User Request: {prompt}
            
            Economic Context:
            {context_data}
            
            Design Requirements:
            - Professional and data-driven design
            - Use India's tricolor theme (saffron #FF9933, white #FFFFFF, green #138808)
            - Include relevant economic symbols (₹ rupee, growth arrows, charts)
            - Modern, clean, and minimalist aesthetic
            - High contrast for readability
            - Suitable for social media posts and professional presentations
            - Clear data visualization principles
            - Professional typography
            """
        else:
            enhanced_prompt = f"""
            Create a professional economic visualization for India Economic Pulse Dashboard:
            
            {prompt}
            
            Design Requirements:
            - Professional and data-driven design
            - Use India's tricolor theme (saffron #FF9933, white #FFFFFF, green #138808)
            - Include relevant economic symbols (₹ rupee, growth arrows, charts)
            - Modern, clean, and minimalist aesthetic
            - High contrast for readability and social media
            """
        
        # Generate image with Gemini
        with st.spinner("🎨 Generating with Google Gemini..."):
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],  # Enable Google Search for current data
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size
                    )
                )
            )
            
            # Extract image from response
            image_parts = [part for part in response.parts if part.inline_data]
            
            if image_parts:
                # FIX: Convert raw bytes to PIL Image manually
                # The .as_image() method in some SDK versions returns a Pydantic model
                # which causes the 'AttributeError: Image object has no attribute format' in Streamlit
                try:
                    raw_data = image_parts[0].inline_data.data
                    image = Image.open(BytesIO(raw_data))
                    st.success("✅ Image generated successfully with Google Gemini!")
                    return image
                except Exception as img_err:
                    st.error(f"❌ Error processing image data: {str(img_err)}")
                    return None
            else:
                st.warning("⚠️ No image generated. Response received but no image data.")
                return None
                
    except Exception as e:
        st.error(f"❌ Google Gemini Error: {str(e)}")
        return None


def generate_economic_image(prompt, context_data=None):
    """
    Generate AI image based on economic data and user prompt (Claude API)
    
    Args:
        prompt: User's description for the image
        context_data: Optional economic data context to enhance the prompt
    
    Returns:
        PIL Image or None if generation fails
    """
    
    if not ANTHROPIC_AVAILABLE:
        st.error("⚠️ Anthropic library not installed. Install with: pip install anthropic")
        return None
    
    # Get API key from Streamlit secrets
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    
    if not api_key:
        st.error("⚠️ API key not found. Please add ANTHROPIC_API_KEY to your Streamlit secrets.")
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Enhance prompt with economic context if provided
        enhanced_prompt = prompt
        if context_data:
            enhanced_prompt = f"""
            Create an image for India Economic Dashboard with the following details:
            
            User Request: {prompt}
            
            Economic Context:
            {context_data}
            
            Style Guidelines:
            - Professional and clean design
            - Use India's tricolor theme where appropriate (saffron, white, green)
            - Include relevant economic symbols (₹, graphs, charts)
            - Modern, minimalist aesthetic
            - High contrast for readability
            - Suitable for social media and presentations
            """
        
        # Call Claude API for image generation
        with st.spinner("🎨 Generating your economic visualization..."):
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ]
            )
            
            # Extract image from response (if Claude returns image data)
            # Note: This is a placeholder - actual implementation depends on API response format
            response_text = message.content[0].text
            
            # For now, we'll use DALL-E style API call through a proxy
            # You can replace this with actual image generation service
            
            st.info("💡 Image generation prompt created. Integrate with your preferred AI image service (DALL-E, Midjourney, etc.)")
            st.code(enhanced_prompt, language="text")
            
            return None
            
    except Exception as e:
        st.error(f"❌ Error generating image: {str(e)}")
        return None


def generate_with_dalle(prompt, context_data=None):
    """
    Alternative: Generate image using OpenAI DALL-E
    
    Args:
        prompt: User's description
        context_data: Economic context
    
    Returns:
        PIL Image or None
    """
    
    if not OPENAI_AVAILABLE:
        st.error("⚠️ OpenAI library not installed. Install with: pip install openai")
        return None
    
    openai_key = st.secrets.get("OPENAI_API_KEY", "")
    
    if not openai_key:
        st.warning("OpenAI API key not configured")
        return None
    
    try:
        openai.api_key = openai_key
        
        enhanced_prompt = prompt
        if context_data:
            enhanced_prompt = f"India Economic Dashboard visualization: {prompt}. Data context: {context_data}. Style: Professional, Indian tricolor theme, modern infographic."
        
        response = openai.Image.create(
            prompt=enhanced_prompt[:1000],  # DALL-E has prompt length limit
            n=1,
            size="1024x1024"
        )
        
        image_url = response['data'][0]['url']
        
        # Download and return image
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        
        return img
        
    except Exception as e:
        st.error(f"DALL-E Error: {str(e)}")
        return None


def create_prompt_suggestions(indicator_type):
    """
    Generate contextual prompt suggestions based on economic indicator
    
    Args:
        indicator_type: Type of economic data (GDP, Inflation, Trade, etc.)
    
    Returns:
        List of suggested prompts
    """
    
    suggestions = {
        "GDP": [
            "Create an infographic showing India's GDP growth trajectory with upward arrows and growth bars",
            "Design a modern chart comparing sectoral contributions to GDP (Agriculture, Industry, Services)",
            "Visualize India's economic resilience with a strong foundation metaphor",
            "Create a comparison graphic: India vs Global GDP growth rates"
        ],
        "Inflation": [
            "Design an inflation meter showing current CPI levels with RBI target bands",
            "Create a price basket visualization showing changing consumer prices",
            "Visualize the impact of inflation on purchasing power with before/after comparison",
            "Design a heatmap of inflation across different product categories"
        ],
        "Trade": [
            "Create a world map highlighting India's major trade partners with export/import flows",
            "Design a balance scale showing trade surplus/deficit",
            "Visualize India's top export products as an infographic",
            "Create a port activity visualization showing India's trade gateways"
        ],
        "Forex": [
            "Design a forex reserves treasure chest visualization showing India's reserves",
            "Create a currency strength meter comparing INR performance",
            "Visualize RBI's intervention strategy in forex markets",
            "Design a timeline showing forex reserves accumulation over years"
        ],
        "General": [
            "Create a comprehensive India economic health dashboard snapshot",
            "Design an economic scorecard for India with key metrics",
            "Visualize India's economic journey from 2012 to 2025",
            "Create a future outlook graphic for India's economy"
        ]
    }
    
    return suggestions.get(indicator_type, suggestions["General"])


def render_image_generator_ui(current_view=None):
    """
    Render the AI Image Generator UI in sidebar or main area
    
    Args:
        current_view: Current dashboard view for context-aware suggestions
    """
    
    st.markdown("---")
    st.markdown("### 🎨 AI Image Generator")
    st.markdown("Generate custom visualizations for social media and presentations")
    
    # Context selection
    indicator_type = st.selectbox(
        "Select Economic Indicator",
        ["General", "GDP", "Inflation", "Trade", "Forex"],
        help="Choose the economic indicator for contextual suggestions"
    )
    
    # Show prompt suggestions
    with st.expander("💡 Prompt Suggestions"):
        suggestions = create_prompt_suggestions(indicator_type)
        for i, suggestion in enumerate(suggestions, 1):
            st.markdown(f"**{i}.** {suggestion}")
    
    # User input
    user_prompt = st.text_area(
        "Describe the image you want to generate",
        placeholder="E.g., Create a professional infographic showing India's GDP growth from 2012-2025 with tricolor theme and upward trend arrows",
        height=100
    )
    
    # Additional context
    add_context = st.checkbox("Add current dashboard data as context", value=True)
    
    # AI Provider Selection
    st.markdown("#### AI Provider")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_gemini = st.checkbox(
            "🌟 Google Gemini" + (" (Recommended)" if GOOGLE_AVAILABLE else ""),
            value=GOOGLE_AVAILABLE,
            disabled=not GOOGLE_AVAILABLE,
            help="Google's Gemini Nano Banana Pro - Best quality and speed"
        )
    
    with col2:
        use_dalle = st.checkbox(
            "OpenAI DALL-E",
            value=False,
            disabled=not OPENAI_AVAILABLE,
            help="OpenAI's DALL-E - High-quality photorealistic images"
        )
    
    with col3:
        use_claude = st.checkbox(
            "Anthropic Claude",
            value=False,
            disabled=not ANTHROPIC_AVAILABLE,
            help="Claude for prompt enhancement"
        )
    
    # Google Gemini specific options (show only when Gemini is selected)
    if use_gemini:
        st.markdown("#### Google Gemini Settings")
        
        col_ar, col_size = st.columns(2)
        
        with col_ar:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["16:9", "1:1", "9:16"],
                index=0,
                help="16:9 for landscape, 1:1 for square, 9:16 for portrait"
            )
        
        with col_size:
            image_size = st.selectbox(
                "Image Quality",
                ["4K", "HD", "SD"],
                index=0,
                help="4K for highest quality, HD for balanced, SD for faster generation"
            )
    else:
        aspect_ratio = "16:9"
        image_size = "4K"
    
    # Generate button
    if st.button("🚀 Generate Image", type="primary", use_container_width=True):
        if not user_prompt:
            st.warning("Please enter a prompt description")
        elif not (use_gemini or use_dalle or use_claude):
            st.warning("Please select at least one AI provider")
        else:
            # Prepare context data if needed
            context_data = None
            if add_context and current_view:
                context_data = f"Dashboard View: {current_view}, Indicator: {indicator_type}"
            
            # Generate image based on selected provider
            image = None
            
            if use_gemini:
                image = generate_with_gemini(user_prompt, context_data, aspect_ratio, image_size)
            elif use_dalle:
                image = generate_with_dalle(user_prompt, context_data)
            elif use_claude:
                image = generate_economic_image(user_prompt, context_data)
            
            # Display result
            if image:
                st.success("✅ Image generated successfully!")
                st.image(image, use_container_width=True)
                
                # Download button
                buf = BytesIO()
                image.save(buf, format="PNG")
                btn = st.download_button(
                    label="📥 Download Image",
                    data=buf.getvalue(),
                    file_name=f"india_economic_pulse_{indicator_type.lower()}.png",
                    mime="image/png",
                    use_container_width=True
                )
    
    # Info section
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        **Steps to generate images:**
        1. Select the economic indicator type
        2. Check prompt suggestions for inspiration
        3. Describe the visualization you want
        4. Choose your AI provider:
           - **Google Gemini** (Recommended): Best quality, multiple aspect ratios, up to 4K
           - **DALL-E**: Photorealistic, professional quality
           - **Claude**: Prompt enhancement and guidance
        5. Click Generate Image
        
        **API Setup:**
        - Add `GOOGLE_API_KEY` for Gemini (Recommended)
        - Add `OPENAI_API_KEY` for DALL-E
        - Add `ANTHROPIC_API_KEY` for Claude
        
        **Google Gemini Features:**
        - **Aspect Ratios**: 16:9 (landscape), 1:1 (square), 9:16 (portrait/story)
        - **Image Sizes**: 4K (ultra HD), HD (high quality), SD (standard)
        - **Google Search Integration**: Automatically uses current data
        
        **Best Practices:**
        - Be specific about chart types, colors, and data points
        - Mention "India Economic Pulse" or "India tricolor theme"
        - Request "professional", "modern", or "minimalist" styles
        - Specify intended use (social media, presentation, report)
        - Use 16:9 for presentations, 1:1 for Instagram, 9:16 for Stories
        """)
    
    # API Provider Status
    with st.expander("🔌 API Provider Status"):
        st.markdown("**Available Providers:**")
        
        providers = [
            ("Google Gemini", GOOGLE_AVAILABLE, "GOOGLE_API_KEY"),
            ("OpenAI DALL-E", OPENAI_AVAILABLE, "OPENAI_API_KEY"),
            ("Anthropic Claude", ANTHROPIC_AVAILABLE, "ANTHROPIC_API_KEY")
        ]
        
        for name, available, key in providers:
            if available:
                has_key = key in st.secrets and st.secrets[key]
                status = "✅ Ready" if has_key else "⚠️ Library installed, API key missing"
                st.markdown(f"- **{name}**: {status}")
            else:
                st.markdown(f"- **{name}**: ❌ Library not installed")
        
        st.markdown("\n**To add API keys:**")
        st.code("""
# In .streamlit/secrets.toml
GOOGLE_API_KEY = "your-google-api-key"
OPENAI_API_KEY = "your-openai-api-key"
ANTHROPIC_API_KEY = "your-anthropic-api-key"
        """, language="toml")


def add_to_app_sidebar():
    """
    Add AI Image Generator to app sidebar with compact view
    """
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎨 AI Image Generator")
        
        if st.button("Open Image Generator", use_container_width=True):
            st.session_state['show_image_generator'] = True
        
        # Show quick generate option
        quick_prompt = st.text_input("Quick Generate", placeholder="Describe visualization...")
        if quick_prompt and st.button("Generate", use_container_width=True):
            image = generate_economic_image(quick_prompt)
            if image:
                st.image(image, use_container_width=True)