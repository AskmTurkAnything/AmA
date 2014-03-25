import boto, mimetypes

class Chunker:
    def __init__(self, requester):
        self.requester = requester

        self.s3 = boto.connect_s3()

        self.bucket = self.s3.create_bucket("ama-charlie-%s" % int(time.time()))

    def process_file(self, filename):
        mt = self.determine_filetype(filename)

        ft = mt[0]

        if ft.split("/")[0] in ("image"):
            pass
        else:
            paragraphs = self.chunk_text(filename)

            for paragraph in paragraphs:
                # text send question

    def determine_filetype(self, filename):
        return mimetypes.guess_type(filename)

    def chunk_text(self, filename):
        with open(filename, "r") as f:
            return f.read().splitlines()

    def upload_image(self, filename):
        key = self.bucket.new_key(filename)
        key.set_contents_from_filename(filename, policy="public-read")
        return key.generate_url(86400, force_http=True, query_auth=False).replace(":433", "")
