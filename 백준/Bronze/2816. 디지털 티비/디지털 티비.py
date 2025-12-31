import sys
input = sys.stdin.readline

def main():
    try:
        line = input().strip()
        if not line: return
        N = int(line)
    except ValueError: return

    channels = []
    for _ in range(N):
        channels.append(input().strip())

    ans = []

    idx1 = channels.index('KBS1')
    ans.append('1' * idx1)
    ans.append('4' * idx1)

    kbs1 = channels.pop(idx1)
    channels.insert(0, kbs1)
    idx2 = channels.index('KBS2')
    
    ans.append('1' * idx2)
    ans.append('4' * (idx2 - 1))

    print(''.join(ans))
    
if __name__ == "__main__":
    main()