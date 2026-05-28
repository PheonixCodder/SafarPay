from __future__ import annotations

import pytest

from sp.infrastructure.messaging import kafka as kafka_module


class _FakeAdminClient:
    instances: list[_FakeAdminClient] = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.created_topics = []
        self.closed = False
        _FakeAdminClient.instances.append(self)

    def create_topics(self, new_topics, validate_only: bool = False) -> None:
        self.created_topics.extend(new_topics)
        self.validate_only = validate_only

    def close(self) -> None:
        self.closed = True


class _FakeTopic:
    def __init__(self, name: str, num_partitions: int, replication_factor: int) -> None:
        self.name = name
        self.num_partitions = num_partitions
        self.replication_factor = replication_factor


@pytest.mark.asyncio
async def test_ensure_kafka_topics_creates_topics_before_consumers_subscribe(monkeypatch) -> None:
    _FakeAdminClient.instances.clear()
    monkeypatch.setattr(kafka_module, "KAFKA_AVAILABLE", True)
    monkeypatch.setattr(kafka_module, "KafkaAdminClient", _FakeAdminClient, raising=False)
    monkeypatch.setattr(kafka_module, "NewTopic", _FakeTopic, raising=False)

    created = await kafka_module.ensure_kafka_topics(
        "kafka:9092",
        ["ride-events", "bidding-events"],
        client_id="notification-topic-admin",
    )

    admin = _FakeAdminClient.instances[0]
    assert created is True
    assert admin.kwargs["bootstrap_servers"] == "kafka:9092"
    assert admin.kwargs["client_id"] == "notification-topic-admin"
    assert [topic.name for topic in admin.created_topics] == ["ride-events", "bidding-events"]
    assert admin.closed is True
