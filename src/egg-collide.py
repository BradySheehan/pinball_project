import EggPost

if __name__ == "__main__":
    import sys, getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:],"i:o:n:k:h",["in=","out=","nodes=","keep=","help"])
    except getopt.GetoptError:
        print "Error: unknown parameter"
        sys.exit(2)

    keepValues = []
    for opt, arg in opts:
        if opt in ("-h","--help"):
            print "Help! I need somebody... help!"
            sys.exit()
            # Put in usage here sometime later
        if opt in ("-i","--in"):
            targetFile = arg
        if opt in ("-o","--out"):
            outFile = arg
        if opt in ("-n","--nodes"):
            print "nodes"
            targetNodes = arg.split(",")
        if opt in ("-k","--keep"):
            print "yays"
            keepValues = arg.split(",")

    if len(keepValues) > len(targetNodes):
        print "\nError: more keep values than target nodes"
        sys.exit(2)

    targetEgg = EggPost.EggPost(targetFile)
    for i in xrange(len(targetNodes)):
        if i < len(keepValues):
           targetEgg.collideGroup(targetNodes[i],keepValues[i])
          else:
         targetEgg.collideGroup(targetNodes[i])
    if outFile:
        targetEgg.saveEgg(outFile)
    else:
        targetEgg.saveEgg()