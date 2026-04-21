"""In-memory Prometheus-compatible metrics collector.

Proper Prometheus text format exposition with # HELP and # TYPE directives.
One MetricsCollector instance per service, stored on app.state.metrics.
"""
from __future__ import annotations

import time
from typing import Any


class MetricsCollector:
    """Per-service metrics collector with valid Prometheus text format output."""

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        self._counters: dict[str, dict[str, Any]] = {}
        self._gauges: dict[str, dict[str, Any]] = {}
        self._histograms: dict[str, dict[str, Any]] = {}

    # ── Writers ───────────────────────────────────────────────────────────────

    def increment(
        self,
        name: str,
        value: int = 1,
        labels: dict[str, str] | None = None,
    ) -> None:
        key = self._key(name, labels)
        if key not in self._counters:
            self._counters[key] = {"name": name, "labels": labels or {}, "value": 0}
        self._counters[key]["value"] += value

    def gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        key = self._key(name, labels)
        self._gauges[key] = {"name": name, "labels": labels or {}, "value": value}

    def histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        key = self._key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = {"name": name, "labels": labels or {}, "values": []}
        self._histograms[key]["values"].append(value)

    def observe_duration(
        self,
        name: str,
        start_time: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record elapsed time since start_time (from time.perf_counter())."""
        self.histogram(name, time.perf_counter() - start_time, labels)

    # ── Exposition ────────────────────────────────────────────────────────────

    def expose_prometheus(self) -> str:
        """Expose all metrics in valid Prometheus text format (0.0.4)."""
        lines: list[str] = []
        svc = self.service_name

        for meta in self._counters.values():
            metric = f"{svc}_{meta['name']}_total"
            label_str = self._fmt_labels(meta["labels"])
            lines += [
                f"# HELP {metric} Total count of {meta['name']}",
                f"# TYPE {metric} counter",
                f"{metric}{label_str} {meta['value']}",
            ]

        for meta in self._gauges.values():
            metric = f"{svc}_{meta['name']}"
            label_str = self._fmt_labels(meta["labels"])
            lines += [
                f"# HELP {metric} Current value of {meta['name']}",
                f"# TYPE {metric} gauge",
                f"{metric}{label_str} {meta['value']}",
            ]

        for meta in self._histograms.values():
            metric = f"{svc}_{meta['name']}"
            label_str = self._fmt_labels(meta["labels"])
            values: list[float] = meta["values"]
            total = sum(values)
            count = len(values)
            lines += [
                f"# HELP {metric} Histogram of {meta['name']}",
                f"# TYPE {metric} histogram",
                f'{metric}_bucket{{{self._fmt_labels_inner(meta["labels"])}le="+Inf"}} {count}',
                f"{metric}_sum{label_str} {total}",
                f"{metric}_count{label_str} {count}",
            ]

        return "\n".join(lines)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _key(self, name: str, labels: dict[str, str] | None) -> str:
        if labels:
            return f"{name},{','.join(f'{k}={v}' for k, v in sorted(labels.items()))}"
        return name

    def _fmt_labels(self, labels: dict[str, str]) -> str:
        if not labels:
            return ""
        pairs = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{{{pairs}}}"

    def _fmt_labels_inner(self, labels: dict[str, str]) -> str:
        """For injecting into existing label set (adds trailing comma)."""
        if not labels:
            return ""
        pairs = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{pairs},"
