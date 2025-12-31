import sys
input = sys.stdin.readline

def main():
    remainer = int(input()) - 1
    i = 0

    while True:
        remainer -= (6*i)
        i += 1
        if remainer <= 0:
            break
    print(i)
    
if __name__ == "__main__":
    main()