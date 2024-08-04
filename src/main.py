import sys
from html_parser import parse_html


def main(input_file, output_file):
    parse_html(input_file, output_file, resume=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
