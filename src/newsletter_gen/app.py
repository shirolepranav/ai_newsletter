import streamlit as st
from newsletter_gen.crew import NewsletterGenCrew
from newsletter_gen.document_processor import DocumentProcessor
from dotenv import load_dotenv
import os

class NewsletterGenUI:
    def __init__(self):
        st.set_page_config(page_title="Newsletter Generation", page_icon="📧", layout="wide")
        load_dotenv()
        self.initialize_session_state()
        self.doc_processor = DocumentProcessor()

    def load_html_template(self):
        """Load HTML template from config directory"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(current_dir, 'config', 'newsletter_template.html')
            with open(template_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            st.error("Newsletter template file not found. Please check the file path.")
            return ""

    def initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            "topic": "",
            "days": 1,
            "model_provider": "openai",
            "newsletter": "",
            "generating": False,
            "use_document": False,
            "document_content": None
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def sidebar(self):
        with st.sidebar:
            st.title("Newsletter Generator")
            
            # Toggle between document upload and web search
            st.session_state.use_document = st.checkbox(
                "Generate from uploaded document", 
                value=st.session_state.use_document
            )

            if st.session_state.use_document:
                uploaded_file = st.file_uploader(
                    "Upload your document (PDF, Word, or Excel)", 
                    type=['pdf', 'doc', 'docx', 'xls', 'xlsx']
                )
                if uploaded_file:
                    try:
                        st.session_state.document_content = self.doc_processor.process_document(uploaded_file)
                        st.success("Document processed successfully!")
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
            else:
                st.text_input("Topic", key="topic")
                st.number_input(
                    "Days (how recent should the news be?)", 
                    min_value=1, 
                    max_value=30, 
                    value=1, 
                    key="days"
                )

            # Model selection with API key status
            model_options = {
                'openai': 'OpenAI GPT-4',
                'llama': 'Meta\'s Llama',
                'anthropic': 'Anthropic Claude'
            }
            
            st.selectbox(
                "Select AI Model",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                key="model_provider"
            )

            if st.button("Generate Newsletter"):
                st.session_state.generating = True

    def generate_newsletter(self):
        """Generate newsletter based on input mode"""
        if st.session_state.use_document:
            if not st.session_state.document_content:
                raise ValueError("No document content available")
            
            inputs = {
                "content": st.session_state.document_content,
                "model_provider": st.session_state.model_provider,
                "html_template": self.load_html_template(),
                "from_document": True
            }
        else:
            inputs = {
                "topic": st.session_state.topic,
                "days": st.session_state.days,
                "model_provider": st.session_state.model_provider,
                "html_template": self.load_html_template(),
                "from_document": False
            }
        
        crew = NewsletterGenCrew(model_provider=st.session_state.model_provider)
        return crew.kickoff(inputs=inputs)

    def render(self):
        self.sidebar()
        
        if st.session_state.generating:
            with st.spinner("Generating newsletter..."):
                try:
                    st.session_state.newsletter = self.generate_newsletter()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.newsletter = ""
            st.session_state.generating = False

        if st.session_state.newsletter:
            st.success("Newsletter generated successfully!")
            st.download_button(
                label="Download HTML file",
                data=st.session_state.newsletter,
                file_name="newsletter.html",
                mime="text/html",
            )
            
            st.subheader("Newsletter Preview")
            st.components.v1.html(st.session_state.newsletter, height=600, scrolling=True)

if __name__ == "__main__":
    NewsletterGenUI().render()