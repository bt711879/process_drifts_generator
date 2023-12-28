from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from pm4py.objects.petri_net.importer import importer as pnml_importer
from fragment_factory import FragmentFactory
import networkx as nx
import pm4py

########## process trees ###############################

def get_leaf(tree : ProcessTree, activity : str):
    leaves = tree._get_leaves()
    if any(leaf._get_label() == activity for leaf in leaves):
        for leaf in leaves:
            label = leaf._get_label()
            if label == activity:
                return leaf
    else:
        # Handle the case where the task does not exist
        print(f"Error: Activity '{activity}' not found in the tree.")



def get_labels_between_activities(tree : ProcessTree, activity_one : str, activity_two : str):
    label_list = []
    found_activity_one = False
    tree_leaves = tree._get_leaves()
    #print("leaves", tree_leaves)
    for leaf in tree_leaves:
        label = leaf._get_label()

        if label == activity_one:
            found_activity_one = True
            label_list.append(label)
        
        if found_activity_one and label != activity_one and label != activity_two:
            label_list.append(label)

        if found_activity_one and label == activity_two:
            label_list.append(label)
            break
    return label_list

     


def get_position_in_children(children : list[ProcessTree], child : ProcessTree):
    position = 0
    for x in children:
        if x == child:
            break
        else:
            position = position + 1
    return position


def get_children_of_root(child : ProcessTree):
    parent = child._get_parent()
    return parent._get_children()


def break_down_tree_fully(tree : ProcessTree):
    operators_list = []
    all_tree_list_without_leaves = []
    tree_dict = {}
    #test the tree has no children
    if tree._get_children() == list():
        tree_dict[0] = tree
    else:
        j = 0
        operators_list.append(tree._get_operator())
        #initiate having the tree as first element
        all_tree_list_without_leaves.append(tree)
        tree_list = []
        children_tree = tree._get_children()
        for x in children_tree:
            #append each child of tree on tree list
            tree_list.append(x)
        for child in tree_list:
            #if child of child has no children
            if child._get_children() == list():
                tree_dict[j] = child._get_label()
                j = j + 1
            else:
                #if child of child still has children
                operators_list.append(child._get_operator())
                all_tree_list_without_leaves.append(child)
                for ch_child in child._get_children():
                    tree_list.append(ch_child)
    return operators_list, all_tree_list_without_leaves, tree_dict



def get_type_operator(operator : Operator):
    if operator == 'seq':
        return Operator.SEQUENCE
    elif operator == 'xor':
        return Operator.XOR
    elif operator == 'and':
        return Operator.PARALLEL
    elif operator == 'xor loop':
        return Operator.LOOP
    elif operator == 'or':
        return Operator.OR
    else:
        return None
    

def import_bpmn_to_process_tree(path : str):
    bpmn_graph = pm4py.read_bpmn(path)
    net, im, fm = bpmn_converter.apply(bpmn_graph)
    tree = wf_net_converter.apply(net, im, fm)
    return pm4py.utils.parse_process_tree(tree._get_label())

def convert_bpmn_to_process_tree(bpmn_graph : BPMN):
    net, im, fm = bpmn_converter.apply(bpmn_graph)
    tree = wf_net_converter.apply(net, im, fm)
    return pm4py.utils.parse_process_tree(tree._get_label())


def combine_three_trees(tree_parent : ProcessTree, tree_ch_one : ProcessTree, tree_ch_two : ProcessTree):
    tree_ch_one._set_parent(tree_parent)
    tree_ch_two._set_parent(tree_parent)
    tree_parent._set_children([tree_ch_one, tree_ch_two])


def get_sub_trees(tree: ProcessTree):
    result_dict = {}

    # Recursive helper function to build subtrees
    def build_sub_trees(current_tree, current_tuple):
        current_tree_leaves = current_tree._get_leaves()
        current_label = str(current_tree.label)
        current_tuple.append(current_label)

        # Add the current subtree to the result dictionary
        result_dict[tuple(current_tree_leaves)] = current_tree

        # Recursively explore the children of the current_tree
        for child in current_tree.children:
            child_tree = ProcessTree(child._get_operator(), None, child._get_children(), child._get_label())
            build_sub_trees(child_tree, current_tuple.copy())

    # Start building subtrees
    build_sub_trees(tree, [])

    return result_dict

################ BPMN ############################################
def get_node_from_id(bpmn : BPMN, id : str):
    nodes = bpmn.get_nodes()
    for node in nodes:
        if node.get_id() == id:
            return node


def get_id_from_activity_label(bpmn : BPMN, activity : str):
    nodes = bpmn.get_nodes()
    for node in nodes:
        if node.get_name() == activity:
            return node.get_id()
    return


def get_flow_element(bpmn : BPMN):
    flows = bpmn.get_flows()
    for f in flows:
        id, name, source, target, process, layout, waypoints = f.get_id(), f.get_name(), f.get_source(), f.get_target(), f.get_process(), f.get_layout(), f.get_waypoints()
        print("flow ", id)
        print("id", id, "name",name, "source", source, "target",target, "process",process, "layout",layout, "waypoints",waypoints)
        print("\n")
    



def get_bpmn_graph_elements(bpmn : BPMN):
    nodes_list = list(bpmn.get_nodes())
    print("Nodes:", bpmn.get_nodes())
    print("First node name:", nodes_list[0].get_name())
    print("Flows:", bpmn.get_flows())


def delete_nodes_and_correct_flows(bpmn : BPMN, nodes : list[BPMN.BPMNNode], start_node_id_predecessor, end_node_id_successor):
    u_flow = start_node_id_predecessor
    removed_flow = []
    nodes_to_remove = []
    #remove flows
    for node in nodes:
        current_node_id = node
        v_flow = get_node_from_id(bpmn, current_node_id)
        flow = get_flow(bpmn, u_flow, v_flow)
        if (flow not in removed_flow) and (flow in bpmn.get_flows()):
            bpmn.remove_flow(flow)
            removed_flow.append(flow)
            nodes_to_remove.append(node)
            print("successfully removed flow", flow)
        u_flow = get_node_from_id(bpmn, current_node_id)
    #last flow
    v_flow = end_node_id_successor
    flow = get_flow(bpmn, u_flow, v_flow)
    if (flow not in removed_flow) and (flow in bpmn.get_flows()):
        bpmn.remove_flow(flow)
    #remove nodes
    for node in nodes_to_remove:
        print("remove node: ", node)
        bpmn.remove_node(node)


def get_flow(bpmn : BPMN, source, target):
    print("I will get the flow for source: ", source, "and target: ", target)
    flows_list = bpmn.get_flows()
    for flow in flows_list:
       if (flow.get_source() == source) & (flow.get_target() == target):
            return flow