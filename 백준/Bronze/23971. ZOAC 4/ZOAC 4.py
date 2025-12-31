import sys
input = sys.stdin.readline
H, W, N, M = map(int, input().split())
N = N + 1
M = M + 1
x = (H + N - 1) // N
y = (W + M - 1) // M
print(x * y)