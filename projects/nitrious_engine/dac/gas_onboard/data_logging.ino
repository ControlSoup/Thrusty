#include <SD.h>
#include <SPI.h>
#define FILE_BASE_NAME "log-"

SdFat sd;
SdFile File;

// Use Teensy SDIO
#define SD_CONFIG  SdioConfig(FIFO_SDIO)

static String data_file_name;
static u_int flush_count = 0;
static float relative_time_start_s;

// Configure data, NOTE: This is pretty sketch as there no catch for length checks.... or ordering
// =================================================================================================
const char header[] = "run_time [s],time [s],state [-],ox_l1 [lbf]";
const int places = 4;

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
  Serial.println("Data has been saved");
}

void check_flush(){
  if (flush_count > 10){ // TODO: Actually do a ring buffer, or get a better number here 10, 100 ect still choke the data 
    File.sync();
    flush_count = 0;
    return 0;
  }
  flush_count += 1;
}

void do_the_data() {

  float relative_time_s = time_s - relative_time_start_s;

  if (is_streaming){
    Serial.println(ox_l1);
  }


  if (is_recording){
    // Sd card writes in 512 byte chunks
    // Re-evaluate if this
    File.print(time_s, places);
    File.print(',');
    File.print(relative_time_s, places);
    File.print(',');
    File.print(State);
    File.print(',');
    File.println(ox_l1, places);
    check_flush();
  }
}

int sd_setup() {
  Serial.println("__ SD Setup __");
 // Initialize the SD.
  if (!sd.begin(SD_CONFIG)) {
    Serial.println("ERROR| Failed to configure SD, check if its in the thingy");
    return 0;
  }
  Serial.println("SD Setup complete");
  return 1;
}

int init_data_file(){

  // Shitty copy pasta code to itterate the next file name
  const uint8_t BASE_NAME_SIZE = sizeof(FILE_BASE_NAME) - 1;
  char file_name[13] = FILE_BASE_NAME "00.csv";
  if (BASE_NAME_SIZE > 6) {
    Serial.println("ERROR| FILE_BASE_NAME too long");
  }
  while (sd.exists(file_name)) {
    if (file_name[BASE_NAME_SIZE + 1] != '9') {
      file_name[BASE_NAME_SIZE + 1]++;
    } else if (file_name[BASE_NAME_SIZE] != '9') {
      file_name[BASE_NAME_SIZE + 1] = '0';
      file_name[BASE_NAME_SIZE]++;
    } else {
      Serial.println("ERROR| Can't create file name");
    }
  }

// Open or create file - truncate existing file.
  if (!File.open(file_name, O_RDWR | O_CREAT | O_TRUNC)) {
    Serial.println("ERROR| Fail to open file");
    return 0;
  }

  Serial.print(F("File Name: "));
  Serial.println(file_name);

  // Write data header.
  writeHeader();
  relative_time_start_s = time_s;

  return 1;
}
