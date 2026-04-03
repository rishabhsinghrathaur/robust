#include <stdint.h>

// Placeholder entry point for ESP32 firmware.
// Replace with ESP-IDF or Arduino startup logic.
int main() {
  volatile uint32_t device_ready = 1;
  return static_cast<int>(device_ready - 1);
}

