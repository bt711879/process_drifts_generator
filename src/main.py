import sys

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
bpmn_simple = pm4py.read_bpmn('bpmn_examples/A.1.0-roundtrip.bpmn')

def test_remove_fragment():
    bpmn_simple = pm4py.read_bpmn('bpmn_examples/A.1.0-roundtrip.bpmn')
    remove_fragment_transformator = RemoveFragment(bpmn_simple,  util.get_id_from_activity_label(bpmn_simple, 'Task 2'), util.get_id_from_activity_label(bpmn_simple,'Task 3'),pop_fragment=False, activity_key=ActivityKey.ID)
    # Apply the transformation
    #remove_fragment_transformator.apply()
    remove_fragment_transformator.check()
    # convert transformed bpmn object to process tree
    # tree = pm4py.convert_to_process_tree(bpmn_shufa)
    # pm4py.view_process_tree(tree)
    # print(bpmn_simple.get_flows())
    tree = pm4py.convert_to_process_tree(bpmn_simple)
    pm4py.view_process_tree(tree)


def test_add_fragment():
    # import the bpmn
    bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
    bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
    pm4py.view_bpmn(bpmn_schufa)
    # test transformations add fragment
    activity = util.get_id_from_activity_label(bpmn_schufa, 'Scoring durchführen(level 1)')
    add_transformator = AddFragment(bpmn_schufa, activity, FragmentFactory.create_fragment('Task 4'), move=Move.ConditionalMove)
    #add_transformator.apply()
    add_transformator.check()
    pm4py.view_bpmn(bpmn_schufa)
    print(bpmn_schufa.get_nodes())


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
    #move_fragment_transformator = MoveFragment(bpmn_process=bpmn_simple, activity_label='_e70a6fcb-913c-4a7b-a65d-e83adc73d69c', fragment_start='_ec59e164-68b4-4f94-98de-ffb1c58a84af', fragment_end='_820c21c0-45f3-473b-813f-06381cc637cd', move=Move.SerialMove, after_gateway=False)
    move_fragment_transformator = MoveFragment(bpmn_simple, activity_label= '_e70a6fcb-913c-4a7b-a65d-e83adc73d69c', fragment_start='_ec59e164-68b4-4f94-98de-ffb1c58a84af', fragment_end='_820c21c0-45f3-473b-813f-06381cc637cd', move=Move.ParallelMove, after_gateway=False, activity_key=ActivityKey.ID)
    move_fragment_transformator.apply()
    pm4py.view_bpmn(bpmn_simple)
    
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
    util.view_bpmn_with_ids(bpmn_graph=bpmn_simple, format='svg')

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


if __name__ == "__main__":
    #test_fragment_factory("")
    test_add_fragment()


