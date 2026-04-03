#include <stdint.h>

int main(void) {
  volatile uint32_t initialized = 1U;
  return (int)(initialized - 1U);
}

