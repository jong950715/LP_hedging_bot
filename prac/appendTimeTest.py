import time
NUMBER_ = 10000

'''
미리 선언해놓는것과 append 간의 차이는 분명히 존재했다. (연산시간 포함해서 약 20%니 실질적으론느 50%이상 될수도?)
그러나 고작 많아야 10개 20개 될 때 유의미한 차이라고 보기는 힘들것 같다.
10000개는 넘어가야 신경써봄직한 최적화 인듯
'''

def funcPreMalloc(li):
    li[0] = 1

    for i in range(1, NUMBER_):
        if i%2:
            li[i] = (i*2 + li[i-1])
        else:
            li[i] = (i * 3)

    return li

def funcAppend():
    li = [1]

    for i in range(1, 10000):
        if i%2:
            li.append(i*2 + li[i-1])
        else:
            li.append(i * 3)

    return li

if __name__ == "__main__":
    start = time.time()  # 시작 시간 저장
    for _ in range(10000):
        l1 = funcAppend()
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

    inLi = [None] * NUMBER_
    start = time.time()  # 시작 시간 저장
    for _ in range(10000):
        l2 = funcPreMalloc(inLi)
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

    start = time.time()  # 시작 시간 저장
    for _ in range(10000):
        l1 = funcAppend()
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

    inLi = [None] * NUMBER_
    start = time.time()  # 시작 시간 저장
    for _ in range(10000):
        l2 = funcPreMalloc(inLi)
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간