from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
import pm4py
import networkx as nx
from itertools import chain
from fragment_factory import FragmentFactory
from util import get_id_from_activity_label, delete_nodes_and_correct_flows, get_node_from_id, get_flow

class RemoveFragment(BpmnTransformation):
    def __init__(self, bpmn_process : BPMN, fragment_start : str, fragment_end : str):
        super().__init__(bpmn_process)
        self.fragment_start = fragment_start
        self.fragment_end = fragment_end

    def apply(self):
        graph = self.bpmn_process.get_graph()
        start_node_id = get_id_from_activity_label(self.bpmn_process, self.fragment_start)
        start_node_predecessor = next(graph.predecessors(start_node_id))
        end_node_id = get_id_from_activity_label(self.bpmn_process, self.fragment_end)
        end_node_id_successors = next(graph.successors(end_node_id))
        nodes_to_remove = list(element for path in nx.all_simple_paths(graph, source=start_node_id, target=end_node_id) for element in path)
        before_pred_seq_flow = get_flow(self.bpmn_process, start_node_predecessor, get_node_from_id(self.bpmn_process, get_id_from_activity_label(self.bpmn_process, self.fragment_start)))
        new_seq_flow = BPMN.SequenceFlow(start_node_predecessor, end_node_id_successors, before_pred_seq_flow.get_id(), before_pred_seq_flow.get_name(), before_pred_seq_flow.get_process)
        self.bpmn_process.add_flow(new_seq_flow)
        #remove necessary flows and nodes
        delete_nodes_and_correct_flows(self.bpmn_process, nodes_to_remove, start_node_predecessor, end_node_id_successors)


    