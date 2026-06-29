"""
Taskiq 주기 작업 스케줄. 설계서 8장 표 대응.

scheduler 실행: taskiq scheduler app.workers.taskiq_app:scheduler
"""
from taskiq.schedule_sources import LabelScheduleSource
from taskiq import TaskiqScheduler

from app.workers.taskiq_app import broker

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
