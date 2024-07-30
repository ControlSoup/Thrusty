

// Globals
const long datarate_ms = 5;
static long prev_ms = 0.0;

// Global Channels (in order)
static float time_s = -404.0;
static float ox_lc_a = -404.0;
static float ox_lc_b = -404.0;
static float ox_lc_c = -404.0;
static float ox_lc_d = -404.0;
static float fu_lc_a = -404.0;
static float fu_lc_b = -404.0;
static float fu_lc_c = -404.0;
static float fu_lc_d = -404.0;
static float ch_lc_a = -404.0;
static float ch_lc_b = -404.0;
static float ox_tc_093 = -404.0;
static float ox_tc_097 = -404.0;
static float fu_tc_056 = -404.0;
static float ch_stc_101_a = -404.0;
static float ch_stc_101_b = -404.0;
static float ch_stc_101_c = -404.0;
static float ox_pt_094 = -404.0;
static float ox_pt_098 = -404.0;
static float n2_pt_019 = -404.0;
static float ch_pt_100 = -404.0;

static bool is_recording = false;
static bool is_streaming = false;

// State machine
typedef enum{
  STATE_ERROR = 0,
  STATE_IDLE = 1
} state_options;
static state_options State;


void setup_try(){
  Serial.print("Using File: ");
  Serial.println(__FILE__);
  if(sd_setup() == 0) while(1); // <- get stuck here like a pro c++ coder
  if(instrumentation_setup() == 0) while(1);
}

void setup() {
  Serial.begin(9600);
  Serial.println("\nWelcome! Hopfully this works out for ya, lets walk through some setup");
  Serial.println("Would you like to continue this adventure? (y to continue)");
  delay(2000);

  while (1){
    if (Serial.available() > 0){
      String message = Serial.readString();
      if (message == "y"){
        Serial.println(":S okay then!");
        State = STATE_IDLE ;
        setup_try();
        break;
      }
    }
    delay(100);
  }
}
void loop() {
  switch (State){
    case STATE_IDLE:
        if (Serial.available() > 0) {
          String message = Serial.readString();
          user_inputs(message);
        };
      };
      break;
    default:
      Serial.println("You have found a Poisen Arrow cause Joe Fucked up");
  };

  update_instrumentation();
  do_the_data();

  long ms = millis();
  long cur_dms = ms - prev_ms;
  time_s = ms / 1000.0;
  if (cur_dms > datarate_ms){
    Serial.print("WARNING| data rate is being choked: ");
    Serial.println(cur_dms);
  }
  prev_ms = ms;
  // Limit loop cycle sample rate
  while (millis() - prev_ms < datarate_ms){};
}


