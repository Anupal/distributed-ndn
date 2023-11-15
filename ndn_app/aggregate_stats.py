import os
import json
import sys
from time import sleep


DIRECTORY_PATH = "stats"


def main():
    while True:
        file_contents = {}

        files = [
            f
            for f in os.listdir(DIRECTORY_PATH)
            if os.path.isfile(os.path.join(DIRECTORY_PATH, f))
        ]

        failure = False
        for file_name in files:
            file_path = os.path.join(DIRECTORY_PATH, file_name)
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    content_dict = json.loads(content)
                    key = next(iter(content_dict))
                    file_contents[key] = content_dict[key]
            except:
                failure = True
                break
        if failure:
            sleep(0.5)
            continue

        with open(sys.argv[1], "w") as file:
            file.write(json.dumps(file_contents, indent=2))
        sleep(0.5)


if __name__ == "__main__":
    main()
