import sys

# Adding 'C:\\GitRepositories\\process_drifts_generator\\src' to the system path
sys.path.insert(0, 'C:\\GitRepositories\\process_drifts_generator\\src')
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from pm4py.objects.petri_net.importer import importer as pnml_importer
from src.fragment_factory import FragmentFactory
import networkx as nx
import pylab
import pm4py
from pm4py.util import constants
from graphviz import Digraph
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer

########## process trees ###############################

def get_leaf(tree: ProcessTree, activity: str):
    leaves = tree._get_leaves()
    if any(leaf._get_label() == activity for leaf in leaves):
        for leaf in leaves:
            label = leaf._get_label()
            if label == activity:
                return leaf
    else:
        # Handle the case where the task does not exist
        print(f"Error: Activity '{activity}' not found in the tree.")


def get_labels_between_activities(tree: ProcessTree, activity_one: str, activity_two: str):
    label_list = []
    found_activity_one = False
    tree_leaves = tree._get_leaves()
    # print("leaves", tree_leaves)
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


def get_position_in_children(children: list[ProcessTree], child: ProcessTree):
    position = 0
    for x in children:
        if x == child:
            break
        else:
            position = position + 1
    return position


def get_children_of_root(child: ProcessTree):
    parent = child._get_parent()
    return parent._get_children()


def break_down_tree_fully(tree: ProcessTree):
    operators_list = []
    all_tree_list_without_leaves = []
    tree_dict = {}
    # test the tree has no children
    if tree._get_children() == list():
        tree_dict[0] = tree
    else:
        j = 0
        operators_list.append(tree._get_operator())
        # initiate having the tree as first element
        all_tree_list_without_leaves.append(tree)
        tree_list = []
        children_tree = tree._get_children()
        for x in children_tree:
            # append each child of tree on tree list
            tree_list.append(x)
        for child in tree_list:
            # if child of child has no children
            if child._get_children() == list():
                tree_dict[j] = child._get_label()
                j = j + 1
            else:
                # if child of child still has children
                operators_list.append(child._get_operator())
                all_tree_list_without_leaves.append(child)
                for ch_child in child._get_children():
                    tree_list.append(ch_child)
    return operators_list, all_tree_list_without_leaves, tree_dict


def get_type_operator(operator: Operator):
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


def import_bpmn_to_process_tree(path: str):
    bpmn_graph = pm4py.read_bpmn(path)
    net, im, fm = bpmn_converter.apply(bpmn_graph)
    tree = wf_net_converter.apply(net, im, fm)
    return pm4py.utils.parse_process_tree(tree._get_label())


def convert_bpmn_to_process_tree(bpmn_graph: BPMN):
    net, im, fm = bpmn_converter.apply(bpmn_graph)
    tree = wf_net_converter.apply(net, im, fm)
    return pm4py.utils.parse_process_tree(tree._get_label())


def combine_three_trees(tree_parent: ProcessTree, tree_ch_one: ProcessTree, tree_ch_two: ProcessTree):
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

def get_node_from_activity_label(bpmn: BPMN, activity: str):
    node_id = get_id_from_activity_label(bpmn, activity)
    return get_node_from_id(bpmn, node_id)

def get_node_from_id(bpmn: BPMN, id: str):
    nodes = bpmn.get_nodes()
    for node in nodes:
        if node.get_id() == id:
            return node


def get_id_from_activity_label(bpmn: BPMN, activity: str):
    nodes = bpmn.get_nodes()
    for node in nodes:
        if node.get_name() == activity:
            return node.get_id()
    return


def get_start_events(bpmn: BPMN):
    events = []
    for node in bpmn.get_nodes():
        if isinstance(node, BPMN.StartEvent):
            events.append(node)
    return events


def get_end_events(bpmn: BPMN):
    events = []
    for node in bpmn.get_nodes():
        if isinstance(node, BPMN.EndEvent):
            events.append(node)
    return events

def get_flow_element(bpmn: BPMN):
    flows = bpmn.get_flows()
    for f in flows:
        id, name, source, target, process, layout, waypoints = f.get_id(), f.get_name(), f.get_source(), f.get_target(), f.get_process(), f.get_layout(), f.get_waypoints()
        print("flow ", id)
        print("id", id, "name", name, "source", source, "target", target, "process", process, "layout", layout,
              "waypoints", waypoints)
        print("\n")


def get_bpmn_graph_elements(bpmn: BPMN):
    nodes_list = list(bpmn.get_nodes())
    print("Nodes:", bpmn.get_nodes())
    print("First node name:", nodes_list[0].get_name())
    print("Flows:", bpmn.get_flows())


def delete_nodes_and_correct_flows(bpmn: BPMN, nodes: list[BPMN.BPMNNode], start_node_id_predecessor,
                                   end_node_id_successor, removed_flow : list):
    u_flow = start_node_id_predecessor
    #removed_flow = []
    nodes_to_remove = []
    # remove flows
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
    # last flow
    v_flow = end_node_id_successor
    flow = get_flow(bpmn, u_flow, v_flow)
    if (flow not in removed_flow) and (flow in bpmn.get_flows()):
        bpmn.remove_flow(flow)
        removed_flow.append(flow)
    # remove nodes
    for node in nodes_to_remove:
        print("remove node: ", node)
        bpmn.remove_node(node)


def get_flow(bpmn: BPMN, source, target):
    print("I will get the flow for source: ", source, "and target: ", target)
    flows_list = bpmn.get_flows()
    for flow in flows_list:
        if (flow.get_source() == source) & (flow.get_target() == target):
            return flow
        

def create_new_gateway_with_name(original_gateway, new_name):
    if isinstance(original_gateway, BPMN.ExclusiveGateway):
        new_gateway = BPMN.ExclusiveGateway(id=original_gateway.id, name=new_name, in_arcs=original_gateway.in_arcs, out_arcs=original_gateway.out_arcs, process=original_gateway.process)
    elif isinstance(original_gateway, BPMN.InclusiveGateway):
        new_gateway = BPMN.InclusiveGateway(id=original_gateway.id, name=new_name, in_arcs=original_gateway.in_arcs, out_arcs=original_gateway.out_arcs, process=original_gateway.process)
    elif isinstance(original_gateway, BPMN.ParallelGateway):
        new_gateway = BPMN.ParallelGateway(id=original_gateway.id, name=new_name, in_arcs=original_gateway.in_arcs, out_arcs=original_gateway.out_arcs, process=original_gateway.process)
    else:
        # Handle other gateway types or raise an exception if needed
        raise NotImplementedError("Unsupported gateway type")

    return new_gateway


def get_gateway_label_after_actvitiy(bpmn: BPMN, actvitiy_label: str):
    bpmn_graph = bpmn.get_graph()
    activity_node = get_node_from_activity_label(bpmn, actvitiy_label)
    print("look for the gateway after activity", activity_node)
    gateway = next(bpmn_graph.successors(activity_node.get_id()))
    if (isinstance(gateway, BPMN.Gateway)):
        gateway_label = gateway.get_name()
        if(gateway_label):
            print("found a gateway", gateway_label)
            return gateway_label
        else:
            gateway_id = gateway.get_id()
            gateway_predecessors = list(bpmn_graph.predecessors(gateway_id))
            print("got the predecessors", gateway_predecessors)
            gateway_successors = list(bpmn_graph.successors(gateway_id))
            print("got the successors", gateway_successors)
            new_name = 'label_' + gateway_id
            new_gateway = create_new_gateway_with_name(gateway, new_name)
            for predecessor in gateway_predecessors:
                flow = get_flow(bpmn, source=predecessor, target=gateway)
                new_flow = BPMN.Flow(flow.get_source(), target=gateway, id=flow.get_id(),name=flow.get_name(), process=flow.get_process())
                bpmn.add_flow(new_flow)
                bpmn.remove_flow(flow)
            for successor in gateway_successors:
                flow = get_flow(bpmn, source=gateway, target=successor)
                new_flow = BPMN.Flow(source=gateway, target=flow.get_target(), id=flow.get_id(),name=flow.get_name(), process=flow.get_process())
                bpmn.add_flow(new_flow)
                bpmn.remove_flow(flow)
            bpmn.remove_node(gateway)
            return new_gateway.get_name()
    else:
        raise TypeError(f"Not a gateway after activity label")
    

def view_bpmn_with_ids(bpmn_graph: BPMN, format: str = 'png',
                       bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    """
    Views a BPMN graph with node IDs displayed

    :param bpmn_graph: BPMN graph
    :param format: Format of the visualization (default: 'png')
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: Sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    Example usage:
    ```
    import pm4py
    bpmn_graph = pm4py.discover_bpmn_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    view_bpmn_with_ids(bpmn_graph)
    ```
    """
    format = str(format).lower()

    # Create a Graphviz Digraph
    dot = Digraph(comment='BPMN Visualization', format=format)
    dot.attr(bgcolor=bgcolor, rankdir=rankdir)

    for node in bpmn_graph.get_nodes():
        # Customize node labels to include the 'id'
        label = f"ID: {node.get_id()}\nNAME: {node.get_name()}"
        dot.node(node.get_id(), label=label)

    for edge in bpmn_graph.get_flows():
        dot.edge(edge.get_source().get_id(), edge.get_target().get_id())

    # Display the modified graph
    dot.view()


def get_conv_gateway(bpmn_process: BPMN, div_gateway: BPMN.Gateway):
    bpmn_process_graph = bpmn_process.get_graph()
    current_node = div_gateway
    print("the div_gateway_type:", type(div_gateway), "direction:", div_gateway.get_gateway_direction())

    while True:
        successors = list(bpmn_process_graph.successors(current_node))
        if not successors:  # Check if there are no more successors
            break

        successor = successors[0]  # Assuming you want to consider only the first successor
        print("check successor", successor.get_id(), ", type", type(successor))
        if isinstance(successor, type(div_gateway)):
            return successor
        else:
            current_node = successor

def check_all_tasks(task_list):
    for task in task_list:
        if not isinstance(task, BPMN.Task):
            return False
    return True


def count_gateways(nodes_list):
    count = 0
    for node in nodes_list:
        if isinstance(node, BPMN.Gateway):
            count += 1
    return count