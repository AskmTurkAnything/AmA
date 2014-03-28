import sys, logging
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *

class Requester:
    # Initializing the MTurkConnection

    def __init__(self):
        self.HOST = "mechanicalturk.sandbox.amazonaws.com"
        self.mtc = MTurkConnection(host=self.HOST)

    # Create Overview of the Turk details
    def initialize_request_details(self, title, description, keywords):
        logging.info("REQUESTER | Request details: title = %s, description = %s, keywords = %s" % (title, description, keywords))

        self.title = title
        self.description = description
        self.keywords = keywords

    def create_question(self, question_text, typeflag, title_text="Provide Question(s) Based On The Text Below"):
        logging.info("REQUESTER | Creating question: question_text = %s, typeflag = %s, title_text = %s" % (question_text, typeflag, title_text))

        # BUILD OVERVIEW
        self.overview = Overview()
        self.overview.append_field("Title",title_text)
        self.overview.append(FormattedContent("""
            <ul>
                <li><font size="1" color="gray">Read these instructions carefully before proceeding.</font></li>
                <li><font size="1" color="gray">For the second question, read the paragraph/view the image and write down ONE MEANINGFUL question that captures its essence.</font></li>
                <li><font size="1" color="gray">Each Question will be verified against several factors like length, accuracy etc.</font></li>
                <li><font size="1" color="gray">Example Response: \"What is the definition of mTurking?\"</font></li>
            </ul>"""))


        # IQ Test Question
        iqc1=QuestionContent()
        iqc1.append_field("Text","What is the fifth word in the third instruction?")

        ians1 = FreeTextAnswer()

        self.iq1 = Question(identifier="Check", content = iqc1, answer_spec=AnswerSpecification(ians1))


        # Question 1
        qc1=QuestionContent()
        identifier = ""
        if typeflag == "image":
            qc1.append(Binary("image", "jpg", question_text,title_text))
            identifier = "Image Question 1"
        else:
            qc1.append_field("Text",question_text)
            identifier = "Text Question 1"

        lc = LengthConstraint(10)

        cs = Constraints()
        cs.append(lc)

        ans1 = FreeTextAnswer(constraints=cs)

        self.q1 = Question(identifier=identifier, content=qc1, answer_spec=AnswerSpecification(ans1))

        # Insert more questions here in the above format as needed.

    def build_question_form(self):
        logging.info("REQUESTER | Building question form...")

        # Building the Question Form

        self.question_form = QuestionForm()
        self.question_form.append(self.overview)
        self.question_form.append(self.iq1)
        self.question_form.append(self.q1)


    def launch_hit(self, max_assignments=2, duration=60*5, reward=0.02):
        logging.info("REQUESTER | Launching hit...")

        # Creating the HIT
        self.mtc.create_hit(questions=self.question_form, max_assignments=max_assignments, title=self.title, description=self.description, keywords=self.keywords, duration=duration, reward=reward, annotation="Question")


