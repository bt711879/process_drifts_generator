# main.py
from bpmn_operations import create_bpmn_process

def main():
    # Call the function to create the BPMN process
    bpmn_process = create_bpmn_process()

    # Optionally, print or display the BPMN model
    bpmn_model_string = bpmn_process.get_xml_representation()
    print("Generated BPMN Model:")
    print(bpmn_model_string)

if __name__ == "__main__":
    main()
