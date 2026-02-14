"""Runtime analysis script for Vector Super Mario Bros Paratroopa Jump."""

import subprocess
import sys
import time
import json
import os
from datetime import datetime

def run_runtime_analysis():
    """Run the game and analyze its runtime behavior."""
    analysis_data = {
        "timestamp": datetime.now().isoformat(),
        "app_name": "vector-super-mario-bros-paratroopa-jump",
        "runtime_seconds": 120,
        "tests": []
    }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting runtime analysis...")

    # Test 1: Launch application
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Test 1: Launching application...")
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        analysis_data["tests"].append({
            "name": "application_launch",
            "status": "PASSED",
            "details": "Application started successfully with PID: {}".format(process.pid)
        })
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Application launched (PID: {process.pid})")
    except Exception as e:
        analysis_data["tests"].append({
            "name": "application_launch",
            "status": "FAILED",
            "error": str(e)
        })
        analysis_data["overall_status"] = "FAILED"
        with open("runtime_analysis.json", "w") as f:
            json.dump(analysis_data, f, indent=2)
        return

    # Wait for initialization
    time.sleep(3)

    # Test 2: Check if process is still running
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Test 2: Checking process stability...")
    poll_result = process.poll()
    if poll_result is None:
        analysis_data["tests"].append({
            "name": "process_stability",
            "status": "PASSED",
            "details": "Process is running after initialization"
        })
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Process is stable")
    else:
        stdout, stderr = process.communicate()
        analysis_data["tests"].append({
            "name": "process_stability",
            "status": "FAILED",
            "details": f"Process exited with code {poll_result}",
            "stdout": stdout,
            "stderr": stderr
        })
        analysis_data["overall_status"] = "FAILED"
        with open("runtime_analysis.json", "w") as f:
            json.dump(analysis_data, f, indent=2)
        return

    # Test 3: Monitor for 2 minutes
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Test 3: Running for 2 minutes...")
    start_time = time.time()
    check_interval = 10  # Check every 10 seconds
    last_check = start_time
    crash_detected = False
    memory_leak_suspected = False

    while time.time() - start_time < 120:
        time.sleep(1)
        current_time = time.time()

        # Check process status every 10 seconds
        if current_time - last_check >= check_interval:
            poll_result = process.poll()
            elapsed = int(current_time - start_time)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Status check at {elapsed}s: Process {'running' if poll_result is None else 'terminated'}")

            if poll_result is not None:
                crash_detected = True
                stdout, stderr = process.communicate()
                analysis_data["tests"].append({
                    "name": "runtime_stability",
                    "status": "FAILED",
                    "details": f"Process crashed after {elapsed} seconds",
                    "exit_code": poll_result,
                    "stdout": stdout,
                    "stderr": stderr
                })
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Process crashed at {elapsed}s!")
                break

            last_check = current_time

    # Test 4: Clean termination
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Test 4: Terminating application...")
    elapsed_time = time.time() - start_time

    try:
        # Try graceful termination first
        process.terminate()
        try:
            process.wait(timeout=5)
            analysis_data["tests"].append({
                "name": "clean_termination",
                "status": "PASSED",
                "details": f"Process terminated gracefully after {elapsed_time:.1f} seconds"
            })
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Process terminated gracefully")
        except subprocess.TimeoutExpired:
            # Force kill if graceful termination fails
            process.kill()
            process.wait()
            analysis_data["tests"].append({
                "name": "clean_termination",
                "status": "WARNING",
                "details": f"Process had to be force-killed after {elapsed_time:.1f} seconds"
            })
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Process was force-killed")
    except Exception as e:
        analysis_data["tests"].append({
            "name": "clean_termination",
            "status": "FAILED",
            "error": str(e)
        })
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error during termination: {e}")

    # Determine overall status
    if not crash_detected:
        analysis_data["tests"].append({
            "name": "runtime_stability",
            "status": "PASSED",
            "details": f"Process ran for full {elapsed_time:.1f} seconds without crashing"
        })

    # Calculate overall status
    failed_tests = [t for t in analysis_data["tests"] if t.get("status") == "FAILED"]
    analysis_data["overall_status"] = "FAILED" if failed_tests else "PASSED"
    analysis_data["total_runtime"] = elapsed_time

    # Write results
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Writing results to runtime_analysis.json...")
    with open("runtime_analysis.json", "w") as f:
        json.dump(analysis_data, f, indent=2)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Runtime analysis complete. Overall status: {analysis_data['overall_status']}")

if __name__ == "__main__":
    run_runtime_analysis()
