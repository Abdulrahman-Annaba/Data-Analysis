from abc import ABC, abstractmethod


class Command(ABC):
    """Command interface for designating commands"""
    @abstractmethod
    def execute(self) -> None:
        """Execute the command"""
        pass
