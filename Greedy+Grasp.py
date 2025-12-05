from LoadData import parse_dat_file
import random
from helperFuncs import (
    cameraCoverage,             # gives squares coverd for each model for each position
    TimeModel,                  # for each camera all possible on/off configurations
    coveredBySolution,          # given a solution outputs all touples (day,square) which are coverd 
    uncoveredBySolution,        # basically same as above but gives the not coverd touples
    cost,                       # given a solution outputs total_cost (buy price + operation cost)
)

File = "Data/gen2.dat"
data = parse_dat_file(File)





def LocalSearch_Replace(initial_solution,
                        data_set,
                        max_iterations=10,
                        coverage = None,
                        patterns_per_model = None
                        ):
    
    ### precompute coverage and patterns per model to speed up local search
    if coverage is None:
        coverage = cameraCoverage(data_set)
    if patterns_per_model is None:
        patterns_per_model = [TimeModel(k, data_set) for k in range(data_set["K"])]
    ### precompute coverage and patterns per model to speed up local search


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
                    input_uncovered=Uncovered,
                    input_solution=partial_solution,
                    coverage=coverage,                      # precomputed coverage to speed up
                    patterns_per_model=patterns_per_model   # precomputed patterns per model to speed up
                )

            candidate_cost = cost(candidate_solution, data_set)

            if candidate_cost < best_cost:
                best_solution = candidate_solution
                best_cost = candidate_cost
                improved = True
                break           ## if better solution found repeat replacement with new solution 

    return best_solution, best_cost





def Greedy(data_set, 
           input_uncovered =None,
           input_solution = None,
           coverage = None,                 ## precomputed coverage to speed up
           patterns_per_model = None):     ## precomputed patterns per model to speed up
    

    K = data_set["K"]
    N = data_set["N"]
    P = data_set["P"]
    C = data_set["C"]

    if coverage is None:
        coverage = cameraCoverage(data_set)
    if patterns_per_model is None:
        patterns_per_model = [TimeModel(k, data_set) for k in range(K)]

    # if already given soltion load the solution
    if input_uncovered is None:
        Uncovered= {(d, j) for d in range(7) for j in range(N)}
    else:
        Uncovered = set(input_uncovered)

    installed_positions= set()  
    solution  = []

    
    if input_solution is not None:
        solution.extend(input_solution)

        for k_fix, n_fix, pattern_fix in input_solution:
            installed_positions.add(n_fix)

        already_covered = coveredBySolution(input_solution, data_set)
        Uncovered -= already_covered


    while Uncovered:
        best_ratio = None
        best_choice = None      
        best_newly = set()

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

                  
                    Newly = set()
                    for d in range(7):  # for every day check which new squares covered
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


def GreedyRandomized (  data_set, 
                        alpha, 
                        coverage = None,
                        patterns_per_model = None,
                        input_uncovered =None,
                        input_solution = None):

    K = data_set["K"]
    N = data_set["N"]
    P = data_set["P"]
    C = data_set["C"]

    if coverage is None:
        coverage = cameraCoverage(data_set)
    if patterns_per_model is None:
        patterns_per_model = [TimeModel(k, data_set) for k in range(K)]

    if input_uncovered is None:
        Uncovered= {(d, j) for d in range(7) for j in range(N)}
    else:
        Uncovered = set(input_uncovered)

    installed_positions= set()  
    solution  = []

    if input_solution is not None:
        solution.extend(input_solution)

        for k_fix, n_fix, pattern_fix in input_solution:
            installed_positions.add(n_fix)

        already_covered = coveredBySolution(input_solution, data_set)
        Uncovered -= already_covered

    while Uncovered:
        candidate_list = []

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

                    Newly = set()
                    for d in range(7):  # for every day check which new squares covered
                        if pattern[d] == 0:
                            continue
                        for j in squares_seen:
                            pair = (d, j)
                            if pair in Uncovered:
                                Newly.add(pair)

                    if not Newly:
                        continue

                    ratio = weekly_cost / len(Newly)  # ratio cost to new squares day pairs coverd

                    candidate_list.append( (ratio, (k, n, pattern), Newly) )

        if not candidate_list:     #if no camera has any -> means no camera can cover any new ones -> infeasable end function
            break

        candidate_list.sort(key=lambda x: x[0])  # sort by ratio

        # determine threshold for RCL
        rcl_threshold = candidate_list[0][0] + alpha * (candidate_list[-1][0] - candidate_list[0][0])

        # build RCL
        RCL = [item for item in candidate_list if item[0] <= rcl_threshold]

        # select randomly from RCL
        selected = random.choice(RCL)
        _, best_choice, best_newly = selected

        k_best, n_best, pattern_best = best_choice 
        solution.append((k_best, n_best, pattern_best))         #add camera placment and on days to solution
        installed_positions.add(n_best)                         #mark square as used 
        Uncovered -= best_newly                                 #update uncoverd
    



    return solution


def Grasp(data_set, alpha, grasp_iterations = 20,ls_max_iterations = 10, coverage = None, patterns_per_model = None):
    ### GRASP metaheuristic
    ### combines greedy randomized construction with local search
    ### returns best solution found
    # to be implemented

    K = data_set["K"]
    N = data_set["N"]
    P = data_set["P"]
    C = data_set["C"]

    if coverage is None:
        coverage = cameraCoverage(data_set)
    if patterns_per_model is None:
        patterns_per_model = [TimeModel(k, data_set) for k in range(K)]

    best_solution = None
    best_cost = +float('inf')

    for iteration in range(grasp_iterations):  # number of iterations can be parameterized
        randomSolution = GreedyRandomized(data_set, alpha, coverage, patterns_per_model)
        sol, sol_cost= LocalSearch_Replace(randomSolution, data_set, max_iterations=ls_max_iterations,coverage=coverage, patterns_per_model=patterns_per_model)
        #sol_cost = cost(sol, data_set)

        if sol_cost < best_cost:
            best_solution = sol
            best_cost = sol_cost


    return best_solution, best_cost



if __name__ == "__main__": ## for testing purpose 

    greedySol = (Greedy(data))
    greedyCost = cost(greedySol, data)
    

    print("=== GRASP ===")
    best_sol, best_cost = Grasp(data, alpha=0, grasp_iterations=1)
    print("Best GRASP cost:", best_cost)
    print("Best GRASP solution:", best_sol)

    print("=== GREEDY ===")
    print("Greedy cost:", greedyCost)
    print("Greedy solution:", greedySol)

    print("=== LOCAL SEARCH on GREEDY ===")
    ls_sol, ls_cost = LocalSearch_Replace(greedySol, data, max_iterations=10)
    print("Local Search cost:", ls_cost)
    print("Local Search solution:", ls_sol)

