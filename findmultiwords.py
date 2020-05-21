#!/usr/bin/env python3

from collections import Counter


class NgramList():
    allwords = []
    covered = []

    def __init__(self, file):
        # TODO Use the index (line number) as key, this will allow the elimination
        # TODO of the overlapping profiles.
        with open(args.i) as infile:
            for line in infile:
                word = line.split('\t')[10]
                NgramList.allwords.append(word)
                NgramList.covered.append(0)

        self.ngrams = {}
        for start, words in get2words(NgramList.allwords):
            wordname = "_".join(words)
            if wordname in self.ngrams:
                self.ngrams[wordname].add_start(start)
            else:
                self.ngrams[wordname] = Ngram(2, words, start)

    def grow_ngrams(self):
        ngs = list(self.ngrams.keys())
        more = True
        while len(ngs) and more:
            more = False
            for ng in ngs:
                ngram = self.ngrams[ng]
                #  print(ngram)
                if ngram.get_next():
                    # mark the positions in covered (list) so that we don't visit them again.
                    #  print("found longer ngram")
                    more = True
                    for pos in ngram.start:
                        for n in range(ngram.nsize+1):
                            NgramList.covered[pos+n] = 1
                else:
                    ngs.remove(ng)
            #  print("ngs: ", len(ngs), more)

    def printNgram(self, minsize=2):
        for ng in self.ngrams:
            if self.ngrams[ng].nsize >= minsize:
                print(self.ngrams[ng])


class Ngram(object):
    def __init__(self, n, words, start):
        self.nsize = n
        self.words = words
        self.start = [start, ]

    def __repr__(self):
        return f"{self.nsize}, {self.words}, {self.start}"

    def get_next(self):
        newwords = Counter()
        newstarts = {}
        for pos in self.start:
            if NgramList.covered[pos] == 1:
                self.start.remove(pos)
                continue
            #  try:
            if pos+self.nsize >= len(NgramList.allwords):
                continue
            #  print(pos, self.nsize)
            nw = NgramList.allwords[pos+self.nsize]
            #  print(nw, NgramList.allwords[pos+self.nsize])
            newwords[nw] += 1
            if nw not in newstarts:
                newstarts[nw] = []
            newstarts[nw].append(pos)
            #  except:
            #      print("error in get_next")
        #  print(newwords.most_common(1))
        #  print(newwords.most_common(1))
        if newwords.most_common(1) and \
                100.0*newwords.most_common(1)[0][1]/len(self.start) >= 30:
            #  print("perc cov", 100.0*newwords.most_common(1)[0][1]/len(self.start))
            res = self.addNgram(newwords.most_common(1)[0][0])
            for n in self.start:
                #  print(newstarts[newwords.most_common(1)[0][0]])
                if n not in newstarts[newwords.most_common(1)[0][0]]:
                    self.start.remove(n)
            return res
        else:
            return False

    def add_start(self, pos):
        self.start.append(pos)

    def addNgram(self, word):
        if len(self.start) < 2:
            return False
        if self.start[0]+self.nsize+1 < self.start[1]:
            self.nsize += 1
            self.words += [word]
            return True
        else:
            # we got a repeat element
            return False


def get2words(words):
    for i in range(len(words)-1):
        yield [i, [words[i], words[i+1]]]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find all repeated word sequences in a column")
    parser.add_argument("-i", help="Repeatmasker .out file")
    args = parser.parse_args()

    NG = NgramList(args.i)
    NG.grow_ngrams()
    NG.printNgram(3)
