import boto, mimetypes, time, logging, datetime

class Chunker:
    def __init__(self, requester):
        self.requester = requester

        self.s3 = boto.connect_s3()

        self.bucket = self.s3.create_bucket("ama-charlie-%s" % int(time.time()))

        logging.basicConfig(
                level = logging.INFO,
                filename = "log.log",
                format = "%(asctime)s %(levelname)s %(message)s")

    def process_file(self, filename):
        logging.info("CHUNKER | Processing %s" % filename)

        mt = self.determine_filetype(filename)

        ft = mt[0]

        if ft.split("/")[0] in ("image"):
            logging.info("CHUNKER | %s is an image" % filename)

            self.requester.initialize_request_details(
                    "Look at the given image and try and provide question(s) Kappa",
                    "View the given image and come up with logical, relevant question(s) that can be used as study material.",
                    "education, study, school")

            self.requester.create_question(
                    title_text = "(Need image specific title)",
                    typeflag = "image",
                    question_text = self.upload_image(filename))

            self.requester.build_question_form()

            self.requester.launch_hit()
        else:
            logging.info("CHUNKER | %s is text" % filename)

            paragraphs = self.chunk_text(filename)

            self.requester.initialize_request_details(
                    "Read the given paragraph and try and provide question(s)",
                    "Read the given paragraph and come up with logical, relevant question(s) that can be used as study material.",
                    "education, study, school")

            for paragraph in paragraphs:
                self.requester.create_question(
                        title_text = "(Need paragraph specific title)",
                        typeflag = "text",
                        question_text = paragraph)

                self.requester.build_question_form()

                self.requester.launch_hit()

    def determine_filetype(self, filename):
        return mimetypes.guess_type(filename)

    def chunk_text(self, filename):
        logging.info("CHUNKER | Chunking text...")

        with open(filename, "r") as f:
            return [ line.strip() for line in f.read().splitlines() if line.strip() ]

    def upload_image(self, filename):
        logging.info("CHUNKER | Uploading image to Amazon S3...")

        key = self.bucket.new_key(filename)

        key.set_contents_from_filename(filename, policy="public-read")

        return key.generate_url(86400, force_http=True, query_auth=False).replace(":433", "")
