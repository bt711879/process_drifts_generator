import pm4py
import uuid
from pm4py.objects.bpmn.obj import BPMN


class FragmentFactory:
    @staticmethod
    def create_fragment(bpmn):
        if isinstance(bpmn, str):
            bpmn_obj = BPMN()
            start_event = BPMN.NormalStartEvent(name='start')
            bpmn_obj.add_node(start_event)
            task_id = 'task_' + str(uuid.uuid4())  # Generate a unique task ID
            task = BPMN.Task(id=task_id, name=bpmn)
            bpmn_obj.add_node(task)
            end_event = BPMN.NormalEndEvent(name='end')
            bpmn_obj.add_node(end_event)

            # Add flow from start_event to new task
            first_seq_flow = BPMN.SequenceFlow(start_event, task, process=bpmn_obj.get_process_id())
            bpmn_obj.add_flow(first_seq_flow)

            # Add flow from new task to end end_event
            second_seq_flow = BPMN.SequenceFlow(task, end_event, process=bpmn_obj.get_process_id())
            bpmn_obj.add_flow(second_seq_flow)

            return bpmn_obj
        elif isinstance(bpmn, list):
            bpmn_obj = BPMN()
            start_event = BPMN.NormalStartEvent(name='start')
            bpmn_obj.add_node(start_event)
            # add all flows from flow_list to bpmn_obj
            first_flow, last_flow = bpmn[0], bpmn[-1]
            for flow in bpmn:
                if flow != first_flow and flow != last_flow:
                    bpmn_obj.add_flow(flow)
            end_event = BPMN.NormalEndEvent(name='end')
            bpmn_obj.add_node(end_event)

            # Add flow from start_event 
            first_seq_flow = BPMN.SequenceFlow(start_event, first_flow.get_target(), process=bpmn_obj.get_process_id())
            bpmn_obj.add_flow(first_seq_flow)

            # Add flow from new task to end end_event
            second_seq_flow = BPMN.SequenceFlow(last_flow.get_source(), end_event, process=bpmn_obj.get_process_id())
            bpmn_obj.add_flow(second_seq_flow)
            return bpmn_obj
        elif isinstance(bpmn, BPMN):
            return bpmn
        else:
            raise ValueError(f"Unsupported input type: {type(bpmn)}")
        
    