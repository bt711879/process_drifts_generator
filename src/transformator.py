# src/transformator.py
from abc import ABC, abstractmethod
from move import Move
import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.process_tree.obj import ProcessTree, Operator

class Transformator(ABC):

    @abstractmethod
    def add_fragment(self, tree : ProcessTree, activity_label : str, fragment : ProcessTree, changed_acs : bool = False):
        """
        Add a fragment to the process.

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process  where the fragment will be added.
        - activity_label (str): The label of the activity after where the fragment will be added.
        - fragment (Fragment): The fragment to be added to the process.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    @abstractmethod
    def remove_fragment(self, tree : ProcessTree, fragment_start_label : str,  fragment_end_label : str, changed_acs : bool = False):
        """
        Remove a fragment from the process.

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process from where the fragment will be deleted.
        - fragment_start_label (str): The label of the activity marking the start of the fragment to be deleted.
        - fragment_end_label (str): The label of the activity marking the end of the fragment to be deleted.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    @abstractmethod
    def move_fragment(self, tree : ProcessTree, activity_label : str, fragment_start_label : str,  fragment_end_label : str, move_type : Move,  changed_acs : bool = False):
        '''
       Move fragment after to the activity .
        The move type defines the relation between the activity and the fragment that can be serial, parallel or conditional.
        

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragment.
        - activity_label (str): The label of the activity. The fragment will be moved to the Position after the activity label.
        - fragment_start_label (str): The label of the activity marking the start of the fragment to be moved.
        - fragment_end_label (str): The label of the activity marking the end of the fragment to be moved.
        - move_type (Move): See enum class Move.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        '''
        pass 

  
    def make_two_fragments_conditional(self, tree : ProcessTree, fragment_one_start_label : str, fragment_one_end_label : str, fragment_two_start_label : str, fragment_two_end_label : str, changed_acs : bool = False):
        """
        Make two fragmets conditions. Two sequential fragments will be disposed in one conditional branch.

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragments.
        - fragment_one_start_label (str): The label of the activity marking the start of the fragment one.
        - fragment__one_end_label (str): The label of the activity marking the end of the fragment one.
        - fragment_two_start_label (str): The label of the activity marking the start of the fragment two.
        - fragment__two_end_label (str): The label of the activity marking the end of the fragment two.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    
    def make_two_fragments_sequential(self, tree : ProcessTree, fragment_one_start_label : str, fragment_one_end_label : str, fragment_two_start_label : str, fragment_two_end_label : str, changed_acs : bool = False):
        """
        Make two fragmets sequental. Two conditional fragments will be disposed sequential.

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragments.
        - fragment_one_start_label (str): The label of the activity marking the start of the fragment one.
        - fragment__one_end_label (str): The label of the activity marking the end of the fragment one.
        - fragment_two_start_label (str): The label of the activity marking the start of the fragment two.
        - fragment__two_end_label (str): The label of the activity marking the end of the fragment two.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    
    def make_fragment_loopable(self, tree : ProcessTree, fragment_start_label : str,  fragment_end_label : str, changed_acs : bool = False):
        """
        Make a fragment loopable in the process. A exclusive gateway will be added after the fragment, leading to the next activity after the fragment or back to the begin of the fragment.
        

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragment.
        - fragment_start_label (str): The label of the activity marking the start of the fragment to be made loopable.
        - fragment_end_label (str): The label of the activity marking the end of the fragment to be made loopable.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    
    def make_fragment_non_loopable(self, tree : ProcessTree, fragment_start_label : str,  fragment_end_label : str, changed_acs : bool = False):
        """
        Make a fragment non-loopable in the process. The exclusive gateway after the fragment will be removed, if exists leading to the next activity after the fragment or back to the begin of the fragment.
    
        

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragment.
        - fragment_start_label (str): The label of the activity marking the start of the fragment to be made non-loopable.
        - fragment_end_label (str): The label of the activity marking the end of the fragment to be made non-loopable.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    
    def make_two_fragments_parallel(self, tree : ProcessTree, fragment_one_start_label : str, fragment_one_end_label : str, fragment_two_start_label : str, fragment_two_end_label : str, changed_acs : bool = False):
        """
        Make two fragmets parallel. Two sequential fragments will be disposed in one parallel branch.

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragments.
        - fragment_one_start_label (str): The label of the activity marking the start of the fragment one.
        - fragment__one_end_label (str): The label of the activity marking the end of the fragment one.
        - fragment_two_start_label (str): The label of the activity marking the start of the fragment two.
        - fragment__two_end_label (str): The label of the activity marking the end of the fragment two.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    
    def make_fragment_skippable(self, tree : ProcessTree, fragment_start_label : str,  fragment_end_label : str, changed_acs : bool = False):
        """
        Make a fragment skippable in the process. A exclusive gateway will be added before the fragment, leading to the  fragment or directly to the activity after the fragment.
        

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragment.
        - fragment_start_label (str): The label of the activity marking the start of the fragment to be made skippable.
        - fragment_end_label (str): The label of the activity marking the end of the fragment to be made skippable.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    
    def make_fragment_unskippable(self, tree : ProcessTree, fragment_start_label : str,  fragment_end_label : str, changed_acs : bool = False):
        """
        Make a fragment unskippable in the process. The exclusive gateway before the fragment will be removed, if exists leading to the fragment or directly to the activity after the fragment.
        

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragment.
        - fragment_start_label (str): The label of the activity marking the start of the fragment to be made skippable.
        - fragment_end_label (str): The label of the activity marking the end of the fragment to be made skippable.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass



    
    def substitute_fragment(self, tree : ProcessTree, activity_label : str, fragment : ProcessTree, changed_acs : bool = False):
        """
        Substitute a fragment in the process on activity.

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process where the fragment will be replaced.
        - activity_label (str): The label of the activity where the fragment will be substituted.
        - fragment (Fragment): The fragment to be substituted in the process.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        pass

    
    def swap_two_fragments(self, tree : ProcessTree, fragment_one_start_label : str, fragment_one_end_label : str, fragment_two_start_label : str, fragment_two_end_label : str, changed_acs : bool = False):
        """
        Swap two fragmets in the process.

        Parameters:
        - tree (ProcessTree): The process tree to the bpmn process containing the fragments.
        - fragment_one_start_label (str): The label of the activity marking the start of the fragment one.
        - fragment__one_end_label (str): The label of the activity marking the end of the fragment one.
        - fragment_two_start_label (str): The label of the activity marking the start of the fragment two.
        - fragment__two_end_label (str): The label of the activity marking the end of the fragment two.
        - changed_acs (bool, optional): If True, ACS (activity change set) is returned as list. Default is False.
        """
        
        pass

    def common_method(self):
        print("This is a common method.")
