import abc


class NotificationBackend(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send(self, to: list[str], subject: str, message: str):
        raise NotImplementedError
