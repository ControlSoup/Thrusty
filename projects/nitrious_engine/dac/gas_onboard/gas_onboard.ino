

// Globals
const long datarate_ms = 10;
static long prev_ms = 0.0;

// Global Channels (in order)
float time_s = -404.0;
float ox_l1 = -404.0;
float ox_l2 = -404.0;
float ox_l3 = -404.0;
float ox_l4 = -404.0;
float fu_l1 = -404.0;
float fu_l2 = -404.0;
float fu_l3 = -404.0;
float fu_l4 = -404.0;
float ox_tc_094 = -404.0;
float ox_tc_097 = -404.0;
float fu_tc_056 = -404.0;
float ch_stc_101_a = -404.0;
float ch_stc_101_b = -404.0;
float ch_stc_101_c = -404.0;


static bool is_recording = false;
static bool is_streaming = false;



float input_timer = 0.0;

// State machine
typedef enum{
  STATE_ERROR = 0,
  STATE_IDLE = 1
} state_options;
static state_options State;


void setup_try(){
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
      if (millis() - input_timer > 1000.0){
        input_timer = millis();
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


