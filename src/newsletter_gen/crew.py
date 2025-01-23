from crewai import Agent, Crew, Process, Task
from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents
import os
import yaml

class NewsletterGenCrew:
    """NewsletterGen crew"""
    
    def __init__(self, model_provider='openai'):
        self.model_provider = model_provider
        self.llm_config = self._get_llm_config()
        # Update paths to use proper directory structure
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(current_dir, 'config')
        self.agents_config = self._load_yaml(os.path.join(config_dir, 'agents.yaml'))
        self.tasks_config = self._load_yaml(os.path.join(config_dir, 'tasks.yaml'))

    def _load_yaml(self, file_path):
        """Load YAML configuration file"""
        try:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            # Provide default configurations if files can't be loaded
            if 'agents.yaml' in file_path:
                return self._default_agents_config()
            elif 'tasks.yaml' in file_path:
                return self._default_tasks_config()
            return {}

    def _default_tasks_config(self):
        """Default configuration for tasks if YAML fails to load"""
        return {
            'research_task': {
                'description': 'Conduct thorough research about the latest news on {topic} from the past {days} day(s).',
                'expected_output': 'A markdown document with the most relevant news stories.'
            },
            'edit_task': {
                'description': 'Review and improve the content quality of the researched news articles.',
                'expected_output': 'A markdown document with edited and improved news articles.'
            },
            'newsletter_task': {
                'description': 'Compile the final newsletter using the provided HTML template.\n{html_template}',
                'expected_output': 'A complete HTML newsletter with all articles formatted correctly.'
            }
        }

    def _default_agents_config(self):
        """Default configuration for agents if YAML fails to load"""
        return {
            'researcher': {
                'role': 'Senior Researcher',
                'goal': 'Uncover the latest news developments on the given topic.',
                'backstory': 'You are a seasoned journalist with a nose for news, known for great research skills and ability to dig up interesting stories.'
            },
            'editor': {
                'role': 'Editor-in-Chief',
                'goal': 'Ensure the quality and accuracy of the final newsletter.',
                'backstory': 'You are the Editor-in-Chief of a prestigious news organization, responsible for overseeing newsletter production.'
            },
            'designer': {
                'role': 'Newsletter Compiler',
                'goal': 'Fill the HTML template with the news articles provided.',
                'backstory': 'You are responsible for compiling the HTML code of the newsletter, ensuring proper formatting.'
            }
        }

    def _get_llm_config(self):
        """Get LLM configuration based on selected provider"""
        configs = {
            'openai': {
                'model': os.getenv('OPENAI_MODEL_NAME', 'gpt-4o'),
                'api_key': os.getenv('OPENAI_API_KEY'),
                'temperature': 0.7
            },
            'llama': {
                'model': os.getenv('LLAMA_MODEL_NAME', 'llama3.1-70b'),
                'api_key': os.getenv('LLAMA_API_KEY'),
                'temperature': 0.7
            },
            'anthropic': {
                'model': os.getenv('ANTHROPIC_MODEL_NAME', 'claude-3-opus-latest'),
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'temperature': 0.7
            }
        }
        return configs.get(self.model_provider)

    def researcher(self) -> Agent:
        """Create researcher agent"""
        return Agent(
            role=self.agents_config['researcher']['role'],
            goal=self.agents_config['researcher']['goal'],
            backstory=self.agents_config['researcher']['backstory'],
            verbose=True,
            llm_config=self.llm_config,
            tools=[SearchAndContents(), FindSimilar(), GetContents()]
        )

    def editor(self) -> Agent:
        """Create editor agent"""
        return Agent(
            role=self.agents_config['editor']['role'],
            goal=self.agents_config['editor']['goal'],
            backstory=self.agents_config['editor']['backstory'],
            verbose=True,
            llm_config=self.llm_config,
            tools=[SearchAndContents(), FindSimilar(), GetContents()]
        )
    
    def designer(self) -> Agent:
        """Create designer agent"""
        return Agent(
            role=self.agents_config['designer']['role'],
            goal=self.agents_config['designer']['goal'],
            backstory=self.agents_config['designer']['backstory'],
            verbose=True,
            llm_config=self.llm_config,
            allow_delegation=False
        )

    def create_tasks(self, inputs):
        """Create tasks with proper input substitution"""
        tasks = []

        # Research Task
        research_config = self.tasks_config['research_task'].copy()
        tasks.append(Task(
            description=research_config['description'].format(**inputs),
            expected_output=research_config['expected_output'],
            agent=self.researcher()
        ))

        # Edit Task
        edit_config = self.tasks_config['edit_task'].copy()
        tasks.append(Task(
            description=edit_config['description'].format(**inputs),
            expected_output=edit_config['expected_output'],
            agent=self.editor()
        ))

        # Newsletter Task
        newsletter_config = self.tasks_config['newsletter_task'].copy()
        tasks.append(Task(
            description=newsletter_config['description'].format(**inputs),
            expected_output=newsletter_config['expected_output'],
            agent=self.designer()
        ))

        return tasks

    def kickoff(self, inputs=None):
        """Initialize and run the crew with the given inputs"""
        if inputs and 'model_provider' in inputs:
            self.model_provider = inputs['model_provider']
            self.llm_config = self._get_llm_config()

        # Create tasks with the provided inputs
        tasks = self.create_tasks(inputs)

        # Create and run the crew
        crew = Crew(
            agents=[self.researcher(), self.editor(), self.designer()],
            tasks=tasks,
            process=Process.sequential,
            verbose=2
        )

        result = crew.kickoff()
    
        # Add this sanitization step
        return result.replace('```html', '').replace('```', '').strip()
    
    