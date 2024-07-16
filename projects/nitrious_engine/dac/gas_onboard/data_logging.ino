#include <SD.h> 
#include <SPI.h>
#define FILE_BASE_NAME "log"

SdFat sd;
SdFile File;

// Use Teensy SDIO
#define SD_CONFIG  SdioConfig(FIFO_SDIO)

static String data_file_name;
static int data_index = 0;
static float relative_time_start_s;

// Configure data, NOTE: This is pretty sketch as there no catch for length checks.... or ordering
// =================================================================================================
const char header[] = "run_time [s],time [s],state [-],ox_l1 [lbf]";
const int places = 6;

// =================================================================================================
void print_header(){
  Serial.println(header);
}

void writeHeader() {
  File.println(header);
  File.sync();
}

void close_data(){
  File.close();
  Serial.println("Data has been saved")
}

void flush_data(){
  File.sync();
}

void do_the_data() {

  float relative_time_s = time_s - relative_time_start_s;

  if (is_streaming){
    Serial.print(time_s, 4);
    Serial.print(',');
    Serial.print(relative_time_s, 4);
    Serial.print(',');
    Serial.print(State);
    Serial.print(',');
    Serial.println(ox_l1);
  }


  if (is_recording){
    File.print(time_s, 4);
    File.print(',');
    File.print(relative_time_s, 4);
    File.print(',');
    File.print(State);
    File.print(',');
    File.println(ox_l1);
  }
}

void sd_setup() {
  Serial.println("__ SD Setup __");
 // Initialize the SD.
  if (!sd.begin(SD_CONFIG)) {
    Serial.println("ERROR| Failed to configure SD, check if its in the thingy");
  }
  Serial.println("SD Setup complete");
}

int init_data_file(){

   // Open or create file - truncate existing file.
  if (!File.open("log-0002.csv", O_RDWR | O_CREAT | O_TRUNC)) {
    Serial.println("ERROR| Fail to open file");
    return 0;
  }

  Serial.print(F("File Name: "));
  Serial.println("log-0002.csv");

  // Write data header.
  writeHeader();
  relative_time_start_s = time_s;

  return 1;
}
