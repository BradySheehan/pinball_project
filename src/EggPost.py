from pandac.PandaModules import EggData, EggGroup, Filename

class EggPost(EggData):
    def __init__(self,filename):
        super(EggPost,self).__init__()
        pandaPath = Filename.fromOsSpecific(filename)
        self.read(pandaPath)

    def __findInGroup(self, nodeList, groupName):
        """
        Searches a list of eggNodes for a named group,
        recursively searches, returns the first one it finds.
        If it doesn't find anything, returns False
        """
        returnNode = None
        for node in nodeList:
            if node.getClassType().getName() == "EggGroup":
                #print "Node name:",node.getName()
                if node.getName() == groupName:
                    return node
                testNode = self.__findInGroup(node.getChildren(),groupName)
                #print "Test Node:",testNode
                if testNode != False:
                    return testNode
        return False

    def findGroup(self,groupName):
        return self.__findInGroup(self.getChildren(),groupName)

    def tagGroup(self,groupName,tag,value):
        targetGroup = self.findGroup(groupName)
        #print targetGroup
        if targetGroup:
            print "tagging %s with %s:%s"%(groupName,tag,value)
            targetGroup.setTag(tag,value)

    def collideGroup(self,groupName,keep="False"):
        targetGroup = self.findGroup(groupName)
        if targetGroup:
            if keep == "True":
                cFlags = EggGroup.CFKeep+EggGroup.CFDescend
            else:
                cFlags = EggGroup.CFDescend
            targetGroup.setCsType(EggGroup.CSTPolyset)
            targetGroup.setCollideFlags(cFlags)

    def saveEgg(self,eggName=None):
        if eggName is None:
            saveFile = pandaPath
        else:
            saveFile = Filename.fromOsSpecific(eggName)
        self.writeEgg(saveFile)