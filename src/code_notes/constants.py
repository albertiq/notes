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


concrete_task_ctx = Context(ConcreteTaskSignature)
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
CELERY_PRODUCER = """
class CeleryProducer:
    def send_task(self, task_name: str, priority: int, payloads: list[dict]) -> None:
        for payload in payloads:
            celery_client.send_task(task_name, payload, priority)

    def send_chain_tasks(self, *tasks: group | Signature, priority: int) -> None:
        celery_app = init_celery_app()
        chain = celery.chain(*tasks)
        chain.app.conf = celery_app.conf
        chain.apply_async(priority)

cp = CeleryProducer()
"""
INIT_CELERY_APP = """
celery = None

def init_celery_app() -> None:
    global celery
    celery_app = celery_client
    celery_app.conf.task_queues = [queue1, queue2, ...]
    celery_app.conf.broker_transport_options = {
        "queue_order_strategy": "priority",
        "priority_steps": list(range(10)),
    }
    celery_app.autodiscover_tasks(related_name="package.tasks_module", force=True)
    celery = celery_app
    return celery
"""
TASK_SENDER = """
class TaskSender:
    def __init__(self, task_signatures: tuple, priority: int) -> None:
        self.task_signatures = task_signatures
        self.priority = priority

    def send_tasks(self) -> None:
        celery_producer.send_chain_tasks(
            *(sig for sig in self.task_signatures if sig),
            self.priority,
        )
"""
KAFKA_PRODUCER_INTERFACE = """
class KafkaProducer(ABC):
    def __init__(self, broker_host: str) -> None:
        self.producer = Producer({"bootstrap.servers": broker_host})

    @abstractmethod
    def get_messages(self) -> list[dict]:
        pass

    def _exception_handler(self, _) -> None:
        self.producer.poll(8)  # for clickhouse queue table (kafka_flush_interval param)

    @backoff.on_exception(backoff.constant, BufferError, on_backoff=_exception_handler)
    def produce(self, topic: str) -> None:
        try:
            messages = self.get_messages()
            for message in messages:
                self.producer.produce(topic, json.dumps(message, default=json_serial).encode("utf-8"))
                self.producer.poll(0)
            self.producer.flush()
        except BufferError as err:
            logger.exception("Buffer limit: %s", str(err))
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
    {
        "name": "Celery producer",
        "code_block": CELERY_PRODUCER,
    },
    {
        "name": "Init celery app",
        "code_block": INIT_CELERY_APP,
    },
    {
        "name": "Task sender",
        "code_block": TASK_SENDER,
    },
    {
        "name": "Kafka producer interface",
        "code_block": KAFKA_PRODUCER_INTERFACE,
    },
]
