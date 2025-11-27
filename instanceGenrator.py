import random



## standart restrictions
maxRange   = 50
maxPrice   = 100
maxOpPrice = 20
maxDistance = 51


# problem size 
NumberOfCam     = 20
NumberOfsquares = 400

#output file
file = "Data/gen1.dat"



def generate(K, N, filename):
    P = []
    R = []
    A = []
    C = []
    M = [[0]*N for i in range(N)]
    for k in range(K):
        R.append(random.randint(1,maxRange))
        P.append(random.randint(1,maxPrice))
        A.append(random.randint(2,8))
        C.append(random.randint(1,maxOpPrice))

    for n in range(N):
        for n2 in range(n,N):
            if (n == n2):
                M[n][n2] = 0 
            else: 
                value = random.randint(1, maxDistance)
                M[n][n2] = value
                M[n2][n] = value

    with open(filename, "w") as f:
        # Write K
        f.write(f"K = {K};\n\n")

        # Write vectors
        f.write("P = [ " + " ".join(map(str, P)) + " ];\n")
        f.write("R = [ " + " ".join(map(str, R)) + " ];\n")
        f.write("A = [ " + " ".join(map(str, A)) + " ];\n")
        f.write("C = [ " + " ".join(map(str, C)) + " ];\n\n")

        # Write N
        f.write(f"N = {N};\n\n")

        # Write matrix M
        f.write("M = [\n")
        for row in M:
            row_str = "   " + "  ".join(f"{val:3}" for val in row)
            f.write(f"    [ {row_str} ]\n")
        f.write("];\n")


generate(NumberOfCam,NumberOfsquares, file )