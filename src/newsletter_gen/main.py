#!/usr/bin/env python
import sys
from newsletter_gen.crew import NewsletterGenCrew
from dotenv import load_dotenv
import os

load_dotenv()

def load_html_template(): 
    with open('src/newsletter_gen/config/newsletter_template.html', 'r') as file:
        html_template = file.read()
        
    return html_template

def run(topic, days=1):
    inputs = {
        'topic': topic,
        'days': days,
        'html_template': load_html_template()
    }
    result = NewsletterGenCrew().crew().kickoff(inputs=inputs)
    return result  # This should be the HTML content of the newsletter