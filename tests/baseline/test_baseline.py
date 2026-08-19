import pytest
import time
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class StandardMediaResult:
    media_id: str
    status: str
    url: Optional[str] = None
    error: Optional[str] = None
    file_size_bytes: int = 0

class BaseJobServiceContract:
    """Abstract contract test suite to verify job service behavior regardless of underlying monolith refactoring."""
    def create_job(self, payload: Dict[str, Any]) -> str:
        raise NotImplementedError
        
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def process_job(self, job_id: str) -> StandardMediaResult:
        raise NotImplementedError

class MockJobService(BaseJobServiceContract):
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def create_job(self, payload: Dict[str, Any]) -> str:
        if not payload.get("source_url"):
            raise ValueError("VALIDATION_ERROR: missing source_url")
        with self._lock:
            self._counter += 1
            job_id = f"job_{self._counter}"
            self._jobs[job_id] = {
                "id": job_id,
                "status": "PENDING",
                "payload": payload,
                "created_at": time.time()
            }
            return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._jobs.get(job_id)

    def process_job(self, job_id: str) -> StandardMediaResult:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return StandardMediaResult(media_id="", status="FAILED", error="JOB_NOT_FOUND")
            
            payload = job.get("payload", {})
            if payload.get("simulated_failure"):
                job["status"] = "FAILED"
                return StandardMediaResult(
                    media_id=job_id,
                    status="FAILED",
                    error="PROCESSING_FAILED",
                    file_size_bytes=0
                )
            
            job["status"] = "COMPLETED"
            return StandardMediaResult(
                media_id=job_id,
                status="COMPLETED",
                url=f"https://storage.cdn.local/{job_id}.mp4",
                file_size_bytes=1024576
            )

class RateLimiterContract:
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(float(self.capacity), self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

def test_job_service_lifecycle():
    """Verify job creation, retrieval, and completion pipeline contract."""
    service = MockJobService()
    
    with pytest.raises(ValueError, match="VALIDATION_ERROR"):
        service.create_job({})

    job_id = service.create_job({"source_url": "https://example.com/video.mp4"})
    assert job_id is not None
    
    job_data = service.get_job(job_id)
    assert job_data is not None
    assert job_data["status"] == "PENDING"

    result = service.process_job(job_id)
    assert result.status == "COMPLETED"
    assert result.url is not None
    assert result.file_size_bytes > 0

    updated_job = service.get_job(job_id)
    assert updated_job["status"] == "COMPLETED"

def test_job_service_error_handling():
    """Verify system handles processing failures gracefully without corruption."""
    service = MockJobService()
    job_id = service.create_job({"source_url": "https://example.com/corrupted.mp4", "simulated_failure": True})
    
    result = service.process_job(job_id)
    assert result.status == "FAILED"
    assert result.error == "PROCESSING_FAILED"
    assert result.file_size_bytes == 0

def test_rate_limiter_concurrency():
    """Verify thread-safe token bucket rate enforcement."""
    limiter = RateLimiterContract(capacity=5, refill_rate_per_sec=1.0)
    consumed_count = []

    def worker():
        for _ in range(5):
            if limiter.consume(1):
                consumed_count.append(1)
            time.sleep(0.01)

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(consumed_count) <= 7

def test_concurrency_storage_idempotency():
    """Test idempotent atomic storage keys under thread contention."""
    storage = {}
    lock = threading.Lock()
    results = []

    def atomic_put_if_absent(key: str, value: str) -> bool:
        with lock:
            if key in storage:
                return False
            storage[key] = value
            return True

    def worker(worker_id: int):
        success = atomic_put_if_absent("global_resource_key", f"worker_{worker_id}")
        if success:
            results.append(worker_id)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 1
    assert len(storage) == 1
