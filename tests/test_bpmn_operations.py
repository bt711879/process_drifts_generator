# tests/test_bpmn_operations.py
import unittest
from src.bpmn_operations import create_bpmn_process

class TestBPMNOperations(unittest.TestCase):
    def test_create_bpmn_process(self):
        
        # Assuming BPMN library has a method to get XML or string representation
        bpmn_model_string = process.get_xml_representation()  # Adjust this based on the actual method

        print("Generated BPMN Model:")
        print(bpmn_model_string)

        # Add assertions or other checks as needed
        self.assertIsNotNone(process)
        self.assertTrue("some_expected_value" in bpmn_model_string)
        # Add more assertions as needed
