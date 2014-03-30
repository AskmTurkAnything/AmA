import time, logging, sys, verifier, studyhit
from boto.mturk.connection import MTurkConnection

mtc = MTurkConnection(host = "mechanicalturk.amazonaws.com")

encountered_hits = {}

logging.basicConfig(
        level = logging.INFO,
        filename = "receiver.log",
        format = "%(asctime)s %(levelname)s %(message)s")

stdoutHandler = logging.StreamHandler(sys.stdout)

stdoutHandler.setLevel(logging.INFO)
stdoutHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logging.getLogger().addHandler(stdoutHandler)

def write_answers_to_file(filename, data):
    with open(filename, 'a') as f:
        for line in data:
            f.write(line)
    return True


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
        hit.verifier.initialize_request_details("View the  given image and pick the question that is most relevant",
                "View the given image and pick the best question amongst the three that is most relevant",
                "education, study, school")
        hit.verifier.create_verification_question(question_text=details[2],typeflag="image",title_text="View the given image and pick the best question amongst the three that is most relevant", choices = hit.get_pending_questions(), hitid = hit.hit.HITId)
    elif details[1] == "Text Question 1":
        hit.verifier.initialize_request_details("Read the given paragraph and pick the question that is most relevant",
                "Read the given paragraph and pick the best question amongst the three that is most relevant",
                "education, study, school")
        hit.verifier.create_verification_question(question_text=details[2],typeflag="text",title_text="Read the given paragraph and pick the best question amongst the three that is most relevant", choices = hit.get_pending_questions(), hitid = hit.hit.HITId)

    hit.verifier.build_question_form()
    hit.verifier.launch_hit(hitid = hit.hit.HITId)

def process_verification_results(hit, original_hitid):
    original_assignments = mtc.get_assignments(original_hitid)
    rank = {}
    for assign_id, assignment in hit.assignments.items():
        if assignment["question"] not in rank:
            rank[assignment["question"]] = 0

        rank[assignment["question"]] += 1

        for field in assignment["question2"]:
            if field not in rank:
                rank[field] = 0

            rank[field] -= 1

    to_print = []
    for assign_id, score in rank.items():
        if score > 0:
            original_hit = encountered_hits[original_hitid]
            to_print.append("Question Text : \n" + original_hit.get_question_deets()[2] + "\nChosen Answer : \n" + original_hit.assignments[assign_id]["question"] + "\n")

            mtc.approve_assignment(assign_id, feedback = "Thanks!")
        else:
            mtc.reject_assignment(assign_id)

    if write_answers_to_file(time.strftime("%d-%m-%Y"), to_print):
        logging.info("Disabling verification hit: %s" % hit.hit.HITId)
        mtc.disable_hit(hit.hit.HITId)

        logging.info("Disposing requester hit: %s" % original_hitid)
        mtc.dispose_hit(original_hitid)


def preprocess_answer(answers, assignment, hit_id):
    logging.info("Preprocess answer for assignment %s" % assignment.AssignmentId)

    hit = encountered_hits[hit_id]

    hit.add_assignment(assignment.AssignmentId, question = answers[1].fields[0].strip())
    details = hit.get_question_deets()
    tag = details[0].split()

    if tag[0] == "Verification":
        #logging.info("ANSWER FIELDS : %s " % str(answers[2].fields[0]) + str(answers[2].fields[1]))
        hit.assignments[assignment.AssignmentId]["question2"] = answers[2].fields
        hit.mark_as_done(assignment.AssignmentId)
        logging.info("HIT DETAILS FOR VERIFICATION: %s" % str(hit.assignments))

    if hit.is_ready_for_verification():
        logging.info("Hit ready for verification")

        if tag[0] == "Question":
            send_for_verification(hit)

        elif tag[0]== "Verification":
            logging.info(str(tag))
            process_verification_results(hit, tag[1])

def gather_hits(page_size = 10):
    logging.info("Gathering reviewable hits: page_size = %s" % page_size)

    return mtc.get_reviewable_hits(page_size = page_size)

def run(max_assignments):
    while True:
        hits = gather_hits()

        for hit in hits:
            if hit.HITId not in encountered_hits:
                encountered_hits[hit.HITId] = studyhit.StudyHit(mtc.get_hit(hit.HITId)[0], verifier.Verifier(), max_assignments)

            try:
                assignments = mtc.get_assignments(hit.HITId)
            except:
                logging.warn("HERE! HERE!! HERE!!! Service Unavailable!")

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

                        preprocess_answer(answers, assignment, hit.HITId)
                    else:
                        reject_answer(assignment.AssignmentId, hit.HITId)


        time.sleep(60)

if __name__ == "__main__":

    run(int(sys.argv[1]))
