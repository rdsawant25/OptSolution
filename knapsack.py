from sys import stdin


def maximum_gold(capacity, weights):
    col = [j for j in range(capacity+1)]
    row = {i:[0 for j in col] for i in range(len(weights))}

    for i in row:
        item_wgt = weights[i]
        item_val = weights[i]
        if i == 0:
            for j in col:
                if j < item_wgt:
                    row[i][j] = 0
                else:
                    row[i][j] = item_val
            continue
        for j in col:
            if j == 0:
                row[i][0] = 0
                continue

            if j < item_wgt:
                not_sel_item = row[i-1][j]
                row[i][j] = not_sel_item
            else:
                not_sel_item = row[i - 1][j]
                sel_item = row[i-1][j-item_wgt] + item_val

                row[i][j] = max(not_sel_item,sel_item)

    return row[i][-1]
    # assert False


if __name__ == '__main__':
    input_capacity, n, *input_weights = list(map(int, stdin.read().split()))
    assert len(input_weights) == n

    print(maximum_gold(input_capacity, input_weights))