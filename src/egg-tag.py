import EggPost

if __name__ == "__main__":
    import sys, getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:],"i:o:n:t:v:h",["in=","out=","nodes=","tags=","values=","help"])
    except getopt.GetoptError:
        print "Error: unknown parameter"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h","--help"):
            print "Help! I need somebody... help!"
            # Put in usage here sometime later
        if opt in ("-i","--in"):
            targetFile = arg
        if opt in ("-o","--out"):
            outFile = arg
        if opt in ("-n","--nodes"):
            targetNodes = arg.split(",")
            print "targetNodes:",targetNodes
        if opt in ("-t","--tags"):
            nodeTags = arg.split(",")
        if opt in ("-v","--values"):
            tagValues = arg.split(",")

    if (len(targetNodes)+len(nodeTags)+len(tagValues))/3 != len(targetNodes):
        print "\nError: The number of target nodes, tags and values mismatch"
        sys.exit(2)
    targetEgg = EggPost.EggPost(targetFile)
    for i in xrange(len(targetNodes)):
        print "attempting to tag %s with %s:%s"%(targetNodes[i],nodeTags[i],tagValues[i])
        targetEgg.tagGroup(targetNodes[i],nodeTags[i],tagValues[i])
    if outFile:
        targetEgg.saveEgg(outFile)
    else:
        targetEgg.saveEgg()