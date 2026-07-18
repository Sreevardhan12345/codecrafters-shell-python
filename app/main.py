import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while( True):
        command = input("$ ")
        sys.stdout.write(f"{command}: command not found\n")
    pass


if __name__ == "__main__":
    main()
