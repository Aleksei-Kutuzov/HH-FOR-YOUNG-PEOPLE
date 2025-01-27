import os
import replicate


class PIX2PIX:
    def __init__(self, token=os.environ.get("REPLICATE_API_TOKEN")):
        self.API_TOKEN = token

    def model_query(self, filename: str, promt: str):
        input = {
            "image": open("uploads/" + filename, "rb"),
            "prompt": promt
        }
        print("START QUERY")
        output = replicate.run(
            "timothybrooks/instruct-pix2pix:30c1d0b916a6f8efce20493f5d61ee27491ab2a60437c13c588468b9810ec23f",
            input=input
        )
        for index, item in enumerate(output):
            with open(f"static/generates/{filename}", "wb") as file:
                file.write(item.read())

        return output