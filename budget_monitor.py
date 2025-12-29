"""
Budget monitoring for free trial optimization
Tracks API usage and prevents overspending
"""
import time
from datetime import datetime

class BudgetMonitor:
    def __init__(self, max_budget=10.0):
        self.max_budget = max_budget
        self.total_calls = 0
        self.estimated_cost = 0.0
        self.start_time = time.time()
        self.call_log = []
        
    def log_call(self, cost=0.009, tokens_used=300):
        """Log an API call with estimated cost"""
        self.total_calls += 1
        self.estimated_cost += cost
        self.call_log.append({
            'timestamp': datetime.now(),
            'cost': cost,
            'tokens': tokens_used,
            'cumulative': self.estimated_cost
        })
        
    def check_budget(self):
        """Check if we're within budget"""
        return self.estimated_cost < self.max_budget
    
    def get_stats(self):
        """Get current statistics"""
        elapsed = time.time() - self.start_time
        return {
            'calls': self.total_calls,
            'cost': self.estimated_cost,
            'budget': self.max_budget,
            'remaining': self.max_budget - self.estimated_cost,
            'elapsed_min': elapsed / 60,
            'calls_per_min': self.total_calls / (elapsed / 60) if elapsed > 0 else 0
        }
    
    def print_summary(self):
        """Print budget summary"""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("💰 BUDGET SUMMARY")
        print("="*60)
        print(f"API Calls: {stats['calls']}")
        print(f"Cost: ${stats['cost']:.2f} / ${stats['budget']:.2f}")
        print(f"Remaining: ${stats['remaining']:.2f}")
        print(f"Time: {stats['elapsed_min']:.1f} min")
        print(f"Rate: {stats['calls_per_min']:.1f} calls/min")
        print("="*60)
