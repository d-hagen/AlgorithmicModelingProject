from typing import Set, List, Tuple
from LoadData import parse_dat_file
from helperFuncs import (
    cameraCoverage,
    TimeModel,
    coverdBySolution,
    uncoveredBySolution,
    cost,
)

File = "Data/project.2.dat"
data = parse_dat_file(File)




def LocalSearch_Replace(initial_solution,
                        data_set,
                        max_iterations=10):

    best_solution = initial_solution[:]
    best_cost = cost(best_solution, data_set)

    iteration = 0
    improved = True

    while improved and iteration < max_iterations: ## if no replacement yields better solution stop local search
        improved = False
        iteration += 1

        for i in range(len(best_solution)):      ## replaces 1st , 2nd ...nth camera until a solution is better then old
            partial_solution = best_solution[:i] + best_solution[i+1:]

            Uncovered = uncoveredBySolution(partial_solution, data_set)

            if not Uncovered:
                candidate_solution = partial_solution
            else:
                print("Iteration " + str(iteration) + "------------------------------")
                candidate_solution = Greedy(   ##build new solution based on old solution + missing camera 
                    data_set,
                    input_uncoverd=Uncovered,
                    input_solution=partial_solution
                )

            candidate_cost = cost(candidate_solution, data_set)

            if candidate_cost < best_cost:
                best_solution = candidate_solution
                best_cost = candidate_cost
                improved = True
                break           ## if better solution found repeat replacement with new solution 

    return best_solution, best_cost





def Greedy(data_set, input_uncoverd =None,
           input_solution = None):
    K = data_set["K"]
    N = data_set["N"]
    P = data_set["P"]
    C = data_set["C"]

    coverage = cameraCoverage(data_set)
    patterns_per_model = [TimeModel(k, data_set) for k in range(K)]
    # if already given soltion load the solution
    if input_uncoverd is None:
        Uncovered: Set[Tuple[int, int]] = {(d, j) for d in range(7) for j in range(N)}
    else:
        Uncovered: Set[Tuple[int, int]] = set(input_uncoverd)

    installed_positions: Set[int] = set()  
    solution: List[Tuple[int, int, List[int]]] = []

    
    if input_solution is not None:
        solution.extend(input_solution)

        for k_fix, n_fix, pattern_fix in input_solution:
            installed_positions.add(n_fix)

        already_covered = coverdBySolution(input_solution, data_set)
        Uncovered -= already_covered


    while Uncovered:
        best_ratio = None
        best_choice = None      
        best_newly: Set[Tuple[int, int]] = set()

        # go through all camera models and all squares 
        for k in range(K):
            for n in range(N):
                if n in installed_positions:
                    continue 

                squares_seen = coverage[k][n]
                if not squares_seen:
                    continue

                for pattern in patterns_per_model[k]:
                    days_on = sum(pattern)
                    if days_on == 0:
                        continue

                    weekly_cost = P[k] + C[k] * days_on 

                  
                    Newly: Set[Tuple[int, int]] = set()
                    for d in range(7):  # for every day check which new swquares coverd
                        if pattern[d] == 0:
                            continue
                        for j in squares_seen:
                            pair = (d, j)
                            if pair in Uncovered:
                                Newly.add(pair)

                    if not Newly:
                        continue

                    ratio = weekly_cost / len(Newly)  # ratio cost to new squares day pairs coverd

                    #this is the greddy function minimize cost of camera operated and inital buy price to how much 
                    #it covers in total(think of it as: each day a squae is a new square 
                    #(so if it covers square 1 for 3 days -> 3 squares coverd)
                    #So min(price/total squares coverd) 
                    #-> similar to computer it does the best for current camera with out considering what might come next
                    if best_ratio is None or ratio < best_ratio: #for all possible patterns take best newcoverd to price
                        best_ratio = ratio #update current best ratio(for checked patterns )
                        best_choice = (k, n, pattern) #update best placement and pattern
                        best_newly = Newly 

        if best_choice is None:     #if no camera has any -> means no camera can cover any new ones -> infeasable end function
            break

        k_best, n_best, pattern_best = best_choice 
        solution.append((k_best, n_best, pattern_best)) #add camera placment and on days to solution
        installed_positions.add(n_best) #mark square as used 
        Uncovered -= best_newly     #update uncoverd 

    print("Remaining uncovered (day, square) pairs:", len(Uncovered))
    print("Solution (model, position, pattern):")
    for cam in solution: 
        print(cam) 

    total_price = cost(solution, data_set)
    

    print("Total weekly cost:", total_price)
    return solution


A = (Greedy(data))
print(A)
print(LocalSearch_Replace(A, data))
