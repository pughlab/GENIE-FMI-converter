import requests
import re
import sys

xml = re.compile(r'<.+>|\n')

# queries using closed intervals [x,y], 1-based
def get_segment(url, chrom, coords):
    r = requests.get(url, params={'segment': "{}:{},{}".format(chrom, *coords)})
    if r.status_code == requests.codes.ok:
        return re.sub(xml, '', r.text).upper()
    else:
        print("Bad request")
        return None


# queries using half-open intervals [x,y), 0-based
def get_segment_local(d, chrom, coords):
    try:
        return str(d[chrom][coords[0] - 1: coords[1]]).upper()
    except:
        print("No record for {}:{}-{} in fasta".format(chrom, coords[0] - 1, coords[1]), file=sys.stderr)
        return None
