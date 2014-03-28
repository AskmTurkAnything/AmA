import time, logging, sys, shelve
from boto.mturk.connection import MTurkConnection

class StudyHit:
    def __init__(self, hit_id, required_for_verification = 3):
        self.hit_id = hit_id
        self.required_for_verification = required_for_verification
        self.assignments = {}

    def add_assignment(self, assign_id, status = "pending", question = ""):
        self.assignments[assign_id] = {
            "status": status,
            "question": question
        }

    def is_ready_for_verification(self):
        count = 0

        for assignment in self.assignments.values():
            if assignment["status"] == "pending":
                count += 1

        return count >= 3


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

def preprocess_answer(answer, assignment, hit_id):
    hit = encountered_hits[hit_id]

    hit.add_assignment(assignment.AssignmentId)

    #encountered_hits[hit_id].add_assignment(assignment.AssignmentId, "pending")

    hit.assignments[assignment.AssignmentId]["question"] = answer.strip()

        #question = [ line.strip() for line in answer.strip().splitlines() if line.strip() ][0]
        #encountered_assignments[assignment.AssignmentId] = {"status":"pending","question":line[0],"hit_id":hit_id}

    if hit.is_ready_for_verification():
        logging.info("Hit ready for verification: %s" % hit_id)

def gather_hits(page_size = 10):
    logging.info("Gathering reviewable hits: page_size = %s" % page_size)

    return mtc.get_reviewable_hits(page_size = page_size)

def run():
    while True:
        hits = gather_hits()

        #print(mtc.get_account_balance())

        #all_hits = mtc.get_all_hits()

        #for hit in all_hits:
            #print(hit.Title, hit.Description)

        for hit in hits:

            if hit.HITId not in encountered_hits:
                encountered_hits[hit.HITId] = StudyHit(hit.HITId)

            assignments = mtc.get_assignments(hit.HITId)

            for assignment in assignments:
                # TODO: Change how this works

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
    run()

    hit_store.close()
