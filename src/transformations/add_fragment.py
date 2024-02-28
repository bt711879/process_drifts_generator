import sys
import os

# Adding 'C:\\GitRepositories\\process_drifts_generator\\src' to the system path
src_path = 'C:\\GitRepositories\\process_drifts_generator\\src'
sys.path.insert(0, src_path)
from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
from src.move import Move
from src.activity_key import ActivityKey
import src.util as util
import uuid
import networkx as nx
import pm4py



class AddFragment(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, activity_before: str, activity_after: str = None, sequence_flow: str =  None, fragment: BPMN = None,  move: Move = Move.SerialMove, activity_key: ActivityKey = ActivityKey.ID):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.activity_before = activity_before
        self.activity_after = activity_after
        self.sequence_flow = sequence_flow
        self.fragment = fragment
        self.move = move

    def check(self):
        activity_before_node = util.get_node_from_id(self.bpmn_process, self.activity_before)
        activity_after_node = util.get_node_from_id(self.bpmn_process, self.activity_after)
        fragment_nodes_set = set()
        fragment_nodes_list = [
            util.get_node_from_id(self.bpmn_process, element)
            for path in nx.all_simple_paths(self.bpmn_process.get_graph(), source=self.activity_before, target=self.activity_after)
            for element in path
            if element not in {self.activity_before, self.activity_after} and element not in fragment_nodes_set and not fragment_nodes_set.add(element)
        ]
        activity_before_successors = list(self.bpmn_process.get_graph().successors(activity_before_node))
        activity_after_successors = list(self.bpmn_process.get_graph().successors(activity_after_node))
        edges_start_acitvity_before  = util.get_edges_from_start_to_node_simple(self.bpmn_process, self.activity_before)
        for successor in activity_after_successors:
                if util.get_flow(self.bpmn_process, self.activity_after, successor).get_id() in edges_start_acitvity_before:
                    raise ValueError(f"Split gateway is trying to get to a already visited flow.")
                else:
                    print("Direction test passed.")
        if (not activity_before_node) | (not activity_after_node):
            raise ValueError(f"Couldn't find a valid node to the activity")
        else:
            print(f"valid node check passed")
        if (util.count_gateways(fragment_nodes_list) % 2 == 1):
            raise ValueError(f"Not all branches between activity before and activity after are closed {fragment_nodes_list}")
        if self.move == Move.SerialMove and activity_after_node not in activity_before_successors:
            raise ValueError(f"Not sequential")
        else:
            print("end event check passed")
        #if util.appears_before(self.bpmn_process.get_graph(), activity_before_node, activity_after_node):
            

 
    def apply(self):
        # get the graph element for bpmn process to change
        bpmn_process_graph = self.bpmn_process.get_graph()
        fragment_graph = self.fragment.get_graph()
        print("the fragment graph", fragment_graph.edges(data=True))
        # get the node to the activity_label
        activity_node = util.get_node_from_id(self.bpmn_process, self.activity_before)
        activity_node_after = util.get_node_from_id(self.bpmn_process, self.activity_after)
        # get the activity successor
        activity_successor = util.get_target_node_id(self.bpmn_process, self.sequence_flow) if self.sequence_flow else next(bpmn_process_graph.successors(activity_node))
        print("activity successor", activity_successor)
        # get the activity_after predecessor
        if self.sequence_flow:
            if activity_successor == self.activity_after:
                activity_after_predecessor = activity_successor
            elif activity_successor != self.activity_after: 
                activity_after_predecessor = list(nx.all_simple_paths(bpmn_process_graph, util.get_target_node_id(self.bpmn_process, self.sequence_flow), activity_node_after))[-1][-2]

        else: activity_after_predecessor = next(bpmn_process_graph.predecessors(activity_node_after))
        # get start and end event lists for fragment to add
        start_events = util.get_start_events(self.fragment)
        end_events = util.get_end_events(self.fragment)

        
        # get a list with successor activities to start_events
        start_events_successors = []
        for start_event in start_events:
            # Get successor
            print("check start event", start_event)
            successor = next(fragment_graph.successors(start_event))
            print("successor")
            start_events_successors.append(successor)
            print(start_events_successors)

        
        
        # get a list with predecessors activities to end_events
        end_events_predecessors = []
        for end_event in end_events:
            # Get predecessor
            print("check end event", end_event)
            predecessor = next(fragment_graph.predecessors(end_event))
            print("predecessor")
            end_events_predecessors.append(predecessor)
            print(end_events_predecessors)
        print("The value of self.move:", self.move)
        if self.move is Move.SerialMove:
            # add a flow from activity label to each start_event successor 
            for event in start_events_successors:
                new_seq_flow = BPMN.SequenceFlow(source=activity_node, target=event)
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from each end_envent predecessor to activity_after 
            for event in end_events_predecessors:
                new_seq_flow = BPMN.SequenceFlow(source=event, target=activity_node_after)
                self.bpmn_process.add_flow(new_seq_flow)
            # remove the flow from activity to activity successor
                seq_flow =  util.get_flow(self.bpmn_process, activity_node, activity_node_after)
                self.bpmn_process.remove_flow(seq_flow)
            
            # add all intern flows from fragments to bpmn_process
            fragment_flows = self.fragment.get_flows()
            bpmn_process_flows = self.bpmn_process.get_flows()
            print("fragment flows", fragment_flows)
            for flow in fragment_flows:
                if (not isinstance(flow.get_source(), BPMN.StartEvent)) and \
                (not isinstance(flow.get_target(), BPMN.EndEvent)) and \
                (flow not in bpmn_process_flows):
                    self.bpmn_process.add_flow(flow)
        elif self.move == Move.ParallelMove:
            parallel_gateway_target = activity_node_after
            # create new parallel gateways
            cov_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
            div_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
            parallel_conv_gateway = BPMN.ParallelGateway(id=cov_gateway_id, gateway_direction= BPMN.Gateway.Direction.CONVERGING)
            parallel_div_gateway = BPMN.ParallelGateway(id=div_gateway_id, gateway_direction= BPMN.Gateway.Direction.DIVERGING)
            # add flow from activity to new gateway
            new_seq_flow = BPMN.SequenceFlow(source=activity_node, target=parallel_div_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
            # add flow from new gateway to activity successor
            if activity_successor != self.activity_after:
                new_seq_flow = BPMN.SequenceFlow(source=parallel_div_gateway, target=activity_successor)
                self.bpmn_process.add_flow(new_seq_flow)
            else:
                new_seq_flow = BPMN.SequenceFlow(source=parallel_div_gateway, target=parallel_conv_gateway) # cover the case that flow with no activity
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from new gateway to each start event successor
            for event in start_events_successors:
                new_seq_flow = BPMN.SequenceFlow(source=parallel_div_gateway, target=event)
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from each end_envent predecessor to new join gateway
            for event in end_events_predecessors:
                new_seq_flow = BPMN.SequenceFlow(source=event, target=parallel_conv_gateway)
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from join gateway to parallel gateway target
            new_seq_flow = BPMN.SequenceFlow(source=parallel_conv_gateway, target=parallel_gateway_target)
            self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from activity_after predecessor to join gateway
            if activity_successor != self.activity_after:
                new_seq_flow = BPMN.SequenceFlow(source= activity_after_predecessor, target=parallel_conv_gateway)
                self.bpmn_process.add_flow(new_seq_flow)

            # remove the flow from activity to activity successor
                # Check if activity_node or activity_successor is None before proceeding
            if activity_node is None or activity_successor is None:
                raise ValueError(f"{activity_node} and {activity_successor} must not be None")
            seq_flow =  util.get_flow(self.bpmn_process, activity_node, activity_successor)
            self.bpmn_process.remove_flow(seq_flow)

            # remove the flow from activity_after predecessor to activity_after
            if activity_after_predecessor != activity_node_after:
                seq_flow =  util.get_flow(self.bpmn_process, activity_after_predecessor, activity_node_after)
                try:
                    self.bpmn_process.remove_flow(seq_flow)
                except AttributeError as e:
                    print(f"No flow could be found from {activity_after_predecessor} to {activity_node_after}: {e}")

            # add all intern flows from fragments to bpmn_process
            fragment_flows = self.fragment.get_flows()
            bpmn_process_flows = self.bpmn_process.get_flows()
            print("fragment flows", fragment_flows)
            for flow in fragment_flows:
                if (not isinstance(flow.get_source(), BPMN.StartEvent)) and \
                (not isinstance(flow.get_target(), BPMN.EndEvent)) and \
                (flow not in bpmn_process_flows):
                    self.bpmn_process.add_flow(flow)

            
        elif self.move == Move.ConditionalMove:
            conditional_gateway_target = activity_node_after
            # create new conditional gateways
            cov_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
            div_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
            cond_conv_gateway = BPMN.ExclusiveGateway(id=cov_gateway_id, gateway_direction= BPMN.Gateway.Direction.CONVERGING)
            cond_div_gateway = BPMN.ExclusiveGateway(id=div_gateway_id, gateway_direction= BPMN.Gateway.Direction.DIVERGING)
            # add flow from activity to new gateway
            new_seq_flow = BPMN.SequenceFlow(source=activity_node, target=cond_div_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
            # add flow from new gateway to activity successor   #change here
            if activity_successor != self.activity_after:
                new_seq_flow = BPMN.SequenceFlow(source=cond_div_gateway, target=activity_successor)
                self.bpmn_process.add_flow(new_seq_flow)
            else: 
                new_seq_flow = BPMN.SequenceFlow(source=cond_div_gateway, target=cond_conv_gateway) # cover the case that flow with no activity
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from new gateway to each start event successor
            for event in start_events_successors:
                new_seq_flow = BPMN.SequenceFlow(source=cond_div_gateway, target=event)
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from each end_envent predecessor to new join gateway 
            for event in end_events_predecessors:
                new_seq_flow = BPMN.SequenceFlow(source=event, target=cond_conv_gateway)
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from join gateway to conditional gateway target
            new_seq_flow = BPMN.SequenceFlow(source=cond_conv_gateway, target=conditional_gateway_target)
            self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from activity_after predecessor to join gateway
            if activity_successor != self.activity_after:
                new_seq_flow = BPMN.SequenceFlow(source= activity_after_predecessor, target=cond_conv_gateway)
                self.bpmn_process.add_flow(new_seq_flow)
            # remove the flow from activity to activity successor
            seq_flow =  util.get_flow(self.bpmn_process, activity_node, activity_successor)
            self.bpmn_process.remove_flow(seq_flow)
            # remove the flow from activity_after predecessor to activity_after
            if activity_after_predecessor != activity_node_after:
                seq_flow =  util.get_flow(self.bpmn_process, activity_after_predecessor, activity_node_after)
                self.bpmn_process.remove_flow(seq_flow)
            # add all intern flows from fragments to bpmn_process
            fragment_flows = self.fragment.get_flows()
            bpmn_process_flows = self.bpmn_process.get_flows()
            print("fragment flows", fragment_flows)
            for flow in fragment_flows:
                if (not isinstance(flow.get_source(), BPMN.StartEvent)) and \
                (not isinstance(flow.get_target(), BPMN.EndEvent)) and \
                (flow not in bpmn_process_flows):
                    self.bpmn_process.add_flow(flow)
        else:
            # Raise an exception for an unsupported move
            raise ValueError(f"Unsupported move type: {self.move}")
