#include "HX711.h"
#include "ADS1X15.h"


// Ox Load Cells
HX711 ox_l1_obj;
const float ox_l1_slope = 1.0;
const float ox_l1_offset = 0.0;
const int TC_ADC_READY = 33;

// TC Adc
ADS1015 TC_ADC(0x48);  
volatile bool tc_ready = false;
uint8_t channel = 0;
int16_t val[4] = { 0, 0, 0, 0 };

int instrumentation_setup() {
  Serial.println("\n\n __ Instrumentation Setup __");
  ox_l1_obj.begin(5, 4);
  Serial.println("Ox L1 Init");

   Serial.begin(115200);
  Serial.println(__FILE__);
  Serial.print("ADS1X15_LIB_VERSION: ");
  Serial.println(ADS1X15_LIB_VERSION);

  Wire.begin();

  pinMode(TC_ADC_READY, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(TC_ADC_READY), adsReady, RISING);

  TC_ADC.begin();
  TC_ADC.setGain(0);        //  6.144 volt
  TC_ADC.setDataRate(7);    //  0 = slow   4 = medium   7 = fast

  //  SET ALERT tc_ready PIN
  TC_ADC.setComparatorThresholdHigh(0x8000);
  TC_ADC.setComparatorThresholdLow(0x0000);
  TC_ADC.setComparatorQueConvert(0);

  //  SET INTERRUPT HANDLER TO CATCH CONVERSION READY
  pinMode(TC_ADC_READY, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(TC_ADC_READY), adsReady, RISING);

  TC_ADC.setMode(0);        //  continuous mode
  TC_ADC.readADC(channel);  //  trigger first read
  Serial.println("TC ADC Init");
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
    ox_l1 = (ox_l1_obj.get_value() * ox_l1_slope) + ox_l1_offset;
  }

  // TC adc
  if (tc_ready){
    //  save the value
    val[channel] = TC_ADC.getValue();
    //  request next channel
    channel++;
    if (channel >= 4) channel = 0;
    TC_ADC.readADC(channel);
    tc_ready = false;
  }
  ox_tc_094 = to_degF(val[0]);
  ox_tc_097 = to_degF(val[1]);
  fu_tc_056 = to_degF(val[2]);
  ch_stc_101_a = to_degF(val[3]);
}
