import sys
input = sys.stdin.readline

def classify_triangle(sides: list[int]) -> None:
    """
    세 변의 길이를 받아 삼각형의 종류를 출력하는 함수
    Args:
        sides (List[int]): 세 변의 길이가 담긴 리스트
    """
    
    # 삼각형 성립 조건 확인: 가장 긴 변 < 나머지 두 변의 합
    max_len = max(sides)
    if max_len >= sum(sides) - max_len:
        print("Invalid")
        return

    # 변의 길이 종류 수로 판별
    unique_count = len(set(sides))

    if unique_count == 1:
        print("Equilateral")
    elif unique_count == 2:
        print("Isosceles")
    else:
        print("Scalene")

def main():
    while True:
        try:
            line = input().split()
            if not line: 
                break
                
            sides = list(map(int, line))
            
            if sum(sides) == 0:
                break
                
            classify_triangle(sides)
            
        except ValueError:
            break

if __name__ == "__main__":
    main()