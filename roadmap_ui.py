import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Optional

from roadmap_generator import RoadmapGenerator
from content_generator import ContentGenerator
from logger_config import shifu_logger
from security import SecurityValidator


def render_markmap(markdown_content: str, height: int = 700):
    """
    Render Markmap (Mindmap) diagram 
    """
    escaped_markdown = markdown_content.replace("`", "\\`").replace("${", "\\${")
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Inter:wght@400;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
        <style>
            body, html {{ 
                margin: 0; padding: 0; width: 100%; height: 100%; 
                overflow: hidden; background-color: #fafafa;
                font-family: 'Inter', sans-serif;
            }}
            .markmap-container {{
                width: 100%;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
                background-size: 20px 20px;
            }}
            svg#mindmap {{
                width: 100%;
                height: 100%;
            }}
            
            /* Hand-drawn / Sketchy Styles */
            .markmap-node {{
                cursor: pointer;
            }}
            
            /* Hide default circles completely */
            .markmap-node circle {{
                display: none !important;
            }}
            
            /* Premium Rectangular Nodes (Roadmap.sh Style) */
            .markmap-node-rect {{
                display: block !important;
                stroke: #18181b !important;
                stroke-width: 2.5px !important;
                rx: 2; ry: 2;
                fill: #ffffff !important;
                filter: drop-shadow(4px 4px 0px #18181b);
            }}
            
            /* Level colors with high contrast */
            .markmap-node-level-0 .markmap-node-rect {{
                fill: #fde047 !important; /* Bright Yellow */
            }}
            .markmap-node-level-1 .markmap-node-rect {{
                fill: #60a5fa !important; /* Blue */
                stroke: #18181b !important;
            }}
            .markmap-node-level-2 .markmap-node-rect {{
                fill: #ffffff !important;
            }}
            
            /* Sketchy Links/Connectors */
            .markmap-link {{
                stroke: #18181b !important;
                stroke-width: 2.5px !important;
                opacity: 1 !important;
            }}
            
            /* Typography */
            .markmap-node-text {{
                fill: #18181b !important;
                font-family: 'Gochi Hand', cursive !important;
                font-weight: 700 !important;
                font-size: 18px !important;
            }}
            
            /* Prevent label clipping */
            svg text {{
                overflow: visible !important;
            }}
            .material-symbols-outlined {{
                font-family: 'Material Symbols Outlined' !important;
                font-weight: normal;
                font-style: normal;
                font-size: 24px;
                line-height: 1;
                letter-spacing: normal;
                text-transform: none;
                display: inline-block;
                white-space: nowrap;
                word-wrap: normal;
                direction: ltr;
                -webkit-font-smoothing: antialiased;
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
        <script src="https://cdn.jsdelivr.net/npm/markmap-view@0.15.4"></script>
        <script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.15.4/dist/browser/index.min.js"></script>
    </head>
    <body>
        <!-- SVG Filters for Hand-drawn effect -->
        <svg style="position: absolute; width: 0; height: 0;">
            <defs>
                <filter id="handdrawn" x="-20%" y="-20%" width="140%" height="140%">
                    <feTurbulence type="fractalNoise" baseFrequency="0.01 0.05" numOctaves="3" result="noise" />
                    <feDisplacementMap in="SourceGraphic" in2="noise" scale="3" />
                </filter>
            </defs>
        </svg>
        <div class="markmap-container">
            <svg id="mindmap"></svg>
        </div>
        <script>
            const {{ Transformer }} = window.markmap;
            const {{ Markmap }} = window.markmap;
            const transformer = new Transformer();
            const markdown = `{escaped_markdown}`;
            const {{ root }} = transformer.transform(markdown);
            
            // Create and initialize Markmap
            const mm = Markmap.create('#mindmap', {{
                embedGlobalCSS: true,
                fitRatio: 0.9,
                duration: 500,
                autoFit: true,
                paddingX: 16,
                paddingY: 16
            }}, root);

            // Function to enforce theme (hiding circles, etc.)
            const enforceTheme = () => {{
                document.querySelectorAll('.markmap-node circle').forEach(c => c.style.display = 'none');
                document.querySelectorAll('.markmap-node-rect').forEach(r => r.style.display = 'block');
            }};

            // Watch for changes (expanding/collapsing nodes)
            const observer = new MutationObserver(enforceTheme);
            observer.observe(document.querySelector('svg#mindmap'), {{
                childList: true,
                subtree: true
            }});

            // Fix "stuck" issue with ResizeObserver
            const resizeObserver = new ResizeObserver(() => {{
                mm.rescale(0.9);
                enforceTheme();
            }});
            resizeObserver.observe(document.querySelector('.markmap-container'));

            // Initial fit
            setTimeout(() => {{
                mm.fit();
                enforceTheme();
            }}, 300);
        </script>
    </body>
    </html>
    """
    components.html(html_template, height=height, scrolling=False)


def render_topic_details(topic_name: str, topic_content: Dict):
    """Render topic details with proper validation"""
    try:
        # Validate inputs
        validated_topic = SecurityValidator.validate_topic(topic_name)
        
        if not topic_content:
            st.warning(f"No content available for {validated_topic}")
            return
        
        # Create tabs for structured learning
        tab1, tab2, tab3 = st.tabs(["📖 Guide", "🔗 Resources", "⚙️ Details"])
        
        with tab1:
            st.markdown(f"### {validated_topic}")
            
            description = topic_content.get('description', 'No description available')
            st.markdown(f"**Description:** {description}")
            
            key_points = topic_content.get('key_points', [])
            if key_points:
                st.markdown("**Key Points:**")
                for point in key_points:
                    st.markdown(f"- {point}")
            
            code_snippet = topic_content.get('code_snippet', '')
            if code_snippet and code_snippet != 'N/A':
                st.markdown("**Code Example:**")
                st.code(code_snippet, language='python')
            
            next_steps = topic_content.get('next_steps', '')
            if next_steps:
                st.markdown(f"**Next Steps:** {next_steps}")
        
        with tab2:
            st.markdown("### Learning Resources")
            links = topic_content.get('links', [])
            
            if links:
                for i, link in enumerate(links, 1):
                    title = link.get('title', f'Resource {i}')
                    url = link.get('url', '')
                    source = link.get('source', 'Unknown')
                    
                    if SecurityValidator.validate_url(url):
                        st.markdown(f"**{i}. {title}**")
                        st.markdown(f"- Source: {source}")
                        st.markdown(f"- [Link]({url})")
                        st.markdown("---")
                    else:
                        st.warning(f"Invalid link for resource {i}: {title}")
            else:
                st.info("No learning resources available for this topic.")
        
        with tab3:
            st.markdown("### Technical Details")
            st.json(topic_content)
    
    except Exception as e:
        shifu_logger.error(f"Error rendering topic details: {topic_name}", exception=e)
        st.error(f"Error loading content for {topic_name}. Please try again.")


def show_topic_details(topic_name: str, content: Dict):
    """
    Display topic details with a roadmap.sh inspired layout.
    """
    # Create tabs for structured learning
    tab1, tab2 = st.tabs(["📖 Guide", "🔗 Resources"])
    
    with tab1:
        st.markdown(f"### {topic_name}")
        description = content.get("description", "No description available.")
        st.markdown(description)
        
        st.markdown("---")
        
        # Key Points
        key_points = content.get("key_points", [])
        if key_points:
            st.markdown("#### 🔑 Key Concepts")
            for point in key_points:
                st.markdown(f"- {point}")
            st.markdown("")
        
        # Code Example
        code_snippet = content.get("code_snippet", "")
        
        # Handle cases where LLM returns a dict instead of string
        if isinstance(code_snippet, dict):
            code_snippet = code_snippet.get("code", str(code_snippet))
            
        if code_snippet and str(code_snippet).strip() and str(code_snippet).lower() != "n/a":
            st.markdown("#### 💻 Code Example")
            # Clean markdown fences if LLM included them in the string
            clean_code = str(code_snippet).strip()
            if clean_code.startswith("```"):
                import re
                clean_code = re.sub(r'^```\w*\n|```$', '', clean_code, flags=re.MULTILINE).strip()
            
            st.code(clean_code, language="python") 
            
        st.markdown("---")
        
        # Next Steps Interaction
        st.markdown('### <span class="material-symbols-outlined">double_arrow</span> What to Learn Next', unsafe_allow_html=True)
        
        # Suggestions from content
        next_steps_text = content.get("next_steps", "")
        if next_steps_text:
            st.info(f"💡 Suggestion: {next_steps_text}")
        
        # Interactive Input
        st.markdown("Ready to continue? Enter your next learning goal similar to roadmap.sh:")
        
        # Use a form to prevent immediate rerun on typing
        with st.form(key=f"next_step_form_{topic_name}"):
            col_input, col_btn = st.columns([3, 1])
            with col_input:
                user_next_step = st.text_input("I want to learn...", value=next_steps_text if next_steps_text else "", label_visibility="collapsed")
            with col_btn:
                start_next_btn = st.form_submit_button("Start Learning 🚀", use_container_width=True)
                
            if start_next_btn and user_next_step:
                # Set the query to the new topic and rerun to generate new roadmap
                st.session_state.next_query = user_next_step
                st.session_state.trigger_new_roadmap = True
                st.rerun()

    with tab2:
        st.markdown("### 📚 Learning Resources")
        links = content.get("links", [])
        if links:
            for link in links:
                st.markdown(f"""
                <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
                    <a href="{link.get('url', '#')}" target="_blank" style="text-decoration: none; color: #0366d6; font-weight: bold;">
                        {link.get('title', 'Resource')}
                    </a>
                    <br>
                    <span style="color: #666; font-size: 0.8em;">Source: {link.get('source', 'Web')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific resources found for this topic.")
            
    # Custom CSS for the "Premium Neubrutalism" feel
    st.markdown("""
    <style>
        /* Global Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;700;900&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');
        
        .material-symbols-outlined {
            font-family: 'Material Symbols Outlined' !important;
            font-size: 24px;
            display: inline-block;
            vertical-align: middle;
        }

        * { font-family: 'Public Sans', sans-serif !important; }

        /* Neubrutalism Cards */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            padding: 10px;
            background: #ffffff;
            border: 3px solid #18181b;
            box-shadow: 6px 6px 0px #18181b;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 44px;
            background-color: #ffffff !important;
            border: 2px solid #18181b !important;
            border-radius: 8px !important;
            padding: 0 20px !important;
            font-weight: 800 !important;
            color: #18181b !important;
            box-shadow: 3px 3px 0px #18181b;
            transition: all 0.1s ease-in-out;
        }
        .stTabs [aria-selected="true"] {
            background-color: #fde047 !important; /* Yellow accent */
            transform: translate(1px, 1px);
            box-shadow: 1px 1px 0px #18181b !important;
        }
        
        /* Expanders as Neubrutalism Blocks */
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 3px solid #18181b !important;
            border-radius: 12px !important;
            box-shadow: 8px 8px 0px #18181b !important;
            margin-bottom: 2rem !important;
            padding: 10px;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 900 !important;
            color: #18181b !important;
            font-size: 1.2rem !important;
            text-transform: uppercase;
        }
        
        /* Info/Success/Warning Boxes */
        div[data-testid="stNotification"] {
            border: 3px solid #18181b !important;
            border-radius: 12px !important;
            box-shadow: 6px 6px 0px #18181b !important;
            font-weight: 700;
        }
        
        /* Input Fields */
        .stTextInput input, .stTextArea textarea {
            border: 3px solid #18181b !important;
            border-radius: 12px !important;
            padding: 12px !important;
            font-weight: 600 !important;
            box-shadow: 4px 4px 0px #e2e8f0 !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            box-shadow: 4px 4px 0px #fde047 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def show_topic_sidebar(roadmap_data: Dict, selected_topic_id: str):
    """
    Show topic details in sidebar when user selects a topic.
    """
    roadmap = roadmap_data.get("roadmap", {})
    modules = roadmap.get("modules", [])
    
    # Find the selected topic (RECURSIVE)
    selected_content = None
    selected_name = ""
    
    def find_topic(nodes, target_id):
        nonlocal selected_content, selected_name
        for node in nodes:
            if node["id"] == target_id:
                selected_content = node.get("content", {})
                selected_name = node["name"]
                return True
            if "subtopics" in node and node["subtopics"]:
                if find_topic(node["subtopics"], target_id):
                    return True
        return False

    find_topic(modules, selected_topic_id)
    
    if selected_content:
        with st.sidebar:
            st.markdown("---")
            show_topic_details(selected_name, selected_content)
    else:
        st.sidebar.warning("Please generate content first to view topic details!")


def roadmap_page(llm):
    """
    Main roadmap page UI.
    """
    st.header("📚 Learning Roadmap Generator")
    st.markdown("Generate personalized learning roadmaps in seconds!")
    
    # Initialize generators
    if 'roadmap_generator' not in st.session_state:
        st.session_state.roadmap_generator = RoadmapGenerator(llm)
    
    if 'content_generator' not in st.session_state:
        st.session_state.content_generator = ContentGenerator(llm)
    
    roadmap_gen = st.session_state.roadmap_generator
    content_gen = st.session_state.content_generator
    
    # Handle trigger from "Next Steps"
    if st.session_state.get("trigger_new_roadmap", False):
        # Update query with the next step
        st.session_state.initial_query = st.session_state.next_query
        # Reset trigger
        st.session_state.trigger_new_roadmap = False
        st.rerun()

    # Input section
    col1, col2 = st.columns([2, 1])
    
    initial_query_val = st.session_state.get("initial_query", "")
    
    with col1:
        query = st.text_area(
            "🎯 What do you want to learn?",
            value=initial_query_val,
            placeholder="Examples:\n- I want to learn RAG from scratch\n- Frontend development roadmap\n- Machine learning for beginners",
            height=100,
            key="roadmap_query_input"
        )
    
    with col2:
        user_context = st.text_area(
            "👤 Your background (optional)",
            placeholder="e.g., I know Python and basic ML",
            height=100
        )
    
    # Generate roadmap button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        generate_structure_btn = st.button("🚀 Generate Roadmap", type="primary", use_container_width=True)
    
    # Generate roadmap structure
    if generate_structure_btn and query.strip():
        with st.spinner("🔍 Creating your learning roadmap..."):
            # Check for existing roadmap
            existing_filename = roadmap_gen.find_existing_roadmap(query)
            
            if existing_filename:
                roadmap_data = roadmap_gen.load_roadmap(existing_filename)
                st.success("✅ Found existing roadmap!")
            else:
                # Generate new roadmap
                roadmap_data = roadmap_gen.generate_roadmap_structure(query, user_context)
                filename = roadmap_gen.save_roadmap(roadmap_data)
                st.success("✅ Roadmap generated successfully!")
            
            st.session_state.current_roadmap = roadmap_data
            st.session_state.roadmap_filename = roadmap_gen.save_roadmap(roadmap_data)
    
    # Display roadmap if generated
    if 'current_roadmap' in st.session_state:
        roadmap_data = st.session_state.current_roadmap
        
        st.markdown("---")
        
        # Roadmap visualization
        st.subheader("🗺️ Your Learning Path")
        
        # Generate and display Markmap (Mindmap)
        markmap_md = roadmap_gen.create_markmap_markdown(roadmap_data)
        render_markmap(markmap_md, height=600)
        st.markdown("""
        <style>
            /* Markmap Container */
            #markmap-container {
                border: 3px solid #18181b;
                border-radius: 12px;
                background: #ffffff;
                box-shadow: 6px 6px 0px #18181b;
                margin-bottom: 2.5rem;
                overflow: hidden;
            }
            
            /* High-Contrast Code Blocks (Premium Light Theme) */
            .stCodeBlock {
                border: 2px solid #18181b !important;
                border-radius: 10px !important;
                background-color: #ffffff !important;
                box-shadow: 4px 4px 0px #18181b !important;
                padding: 10px !important;
            }
            .stCodeBlock code {
                color: #18181b !important; /* Base color */
                font-family: 'Fira Code', 'Courier New', monospace !important;
            }
            
            /* Sketchy Button Styles (roadmap.sh style) */
            .stButton>button {
                border: 2px solid #18181b !important;
                border-radius: 8px !important;
                background-color: #ffffff !important;
                color: #18181b !important;
                font-weight: 700 !important;
                box-shadow: 3px 3px 0px #18181b !important;
                transition: all 0.1s ease-in-out !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            .stButton>button:hover {
                transform: translate(-1px, -1px) !important;
                box-shadow: 5px 5px 0px #18181b !important;
                background-color: #f8fafc !important;
            }
            .stButton>button:active {
                transform: translate(2px, 2px) !important;
                box-shadow: 0px 0px 0px #18181b !important;
            }
            /* Primary Button (Yellow Accent) */
            .stButton>button[kind="primary"] {
                background-color: #fde047 !important;
            }
            .stButton>button[kind="primary"]:hover {
                background-color: #facc15 !important;
            }
            
            /* Real-time Activity Stream */
            .activity-stream {
                background: #fefce8;
                border: 2px solid #ca8a04;
                border-radius: 8px;
                padding: 12px;
                max-height: 200px;
                overflow-y: auto;
                font-family: 'Inter', sans-serif;
                font-size: 0.95rem;
                margin-bottom: 15px;
                box-shadow: 3px 3px 0px #ca8a04;
            }
            .activity-item {
                padding: 6px 0;
                border-bottom: 1px dashed #fde68a;
                color: #854d0e;
            }
            .activity-item b { color: #18181b; }
        </style>
        """, unsafe_allow_html=True)

        # Re-enforce Markmap Theme
        
        # Content generation section - reduced gap
        st.markdown("<br>", unsafe_allow_html=True)  # Small spacing only
        
        # Content generation section
        col1, col2, col3 = st.columns([1, 1, 2])
        
        content_generated = roadmap_data.get("content_generated", False)
        generate_content_btn = False  # Initialize variable
            
        with col1:
            if not content_generated:
                generate_content_btn = st.button(
                    "📝 Generate Detailed Content",
                    type="primary",
                    use_container_width=True,
                    help="Generate comprehensive content for all topics (~1 minute)",
                    key="gen_content_btn"
                )
            else:
                st.success("✅ Content Generated!")
                if st.button("🔄 Regenerate Content", use_container_width=True, key="regen_content_btn"):
                    generate_content_btn = True
                    # Reset content_generated flag
                    roadmap_data["content_generated"] = False
        
        if generate_content_btn:
            # Create a status container for real-time progress
            status_container = st.status("🚀 Starting content generation...", expanded=True)
            
            try:
                roadmap = roadmap_data.get("roadmap", {})
                modules = roadmap.get("modules", [])
                context = roadmap_data.get("query", "")
                
                # 1. Identify all topics to generate (RECURSIVE)
                topics_to_generate = []
                
                def collect_topics(nodes, depth=1):
                    for node in nodes:
                        topics_to_generate.append({
                            "id": node["id"],
                            "name": node["name"],
                            "depth": depth
                        })
                        if "subtopics" in node and node["subtopics"]:
                            collect_topics(node["subtopics"], depth + 1)

                collect_topics(modules)
                
                total_topics = len(topics_to_generate)
                completed_count = 0
                progress_bar = status_container.progress(0, text=f"Generating content for 0/{total_topics} topics...")
                
                # Stream for real-time updates
                activity_stream_placeholder = st.empty()
                stream_items = []
                
                # Simple Sequential Content Generation
                for topic in topics_to_generate:
                    completed_count += 1
                    progress_bar.progress(completed_count / total_topics, text=f"Generating {completed_count}/{total_topics}: {topic['name']}")
                    
                    content = content_gen.generate_topic_content(topic["name"], context)
                    
                    # Add to real-time activity stream
                    stream_items.insert(0, f'<div class="activity-item">✨ Generated: <b>{topic["name"]}</b></div>')
                    activity_stream_placeholder.markdown(f'<div class="activity-stream">{"".join(stream_items)}</div>', unsafe_allow_html=True)
                    
                    # Store in roadmap_data (RECURSIVE UPDATE)
                    def update_content(nodes, target_id, content_data):
                        for node in nodes:
                            if node["id"] == target_id:
                                node["content"] = content_data
                                return True
                            if "subtopics" in node and node["subtopics"]:
                                if update_content(node["subtopics"], target_id, content_data):
                                    return True
                        return False

                    update_content(modules, topic["id"], content)
                
                roadmap_data["content_generated"] = True
                # Save the updated roadmap
                roadmap_gen.save_roadmap(roadmap_data)
                st.session_state.current_roadmap = roadmap_data
                
                status_container.update(label="✨ Content Generation Complete!", state="complete", expanded=False)
                st.rerun()
                
            except Exception as e:
                status_container.error(f"Error during generation: {e}")
                import traceback
                print(f"Generation error: {traceback.format_exc()}")
        
        # Display topics section
        if content_generated:
            st.markdown("---")
            st.subheader("📑 Explore Topics")
            st.markdown("Click on any topic below to see detailed content, examples, and resources!")
            
            roadmap = roadmap_data.get("roadmap", {})
            modules = roadmap.get("modules", [])
            
            # Recursive Rendering Function
            def render_recursive_topics(nodes, level=1):
                for node in nodes:
                    name = node['name']
                    content = node.get("content", {})
                    
                    # Use distinct levels for expanders and headers
                    if level == 1:
                        with st.expander(f"📦 {name}", expanded=True):
                            if content:
                                show_topic_details(name, content)
                            if node.get('subtopics', []):
                                st.markdown("#### Subtopics")
                                render_recursive_topics(node['subtopics'], level + 1)
                    else:
                        # For nested levels
                        indent = "  " * (level - 2)
                        st.markdown(f"{indent}**🔹 {name}**")
                        if content:
                            show_topic_details(name, content)
                        
                        if node.get('subtopics', []):
                            render_recursive_topics(node['subtopics'], level + 1)
                        # Add a small separator
                        st.markdown("")

            render_recursive_topics(modules)
        else:
            st.info("💡 Click 'Generate Detailed Content' to see comprehensive information for each topic!")
    
    elif generate_structure_btn and not query.strip():
        st.warning("⚠️ Please enter what you want to learn!")
    
    