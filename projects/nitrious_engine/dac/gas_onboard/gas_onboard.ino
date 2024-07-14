
// Globals
static bool is_recording = false;
static bool is_streaming = false;

// Data (so lazy with globals lol)
float time_s = 0.0;
float ox_l1 = 0.0;



// State machine
typedef enum{
  STATE_ERROR = 0,
  STATE_IDLE = 1
} state_options;
static state_options State;


void setup_try(){
  sd_setup();
  instrumentation_setup();
}


void setup() {
  Serial.begin(115200);
  Serial.println("\nWelcome! Hopfully this works out for ya, lets walk through some setup");
  Serial.println("Would you like to continue this adventure? (y to continue)");
  delay(2000);

  while (1){
    if (Serial.available() >0){
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
  
  time_s = millis() / 1000.0;

  switch (State){
    case STATE_IDLE:
      if (Serial.available() > 0) {
        String message = Serial.readString();
        user_inputs(message);
      }
      break;
    default:
      Serial.println("You have found a Poisend Arrow cause Joe Fucked up");
  };
  update_instrumentation();
  do_the_data();
  delay(2);
  

}


