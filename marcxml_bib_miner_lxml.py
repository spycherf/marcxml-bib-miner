import argparse
import csv
import functools
import re
import sys
import time

from bs4 import BeautifulSoup


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start = time.perf_counter()
        value = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_time = end - start
        print("Elapsed time: {:0.4f} seconds".format(elapsed_time))

        return value

    return wrapper_timer


def update_progress(n_records: int):
    n_records = str(n_records)
    progress_text = " records parsed"

    for i in range(0, len(n_records) + len(progress_text)):
        sys.stdout.write("\b")

    sys.stdout.write("{0}{1}".format(n_records, progress_text))
    sys.stdout.flush()


def clean_feature(s: str):
    s = s.lower()
    s = re.sub("ldr", "leader", s)
    s = re.sub("[$/.:\-_]0?", "_", s)

    return s


@timer
def main():
    # Argument handling
    parser = argparse.ArgumentParser(description="Extract data from BIB")
    parser.add_argument("input_filename", action="store")
    parser.add_argument("output_filename", action="store")
    parser.add_argument("features",
                        action="store",
                        help="tag[$/.:-_]parameter[,;+], e.g. 'LDR/7;008;856$u'"
                        )
    parser.add_argument("-p",
                        "--count_ploc",
                        action="store_true",
                        help="Count physical locations (field 852)"
                        )
    parser.add_argument("-e",
                        "--count_eloc",
                        action="store_true",
                        help="Count electronic locations (field 856)"
                        )
    parser.add_argument("-l",
                        "--count_local_ext",
                        action="store_true",
                        help="Count local extensions ($9 LOCAL)"
                        )
    parser.add_argument("-s",
                        "--split_by_holdings",
                        action="store_true",
                        help="Write 1 row per holdings (requires embedded HOL)"
                        )
    args = parser.parse_args()
    filename_in = args.input_filename
    filename_out = args.output_filename
    features = [clean_feature(_) for _ in re.split("[,;+]", args.features)]

    # File handling
    f_in = open(filename_in, "r", encoding="utf-8")
    f_out = open(filename_out, "w", encoding="utf-8", newline="")
    header = ["bib_cnum",
              "hol_cnum",
              "n_ploc",
              "n_eloc",
              "n_local_ext"
              ] + features
    writer = csv.DictWriter(f_out, fieldnames=header)
    writer.writeheader()

    rec_n = 0
    soup = BeautifulSoup(f_in, "lxml")

    for record in soup.find_all("record"):
        rec_n += 1

        if rec_n == 1 or rec_n % 100 == 0:
            update_progress(rec_n)

        dict_out = {}

        # Get bib control number
        bib_cnum = record.find(tag="001")
        dict_out["bib_cnum"] = bib_cnum.contents[0] if bib_cnum else ""

        # Extract features
        for feature in features:
            tag_param = re.split("_", feature)
            tag = tag_param[0]
            param = tag_param[1] if len(tag_param) > 1 else ""
            data = []

            if tag == "leader":
                select_fields = record.find_all(tag)
            else:
                select_fields = record.find_all(tag=tag)

            for field in select_fields:
                contents = field.contents[0]

                if tag == "leader" or tag.startswith("00"):
                    if param in ["all", "full", ""]:
                        data.append(contents)
                    else:
                        data.append(contents[int(param)])
                else:
                    if param in ["all", "full", ""]:
                        data.append(field.get_text(" ", strip=True))
                    else:
                        for subfield in field.find_all(code=param):
                            data.append(subfield.contents[0])

            dict_out[feature] = "|".join(data)

        # Count physical locations (= holdings)
        if args.count_ploc:
            dict_out["n_ploc"] = len(record.find_all(tag="852"))

        # Count electronic locations (= URL)
        if args.count_eloc:
            dict_out["n_eloc"] = len(record.find_all(tag="856"))

        # Count local extensions
        if args.count_local_ext:
            regexp = re.compile("local", re.IGNORECASE)
            dict_out["n_local_ext"] = len(record.find_all(code="9", string=regexp))

        # Write to file output
        if args.split_by_holdings:
            for location in record.find_all(tag="852"):
                hol_cnum = location.find(code="8")
                dict_out["hol_cnum"] = hol_cnum.contents[0] if hol_cnum else ""
                writer.writerow(dict_out)
        else:
            writer.writerow(dict_out)

    update_progress(rec_n)
    sys.stdout.write("\n")

    f_in.close()
    f_out.close()


if __name__ == "__main__":
    main()
