# Nuxt Scraper

Extract Nuxt data from Nuxt.js applications using [Playwright](https://playwright.dev/python/). Supports both `#__NUXT_DATA__` element extraction (Nuxt 3) and `window.__NUXT__` object extraction (Nuxt 2 and some Nuxt 3 configurations). Navigate to a URL, optionally run steps (click, fill, wait, scroll, etc.), then get the page's Nuxt data as JSON.

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "User Interface"
        A[extract_nuxt_data] --> B[NuxtDataExtractor]
        C[NavigationStep] --> B
        D[StealthConfig] --> B
    end
    
    subgraph "Core Engine"
        B --> E[Browser Management]
        B --> F[Navigation Engine]
        B --> G[Data Extraction]
        
        E --> H[Playwright Browser]
        E --> I[Anti-Detection]
        
        F --> J[Step Execution]
        F --> K[Calendar Selection]
        
        G --> L[Combined Extraction]
        G --> M[Legacy Extraction]
    end
    
    subgraph "Data Processing"
        L --> N[Parser Engine]
        M --> N
        N --> O[JSON Parsing]
        N --> P[Nuxt 3 Deserialization]
        
        P --> Q[Hydration Engine]
        Q --> R[Special Types Handler]
        Q --> S[Circular Ref Prevention]
    end
    
    subgraph "Output"
        O --> T[Raw JSON Data]
        P --> U[Deserialized Objects]
        T --> V[Final Result]
        U --> V
    end
    
    style B fill:#e1f5fe
    style G fill:#f3e5f5
    style P fill:#e8f5e8
    style V fill:#fff3e0
```

## 🔄 Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Extractor as NuxtDataExtractor
    participant Browser as Playwright Browser
    participant Page as Web Page
    participant Parser as Parser Engine
    participant Hydrator as Hydration Engine
    
    User->>Extractor: extract_nuxt_data(url, steps, options)
    Extractor->>Browser: Launch browser with stealth config
    Browser->>Page: Navigate to URL
    
    alt Navigation Steps Provided
        loop For each step
            Extractor->>Page: Execute navigation step
            Page-->>Extractor: Step completed
        end
    end
    
    Extractor->>Page: Execute extraction script
    Page->>Page: Try #__NUXT_DATA__ element
    Page->>Page: Try window.__NUXT__ object
    Page-->>Extractor: Return extraction result
    
    Extractor->>Parser: Parse extraction result
    
    alt Deserialization Enabled
        Parser->>Hydrator: Deserialize Nuxt 3 data
        Hydrator->>Hydrator: Resolve references with caching
        Hydrator->>Hydrator: Handle special types ($d, $s, $m, $b, $r)
        Hydrator-->>Parser: Return hydrated data
    else Deserialization Disabled
        Parser->>Parser: Return raw JSON data
    end
    
    Parser-->>Extractor: Return processed data
    Extractor-->>User: Final result
```

## 🧩 Component Interaction

```mermaid
graph TB
    subgraph "Public API Layer"
        API1[extract_nuxt_data] 
        API2[NuxtDataExtractor]
        API3[NavigationStep]
        API4[StealthConfig]
    end
    
    subgraph "Core Processing Layer"
        CORE1[Browser Manager]
        CORE2[Navigation Engine]
        CORE3[Extraction Engine]
        CORE4[Parser Engine]
    end
    
    subgraph "Browser Interaction Layer"
        BROWSER1[Playwright Browser]
        BROWSER2[Page Controller]
        BROWSER3[Element Interactions]
    end
    
    subgraph "Data Processing Layer"
        DATA1[JSON Parser]
        DATA2[Nuxt 3 Deserializer]
        DATA3[Hydration Engine]
        DATA4[Type Converters]
    end
    
    subgraph "Anti-Detection Layer"
        AD1[Stealth Scripts]
        AD2[Human Simulation]
        AD3[Randomization]
        AD4[Proxy Management]
    end
    
    API1 --> API2
    API2 --> CORE1
    API2 --> CORE2
    API2 --> CORE3
    API3 --> CORE2
    API4 --> AD1
    API4 --> AD2
    
    CORE1 --> BROWSER1
    CORE2 --> BROWSER2
    CORE3 --> BROWSER2
    CORE3 --> CORE4
    
    BROWSER1 --> BROWSER2
    BROWSER2 --> BROWSER3
    
    CORE4 --> DATA1
    CORE4 --> DATA2
    DATA2 --> DATA3
    DATA3 --> DATA4
    
    AD1 --> BROWSER1
    AD2 --> BROWSER3
    AD3 --> BROWSER1
    AD4 --> BROWSER1
    
    style API2 fill:#e1f5fe
    style CORE3 fill:#f3e5f5
    style DATA2 fill:#e8f5e8
    style AD2 fill:#fff3e0
```

## Installation

### From PyPI (when published):
```bash
pip install nuxt_scraper
playwright install chromium
```

### From GitHub:
```bash
pip install git+https://github.com/rahjooh/nuxt_scraper.git
playwright install chromium
```

### For development:
```bash
git clone https://github.com/rahjooh/nuxt_scraper.git
cd nuxt_scraper
pip install -e ".[dev]"
playwright install chromium
```

## Usage

Nuxt Scraper provides flexible ways to extract data, from simple one-liners to complex, multi-step navigation with advanced anti-detection. Below are examples covering common scenarios.

### Basic Extraction

For straightforward cases where you just need to navigate to a URL and extract Nuxt data without complex interactions, use the `extract_nuxt_data` convenience function. The scraper automatically detects and extracts from both `#__NUXT_DATA__` elements and `window.__NUXT__` objects.

```python
from nuxt_scraper import extract_nuxt_data
from nuxt_scraper.utils import StealthConfig

# Simple extraction - automatically detects both #__NUXT_DATA__ and window.__NUXT__
data = extract_nuxt_data("https://your-nuxt-app.com")
print("Extraction Data:", data)

# Extraction with anti-detection and proxy
stealth_config = StealthConfig(random_delays=True, human_typing=True)
proxy_config = {"server": "http://user:password@proxy.example.com:8080"}

data_with_stealth = extract_nuxt_data(
    "https://your-advanced-nuxt-app.com",
    stealth_config=stealth_config,
    proxy=proxy_config
)
print("Stealthy Extraction Data:", data_with_stealth)

# Force legacy mode (only #__NUXT_DATA__ element) if needed
data_legacy = extract_nuxt_data(
    "https://your-nuxt3-app.com",
    use_combined_extraction=False  # Only try #__NUXT_DATA__ element
)
print("Legacy Mode Data:", data_legacy)
```

### Advanced Extraction with `NuxtDataExtractor`

For more control over the browser session, including persistent sessions, custom browser arguments, and advanced debugging, use the `NuxtDataExtractor` class as an asynchronous context manager.

```python
import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep
from nuxt_scraper.utils import StealthConfig

async def advanced_extraction_example():
    custom_stealth = StealthConfig(
        random_delays=True, min_action_delay_ms=200, max_action_delay_ms=2000,
        human_typing=True, typing_speed_wpm=60,
        mouse_movement=True, randomize_viewport=True,
    )
    custom_proxy = {"server": "http://proxy.example.com:8080"}

    async with NuxtDataExtractor(
        headless=False, # Run browser in headful mode for debugging
        timeout=60000, # Longer timeout for complex pages
        browser_type="chromium",
        ignore_https_errors=True,
        stealth_config=custom_stealth,
        proxy=custom_proxy,
    ) as extractor:
        steps = [
            NavigationStep.click("button[data-accept-cookies]"),
            NavigationStep.wait(".main-content-loaded", timeout=10000),
        ]
        
        # Combined extraction (default) - tries both methods automatically
        data = await extractor.extract(
            "https://your-complex-site.com",
            steps=steps,
            use_combined_extraction=True,  # Default: tries both #__NUXT_DATA__ and window.__NUXT__
        )
        
        # Or use legacy mode for Nuxt 3 sites with only #__NUXT_DATA__
        data_legacy = await extractor.extract(
            "https://your-nuxt3-site.com",
            steps=steps,
            use_combined_extraction=False,  # Only try #__NUXT_DATA__ element
            wait_for_nuxt=True,
            wait_for_nuxt_timeout=20000,
        )
        
    print("Advanced Extraction Data:", data)

if __name__ == "__main__":
    asyncio.run(advanced_extraction_example())
```

### Nuxt Data Extraction Methods

Nuxt Scraper supports both modern and legacy Nuxt.js data extraction methods:

#### Combined Extraction (Recommended)
By default, the scraper uses **combined extraction** which automatically tries both methods:

1. **`#__NUXT_DATA__` Element** (Nuxt 3 standard): Extracts JSON from a script element with ID `__NUXT_DATA__`
2. **`window.__NUXT__` Object** (Nuxt 2 and some Nuxt 3): Extracts directly from the JavaScript `window.__NUXT__` global object

```python
from nuxt_scraper import extract_nuxt_data

# Automatically tries both methods - works with most Nuxt apps
data = extract_nuxt_data("https://any-nuxt-app.com")

# Explicitly enable combined extraction (default behavior)
data = extract_nuxt_data("https://nuxt-app.com", use_combined_extraction=True)
```

#### Legacy Mode
For sites that specifically require only the `#__NUXT_DATA__` element method:

```python
# Only try #__NUXT_DATA__ element (legacy mode)
data = extract_nuxt_data(
    "https://nuxt3-only-app.com", 
    use_combined_extraction=False,
    wait_for_nuxt=True  # Wait for the element to appear
)
```

#### Manual Method Selection with NuxtDataExtractor
```python
import asyncio
from nuxt_scraper import NuxtDataExtractor

async def method_selection_example():
    async with NuxtDataExtractor() as extractor:
        # Combined extraction (tries both methods)
        data1 = await extractor.extract("https://app1.com", use_combined_extraction=True)
        
        # Legacy mode (element only)
        data2 = await extractor.extract("https://app2.com", use_combined_extraction=False)
        
        return data1, data2

data1, data2 = asyncio.run(method_selection_example())
```

The combined extraction method includes intelligent retry logic and will automatically use whichever method works for the target site, making it compatible with a wider range of Nuxt.js applications.

### Nuxt 3 Deserialization

Nuxt Scraper features a **completely rewritten deserialization engine** that properly handles Nuxt 3's serialized data format using hydration-based processing. This solves critical issues with exponential data expansion and provides robust support for complex data structures.

#### 🚀 **Recent Improvements (v0.2.3+)**

The deserialization system has been completely rebuilt to follow Nuxt 3's actual serialization format (based on the `devalue` library):

- **✅ Prevents exponential data expansion** - No more 1GB+ files from small datasets
- **✅ Proper circular reference handling** - Uses caching to prevent infinite loops  
- **✅ Full devalue format support** - Handles all special types (Date, Set, Map, BigInt, RegExp)
- **✅ Performance optimized** - Efficient hydration instead of naive recursive expansion
- **✅ Memory efficient** - Smart caching prevents duplicate processing

#### Automatic Deserialization (Default)
```python
from nuxt_scraper import extract_nuxt_data

# Automatically deserializes Nuxt 3 data with the new hydration engine
data = extract_nuxt_data("https://nuxt3-app.com/race-details")
print(data)  # Fully resolved, properly sized data structure

# Example: Racing data that previously caused 1GB+ files now stays under 50MB
racing_data = extract_nuxt_data("https://racenet.com.au/form-guide/...")
print(f"Data size is reasonable: {len(str(racing_data)) / 1024 / 1024:.2f} MB")
```

#### Manual Control & Comparison
```python
# Get both raw and deserialized data for comparison
raw_data = extract_nuxt_data(
    "https://nuxt3-app.com/race-details",
    deserialize_nuxt3=False  # Raw serialized format
)

deserialized_data = extract_nuxt_data(
    "https://nuxt3-app.com/race-details", 
    deserialize_nuxt3=True   # Hydrated format (default)
)

# Manually deserialize later if needed
from nuxt_scraper import deserialize_nuxt3_data
resolved_data = deserialize_nuxt3_data(raw_data, is_json_string=False)
```

#### Advanced Usage with Size Monitoring
```python
import asyncio
import json
from nuxt_scraper import NuxtDataExtractor

async def compare_serialization_methods():
    async with NuxtDataExtractor() as extractor:
        # Extract raw serialized data
        raw_data = await extractor.extract(
            "https://complex-nuxt3-app.com",
            deserialize_nuxt3=False
        )
        
        # Extract with new hydration engine
        hydrated_data = await extractor.extract(
            "https://complex-nuxt3-app.com",
            deserialize_nuxt3=True
        )
        
        # Compare sizes
        raw_size = len(json.dumps(raw_data, default=str))
        hydrated_size = len(json.dumps(hydrated_data, default=str))
        
        print(f"Raw data: {raw_size / 1024 / 1024:.2f} MB")
        print(f"Hydrated data: {hydrated_size / 1024 / 1024:.2f} MB")
        print(f"Expansion ratio: {hydrated_size / raw_size:.2f}x")
        
        return raw_data, hydrated_data

asyncio.run(compare_serialization_methods())
```

#### How the New Deserialization Works

```mermaid
graph TD
    subgraph "Nuxt 3 Deserialization Engine"
        A[Raw Nuxt 3 Data Array] --> B{Is Array Format?}
        B -->|Yes| C[Initialize Cache]
        B -->|No| D[Return Raw Data]
        
        C --> E[Start Hydration from Index 1]
        E --> F{Value Type?}
        
        F -->|Integer| G[Index Reference]
        F -->|Object| H[Check Special Types]
        F -->|Array| I[Hydrate Each Item]
        F -->|Primitive| J[Return As-Is]
        
        G --> K{In Cache?}
        K -->|Yes| L[Return Cached]
        K -->|No| M[Resolve Reference]
        M --> N[Cache Result]
        N --> F
        
        H --> O{Special Type?}
        O -->|$d| P[Convert to DateTime]
        O -->|$s| Q[Convert to Set]
        O -->|$m| R[Convert to Map/Dict]
        O -->|$b| S[Convert to BigInt]
        O -->|$r| T[Convert to RegExp]
        O -->|Regular| U[Hydrate Object Properties]
        
        P --> V[Cache & Return]
        Q --> V
        R --> V
        S --> V
        T --> V
        U --> V
        I --> V
        J --> V
        L --> V
        
        V --> W[Hydrated Result]
    end
    
    style C fill:#e3f2fd
    style K fill:#f3e5f5
    style O fill:#e8f5e8
    style W fill:#fff3e0
```

The new hydration engine follows Nuxt 3's actual serialization format using the `devalue` library standard:

**🔧 Supported Special Types:**
- **`{"$d": 1672531200000}`** → `datetime` objects (timestamps)
- **`{"$s": [1, 2, 3]}`** → Python `set` objects  
- **`{"$m": [[1, 2], [3, 4]]}`** → Python `dict` objects (Maps)
- **`{"$b": "123456789"}`** → Python `int` objects (BigInt)
- **`{"$r": "/pattern/gi"}`** → Python `re.Pattern` objects (RegExp)

**📊 Example Transformation:**

**Before (serialized):**
```json
[
  {"state": 1, "data": 2},
  {"meetings": 3, "timestamp": {"$d": 1672531200000}},
  {"venue": "Albion Park", "races": [4, 5]},
  {"race": 1, "name": "Race 1", "runners": {"$s": [6, 7]}},
  {"race": 2, "name": "Race 2", "distance": {"$b": "1200"}},
  {"id": 101, "name": "Horse A"},
  {"id": 102, "name": "Horse B"}
]
```

**After (hydrated):**
```json
{
  "meetings": {
    "venue": "Albion Park",
    "races": [
      {
        "race": 1, 
        "name": "Race 1",
        "runners": [
          {"id": 101, "name": "Horse A"},
          {"id": 102, "name": "Horse B"}
        ]
      },
      {
        "race": 2,
        "name": "Race 2", 
        "distance": 1200
      }
    ]
  },
  "timestamp": "2023-01-01T00:00:00"
}
```

**🛡️ Key Features:**

1. **Circular Reference Prevention**: Uses early caching to handle self-referencing objects
2. **Memory Efficient**: Each value is processed only once and cached
3. **Type Preservation**: Maintains proper Python types for dates, numbers, etc.
4. **Error Resilient**: Graceful fallbacks for malformed special types
5. **Performance Optimized**: O(n) complexity instead of exponential expansion

#### Troubleshooting Large Data Issues

If you encounter unexpectedly large deserialized data:

```python
# 1. Compare raw vs deserialized sizes
raw = extract_nuxt_data(url, deserialize_nuxt3=False)
deserialized = extract_nuxt_data(url, deserialize_nuxt3=True)

print(f"Raw: {len(str(raw)):,} chars")
print(f"Deserialized: {len(str(deserialized)):,} chars")

# 2. Analyze the data structure
from nuxt_scraper.parser import deserialize_nuxt3_data
import logging

# Enable debug logging to see cache statistics
logging.getLogger('nuxt_scraper.parser').setLevel(logging.INFO)

result = deserialize_nuxt3_data(raw, is_json_string=False)
# Look for "Cache size: X" in the logs - should be reasonable
```

#### Migration from Old Deserialization

If you were using the old deserialization system and experiencing issues:

```python
# OLD (caused exponential expansion):
# The old system would create massive files from reference resolution

# NEW (efficient hydration):
data = extract_nuxt_data(
    "https://your-problematic-site.com",
    deserialize_nuxt3=True  # Now uses the new hydration engine
)

# Expected improvements:
# - 1GB+ files → <50MB typical
# - Minutes of processing → Seconds
# - Memory exhaustion → Efficient processing
# - Circular reference errors → Proper handling
```

### 🔧 Technical Implementation Details

#### Deserialization Algorithm

The new hydration engine implements a proper Nuxt 3 deserialization algorithm based on the `devalue` library specification:

```python
def hydrate_value(data_array, index_or_value, cache):
    """
    Core hydration logic:
    1. Check if value is an integer index → resolve from data_array
    2. Check cache to prevent circular references and duplicate work
    3. Handle special devalue types ($d, $s, $m, $b, $r)
    4. Recursively hydrate nested structures
    5. Cache result before returning
    """
    
    # Example usage:
    from nuxt_scraper.parser import deserialize_nuxt3_data
    
    # Raw Nuxt 3 data array
    raw_data = [
        {"state": 1},           # Index 0: metadata
        {"users": [2, 3]},      # Index 1: root object
        {"id": 1, "name": "Alice", "created": {"$d": 1672531200000}},  # Index 2
        {"id": 2, "name": "Bob", "tags": {"$s": [4, 5]}}              # Index 3
        "admin",                # Index 4
        "user"                  # Index 5
    ]
    
    # Hydration process:
    # 1. Start from index 1 (root)
    # 2. Resolve users array: [2, 3] → [hydrate(2), hydrate(3)]
    # 3. Hydrate index 2: resolve {"$d": ...} → datetime object
    # 4. Hydrate index 3: resolve {"$s": [4, 5]} → {"admin", "user"} set
    # 5. Cache all results to prevent re-processing
    
    result = deserialize_nuxt3_data(raw_data, is_json_string=False)
```

#### Performance Characteristics

| Metric | Old System | New Hydration Engine |
|--------|------------|---------------------|
| **Time Complexity** | O(n²) to O(n!) | O(n) |
| **Memory Usage** | Exponential growth | Linear with caching |
| **Circular References** | Infinite loops | Properly handled |
| **Large Datasets** | 1GB+ files | Reasonable sizes |
| **Processing Time** | Minutes | Seconds |

#### Best Practices

**✅ Recommended Usage:**
```python
# Always use the default (deserialize_nuxt3=True) for production
data = extract_nuxt_data("https://your-site.com")

# For debugging, compare both formats
raw = extract_nuxt_data("https://your-site.com", deserialize_nuxt3=False)
hydrated = extract_nuxt_data("https://your-site.com", deserialize_nuxt3=True)

# Monitor data sizes in production
import json
size_mb = len(json.dumps(data, default=str)) / 1024 / 1024
if size_mb > 100:  # Adjust threshold as needed
    print(f"⚠️ Large dataset detected: {size_mb:.2f} MB")
```

**❌ Avoid These Patterns:**
```python
# Don't manually implement deserialization
# The built-in engine handles all edge cases properly

# Don't disable deserialization unless you specifically need raw data
# The hydrated format is more useful for most applications

# Don't worry about performance with the new engine
# It's optimized for large, complex Nuxt 3 datasets
```

#### Debugging Deserialization Issues

```python
import logging
from nuxt_scraper import extract_nuxt_data

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('nuxt_scraper.parser')
logger.setLevel(logging.DEBUG)

# Extract with detailed logging
data = extract_nuxt_data("https://problematic-site.com")

# Look for log messages like:
# - "Deserializing Nuxt 3 data format using hydration"
# - "Successfully deserialized Nuxt 3 data. Cache size: X"
# - Warning messages about malformed special types
```

### Navigation Steps

```mermaid
graph LR
    subgraph "Navigation Step Types"
        A[Click] --> B[Fill]
        B --> C[Select]
        C --> D[Wait]
        D --> E[Scroll]
        E --> F[Hover]
        F --> G[Select Date]
    end
    
    subgraph "Step Execution Flow"
        H[Step List] --> I{For Each Step}
        I --> J[Apply Anti-Detection]
        J --> K[Execute Step Action]
        K --> L{Wait After Selector?}
        L -->|Yes| M[Wait for Element]
        L -->|No| N[Continue to Next]
        M --> N
        N --> O{More Steps?}
        O -->|Yes| I
        O -->|No| P[Complete]
    end
    
    subgraph "Anti-Detection Features"
        Q[Human Delays] --> R[Mouse Movement]
        R --> S[Human Typing]
        S --> T[Random Pauses]
    end
    
    J -.-> Q
    
    style I fill:#e1f5fe
    style K fill:#f3e5f5
    style P fill:#e8f5e8
```

`NavigationStep` objects define interactions with the web page before data extraction. They are chained in a list and executed sequentially. Each step can have an optional `wait_after_selector` to pause execution until a specific element appears after the step's action.

```python
from nuxt_scraper import NavigationStep
```

#### `NavigationStep.click(selector, timeout=5000, wait_after_selector=None)`

Clicks an element matching the given CSS `selector`.

```python
click_button = NavigationStep.click("button#submit-form", wait_after_selector=".form-submitted-message")
```

#### `NavigationStep.fill(selector, value, timeout=5000, wait_after_selector=None)`

Fills an input or textarea field with the specified `value`.

```python
fill_input = NavigationStep.fill("input[name='username']", "myusername", wait_after_selector="#username-validation-ok")
```

#### `NavigationStep.select(selector, value, timeout=5000, wait_after_selector=None)`

Selects an option in a dropdown (`<select>`) element by its `value`.

```python
select_dropdown = NavigationStep.select("select#country", "US", wait_after_selector="#state-dropdown-loaded")
```

#### `NavigationStep.wait(selector, timeout=10000, wait_after_selector=None)`

Waits for an element matching the `selector` to become visible on the page. Useful for ensuring dynamic content has loaded.

```python
wait_for_element = NavigationStep.wait("div.loading-spinner-hidden", timeout=15000)
```

#### `NavigationStep.scroll(selector, timeout=5000, wait_after_selector=None)`

Scrolls the element matching the `selector` into the viewport. Useful for triggering lazy-loaded content.

```python
scroll_to_footer = NavigationStep.scroll("footer#main-footer", wait_after_selector="#lazy-loaded-ads")
```

#### `NavigationStep.hover(selector, timeout=5000, wait_after_selector=None)`

Hover over an element matching the `selector`.

```python
hover_menu_item = NavigationStep.hover("li.menu-item-with-submenu", wait_after_selector=".submenu-visible")
```

#### `NavigationStep.select_date(target_date, calendar_selector, prev_month_selector, next_month_selector, month_year_display_selector, date_cell_selector, view_results_selector=None, timeout=15000, wait_after_selector=None)`

Selects a specific date from a calendar pop-up. This step intelligently navigates months until the `target_date` (format: YYYY-MM-DD) is found and clicked. You must provide specific selectors for the calendar components.

```python
import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep
from nuxt_scraper.utils import StealthConfig

async def select_date_example():
    # First, click the input that opens the calendar (if necessary)
    open_calendar_step = NavigationStep.click("input#date-picker-input")

    # Then, define the date selection step
    select_specific_date = NavigationStep.select_date(
        target_date="2026-03-15", # Example: March 15, 2026
        calendar_selector="div.calendar-popup", # Main calendar container
        prev_month_selector="button.prev-month", # Button to go to previous month
        next_month_selector="button.next-month", # Button to go to next month
        month_year_display_selector="div.month-year-display", # Element showing current month/year (e.g., "Feb 2026")
        date_cell_selector="div.day-cell", # General selector for individual date cells
        view_results_selector="button:has-text('View Results')", # Optional: button to click after date is selected
        timeout=20000, # Max timeout for this entire step
    )

    async with NuxtDataExtractor(headless=False, stealth_config=StealthConfig()) as extractor:
        data = await extractor.extract(
            "https://your-site-with-calendar.com",
            steps=[open_calendar_step, select_specific_date]
        )
    print("Data after date selection:", data)

if __name__ == "__main__":
    asyncio.run(select_date_example())
```

#### How to Find Calendar Selectors

To use `NavigationStep.select_date()` with any calendar widget, you need to identify the CSS selectors for each component. Here's a step-by-step guide:

**Step 1: Open Browser DevTools**
1. Navigate to the page with the calendar
2. Open DevTools (F12 or Right-click → Inspect)
3. Open the calendar widget

**Step 2: Identify Each Component**

1. **Calendar Container** (`calendar_selector`):
   - Right-click the calendar popup → Inspect
   - Find the outermost container element
   - Copy its CSS selector (right-click element → Copy → Copy selector)
   - Example: `.vdp-datepicker__calendar` or `div.calendar-popup`

2. **Month/Year Display** (`month_year_display_selector`):
   - Inspect the element showing "February 2025" or similar
   - Copy its selector
   - Example: `.vdp-datepicker__calendar header span.up` or `div.month-year`

3. **Previous Month Button** (`prev_month_selector`):
   - Inspect the "←" or "Prev" button
   - Copy its selector
   - Example: `.vdp-datepicker__calendar header .prev` or `button.prev-month`

4. **Next Month Button** (`next_month_selector`):
   - Inspect the "→" or "Next" button
   - Copy its selector
   - Example: `.vdp-datepicker__calendar header .next` or `button.next-month`

5. **Date Cells** (`date_cell_selector`):
   - Inspect any day cell (e.g., "15")
   - Copy the selector that matches ALL day cells (not just one)
   - Example: `span.cell.day` or `td.day-cell` or `div[class*="day"]`

6. **View Results Button** (`view_results_selector`, optional):
   - If there's a button to click after selecting date
   - Inspect and copy its selector
   - Example: `button:has-text('View Results')` or `button.apply`

**Step 3: Test Your Selectors**

Create a test script to verify selectors work:

```python
async with NuxtDataExtractor(headless=False) as extractor:
    await extractor.navigate("https://your-site.com")
    
    # Test each selector individually
    page = extractor._context.pages[0]
    
    # Test calendar appears
    calendar = await page.wait_for_selector(".vdp-datepicker__calendar", timeout=5000)
    print("✅ Calendar found")
    
    # Test month display
    month_display = await page.wait_for_selector(".vdp-datepicker__calendar header span.up", timeout=5000)
    print(f"✅ Month display: {await month_display.text_content()}")
    
    # Test navigation buttons
    next_btn = await page.wait_for_selector(".vdp-datepicker__calendar header .next", timeout=5000)
    print("✅ Next button found")
```

**Step 4: Common Patterns**

Different calendar libraries use different class names:

- **Vue DatePicker**: `.vdp-datepicker__calendar`, `.cell.day`
- **jQuery UI DatePicker**: `.ui-datepicker`, `.ui-datepicker-calendar td`
- **Material-UI**: `.MuiCalendarPicker-root`, `.MuiPickersDay-root`
- **Custom calendars**: Inspect and find unique class names or data attributes

**Step 5: Use Fallback Selectors**

If selectors might change, use multiple options:

```python
# Try multiple selectors (package handles this internally, but you can be explicit)
calendar_selector = ".vdp-datepicker__calendar, [class*='datepicker'], [class*='calendar']"
```

**Real-World Example:**

See `examples/racenet/01_historical_calendar_navigation.py` for a complete working example with actual selectors. The example shows how to organize selectors in a dictionary for maintainability:

```python
CALENDAR_SELECTORS = {
    "select_date_button": "a.tab:has-text('Select Date')",
    "calendar_selector": ".vdp-datepicker__calendar",
    "month_year_display": ".vdp-datepicker__calendar header span.up",
    "prev_month": ".vdp-datepicker__calendar header .prev",
    "next_month": ".vdp-datepicker__calendar header .next",
    "date_cell": "span.cell.day",
    "view_results": "button:has-text('View Results')",
}
```

### Anti-Detection Configuration (`StealthConfig`)

To make your scraping activities less detectable, `nuxt_scraper` offers a `StealthConfig` dataclass to fine-tune human-like behaviors. By default, anti-detection is enabled with sensible defaults. You can customize it as needed.

```python
from nuxt_scraper.utils import StealthConfig

# Enable only random delays and human typing
moderate_stealth = StealthConfig(
    random_delays=True,
    human_typing=True,
    mouse_movement=False, # Disable mouse movement for faster execution
    randomize_viewport=False,
    realistic_user_agent=False,
)

# Or a more aggressive configuration
paranoid_config = StealthConfig(
    random_delays=True,
    min_action_delay_ms=500,
    max_action_delay_ms=4000,
    human_typing=True,
    typing_speed_wpm=45,
    typo_chance=0.03,
    pause_chance=0.08,
    mouse_movement=True,
    randomize_viewport=True,
    realistic_user_agent=True,
)

# Pass to extractor:
# extractor = NuxtDataExtractor(stealth_config=paranoid_config)
# or
# data = extract_nuxt_data(url, stealth_config=moderate_stealth)
```

### Working with Dynamic Content and API Responses

When navigating calendars or interacting with dynamic content, `window.__NUXT__` may not update after user interactions. In these cases, the fresh data is often available through API responses. The `extract_with_api_capture()` method captures all API responses during navigation and extraction, allowing you to access the most up-to-date data.

#### Why Use API Response Capture?

On some sites (like racenet.com.au), when you select a date from a calendar:
- The page visually updates with new content
- An API call is made to fetch the new data
- **But** `window.__NUXT__` retains the original page load data (stale)

In these scenarios, you need to capture the API responses to get the correct data.

#### Basic Usage

```python
import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep, validate_meeting_date

async def extract_with_calendar_navigation():
    async with NuxtDataExtractor(headless=False) as extractor:
        # Use extract_with_api_capture instead of extract
        nuxt_data, api_responses = await extractor.extract_with_api_capture(
            "https://racenet.com.au/results/harness",
            steps=[
                NavigationStep.click("a.tab:has-text('Select Date')"),
                NavigationStep.select_date(
                    target_date="2025-02-20",
                    calendar_selector=".vdp-datepicker__calendar",
                    prev_month_selector=".vdp-datepicker__calendar .prev",
                    next_month_selector=".vdp-datepicker__calendar .next",
                    month_year_display_selector=".vdp-datepicker__calendar header span.up",
                    date_cell_selector=".vdp-datepicker__calendar .cell.day",
                    view_results_selector="button:has-text('View Results')",
                    timeout=20000
                )
            ]
        )
        
        # Find the specific API response containing the updated data
        meetings_response = extractor.find_api_response(
            api_responses,
            "meetingsGroupedByStartEndDate"  # URL pattern to search for
        )
        
        if meetings_response:
            data = meetings_response["data"]
            
            # Validate the date matches what we selected
            if validate_meeting_date(data, "2025-02-20"):
                print("✅ Date validation passed!")
                return data
            else:
                print("❌ Date mismatch - data may be stale")
        else:
            print("⚠️ API response not found, falling back to __NUXT__")
            return nuxt_data

if __name__ == "__main__":
    data = asyncio.run(extract_with_calendar_navigation())
    print(data)
```

#### Custom API Response Filtering

By default, `extract_with_api_capture()` captures JSON responses from `puntapi.com` or URLs containing `graphql`. You can provide a custom filter:

```python
def my_api_filter(response):
    """Capture all successful JSON responses from any API endpoint."""
    return (
        response.status == 200 
        and "api" in response.url.lower()
    )

nuxt_data, api_responses = await extractor.extract_with_api_capture(
    url,
    steps=steps,
    api_filter=my_api_filter
)
```

#### Finding Specific API Responses

The `find_api_response()` helper searches captured responses by URL pattern:

```python
# Find response with specific endpoint
meetings_data = extractor.find_api_response(api_responses, "meetingsGrouped")

# With fallback to first response if pattern not found
any_data = extractor.find_api_response(api_responses, "specific-endpoint", fallback_to_first=True)
```

#### Date Validation Utility

The `validate_meeting_date()` utility helps verify that extracted data matches your expected date. It handles both simple date formats (`YYYY-MM-DD`) and ISO datetime strings (`YYYY-MM-DDTHH:MM:SS.000Z`):

```python
from nuxt_scraper import validate_meeting_date

# With API response
if validate_meeting_date(api_response["data"], "2025-02-20"):
    print("Date matches!")

# With __NUXT__ data
if validate_meeting_date(nuxt_data, "2025-02-20", date_field="meetingDateLocal"):
    print("Date matches!")
```

#### Complete Calendar Navigation Pattern

For a complete example of calendar navigation with API capture, see `examples/racenet/01_historical_calendar_navigation.py`.

### Error Handling

`nuxt_scraper` defines a suite of custom exceptions, all inheriting from `NuxtFlowException`, to help you gracefully handle various failure scenarios. Key exceptions include `NuxtDataNotFound`, `NavigationStepFailed`, `ExtractionTimeout`, `DataParsingError`, `BrowserError`, `ProxyError`, and `DateNotFoundInCalendarError`.

## API Reference

### `extract_nuxt_data(url, steps=None, headless=True, timeout=30000, wait_for_nuxt=True, use_combined_extraction=True, deserialize_nuxt3=True, stealth_config=None, proxy=None)`

Convenience function: creates an extractor, opens the URL, and returns the parsed Nuxt data.

- **`url`** (`str`) – Target page URL.
- **`steps`** (`Optional[List[NavigationStep]]`) – List of `NavigationStep` instances to execute.
- **`headless`** (`bool`) – Run browser in headless mode (default `True`).
- **`timeout`** (`int`) – Default timeout for Playwright operations in milliseconds (default `30000`).
- **`wait_for_nuxt`** (`bool`) – If `True`, waits for the `#__NUXT_DATA__` element to be present. Only used when `use_combined_extraction=False` (default `True`).
- **`use_combined_extraction`** (`bool`) – If `True`, tries both `#__NUXT_DATA__` element and `window.__NUXT__` object extraction. If `False`, only tries `#__NUXT_DATA__` element (default `True`).
- **`deserialize_nuxt3`** (`bool`) – If `True`, automatically deserializes Nuxt 3 reactive references (default `True`).
- **`stealth_config`** (`Optional[StealthConfig]`) – Configuration for anti-detection features. Defaults to `StealthConfig()`.
- **`proxy`** (`Optional[Dict[str, str]]`) – Dictionary for proxy settings (e.g., `{"server": "http://ip:port", "username": "user", "password": "pass"}`).

### `NuxtDataExtractor`

Main class for controlled extraction and reuse of a browser session. Use as an `async with` context manager.

**Constructor:**

- **`headless`** (`bool`) – Run browser headless (default `True`).
- **`timeout`** (`int`) – Default timeout for Playwright operations in milliseconds (default `30000`).
- **`browser_type`** (`str`) – `"chromium"`, `"firefox"`, or `"webkit"` (default `"chromium"`).
- **`ignore_https_errors`** (`bool`) – Ignore HTTPS certificate errors (default `False`).
- **`viewport_width`** (`Optional[int]`) / **`viewport_height`** (`Optional[int]`) – Fixed viewport size in pixels. Ignored when `StealthConfig.randomize_viewport` is `True`.
- **`user_agent`** (`Optional[str]`) – Custom user agent string. Ignored when `StealthConfig.realistic_user_agent` is `True`.
- **`stealth_config`** (`Optional[StealthConfig]`) – Configuration for anti-detection features. Defaults to `StealthConfig()`.
- **`proxy`** (`Optional[Dict[str, str]]`) – Dictionary for proxy settings.

**Methods:**

- **`extract(url, steps=None, wait_for_nuxt=True, wait_for_nuxt_timeout=None, use_combined_extraction=True, deserialize_nuxt3=True)`**  
  Asynchronous method: navigates to `url`, runs `steps` (if any), then extracts and returns parsed Nuxt data. Uses combined extraction and Nuxt 3 deserialization by default.
- **`extract_sync(url, steps=None, wait_for_nuxt=True, wait_for_nuxt_timeout=None)`**  
  Synchronous wrapper that executes the `extract()` method in an event loop with combined extraction and deserialization enabled.
- **`extract_from_current_page(use_combined_extraction=True, deserialize_nuxt3=True)`**  
  Extract Nuxt data from the currently loaded page without navigation.
- **`navigate(url)`**  
  Navigate to a URL without extracting data.
- **`execute_step(step)`**  
  Execute a single navigation step on the current page.

### `deserialize_nuxt3_data(raw_data, is_json_string=True)`

Manually deserialize Nuxt 3 serialized data format using the new hydration engine.

- **`raw_data`** (`Union[str, List[Any]]`) – Raw Nuxt data (JSON string or already parsed list).
- **`is_json_string`** (`bool`) – Whether raw_data is a JSON string that needs parsing (default `True`).

Returns deserialized data with resolved references and proper type conversion. The new implementation:
- **Prevents exponential expansion** through proper caching
- **Handles circular references** without infinite loops  
- **Supports all devalue special types** ($d, $s, $m, $b, $r)
- **Maintains O(n) time complexity** for efficient processing
- **Provides detailed logging** for debugging complex datasets

**Example:**
```python
from nuxt_scraper import deserialize_nuxt3_data

# Deserialize raw Nuxt 3 data
raw_data = [{"state": 1}, {"users": [2]}, {"name": "Alice", "date": {"$d": 1672531200000}}]
result = deserialize_nuxt3_data(raw_data, is_json_string=False)
# Result: {"users": [{"name": "Alice", "date": datetime(2023, 1, 1, 0, 0)}]}
```

### `NavigationStep`

Dataclass representing a single browser interaction step. Steps are executed in order before data extraction.

| Factory method | Description | Parameters |
|----------------|-------------|------------|
| `NavigationStep.click` | Clicks an element. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.fill` | Fills an input/textarea. | `selector`, `value`, `timeout`, `wait_after_selector` |
| `NavigationStep.select` | Selects a dropdown option. | `selector`, `value`, `timeout`, `wait_after_selector` |
| `NavigationStep.wait` | Waits for a selector. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.scroll` | Scrolls element into view. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.hover` | Hovers over an element. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.select_date` | Selects a date from a calendar. | `target_date`, `calendar_selector`, `prev_month_selector`, `next_month_selector`, `month_year_display_selector`, `date_cell_selector`, `view_results_selector`, `timeout`, `wait_after_selector` |

## Anti-Detection Strategies

```mermaid
graph TB
    subgraph "Browser Level"
        A[User Agent Rotation] --> B[Viewport Randomization]
        B --> C[Stealth Scripts Injection]
        C --> D[WebDriver Property Masking]
    end
    
    subgraph "Interaction Level"
        E[Human-like Delays] --> F[Realistic Mouse Movement]
        F --> G[Human Typing Simulation]
        G --> H[Random Pauses & Typos]
    end
    
    subgraph "Network Level"
        I[Proxy Support] --> J[Request Timing]
        J --> K[Connection Patterns]
    end
    
    subgraph "Configuration"
        L[StealthConfig] --> A
        L --> E
        L --> I
        
        M[Minimal Stealth] --> N[Balanced Stealth]
        N --> O[Maximum Stealth]
        
        L -.-> M
        L -.-> N
        L -.-> O
    end
    
    style L fill:#e1f5fe
    style A fill:#f3e5f5
    style E fill:#e8f5e8
    style I fill:#fff3e0
```

Nuxt Scraper incorporates several measures to make automation less detectable:

-   **Human-like Delays**: Random pauses between actions and during typing.
-   **Realistic Mouse Movements**: Simulated curved mouse paths before clicks.
-   **Human-like Typing**: Varied typing speeds, occasional typos, and corrections.
-   **User Agent Rotation**: Uses a random, realistic browser user agent for each new browser context.
-   **Randomized Viewports**: Cycles through common desktop resolutions to avoid a consistent browser footprint.
-   **Stealth Scripts**: Injects JavaScript to mask `webdriver` property, mock `chrome.runtime`, spoof permissions API, mimic browser plugins, and reduce WebGL fingerprinting.

These features are controlled via the `StealthConfig` object, allowing you to fine-tune the level of stealth needed.

## WAF & Advanced Detection Considerations

While Nuxt Scraper provides robust browser-level anti-detection, certain advanced measures like AWS WAF, sophisticated IP reputation systems, and CAPTCHAs require additional considerations:

-   **TLS-based Rules**: Playwright uses real browser engines, so its TLS fingerprint is generally good. However, highly advanced WAFs might analyze the full TLS handshake for bot patterns. For such cases, consider using *external proxy services* that specialize in TLS fingerprinting obfuscation. Nuxt Scraper's proxy support allows integration with these services.

-   **IP Reputation**: Repeated requests from a single IP address will quickly flag you. For effective evasion:
    -   **Proxy Rotation**: Utilize a pool of high-quality, frequently rotating residential or mobile proxies. Nuxt Scraper allows you to configure a proxy for each extractor instance.
    -   **Proxy Provider**: Choose reputable proxy providers (e.g., Bright Data, Oxylabs, Smartproxy) that manage IP rotation and quality.

-   **CAPTCHA**: Nuxt Scraper does not automatically solve CAPTCHAs, as this is a complex and evolving challenge. If you encounter CAPTCHAs:
    -   **Manual Intervention**: For low-volume tasks, you might configure the extractor to pause and wait for manual CAPTCHA solving.
    -   **Third-Party CAPTCHA Solving Services**: Integrate with services like 2Captcha, Anti-Captcha, or CapMonster. Your script can detect the CAPTCHA, send it to the service, and then input the solved token.

-   **Behavioral CAPTCHAs**: These monitor mouse movements, typing speed, and other interactions. Nuxt Scraper's human-like behaviors (mouse movement, typing, delays) significantly improve your chances against these, but are not foolproof.

Effective evasion against advanced WAFs often requires a layered approach combining Nuxt Scraper's browser stealth with high-quality external proxy infrastructure and, if necessary, CAPTCHA solving services.

## Examples (Deprecated - see Usage section)

-   **examples/basic_usage.py** – Simple extraction and context manager usage.
-   **examples/advanced_navigation.py** – Multiple steps: tabs, fill, scroll, select.
-   **examples/async_parallel.py** – Sequential and parallel extraction from multiple URLs.

## Development

### Setup Development Environment

```bash
git clone https://github.com/rahjooh/nuxt_scraper.git
cd nuxt_scraper
pip install -e ".[dev]"
playwright install chromium
```

### Running Tests

The test suite provides comprehensive coverage of all functionality:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=nuxt_scraper --cov-report=html

# Run specific test categories
pytest tests/test_parser.py                    # Parser and deserialization tests
pytest tests/test_deserialization_performance.py  # Performance and edge cases
pytest tests/test_extraction_methods.py       # Extraction method tests
pytest tests/test_integration.py              # End-to-end integration tests
pytest tests/test_extractor.py                # Core extractor functionality
pytest tests/test_steps.py                    # Navigation steps
pytest tests/test_anti_detection.py           # Anti-detection features
pytest tests/test_utils.py                    # Utility functions

# Run tests with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "deserialization"
pytest -k "stealth"
pytest -k "calendar"
```

### Test Architecture

```mermaid
graph TB
    subgraph "Test Categories"
        A[Unit Tests] --> B[Integration Tests]
        B --> C[Performance Tests]
        C --> D[End-to-End Tests]
    end
    
    subgraph "Unit Test Coverage"
        E[Parser Module] --> F[Extractor Module]
        F --> G[Navigation Steps]
        G --> H[Anti-Detection]
        H --> I[Utilities]
    end
    
    subgraph "Integration Test Scenarios"
        J[Complete Workflows] --> K[Error Handling]
        K --> L[Concurrent Extraction]
        L --> M[Real-World Scenarios]
    end
    
    subgraph "Performance Validation"
        N[Large Dataset Handling] --> O[Memory Efficiency]
        O --> P[Processing Speed]
        P --> Q[Circular Reference Handling]
    end
    
    A --> E
    B --> J
    C --> N
    D --> R[E-commerce Scraping]
    D --> S[Racing Data Collection]
    D --> T[Calendar Interactions]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

### Test Coverage

The test suite covers:

- **Parser Module**: Complete deserialization engine testing
  - Nuxt 3 hydration algorithm
  - Special type handling ($d, $s, $m, $b, $r)
  - Circular reference prevention
  - Performance with large datasets
  - Edge cases and error conditions

- **Extractor Module**: All extraction methods and configurations
  - Combined vs legacy extraction
  - Deserialization options
  - Error handling and fallbacks
  - Browser management

- **Navigation Steps**: All step types and interactions
  - Click, fill, select, wait, scroll, hover
  - Calendar date selection
  - Anti-detection integration
  - Error handling

- **Anti-Detection**: Stealth features and configurations
  - Human delays and typing
  - Mouse movement simulation
  - User agent and viewport randomization
  - Stealth script injection

- **Integration Tests**: Real-world scenarios
  - E-commerce scraping workflows
  - Racing data collection
  - Multi-step navigation
  - Concurrent extractions

- **Performance Tests**: Large dataset handling
  - Memory efficiency
  - Processing speed
  - Circular reference handling
  - Special type conversion performance

### Code Quality

```bash
# Format code
black nuxt_scraper tests examples

# Check linting
ruff check nuxt_scraper tests examples

# Type checking
mypy nuxt_scraper

# Run all quality checks
black nuxt_scraper tests examples && ruff check nuxt_scraper tests examples && mypy nuxt_scraper
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Run linting (`black . && ruff check .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Building and Distribution

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (maintainers only)
twine upload dist/*
```

### Contributing Guidelines

1. **Fork and Clone**: Fork the repository and clone your fork
2. **Create Branch**: Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Install Dependencies**: `pip install -e ".[dev]"` and `playwright install chromium`
4. **Write Tests**: Add comprehensive tests for your changes
5. **Run Tests**: Ensure all tests pass (`pytest`)
6. **Check Code Quality**: Run linting and formatting (`black . && ruff check .`)
7. **Update Documentation**: Update README and docstrings as needed
8. **Commit Changes**: Use clear, descriptive commit messages
9. **Push and PR**: Push to your fork and create a Pull Request

### Test Requirements

All contributions must include:
- **Unit tests** for new functionality
- **Integration tests** for complex features
- **Performance tests** for optimization changes
- **Documentation updates** for user-facing changes

The test suite must maintain >95% coverage and all tests must pass.

## Changelog

### v0.3.0 - Major Release - Complete Deserialization Engine Rewrite

#### 🚀 **Complete Deserialization Engine Rewrite**

- **Fixed exponential data expansion**: Resolved critical issue where deserialized data could grow to 1GB+ from small datasets
- **Implemented proper hydration algorithm**: Now follows Nuxt 3's actual serialization format based on the `devalue` library
- **Added comprehensive special type support**: Full support for Date, Set, Map, BigInt, and RegExp objects
- **Improved circular reference handling**: Uses smart caching to prevent infinite loops and duplicate processing
- **Optimized performance**: Reduced time complexity from O(n²) to O(n) for large datasets

#### 🛠️ **Technical Improvements**

- **New `_hydrate_nuxt3_value()` function**: Replaces the old `_resolve_nuxt3_references()` with proper hydration logic
- **Enhanced error handling**: Graceful fallbacks for malformed special types with detailed logging
- **Memory efficiency**: Smart caching prevents duplicate object creation and reduces memory usage
- **Debug capabilities**: Added detailed logging for troubleshooting complex deserialization scenarios

#### 📊 **Performance Gains**

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| Large racing datasets | 1GB+ files | <50MB typical | 20x+ reduction |
| Processing time | Minutes | Seconds | 60x+ faster |
| Memory usage | Exponential growth | Linear scaling | Stable |
| Circular references | Infinite loops | Proper handling | ✅ Fixed |

#### 🔄 **Backward Compatibility**

- **API unchanged**: All existing code continues to work without modifications
- **Default behavior improved**: `deserialize_nuxt3=True` now uses the new engine automatically
- **Migration path**: No code changes required - improvements are transparent

#### 🐛 **Bug Fixes**

- Fixed infinite recursion in complex reference structures
- Resolved memory exhaustion on large datasets  
- Corrected handling of nested reactive references
- Fixed date/time parsing edge cases
- Improved error messages for debugging

## License

MIT License. See [LICENSE](LICENSE) for details.
