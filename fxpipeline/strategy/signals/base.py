from abc import ABC, abstractmethod

"""
The model's responsibility
- decide once
- specify:
    - direction
    - invalidation (SL)
    - target (TP)
"""


# TODO: multiclass classification: HOLD, BUY, SELL
class SignalGenerator(ABC):
    @abstractmethod
    def generate_batch(self, data: Data) -> np.ndarray:
        """
        Vectorized for quick validation + Left-padded if warm-up is needed.

        Return a batch of probability of holding a buy position.
        """

    def generate(self, data: Data) -> bool:
        """
        Live mode (default: delegate to batch)

        Return a probability of holding a buy position.
        """
        if len(data) != 1:
            raise ValueError("generate() expects a single row")
        return self.generate_batch(data)[0]

    def __repr__(self):
        return self.__class__.__name__
