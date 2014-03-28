import time, logging, sys, shelve, verifier
import xml.dom.minidom
from boto.mturk.connection import MTurkConnection

class StudyHit:
    def __init__(self, hit, verifier, required_for_verification = 3):
        self.hit = mtc.get_hit(hit.HITId)[0]
        self.verifier = verifier
        self.required_for_verification = required_for_verification
        self.assignments = {}

    def add_assignment(self, assign_id, status = "pending", question = ""):
        self.assignments[assign_id] = {
            "status": status,
            "question": question
        }

    def mark_as_done(self):
        for assignment in self.assignments.values():
            if assignment["status"] == "pending":
                assignment["status"] = "done"
        
    def is_ready_for_verification(self):
        count = 0

        for assignment in self.assignments.values():
            if assignment["status"] == "pending":
                count += 1

        return count >= self.required_for_verification

    def get_pending_questions(self):
        count = 1
        questions_to_send = []
        for assignment in self.assignments.values():
            if assignment["status"] == "pending":
                questions_to_send.append(("Option " + str(count) + ": " + assignment["question"], count))
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


mtc = MTurkConnection(host = "mechanicalturk.sandbox.amazonaws.com")

hit_store = shelve.open("hits.shelve", writeback = True)

encountered_hits = {}

logging.basicConfig(
        level = logging.INFO,
        filename = "receiver.log",
        format = "%(asctime)s %(levelname)s %(message)s")

stdoutHandler = logging.StreamHandler(sys.stdout)

stdoutHandler.setLevel(logging.INFO)
stdoutHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logging.getLogger().addHandler(stdoutHandler)

def reject_answer(assign_id, hit_id):
    logging.info("Assignment %s rejected due to failed quality check!" % assign_id)

    mtc.reject_assignment(assign_id, feedback="Sorry! Failed the quality check.")
    mtc.extend_hit(hit_id, assignments_increment=1)

def verify_quality(answer):
    return answer.strip().lower() == "verified"

def send_for_verification(hit):
    logging.info("Hit ready for verification: %s" % hit.hit.HITId)

    details = hit.get_question_deets()

    if details[1] == "Image Question 1":
    # TODO: Make tags open ended
        hit.verifier.initialize_request_details("View the given image and pick the question that is most relevant",
                "View the given image and pick the best question amongst the three that is most relevant",
                "education, study, school")
        hit.verifier.create_verification_question(question_text=details[2],typeflag="image",title_text="View the given image and pick the best question amongst the three that is most relevant", choices = hit.get_pending_questions())
    elif details[1] == "Text Question 1":
        hit.verifier.initialize_request_details("Read the given paragraph and pick the question that is most relevant",
                "Read the given paragraph and pick the best question amongst the three that is most relevant",
                "education, study, school")
        hit.verifier.create_verification_question(question_text=details[2],typeflag="text",title_text="Read the given paragraph and pick the best question amongst the three that is most relevant", choices = hit.get_pending_questions())

    hit.verifier.build_question_form()
    hit.verifier.launch_hit()

    
    
def preprocess_answer(answer, assignment, hit_id):
    logging.info("Preprocess answer for assignment %s" % assignment.AssignmentId)

    hit = encountered_hits[hit_id]

    hit.add_assignment(assignment.AssignmentId, question = answer.strip())

    if hit.is_ready_for_verification():
        details = hit.get_question_deets()

        if details[0] == "Question":
            send_for_verification(hit)
        elif details[0] == "Verification":
            hit.mark_as_done()

def gather_hits(page_size = 10):
    logging.info("Gathering reviewable hits: page_size = %s" % page_size)

    return mtc.get_reviewable_hits(page_size = page_size)

def run(max_assignments):
    while True:
        hits = gather_hits()

        for hit in hits:

            if hit.HITId not in encountered_hits:
                encountered_hits[hit.HITId] = StudyHit(hit, verifier.Verifier(), max_assignments)

            assignments = mtc.get_assignments(hit.HITId)

            for assignment in assignments:

                if assignment.AssignmentId not in encountered_hits[hit.HITId].assignments and assignment.AssignmentStatus != "Rejected":
                    logging.info("Answers from worker %s" % assignment.WorkerId)
                    logging.info("Assignment ID: %s" % assignment.AssignmentId)
                    logging.info("Encountered hit assignments: %s" % encountered_hits[hit.HITId].assignments)

                    answers = assignment.answers[0]

                    logging.info("Answer: %s" % answers[0].fields[0])

                    quality = verify_quality(answers[0].fields[0])

                    if quality:
                        logging.info("Answer: %s" % answers[1].fields[0])

                        preprocess_answer(answers[1].fields[0], assignment, hit.HITId)
                    else:
                        reject_answer(assignment.AssignmentId, hit.HITId)

                    hit_store[str(hit.HITId)] = encountered_hits[hit.HITId]

                    hit_store.sync()

        time.sleep(15)

if __name__ == "__main__":

    run(sys.argv[1])

    hit_store.close()
