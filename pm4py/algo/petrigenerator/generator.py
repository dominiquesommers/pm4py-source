from pm4py.models import petri
import random
import string

class SubtreeGenerator(object):
    def __init__(self, minNoOfActivitiesPerSubtree, maxNoOfActivitiesPerSubtree, maxNoOfSubtrees, probSpawnSubtree, possible_behaviors):
        self.minNoOfActivitiesPerSubtree = minNoOfActivitiesPerSubtree
        self.maxNoOfActivitiesPerSubtree = maxNoOfActivitiesPerSubtree
        self.maxNoOfSubtrees = maxNoOfSubtrees
        self.probSpawnSubtree = probSpawnSubtree
        self.possible_behaviors = possible_behaviors
        self.lastAddedPlace = None
        self.noOfPlaces = 0
        self.noOfHiddenTrans = 0
        self.noOfSubtrees = 0
        self.addedActivities = set()
        self.net = petri.net.PetriNet()
        self.startPlace = petri.net.PetriNet.Place('start')
        self.net.places.add(self.startPlace)
        self.simulate_net()

        self.lastAddedPlace.name = "end"

    def generate_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def generate_activity(self):
        while True:
            activity_name = self.generate_string(4)
            if not activity_name in self.addedActivities:
                self.addedActivities.add(activity_name)
                return activity_name

    def simulate_net(self):
        self.add_subtree(self.startPlace, 0)

    def add_subtree(self, subtreeSourceNode, recDepth, subtreeTargetNode=None, chosenBehavior=None):
        self.noOfSubtrees = self.noOfSubtrees + 1
        if chosenBehavior is None:
            chosenBehavior = random.choice(self.possible_behaviors)
        if chosenBehavior == "sequential" or chosenBehavior == "flower":
            numOfActivitiesThisSubtree = 0
            while numOfActivitiesThisSubtree < self.minNoOfActivitiesPerSubtree:
                numOfActivitiesThisSubtree = random.randrange(0, self.maxNoOfActivitiesPerSubtree)
            activitiesNames = []
            addedTransitions = []
            i = 0
            while i < numOfActivitiesThisSubtree:
                activityName = self.generate_activity()
                activitiesNames.append(activityName)
                trans = petri.net.PetriNet.Transition(activityName, activityName)
                self.net.transitions.add(trans)
                addedTransitions.append(trans)
                i = i + 1
        if chosenBehavior == "concurrent" or chosenBehavior == "parallel":
            numOfChildSubtrees = 0
            while numOfChildSubtrees < self.minNoOfActivitiesPerSubtree:
                numOfChildSubtrees = random.randrange(0, self.maxNoOfActivitiesPerSubtree)
            subtreesTypes = []
            for i in range(numOfChildSubtrees):
                if self.noOfSubtrees >= self.maxNoOfSubtrees:
                    subtreesTypes.append("sequential")
                else:
                    subtreesTypes.append(random.choice(self.possible_behaviors))
        if chosenBehavior == "sequential":
            nextSourceNode = subtreeSourceNode
            for i in range(numOfActivitiesThisSubtree):
                petri.utils.add_arc_from_to(nextSourceNode, addedTransitions[i], self.net)
                if i == numOfActivitiesThisSubtree-1 and subtreeTargetNode is not None and type(subtreeTargetNode) is petri.net.PetriNet.Place:
                    print(type(subtreeTargetNode))
                    nextSourceNode = subtreeTargetNode
                else:
                    self.noOfPlaces = self.noOfPlaces + 1
                    nextSourceNode = petri.net.PetriNet.Place('p'+str(self.noOfPlaces))
                    self.lastAddedPlace = nextSourceNode
                    self.net.places.add(nextSourceNode)
                petri.utils.add_arc_from_to(addedTransitions[i], nextSourceNode, self.net)
            r = random.random()
            if r < self.probSpawnSubtree and self.noOfSubtrees < self.maxNoOfSubtrees:
                self.add_subtree(self.lastAddedPlace, recDepth + 1, subtreeTargetNode=subtreeTargetNode)
            if subtreeTargetNode is not None and type(subtreeTargetNode) is petri.net.PetriNet.Transition:
                petri.utils.add_arc_from_to(self.lastAddedPlace, subtreeTargetNode, self.net)
        elif chosenBehavior == "concurrent":
            self.noOfPlaces = self.noOfPlaces + 1
            connectionNode = petri.net.PetriNet.Place('p'+str(self.noOfPlaces))
            self.net.places.add(connectionNode)
            for i in range(numOfChildSubtrees):
                self.add_subtree(subtreeSourceNode, recDepth+1, subtreeTargetNode=connectionNode, chosenBehavior=subtreesTypes[i])

            self.lastAddedPlace = connectionNode

def generate_petri(minNoOfActivitiesPerSubtree=2, maxNoOfActivitiesPerSubtree=4, maxNoOfSubtrees=10, probSpawnSubtree=0.4, possible_behaviors=["sequential", "concurrent"]):
    STG = SubtreeGenerator(minNoOfActivitiesPerSubtree, maxNoOfActivitiesPerSubtree, maxNoOfSubtrees, probSpawnSubtree, possible_behaviors)
    #STG.simulate_net()
    marking = petri.net.Marking({STG.startPlace: 1})
    return STG.net, marking