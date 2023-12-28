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
from  core_transformator import CoreTransformator
from transformations.remove_fragment import RemoveFragment
from transformations.add_fragment import AddFragment
import util

if __name__ == "__main__":
    #core_transformator = CoreTransformator(random_transformation=False)

    # import the process tree
    tree = util.import_bpmn_to_process_tree('bpmn_examples\schufascoring-synchron.bpmn')

    # Get the subtree dictionary
    subtree_dict = util.get_sub_trees(tree)

    #visualize the process
    bpmn_shufa = pm4py.convert_to_bpmn(tree)
    bpmn_simple = pm4py.read_bpmn('bpmn_examples\A.1.0-roundtrip.bpmn')
    pm4py.view_bpmn(bpmn_shufa)
    
    #get labels for searched fragment
    #labels_tuple = ('Scoring_ergebnis einholen', 'Verzörgerung melden', 'Schufascore zurückmelden')
    #for key,value in subtree_dict.items():
    #    print(f"{key}: {value}\n")

    #output bpmn nodes
    #util.get_process_fragment(bpmn_shufa)

    #output graph nx multi direct
    #util.get_graph_elements(bpmn_simple)


    #output BPMN nodes
    #util.get_bpmn_graph_elements(bpmn_simple)
    #util.get_flow_element(bpmn_simple)

    #output remove_fragment
    #core_transformator.remove_fragment(bpmn_shufa, 'Scoring-ergebnis einholen', 'Schufascore zurückmelden')
    #core_transformator.remove_fragment(bpmn_shufa, 'Scoring durchführen (level 2)', 'Schufascore senden')
    #core_transformator.remove_fragment(bpmn_simple, 'Task 2', 'Task 3')
    

    #output remove flow
    '''
    source = util.get_node_from_id(bpmn_shufa, util.get_id_from_activity_label(bpmn_shufa, 'Scoring durchführen (level 2)'))
    target = util.get_node_from_id(bpmn_shufa, util.get_id_from_activity_label(bpmn_shufa, 'Schufascore senden'))
    flow_key = BPMN.SequenceFlow(source, target)
    bpmn_shufa.remove_flow(util.get_flow(bpmn_shufa, source, target))
    pm4py.view_bpmn(bpmn_shufa)
    '''


    #pm4py.visualization.process_tree(tree)
    #pm4py.view_process_tree(tree)

    #test tranformations remove
    #remove_fragment_transformator = RemoveFragment(bpmn_shufa, 'Scoring durchführen (level 2)', 'Schufascore senden')
    #remove_fragment_transformator = RemoveFragment(bpmn_shufa, 'Scoring-ergebnis einholen', 'Schufascore zurückmelden')
    remove_fragment_transformator = RemoveFragment(bpmn_simple, 'Task 2', 'Task 3')
    # Apply the transformation
    #remove_fragment_transformator.apply()
    #convert transformed bpmn object to process tree
    #tree = pm4py.convert_to_process_tree(bpmn_shufa)
    #pm4py.view_process_tree(tree)
    #print(bpmn_simple.get_flows())
    #tree = pm4py.convert_to_process_tree(bpmn_simple)
    #pm4py.view_process_tree(tree)

    #test transformations add fragment
    add_fragment_tranformator = AddFragment(bpmn_shufa, 'Schufascore zurückmelden', 'Task 4')
    add_fragment_tranformator.apply()
    pm4py.view_bpmn(bpmn_shufa)