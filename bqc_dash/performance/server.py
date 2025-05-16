import time


# Performance tracking
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.callback_times = {}

    def start_timer(self, name):
        """Start timing a callback or operation"""
        return time.time()

    def end_timer(self, name, start_time):
        """End timing and record the result"""
        duration = time.time() - start_time
        if name not in self.callback_times:
            self.callback_times[name] = []
        self.callback_times[name].append(duration)
        # Keep only last 100 measurements
        if len(self.callback_times[name]) > 100:
            self.callback_times[name].pop(0)
        return duration

    def get_avg_time(self, name):
        """Get average execution time for a callback"""
        if name in self.callback_times and self.callback_times[name]:
            return sum(self.callback_times[name]) / len(self.callback_times[name])
        return 0

    def get_max_time(self, name):
        """Get maximum execution time for a callback"""
        if name in self.callback_times and self.callback_times[name]:
            return max(self.callback_times[name])
        return 0

    def get_metrics(self):
        """Get all metrics as a dictionary"""
        metrics = {}
        for name in self.callback_times:
            if self.callback_times[name]:
                metrics[name] = {
                    "avg": self.get_avg_time(name),
                    "max": self.get_max_time(name),
                    "last": self.callback_times[name][-1],
                    "count": len(self.callback_times[name]),
                }
        return metrics
