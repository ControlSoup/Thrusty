#include "HX711.h"
#include "ADS1X15.h"

typedef struct{
  slope: float,
  offset: float
} LinearSensor;

float reading_to_value(float value, LinearSenor info){
  return (value * info.slope) - info.offset;
}

// Ox Load Cells
HX711 ox_l1_obj;
ox_l1_info = LinearSensor(1.0, 0.0);

// TC Adc
ADS1015 TC_ADC(0x48);
volatile bool tc_ready = false;
uint8_t tc_channels = 0;
int16_t tc_val[4] = { 0, 0, 0, 0 };
const int TC_ADC_TRIG = 33;

// Voltage ADC1
ADS1015 V1_ADC(0x49);
volatile bool v1_ready = false;
uint8_t v1_channels = 0;
int16_t v1_val[4] = { 0, 0, 0, 0 };
const int V1_ADC_TRIG = 32;

// Voltage ADC1
ADS1015 V2_ADC(0x4A);
volatile bool v2_ready = false;
uint8_t v2_channels = 0;
int16_t v2_val[4] = { 0, 0, 0, 0 };
const int V2_ADC_TRIG = 31;

ox_pt_094_info = LinearSensor(355.5555, 0.0);
ox_pt_098_info = LinearSensor(355.5555, 0.0);
n2_pt_019_info = LinearSensor(66.6667, 0.0);
ch_pt_100_info = LinearSensor(66.6667, 0.0);

void tc_adc_setup(){
  pinMode(TC_ADC_TRIG, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(TC_ADC_TRIG), adsReady, RISING);

  TC_ADC.begin();
  TC_ADC.setGain(0);        //  6.144 volt
  TC_ADC.setDataRate(7);    //  0 = slow   4 = medium   7 = fast

  //  SET ALERT tc_ready PIN
  TC_ADC.setComparatorThresholdHigh(0x8000);
  TC_ADC.setComparatorThresholdLow(0x0000);
  TC_ADC.setComparatorQueConvert(0);

  //  SET INTERRUPT HANDLER TO CATCH CONVERSION READY
  pinMode(TC_ADC_TRIG, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(TC_ADC_TRIG), adsReady, RISING);

  TC_ADC.setMode(0);        //  continuous mode
  TC_ADC.readADC(tc_channels);  //  trigger first read
}

void v1_adc_setup(){
  pinMode(V1_ADC_TRIG, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(V1_ADC_TRIG), adsReady, RISING);

  V1_ADC.begin();
  V1_ADC.setGain(0);        //  6.144 volt
  V1_ADC.setDataRate(7);    //  0 = slow   4 = medium   7 = fast

  //  SET ALERT tc_ready PIN
  V1_ADC.setComparatorThresholdHigh(0x8000);
  V1_ADC.setComparatorThresholdLow(0x0000);
  V1_ADC.setComparatorQueConvert(0);

  //  SET INTERRUPT HANDLER TO CATCH CONVERSION READY
  pinMode(V1_ADC_TRIG, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(V1_ADC_TRIG), adsReady, RISING);

  V1_ADC.setMode(0);        //  continuous mode
  V1_ADC.readADC(v1_channels);  //  trigger first read
}

void v2_adc_setup(){
  pinMode(V2_ADC_TRIG, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(V2_ADC_TRIG), adsReady, RISING);

  V2_ADC.begin();
  V2_ADC.setGain(0);        //  6.144 volt
  V2_ADC.setDataRate(7);    //  0 = slow   4 = medium   7 = fast

  //  SET ALERT tc_ready PIN
  V2_ADC.setComparatorThresholdHigh(0x8000);
  V2_ADC.setComparatorThresholdLow(0x0000);
  V2_ADC.setComparatorQueConvert(0);

  //  SET INTERRUPT HANDLER TO CATCH CONVERSION READY
  pinMode(V2_ADC_TRIG, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(V2_ADC_TRIG), adsReady, RISING);

  V2_ADC.setMode(0);        //  continuous mode
  V2_ADC.readADC(v2_channels);  //  trigger first read
}

int instrumentation_setup() {
  Wire.begin();
  Serial.println("\n\n __ Instrumentation Setup __");
  Serial.println("Ox L1 Init");
  ox_l1_obj.begin(5, 4);

  Serial.print("ADS1X15_LIB_VERSION: ");
  Serial.println(ADS1X15_LIB_VERSION);

  Serial.println("TC ADC Init");
  tc_adc_setup();
  Serial.println("V1 ADC Init");
  v1_adc_setup();

  Wire.setClock(1000000); // Reqest a stupid large i2c clock cycle

  Serial.println("Instrumentation setup complete");
  return 1;
}

void adsReady()
{
  tc_ready = true;
}

float to_degF(float adc_reading){
  float volt = adc_reading * (6.144f / (32768 >> 4));
  return ((volt - 1.25) * 360.0) + 32.0;
}


void update_instrumentation() {

  // Ox Load Cells
  if (ox_l1_obj.is_ready()) {
    ox_l1 = reading_to_value(ox_l1_obj.get_value(), ox_l1_info);
  }

  // TC adc
  if (tc_ready){
    //  save the value
    tc_val[tc_channels] = TC_ADC.getValue();
    //  request next tc_channels
    tc_channels++;
    if (tc_channels >= 4) tc_channels = 0;
    TC_ADC.readADC(tc_channels);
    tc_ready = false;
  }
  ox_tc_094 = to_degF(tc_val[0]);
  ox_tc_097 = to_degF(tc_val[1]);
  fu_tc_056 = to_degF(tc_val[2]);
  ch_stc_101_a = to_degF(tc_val[3]);

  // V1 adc
  if (v1_ready){
    //  save the value
    v1_val[v1_channels] = V1_ADC.getValue();
    //  request next tc_channels
    v1_channels++;
    if (v1_channels >= 4) v1_channels = 0;
    V1_ADC.readADC(v1_channels);
    v1_ready = false;
  }
  ox_pt_094 =  sensor_to_engineering(v1_channels[0], ox_pt_094_info)
  ox_pt_098 =  sensor_to_engineering(v1_channels[1], ox_pt_098_info)
  n2_pt_019 =  sensor_to_engineering(v1_channels[2], n2_pt_019_info)
  ch_pt_100 =  sensor_to_engineering(v1_channels[3], ch_pt_100_info)

}
