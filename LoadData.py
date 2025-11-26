import re

def parse_dat_file(filename):
    with open(filename, "r") as f:
        content = f.read()

    # Remove comments like % this is a comment
    content = re.sub(r"%.*", "", content)

    # Find all assignments of the form: NAME = ...;
    # The .*? is non-greedy and DOTALL lets it span multiple lines
    assignments = re.findall(r"([A-Za-z]\w*)\s*=\s*(.*?);", content, re.DOTALL)

    data = {}

    for name, rhs in assignments:
        rhs = rhs.strip()

        # ---------- Scalar ----------
        if "[" not in rhs:
            # plain integer
            data[name] = int(rhs)
            continue

        # ---------- Vector / Matrix ----------
        # Strip a single pair of outer brackets if present
        if rhs[0] == "[" and rhs[-1] == "]":
            rhs_inner = rhs[1:-1].strip()
        else:
            rhs_inner = rhs

        rows = []
        for line in rhs_inner.splitlines():
            line = line.strip()
            if not line:
                continue

            # Remove inner [ ] on each row
            line = line.replace("[", "").replace("]", "").strip()
            if not line:
                continue

            nums = [int(x) for x in line.split()]
            rows.append(nums)

        # Vector vs matrix
        if len(rows) == 1:
            data[name] = rows[0]      # row vector
        else:
            data[name] = rows         # matrix

    return data
