import sys, logging
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *

class Verifier:

    
    
    def __init__(self):
        self.HOST = "mechanicalturk.sandbox.amazonaws.com"
        self.mtc = MTurkConnection(host=self.HOST)
        self.choices = ["Option 1", "Option 2", "Option 3"]
        
    def initialize_request_details(self, title, description, keywords):
        logging.info("VERIFIER | Request details: title = %s, description = %s, keywords = %s" % (title, description, keywords))

        self.title = title
        self.description = description
        self.keywords = keywords
        
    def create_verification_question(self, question_text, typeflag, title_text="Select the Question That Best Captures the Essence of the Given Text"):
        logging.info("VERIFIER | Creating question: question_text = %s, typeflag = %s, title_text = %s" % (question_text, typeflag, title_text))
        
        # BUILD OVERVIEW
        self.overview = Overview()
        self.overview.append_field("Title",title_text)
        self.overview.append(FormattedContent("""
            <ul>
                <li><font size="1" color="gray">Read these instructions carefully before proceeding.</font></li>
                <li><font size="1" color="gray">For the second question, read the paragraph/view the image and choose the MOST MEANINGFUL question that captures its essence.</font></li>
                <li><font size="1" color="gray">Your response will be verified against several factors. Please choose carefully.</font></li>
            </ul>"""))
        
        # IQ Test Question
        iqc1=QuestionContent()
        iqc1.append_field("Text","What is the fifth word in the third instruction?")
        
        ians1 = FreeTextAnswer()
        
        self.iq1 = Question(identifier="Check", content = iqc1, answer_spec=AnswerSpecification(ians1))
            
            
        # Question 1
        qc1=QuestionContent()
        if typeflag == "image":
            qc1.append(Binary("image", "jpg", question_text,title_text))
        else:
            qc1.append_field("Text",question_text)
        
        ans1 = SelectionAnswer(style="radiobutton",selections=self.choices,type="text",other=False)
        
        self.q1 = Question(identifier="Verification", content=qc1, answer_spec=AnswerSpecification(ans1))
            
        
        
        
    def build_question_form(self):
        logging.info("VERIFIER | Building question form...")

        # Building the Question Form

        self.question_form = QuestionForm()
        self.question_form.append(self.overview)
        self.question_form.append(self.iq1)
        self.question_form.append(self.q1)

    def launch_hit(self, max_assignments=2, duration=60*5, reward=0.02):
        logging.info("VERIFIER | Launching hit...")

        # Creating the HIT
        self.mtc.create_hit(questions=self.question_form, max_assignments=max_assignments, title=self.title, description=self.description, keywords=self.keywords, duration=duration, reward=reward, annotation="Verification")
