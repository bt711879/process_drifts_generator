from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
from src.move import Move
from src.transformations.remove_fragment import RemoveFragment
from src.transformations.add_fragment import AddFragment
from src.transformations.move_fragment import MoveFragment
from src.fragment_factory import FragmentFactory
import src.util as util
from src.activity_key import ActivityKey
import uuid
import networkx as nx
import pm4py


class ParellelizeFragment(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, fragment_start: str, fragment_end: str, activity_key: ActivityKey = ActivityKey.ID):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.fragment_start = fragment_start
        self.fragment_end = fragment_end


    def check(self):
        # check if element only contain tasks
        fragment_nodes_list = list(
            util.get_node_from_id(self.bpmn_process, element) for path in nx.all_simple_paths(self.bpmn_process.get_graph(), source=self.fragment_start, target=self.fragment_end) for element in
            path)
        if not util.check_all_tasks(fragment_nodes_list):
             raise ValueError("Not all elements in the fragment are BPMN.Tasks")
        # check if no element has more than one successor
        for node in fragment_nodes_list:
            if not len(list(self.bpmn_process.get_graph().successors(node)))==1:
                raise ValueError("Not all elements in sequence")
        print("Sequence check passed.")


    def apply(self):
        bpmn_process_graph = self.bpmn_process.get_graph()
        fragment_start_node = util.get_node_from_id(self.bpmn_process, self.fragment_start)
        fragment_end_node = util.get_node_from_id(self.bpmn_process, self.fragment_end)
        fragment_start_predecessors = list(bpmn_process_graph.predecessors(fragment_start_node))
        fragment_end_successors = list(bpmn_process_graph.successors(fragment_end_node))
        # create diverging and converging parallel gateways
        cov_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
        div_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
        parallel_conv_gateway = BPMN.ParallelGateway(id=cov_gateway_id, gateway_direction= BPMN.Gateway.Direction.CONVERGING)
        parallel_div_gateway = BPMN.ParallelGateway(id=div_gateway_id, gateway_direction= BPMN.Gateway.Direction.DIVERGING)
        # connect fragment_start_predecessor to parallel_div_gateway
        for predecessor in fragment_start_predecessors:
            new_seq_flow = BPMN.SequenceFlow(source=predecessor, target=parallel_div_gateway)
            self.bpmn_process.add_flow(new_seq_flow)

        # remove flow from fragment_start_predecessor to fragment_start
        for predecessor in fragment_start_predecessors:
            flow = util.get_flow(self.bpmn_process, predecessor, fragment_start_node)
            self.bpmn_process.remove_flow(flow)
        # add flow from parallel_div_gateway to each element on fragment 
        fragment_nodes_list = list(
            element for path in nx.all_simple_paths(bpmn_process_graph, source=fragment_start_node.get_id(), target=fragment_end_node.get_id()) for element in
            path)
        for node_id in fragment_nodes_list:
            node = util.get_node_from_id(self.bpmn_process, node_id)
            new_seq_flow = BPMN.SequenceFlow(source=parallel_div_gateway, target=node)
            self.bpmn_process.add_flow(new_seq_flow)
        # add flow from each element on fragment to parallel_conv_gateway
        for node_id in fragment_nodes_list:
            node = util.get_node_from_id(self.bpmn_process, node_id)
            new_seq_flow = BPMN.SequenceFlow(source=node, target=parallel_conv_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
        # add flow from parallel_conv_gateway to fragment_end_successor
        for successor in fragment_end_successors:
            new_seq_flow = BPMN.SequenceFlow(source=parallel_conv_gateway, target=successor)
            self.bpmn_process.add_flow(new_seq_flow)
        # remove from from fragment_end to fragment_end to fragment_end_successors
        for successor in fragment_end_successors:
            flow = util.get_flow(self.bpmn_process, fragment_end_node, successor)
            self.bpmn_process.remove_flow(flow)
        # remove flow from activity in fragment to it's successor
        for i in range(len(fragment_nodes_list) -1):
            node = util.get_node_from_id(self.bpmn_process, fragment_nodes_list[i])
            node_successor = util.get_node_from_id(self.bpmn_process, fragment_nodes_list[i+1])
            flow = util.get_flow(self.bpmn_process, node, node_successor)
            self.bpmn_process.remove_flow(flow)
 
            