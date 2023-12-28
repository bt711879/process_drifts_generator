from bpmn_python.bpmn_diagram_import import BpmnDiagramGraphImport
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph

bpmn_file_path = 'bpmn_examples/A.1.0-roundtrip.bpmn'
    
# Create an instance of BpmnDiagramGraphImport
bpmn_diagram_importer = BpmnDiagramGraphImport()

# Create an instance of BpmnDiagramGraph
bpmn_diagram = BpmnDiagramGraph()

file_path = 'bpmn_examples/A.1.0-roundtrip.bpmn'

# Load the BPMN diagram from XML file
bpmn_diagram_importer.load_diagram_from_xml(bpmn_file_path, bpmn_diagram)