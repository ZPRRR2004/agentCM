"""Keep the service alive for open pages and experiments still running."""
import threading
import time


class BrowserSessions:
    def __init__(self, idle_timeout=30, startup_timeout=120, clock=time.monotonic):
        self.idle_timeout = idle_timeout
        self.clock = clock
        self.deadline = clock() + startup_timeout
        self.connections = {}
        self.lock = threading.Lock()
        self.stopping = False

    def open(self, identity):
        with self.lock:
            if self.stopping:
                raise ValueError('工作台正在停止，请从项目入口重新打开')
            old = self.connections.get(identity)
            if old:
                old.set()
            connection = threading.Event()
            self.connections[identity] = connection
            self.deadline = None
            return connection

    def close(self, identity, connection=None):
        with self.lock:
            current = self.connections.get(identity)
            if current is None or (connection is not None and current is not connection):
                return
            current.set()
            del self.connections[identity]
            if not self.connections:
                self.deadline = self.clock() + self.idle_timeout

    def should_stop(self, *, busy=False):
        with self.lock:
            if not busy and self.deadline is not None and self.clock() >= self.deadline:
                self.stopping = True
            return self.stopping

    def close_all(self):
        with self.lock:
            self.stopping = True
            for connection in self.connections.values():
                connection.set()
            self.connections.clear()

    def count(self):
        with self.lock:
            return len(self.connections)
