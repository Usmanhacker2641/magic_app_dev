"""
Optimized configuration for free trial usage
Dynamic retries, beautiful designs, fast generation
"""

# ============= FREE TRIAL BUDGET =============
FREE_TRIAL_CREDIT = 18.0
MAX_BUDGET_PER_APP = 10.0
TARGET_TIME_MINUTES = 15
TARGET_MIN_TIME = 5      # Simple apps
TARGET_MAX_TIME = 30     # Complex apps

# ============= TOKEN LIMITS =============
MAX_TOKENS_PER_REQUEST = 1800  # Increased for better design output
TEMPERATURE = 0.7
CONTEXT_WINDOW = 4096

# ============= DYNAMIC RETRY STRATEGY =============
RETRY_BY_COMPLEXITY = {
    'html': 2,    # Simple structure
    'css': 3,     # Styling needs refinement
    'js': 4,      # Logic may need more tries
    'md': 1,      # Documentation is simple
}
API_DELAY_SECONDS = 1.2  # Faster for quick generation

# ============= DESIGN REQUIREMENTS =============
DESIGN_KEYWORDS = [
    'gradient', 'shadow', 'animation', 'transition',
    'responsive', 'modern', 'colorful', 'beautiful',
    'hover effects', 'smooth scrolling'
]

# ============= FILE ORGANIZATION =============
USE_FOLDERS = True
FOLDER_STRUCTURE = {
    'css': 'css/',
    'js': 'js/',
    'assets': 'assets/',
    'images': 'assets/images/',
}

# ============= CODE QUALITY =============
NO_COMMENTS = True           # Production-ready code only
NO_PLACEHOLDERS = True       # Complete implementation
MIN_FILE_SIZES = {
    'html': 200,   # Substantial HTML
    'css': 100,    # Good styling
    'js': 50,      # Functional code
    'md': 30,      # Brief docs
}

# ============= OPTIMIZATION FLAGS =============
USE_COMPACT_PROMPTS = True
ENABLE_BUDGET_CHECKS = True
ENABLE_DYNAMIC_RETRIES = True
PARALLEL_FILE_GENERATION = False

def get_time_estimate(complexity='medium'):
  
    times = {'simple': 5, 'medium': 15, 'complex': 30}
    return times.get(complexity, 15)

# ============= RATE LIMITS =============
# Groq/OpenAI typical limits (check docs for current values)
MAX_REQUESTS_PER_MINUTE = 30
MAX_TOKENS_PER_MINUTE = 8000
MAX_REQUESTS_PER_DAY = 1000

# ============= COST ESTIMATES =============
COST_PER_SIMPLE_CALL = 0.009   # 300 tokens
COST_PER_AGENT_CALL = 0.012    # Agent calls use more tokens
COST_PER_LARGE_CALL = 0.030    # 1000 tokens

# ============= OPTIMIZATION FLAGS =============
USE_COMPACT_PROMPTS = True     # Minimize prompt tokens
ENABLE_BUDGET_CHECKS = True    # Stop if budget exceeded
ENABLE_CACHING = False         # Cache responses (if supported)
PARALLEL_FILE_GENERATION = False  # Sequential is safer for free tier

# ============= FILE VALIDATION =============
MIN_FILE_SIZE_BYTES = 50       # Minimum acceptable file size
VALIDATION_DELAY_SECONDS = 1.0 # Wait before validation

# ============= WARNINGS =============
WARNING_THRESHOLD = 0.8        # Warn at 80% budget
CRITICAL_THRESHOLD = 0.95      # Stop at 95% budget

def get_estimated_calls_for_budget(budget=MAX_BUDGET_PER_APP):
    """Calculate how many calls we can afford"""
    return int(budget / COST_PER_SIMPLE_CALL)

def get_estimated_time_minutes(num_calls, delay=API_DELAY_SECONDS):
    """Estimate how long generation will take"""
    return (num_calls * delay) / 60

def print_config_summary():
    """Print configuration summary"""
    calls = get_estimated_calls_for_budget()
    time_est = get_estimated_time_minutes(calls)
    
    print("\n" + "="*60)
    print("⚙️  FREE TRIAL OPTIMIZATION CONFIG")
    print("="*60)
    print(f"Budget per app: ${MAX_BUDGET_PER_APP}")
    print(f"Estimated calls: ~{calls}")
    print(f"Max tokens/call: {MAX_TOKENS_PER_REQUEST}")
    print(f"Retries per file: {MAX_RETRIES_PER_FILE}")
    print(f"API delay: {API_DELAY_SECONDS}s")
    print(f"Target time: {TARGET_TIME_MINUTES} min")
    print(f"Estimated time: {time_est:.1f} min")
    print("="*60)
