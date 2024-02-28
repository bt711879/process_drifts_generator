from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
from src.move import Move
from src.transformations.remove_fragment import RemoveFragment
from src.transformations.add_fragment import AddFragment
from src.fragment_factory import FragmentFactory
import src.util as util
from src.activity_key import ActivityKey
import uuid
import networkx as nx
import pm4py


class MoveFragment(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, activity_before: str, activity_after: str= None, sequence_flow: str =  None, fragment_start: str= None, fragment_end: str=None, move: Move=Move.SerialMove, activity_key: ActivityKey = ActivityKey.ID):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.activity_label = activity_before
        self.activity_after = activity_after
        self.sequence_flow = sequence_flow
        self.fragment_start = fragment_start
        self.fragment_end = fragment_end
        self.move = move


    def check(self):
        activity_node = util.get_node_from_id(self.bpmn_process, self.activity_label)
        fragment_nodes_list = list(
            util.get_node_from_id(self.bpmn_process, element) for path in nx.all_simple_paths(self.bpmn_process.get_graph(), source=self.fragment_start, target=self.fragment_end) for element in
        path)
        between_activities_list = list(
            util.get_node_from_id(self.bpmn_process, element) for path in nx.all_simple_paths(self.bpmn_process.get_graph(), source=self.activity_label, target=self.activity_after) for element in
        path)
        if (util.count_gateways(fragment_nodes_list) % 2 == 1):
            raise ValueError(f"Not all branches in fragment are closed {fragment_nodes_list}")
        #if (util.count_gateways(between_activities_list) % 2 == 1):
        #    raise ValueError(f"Not all branches in fragment are closed {between_activities_list}")
        if(activity_node in fragment_nodes_list):
            raise ValueError(f"The activity overlaps with the fragment")
        for node in fragment_nodes_list:
            if isinstance(node, BPMN.StartEvent | BPMN.EndEvent):
                raise ValueError(f"Start and end events can not be moved")
        

    def apply(self):
        remove_fragment_transformator = RemoveFragment(self.bpmn_process, self.fragment_start, self.fragment_end, True, self.activity_key)
        remove_fragment_transformator.check()
        extracted_fragment = FragmentFactory.create_fragment(remove_fragment_transformator.apply())
        add_fragment_transformator = AddFragment(bpmn_process=self.bpmn_process, activity_before=self.activity_label, activity_after=self.activity_after, sequence_flow=self.sequence_flow, fragment=extracted_fragment, move=self.move, activity_key=self.activity_key)
        add_fragment_transformator.check()
        add_fragment_transformator.apply()