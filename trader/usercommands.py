import queue


class ExitUserCmd:
    pass


class CheckStatusUserCmd:
    pass


class InitLimitsUserCmd:
    pass


class CloseAllUserCmd:
    '''Закрыть все позиции.
    Например, перед экспирацией, длинными выходными/праздниками'''
    pass


# потом можно прикрутить, чтобы команды не только из консоли, но например из телеграм бота.
def handle(messages: queue.Queue):
    while True:
        user_input = input("")
        cmd = _parse(user_input)
        if cmd is None:
            continue
        messages.put(cmd)
        if isinstance(cmd, ExitUserCmd):
            return


def _parse(commandLine: str):
    if commandLine in ["quit", "exit"]:
        return ExitUserCmd()
    if commandLine == "status":
        return CheckStatusUserCmd()
    if commandLine == "initlimits":
        return InitLimitsUserCmd()
    if commandLine == "closeall":
        return CloseAllUserCmd()
    return None
