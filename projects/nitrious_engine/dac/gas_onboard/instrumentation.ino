#include "HX711.h"

// Ox Load Cells
HX711 ox_l1_obj;
const float ox_l1_slope = 1.0;
const float ox_l1_offset = 0.0;


int instrumentation_setup() {
  Serial.println("\n\n __ Instrumentation Setup __");
  ox_l1_obj.begin(5, 4);
  Serial.println("Instrumentation setup complete");
  return 1;
}

void update_instrumentation() {
  
  // Ox Load Cells
  if (ox_l1_obj.is_ready()) {
    ox_l1 = (ox_l1_obj.get_value() * ox_l1_slope) + ox_l1_offset;
  }

}
