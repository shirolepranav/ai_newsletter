import streamlit as st
from newsletter_gen.crew import NewsletterGenCrew
from dotenv import load_dotenv

class NewsletterGenUI:
    def __init__(self):
        st.set_page_config(page_title="Newsletter Generation", page_icon="📧", layout="wide")
        load_dotenv()
        if "topic" not in st.session_state:
            st.session_state.topic = ""
        if "days" not in st.session_state:
            st.session_state.days = 1
        if "newsletter" not in st.session_state:
            st.session_state.newsletter = ""
        if "generating" not in st.session_state:
            st.session_state.generating = False

    def load_html_template(self):
        try:
            with open("src/newsletter_gen/config/newsletter_template.html", "r") as file:
                return file.read()
        except FileNotFoundError:
            st.error("Newsletter template file not found. Please check the file path.")
            return ""

    def generate_newsletter(self, topic, days):
        inputs = {
            "topic": topic,
            "days": days,
            "html_template": self.load_html_template(),
        }
        return NewsletterGenCrew().crew().kickoff(inputs=inputs)

    def sidebar(self):
        with st.sidebar:
            st.title("Newsletter Generator")
            st.write(
                """
                To generate a newsletter:
                1. Enter a topic
                2. Select the number of days for recent news
                3. Click Generate Newsletter
                
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
            if st.button("Generate Newsletter"):
                st.session_state.generating = True

    def newsletter_generation(self):
        if st.session_state.generating:
            with st.spinner("Generating newsletter..."):
                try:
                    st.session_state.newsletter = self.generate_newsletter(
                        st.session_state.topic,
                        st.session_state.days
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

if __name__ == "__main__":
    NewsletterGenUI().render()