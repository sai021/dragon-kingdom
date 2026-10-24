"""Batch connection gate: re-enumeration must never start a second flash."""
import time


class BatchGate:
    def __init__(self):
        self.enabled=False;self.waiting=False;self.background=set();self.absent=0;self.settle=0
    def arm(self):
        self.enabled=True;self.waiting=False;self.background=set();self.absent=0
    def stop(self):self.enabled=False
    def choose(self,ports,busy=False,now=None):
        if not self.enabled or busy:return None
        now=time.monotonic() if now is None else now
        ports=set(ports)
        if self.waiting:
            if now<self.settle:return None
            self.absent=self.absent+1 if ports<=self.background else 0
            if self.absent<2:return None
            self.waiting=False;self.background=ports;return None
        candidates=ports-self.background
        if len(candidates)>1:
            self.stop();raise ValueError('Several ESP32 ports are connected. Connect only one board, then enable Auto again.')
        if not candidates:return None
        port=candidates.pop();self.background=ports-{port};self.waiting=True;self.absent=0
        return port
    def finished(self,now=None):
        self.settle=(time.monotonic() if now is None else now)+3
