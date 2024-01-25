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
    def __init__(self, bpmn_process: BPMN, activity_label: str, fragment, move: Move, after_gateway: bool = False, activity_key: ActivityKey = ActivityKey.ID):
        super().__init__(bpmn_process)
        self.activity_key = activity_key
        self.activity_label = activity_label
        self.fragment = fragment
        self.move = move
        self.after_gateway = after_gateway

    def check(self):
        activity_node = util.get_node_from_id(self.bpmn_process, self.activity_label)
        if (not activity_node):
            raise ValueError(f"Couldn't find a valid node to the activity")
        else:
            print(f"valid node check passed")
        if (isinstance(activity_node, BPMN.EndEvent)):
            raise ValueError(f"It is not allowed to add a fragment after the end event")
        else:
            print("end event check passed")
        if (self.move==Move.ParallelMove):
            # check successor of activity_label are all task
           if(not util.check_all_tasks(list(self.bpmn_process.get_graph().successors(activity_node)))):
              raise ValueError(f"Not all successors of the activity are tasks")



    def apply(self):
        # get the graph element for bpmn process to change
        bpmn_process_graph = self.bpmn_process.get_graph()
        fragment_graph = self.fragment.get_graph()
        print("the fragment graph", fragment_graph.edges(data=True))
        # get the node to the activity_label
        activity_node = util.get_node_from_id(self.bpmn_process, self.activity_label)
        # get the activity successor
        activity_successor = next(bpmn_process_graph.successors(activity_node))
        print("activity successor", activity_successor)
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
            # add a flow from each end_envent predecessor to activity_label succesor 
            for event in end_events_predecessors:
                new_seq_flow = BPMN.SequenceFlow(source=event, target=activity_successor)
                self.bpmn_process.add_flow(new_seq_flow)
            # remove the flow from activity to activity successor
                seq_flow =  util.get_flow(self.bpmn_process, activity_node, activity_successor)
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
            parallel_gateway_target = next(bpmn_process_graph.successors(activity_successor))
            # create new parallel gateways
            cov_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
            div_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
            parallel_conv_gateway = BPMN.ParallelGateway(id=cov_gateway_id, gateway_direction= BPMN.Gateway.Direction.CONVERGING)
            parallel_div_gateway = BPMN.ParallelGateway(id=div_gateway_id, gateway_direction= BPMN.Gateway.Direction.DIVERGING)
            # add flow from activity to new gateway
            new_seq_flow = BPMN.SequenceFlow(source=activity_node, target=parallel_div_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
            # add flow from new gateway to activity successor
            new_seq_flow = BPMN.SequenceFlow(source=parallel_div_gateway, target=activity_successor)
            self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from activity successor to new join gateway
            new_seq_flow = BPMN.SequenceFlow(source=activity_successor, target=parallel_conv_gateway)
            self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from new gateway to each start event successor
            for event in start_events_successors:
                new_seq_flow = BPMN.SequenceFlow(source=parallel_div_gateway, target=event)
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from each end_envent predecessor to new join gateway 
            for event in end_events_predecessors:
                new_seq_flow = BPMN.SequenceFlow(source=event, target=parallel_conv_gateway)
                self.bpmn_process.add_flow(new_seq_flow)
            # add a flow from join gateway to parallel gateway target, predecessor of the activity predecessor
            new_seq_flow = BPMN.SequenceFlow(source=parallel_conv_gateway, target=parallel_gateway_target)
            self.bpmn_process.add_flow(new_seq_flow)
            # remove the flow from activity to activity successor
            seq_flow =  util.get_flow(self.bpmn_process, activity_node, activity_successor)
            self.bpmn_process.remove_flow(seq_flow)
            # remove the flow from activity successor to parallel_gateway_target
            seq_flow =  util.get_flow(self.bpmn_process, activity_successor, parallel_gateway_target)
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

            
        elif self.move == Move.ConditionalMove:
            join_gateway_target = next(bpmn_process_graph.successors(activity_successor))
            if(isinstance(activity_successor, BPMN.Task)):
                # create new conditional gateways
                cov_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
                div_gateway_id = 'gateway_' + str(uuid.uuid4())  # Generate a unique gateway ID
                conv_gateway = BPMN.ExclusiveGateway(id=cov_gateway_id, gateway_direction= BPMN.Gateway.Direction.CONVERGING)
                div_gateway = BPMN.ExclusiveGateway(id=div_gateway_id, gateway_direction= BPMN.Gateway.Direction.DIVERGING)
                # add flow from activity to new gateway
                new_seq_flow = BPMN.SequenceFlow(source=activity_node, target=div_gateway)
                self.bpmn_process.add_flow(new_seq_flow)
                # add flow from new gateway to activity successor
                new_seq_flow = BPMN.SequenceFlow(source=div_gateway, target=activity_successor)
                self.bpmn_process.add_flow(new_seq_flow)
                # add a flow from activity successor to new join gateway
                new_seq_flow = BPMN.SequenceFlow(source=activity_successor, target=conv_gateway)
                self.bpmn_process.add_flow(new_seq_flow)
                # add a flow from new gateway to each start event successor
                for event in start_events_successors:
                    new_seq_flow = BPMN.SequenceFlow(source=div_gateway, target=event)
                    self.bpmn_process.add_flow(new_seq_flow)
                # add a flow from each end_envent predecessor to new join gateway 
                for event in end_events_predecessors:
                    new_seq_flow = BPMN.SequenceFlow(source=event, target=conv_gateway)
                    self.bpmn_process.add_flow(new_seq_flow)
                # add a flow from join gateway to parallel gateway target, predecessor of the activity predecessor
                new_seq_flow = BPMN.SequenceFlow(source=conv_gateway, target=join_gateway_target)
                self.bpmn_process.add_flow(new_seq_flow)
                # remove the flow from activity to activity successor
                seq_flow =  util.get_flow(self.bpmn_process, activity_node, activity_successor)
                self.bpmn_process.remove_flow(seq_flow)
                # remove the flow from activity successor to parallel_gateway_target
                seq_flow =  util.get_flow(self.bpmn_process, activity_successor, join_gateway_target)
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
                raise TypeError(f"Move only supported between two tasks")
        else:
            # Raise an exception for an unsupported move
            raise ValueError(f"Unsupported move type: {self.move}")
