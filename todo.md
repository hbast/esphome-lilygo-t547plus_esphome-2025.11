# To-Do List for Official ESPHome Inclusion

This document outlines the necessary steps to prepare the component for submission to the official [ESPHome repository](https://github.com/esphome/esphome).

**Goal:** Create a high-quality **"LilyGo T5-4.7 Display Component"** that offers a "Plug & Play" experience for users while maintaining clean internal code abstraction.

## 1. Component Strategy & Naming
- [ ] **Rename Component**:
    - Current Name: `t547` (slightly ambiguous).
    - **Target Name**: `lilygo_t547` (Clear assignment to the board family).
- [ ] **User Experience (UX)**:
    - **Requirement**: Zero-Config for standard boards. The user should not need to look up pinouts.
    - **Implementation**: The component will automatically detect the variant (e.g., via the ESP32 chip type or an optional `version` field) and configure the correct pins automatically.

## 2. Hardware Abstraction (Internal)
- [x] **Refactor Pin Management (The "Hidden" Abstraction)**:
    - **Current State**: Pins are hardcoded in C++ headers (`ed047tc1.h`) via `#define`.
    - **Problem**: Makes the C++ code rigid and hard to test/maintain.
    - **Solution**:
        1.  **C++ Layer**: Modify the `T547` class to accept pins in its constructor (e.g., `T547(d0, d1, ...)`). Remove the hardcoded `#define`s in `ed047tc1.h`.
        2.  **Python Layer (`display.py`)**: Move the "Knowledge" about which pin is connected where into Python dictionaries.
        3.  **Code Generation**: In `to_code`, the Python script selects the correct pin set (based on ESP32 vs S3) and passes them to the C++ constructor.
    - **Benefit**: The user sees simple YAML, but the C++ driver is clean and generic.
- [ ] **Power Management**:
    - Ensure power sequence pins are also handled via this injection mechanism.

## 3. Cleanup & Separation of Concerns
- [ ] **Remove Touch Driver**:
    - **Current State**: `touch.cpp` is bundled.
    - **Action**: **Delete it.**
    - **Reasoning**: Touchscreens are separate components in ESPHome (`touchscreen` platform).
    - **Solution**: Create a separate component (or use an existing one) for the specific touch controller (L58) used on this board. Users will add a `touchscreen:` entry to their YAML.
- [ ] **Remove Font Engine**:
    - **Current State**: `font.c` exists.
    - **Action**: **Delete it.**
    - **Reasoning**: ESPHome has a powerful native font engine. The display driver just needs to implement `draw_absolute_pixel`.
- [ ] **Battery Monitoring**:
    - **Action**: Do not add battery logic to this component.
    - **Reasoning**: Use the standard `adc` sensor component in the user's YAML to read battery voltage.

## 4. Code Quality & Standards
- [ ] **Namespace**:
    - Wrap all C driver code (currently global in `epd_driver.c`) into the `esphome::lilygo_t547` namespace to avoid symbol conflicts.
- [ ] **Memory Management**:
    - Use `esphome::ExternalRAMAllocator` for the large framebuffer allocation. This handles PSRAM availability checks and fallbacks automatically and is the standard way.
- [ ] **Logging**:
    - Fix the tag: `static const char *const TAG = "lilygo_t547";`.

## 5. Documentation & Examples
- [ ] **Create Standard Example**:
    - Create `examples/lilygo-t5-47.yaml`:
      ```yaml
      display:
        - platform: lilygo_t547
          id: my_display
          # Optional: version: v2.3 (if needed later)
      ```

## Summary of Work
1.  **Refactor C++**: Make pins dynamic (passed in constructor).
2.  **Update Python**: Move pin definitions to `display.py` and inject them automatically.
3.  **Delete**: Remove touch, font, and unused files.
