import streamlit as st
from newsletter_gen.crew import NewsletterGenCrew
from dotenv import load_dotenv
import os

class NewsletterGenUI:
    def __init__(self):
        st.set_page_config(page_title="Newsletter Generation", page_icon="📧", layout="wide")
        load_dotenv()
        if "topic" not in st.session_state:
            st.session_state.topic = ""
        if "days" not in st.session_state:
            st.session_state.days = 1
        if "model_provider" not in st.session_state:
            st.session_state.model_provider = "openai"
        if "newsletter" not in st.session_state:
            st.session_state.newsletter = ""
        if "generating" not in st.session_state:
            st.session_state.generating = False

    def load_html_template(self):
        try:
            template_path = os.path.join('src', 'newsletter_gen', 'config', 'newsletter_template.html')
            with open(template_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            st.error("Newsletter template file not found. Please check the file path.")
            return ""

    def check_api_key(self, provider):
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'llama': 'LLAMA_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY'
        }
        key = os.getenv(key_mapping[provider])
        return bool(key and key.strip())

    def generate_newsletter(self, topic, days, model_provider):
        if not self.check_api_key(model_provider):
            raise ValueError(f"No API key found for {model_provider}. Please check your .env file.")
            
        inputs = {
            "topic": topic,
            "days": days,
            "model_provider": model_provider,
            "html_template": self.load_html_template(),
        }
        # Create a new instance of NewsletterGenCrew and call kickoff directly
        crew = NewsletterGenCrew(model_provider=model_provider)
        return crew.kickoff(inputs=inputs)

    def sidebar(self):
        with st.sidebar:
            st.title("Newsletter Generator")
            st.write(
                """
                To generate a newsletter:
                1. Enter a topic
                2. Select the number of days for recent news
                3. Choose your preferred AI model
                4. Click Generate Newsletter
                
                You can run the generation multiple times.
                If you want to save a newsletter, make sure to download the HTML template before running the generation again.
                """
            )
            st.text_input("Topic", key="topic")
            st.number_input(
                "Days (how recent should the news be?)", 
                min_value=1, 
                max_value=30, 
                value=1, 
                key="days",
                help="Select number of days to look back for news articles"
            )
            
            # Model selection with API key status
            model_options = {
                'openai': 'OpenAI GPT',
                'llama': 'Meta Llama',
                'anthropic': 'Anthropic Claude'
            }
            
            model_provider = st.selectbox(
                "Select AI Model",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                key="model_provider",
                help="Choose which AI model to use for generating the newsletter"
            )
            
            if not self.check_api_key(model_provider):
                st.warning(f"No API key found for {model_options[model_provider]}. Please add it to your .env file.")
            
            if st.button("Generate Newsletter", disabled=not self.check_api_key(model_provider)):
                st.session_state.generating = True

    def newsletter_generation(self):
        if st.session_state.generating:
            with st.spinner("Generating newsletter..."):
                try:
                    st.session_state.newsletter = self.generate_newsletter(
                        st.session_state.topic,
                        st.session_state.days,
                        st.session_state.model_provider
                    )
                except Exception as e:
                    st.error(f"An error occurred while generating the newsletter: {str(e)}")
                    st.session_state.newsletter = ""
            st.session_state.generating = False

        if st.session_state.newsletter and st.session_state.newsletter != "":
            st.success("Newsletter generated successfully!")
            st.download_button(
                label="Download HTML file",
                data=st.session_state.newsletter,
                file_name="newsletter.html",
                mime="text/html",
            )
            
            st.subheader("Newsletter Preview")
            st.components.v1.html(st.session_state.newsletter, height=600, scrolling=True)

    def render(self):
        self.sidebar()
        self.newsletter_generation()

    def check_api_key(self, provider):
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'llama': 'LLAMA_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY'
        }
        
        # Add debug print
        print("Current environment variables:", os.environ) 
        
        key_name = key_mapping[provider]
        key = os.getenv(key_name)
        return bool(key and key.strip())

if __name__ == "__main__":
    NewsletterGenUI().render()