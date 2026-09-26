from __future__ import annotations

from .models import ExecutionResult, ResultClass, ResultClassification


_UNREACHABLE_NETWORK_STATES = {
    "unreachable",
    "connection_refused",
    "connection_reset",
    "dns_failure",
    "offline",
}
_INPUT_REJECTION_STATUSES = {400, 405, 406, 409, 413, 415, 422}


def _classification(result_class: ResultClass, rationale: str, *fields: str) -> ResultClassification:
    return ResultClassification(result_class, rationale, tuple(fields))


def classify_result(result: ExecutionResult) -> ResultClassification:
    """Classify what happened without assigning hypothesis meaning."""
    if result.timed_out:
        return _classification(ResultClass.TIMEOUT, "Execution exceeded its timeout", "timed_out")

    if result.environment_available is False:
        return _classification(
            ResultClass.ENVIRONMENT_FAILURE,
            "Required execution environment is unavailable",
            "environment_available",
        )

    if result.tool_available is False:
        return _classification(
            ResultClass.TOOL_FAILURE, "Requested tool is unavailable", "tool_available"
        )

    if (result.network_state or "").lower() in _UNREACHABLE_NETWORK_STATES:
        return _classification(
            ResultClass.NETWORK_FAILURE,
            "The target could not be reached at the network layer",
            "network_state",
        )

    if result.http_status == 429:
        return _classification(ResultClass.RATE_LIMIT, "HTTP 429 rate limit", "http_status")
    if result.http_status == 401:
        return _classification(
            ResultClass.AUTH_FAILURE, "HTTP 401 authentication failure", "http_status"
        )
    if result.http_status == 403:
        return _classification(
            ResultClass.AUTHZ_FAILURE, "HTTP 403 authorization failure", "http_status"
        )
    if result.input_rejected or result.http_status in _INPUT_REJECTION_STATUSES:
        fields = ("input_rejected",) if result.input_rejected else ("http_status",)
        return _classification(ResultClass.INPUT_REJECTION, "Target rejected the input", *fields)

    if result.authoritative_success:
        return _classification(
            ResultClass.SUCCESS,
            "Execution metadata explicitly records authoritative success",
            "authoritative_success",
        )

    if result.state_changed:
        return _classification(
            ResultClass.STATE_CHANGE, "Execution changed relevant state", "state_changed"
        )

    if result.http_status is not None:
        return _classification(
            ResultClass.TARGET_RESPONSE,
            "Target returned an HTTP response",
            "http_status",
        )

    if result.exit_code is not None and result.exit_code != 0:
        return _classification(
            ResultClass.TOOL_FAILURE,
            "Tool process exited unsuccessfully without a more specific structured condition",
            "exit_code",
        )

    if result.exit_code == 0:
        return _classification(ResultClass.SUCCESS, "Tool process completed", "exit_code")

    return _classification(
        ResultClass.AMBIGUOUS,
        "Insufficient structured execution fields to classify the result",
    )
