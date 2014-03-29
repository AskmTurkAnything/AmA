import logging, xml.dom.minidom

class StudyHit:
    def __init__(self, hit, verifier, required_for_verification = 3):
        self.hit = hit
        self.verifier = verifier
        self.required_for_verification = required_for_verification
        self.assignments = {}

    def add_assignment(self, assign_id, status = "pending", question = "", question2 = ""):
        self.assignments[assign_id] = {
            "status": status,
            "question": question,
            "question2": question2
        }

    def mark_as_done(self, assignment_id):
         self.assignments[assignment_id]["status"] = "done"
         self.required_for_verification -= 1

    def is_ready_for_verification(self):
        count = 0

        for assignment in self.assignments.values():
            logging.info(assignment["status"])

            if assignment["status"] == "pending":
                count += 1

        logging.info("Number of Verification Results yet to be processed : %s " % str(self.required_for_verification))
        return count >= self.required_for_verification

    def get_pending_questions(self):
        count = 1
        questions_to_send = []
        for assign_id, assignment in self.assignments.items():
            if assignment["status"] == "pending":
                questions_to_send.append(("Option " + str(count) + ": " + assignment["question"], assign_id))
                count += 1
        return questions_to_send

    def get_text(self, node):
        logging.debug("Grabbing text from node...")
        rc = []
        for n in node:
            if n.nodeType == n.TEXT_NODE:
                rc.append(n.data)
        return "".join(rc)

    def get_question_deets(self):
        question = xml.dom.minidom.parseString(self.hit.Question)

        question_identifier = self.get_text(question.getElementsByTagName("QuestionIdentifier")[1].childNodes)

        if question_identifier != "Image Question 1":
            question_text = self.get_text(question.getElementsByTagName("Text")[1].childNodes)
        else:
            question_text = self.get_text(question.getElementsByTagName("DataURL")[0].childNodes)

        print(self.hit.RequesterAnnotation, question_identifier, question_text)
        return ( self.hit.RequesterAnnotation, question_identifier, question_text )
