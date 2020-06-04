#!/usr/bin/env python3

from collections import Counter
import sys
import contextlib


@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != "-":
        fh = open(filename, "w")
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


class NgramList:
    allwords = []
    covered = []

    def __init__(self, file):
        # TODO Use the index (line number) as key, this will allow the elimination
        # TODO of the overlapping profiles.
        self.positions = []
        with open(file) as infile:
            for line in infile:
                fields = line.strip().split("\t")
                self.positions.append([fields[4], fields[5], fields[6]])
                word = fields[9]
                NgramList.allwords.append(word)
                NgramList.covered.append(0)

        self.ngrams = {}
        #  for start, word in enumerate(NgramList.allwords):
        for start, word in getNwords(NgramList.allwords, 1):
            nameword = "_".join(word)
            if nameword in self.ngrams:
                self.ngrams[nameword].add_start(start)
            else:
                self.ngrams[nameword] = Ngram(word, start)
        #  print(self.ngrams, len(self.ngrams))
        #  print("1--", len(self.ngrams))

    def grow_ngrams(self, turns=0):
        ngs = list(self.ngrams.keys())
        more = True
        i = 0
        while len(ngs) and more:
            more = False
            for ng in ngs:
                ngram = self.ngrams[ng]
                #  print(ngram)
                if ngram.get_next():
                    more = True
                    #  for pos in ngram.start:
                    #      for n in range(ngram.nsize+1):
                    #          NgramList.covered[pos+n] = 1
                else:
                    ngs.remove(ng)
            i += 1
            if i >= turns:
                break
        #  print("grow", len(self.ngrams))

    def clean_overlapping(self):
        ngs = list(self.ngrams.keys())
        todelete = []
        #  print(len(ngs))
        i = 0
        while i <= len(ngs) - 1:
            #  print(f"doing {i}")
            try:
                ng1 = self.ngrams[ngs[i]]
            except:
                #  print(f"didn't find {ngs[i]}")
                break
            if ng1.nsize < 2:
                i += 1
                continue
            for j in range(i + 1, len(ngs)):
                ng2 = self.ngrams[ngs[j]]
                #  print(ng1, ng2)
                if are_overlapping(
                    [ng1.start[0], ng1.start[0] + ng1.nsize],
                    [ng2.start[0], ng2.start[0] + ng2.nsize],
                ):
                    #  print(f"overlapping with {j}")
                    diff = ng2.start[0] - ng1.start[0]
                    if diff > 0:
                        todelete.append(ngs[j])
                        del self.ngrams[ngs[j]]
                        ng1.words += ng2.words[:-diff]
                        ng1.nsize += diff
                else:
                    break
            i = j

    def stats(self):
        maxlen = max([self.ngrams[n].nsize for n in self.ngrams])
        print(f"number of ngrams: {len(self.ngrams)}")
        print(f"longest ngram: {maxlen}")

    def writeNgrams(self, file=None, minsize=2, maxsize=None):
        with smart_open(file) as infile:
            for ng in self.ngrams:
                if len(self.ngrams[ng].start) < 2:
                    continue
                if self.ngrams[ng].nsize >= minsize:
                    #  print(minsize, maxsize)
                    if maxsize:
                        if self.ngrams[ng].nsize <= maxsize:
                            print(self.ngrams[ng], file=infile)
                            for st in self.ngrams[ng].start:
                                regstart = min(
                                    [
                                        p[1]
                                        for p in self.positions[
                                            st : st + self.ngrams[ng].nsize + 1
                                        ]
                                    ]
                                )
                                regstop = max(
                                    [
                                        p[2]
                                        for p in self.positions[
                                            st : st + self.ngrams[ng].nsize + 1
                                        ]
                                    ]
                                )
                                print(
                                    "\t".join(
                                        [self.positions[st][0], regstart, regstop]
                                    ),
                                    file=infile,
                                )
                    else:
                        print(self.ngrams[ng], file=infile)
                        for st in self.ngrams[ng].start:
                            regstart = min(
                                [
                                    p[1]
                                    for p in self.positions[
                                        st : st + self.ngrams[ng].nsize + 1
                                    ]
                                ]
                            )
                            regstop = max(
                                [
                                    p[2]
                                    for p in self.positions[
                                        st : st + self.ngrams[ng].nsize + 1
                                    ]
                                ]
                            )
                            print(
                                "\t".join([self.positions[st][0], regstart, regstop]),
                                file=infile,
                            )


class Ngram(object):
    def __init__(self, words, start):
        self.words = [
            words,
        ]
        self.start = [
            start,
        ]
        self.nsize = len(self.words)

    def __repr__(self):
        return f"#{str(self.nsize)}\t{self.words}\t{self.start}"

    def get_next(self):
        newwords = Counter()
        newstarts = {}
        for pos in self.start:
            if NgramList.covered[pos] == 1:
                self.start.remove(pos)
                continue
            if pos + self.nsize >= len(NgramList.allwords):
                continue
            #  print(pos, self.nsize)
            nw = NgramList.allwords[pos + self.nsize]
            #  print(nw, NgramList.allwords[pos+self.nsize])
            newwords[nw] += 1
            if nw not in newstarts:
                newstarts[nw] = []
            newstarts[nw].append(pos)

        if (
            newwords.most_common(1)
            and 100.0 * newwords.most_common(1)[0][1] / len(self.start) >= 30
        ):
            #  print("perc cov", 100.0*newwords.most_common(1)[0][1]/len(self.start))
            for n in self.start:
                #  print(newstarts[newwords.most_common(1)[0][0]])
                if n not in newstarts[newwords.most_common(1)[0][0]]:
                    self.start.remove(n)
            res = self.addNgram(newwords.most_common(1)[0][0])
            return res
        else:
            return False

    def add_start(self, pos):
        self.start.append(pos)

    def addNgram(self, word):
        if len(self.start) < 2:
            self.nsize += 1
            self.words += [word]
            return True
        for i in range(len(self.start) - 1):
            if self.start[i] + self.nsize + 1 < self.start[i + 1]:
                self.nsize += 1
                self.words += [word]
                return True
            else:
                # we got a repeat element
                del self.start[i + 1]
                return False


def getNwords(words, n):
    for i in range(len(words) - n):
        yield [i, words[i : i + n]]


def are_overlapping(r, s):
    return not (r[1] < s[0] or s[1] < r[0])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find all repeated word sequences in a column"
    )
    parser.add_argument("-i", help="Repeatmasker .out file")
    parser.add_argument("-o", default=None, help="Output filename")
    args = parser.parse_args()

    NG = NgramList(args.i)
    NG.grow_ngrams(10)
    #  NG.clean_overlapping()
    NG.writeNgrams(args.o, 3, 4)
