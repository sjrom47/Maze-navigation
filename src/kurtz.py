from labyrinth import LogicalMaze, BayesianMaze

if __name__ == "__main__":
    option = input("Enter which maze you want to try: B (Bayesian) or L (Logical) ")
    while option not in ["B", "b", "L", "l"]:
        option = input("Enter which maze you want to try: B (Bayesian) or L (Logical)")
    auto = input("Do you want it to run automatically? ")
    while auto not in ["Yes", "yes", "No", "no"]:
        auto = input("Do you want it to run automatically? ")
    auto = auto in ["Yes", "yes"]
    if option not in ["B", "b"]:
        LogicalMaze(auto=auto)
    else:
        BayesianMaze(auto=auto)
