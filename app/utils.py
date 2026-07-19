def parse_command(command : str) -> list:
    index , length = 0, len(command)
    result = []
    arg = ''
    isSpace = False

    while index < length:
        if command[index].isalnum() or command[index] in ['-', '_', '.', '/', '~']:
            arg += command[index]
            index += 1
            continue
        
        if command[index] == ' ':
            if arg:
                result.append(arg)
                arg = ''
            index += 1
            continue

        if command[index] == '\\':
            index += 1
            if index < length:
                arg += command[index]
                index += 1
            continue

        if command[index] in ['"', "'"]:
            quote_char = command[index]
            index += 1
            while index < length and command[index] != quote_char:
                arg += command[index]
                index += 1

        index+=1
    if arg:
        result.append(arg)
    return result
    # return ' '.join(result)
