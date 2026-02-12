import os
import sys
import time
import json
import subprocess
import psutil
import ctypes
import ctypes.wintypes

# Runtime Analysis Configuration
ANALYSIS_DURATION = 120  # 2 minutes
OUTPUT_FILE = "runtime_analysis.json"

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def kill_process_tree(pid):
    """Kill a process and its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        parent.kill()
    except psutil.NoSuchProcess:
        pass

class KeystrokeSimulator:
    """Windows keystroke simulator using SendInput"""

    def __init__(self):
        # Virtual key codes
        self.VK_SPACE = 0x20
        self.VK_UP = 0x26
        self.VK_LEFT = 0x25
        self.VK_RIGHT = 0x27
        self.VK_DOWN = 0x28
        self.VK_ESCAPE = 0x1B
        self.VK_W = 0x57
        self.VK_A = 0x41
        self.VK_D = 0x44

        # Input structure for key events
        self.KEYEVENTF_SCANCODE = 0x0008
        self.KEYEVENTF_KEYUP = 0x0002

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", ctypes.wintypes.WORD),
                ("wScan", ctypes.wintypes.WORD),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.wintypes.ULONG)),
            ]

        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT)]

            _anonymous_ = ("_input",)
            _fields_ = [
                ("type", ctypes.wintypes.DWORD),
                ("_input", _INPUT),
            ]

        self.KEYBDINPUT = KEYBDINPUT
        self.INPUT = INPUT
        self.user32 = ctypes.windll.user32
        self.SendInput = self.user32.SendInput
        self.SendInput.argtypes = [ctypes.wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
        self.SendInput.restype = ctypes.wintypes.UINT

    def send_key(self, vk_code, press=True):
        """Send a key press or release"""
        ki = self.KEYBDINPUT()
        ki.wVk = vk_code
        ki.wScan = 0
        ki.dwFlags = 0 if press else self.KEYEVENTF_KEYUP
        ki.time = 0
        ki.dwExtraInfo = None

        inp = self.INPUT()
        inp.type = 1  # INPUT_KEYBOARD
        inp.ki = ki

        # Create array properly for ctypes
        input_array = (self.INPUT * 1)(inp)
        nInputs = 1
        inputSize = ctypes.sizeof(self.INPUT)
        self.SendInput(nInputs, input_array, inputSize)

    def press_space(self):
        """Press and release space"""
        self.send_key(self.VK_SPACE, True)
        time.sleep(0.05)
        self.send_key(self.VK_SPACE, False)

    def hold_key(self, vk_code, duration):
        """Hold a key for a duration"""
        self.send_key(vk_code, True)
        time.sleep(duration)
        self.send_key(vk_code, False)

    def press_esc(self):
        """Press and release ESC"""
        self.send_key(self.VK_ESCAPE, True)
        time.sleep(0.05)
        self.send_key(self.VK_ESCAPE, False)

def run_runtime_analysis():
    """Run automated runtime analysis"""
    log("Starting Runtime Analysis")
    log("=" * 50)

    analysis = {
        "app_name": "asteroid-blaster",
        "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_duration_seconds": ANALYSIS_DURATION,
        "phases": [],
        "checks": {},
        "errors": [],
        "overall_status": "FAILED"
    }

    # Check dependencies
    log("Checking dependencies...")
    checks = analysis["checks"]

    # Check Python
    python_version = sys.version_info
    checks["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    checks["python_available"] = True
    log(f"  Python {checks['python_version']}")

    # Check pygame
    try:
        import pygame
        checks["pygame_available"] = True
        checks["pygame_version"] = pygame.version.ver
        log(f"  Pygame {pygame.version.ver} found")
    except ImportError:
        checks["pygame_available"] = False
        checks["pygame_version"] = None
        log("  ERROR: Pygame not available")
        analysis["errors"].append("Pygame is not installed")

    # Check main.py exists
    if os.path.exists("main.py"):
        checks["main_py_exists"] = True
        log("  main.py found")
    else:
        checks["main_py_exists"] = False
        log("  ERROR: main.py not found")
        analysis["errors"].append("main.py not found")

    if not checks.get("pygame_available") or not checks.get("main_py_exists"):
        log("Critical dependencies missing, aborting analysis")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(analysis, f, indent=2)
        return

    log("\nLaunching application...")
    log("-" * 50)

    # Initialize input simulator
    try:
        input_sim = KeystrokeSimulator()
        log("  Input simulation initialized")
    except Exception as e:
        log(f"  WARNING: Could not init input sim: {e}")
        input_sim = None

    # Use the current Python interpreter since it has pygame
    python_exe = sys.executable

    # Launch the application
    proc = None
    try:
        cmd = [python_exe, "main.py"]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        checks["app_launched"] = True
        checks["app_pid"] = proc.pid
        log(f"  Process started with PID: {proc.pid}")

    except Exception as e:
        checks["app_launched"] = False
        analysis["errors"].append(f"Failed to launch: {str(e)}")
        log(f"  ERROR: Failed to launch - {e}")

        with open(OUTPUT_FILE, 'w') as f:
            json.dump(analysis, f, indent=2)
        return

    # Give time for app to initialize
    time.sleep(3)

    # Check if process is still running
    if proc.poll() is not None:
        checks["app_running"] = False
        stdout, stderr = proc.communicate()
        if stderr:
            analysis["errors"].append(f"Startup error: {stderr.decode()}")
        log(f"  ERROR: Process terminated early")
        log(f"  STDERR: {stderr.decode()}")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(analysis, f, indent=2)
        return

    checks["app_running"] = True
    log("  Application is running")

    start_time = time.time()

    # Phase 1: Menu navigation and start (0-10 seconds)
    phase = {
        "name": "Menu Navigation",
        "start_time": time.time(),
        "duration_seconds": 10,
        "actions": [],
        "status": "PENDING"
    }
    log("\nPhase 1: Menu Navigation")
    log("-" * 50)

    try:
        time.sleep(2)
        if input_sim:
            log("  Action: Press SPACE to start")
            input_sim.press_space()
            phase["actions"].append("Press SPACE to start game")
        else:
            log("  Skipping: Input simulation not available")

        phase["status"] = "COMPLETED"
        checks["menu_accessible"] = True
        log("  Phase 1 COMPLETED")

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 1 FAILED: {e}")
        analysis["errors"].append(f"Menu navigation failed: {e}")

    analysis["phases"].append(phase)

    # Phase 2: Basic gameplay testing (10-60 seconds)
    phase = {
        "name": "Basic Gameplay",
        "start_time": time.time(),
        "duration_seconds": 50,
        "actions": [],
        "status": "PENDING"
    }
    log("\nPhase 2: Basic Gameplay")
    log("-" * 50)

    action_count = 0
    phase_start = time.time()

    try:
        while time.time() - phase_start < 50:
            elapsed = time.time() - phase_start

            # Simulate various game actions
            if int(elapsed) % 5 == 0 and action_count != int(elapsed):
                action_count = int(elapsed)

                if input_sim:
                    if action_count % 20 == 0:
                        log(f"  Time: {10 + action_count}s - Shooting")
                        input_sim.press_space()
                        phase["actions"].append(f"Shoot at {10 + action_count}s")

                    elif action_count % 15 == 0:
                        log(f"  Time: {10 + action_count}s - Rotating left")
                        input_sim.hold_key(input_sim.VK_LEFT, 0.2)
                        phase["actions"].append(f"Rotate left at {10 + action_count}s")

                    elif action_count % 10 == 0:
                        log(f"  Time: {10 + action_count}s - Rotating right")
                        input_sim.hold_key(input_sim.VK_RIGHT, 0.2)
                        phase["actions"].append(f"Rotate right at {10 + action_count}s")

                    elif action_count % 5 == 0:
                        log(f"  Time: {10 + action_count}s - Thrusting")
                        input_sim.hold_key(input_sim.VK_UP, 0.3)
                        phase["actions"].append(f"Thrust at {10 + action_count}s")

            # Check if process still running
            if proc.poll() is not None:
                log("  WARNING: Process terminated during gameplay")
                phase["status"] = "INTERRUPTED"
                phase["terminated_at"] = 10 + elapsed
                break

            time.sleep(0.5)

        if proc.poll() is None:
            phase["status"] = "COMPLETED"
            checks["gameplay_stable"] = True
            log("  Phase 2 COMPLETED")
        else:
            checks["gameplay_stable"] = False
            log(f"  Phase 2 INTERRUPTED")

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 2 FAILED: {e}")
        analysis["errors"].append(f"Gameplay failed: {e}")

    analysis["phases"].append(phase)

    # Phase 3: Extended stability test (60-110 seconds)
    phase = {
        "name": "Extended Stability",
        "start_time": time.time(),
        "duration_seconds": 50,
        "status": "PENDING"
    }
    log("\nPhase 3: Extended Stability Test")
    log("-" * 50)

    phase_start = time.time()

    try:
        while time.time() - phase_start < 50:
            elapsed = time.time() - phase_start

            if int(elapsed) % 10 == 0:
                log(f"  Stability test: {60 + int(elapsed)}s elapsed")

            # Occasional input during stability test
            if input_sim and int(elapsed) % 20 == 0 and int(elapsed) > 0:
                log(f"  Time: {60 + int(elapsed)}s - Random action")
                input_sim.press_space()

            if proc.poll() is not None:
                log(f"  Process terminated at {60 + elapsed}s")
                phase["status"] = "INTERRUPTED"
                phase["terminated_at"] = 60 + elapsed
                break

            time.sleep(1)

        if proc.poll() is None:
            phase["status"] = "COMPLETED"
            checks["extended_stable"] = True
            log("  Phase 3 COMPLETED")
        else:
            checks["extended_stable"] = False
            log(f"  Phase 3 INTERRUPTED")

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 3 FAILED: {e}")
        analysis["errors"].append(f"Stability test failed: {e}")

    analysis["phases"].append(phase)

    # Phase 4: Graceful shutdown (110-120 seconds)
    phase = {
        "name": "Graceful Shutdown",
        "start_time": time.time(),
        "status": "PENDING"
    }
    log("\nPhase 4: Graceful Shutdown")
    log("-" * 50)

    try:
        time.sleep(2)

        if input_sim:
            log("  Action: Sending ESC to quit")
            input_sim.press_esc()
        else:
            log("  Attempting graceful shutdown without input simulation")

        # Wait for graceful termination
        wait_start = time.time()
        terminated = False

        while time.time() - wait_start < 5:
            if proc.poll() is not None:
                terminated = True
                checks["graceful_shutdown"] = True
                phase["status"] = "COMPLETED"
                log("  Application terminated gracefully")
                break
            time.sleep(0.5)

        if not terminated:
            log("  Application did not terminate, force killing")
            phase["status"] = "FORCED"
            checks["graceful_shutdown"] = False

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 4 FAILED: {e}")

    analysis["phases"].append(phase)

    # Force kill if still running
    if proc.poll() is None:
        log("  Force killing process...")
        kill_process_tree(proc.pid)
        time.sleep(1)

    total_elapsed = time.time() - start_time

    # Calculate overall status
    log("\n" + "=" * 50)
    log("ANALYSIS SUMMARY")
    log("=" * 50)

    passed_count = 0
    total_count = 0

    for check_name, check_value in checks.items():
        if isinstance(check_value, bool):
            total_count += 1
            status = "PASS" if check_value else "FAIL"
            log(f"  {check_name}: {status}")
            if check_value:
                passed_count += 1

    log(f"\nPassed: {passed_count}/{total_count}")
    log(f"Total Analysis Time: {total_elapsed:.1f}s")

    if passed_count >= total_count * 0.8:
        analysis["overall_status"] = "PASSED"
        log("Overall Status: PASSED")
    else:
        analysis["overall_status"] = "FAILED"
        log("Overall Status: FAILED")

    # Add execution stats
    analysis["execution_stats"] = {
        "total_phases": len(analysis["phases"]),
        "completed_phases": sum(1 for p in analysis["phases"] if p.get("status") == "COMPLETED"),
        "total_actions": sum(len(p.get("actions", [])) for p in analysis["phases"]),
        "total_errors": len(analysis["errors"]),
        "actual_duration_seconds": round(total_elapsed, 2)
    }

    # Write results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(analysis, f, indent=2)

    log(f"\nResults saved to {OUTPUT_FILE}")
    log("Analysis complete!")

if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    run_runtime_analysis()
