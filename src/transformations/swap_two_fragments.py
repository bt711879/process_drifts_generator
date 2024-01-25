from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
import pm4py
import networkx as nx
from itertools import chain
from fragment_factory import FragmentFactory
from activity_key import ActivityKey
from move import Move
from util import get_id_from_activity_label, delete_nodes_and_correct_flows, get_node_from_id, get_flow
from transformations.add_fragment import AddFragment
from transformations.remove_fragment import RemoveFragment



class SwapFragments(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, fragment_one_start: str, fragment_one_end: str, fragment_two_start: str, fragment_two_end: str, activity_key: ActivityKey = ActivityKey.NAME):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.fragment_one_start = fragment_one_start
        self.fragment_one_end = fragment_one_end
        self.fragment_two_start = fragment_two_start
        self.fragment_two_end = fragment_two_end

    def check(self):
        pass
    
    def apply(self):
        graph = self.bpmn_process.get_graph()
        # get fragment predecessors as reference position for add
        fragment_one_start_id = get_id_from_activity_label(self.bpmn_process, self.fragment_one_start) if self.activity_key == ActivityKey.NAME else self.fragment_one_start
        fragment_one_start_predecessor = next(graph.predecessors(fragment_one_start_id))
        fragment_two_start_id = get_id_from_activity_label(self.bpmn_process, self.fragment_two_start) if self.activity_key == ActivityKey.NAME else self.fragment_two_start
        fragment_two_start_predecessor = next(graph.predecessors(fragment_two_start_id))
        # pop the fragments
        remove_fragment_one_transformator = RemoveFragment(self.bpmn_process, self.fragment_one_start, self.fragment_one_end,pop_fragment=True, activity_key=self.activity_key)
        remove_fragment_one_transformator.check()
        extracted_fragment_one = FragmentFactory.create_fragment(remove_fragment_one_transformator.apply())
        remove_fragment_two_transformator = RemoveFragment(self.bpmn_process, self.fragment_two_start, self.fragment_two_end,pop_fragment=True, activity_key=self.activity_key)
        remove_fragment_two_transformator.check()
        extracted_fragment_two = FragmentFactory.create_fragment(remove_fragment_two_transformator.apply())
        # add the extracted_fragment_one after the fragment_two_start_predecessor
        add_fragment_one_transformator = AddFragment(self.bpmn_process, fragment_two_start_predecessor.get_id(), extracted_fragment_one, Move.SerialMove, activity_key=ActivityKey.ID)
        add_fragment_one_transformator.check()
        add_fragment_one_transformator.apply()
        # add the extracted_fragment_two after the fragment_one_start_predecessor
        add_fragment_two_transformator = AddFragment(self.bpmn_process, fragment_one_start_predecessor.get_id(), extracted_fragment_two, Move.SerialMove, activity_key=ActivityKey.ID)
        add_fragment_two_transformator.check()
        add_fragment_two_transformator.apply()
