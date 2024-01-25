import sys
sys.path.append("C:/GitRepositories/process_drifts_generator")
import unittest
import pm4py
from src.fragment_factory import FragmentFactory
from src.transformations.add_fragment import AddFragment
from src.transformations.remove_fragment import RemoveFragment
from src.move import Move
import src.util as util
from src.activity_key import ActivityKey


class TestViewBpmnWithIds(unittest.TestCase):

    def setUp(self):
        # import the bpmn
        self.bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
        self.bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
        pm4py.view_bpmn(self.bpmn_schufa)  

    def tearDown(self):
        pm4py.view_bpmn(self.bpmn_schufa)
        pass

    def test_view_schufa(self):
        # Act 
        util.view_bpmn_with_ids(self.bpmn_schufa, 'svg')
   
        # Assert


    def test_view_simple(self):
        # Act 
        util.view_bpmn_with_ids(self.bpmn_simple, 'svg')
   
        # Assert



if __name__ == "__main__":
    unittest.main()
