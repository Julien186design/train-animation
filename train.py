import tkinter as tk
from tkinter import ttk
import time
import threading

class TrainPantographSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulation Changement Pantographes Train")
        self.root.geometry("1000x600")
        self.root.configure(bg='lightblue')

        # Variables d'état
        self.train_position = 0
        self.pantograph_1500v_angle = 0  # 0 = levé, 90 = baissé
        self.pantograph_25kv_angle = 90  # 90 = baissé, 0 = levé
        self.system_1500v_active = True
        self.system_25kv_active = False
        self.animation_running = False
        self.current_phase = "Attente"

        self.setup_gui()

    def setup_gui(self):
        # Canvas principal
        self.canvas = tk.Canvas(self.root, width=900, height=400, bg='lightgreen')
        self.canvas.pack(pady=20)

        # Panel d'informations
        info_frame = ttk.Frame(self.root)
        info_frame.pack(pady=10)

        ttk.Label(info_frame, text="État des Systèmes:", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2)

        ttk.Label(info_frame, text="1500V DC:").grid(row=1, column=0, sticky='w')
        self.status_1500v = ttk.Label(info_frame, text="ACTIF", foreground='green', font=('Arial', 10, 'bold'))
        self.status_1500v.grid(row=1, column=1, sticky='w')

        ttk.Label(info_frame, text="25kV AC:").grid(row=2, column=0, sticky='w')
        self.status_25kv = ttk.Label(info_frame, text="INACTIF", foreground='red', font=('Arial', 10, 'bold'))
        self.status_25kv.grid(row=2, column=1, sticky='w')

        ttk.Label(info_frame, text="Phase:").grid(row=3, column=0, sticky='w')
        self.phase_label = ttk.Label(info_frame, text=self.current_phase, font=('Arial', 10))
        self.phase_label.grid(row=3, column=1, sticky='w')

        # Boutons de contrôle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_btn = ttk.Button(control_frame, text="Démarrer Animation", command=self.start_animation)
        self.start_btn.pack(side='left', padx=5)

        self.reset_btn = ttk.Button(control_frame, text="Reset", command=self.reset_simulation)
        self.reset_btn.pack(side='left', padx=5)

        # Marquer que le fond n'est pas encore dessiné
        self.background_drawn = False

        # Dessiner la scène initiale
        self.draw_scene()

    def draw_scene(self):
        # Ne redessiner que si nécessaire pour éviter le clignotement
        self.canvas.delete("train", "pantograph", "sparks")

        # Dessiner les éléments fixes seulement une fois
        if not hasattr(self, 'background_drawn'):
            self.draw_background()
            self.background_drawn = True

        # Train (avec tag pour pouvoir l'effacer)
        self.draw_train()

    def draw_background(self):
        """Dessine les éléments fixes du décor"""
        # Caténaires
        # 1500V (gauche)
        self.canvas.create_line(50, 80, 450, 80, fill='gold', width=4, tags="background")
        self.canvas.create_text(250, 60, text="1500V DC", fill='darkgoldenrod', font=('Arial', 12, 'bold'),
                                tags="background")

        # 25kV (droite)
        self.canvas.create_line(450, 75, 850, 75, fill='orangered', width=5, tags="background")
        self.canvas.create_text(650, 55, text="25kV AC", fill='darkred', font=('Arial', 12, 'bold'), tags="background")

        # Rails
        self.canvas.create_line(50, 350, 850, 350, fill='gray', width=3, tags="background")
        self.canvas.create_line(50, 360, 850, 360, fill='gray', width=3, tags="background")

        # Traverses
        for x in range(50, 850, 30):
            self.canvas.create_rectangle(x - 2, 345, x + 2, 365, fill='brown', outline='brown', tags="background")

        # Zone de transition
        self.canvas.create_line(450, 50, 450, 380, fill='red', width=2, dash=(10, 5), tags="background")
        self.canvas.create_text(450, 40, text="Zone Transition", fill='red', font=('Arial', 10, 'bold'),
                                tags="background")

    def draw_train(self):
        # Position du train
        x = 100 + self.train_position * 6
        y = 320

        # Corps de la locomotive (avec tag)
        self.canvas.create_rectangle(x - 40, y - 30, x + 40, y, fill='blue', outline='darkblue', width=2, tags="train")
        self.canvas.create_polygon(x + 30, y - 30, x + 40, y - 20, x + 40, y, x + 30, y, fill='darkblue', tags="train")

        # Fenêtres
        self.canvas.create_rectangle(x - 30, y - 25, x - 10, y - 10, fill='lightblue', outline='darkblue', tags="train")
        self.canvas.create_rectangle(x - 5, y - 25, x + 15, y - 10, fill='lightblue', outline='darkblue', tags="train")

        # Roues
        for wheel_x in [x - 25, x - 10, x + 10, x + 25]:
            self.canvas.create_oval(wheel_x - 8, y - 5, wheel_x + 8, y + 11, fill='black', outline='gray', width=2,
                                    tags="train")

        # Pantographe 1500V
        self.draw_pantograph(x - 15, y - 30, self.pantograph_1500v_angle, "1500v")

        # Pantographe 25kV
        self.draw_pantograph(x + 15, y - 30, self.pantograph_25kv_angle, "25kv")

    def draw_pantograph(self, x, y, angle, type_panto):
        # Base du pantographe (avec tag)
        self.canvas.create_rectangle(x - 3, y, x + 3, y + 8, fill='gray', outline='black', tags="pantograph")

        # Calcul des positions selon l'angle
        if angle == 0:  # Levé
            arm_end_x = x
            arm_end_y = y - 25
            contact_y = 85 if type_panto == "1500v" else 80
        else:  # Baissé (angle = 90)
            arm_end_x = x + 20
            arm_end_y = y - 5
            contact_y = y - 5

        # Bras du pantographe
        self.canvas.create_line(x, y, arm_end_x, arm_end_y, fill='darkgray', width=3, tags="pantograph")

        # Contact (partie supérieure)
        if type_panto == "25kv":
            contact_width = 25
            contact_color = 'darkred'
        else:
            contact_width = 20
            contact_color = 'darkgoldenrod'

        self.canvas.create_rectangle(arm_end_x - contact_width // 2, contact_y - 2,
                                     arm_end_x + contact_width // 2, contact_y + 2,
                                     fill=contact_color, outline='black', tags="pantograph")

        # Arcs électriques (si pantographe actif et levé)
        if angle == 0:
            if (type_panto == "1500v" and self.system_1500v_active) or \
                    (type_panto == "25kv" and self.system_25kv_active):
                # Animation des étincelles
                for i in range(3):
                    spark_x = arm_end_x + (i - 1) * 3
                    spark_y = contact_y - 5
                    self.canvas.create_oval(spark_x - 1, spark_y - 3, spark_x + 1, spark_y + 1,
                                            fill='cyan', outline='white', tags="sparks")

    def update_phase(self, phase):
        self.current_phase = phase
        self.phase_label.config(text=phase)

    def update_system_status(self):
        if self.system_1500v_active:
            self.status_1500v.config(text="ACTIF", foreground='green')
        else:
            self.status_1500v.config(text="INACTIF", foreground='red')

        if self.system_25kv_active:
            self.status_25kv.config(text="ACTIF", foreground='green')
        else:
            self.status_25kv.config(text="INACTIF", foreground='red')

    def animate_pantograph(self, pantograph, start_angle, end_angle, duration):
        """Anime un pantographe de start_angle à end_angle"""
        steps = 15  # Réduire le nombre d'étapes
        angle_step = (end_angle - start_angle) / steps

        for i in range(steps + 1):
            if pantograph == "1500v":
                self.pantograph_1500v_angle = start_angle + (angle_step * i)
            else:
                self.pantograph_25kv_angle = start_angle + (angle_step * i)

            self.draw_scene()
            self.root.update_idletasks()  # Plus fluide que update()
            time.sleep(duration / steps)

    def animation_sequence(self):
        """Séquence principale d'animation"""
        try:
            # Phase 1: Démarrage
            self.update_phase("Circulation en 1500V DC")
            for pos in range(0, 40, 2):
                self.train_position = pos
                self.draw_scene()
                self.root.update_idletasks()
                time.sleep(0.08)  # Réduire légèrement le délai

            # Phase 2 : Approche de la transition
            self.update_phase("Approche zone de transition")
            for pos in range(40, 55, 1):
                self.train_position = pos
                self.draw_scene()
                self.root.update_idletasks()
                time.sleep(0.12)

            # Phase 3 : Arrêt et coupure 1500V
            self.update_phase("Arrêt - Coupure alimentation 1500V")
            time.sleep(1)

            self.system_1500v_active = False
            self.update_system_status()
            time.sleep(0.5)

            # Phase 4: Abaissement pantographe 1500V
            self.update_phase("Abaissement pantographe 1500V")
            self.animate_pantograph("1500v", 0, 90, 1.5)

            # Phase 5: Levage pantographe 25kV
            self.update_phase("Levage pantographe 25kV")
            self.animate_pantograph("25kv", 90, 0, 1.5)

            # Phase 6: Activation 25kV
            self.update_phase("Activation alimentation 25kV")
            time.sleep(0.5)
            self.system_25kv_active = True
            self.update_system_status()
            time.sleep(1)

            # Phase 7: Reprise circulation
            self.update_phase("Reprise circulation - Alimentation 25kV AC")
            for pos in range(55, 100, 2):
                self.train_position = pos
                self.draw_scene()
                self.root.update_idletasks()
                time.sleep(0.08)

            self.update_phase("Animation terminée - Train en 25kV AC")

        except Exception as e:
            print(f"Erreur pendant l'animation: {e}")
        finally:
            self.animation_running = False
            self.start_btn.config(state='normal')

    def start_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.start_btn.config(state='disabled')

            # Lancer l'animation dans un thread séparé
            animation_thread = threading.Thread(target=self.animation_sequence)
            animation_thread.daemon = True
            animation_thread.start()

    def reset_simulation(self):
        """Remet la simulation à l'état initial"""
        if not self.animation_running:
            self.train_position = 0
            self.pantograph_1500v_angle = 0
            self.pantograph_25kv_angle = 90
            self.system_1500v_active = True
            self.system_25kv_active = False
            self.background_drawn = False  # Forcer le redessin du fond

            self.update_phase("Attente")
            self.update_system_status()
            self.canvas.delete("all")  # Tout effacer pour reset complet
            self.draw_scene()

    def run(self):
        """Démarre l'application"""
        self.root.mainloop()


# Classe pour version console (alternative)
class TrainSimulationConsole:
    def __init__(self):
        self.train_position = 0
        self.pantograph_1500v_up = True
        self.pantograph_25kv_up = False
        self.system_1500v_active = True
        self.system_25kv_active = False

    def display_status(self, phase):
        print(f"\n{'=' * 50}")
        print(f"PHASE: {phase}")
        print(f"{'=' * 50}")
        print(f"Position du train: {self.train_position}%")
        print(f"Pantographe 1500V: {'LEVÉ' if self.pantograph_1500v_up else 'BAISSÉ'}")
        print(f"Pantographe 25kV:  {'LEVÉ' if self.pantograph_25kv_up else 'BAISSÉ'}")
        print(f"Système 1500V: {'ACTIF' if self.system_1500v_active else 'INACTIF'}")
        print(f"Système 25kV:  {'ACTIF' if self.system_25kv_active else 'INACTIF'}")

        # Représentation ASCII simple
        panto_1500 = "⚡" if self.pantograph_1500v_up and self.system_1500v_active else "🔽"
        panto_25kv = "⚡" if self.pantograph_25kv_up and self.system_25kv_active else "🔽"

        print(f"\nReprésentation: {panto_1500}🚂{panto_25kv}")
        print(f"{'=' * 50}")
        time.sleep(2)

    def run_simulation(self):
        print("🚂 SIMULATION CHANGEMENT DE PANTOGRAPHES 🚂")
        input("Appuyez sur Entrée pour démarrer l'animation...")

        # Séquence d'animation
        phases = [
            ("Circulation initiale en 1500V DC", 20),
            ("Approche de la zone de transition", 45),
            ("Arrêt en zone neutre", 50),
            ("Coupure système 1500V", 50),
            ("Abaissement pantographe 1500V", 50),
            ("Levage pantographe 25kV", 50),
            ("Activation système 25kV", 50),
            ("Reprise circulation en 25kV AC", 80),
            ("Circulation normale en 25kV AC", 100)
        ]

        for i, (phase, position) in enumerate(phases):
            self.train_position = position

            # Actions spécifiques selon la phase
            if i == 3:  # Coupure 1500V
                self.system_1500v_active = False
            elif i == 4:  # Abaissement pantographe 1500V
                self.pantograph_1500v_up = False
            elif i == 5:  # Levage pantographe 25kV
                self.pantograph_25kv_up = True
            elif i == 6:  # Activation 25kV
                self.system_25kv_active = True

            self.display_status(phase)

        print("\n🎉 SIMULATION TERMINÉE 🎉")
        print("Le train circule maintenant avec l'alimentation 25kV AC")