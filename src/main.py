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
from core_transformator import CoreTransformator
from src.transformations.add_fragment import AddFragment
from transformations.remove_fragment import RemoveFragment
from transformations.add_fragment import AddFragment
from src.fragment_factory import FragmentFactory
import util
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


def test_remove_fragment():
    bpmn_simple = pm4py.read_bpmn('bpmn_examples/A.1.0-roundtrip.bpmn')
    remove_fragment_transformator = RemoveFragment(bpmn_simple, 'Task 2', 'Task 3')
    # Apply the transformation
    remove_fragment_transformator.apply()
    # convert transformed bpmn object to process tree
    # tree = pm4py.convert_to_process_tree(bpmn_shufa)
    # pm4py.view_process_tree(tree)
    # print(bpmn_simple.get_flows())
    tree = pm4py.convert_to_process_tree(bpmn_simple)
    pm4py.view_process_tree(tree)


def test_add_fragment():
    # import the bpmn
    bpmn_schufa = pm4py.read_bpmn("C:/Users/R40106/PycharmProjects/process_drifts_generator/bpmn_examples/schufascoring-synchron.bpmn")
    # test transformations add fragment
    add_transformator = AddFragment(bpmn_schufa, 'Schufascore zurückmelden', FragmentFactory.create_fragment('Task 4'), move=Move.SerialMove)
    add_transformator.apply()
    pm4py.view_bpmn(bpmn_schufa)


def test_fragment_factory():
    new_fragment = FragmentFactory.create_fragment("task2")
    pm4py.view_bpmn(new_fragment)


if __name__ == "__main__":
    test_add_fragment()
