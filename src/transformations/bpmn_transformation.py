from abc import ABC, abstractmethod


class BpmnTransformation(ABC):
    def __init__(self, bpmn_process):
        self.bpmn_process = bpmn_process

    @abstractmethod
    def apply(self):
        pass
