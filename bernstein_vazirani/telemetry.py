"""
Telemetry Module for Job Status Monitoring

This module provides background thread monitoring of job status and queued position.
It outputs JSON strings that can be parsed by external agents to update UI status bars.
"""

import json
import threading
import time
from typing import Optional, Callable, Dict, Any
from enum import Enum
import queue


class JobStatus(Enum):
    """Enumeration of possible job statuses."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobMonitor:
    """Background thread monitor for job status tracking."""
    
    def __init__(self, check_interval: float = 1.0, output_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the JobMonitor.
        
        Args:
            check_interval: Time in seconds between status checks (default: 1.0)
            output_callback: Optional callback function to handle JSON output instead of printing
        """
        self.check_interval = check_interval
        self.output_callback = output_callback or print
        self.job_id: Optional[str] = None
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.status_queue: queue.Queue = queue.Queue()
        self._status_data: Dict[str, Any] = {
            "status": JobStatus.QUEUED.value,
            "pos": None,
            "job_id": None
        }
        self._lock = threading.Lock()
    
    def start_monitoring(self, job_id: str) -> None:
        """
        Start monitoring a job by its ID.
        
        Args:
            job_id: The unique identifier for the job to monitor
        """
        if self.running:
            raise RuntimeError("Monitor is already running")
        
        self.job_id = job_id
        self.running = True
        self._status_data["job_id"] = job_id
        
        # Start the background thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop the background monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.monitor_thread = None
    
    def set_status(self, status: str, position: Optional[int] = None) -> None:
        """
        Update the current job status.
        
        Args:
            status: The new status (e.g., 'queued', 'running', 'completed')
            position: Optional position in queue for queued jobs
        """
        with self._lock:
            self._status_data["status"] = status
            if position is not None:
                self._status_data["pos"] = position
            else:
                # Remove position if not specified
                self._status_data.pop("pos", None)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status data.
        
        Returns:
            Dictionary with current status information
        """
        with self._lock:
            return self._status_data.copy()
    
    def _monitor_loop(self) -> None:
        """Background loop that periodically outputs status as JSON."""
        while self.running:
            try:
                # Get current status
                status_data = self.get_status()
                
                # Output as JSON string
                json_output = json.dumps(status_data)
                self.output_callback(json_output)
                
                # Put into queue for polling if needed
                try:
                    self.status_queue.put_nowait(json_output)
                except queue.Full:
                    pass  # Queue is full, skip this update
                
                # Wait before next check
                time.sleep(self.check_interval)
            except Exception as e:
                # Log errors but keep monitoring
                error_data = {
                    "status": "error",
                    "job_id": self.job_id,
                    "error": str(e)
                }
                self.output_callback(json.dumps(error_data))
                time.sleep(self.check_interval)
    
    def get_latest_status_json(self) -> str:
        """
        Get the latest status as a JSON string from the queue (non-blocking).
        
        Returns:
            JSON string of the latest status, or empty string if queue is empty
        """
        try:
            return self.status_queue.get_nowait()
        except queue.Empty:
            return ""


class TelemetryManager:
    """Central manager for telemetry monitoring."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the telemetry manager (called once due to singleton)."""
        if self._initialized:
            return
        self.monitors: Dict[str, JobMonitor] = {}
        self._initialized = True
    
    def create_monitor(self, job_id: str, check_interval: float = 1.0, 
                      output_callback: Optional[Callable[[str], None]] = None) -> JobMonitor:
        """
        Create and start a new job monitor.
        
        Args:
            job_id: The job ID to monitor
            check_interval: Time between status checks
            output_callback: Optional callback for JSON output
            
        Returns:
            The created JobMonitor instance
        """
        if job_id in self.monitors:
            raise ValueError(f"Monitor for job {job_id} already exists")
        
        monitor = JobMonitor(check_interval=check_interval, output_callback=output_callback)
        monitor.start_monitoring(job_id)
        self.monitors[job_id] = monitor
        return monitor
    
    def stop_monitor(self, job_id: str) -> None:
        """
        Stop a job monitor.
        
        Args:
            job_id: The job ID of the monitor to stop
        """
        if job_id in self.monitors:
            self.monitors[job_id].stop_monitoring()
            del self.monitors[job_id]
    
    def update_status(self, job_id: str, status: str, position: Optional[int] = None) -> None:
        """
        Update the status of a monitored job.
        
        Args:
            job_id: The job ID
            status: The new status
            position: Optional queue position
        """
        if job_id in self.monitors:
            self.monitors[job_id].set_status(status, position)
    
    def get_monitor(self, job_id: str) -> Optional[JobMonitor]:
        """
        Get a monitor by job ID.
        
        Args:
            job_id: The job ID
            
        Returns:
            The JobMonitor if it exists, None otherwise
        """
        return self.monitors.get(job_id)


# Global instance for easy access
telemetry = TelemetryManager()


if __name__ == "__main__":
    # Example usage
    print("Starting telemetry example...\n")
    
    # Create a monitor
    job_id = "job_12345"
    monitor = telemetry.create_monitor(job_id, check_interval=0.5)
    
    # Simulate job status changes
    try:
        print("Simulating job status updates:\n")
        
        # Queued state
        for pos in range(5, 0, -1):
            telemetry.update_status(job_id, "queued", position=pos)
            time.sleep(1.5)
        
        # Running state
        telemetry.update_status(job_id, "running")
        time.sleep(3)
        
        # Completed state
        telemetry.update_status(job_id, "completed")
        time.sleep(1)
        
    finally:
        # Stop monitoring
        telemetry.stop_monitor(job_id)
        print("\nMonitoring stopped.")
