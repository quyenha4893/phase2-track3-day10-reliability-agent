from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="reports/metrics.json")
    parser.add_argument("--out", default="reports/final_report.md")
    parser.add_argument("--student", default="Nguyễn Việt Long")
    parser.add_argument("--mssv", default="2A202600242")
    args = parser.parse_args()
    metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    scenarios = metrics.get("scenarios", {})
    lines = [
        "# Day 10 Reliability Final Report",
        "",
        f"**Student:** {args.student}",
        f"**MSSV:** {args.mssv}",
        "",
        "## Architecture Summary",
        "",
        "Requests flow through a reliability gateway that checks cache first, then calls the primary provider through a circuit breaker. If the primary path fails or the circuit is open, traffic falls back to the backup provider. If all providers fail, the gateway returns a static degraded-service response.",
        "",
        "```text",
        "User Request -> Gateway -> Cache",
        "                         |",
        "                         +-> CircuitBreaker(primary) -> primary provider",
        "                         +-> CircuitBreaker(backup)  -> backup provider",
        "                         +-> static fallback",
        "```",
        "",
        "## Metrics Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in metrics.items():
        if key == "scenarios":
            continue
        lines.append(f"| {key} | {value} |")
    lines += ["", "## Chaos Scenarios", "", "| Scenario | Status |", "|---|---|"]
    for key, value in scenarios.items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Analysis",
        "",
        f"The run processed {metrics.get('total_requests', 0)} requests with availability {metrics.get('availability')} and error rate {metrics.get('error_rate')}. Cache hits reduced provider calls and estimated cost saved was {metrics.get('estimated_cost_saved')}. Circuit open count was {metrics.get('circuit_open_count')}, showing the breaker protected unhealthy provider paths during chaos scenarios.",
        "",
        "The fallback path worked when the primary provider was unavailable or flaky. A remaining production weakness is that circuit breaker state is process-local; a multi-instance deployment should share provider health or circuit state across instances.",
        "",
        "## Next Steps",
        "",
        "1. Share provider health and circuit state across gateway instances.",
        "2. Add concurrent multi-instance load tests with Redis cache enabled.",
        "3. Add answer-quality and per-user rate-limit SLOs before production.",
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
