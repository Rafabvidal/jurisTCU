from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    print(f"Exception: {exc}")
    print(f"Context: {context}")

    return response
