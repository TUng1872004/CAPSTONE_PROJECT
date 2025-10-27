from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from prometheus_client import ProcessCollector, PlatformCollector, GCCollector



class ServiceMetrics:
    
    def __init__(self, service_name: str, registry: CollectorRegistry | None = None):
        self.service_name = service_name
        self.registry = registry or CollectorRegistry()

        if ProcessCollector and PlatformCollector and GCCollector:
            try:
                ProcessCollector(registry=self.registry)
                PlatformCollector(registry=self.registry)
                GCCollector(registry=self.registry)
            except Exception:
                pass

        self.request_total = Counter(
            "service_requests_total",
            "Total number of service requests",
            ["service", "endpoint", "status"],
            registry=self.registry,
        )
        
        self.request_duration = Histogram(
            "service_request_duration_seconds",
            "Request duration in seconds",
            ["service", "endpoint"],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
            registry=self.registry,
        )
        
        self.request_errors = Counter(
            "service_request_errors_total",
            "Total number of request errors",
            ["service", "endpoint", "error_type"],
            registry=self.registry,
        )
        
        self.cpu_usage = Gauge(
            "service_cpu_usage_percent",
            "CPU usage percentage (0-100)",
            ["service"],
            registry=self.registry,
        )
        
        self.memory_usage = Gauge(
            "service_memory_bytes",
            "RAM usage in bytes",
            ["service"],
            registry=self.registry,
        )
        
        self.memory_percent = Gauge(
            "service_memory_usage_percent",
            "RAM usage percentage (0-100)",
            ["service"],
            registry=self.registry,
        )
        
        self.gpu_memory_used = Gauge(
            "service_gpu_memory_used_bytes",
            "GPU VRAM used in bytes",
            ["service", "gpu_id"],
            registry=self.registry,
        )
        
        self.gpu_memory_total = Gauge(
            "service_gpu_memory_total_bytes",
            "Total GPU VRAM in bytes",
            ["service", "gpu_id"],
            registry=self.registry,
        )
        
        self.gpu_memory_free = Gauge(
            "service_gpu_memory_free_bytes",
            "Free GPU VRAM in bytes",
            ["service", "gpu_id"],
            registry=self.registry,
        )
        
        self.gpu_utilization = Gauge(
            "service_gpu_utilization_percent",
            "GPU memory utilization percentage (0-100)",
            ["service", "gpu_id"],
            registry=self.registry,
        )
    
    def track_request(self, endpoint: str, status: str):
        self.request_total.labels(
            service=self.service_name,
            endpoint=endpoint,
            status=status
        ).inc()
    
    def track_error(self, endpoint: str, error_type: str):
        self.request_errors.labels(
            service=self.service_name,
            endpoint=endpoint,
            error_type=error_type
        ).inc()

    def observe_request_duration(self, endpoint: str, duration_seconds: float) -> None:
        self.request_duration.labels(
            service=self.service_name,
            endpoint=endpoint,
        ).observe(duration_seconds)
    
    def update_cpu_usage(self, usage_percent: float):
        self.cpu_usage.labels(service=self.service_name).set(usage_percent)
    
    def update_memory_usage(self, bytes_used: float, percent_used: float | None = None):
        self.memory_usage.labels(service=self.service_name).set(bytes_used)
        if percent_used is not None:
            self.memory_percent.labels(service=self.service_name).set(percent_used)
    
    def update_gpu_metrics(
        self,
        gpu_id: int,
        memory_used: int,
        memory_total: int,
        utilization: float
    ):
        gpu_id_str = str(gpu_id)
        
        self.gpu_memory_used.labels(
            service=self.service_name,
            gpu_id=gpu_id_str
        ).set(memory_used)
        
        self.gpu_memory_total.labels(
            service=self.service_name,
            gpu_id=gpu_id_str
        ).set(memory_total)
        
        self.gpu_memory_free.labels(
            service=self.service_name,
            gpu_id=gpu_id_str
        ).set(memory_total - memory_used)
        
        self.gpu_utilization.labels(
            service=self.service_name,
            gpu_id=gpu_id_str
        ).set(utilization)
    
    def get_metrics(self) -> bytes:
        return generate_latest(self.registry)
    
    def get_content_type(self) -> str:
        return CONTENT_TYPE_LATEST
