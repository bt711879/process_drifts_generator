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
    def __init__(self, bpmn_process: BPMN, activity_label: str, fragment_start: str, fragment_end: str, move: Move, after_gateway: bool, activity_key: ActivityKey = ActivityKey.ID):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.activity_label = activity_label
        self.fragment_start = fragment_start
        self.fragment_end = fragment_end
        self.move = move
        self.after_gateway = after_gateway

    def check(self):
        pass

    def apply(self):
        remove_fragment_transformator = RemoveFragment(self.bpmn_process, self.fragment_start, self.fragment_end, True, self.activity_key)
        remove_fragment_transformator.check()
        extracted_fragment = FragmentFactory.create_fragment(remove_fragment_transformator.apply())
        add_fragment_transformator = AddFragment(bpmn_process=self.bpmn_process, activity_label=self.activity_label, fragment=extracted_fragment, move=self.move, after_gateway=self.after_gateway, activity_key=self.activity_key)
        add_fragment_transformator.check()
        add_fragment_transformator.apply()