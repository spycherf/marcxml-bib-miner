import argparse
import csv
import functools
import re
import sys
import time


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
    s = re.sub(r"[_\-/$.:]", "_", s)

    return s


def get_record_regexp():
    pattern = """(?<=<record>)
                 .*?
                 (?=</record>)
                 """

    return re.compile(pattern, re.VERBOSE | re.DOTALL)


def get_bib_cnum_regexp():
    pattern = """(?<=<controlfield\stag="001">)
                 (\S+)
                 (?=</controlfield>)
                 """

    return re.compile(pattern, re.VERBOSE)


def get_fields_with_tag_regexp(f_tag: str):
    if f_tag == "leader":
        pattern = """leader>
                     .*?
                     (?=</leader)
                     """
    else:
        pattern = """(?<=field\stag=")
                     {tag}
                     .*?
                     (?=</controlfield|</datafield)
                     """.format(tag=f_tag)

    return re.compile(pattern, re.VERBOSE | re.DOTALL)


def get_field_contents_regexp(f_tag: str, f_param: str):
    if f_tag == "leader" or f_tag.startswith("00"):
        if f_param == "":
            pattern = """{tag}"?>
                         (.*)  # group 1 (data to be mined)
                         """.format(tag=f_tag)
        else:
            pattern = """{tag}"?>
                         .{{{pos}}}
                         (.)  # group 1 (data to be mined)
                         """.format(tag=f_tag, pos=int(f_param))
        flags = re.VERBOSE
    else:  # data fields
        if f_param == "":
            pattern = """<subfield[^>]+>
                         (.*?)
                         <\/subfield>"""
        else:
            pattern = """{tag}"
                         .*?
                         <subfield\scode="{sbf_code}">
                         (.*?)  # group 1 (data to be mined)
                         (?=</subfield>)
                         """.format(tag=f_tag, sbf_code=f_param)
        flags = re.VERBOSE | re.DOTALL

    return re.compile(pattern, flags)


def get_indicators(field):
    return re.findall("ind[1-2]=\"(.)\"", field)


def get_all_hol_cnum(record: str):
    pattern = """(?<=tag="852")
                 .*?code="8">
                 (\S+)  # group 1 (data to be mined)
                 (?=</subfield)
                 """

    return re.findall(re.compile(pattern, re.VERBOSE | re.DOTALL), record)


@timer
def main():
    # Argument handling
    parser = argparse.ArgumentParser(description="Extract data from MARCXML bibliographic records")
    parser.add_argument("input_filename", action="store")
    parser.add_argument("output_filename", action="store")
    parser.add_argument("features",
                        action="store",
                        help="""Specify tags of the fields to be extracted.
                                Use ind[1-2]= to add conditions based on indicators.
                                Optionally, specify a parameter, i.e., 
                                the position (for LDR/control fields) 
                                or the subfield code (for data fields).
                                Feature separators: [,;]
                                Parameter separators: [_-/$.:]
                                Example: "LDR/6,264ind1= ind2=4,300,338$b,856ind2=1$u"
                                """
                        )
    parser.add_argument("-i",
                        "--show_ind",
                        action="store_true",
                        help="extract indicators for all features"
                        )
    parser.add_argument("-p",
                        "--count_ploc",
                        action="store_true",
                        help="count physical locations (field 852)"
                        )
    parser.add_argument("-e",
                        "--count_eloc",
                        action="store_true",
                        help="count electronic locations (field 856)"
                        )
    parser.add_argument("-l",
                        "--count_local_ext",
                        action="store_true",
                        help="count local extensions ($9 LOCAL)"
                        )
    parser.add_argument("-s",
                        "--split_by_holdings",
                        action="store_true",
                        help="write 1 row per holdings (requires embedded holdings data)"
                        )
    args = parser.parse_args()
    filename_in = args.input_filename
    filename_out = args.output_filename
    features = [clean_feature(_) for _ in re.split("[,;]", args.features)]

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

    for record_match in re.finditer(get_record_regexp(), f_in.read()):
        rec_n += 1

        if rec_n == 1 or rec_n % 100 == 0:
            update_progress(rec_n)

        record = record_match.group(0)
        dict_out = {}

        # Get bib control number
        m = re.search(get_bib_cnum_regexp(), record)
        bib_cnum = m.group(0) if m is not None else ""
        dict_out["bib_cnum"] = bib_cnum

        # Extract features
        for feature in features:
            feat_parts = re.split("_", feature)
            tag_ind = re.split("ind", feat_parts[0])
            tag = tag_ind[0]
            ind_filter = tag_ind[1:]
            param = feat_parts[1] if len(feat_parts) > 1 else ""
            data = []

            select_fields = re.findall(get_fields_with_tag_regexp(tag), record)

            for field in select_fields:
                inds = get_indicators(field)

                if args.show_ind:
                    if len(inds) > 0:
                        data.append("{" + "".join(inds) + "}")

                ind_check_passed = True
                
                if len(ind_filter) > 0:
                    for ind in ind_filter:
                        ind_n, ind_val = re.split("=", ind)

                        if inds[int(ind_n)-1] != ind_val:
                            ind_check_passed = False

                if ind_check_passed:
                    m = re.findall(get_field_contents_regexp(tag, param), field)
                    data.append(" ".join(m))

            dict_out[feature] = "|".join(data)

        # Count physical locations (= holdings)
        if args.count_ploc:
            dict_out["n_ploc"] = len(re.findall("tag=\"852\"", record))

        # Count electronic locations (= URL)
        if args.count_eloc:
            dict_out["n_eloc"] = len(re.findall("tag=\"856\"", record))

        # Count local extensions
        if args.count_local_ext:
            regexp = re.compile("(?<=code=\"9\">)local", re.IGNORECASE)
            dict_out["n_local_ext"] = len(re.findall(regexp, record))

        # Write to file output
        if args.split_by_holdings:
            for hol_cnum in get_all_hol_cnum(record):
                dict_out["hol_cnum"] = hol_cnum
                writer.writerow(dict_out)
        else:
            writer.writerow(dict_out)

    update_progress(rec_n)
    sys.stdout.write("\n")

    f_in.close()
    f_out.close()


if __name__ == "__main__":
    main()
