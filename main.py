
import sys


def main():
    print("Hello World")
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")


if __name__ == '__main__':
    main()
