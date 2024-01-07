# core_transformator.py
from transformator import Transformator
from fragment_factory import FragmentFactory
from move import Move
import networkx as nx
import pm4py
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.bpmn.obj import BPMN
import util
from util import get_leaf, get_labels_between_activities, get_position_in_children



class CoreTransformator(Transformator):

    def __init__(self, random_transformation: bool = False):
        self.random_transformation = random_transformation

    def add_fragment(self, tree : ProcessTree, activity_label: str, fragment: ProcessTree, move_type: Move, changed_acs: bool = False):
        leaf = get_leaf(tree, activity_label)
        parent = leaf._get_parent()
        children_list = parent.children
        fragment_tree = FragmentFactory.create_fragment(fragment)
        children_list.append(fragment_tree)
        fragment_tree._set_parent(parent)
        parent._set_children(children_list)
        changed_acs.append(fragment_tree)
        # Optionally, you can call the common_method from the base class
        super().common_method()

    def remove_fragment(self, bpmn : BPMN, fragment_start : str, fragment_end : str, changed_acs: bool = False):
        graph = bpmn.get_graph()
        # Print basic information about the graph
        nodes = list(graph.nodes())
        edges = list(graph.edges())
        print("Nodes:", nodes)
        print("Edges:", edges)
        #previous_node = nodes[0].parent
        start_node_id = util.get_id_from_activity_label(bpmn, fragment_start)
        start_node_predecessor = next(graph.predecessors(start_node_id))
        end_node_id = util.get_id_from_activity_label(bpmn, fragment_end)
        end_node_id_successors = next(graph.successors(end_node_id))
        nodes_to_remove = list(nx.shortest_path(graph, source=start_node_id, target=end_node_id))
        print("shortest path from:", start_node_id, "to", end_node_id , "ist", nodes_to_remove)
        # Remove the nodes
        #graph.remove_nodes_from(nodes_to_remove)
        '''
        for node in nodes_to_remove:
            bpmn.remove_node(node)
        '''
        #add new flow
        before_pred_seq_flow = util.get_flow(bpmn, start_node_predecessor, util.get_node_from_id(bpmn, util.get_id_from_activity_label(bpmn, fragment_start)))
        new_seq_flow = BPMN.SequenceFlow(start_node_predecessor, end_node_id_successors, before_pred_seq_flow.get_id(), before_pred_seq_flow.get_name(), before_pred_seq_flow.get_process)
        bpmn.add_flow(new_seq_flow)
        #remove necessary flows and nodes
        util.delete_nodes_and_correct_flows(bpmn, nodes_to_remove, start_node_predecessor, end_node_id_successors)
        #graph.add_edge(start_node_predecessor_id, end_node_id_successors_id)
        print("predecessors:", start_node_predecessor)
        print("successors:", end_node_id_successors)
        bpmn_tree = pm4py.convert_to_process_tree(bpmn)
        #bpmn = pm4py.convert_to_bpmn(bpmn_tree)
        pm4py.view_bpmn(bpmn)

    def move_fragment(self, tree : ProcessTree, activity_label : str, fragment_start_label : str,  fragment_end_label : str, move_type : Move,  changed_acs : bool = False):
        '''
        implement
        '''
        

        '''
    def remove_fragment(self, tree : ProcessTree, fragment_start_label : str,  fragment_end_label : str, changed_acs : bool = False):
        #get all leaves between task_start and task_end in a list
        label_list = get_labels_between_activities(tree, fragment_start_label, fragment_end_label)
        leaves = tree._get_leaves()
        if any(leaf._get_label() == fragment_start_label for leaf in leaves):
            for leaf in leaves:
                label = leaf._get_label()
                if label in label_list:
                    print("label:", label)
                    parent = leaf._get_parent()
                    children_list = parent.children
                    empty_tree = ProcessTree(None, None, None, None)
                    empty_tree._set_parent(parent)
                    position = get_position_in_children(children_list, leaf)
                    children_list[position] = empty_tree
                    parent._set_children(children_list)
    '''