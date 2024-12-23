from crewai import Agent, Crew, Process, Task
from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents
import os
import yaml

class NewsletterGenCrew:
    def __init__(self, model_provider='openai'):
        self.model_provider = model_provider
        self.llm_config = self._get_llm_config()
        self._load_configurations()

    def _get_llm_config(self):
        """Get LLM configuration based on selected provider"""
        configs = {
            'openai': {
                'model': os.getenv('OPENAI_MODEL_NAME', 'chatgpt-4o-latest'),
                'api_key': os.getenv('OPENAI_API_KEY'),
                'temperature': 0.7
            },
            'llama': {
                'model': os.getenv('LLAMA_MODEL_NAME', 'llama3.1-405b'),
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

    def _load_configurations(self):
        """Load YAML configurations"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(current_dir, 'config')
        
        # Load agents config
        agents_path = os.path.join(config_dir, 'agents.yaml')
        with open(agents_path, 'r') as file:
            self.agents_config = yaml.safe_load(file)
            
        # Load tasks config
        tasks_path = os.path.join(config_dir, 'tasks.yaml')
        with open(tasks_path, 'r') as file:
            self.tasks_config = yaml.safe_load(file)

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
        """Create tasks based on input type"""
        tasks = []
        
        if inputs.get('from_document', False):
            # For document-based generation
            tasks.extend(self._create_document_tasks(inputs))
        else:
            # For web search-based generation
            tasks.extend(self._create_web_tasks(inputs))
            
        return tasks

    def _create_document_tasks(self, inputs):
        """Create tasks for document-based generation"""
        tasks = []
        
        # Editor task to process document content
        edit_config = self.tasks_config['edit_task'].copy()
        tasks.append(Task(
            description=f"Review and structure the following document content into newsletter format: {inputs['content']}",
            expected_output=edit_config['expected_output'],
            agent=self.editor()
        ))
        
        # Newsletter compilation task
        newsletter_config = self.tasks_config['newsletter_task'].copy()
        tasks.append(Task(
            description=newsletter_config['description'].format(**inputs),
            expected_output=newsletter_config['expected_output'],
            agent=self.designer()
        ))
        
        return tasks

    def _create_web_tasks(self, inputs):
        """Create tasks for web search-based generation"""
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

        # Create appropriate tasks based on input type
        tasks = self.create_tasks(inputs)

        # Create and run the crew
        crew = Crew(
            agents=[self.researcher(), self.editor(), self.designer()],
            tasks=tasks,
            process=Process.sequential,
            verbose=2
        )

        return crew.kickoff()