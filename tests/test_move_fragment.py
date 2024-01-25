import sys
sys.path.append("C:/GitRepositories/process_drifts_generator")
import unittest
import pm4py
from src import util
from src.fragment_factory import FragmentFactory
from src.transformations.move_fragment import MoveFragment
from src.transformations.remove_fragment import RemoveFragment
from src.move import Move
from src.activity_key import ActivityKey


class TestMoveFragmentInProcess(unittest.TestCase):
    
    def setUp(self):
        # import the bpmn
        self.bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
        self.bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
        pm4py.view_bpmn(self.bpmn_simple)  # Fix typo here: self.bpmn_schufa -> bpmn_schufa
        # set up transformator
        # moving a fragment before the end activity: Move Fragment {Task, Task 2} after Task3 parallel
        self.move_fragment_transformator_before_end_event = MoveFragment(self.bpmn_simple, activity_label= '_e70a6fcb-913c-4a7b-a65d-e83adc73d69c', fragment_start='_ec59e164-68b4-4f94-98de-ffb1c58a84af', fragment_end='_820c21c0-45f3-473b-813f-06381cc637cd', move=Move.ParallelMove, after_gateway=False, activity_key=ActivityKey.ID)
        # moving a fragment after the end of the fragment: Move Fragment {Task, Task 2} after Task 2 parallel
        self.move_fragment_transformator_after_end_fragment = MoveFragment(self.bpmn_simple, activity_label= '_820c21c0-45f3-473b-813f-06381cc637cd', fragment_start='_ec59e164-68b4-4f94-98de-ffb1c58a84af', fragment_end='_820c21c0-45f3-473b-813f-06381cc637cd', move=Move.ParallelMove, after_gateway=False, activity_key=ActivityKey.ID)
    def tearDown(self):
        pm4py.view_bpmn(self.bpmn_simple)
        pass

    
    def test_before_end_event_task1_predecessor(self):
        # Act 
        with self.assertRaises(ValueError):
              self.move_fragment_transformator_before_end_event.check()
        self.move_fragment_transformator_before_end_event.apply()
        # Assert
        bpmn_graph = self.bpmn_simple.get_graph()
        Task1_node = util.get_node_from_id(self.bpmn_simple, '_ec59e164-68b4-4f94-98de-ffb1c58a84af')
        task1_predecessor_is_parallel_gateway = isinstance(next(bpmn_graph.predecessors(Task1_node), pm4py.BPMN))
        self.assertTrue(task1_predecessor_is_parallel_gateway, "Task 1 predecessor is not parallel gateway")

    
    def test_before_end_event_task3_predecessor(self):
        # Act
        with self.assertRaises(ValueError):
            self.move_fragment_transformator_before_end_event.check()   
        self.move_fragment_transformator_before_end_event.apply()
        # Assert
        bpmn_graph = self.bpmn_simple.get_graph()
        Task3_node = util.get_node_from_id(self.bpmn_simple, '_e70a6fcb-913c-4a7b-a65d-e83adc73d69c')
        task3_predecessor_is_parallel_gateway = isinstance(next(bpmn_graph.predecessors(Task3_node), pm4py.BPMN))
        self.assertTrue(task3_predecessor_is_parallel_gateway, "Task 1 predecessor is not parallel gateway")
    
    
    def test_after_end_fragment_task1_predecessor(self):
        # Act   
        with self.assertRaises(ValueError):
             self.move_fragment_transformator_after_end_fragment.check()
        self.move_fragment_transformator_after_end_fragment.apply()
        # Assert
        bpmn_graph = self.bpmn_simple.get_graph()
        Task1_node = util.get_node_from_id(self.bpmn_simple, '_ec59e164-68b4-4f94-98de-ffb1c58a84af')
        task1_predecessor_is_parallel_gateway = isinstance(next(bpmn_graph.predecessors(Task1_node), pm4py.BPMN))
        self.assertTrue(task1_predecessor_is_parallel_gateway, "Task 1 predecessor is not parallel gateway")
   

    def test_after_end_fragment_task3_predecessor(self):
        # Act   
        with self.assertRaises(ValueError):
            self.move_fragment_transformator_after_end_fragment.check()
        self.move_fragment_transformator_after_end_fragment.apply()
        # Assert
        bpmn_graph = self.bpmn_simple.get_graph()
        Task3_node = util.get_node_from_id(self.bpmn_simple, '_e70a6fcb-913c-4a7b-a65d-e83adc73d69c')
        task3_predecessor_is_parallel_gateway = isinstance(next(bpmn_graph.predecessors(Task3_node), pm4py.BPMN))
        self.assertTrue(task3_predecessor_is_parallel_gateway, "Task 3 predecessor is not parallel gateway")
    




if __name__ == "__main__":
    unittest.main()