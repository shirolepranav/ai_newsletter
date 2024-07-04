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


# def run():
#     # Replace with your inputs, it will automatically interpolate any tasks and agents information
#     inputs = {
#         'topic': input('Enter the topic for your newsletter: '),
#         'html_template': load_html_template()
#     }
#     NewsletterGenCrew().crew().kickoff(inputs=inputs)

def run(topic):
    inputs = {
        'topic': topic,
        'html_template': load_html_template()
    }
    result = NewsletterGenCrew().crew().kickoff(inputs=inputs)
    return result  # This should be the HTML content of the newsletter

