import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.process_tree.obj import ProcessTree, Operator

class FragmentFactory:
    @staticmethod 
    def createFragment(tree):
        if isinstance(tree, str):
            return ProcessTree(None, None, None, tree)
        elif isinstance(tree, ProcessTree):
            return tree
        elif isinstance (BPMN, tree):
            return pm4py.convert_to_process_tree(tree)
        else: return ProcessTree(None, None, None, None)