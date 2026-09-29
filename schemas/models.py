from abc import ABC, abstractmethod

class LLM(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def generate(self, prompt):
        pass
