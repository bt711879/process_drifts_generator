import pm4py
from pm4py.objects.bpmn.obj import BPMN


class FragmentFactory:
    @staticmethod
    def create_fragment(bpmn):
        if isinstance(bpmn, str):
            bpmn_obj = BPMN()
            start_event = BPMN.NormalStartEvent(name='start')
            bpmn_obj.add_node(start_event)
            task = BPMN.Task(id=None, name=bpmn)
            bpmn_obj.add_node(task)
            end_event = BPMN.NormalEndEvent(name='end')
            bpmn_obj.add_node(end_event)
            #add flow from start_event to new task
            first_seq_flow = BPMN.SequenceFlow(start_event, task, process=bpmn_obj.get_process_id())
            bpmn_obj.add_flow(first_seq_flow)
            #add flow from new task to end end_event
            second_seq_flow = BPMN.SequenceFlow(task, end_event, process=bpmn_obj.get_process_id())
            bpmn_obj.add_flow(second_seq_flow)
            return bpmn_obj
        elif isinstance(bpmn, BPMN):
            return bpmn
        else:
            raise ValueError(f"Unsupported input type: {type(bpmn)}")
