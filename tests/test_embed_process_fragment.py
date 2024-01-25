import sys
sys.path.append("C:/GitRepositories/process_drifts_generator")
import unittest
import pm4py
from src.fragment_factory import FragmentFactory
from src.transformations.embed_process_fragment import EmbedFragment, EmbedType
from src.transformations.remove_fragment import RemoveFragment
from src.move import Move
from src.activity_key import ActivityKey


class TestEmbedFragmentInProcess(unittest.TestCase):

    def setUp(self):
        # import the bpmn
        self.bpmn_schufa = pm4py.read_bpmn("bpmn_examples/schufascoring-synchron.bpmn")
        self.bpmn_simple = pm4py.read_bpmn("bpmn_examples/A.1.0-roundtrip.bpmn")
        #pm4py.view_bpmn(self.bpmn_schufa)  # Fix typo here: self.bpmn_schufa -> bpmn_schufa
        # set up transformator
        self.embed_transformator_1 = EmbedFragment(self.bpmn_schufa, fragment_start='Task_16winvj', fragment_end= 'Task_1fzfxey', embed_type= EmbedType.Loop) # between Scoring-ergebnis einholen and Schufascore zurückmelden
        self.embed_transformator_2 = EmbedFragment(self.bpmn_schufa, fragment_start='Task_1r15hqs', fragment_end= 'Task_04l4kzo', embed_type= EmbedType.Loop) # between Scoring durchführen(level 1) and Ergebnis senden 

    def tearDown(self):
        pm4py.view_bpmn(self.bpmn_schufa)
        pass

    def test_embed_1(self):
        # Act   
        self.embed_transformator_1.apply()
        # Assert


    def test_embed_2(self):
        # Act   
        self.embed_transformator_2.apply()
        # Assert
   



if __name__ == "__main__":
    unittest.main()
