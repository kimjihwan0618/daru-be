"""
Taskiq 브로커/스케줄러 설정.

Worker 실행:
    taskiq worker app.workers.taskiq_app:broker

Scheduler 실행 (주기 작업):
    taskiq scheduler app.workers.taskiq_app:scheduler
"""
from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.config import settings

broker = ListQueueBroker(settings.REDIS_URL).with_result_backend(
    RedisAsyncResultBackend(settings.REDIS_URL)
)

scheduler = TaskiqScheduler(broker=broker, sources=[])
