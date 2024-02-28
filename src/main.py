import sys
import click


# Adding 'C:\\GitRepositories\\process_drifts_generator\\src' to the system path
sys.path.insert(0, 'C:\\GitRepositories\\process_drifts_generator')
  

# main.py
import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.algo.simulation.tree_generator import algorithm as tree_gen
from pm4py.objects.process_tree.importer import importer as ptml_importer
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from pm4py.objects.petri_net.importer import importer as pnml_importer
from random import randint
from src.transformations.add_fragment import AddFragment
from src.transformations.remove_fragment import RemoveFragment
from src.transformations.add_fragment import AddFragment
from src.transformations.move_fragment import MoveFragment
from src.transformations.replace_fragment import ReplaceFragment
from src.transformations.swap_two_fragments import SwapFragments
from src.transformations.embed_process_fragment import EmbedFragment, EmbedType
from src.transformations.parallelize_process_fragments import ParellelizeFragment
from src.fragment_factory import FragmentFactory
from src.activity_key import ActivityKey
import src.util as util
from src.move import Move

import networkx as nx


def test_process_visualization():
    # core_transformator = CoreTransformator(random_transformation=False)

    # import the process tree
    tree = util.import_bpmn_to_process_tree('bpmn_examples/schufascoring-synchron.bpmn')

    # Get the subtree dictionary
    subtree_dict = util.get_sub_trees(tree)

    # visualize the process
    bpmn_shufa = pm4py.convert_to_bpmn(tree)
    bpmn_simple = pm4py.read_bpmn('bpmn_examples/A.1.0-roundtrip.bpmn')
    pm4py.view_bpmn(bpmn_shufa)

bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
bpmn_schufa_loop = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron-loop.bpmn")
bpmn_simple = pm4py.read_bpmn('bpmn_examples/A.1.0-roundtrip.bpmn')

def test_remove_fragment():
    bpmn_simple = pm4py.read_bpmn('bpmn_examples/A.1.0-roundtrip.bpmn')
    remove_fragment_transformator = RemoveFragment(bpmn_process=bpmn_simple,  fragment_start=util.get_id_from_activity_label(bpmn_simple, 'Task 2'), fragment_end=util.get_id_from_activity_label(bpmn_simple,'Task 2'),pop_fragment=False, activity_key=ActivityKey.ID)
    # Apply the transformation
    #remove_fragment_transformator.apply()
    remove_fragment_transformator.check()
    remove_fragment_transformator.apply()
    pm4py.view_bpmn(bpmn_simple)
    # convert transformed bpmn object to process tree
    # tree = pm4py.convert_to_process_tree(bpmn_shufa)
    # pm4py.view_process_tree(tree)
    # print(bpmn_simple.get_flows())
    # tree = pm4py.convert_to_process_tree(bpmn_simple)
    # pm4py.view_process_tree(tree)


def test_add_fragment():
    # import the bpmn
    bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
    bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
    # pm4py.view_bpmn(bpmn_schufa)
    # test transformations add fragment
    activity = util.get_id_from_activity_label(bpmn_schufa, 'Scoring-ergebnis einholen')
    activity_after = util.get_id_from_activity_label(bpmn_schufa, 'Schufascore zurückmelden')
    add_transformator = AddFragment(bpmn_process=bpmn_schufa, activity_before=activity, activity_after=activity_after, fragment=FragmentFactory.create_fragment('Task 4'), move=Move.SerialMove)
    add_transformator.check()
    add_transformator.apply()
    pm4py.view_bpmn(bpmn_schufa)
    #print(bpmn_schufa.get_nodes())


def test_fragment_factory():
    new_fragment = FragmentFactory.create_fragment("task2")
    graph = new_fragment.get_graph()
    print(graph.edges())


def test_fragment_from_list_flow():
    bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
    remove_fragment_transformator = RemoveFragment(bpmn_process=bpmn_simple, fragment_start='Task 1', fragment_end='Task 2', pop_fragment=True)
    bpmn_extracted = FragmentFactory.create_fragment(remove_fragment_transformator.apply())
    pm4py.view_bpmn(bpmn_simple)
    pm4py.view_bpmn(bpmn_extracted)


def test_move_fragment():
    bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
    pm4py.view_bpmn(bpmn_simple)
    activity_label = "_93c466ab-b271-4376-a427-f4c353d55ce8" # start event
    activity_after = "_e70a6fcb-913c-4a7b-a65d-e83adc73d69c" # task 3
    fragment_start = "_ec59e164-68b4-4f94-98de-ffb1c58a84af" # task 1
    fragment_end = "_ec59e164-68b4-4f94-98de-ffb1c58a84af" # task 1
    move_fragment_transformator = MoveFragment(bpmn_simple, activity_before=activity_label, activity_after=activity_after, fragment_start=fragment_start, fragment_end=fragment_end, move=Move.SerialMove, activity_key=ActivityKey.ID)
    move_fragment_transformator.apply()
    pm4py.view_bpmn(bpmn_simple)

def test_move_fragment_schufa():
    pm4py.view_bpmn(bpmn_schufa)
    move_fragment_transformator_after_gateway = MoveFragment(bpmn_process=bpmn_schufa, activity_before='ExclusiveGateway_0e5en8h', activity_after='Task_0l942o9', fragment_start='Task_16winvj', fragment_end='Task_16winvj', move=Move.SerialMove, activity_key=ActivityKey.ID)
    move_fragment_transformator_after_gateway.check()
    move_fragment_transformator_after_gateway.apply()
    pm4py.view_bpmn(bpmn_schufa)
    
def test_view_schufa():
    bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
    pm4py.view_bpmn(bpmn_schufa)


def test_replace_fragment():
    gateway_start = 'ExclusiveGateway_0e5en8h'
    gateway_end = 'ExclusiveGateway_11dldcm'
    replace_transformator = ReplaceFragment(bpmn_process=bpmn_schufa, fragment_one_start=gateway_start, fragment_one_end=gateway_end, replace_fragment=bpmn_simple, activity_key=ActivityKey.ID)
    replace_transformator.apply()
    pm4py.view_bpmn(bpmn_schufa)


def test_get_gateway():
    join_gateway_label = util.get_gateway_label_after_actvitiy(bpmn_schufa, 'Schufascore senden')
    print(join_gateway_label)
    new_gateway_id = util.get_id_from_activity_label(bpmn_schufa, join_gateway_label)
    print("new gatew id", new_gateway_id)
    #util.get_flow_element(bpmn_schufa)

def test_visualize_ids():
    #pm4py.view_bpmn(bpmn_schufa, format='html')
    #print(util.get_id_from_activity_label(bpmn=bpmn_schufa, activity='Verzögerung melden'))
    #pm4py.view_bpmn(bpmn_graph=bpmn_schufa)
    util.view_bpmn_with_ids(bpmn_graph=bpmn_schufa, format='svg')

def test_swap_fragments():
    swap_fragments_transformator = SwapFragments(bpmn_process=bpmn_schufa, fragment_one_start='Task_1r15hqs', fragment_one_end='ExclusiveGateway_125lzox', fragment_two_start='ExclusiveGateway_0e5en8h', fragment_two_end='ExclusiveGateway_11dldcm', activity_key=ActivityKey.ID)
    swap_fragments_transformator.apply()
    pm4py.view_bpmn(bpmn_schufa)

def test_embed_process_fragment():
    pm4py.view_bpmn(bpmn_schufa)
    embed_transformator_1 = EmbedFragment(bpmn_schufa, fragment_start='Task_16winvj', fragment_end= 'Task_1fzfxey', embed_type= EmbedType.Conditional) # between Scoring-ergebnis einholen and Schufascore zurückmelden
    embed_transformator_1.apply()
    pm4py.view_bpmn(bpmn_schufa)

def test_get_conv_gateway():
    div_gateway = util.get_node_from_id(bpmn_schufa, 'ExclusiveGateway_0e5en8h')
    conv_gateway = util.get_conv_gateway(bpmn_schufa, div_gateway)
    print(conv_gateway.get_id())
    print(conv_gateway.get_gateway_direction())

def test_parallelize_fragment():
    parallelize_fragment_transformator = ParellelizeFragment(bpmn_simple, fragment_start='_ec59e164-68b4-4f94-98de-ffb1c58a84af', fragment_end='_e70a6fcb-913c-4a7b-a65d-e83adc73d69c', activity_key=ActivityKey.ID)
    print(parallelize_fragment_transformator.check())
    #parallelize_fragment_transformator.apply()
    #pm4py.view_bpmn(bpmn_simple)

def test_successors_predecessors():
        bpmn_graph = bpmn_schufa.get_graph()
        activity_successor = list(bpmn_graph.successors(util.get_node_from_id(bpmn_schufa, 'ExclusiveGateway_0e5en8h'))) #get only the first
        #print("activity successor", activity_successor)
        # get the activity_after predecessor
        activity_after_predecessor = list(bpmn_graph.predecessors(util.get_node_from_id(bpmn_schufa, 'ExclusiveGateway_11dldcm')))
        print ('activity_successor_list:', activity_successor[1],'activity_predecessor_list:', activity_after_predecessor[1])

def test_get_target_of_flow():
    schufa_graph = bpmn_schufa.get_graph()
    edge_id = 'SequenceFlow_14gfddm'
    target_node_id = util.get_target_node_id(bpmn_schufa, edge_id)
    print(type(target_node_id))
    target_node = util.get_node_from_id(bpmn_schufa, target_node_id)
    activity_after_node = util.get_node_from_id(bpmn_schufa, 'ExclusiveGateway_11dldcm')
    path_list = list(nx.all_simple_paths(schufa_graph, target_node, activity_after_node))[-1][-2]
    print(path_list)

def test_get_right_predecessor():
    # 
    pass

def test_appairs_before():
    graph = bpmn_schufa_loop.get_graph()
    activity_before=util.get_node_from_id(bpmn_schufa_loop, 'Task_1fzfxey')
    activity_after=util.get_node_from_id(bpmn_schufa_loop, 'ExclusiveGateway_0e5en8h')
    gateway_before = util.get_node_from_id(bpmn_schufa_loop, 'ExclusiveGateway_0e5en8h')
    gateway_after = util.get_node_from_id(bpmn_schufa_loop, 'ExclusiveGateway_11dldcm')
    print(util.appears_before(graph=graph, node_a=gateway_before, node_b=gateway_after))

def test_get_edges_from_start_to_node():
    return util.get_edges_from_start_to_node_simple(bpmn=bpmn_schufa_loop, node_id='gateway_ce00d2e7-0881-4569-a23c-4866bbe59f0a')

def test_all_simple_paths():
    graph = bpmn_schufa_loop.get_graph()
    node = 'gateway_ce00d2e7-0881-4569-a23c-4866bbe59f0a'
    start_events = util.get_start_events(bpmn_schufa_loop, id=True)
    paths = set()
    for start_event in start_events:
        simple_paths = nx.all_simple_paths(G=graph, source=start_event, target=node)
        for path in simple_paths:
            for node in path:
                paths.add(node)  # Convert list to tuple and add to set
    print(paths)


def test_all_edges():
    graph = bpmn_schufa_loop.get_graph()
    node = 'Task_1fzfxey'
    start_events = util.get_start_events(bpmn_schufa_loop, id=True)
    edges_set = set()
    for start_event in start_events:
        simple_paths = nx.all_simple_paths(G=graph, source=start_event, target=node)
        for path in simple_paths:
            for i in range(len(path) - 1):
                edges_set.add(util.get_flow(bpmn_schufa_loop, path[i], path[i+1]).get_id())  # Get flow between to nodes
    print(edges_set, len(edges_set))



@click.command()
@click.argument('name')
@click.option('--greeting', '-g', default='Hello', help='The greeting to use.', required=True, type=str)
def mycommand(name, greeting):
    '''
    This command greets a person. Can customize the greet and the name of the person
    '''
    click.echo(greeting + " " + name)

if __name__ == "__main__":
    #test_fragment_factory("")
    #test_visualize_ids()
    #test_appairs_before()
    #pm4py.view_bpmn(bpmn_schufa_loop)
    #test_all_edges()
    #print(util.get_start_events(bpmn_schufa_loop, id=True))
    mycommand()
   

