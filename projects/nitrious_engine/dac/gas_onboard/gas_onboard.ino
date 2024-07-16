

// Globals
const long datarate_ms = 10;
const long lograte_ms = 10;
static long prev_ms = 0.0;

static bool is_recording = false;
static bool is_streaming = false;
// Data (so lazy with globals lol)
float time_s = 0.0;
float ox_l1 = 0.0;

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
  long ms = millis();
  long log_timer_ms = lograte_ms;
  u_int logs_unsaved = 0;

  time_s = ms / 1000.0;


  switch (State){
    case STATE_IDLE:
      if (ms - input_timer > 1000.0){
        input_timer = ms;
        if (Serial.available() > 0) {
          String message = Serial.readString();
          user_inputs(message);
        };
      };
      break;

    default:
      Serial.println("You have found a Poisen Arrow cause Joe Fucked up");
  };

  if ((ms - log_timer_ms) > lograte_ms){
    log_timer_ms = ms;
    update_instrumentation();
    do_the_data();
  }


  // Limit
  long cur_dms = ms - prev_ms;
  if (cur_dms > datarate_ms){
    Serial.print("WARNING| data rate is being choked: ");
    Serial.println(cur_dms);
  }
  prev_ms = ms;
}


