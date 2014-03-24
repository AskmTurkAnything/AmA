import sys
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *

class Requester:
	# Initializing the MTurkConnection
	
	def __init__(self):
		self.HOST = "mechanicalturk.sandbox.amazonaws.com"
		self.mtc = MTurkConnection(host=self.HOST)

	# Create Overview of the Turk details
	def initialize_request_details(self, title, description, keywords):
		self.title = title
		self.description = description
		self.keywords = keywords
		
	# def insert_text(text):
		# self.content = QuestionContent()
		# self.content.append_field("Text", text)
		
	# def insert_image(img):
		# self.content = QuestionContent(binary = img)
		
	def create_question(self, question_text, title_text="Provide Question(s) Based On The Text Below"):	
	
		# BUILD OVERVIEW
		self.overview = Overview(title = "Instructions")
		self.overview.append(FormattedContent("""
			<ul>
				<li><font size="1" color="gray">Read the paragraph and write down one or more questions (max 5)</font></li>
				<li><font size="1" color="gray">Number your questions (1.,2.,etc.)</font></li>
				<li><font size="1" color="gray">Each Question will be verified against several factors like length, accuracy etc.</font></li>
				<li><font size="1" color="gray">Example Response: \"1.What time of the day is it?\"</font></li>
			</ul>"""))
			

		# Question 1
		qc1 = QuestionContent()
		qc1.append_field("Text",question_text)

		ans1 = FreeTextAnswer()

		self.q1 = Question(identifier="Question", content=qc1, answer_spec=AnswerSpecification(ans1))

		# Insert more questions here in the above format as needed.

	def build_question_form(self):
	
		# Building the Question Form

		self.question_form = QuestionForm()
		self.question_form.append(self.overview)
		self.question_form.append(self.q1)

	def launch_hit(self):
		# Creating the HIT

		self.mtc.create_hit(questions=self.question_form, max_assignments=2, title=self.title, description=self.description, keywords=self.keywords, duration=60*5, reward=0.05)

	def account_balance(self):
		print self.mtc.get_account_balance()

if __name__ == "__main__":
	if (len(sys.argv) < 1):
		print "Usage: python requester.py <name_of_file_with_text>"
		sys.exit(0)
	req = Requester()
	req.initialize_request_details("Read the given material and provide question(s)", 
		"Read the given paragraph and come up with logical, relevant questions that can be used in a study review session",
		"education, study, school")
	req.create_question(title_text="Question This", question_text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras nisi elit, rutrum nec laoreet et, rhoncus condimentum tellus. Donec quam est, condimentum ullamcorper sapien id, porta volutpat mauris. Pellentesque at elit euismod, congue mi non, tristique lorem. Morbi ornare, turpis sed dapibus dignissim, leo dolor aliquet nulla, vitae auctor sapien odio id mi. Proin ut rutrum mi, sit amet cursus felis. Aliquam in nulla sed arcu vestibulum auctor eu eget metus. Curabitur dolor eros, eleifend quis varius quis, malesuada quis ipsum. Praesent elementum velit eu nibh ultricies fringilla. In suscipit facilisis erat, sit amet tempor mauris dapibus et. Duis faucibus eros ut urna interdum gravida. Integer cursus enim cursus accumsan posuere. Cras laoreet tristique quam ut facilisis. Mauris congue nibh eu tellus consequat eleifend. Aenean viverra eros in risus euismod, sit amet lobortis augue venenatis.")
	req.build_question_form()
	req.launch_hit()
	req.account_balance()
	
	