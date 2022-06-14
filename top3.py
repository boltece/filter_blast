#!/usr/bin/python

########################################################
#
# 
# by Niels Asmussen - November 2021
########################################################

from __future__ import print_function
import argparse,datetime,glob,os,re,sys
from os.path import isfile
#from decimal import *
#from math import log
from operator import itemgetter
#from collections import OrderedDict


#######################################################
# setup a class - if desired
########################################################
class top3(object):

    reads = {}

    def __init__(self, blastFile, pIndex, sIndex):

        # BASIC framework for file loading into class object..
        if isfile(blastFile):
            out("\topening file {0}".format(blastFile))

            with open(blastFile, 'r') as BLAST:
                for l in BLAST:
                    if l[0] != '#':
                        la = l.strip().split('\t')

                        #print (la[pIndex] + la[sIndex])

                        # check to see if this contig is in the dict
                        if la[pIndex] not in self.reads: self.reads[la[pIndex]] = []

                        # turn the evalue into a float so it can be sorted correctly
                        la[sIndex] = float(la[sIndex])
                        # add the list to the dict in the contig
                        self.reads[la[pIndex]].append(la)

                # test print
                #print(self.reads['dDocent_Contig_10768'])
                
                # sample line from genome annotation file:
                #dDocent_Contig_10767    scaffold13435   91.071  56  4   1   2   56  33059   33004   8.06e-10    69.4
                #print(sorted(self.reads['dDocent_Contig_10768'], key=itemgetter(10))[0:3])

            out("\tfinished processing annotation file, closing")
            BLAST.close()
        else:
            exit("unable to locate the annotation file ({0}) - EXITING".format(annotation))

    # possible class function to run
    def dump(self, summary, topX, sIndex):

        out("dumping based on column {0}".format(sIndex))
        # basic varible setup
        if isfile(summary): exit("summary file already exists...", "FAIL")

        out("\topening summary read count file {0} ".format(summary))
        sumOUT= open(summary, 'w')

         
        # Lexicographical sort of the the dictionary
        # import ordered dict again above..
        #self.reads = OrderedDict(sorted(self.reads.items()))
        # run through the dictionary setting the keys to be in alphabetical order
        # basic sort that doesn't handle different numbers types well
        for con in sorted(self.reads.keys()):
        #for con in self.reads:

            # sample line from genome annotation file:
            #dDocent_Contig_10767    scaffold13435   91.071  56  4   1   2   56  33059   33004   8.06e-10    69.4

            # print out test line
            #print(sorted(self.reads[con], key=itemgetter(10))[0:3])

            # pull out the lowest three for this contig based on evalue in column 10 that was set to a float 
            # when reading in the file...
            top3 = sorted(self.reads[con], key=itemgetter(sIndex))[0:topX]

            # check to make sure a hit exists
            # turn the float back into a string to let it be joined below
            # write to the output file
            for i in range(0,topX): 
                if len(top3) > i:
                    top3[i][sIndex] = str(top3[i][sIndex])
                    sumOUT.write("{0}\n".format('\t'.join(top3[i])))

        sumOUT.close()

# upgraded output message handler
# the breaker option can now support a multi option input if desired
# existing commands accepted but option to specify indent in # of 4 char tabs follow breaker call
# eg: above-1
def out(msg, breaker=0, newline=1, fileOnly=0):

    # check and see if the breaker command has a -INT following it
    # and pull that out to define the # of tabs to indent the line
    try: tab = int(breaker.split("-")[1]) * 4
    except: tab = 0
    if tab > 40: tab = 40

    if breaker == 1: msg = "{0!s:-<80}".format("")
    if isinstance(breaker, str):
        if breaker.startswith('above'): msg = "{0!s: <{widthIN}}{0!s:-<{widthFULL}}\n{0!s: <{widthIN}}{1}".format("", msg, widthIN=tab, widthFULL=80-tab)
        if breaker.startswith('below'): msg = "{0!s: <{widthIN}}{1}\n{0!s: <{widthIN}}{0!s:-<{widthFULL}}".format("", msg, widthIN=tab, widthFULL=80-tab)
        if breaker.startswith('both'): msg = "{0!s: <{widthIN}}{0!s:-<{widthFULL}}\n{0!s: <{widthIN}}{1}\n{0!s: <{widthIN}}{0!s:-<{widthFULL}}".format("", msg, widthIN=tab, widthFULL=80-tab)
        if breaker.startswith('open'): msg = "{0!s: <{widthIN}}{0!s:|<{widthFULL}}\n{0!s: <{widthIN}}{0!s:-<{widthFULL}}\n{0!s: <{widthIN}}{1!s}".format("", msg, widthIN=tab, widthFULL=80-tab)
        if breaker.startswith('close'): msg = "{0!s: <{widthIN}}{1!s}\n{0!s: <{widthIN}}{0!s:-<{widthFULL}}\n{0!s: <{widthIN}}{0!s:|<{widthFULL}}".format("", msg, widthIN=tab, widthFULL=80-tab)
        if breaker.startswith('tabIN'):
            if len(msg) == 0: msg = "{0!s: <{widthIN}}{0!s:-<{widthFULL}}".format("", widthIN=tab, widthFULL=80-tab)
            else: msg = "{0!s: <{widthIN}}{1}".format("", msg, widthIN=tab)

    # go with a more reasonable tab stop of 4...
    msg = msg.expandtabs(4)
    if newline:
        if not fileOnly: print(msg)
        LOG.write("{0}\n".format(msg))
    else:
        if not fileOnly: print(msg, end='')
        LOG.write("{0}".format(msg))


# make a controlled exit
def exit(msg, status="FAIL"):

    if msg != '':
        out('',1)
        out('',1)
        out(msg)
        out('',1)
        out('',1)

    LOG.write("\n\n{0!s:-^104}".format(''))
    LOG.write("\n{0!s:^25}{0!s:-^54}{0!s:^25}".format(''))
    LOG.write("\n{0!s:^40}{0!s:-^24}{0!s:^40}".format(''))
    LOG.write('\n{0!s:^104}'.format('top3.py finished on ' + datetime.datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')))
    LOG.write('\n{0!s:^104}'.format('status: ' + status))
    LOG.write("\n{0!s:^40}{0!s:-^24}{0!s:^40}".format(''))
    LOG.write("\n{0!s:^25}{0!s:-^54}{0!s:^25}".format(''))
    LOG.write("\n{0!s:-^104}\n".format(''))
    LOG.close()

    sys.exit()

# start it all, take some input and do some error checks... also dump help when needed
def main():

    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description=
    """Simple script to read in BLAST data and dump out 3 results for each unique contig with the lowest e-value
and dump it into a summary file using .sum to replace .tab.
expected tab delimited blast input:
dDocent_Contig_10767    scaffold13435   91.071  56  4   1   2   56  33059   33004   8.06e-10    69.4
contig ID in col 0, e=value in col 10

    Author: Niels Asmussen
    Created: March 16, 2022
    Modified: March 16, 2022""",)

    # positional input:
    parser.add_argument("blast",help="blast data file",metavar="\'.blast\'")
    parser.add_argument("summary",help="top3 output file",metavar="\'.top3\'")

    # typical input options:
    #sourceOptions = ['ncbi', 'ensembl']
    #parser.add_argument("-s", "--source", help="annotation source for gff/gtf file (def = ncbi)",default='ncbi',dest="source",choices=sourceOptions,required=True)
    parser.add_argument("-c", help="top X reads per contig, if fewer reads exist they will all be included",default='3',type=int, dest="topX",required=False,metavar="count")
    parser.add_argument("-p", help="primary index position",default='0',type=int, dest="pIndex",required=False,metavar="primary")
    parser.add_argument("-s", help="secondary index position: e-value, always set to float for sort",default='10',type=int, dest="sIndex",required=False,metavar="secondary")
    #parser.add_argument("-f", "--fold",help="output fold change file",dest="foldChange",action='store_true')
    #parser.add_argument("-b", "--base",help="base for value type log or logit (def = 2)",default=2,type=int,dest="logitBase",required=False,metavar="2")

    parser.add_argument("-l", "--log",help="turn OFF logfile generation, (date)+top3.log (blank = log)",dest="output",required=False,action='store_false')

    # parse the arguments
    args=vars(parser.parse_args())

    # true / false for logfile..
    if args['output']: args['output'] = datetime.datetime.now().strftime('%Y-%m-%d') + '-top3.log'
    else: args['output'] = "/dev/null"

    global LOG
    LOG = open(args['output'], 'a')
    LOG.write("\n\n{0!s:-^104}".format(''))
    LOG.write("\n{0!s:-^16}{0!s:^72}{0!s:-^16}".format(''))
    LOG.write("\n{0!s:-^8}{0!s:^88}{0!s:-^8}".format(''))
    LOG.write("\n{0!s:-^4}{1!s:^96}{0!s:-^4}".format('', 'top3.py run on ' + datetime.datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')))
    LOG.write("\n{0!s:-^8}{0!s:^88}{0!s:-^8}".format(''))
    LOG.write("\n{0!s:-^16}{0!s:^72}{0!s:-^16}".format(''))
    LOG.write("\n{0!s:-^104}\n".format(''))

    #out('SHOW ME THE ARGS!: {0}'.format(args), 'open')
    #out('','close')

    # replace only tab at the end of a string
    #args['summary'] = re.sub('tab$', 'sum', args['blast'])

    startDir = os.getcwd() + '/'
    out("PATH: {0}".format(startDir), 'above')
    out("INPUT VARS:")
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "X reads ", args['topX']))
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "primary index ", args['pIndex']))
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "secondary index ", args['sIndex']))
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "blast file ", args['blast']))
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "summary file ", args['summary']))
    #out("{0!s: >8}{1!s:.<28} {2}".format("|-> ", "IF log or logit, base ", args['logitBase']))
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "logFile ", args['output']), 'below')

    out("ERROR CHECK")
    #sample blast line
    #contig
    #dDocent_Contig_10767    scaffold13435   91.071  56  4   1   2   56  33059   33004   8.06e-10    69.4

    # file status
    foundError = ""
    # print out overview table of input / output files
    out("{0!s: <6}{1!s: <10}{2!s: <}".format("pass","exists?","filename"), "tabIN-1")

    if isfile(args['blast']): out("{0!s: <6}{1!s: <10}{2!s: <}".format("+", "YES", args['blast']), "tabIN-1")
    else: 
        out("{0!s: <6}{1!s: <10}{2!s: <}".format("-", "NO", args['blast']), "tabIN-1")
        foundError += "\n\t{0} missing".format(args['blast'])
    if isfile(args['summary'] + ''): 
        out("{0!s: <6}{1!s: <10}{2!s: <}".format("-", "YES", args['summary'] + ''), "tabIN-1")
        foundError += "\n\t{0} exists".format(args['summary'] + '')
    else: out("{0!s: <6}{1!s: <10}{2!s: <}".format("+", "NO", args['summary'] + ''), "tabIN-1")

    # handle errors and fail if found
    out("ERROR CHECK")
    if len(foundError) > 0:
        exit("ERROR CHECK FAILED! details below: {0}".format(foundError), "FAIL")
    else: out("PASSED!", "tabIN-1")

    out("\nloading blast file ", 'above')
    top = top3(args['blast'], args['pIndex'], args['sIndex'])
    out("blast file loaded...")

    out("\ndump out {0} lowest reads basd on e-value for each contig into {1}".format(args['topX'], args['summary'] ), 'above')
    top.dump(args['summary'], args['topX'], args['sIndex'])
    out("summary file should now be finished and ready...", 'below')

    exit("bye, things look good to me!", "Success")

if __name__ == "__main__":
    main()
