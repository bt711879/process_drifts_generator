from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
from fragment_factory import FragmentFactory
from pm4py.objects.process_tree.obj import ProcessTree
from util import get_leaf, convert_bpmn_to_process_tree
import pm4py

class AddFragment(BpmnTransformation):
    def __init__(self, bpmn_process : BPMN, activity_label : str, fragment):
        super().__init__(bpmn_process)
        self.activity_label = activity_label
        self.fragment = fragment

    def apply(self):
        bpmn_tree = convert_bpmn_to_process_tree(self.bpmn_process)
        leaf = get_leaf(bpmn_tree, self.activity_label)
        print("leaf label: ", leaf._get_label())
        parent = leaf._get_parent()
        children_list = parent.children
        fragment_tree = FragmentFactory.createFragment(self.fragment)
        children_list.append(fragment_tree)
        fragment_tree._set_parent(parent)
        parent._set_children(children_list)
        self.bpmn_process = pm4py.convert_to_bpmn(bpmn_tree)
        #pm4py.view_bpmn(self.bpmn_process)
        
