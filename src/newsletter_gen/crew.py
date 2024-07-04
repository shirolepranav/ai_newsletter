from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents


# Uncomment the following line to use an example of a custom tool
# from gtarealest.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

@CrewBase
class NewsletterGenCrew():
	"""NewsletterGen crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[SearchAndContents(), FindSimilar(), GetContents()]
		)

	@agent
	def editor(self) -> Agent:
		return Agent(
			config=self.agents_config['editor'],
			verbose=True,
			tools=[SearchAndContents(), FindSimilar(), GetContents()]
		)
	
	@agent
	def designer(self) -> Agent:
		return Agent(
			config=self.agents_config['designer'],
			verbose=True,
			allow_delegation=False
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.researcher()
		)

	@task
	def edit_task(self) -> Task:
		return Task(
			config=self.tasks_config['edit_task'],
			agent=self.editor()
		)
	
	@task
	def newsletter_task(self) -> Task:
		return Task(
			config=self.tasks_config['newsletter_task'],
			agent=self.designer()
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the NewsletterGen crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)