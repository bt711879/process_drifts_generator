import sys
sys.path.append("C:/GitRepositories/process_drifts_generator")
import unittest
import pm4py
from src.fragment_factory import FragmentFactory
from src.transformations.add_fragment import AddFragment
from src.transformations.remove_fragment import RemoveFragment
from src.move import Move
from src.activity_key import ActivityKey


class TestAddTasksToProcess(unittest.TestCase):

    def setUp(self):
        # import the bpmn
        self.bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
        bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
        pm4py.view_bpmn(self.bpmn_schufa)  # Fix typo here: self.bpmn_schufa -> bpmn_schufa
        # set up transformator
        self.fragment_to_add_task4 = FragmentFactory.create_fragment('Task 4')
        self.fragment_to_add_task5 = FragmentFactory.create_fragment('Task 5')
        self.fragment_to_add_task6 = FragmentFactory.create_fragment('Task 6')
        self.add_transformator_task4 = AddFragment(self.bpmn_schufa, 'Task_1r15hqs', self.fragment_to_add_task4, move=Move.ParallelMove)
        self.add_transformator_task5 = AddFragment(self.bpmn_schufa, 'Task_1r15hqs', self.fragment_to_add_task5, move=Move.ConditionalMove)
        self.add_transformator_task6 = AddFragment(self.bpmn_schufa, 'Task_1r15hqs', self.fragment_to_add_task6, move=Move.SerialMove)

    def tearDown(self):
        pm4py.view_bpmn(self.bpmn_schufa)
        pass

    def test_add_task4_parallel(self):
        # Act   
        self.add_transformator_task4.check()
        self.add_transformator_task4.apply()
        # Assert
        nodes_with_task4_name = [node for node in self.bpmn_schufa.get_nodes() if node.get_name() == 'Task 4']
        self.assertTrue(nodes_with_task4_name, "No node with name 'Task 4' found")

    def test_add_task5_conditional(self):
        # Act  
        self.add_transformator_task5.check()
        self.add_transformator_task5.apply()
        # Assert
        nodes_with_task5_name = [node for node in self.bpmn_schufa.get_nodes() if node.get_name() == 'Task 5']
        self.assertTrue(nodes_with_task5_name, "No node with name 'Task 5' found")

    def test_add_task5_conditional_double(self):
        # Act  
        self.add_transformator_task5.check()
        self.add_transformator_task5.apply()
        self.add_transformator_task5.apply()
        # Assert
        nodes_with_task5_name = [node for node in self.bpmn_schufa.get_nodes() if node.get_name() == 'Task 5']
        self.assertTrue(nodes_with_task5_name, "No node with name 'Task 5' found")

    def test_add_task6_serial(self):
        # Act 
        self.add_transformator_task6.check()
        self.add_transformator_task6.apply()
        # Assert
        nodes_with_task6_name = [node for node in self.bpmn_schufa.get_nodes() if node.get_name() == 'Task 6']
        self.assertTrue(nodes_with_task6_name, "No node with name 'Task 6' found")
        



class TestAddFragmentsToProcess(unittest.TestCase):

    def setUp(self):
        # import the bpmn
        self.bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
        self.bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
        # pm4py.view_bpmn(self.bpmn_schufa)  # Fix typo here: self.bpmn_schufa -> bpmn_schufa
        # set up transformator
        self.fragment_to_add_bpmn_simple = self.bpmn_simple
        self.add_transformator_after_start = AddFragment(self.bpmn_schufa, 'StartEvent_0o849un', self.fragment_to_add_bpmn_simple, move=Move.SerialMove, activity_key=ActivityKey.ID)
        self.add_transformator_parallel = AddFragment(self.bpmn_schufa, 'Task_0l942o9', self.fragment_to_add_bpmn_simple, move=Move.ParallelMove, activity_key=ActivityKey.ID)
        self.add_transformator_conditional = AddFragment(self.bpmn_schufa, 'Task_1r15hqs', self.fragment_to_add_bpmn_simple, move=Move.ParallelMove, activity_key=ActivityKey.ID)

    def tearDown(self):
        pm4py.view_bpmn(self.bpmn_schufa)
        pass

    def test_add_after_start(self):
        # Act   
        self.add_transformator_after_start.apply()
        # Assert
        nodes_bpmn_simple = self.bpmn_simple.get_nodes()
        nodes_bpmn_schufa = self.bpmn_schufa.get_nodes()

        for node_bpmn_simple in nodes_bpmn_simple:
             if not isinstance(node_bpmn_simple, (pm4py.BPMN.StartEvent, pm4py.BPMN.EndEvent)):
                self.assertIn(node_bpmn_simple, nodes_bpmn_schufa, f"Node {node_bpmn_simple.get_name()} not found in bpmn_schufa nodes")    


    def test_add_parallel(self):
        # Act   
        self.add_transformator_parallel.apply()
        # Assert
        nodes_bpmn_simple = self.bpmn_simple.get_nodes()
        nodes_bpmn_schufa = self.bpmn_schufa.get_nodes()
        for node_bpmn_simple in nodes_bpmn_simple:
            if not isinstance(node_bpmn_simple, (pm4py.BPMN.StartEvent, pm4py.BPMN.EndEvent)):
                self.assertIn(node_bpmn_simple, nodes_bpmn_schufa, f"Node {node_bpmn_simple.get_name()} not found in bpmn_schufa nodes") 

    def test_add_parallel_double(self):
        # Act
        self.add_transformator_parallel.check() 
        self.add_transformator_parallel.apply()
        self.add_transformator_parallel.apply()
        # Assert
        nodes_bpmn_simple = self.bpmn_simple.get_nodes()
        nodes_bpmn_schufa = self.bpmn_schufa.get_nodes()
        for node_bpmn_simple in nodes_bpmn_simple:
            if not isinstance(node_bpmn_simple, (pm4py.BPMN.StartEvent, pm4py.BPMN.EndEvent)):
                self.assertIn(node_bpmn_simple, nodes_bpmn_schufa, f"Node {node_bpmn_simple.get_name()} not found in bpmn_schufa nodes") 


    def test_add_conditional(self):
        # Act   
        self.add_transformator_conditional.apply()
        # Assert
        nodes_bpmn_simple = self.bpmn_simple.get_nodes()
        nodes_bpmn_schufa = self.bpmn_schufa.get_nodes()
        for node_bpmn_simple in nodes_bpmn_simple:
            if not isinstance(node_bpmn_simple, (pm4py.BPMN.StartEvent, pm4py.BPMN.EndEvent)):
                self.assertIn(node_bpmn_simple, nodes_bpmn_schufa, f"Node {node_bpmn_simple.get_name()} not found in bpmn_schufa nodes")  


class TestAddFragmentsToProcessEdge(unittest.TestCase):

    def setUp(self):
        # import the bpmn
        self.bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
        self.bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
        # pm4py.view_bpmn(self.bpmn_schufa)  # Fix typo here: self.bpmn_schufa -> bpmn_schufa
        # set up transformator
        self.fragment_to_add_bpmn_simple = self.bpmn_simple
        self.add_transformator_after_end = AddFragment(self.bpmn_schufa, 'EndEvent_0khk0tq', self.fragment_to_add_bpmn_simple, move=Move.SerialMove, activity_key=ActivityKey.ID)
        self.add_transformator_parallel = AddFragment(self.bpmn_schufa, 'EndEvent_0rp5trg', self.fragment_to_add_bpmn_simple, move=Move.ParallelMove, activity_key=ActivityKey.ID)
        self.add_transformator_conditional = AddFragment(self.bpmn_schufa, 'ExclusiveGateway_0e5en8h', self.fragment_to_add_bpmn_simple, move=Move.ParallelMove, activity_key=ActivityKey.ID)

    def tearDown(self):
        pm4py.view_bpmn(self.bpmn_schufa)
        pass

    def test_add_after_start(self):
        # Act
        with self.assertRaises(ValueError):
            self.add_transformator_after_end.check()
        # Assert
        


    def test_add_parallel(self):
        # Act  
        with self.assertRaises(ValueError):
            self.add_transformator_parallel.check()
        # Assert
        

    def test_add_conditional(self):
        # Act 
        with self.assertRaises(ValueError):  
            self.add_transformator_conditional.check()
        # Assert
        


if __name__ == "__main__":
    unittest.main()
