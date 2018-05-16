protocols = [
    'ipfs',
    'https',
    'ftp',
]


def clean_address(protocol, address):
    if address is None:
        return

    if protocol == 'ipfs':
        address = address.replace('/ipfs/', '')
    elif protocol == 'https':
        address = address.replace('https://', '')
    elif protocol == 'ftp':
        address = address.replace('ftp://', '')
    return address


def clean_arguments(args):
    new_args = {}
    for key, value in args.items():
        key = key.replace('--', '')
        key = key.replace('<', '')
        key = key.replace('>', '')
        key = key.replace('-', '_')

        if value is None and new_args.get(key) is not None:
            continue

        if key in protocols:
            new_args[key] = clean_address(key, value)
        else:
            new_args[key] = value
    return new_args


def select_command(args, _commands):
    for command_name, command in _commands.items():
        if args.get(command_name):
            return command
    return _commands.get('default')
