#Gives for all cameras how many squares they cover at each square 
def cameraCoverage(data_set):
    K = data_set["K"]
    N = data_set["N"]
    R = data_set["R"]
    M = data_set["M"]  

    coverage = [[set() for _ in range(N)] for _ in range(K)]
    for k in range(K):
        for n in range(N):
            for j, dist in enumerate(M[n]):
                if dist <= R[k]:
                    coverage[k][n].add(j)

    return coverage

def cost(solution, data_set):
    P = data_set["P"]
    C = data_set["C"]

    total_price = 0
    for k, n, pattern in solution:
        days_on = sum(pattern)
        total_price += P[k]            # purchase cost
        total_price += C[k] * days_on  # energy cost over the week

    return total_price


def coverdBySolution(solution, data_set):
        coverage = cameraCoverage(data_set)
        coverd: Set[Tuple[int, int]] = set() 
        for k, n, pattern in solution:
            visible_squares = coverage[k][n]
            for d in range(7):
                if pattern[d] == 0:
                    continue
                for s in visible_squares:
                    coverd.add((d, s))
        return coverd

        
def uncoveredBySolution(solution, data_set):
    coverd = coverdBySolution(solution, data_set)
    uncoverd: Set[Tuple[int, int]] = set() 
    for d in range(7):
        for n in range(data_set["N"]):
            if (d,n) not in coverd:
                uncoverd.add((d, n))
    return uncoverd



##creates all possible on day combinations for a given camera
def TimeModel(k, data_set):   
    A = data_set["A"][k]
    patterns = []

    for mask in range(1, 1 << 7):  
        pattern = [(mask >> d) & 1 for d in range(7)]
        total_on = sum(pattern)
        if total_on < 2:
            continue  

        if total_on == 7:
            runs = [7]  
        else:
            try:
                i0 = next(i for i in range(7) if pattern[i] == 0)
            except StopIteration:
                continue

            runs = []
            count = 0
            for t in range(7):
                i = (i0 + 1 + t) % 7
                if pattern[i] == 1:
                    count += 1
                else:
                    if count > 0:
                        runs.append(count)
                        count = 0
            if count > 0:
                runs.append(count)

        if not runs:
            continue
        if not all(2 <= r <= A for r in runs):
            continue

        patterns.append(pattern)

    # Deduplicate
    unique_patterns = [list(p) for p in set(tuple(p) for p in patterns)] #remove duplicates 
    return unique_patterns


