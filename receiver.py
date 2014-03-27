import time, logging, sys
from boto.mturk.connection import MTurkConnection

mtc = MTurkConnection(host = "mechanicalturk.sandbox.amazonaws.com")

logging.basicConfig(
        level = logging.INFO,
        filename = "receiver.log",
        format = "%(asctime)s %(levelname)s %(message)s")

stdoutHandler = logging.StreamHandler(sys.stdout)

stdoutHandler.setLevel(logging.INFO)
stdoutHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logging.getLogger().addHandler(stdoutHandler)

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
            assignments = mtc.get_assignments(hit.HITId)

            for assignment in assignments:
                logging.info("Answers from worker %s" % assignment.WorkerId)

                for question_form_answer in assignment.answers[0]:
                    logging.info("Answer: %s" % question_form_answer.fields[0])

        time.sleep(15)

if __name__ == "__main__":
    run()
