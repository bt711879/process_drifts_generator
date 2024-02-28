from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
import pm4py
import networkx as nx
from itertools import chain
from enum import Enum, auto
import uuid
from src.fragment_factory import FragmentFactory
from src.move import Move
from src.activity_key import ActivityKey
from src.util import get_id_from_activity_label, delete_nodes_and_correct_flows, get_node_from_id, get_flow, get_start_events, get_end_events, count_gateways

class EmbedType(Enum):
    Conditional = auto()
    Loop = auto()


class EmbedFragment(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, fragment_start: str, fragment_end: str, embed_type: EmbedType = EmbedType.Loop, activity_key: ActivityKey = ActivityKey.ID):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.fragment_start = fragment_start
        self.fragment_end = fragment_end
        self.embed_type = embed_type

    def check(self):
        fragment_nodes_list = list(
            get_node_from_id(bpmn=self.bpmn_process, id=element) for path in nx.all_simple_paths(self.bpmn_process.get_graph(), source=self.fragment_start, target=self.fragment_end) for element in
            path)
        if count_gateways(fragment_nodes_list) % 2 == 1:
            raise ValueError(f"There is a even number of gateway in the fragment")
        else:
            print("Gateway check passed.")
        if(isinstance(get_node_from_id(bpmn=self.bpmn_process, id=self.fragment_end), BPMN.EndEvent)):
            raise ValueError(f"The node with ID {self.fragment_start} is a BPMN.EndEvent, which is not allowed.")
        else:
            print("Node check passed.")

    def apply(self):
        bpmn_graph = self.bpmn_process.get_graph()
        bpmn_start_events = get_start_events(self.bpmn_process)
        bpmn_end_events = get_end_events(self.bpmn_process)
        fragment_start_node = get_node_from_id(bpmn=self.bpmn_process, id=self.fragment_start)
        fragment_end_node = get_node_from_id(bpmn=self.bpmn_process, id=self.fragment_end)
        fragment_start_predecessors = list(bpmn_graph.predecessors(fragment_start_node))
        fragment_end_successors = list(bpmn_graph.successors(fragment_end_node))
        # create conditional JOIN gateway
        cov_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
        conditional_conv_gateway = BPMN.ExclusiveGateway(id=cov_gateway_id, gateway_direction= BPMN.Gateway.Direction.CONVERGING)
        # create condtional SPLIT gateway
        div_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
        conditional_div_gateway = BPMN.ExclusiveGateway(id=div_gateway_id, gateway_direction= BPMN.Gateway.Direction.DIVERGING)
        # cut connections from fragment
        # remove flows from fragment_start_predecessors to fragment_start:
        for predecessor in fragment_start_predecessors:
            print("remove flow from predecessor:", predecessor)
            flow = get_flow(self.bpmn_process, predecessor, fragment_start_node)
            self.bpmn_process.remove_flow(flow)
        # remove flows from fragment_end to fragment_end_successors:
        for succesor in fragment_end_successors:
            print("remove flow to successor:", succesor)
            flow = get_flow(self.bpmn_process, fragment_end_node, succesor)
            self.bpmn_process.remove_flow(flow)
        
        if self.embed_type == EmbedType.Loop:
            # set flow from fragment_end to condition_div_gateway
            new_seq_flow = BPMN.SequenceFlow(source=fragment_end_node, target=conditional_div_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
            # set flow from conditional_div_gateway to fragment_end successors
            for successor in fragment_end_successors:
                new_seq_flow = BPMN.SequenceFlow(source=conditional_div_gateway, target=successor)
                print('add flow from ',conditional_div_gateway.get_id(), 'to ', successor.get_id())
                self.bpmn_process.add_flow(new_seq_flow)
            # set flow from conditional_conv_gateway to fragment_start
            new_seq_flow = BPMN.SequenceFlow(source=conditional_conv_gateway, target=fragment_start_node)
            self.bpmn_process.add_flow(new_seq_flow)
            # set flow from fragment_start predecessors to conditional_conv_gateway
            for predecessor in fragment_start_predecessors:
                new_seq_flow = BPMN.SequenceFlow(source=predecessor, target=conditional_conv_gateway)
                self.bpmn_process.add_flow(new_seq_flow)    
            # set from from conditional_div_gateway to conditional_conv_gateway:
            new_seq_flow = BPMN.SequenceFlow(source=conditional_div_gateway, target=conditional_conv_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
        else:
            # set flow from fragment_end to condition_conv_gateway
            new_seq_flow = BPMN.SequenceFlow(source=fragment_end_node, target=conditional_conv_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
            # set flow from conditional_conv_gateway to fragment_end successors
            for successor in fragment_end_successors:
                new_seq_flow = BPMN.SequenceFlow(source=conditional_conv_gateway, target=successor)
                self.bpmn_process.add_flow(new_seq_flow)
            # set flow from conditional_div_gateway to fragment_start
            new_seq_flow = BPMN.SequenceFlow(source=conditional_div_gateway, target=fragment_start_node)
            self.bpmn_process.add_flow(new_seq_flow)
            # set flow from fragment_start predecessors to conditional_div_gateway
            for predecessor in fragment_start_predecessors:
                new_seq_flow = BPMN.SequenceFlow(source=predecessor, target=conditional_div_gateway)
                self.bpmn_process.add_flow(new_seq_flow)    
            # set from from conditional_div_gateway to conditional_conv_gateway:
            new_seq_flow = BPMN.SequenceFlow(source=conditional_div_gateway, target=conditional_conv_gateway)
            self.bpmn_process.add_flow(new_seq_flow) 
        