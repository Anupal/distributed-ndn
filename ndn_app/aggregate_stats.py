import os
import json
import sys


DIRECTORY_PATH = "stats"


def main():
    while True:
        file_contents = {}

        files = [
            f
            for f in os.listdir(DIRECTORY_PATH)
            if os.path.isfile(os.path.join(DIRECTORY_PATH, f))
        ]

        for file_name in files:
            file_path = os.path.join(DIRECTORY_PATH, file_name)
            with open(file_path, "r") as file:
                content = file.read()
                content_dict = json.loads(content)
                key = next(iter(content_dict))
                file_contents[key] = content_dict[key]

        with open(sys.argv[1], "w") as file:
            file.write(json.dumps(file_contents, indent=2))


if __name__ == "__main__":
    main()
