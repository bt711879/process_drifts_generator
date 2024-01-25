from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
import pm4py
import networkx as nx
from itertools import chain
from src.fragment_factory import FragmentFactory
from src.activity_key import ActivityKey
from src.util import get_id_from_activity_label, delete_nodes_and_correct_flows, get_node_from_id, get_flow, count_gateways


class RemoveFragment(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, fragment_start: str, fragment_end: str, pop_fragment: bool, activity_key: ActivityKey = ActivityKey.ID):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.fragment_start = fragment_start
        self.fragment_end = fragment_end
        self.pop_fragment = pop_fragment

    def check(self):
        node = get_node_from_id(self.bpmn_process, self.fragment_start)
        fragment_nodes_list = list(
            get_node_from_id(self.bpmn_process, element) for path in nx.all_simple_paths(self.bpmn_process.get_graph(), source=self.fragment_start, target=self.fragment_end) for element in
            path)
        if isinstance(node, (BPMN.StartEvent, BPMN.EndEvent)):
            raise ValueError(f"The node with ID {self.fragment_start} is a BPMN.StartEvent or BPMN.EndEvent, which is not allowed.")
        else:
            print("Node check passed.")

        if count_gateways(fragment_nodes_list) % 2 == 1:
            raise ValueError(f"There is a even number of gateway in the fragment")
        else:
            print("Gateway check passed.")

    def apply(self):
        graph = self.bpmn_process.get_graph()
        start_node_id = get_id_from_activity_label(self.bpmn_process, self.fragment_start) if self.activity_key == ActivityKey.NAME else self.fragment_start
        print("delete from start node", start_node_id)
        start_node_predecessor = next(graph.predecessors(start_node_id))
        end_node_id = get_id_from_activity_label(self.bpmn_process, self.fragment_end) if self.activity_key == ActivityKey.NAME else self.fragment_end
        print("delete to end node", end_node_id)
        end_node_id_successors = next(graph.successors(end_node_id))
        nodes_to_remove = list(
            element for path in nx.all_simple_paths(graph, source=start_node_id, target=end_node_id) for element in
            path)
        if (self.activity_key==ActivityKey.NAME):
            before_pred_seq_flow = get_flow(self.bpmn_process, start_node_predecessor, get_node_from_id(self.bpmn_process,
                                                                                                        get_id_from_activity_label(
                                                                                                            self.bpmn_process,
                                                                                                            self.fragment_start)))
        else:
            before_pred_seq_flow = get_flow(self.bpmn_process, start_node_predecessor, get_node_from_id(self.bpmn_process,
                                                                                                        self.fragment_start))
        new_seq_flow = BPMN.SequenceFlow(start_node_predecessor, end_node_id_successors, before_pred_seq_flow.get_id(),
                                         before_pred_seq_flow.get_name(), before_pred_seq_flow.get_process)
        self.bpmn_process.add_flow(new_seq_flow)
        # remove necessary flows and nodes
        removed_flows = []
        delete_nodes_and_correct_flows(self.bpmn_process, nodes_to_remove, start_node_predecessor,
                                       end_node_id_successors, removed_flow=removed_flows)
        if(self.pop_fragment):
            return removed_flows