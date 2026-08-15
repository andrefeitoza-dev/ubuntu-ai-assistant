from ubuntu_ai.autonomy.task_queue import AutonomousTask, TaskQueue


def test_task_queue_prioritizes_higher_priority() -> None:
    queue = TaskQueue()
    queue.push(
        AutonomousTask(
            task_id="low",
            goal_id="g",
            payload=None,
            priority=10,
        )
    )
    queue.push(
        AutonomousTask(
            task_id="high",
            goal_id="g",
            payload=None,
            priority=100,
        )
    )

    assert queue.pop().task_id == "high"
