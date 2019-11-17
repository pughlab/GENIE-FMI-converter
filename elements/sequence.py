import re
import sys
import os.path as path

from elements.requesting import get_segment, get_segment_local

# Note:  All cds-effects are matched after calling upper()

off_re = re.compile(r"^-?\d+([+-]\d+)?(_(\*|-)?\d+([+-]\d+)?)?")
sep_re = re.compile(r"^(INS|DEL|>)")
seq_re = re.compile(r"^([ACTG]+)")

cmap = {'A':'T', 'T':'A', 'C':'G', 'G':'C', 'N':'N', '-':'-'}

class Entry:

    def __init__(self, filename, text, start, strand):
        self.sep     = None
        self.seq     = None
        self.altseq  = None
        self.length  = 0
        self.chr     = None
        self.start   = None
        self.end     = None
        self.strand  = strand

        self.read(filename, text, start)


    def __str__(self):
        return "(" + " ".join((str(x) for x in (
            self.chr, self.start, self.end, self.seq,
            self.sep, self.altseq, self.length))) + ")"


    def read_offsets(self, text, i):
        m = re.match(off_re, text[i:])

        if m:

            i += m.end()

        return i


    def read_seq_sep(self, text, i):
        a = re.match(sep_re, text[i:])
        b = re.match(seq_re, text[i:])

        if a:  # sep -> length or sep -> seq
            self.sep = text[i:i + a.end()]
            i += a.end()

            b = re.match(off_re, text[i:])
            c = re.match(seq_re, text[i:])

            if b:
                self.length = int(text[i:i + b.end()])
                i += b.end()

                if self.sep == "DEL":
                    self.seq    = ""
                    self.altseq = "-"
                    self.start += 1
                    self.length -= 1

                elif self.sep == "INS":
                    self.seq    = "-"
                    self.altseq = ""

            elif c:
                if self.sep == "DEL":
                    i += 1
                    self.seq    = text[i:i + c.end()]
                    self.altseq = "-"
                    if len(self.seq) > 1:
                        self.length = len(self.seq) - 1
                    else:
                        self.length = 0

                    self.start += 1

                    if not self.strand:
                        self.start += 1

                elif self.sep == "INS":
                    self.seq    = "-"
                    self.altseq = text[i:i + c.end()]

                i += c.end()

        elif b:  # seq -> sep -> seq
            self.seq = text[i:i + b.end()]
            i += b.end()
            a = re.match(sep_re, text[i:])

            if a:
                self.sep = text[i:i + a.end()]
                i += a.end()
                b = re.match(seq_re, text[i:])

                if b:
                    self.altseq = text[i:i + b.end()]
                    i += b.end()

                    if self.sep == ">":
                        if len(self.seq) > 1:
                            self.length = len(self.seq) - 1
                        else:
                            self.length = 0

        return i


    def read(self, filename, text, start):
        self.chr   = start[0]
        self.start = start[1]

        index = self.read_offsets(text, 0)
        index = self.read_seq_sep(text, index)

        if index < len(text):
            print("Error reading cds-effect in {}: {}/{} - {}"
                    .format(filename, text, text[index:], self))

        if self.strand:
            if self.seq:
                self.seq = revc(self.seq)

            if self.altseq:
                self.altseq = revc(self.altseq)

        self.end = self.start + self.length


    def coords(self):
        return (self.start, self.end)


def revc(inp):
    return ''.join(cmap[c.upper()] for c in inp[::-1])


def get_pos(inp):
    out = inp.split(":")
    return (out[0][3:], int(out[1]))


def count(depth, fraction):
    return str(round(int(depth) * float(fraction) / 100))


def check_ref(filename, fasta, entry, prefix, ref_err):
    if fasta:
        if prefix:
            ref_seq = get_segment_local(fasta, prefix + entry.chr, entry.coords())
        else:
            ref_seq = get_segment_local(fasta, entry.chr, entry.coords())

    else:
        ref_seq = get_segment("http://genome.ucsc.edu/cgi-bin/das/hg19/dna",
                              entry.chr,
                              entry.coords())

    if not entry.seq:
        return ref_seq

    elif entry.seq == ref_seq:
        return ref_seq

    else:
        print(filename, entry, ref_seq, file=ref_err)
        return ""


def generate_maf(filename, iID, prefix, paths, p_ident, s_ident, fasta, out, ref_missing, ref_err):
    sample = "GENIE-{}-{}-{}".format(iID, p_ident, s_ident)

    for x in paths:
        ref_seq = None

        entry = Entry(filename,
                      x.attr("cds-effect").upper(),
                      get_pos(x.attr("position")),
                      x.attr("strand") == "-")

        if entry.seq != "-" and not check_ref(filename, fasta, entry, prefix, ref_err):
                continue

        if not entry.seq or not entry.altseq:
            print("{}/{}-{}".format(filename, p_ident, s_ident), entry, file=ref_missing)
            continue

        alt_count = count(x.attr("depth"), x.attr("percent-reads"))

        print("{}\t{}".format(entry.chr, entry.start), entry.seq, entry.altseq,
                         sample, alt_count, x.attr("depth"),
              file=out, sep="\t")
