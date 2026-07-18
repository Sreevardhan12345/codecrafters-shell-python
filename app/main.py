import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while( True):
        command = input("$ ")
        if command == "exit":
            sys.exit(0)
        elif command.startswith("echo "):
            sys.stdout.write( command[5:] + "\n")
        elif command == "type":
            cmdLets = command.split()
            if len(cmdLets) > 1:
                if cmdLets[1] in ["echo", "type", "exit"]:
                    sys.stdout.write(f"{cmdLets[1]} is a shell builtin\n")
                sys.stdout.write(f"{cmdLets[1]} is /usr/bin/{cmdLets[1]}\n")
            else:
                sys.stdout.write("type: missing operand\n")
        else:
            sys.stdout.write(f"{command}: command not found\n")
    pass


if __name__ == "__main__":
    main()
