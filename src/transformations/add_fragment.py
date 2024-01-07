from .bpmn_transformation import BpmnTransformation
from pm4py.objects.bpmn.obj import BPMN
from src.move import Move
import src.util as util
import networkx as nx
import pm4py


class AddFragment(BpmnTransformation):
    def __init__(self, bpmn_process: BPMN, activity_label: str, fragment, move: Move):
        super().__init__(bpmn_process)
        self.activity_label = activity_label
        self.fragment = fragment
        self.move = move

    def apply(self):
        # get the graph element for bpmn process to change
        bpmn_process_graph = self.bpmn_process.get_graph()
        fragment_graph = self.fragment.get_graph()
        print("the fragment graph", fragment_graph)
        # get the node to the activity_label
        activity_node = util.get_node_from_activity_label(self.bpmn_process, self.activity_label)
        # get start and end event lists for fragment to add
        start_events = util.get_start_events(self.fragment)
        end_events = util.get_end_events(self.fragment)

        '''
        # get a list with successor activities to start_events
        start_events_successors = []
        for start_event in start_events:
            # Get successor
            print("check start event", start_event)
            successor = next(fragment_graph.successors(start_event.get_id()))
            print("successor")
            start_events_successors.append(successor)
            print(start_events_successors)

        
       
        # get a list with predecessors activities to end_events
        end_events_predecessors = []
        for end_event in end_events:
            end_events_predecessors.append((graph.predecessors(end_event.get_id())))
        # add all the nodes between start_event successors and end_event predecessors from fragment to bpmn_graph
        paths = []
        for event_source in start_events_successors:
            for event_target in end_events_predecessors:
                paths.append(nx.all_simple_paths(graph, source=event_source, target=event_target))

        print(paths)
        # add a flow from each start_event successor to activity_label
        for event in start_events_successors:
            new_seq_flow = BPMN.SequenceFlow(source=activity_node, target=event)
            self.bpmn_process.add_flow(new_seq_flow)
        '''
        #
        if self.move == Move.SerialMove:
            # Handle serialMove
            pass
        elif self.move == Move.ParallelMove:
            # Handle serialMove
            pass
        elif self.move == Move.ConditionalMove:
            # Handle serialMove
            pass
        else:
            # Raise an exception for an unsupported move
            raise ValueError(f"Unsupported move type: {self.move}")
