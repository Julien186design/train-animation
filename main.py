from train import TrainSimulationConsole, TrainPantographSimulation


if __name__ == "__main__":
    print("Choose the simulation mode:")
    print("1. Graphical interface (recommended)")
    print("2. Console mode")

    choice = input("Your choice (1 or 2): ").strip()

    if choice == "2":
        sim = TrainSimulationConsole()
        sim.run_simulation()
    else:
        print("Launching the graphical interface...")
        sim = TrainPantographSimulation()
        sim.run()
