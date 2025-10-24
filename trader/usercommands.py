
class ExitUserCmd:
    pass


class CheckStatusUserCmd:
    pass

# потом можно прикрутить, чтобы команды не только из консоли, но например из телеграм бота.


def handle(queue):
    while True:
        user_input = input("")
        cmd = _parse(user_input)
        if cmd is None:
            continue
        queue.put(cmd)
        if isinstance(cmd, ExitUserCmd):
            return


def _parse(commandLine: str):
    if commandLine in ["quit", "exit"]:
        return ExitUserCmd()
    if commandLine == "status":
        return CheckStatusUserCmd()
    return None
