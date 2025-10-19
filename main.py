from train import TrainSimulationConsole, TrainPantographSimulation


if __name__ == "__main__":
    print("Choisissez le mode de simulation:")
    print("1. Interface graphique (recommandé)")
    print("2. Mode console")

    choice = input("Votre choix (1 ou 2): ").strip()

    if choice == "2":
        sim = TrainSimulationConsole()
        sim.run_simulation()
    else:
        print("Lancement de l'interface graphique...")
        sim = TrainPantographSimulation()
        sim.run()