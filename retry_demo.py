from reliable_AI_app import call_with_retry


class FakeServerError(Exception):
    code = 503


attempts = {"count": 0}


def flaky_task():
    attempts["count"] += 1
    if attempts["count"] < 3:
        raise FakeServerError("Server overloaded")
    return "Success!"


print(call_with_retry(flaky_task))