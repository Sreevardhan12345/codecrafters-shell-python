import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while( True):
        command = input("$ ")
        if command == "exit":
            sys.exit(0)
        elif command.startswith("echo "):
            sys.stdout.write( command[5:] + "\n")
        sys.stdout.write(f"{command}: command not found\n")
    pass


if __name__ == "__main__":
    main()
