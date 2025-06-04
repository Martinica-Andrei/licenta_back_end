from enum import Enum


class TrainingStatus(Enum):
    MUST_TRAIN = 0
    CAN_TRAIN = 1
    CANNOT_TRAIN = 2
    ALREADY_TRAINED = 3
    CURRENTLY_TRAINING_OTHER_USER = 4
    CURRENTLY_TRAINING_LOGGED_IN_USER = 5


class TrainingStatusDto:
    def __init__(self, training_status: TrainingStatus, message : str):
        self.training_status = training_status
        self.message = message

    def to_json(self):
        return {
            "training_status": self.training_status.name.lower(),
            "message" : self.message
        }
