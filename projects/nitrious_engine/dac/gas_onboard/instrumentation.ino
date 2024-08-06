#include "HX711.h"
#include "ADS1X15.h"

typedef struct LSR{
  float slope;
  float offset;
} LinearSensor;


// Ox Load Cells
HX711 ox_lc_a_obj;
LinearSensor ox_lc_a_info      = {1.0, 0.0};

// 5v power through a 47/75 divider
LinearSensor sensor_voltage_info = {1.62666666666667, 0};

// 0-5v AD8495 through a 47/75 divider
LinearSensor ox_tc_093_info    = {585.6, -418.0};
LinearSensor ox_tc_097_info    = {585.6, -418.0};
LinearSensor fu_tc_056_info    = {585.6, -418.0};
LinearSensor ch_stc_101_a_info = {585.6, -418.0};
LinearSensor ch_stc_101_b_info = {585.6, -418.0};
LinearSensor ch_stc_101_c_info = {585.6, -418.0};

// 0.5-4.5v 1600psig through a 47/75 divider
LinearSensor ox_pt_094_info    = {650.666667, -200.000000};
LinearSensor ox_pt_098_info    = {650.666667, -200.000000};

// 0.5-4.5v 300psig through a 47/75 divider
LinearSensor n2_pt_019_info    = {122.0, -37.5};
LinearSensor ch_pt_100_info    = {122.0, -37.5};

float reading_to_value(float value, struct LSR info){
  return (value * info.slope) + info.offset;
}

float analogVolt(int pin){
    //https://www.pjrc.com/teensy/tutorial4.html
    return analogRead(pin) * 3.3 / 1023;
}


int instrumentation_setup() {
  Wire.begin();
  Serial.println("\n\n __ Instrumentation Setup __");
  Serial.println("Ox L1 Init");
  ox_lc_a_obj.begin(5, 4);
  Serial.println("Instrumentation setup complete");
  return 1;
}


void update_instrumentation() {


  // Voltage Readings
  sensor_voltage = reading_to_value(analogVolt(A9), sensor_voltage_info);

  // Ox Load Cells
  if (ox_lc_a_obj.is_ready()) {
    ox_lc_a = reading_to_value(ox_lc_a_obj.get_value(), ox_lc_a_info);
  }

  // TC
  ox_tc_093 = reading_to_value(analogVolt(A14), ox_tc_093_info);
  ox_tc_097 = reading_to_value(analogVolt(A15), ox_tc_097_info);
  fu_tc_056 = reading_to_value(analogVolt(A16), fu_tc_056_info);


  // Skin TCs
  ch_stc_101_a = reading_to_value(analogVolt(A17), ch_stc_101_a_info);
  ch_stc_101_b = reading_to_value(analogVolt(A0), ch_stc_101_b_info);
  ch_stc_101_c = reading_to_value(analogVolt(A1), ch_stc_101_c_info);

  // Pts
  ox_pt_094 =  reading_to_value(analogVolt(A2), ox_pt_094_info);
  ox_pt_098 =  reading_to_value(analogVolt(A3), ox_pt_098_info);
  n2_pt_019 =  reading_to_value(analogVolt(A4), n2_pt_019_info);
  ch_pt_100 =  reading_to_value(analogVolt(A5), ch_pt_100_info);

}
