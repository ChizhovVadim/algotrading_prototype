import queue


class ExitUserCmd:
    pass


class CheckStatusUserCmd:
    pass


class InitLimitsUserCmd:
    pass


class CloseAllUserCmd:
    pass


# потом можно прикрутить, чтобы команды не только из консоли, но например из телеграм бота.


def handle(inbox: queue.Queue):
    while True:
        user_input = input("")
        if not user_input:
            continue
        if user_input in ["quit", "exit"]:
            inbox.put(ExitUserCmd())
            return
        elif user_input == "status":
            inbox.put(CheckStatusUserCmd())
