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
class distCalc(object):

    distRes = []

    def __init__(self, distFile):

        # BASIC framework for file loading into class object..
        if isfile(distFile):
            out("\topening file {0}".format(distFile))

            # stats trackers
            lineNum = 0
            lineSkip = 0
            spanNum = 0
            endIn = 0
            startIn = 0
            swapDB = 0
            swapQ = 0


            with open(distFile, 'r') as DIST:
                for l in DIST:

                    # reporters
                    found = False
                    span = False
                    hitIn = "NA"
                    sDist = 0
                    eDist = 0
                    minDist = 0
                    dist20K = False
                    swap = "NA"

                    if l[0] != '#':
                        la = l.strip().split('\t')

                        lineNum += 1
                        # skipping the header line...
                        if lineNum == 1: 
                            la = la[:9] + ['found', 'span', 'hit_loc', 'minDist', 'startDist', 'endDist', 'in20K', 'swap'] + la[9:]
                            self.distRes.append(la)
                            continue

                        #print (la)
                        out ("S: {0} \t E: {1} \t~\t TS: {2} \t TE: {3}".format(la[7], la[8], la[11], la[12]), "tabIN-1")

                        try:
                            dbStart = int(la[7])
                            dbEnd = int(la[8])
                            qStart = int(la[11])
                            qEnd = int(la[12])
                        except:
                            out("WARNING - following line could not be loaded - one of the start / end values was not an integer \n{0}\n ".format(" | ".join([str(ls) for ls in la])), "tabIN-1")
                            lineSkip += 1
                            continue

                        # is the start actually below the end?
                        if dbStart > dbEnd: 
                            swapDB += 1
                            tmp = dbStart
                            dbStart = dbEnd
                            dbEnd = tmp
                            swap = "DB"
                        if qStart > qEnd:
                            swapQ += 1
                            tmp = qStart
                            qStart = qEnd
                            qEnd = tmp
                            if swap == "NA": swap = "Q"
                            else: swap += "|Q"

                        # does the query read span the entire db read?
                        if (qStart < dbStart and qEnd > dbEnd):
                            span = True
                            hitIn = "in"
                            spanNum += 1
                            out("query SPANS the entire db region")

                        # is the query read starting within the db read?
                        elif (qStart <= dbEnd and qStart >= dbStart):
                            found = True
                            hitIn = "in"
                            startIn += 1
                            out("FOUND - START inside", "tabIN-2")

                        # is the query read ending within the db read?
                        elif (qEnd <= dbEnd and qEnd >= dbStart):
                            found = True
                            hitIn = "in"
                            endIn += 1
                            out("FOUND - END inside", "tabIN-2")

                        # determine the distances..
                        else:
                            #qStartTOdbStart = abs(qStart - dbStart)
                            #qStartTOdbEnd = abs(qStart - dbEnd)
                            #qEndTOdbStart = abs(qEnd - dbStart)
                            #qEndTOdbEnd = abs(qEnd - dbEnd)

                            # make a list in following order:
                            # query start to db start; query start to db end; query end to db start; query end to db end
                            distances = [abs(qStart - dbStart), abs(qStart - dbEnd), abs(qEnd - dbStart), abs(qEnd - dbEnd) ]


                            minDist = distances[distances.index(min(distances))]
                            sDist = distances[distances.index(min(distances[:2]))]
                            eDist = distances[distances.index(min(distances[2:]))]
                            out("ALL DIST: {0}".format(distances))
                            out("minDist: {0}, startDist: {1}, endDist: {2}".format(minDist, sDist, eDist))
                            if minDist < 20000: dist20K = True
                            if minDist == sDist: hitIn = "after"
                            elif minDist == eDist: hitIn = "before"

                        la = la[:9] + [str(found), str(span), hitIn, str(minDist), str(sDist), str(eDist), str(dist20K), swap] + la[9:]
                        self.distRes.append(la)
                            

            out ("STATS:", "above")
            out ("processed {0} lines, skipped {1}".format(lineNum, lineSkip), "tabIN-1")
            out ("{0} query read spans entire db read".format(spanNum ), "tabIN-1")
            out ("swap DB: {0}; swap query: {1}".format(swapDB, swapQ), "tabIN-1")
            out ("end In: {0}; start IN: {1}".format(endIn, startIn), "tabIN-1")

            #out ("FULL RESULTS\n{0}".format(self.distRes), "both")

                        # start in
                        # end in
                        # start in 20k
                        # start in 40k
                        # start in 60k
                        # start in 80k
                        # start in 100k
                        # start over 100k

                        #col 7 & 8 have start hit and end hit for target
                        #col 11 & 12 have connie's data - is 11 between 7 & 8? 
                        #break down distance by 20K from 7 or 8

            DIST.close()
        else:
            exit("unable to locate the file ({0}) - EXITING".format(distFile))

    # possible class function to run
    def dump(self, summary):

        out("dumping all lines in list")
        # basic varible setup
        if isfile(summary): exit("summary file already exists...", "FAIL")

        out("\topening summary read count file {0} ".format(summary))
        sumOUT= open(summary, 'w')
        for distLine in self.distRes:
           sumOUT.write("{0}\n".format('\t'.join(distLine))) 
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
    """Simple script to read in tab delim data and calculate distance between multiple columns
and dump it into a summary file using .sum to replace .tab.
expected tab delimited input:

col 7 & 8 have start hit and end hit for target
col 11 & 12 have connie's data - is 11 between 7 & 8? 
break down distance by 20K from 7 or 8

481 dDocent_Contig_65343    0.945400973 super1454   PITA_18237  GFACS   gene    7671    72939   in  intron  49973   49919   1.58E-16    1   -   phosphatase 2C  "GO:0008152-metabolic process(L=1),GO:0009987-cellular process(L=1),"       "GO:0003824-catalytic activity(L=1),GO:0005488-binding(L=1),"   "PFAM (PP2C), SMART (PP2Cc, PP2C_SIG, COIL, SIGNAL)"    P.taeda gene for protochlorophyllide reductase  5.00E-28            NA  100 55  0   0   2   56  92.4    0.027   0.945400973 XP_031502254.1  67.2    305 98  1   13  317 45  347 2.30E-108   95.9    XP_031502254.1 probable protein phosphatase 2C 52 [Nymphaea colorata]   nymphaea colorata   nymphaea colorata;nymphaea;nymphaeaceae;nymphaeales;magnoliopsida;spermatophyta;euphyllophyta;tracheophyta;embryophyta;streptophytina;streptophyta;viridiplantae;eukaryota;cellular organisms;root  /home/FCAM/egrau/gmap/Pita/entap_results/similarity_search/DIAMOND/blastp_Pita_final_complete.out   No  Yes 29760.VIT_16s0050g02570.t01 3.10E-107   393.7       Viridiplantae   virNOG[6]   "1BG4Q@strNOG,1DU2D@virNOG,COG0631@NOG,KOG0698@euNOG"


contig ID in col 0, e=value in col 10
    List ouput sorting options available:
        none: output order will match input
        basic: python's default sort
        complex: assume ID field is in format dDocent_Contig_10767, dDocent_Contig_ will be dropped and sort will function on the remaining integer

    Author: Niels Asmussen
    Created: March 25, 2022
    Modified: March 25, 2022""",)

    # positional input:
    parser.add_argument("input",help="input data file",metavar="\'.input\'")
    parser.add_argument("dist",help="dist output file",metavar="\'.dist\'")

    # typical input options:
    sortOptions = ['complex', 'basic', 'none']
    # sort the keyList based on the assumption that the beginning text
    # matches (abc_def_###) and that the final int bit is what should be sorted..

    #parser.add_argument("-o", help="should the output list be organized as described above? (def: complex)",default='complex',dest="sortMeth",choices=sortOptions,required=False)
    #parser.add_argument("-c", help="distanceX reads per contig, if fewer reads exist they will all be included (def: 3)",default='3',type=int, dest="dist",required=False,metavar="count")
    #parser.add_argument("-p", help="primary index position (def: 0)",default='0',type=int, dest="pIndex",required=False,metavar="primary")
    #parser.add_argument("-s", help="secondary index position: e-value, always set to float for sort (def: 10)",default='10',type=int, dest="sIndex",required=False,metavar="secondary")
    #parser.add_argument("-f", "--fold",help="output fold change file",dest="foldChange",action='store_true')
    #parser.add_argument("-b", "--base",help="base for value type log or logit (def = 2)",default=2,type=int,dest="logitBase",required=False,metavar="2")

    parser.add_argument("-l", "--log",help="turn OFF logfile generation, (date)+dist.log (blank = log)",dest="output",required=False,action='store_false')

    # parse the arguments
    args=vars(parser.parse_args())

    # true / false for logfile..
    if args['output']: args['output'] = datetime.datetime.now().strftime('%Y-%m-%d') + '-dist.log'
    else: args['output'] = "/dev/null"

    global LOG
    LOG = open(args['output'], 'a')
    LOG.write("\n\n{0!s:-^104}".format(''))
    LOG.write("\n{0!s:-^16}{0!s:^72}{0!s:-^16}".format(''))
    LOG.write("\n{0!s:-^8}{0!s:^88}{0!s:-^8}".format(''))
    LOG.write("\n{0!s:-^4}{1!s:^96}{0!s:-^4}".format('', 'dist.py run on ' + datetime.datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')))
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
    #out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "X reads ", args['dist']))
    #out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "primary index ", args['pIndex']))
    #out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "secondary index ", args['sIndex']))
    #out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "organization option ", args['sortMeth']))
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "input file ", args['input']))
    out("{0!s: >6}{1!s:.<30} {2}".format("-> ", "distance file ", args['dist']))
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

    if isfile(args['input']): out("{0!s: <6}{1!s: <10}{2!s: <}".format("+", "YES", args['input']), "tabIN-1")
    else: 
        out("{0!s: <6}{1!s: <10}{2!s: <}".format("-", "NO", args['input']), "tabIN-1")
        foundError += "\n\t{0} missing".format(args['input'])
    if isfile(args['dist'] + ''): 
        out("{0!s: <6}{1!s: <10}{2!s: <}".format("-", "YES", args['dist'] + ''), "tabIN-1")
        foundError += "\n\t{0} exists".format(args['dist'] + '')
    else: out("{0!s: <6}{1!s: <10}{2!s: <}".format("+", "NO", args['dist'] + ''), "tabIN-1")

    # handle errors and fail if found
    out("ERROR CHECK")
    if len(foundError) > 0:
        exit("ERROR CHECK FAILED! details below: {0}".format(foundError), "FAIL")
    else: out("PASSED!", "tabIN-1")

    out("\nloading subset file ", 'above')
    dist = distCalc(args['input'])
    out("distance file loaded...")

    out("\ndump out all lines {0}".format(args['dist'] ), 'above')
    dist.dump(args['dist'])
    out("summary file should now be finished and ready...", 'below')

    exit("bye, things look good to me!", "Success")

if __name__ == "__main__":
    main()
