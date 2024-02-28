from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
from move import Move
from transformations.remove_fragment import RemoveFragment
from transformations.add_fragment import AddFragment
from fragment_factory import FragmentFactory
from activity_key import ActivityKey
import util as util
import uuid
import networkx as nx
import pm4py



class ReplaceFragment(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, fragment_one_start: str, fragment_one_end: str, replace_fragment: BPMN, activity_key: ActivityKey= ActivityKey.NAME):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.fragment_one_start = fragment_one_start
        self.fragment_one_end = fragment_one_end
        self.replace_fragment = replace_fragment

    def check():
        pass

    def apply(self):
        # get the nx graph for the bpmn process
        graph = self.bpmn_process.get_graph()
        # get the fragment_one predecessor
        fragment_one_start_node = util.get_node_from_activity_label(self.bpmn_process, self.fragment_one_start) if self.activity_key==ActivityKey.NAME else util.get_node_from_id(self.bpmn_process, self.fragment_one_start)
        fragment_one_predecessor = next(graph.predecessors(fragment_one_start_node))
        activity_label = fragment_one_predecessor.get_name() if self.activity_key==ActivityKey.NAME else fragment_one_predecessor.get_id()
        # remove fragment_one
        remove_fragment_transformator = RemoveFragment(self.bpmn_process, self.fragment_one_start, self.fragment_one_end, False, activity_key=self.activity_key)
        remove_fragment_transformator.check()
        remove_fragment_transformator.apply()
        # add new fragment sequential
        add_fragment_transformator = AddFragment(bpmn_process=self.bpmn_process, activity_after=activity_label, fragment=self.replace_fragment, move=Move.SerialMove, activity_key=self.activity_key)
        add_fragment_transformator.check()
        add_fragment_transformator.apply()

        