from sys import stdin

def is_partition_possible(values,sum):
    l = [i for i in range(sum + 1)]
    b = [j for j in range(sum + 1)]
    d = [k for k in range(len(values)+1)]

    dp = {(i,j,k):0 for i in l for j in b for k in d}

    dp[(0,0,0)] = 1
    for i in l[1:]:
        for j in b[1:]:
            dp[(i,j,0)] = 0

    for k in d[1:]:
        item = values[k-1]
        for i in l:
            for j in b:
                if i < item and j < item:
                    dp[(i, j, k)] = dp[(i, j, k - 1)]
                elif i < item and j >= item:
                    dp[(i, j, k)] = dp[(i, j, k - 1)] or dp[(i, j - item, k - 1)]
                elif i >= item and j < item:
                    dp[(i, j, k)] = dp[(i, j, k - 1)] or dp[(i - item, j, k - 1)]
                else:
                    dp[(i, j, k)] = dp[(i, j, k - 1)] or dp[(i - item, j, k - 1)] or dp[(i, j - item, k - 1)]

    return dp[(len(l)-1,len(b)-1,len(d)-1)]


def partition3(values):
    if sum(values) % 3 != 0:
        return 0
    else:
        subsetsum = int(sum(values) / 3)
        return is_partition_possible(values, subsetsum)


if __name__ == '__main__':
    input_n, *input_values = list(map(int, stdin.read().split()))
    assert input_n == len(input_values)
    print(partition3(input_values))
