import tkinter as tk
from tkinter import ttk
import time
import threading

class TrainPantographSimulation:
    def __init__(self):
        self.background_drawn = None
        self.reset_btn = None
        self.start_btn = None
        self.phase_label = None
        self.status_25kv = None
        self.status_1500v = None
        self.canvas = None
        self.root = tk.Tk()
        self.root.title("Train Pantograph Change Simulation")
        self.root.geometry("1000x600")
        self.root.configure(bg='lightblue')

        # State variables
        self.train_position = 0
        self.pantograph_1500v_angle = 0  # 0 = up, 90 = down
        self.pantograph_25kv_angle = 90  # 90 = down, 0 = up
        self.system_1500v_active = True
        self.system_25kv_active = False
        self.animation_running = False
        self.current_phase = "Waiting"

        self.setup_gui()

    def setup_gui(self):
        # Main canvas
        self.canvas = tk.Canvas(self.root, width=900, height=400, bg='lightgreen')
        self.canvas.pack(pady=20)

        # Information panel
        info_frame = ttk.Frame(self.root)
        info_frame.pack(pady=10)

        ttk.Label(info_frame, text="System Status:", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2)

        ttk.Label(info_frame, text="1500V DC:").grid(row=1, column=0, sticky='w')
        self.status_1500v = ttk.Label(info_frame, text="ACTIVE", foreground='green', font=('Arial', 10, 'bold'))
        self.status_1500v.grid(row=1, column=1, sticky='w')

        ttk.Label(info_frame, text="25kV AC:").grid(row=2, column=0, sticky='w')
        self.status_25kv = ttk.Label(info_frame, text="INACTIVE", foreground='red', font=('Arial', 10, 'bold'))
        self.status_25kv.grid(row=2, column=1, sticky='w')

        ttk.Label(info_frame, text="Phase:").grid(row=3, column=0, sticky='w')
        self.phase_label = ttk.Label(info_frame, text=self.current_phase, font=('Arial', 10))
        self.phase_label.grid(row=3, column=1, sticky='w')

        # Control buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_btn = ttk.Button(control_frame, text="Start Animation", command=self.start_animation)
        self.start_btn.pack(side='left', padx=5)

        self.reset_btn = ttk.Button(control_frame, text="Reset", command=self.reset_simulation)
        self.reset_btn.pack(side='left', padx=5)

        # Mark that the background has not been drawn yet
        self.background_drawn = False

        # Draw the initial scene
        self.draw_scene()

    def draw_scene(self):
        # Redraw only if necessary to avoid flickering
        self.canvas.delete("train", "pantograph", "sparks")

        # Draw fixed elements only once
        if not hasattr(self, 'background_drawn'):
            self.draw_background()
            self.background_drawn = True

        # Train (with tag so it can be erased)
        self.draw_train()

    def draw_background(self):
        """Draw the fixed scenery elements"""
        # Overhead lines
        # 1500V (left)
        self.canvas.create_line(50, 80, 450, 80, fill='gold', width=4, tags="background")
        self.canvas.create_text(250, 60, text="1500V DC", fill='darkgoldenrod', font=('Arial', 12, 'bold'),
                                tags="background")

        # 25kV (right)
        self.canvas.create_line(450, 75, 850, 75, fill='orangered', width=5, tags="background")
        self.canvas.create_text(650, 55, text="25kV AC", fill='darkred', font=('Arial', 12, 'bold'), tags="background")

        # Rails
        self.canvas.create_line(50, 350, 850, 350, fill='gray', width=3, tags="background")
        self.canvas.create_line(50, 360, 850, 360, fill='gray', width=3, tags="background")

        # Sleepers
        for x in range(50, 850, 30):
            self.canvas.create_rectangle(x - 2, 345, x + 2, 365, fill='brown', outline='brown', tags="background")

        # Transition zone
        self.canvas.create_line(450, 50, 450, 380, fill='red', width=2, dash=(10, 5), tags="background")
        self.canvas.create_text(450, 40, text="Transition Zone", fill='red', font=('Arial', 10, 'bold'),
                                tags="background")

    def draw_train(self):
        # Train position
        x = 100 + self.train_position * 6
        y = 320

        # Locomotive body (with tag)
        self.canvas.create_rectangle(x - 40, y - 30, x + 40, y, fill='blue', outline='darkblue', width=2, tags="train")
        self.canvas.create_polygon(x + 30, y - 30, x + 40, y - 20, x + 40, y, x + 30, y, fill='darkblue', tags="train")

        # Windows
        self.canvas.create_rectangle(x - 30, y - 25, x - 10, y - 10, fill='lightblue', outline='darkblue', tags="train")
        self.canvas.create_rectangle(x - 5, y - 25, x + 15, y - 10, fill='lightblue', outline='darkblue', tags="train")

        # Wheels
        for wheel_x in [x - 25, x - 10, x + 10, x + 25]:
            self.canvas.create_oval(wheel_x - 8, y - 5, wheel_x + 8, y + 11, fill='black', outline='gray', width=2,
                                    tags="train")

        # 1500V pantograph
        self.draw_pantograph(x - 15, y - 30, self.pantograph_1500v_angle, "1500v")

        # 25kV pantograph
        self.draw_pantograph(x + 15, y - 30, self.pantograph_25kv_angle, "25kv")

    def draw_pantograph(self, x, y, angle, type_panto):
        # Pantograph base (with tag)
        self.canvas.create_rectangle(x - 3, y, x + 3, y + 8, fill='gray', outline='black', tags="pantograph")

        # Calculate positions according to angle
        if angle == 0:  # Up
            arm_end_x = x
            arm_end_y = y - 25
            contact_y = 85 if type_panto == "1500v" else 80
        else:  # Down (angle = 90)
            arm_end_x = x + 20
            arm_end_y = y - 5
            contact_y = y - 5

        # Pantograph arm
        self.canvas.create_line(x, y, arm_end_x, arm_end_y, fill='darkgray', width=3, tags="pantograph")

        # Contact strip (upper part)
        if type_panto == "25kv":
            contact_width = 25
            contact_color = 'darkred'
        else:
            contact_width = 20
            contact_color = 'darkgoldenrod'

        self.canvas.create_rectangle(arm_end_x - contact_width // 2, contact_y - 2,
                                     arm_end_x + contact_width // 2, contact_y + 2,
                                     fill=contact_color, outline='black', tags="pantograph")

        # Electric arcs (if pantograph active and raised)
        if angle == 0:
            if (type_panto == "1500v" and self.system_1500v_active) or \
                    (type_panto == "25kv" and self.system_25kv_active):
                # Spark animation
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
            self.status_1500v.config(text="ACTIVE", foreground='green')
        else:
            self.status_1500v.config(text="INACTIVE", foreground='red')

        if self.system_25kv_active:
            self.status_25kv.config(text="ACTIVE", foreground='green')
        else:
            self.status_25kv.config(text="INACTIVE", foreground='red')

    def animate_pantograph(self, pantograph, start_angle, end_angle, duration):
        """Animate a pantograph from start_angle to end_angle"""
        steps = 15  # Reduce the number of steps
        angle_step = (end_angle - start_angle) / steps

        for i in range(steps + 1):
            if pantograph == "1500v":
                self.pantograph_1500v_angle = start_angle + (angle_step * i)
            else:
                self.pantograph_25kv_angle = start_angle + (angle_step * i)

            self.draw_scene()
            self.root.update_idletasks()  # Smoother than update()
            time.sleep(duration / steps)

    def animation_sequence(self):
        """Main animation sequence"""
        try:
            # Phase 1: Start
            self.update_phase("Running on 1500V DC")
            for pos in range(0, 40, 2):
                self.train_position = pos
                self.draw_scene()
                self.root.update_idletasks()
                time.sleep(0.08)  # Slightly reduce the delay

            # Phase 2: Approach transition
            self.update_phase("Approaching transition zone")
            for pos in range(40, 55, 1):
                self.train_position = pos
                self.draw_scene()
                self.root.update_idletasks()
                time.sleep(0.12)

            # Phase 3: Stop and cut 1500V
            self.update_phase("Stop - Cut 1500V power")
            time.sleep(1)

            self.system_1500v_active = False
            self.update_system_status()
            time.sleep(0.5)

            # Phase 4: Lower 1500V pantograph
            self.update_phase("Lowering 1500V pantograph")
            self.animate_pantograph("1500v", 0, 90, 1.5)

            # Phase 5: Raise 25kV pantograph
            self.update_phase("Raising 25kV pantograph")
            self.animate_pantograph("25kv", 90, 0, 1.5)

            # Phase 6: Activate 25kV
            self.update_phase("Activating 25kV power")
            time.sleep(0.5)
            self.system_25kv_active = True
            self.update_system_status()
            time.sleep(1)

            # Phase 7: Resume operation
            self.update_phase("Resuming operation - 25kV AC power")
            for pos in range(55, 100, 2):
                self.train_position = pos
                self.draw_scene()
                self.root.update_idletasks()
                time.sleep(0.08)

            self.update_phase("Animation finished - Train on 25kV AC")

        except Exception as e:
            print(f"Error during animation: {e}")
        finally:
            self.animation_running = False
            self.start_btn.config(state='normal')

    def start_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.start_btn.config(state='disabled')

            # Launch the animation in a separate thread
            animation_thread = threading.Thread(target=self.animation_sequence)
            animation_thread.daemon = True
            animation_thread.start()

    def reset_simulation(self):
        """Reset the simulation to the initial state"""
        if not self.animation_running:
            self.train_position = 0
            self.pantograph_1500v_angle = 0
            self.pantograph_25kv_angle = 90
            self.system_1500v_active = True
            self.system_25kv_active = False
            self.background_drawn = False  # Force background redraw

            self.update_phase("Waiting")
            self.update_system_status()
            self.canvas.delete("all")  # Clear everything for full reset
            self.draw_scene()

    def run(self):
        """Start the application"""
        self.root.mainloop()


# Console version class (alternative)
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
        print(f"Train position: {self.train_position}%")
        print(f"1500V pantograph: {'UP' if self.pantograph_1500v_up else 'DOWN'}")
        print(f"25kV pantograph:  {'UP' if self.pantograph_25kv_up else 'DOWN'}")
        print(f"1500V system: {'ACTIVE' if self.system_1500v_active else 'INACTIVE'}")
        print(f"25kV system:  {'ACTIVE' if self.system_25kv_active else 'INACTIVE'}")

        # Simple ASCII representation
        panto_1500 = "⚡" if self.pantograph_1500v_up and self.system_1500v_active else "🔽"
        panto_25kv = "⚡" if self.pantograph_25kv_up and self.system_25kv_active else "🔽"

        print(f"\nRepresentation: {panto_1500}🚂{panto_25kv}")
        print(f"{'=' * 50}")
        time.sleep(2)

    def run_simulation(self):
        print("🚂 PANTOGRAPH CHANGE SIMULATION 🚂")
        input("Press Enter to start the animation...")

        # Animation sequence
        phases = [
            ("Initial run on 1500V DC", 20),
            ("Approaching the transition zone", 45),
            ("Stop in neutral zone", 50),
            ("Cutting off 1500V system", 50),
            ("Lowering 1500V pantograph", 50),
            ("Raising 25kV pantograph", 50),
            ("Activating 25kV system", 50),
            ("Resuming operation on 25kV AC", 80),
            ("Normal operation on 25kV AC", 100)
        ]

        for i, (phase, position) in enumerate(phases):
            self.train_position = position

            # Specific actions depending on the phase
            if i == 3:  # Cut 1500V
                self.system_1500v_active = False
            elif i == 4:  # Lower 1500V pantograph
                self.pantograph_1500v_up = False
            elif i == 5:  # Raise 25kV pantograph
                self.pantograph_25kv_up = True
            elif i == 6:  # Activate 25kV
                self.system_25kv_active = True

            self.display_status(phase)

        print("\n🎉 SIMULATION FINISHED 🎉")
        print("The train is now running with 25kV AC power")
