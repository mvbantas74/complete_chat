from abc import ABC, abstractmethod

class LLM(ABC):
    def __init__(self, model):
        self.model = model
