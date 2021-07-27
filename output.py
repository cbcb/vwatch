from colorama import Fore, Style, init  # , Back


init()


def repo(string: str):
    string = string.replace("/", f"/{Style.BRIGHT}")
    return f'{Fore.YELLOW}{string}{Style.RESET_ALL}'


def ver(string: str):
    return f'{Style.BRIGHT}{Fore.BLUE}{string}{Style.RESET_ALL}'


def desc(string: str):
    return f'{Fore.CYAN}{string}{Style.RESET_ALL}'


def url(string: str):
    return f'{Fore.BLUE}{string}{Style.RESET_ALL}'


def good(string: str):
    return f'{Style.BRIGHT}{Fore.GREEN}{string}{Style.RESET_ALL}'


def bad(old: str, new: str = None):
    if new is None:
        return f'{Style.BRIGHT}{Fore.RED}{old}{Style.RESET_ALL}'
    return f'{Style.BRIGHT}{Fore.RED}{old}{Style.RESET_ALL} → {ver(new)}'


def bracketed(string: str):
    return (
        f'{Style.BRIGHT}{Fore.BLUE}[{Style.RESET_ALL}'
        f'{string}'
        f'{Style.BRIGHT}{Fore.BLUE}]{Style.RESET_ALL}'
           )


def bold(string: str):
    return f'{Style.BRIGHT}{string}{Style.RESET_ALL}'
