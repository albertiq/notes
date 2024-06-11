TASK_SIGNATURE_STRATEGY_PATTERN = """
class TaskSignature(ABC):
    @abstractmethod
    def get_signature(self, args: TaskArgsBase, signature: Signature) ->: group | Signature
        pass


class ConcreteTaskSignature(TaskSignature):
    def get_signature(self, args: ConcreteTaskArgs, signature: Signature) -> group:
        concrete_task_creator = ConcreteTaskCreator(args)
        concrete_task_group = concrete_task_creator.create_task_group(signature)

        return concrete_task_group


class Context:
    def __init__(self, task_signature: TaskSignature):
        self._task_signature = task_signature

    def set_task_signature(self, task_signature: TaskSignature):
        self._task_signature = task_signature

    def get_signature(self, args: TaskArgsBase, signature: Signature):
        return self._task_signature.get_signature(args, signature)
"""
CELERY_TASK_CREATOR = """
class CeleryTaskCreator(ABC):
    @abstractmethod
    def get_payloads(self) -> list[dict]:
        pass

    def create_task(self, task_signature: Signature) -> Signature:
        payloads = self.get_payloads()
        for payload in payloads:
            task_signature.kwargs = payload
        return task_signature

    def create_task_group(self, task_signature: Signature) -> group:
        task_signatures = []
        payloads = self.get_payloads()
        for payload in payloads:
            task_signature.kwargs = payload
            task_sig = copy.copy(task_signature)
            task_signatures.append(task_sig)
        return group(task_signatures)
"""
CELERY_WITH_REDIS_PATCH = """
class CeleryClient(metaclass=Singleton):
    def __init__(self) -> None:
        # Использовать redis в качестве backend: https://github.com/celery/celery/pull/2204
        self._celery = self.patch_celery().Celery(**config)

    def patch_celery(self) -> None:
        # https://github.com/celery/celery/issues/4834
        def _unpack_chord_result(...):
            ...

    def get_celery(self) -> Celery:
        return self._celery

celery_client = CeleryClient().get_celery()
"""
NOTES_DATA: list[dict] = [
    {
        "name": "Celery task signature strategy",
        "code_block": TASK_SIGNATURE_STRATEGY_PATTERN,
    },
    {
        "name": "Celery task creator",
        "code_block": CELERY_TASK_CREATOR,
    },
    {
        "name": "Celery client with redis patch",
        "code_block": CELERY_WITH_REDIS_PATCH,
    },
]
