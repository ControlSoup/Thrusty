#include <SdFat.h>
#include <SPI.h>
#define FILE_BASE_NAME "log-"

SdFat sd;
SdFile File;

// Use Teensy SDIO
#define SD_CONFIG  SdioConfig(FIFO_SDIO)

static String data_file_name;
static float relative_time_start_s;



// =================================================================================================
// Configure data, NOTE: This is pretty sketch as there no catch for length checks.... or ordering

const char header[] = "run_time [s],time [s],state [-],"\
"OX-LC-A [lbf],OX-LC-B [lbf],OX-LC-C [lbf],OX-LC-D[lbf], FU-LC-A [lbf],FU-LC-B [lbf],FU-LC-C [lbf],FU-LC-D [lbf],CH-LC-A [lbf], CH-LC-B [lbf]"\ 
"OX-TC-093 [degF],OX-TC-097 [degF],FC-TC-056 [degF],CH-STC-101-A [degF], CH-STC-101-B [degF],CH-STC-101-C [degF]"\
"OX-PT-094 [psig],OX-PT-098 [psig],N2-PT-019 [psig], CH-PT-100 [psig]";

const int places = 4;

void write_data(){
  
  float relative_time_s = time_s - relative_time_start_s;

  File.print(time_s, places);
  File.print(",");
  File.print(relative_time_s, places);
  File.print(",");
  File.print(State);
  File.print(",");
  File.print(ox_lc_a, places);
  File.print(",");  
  File.print(ox_lc_b, places);
  File.print(",");
  File.print(ox_lc_c, places);
  File.print(",");
  File.print(ox_lc_d, places);
  File.print(",");
  File.print(fu_lc_a, places);
  File.print(",");  
  File.print(fu_lc_b, places);
  File.print(",");  
  File.print(fu_lc_c, places);
  File.print(",");  
  File.print(fu_lc_d, places);
  File.print(",");
  File.print(ch_lc_a, places);
  File.print(",");
  File.print(ch_lc_b, places);
  File.print(",");
  File.print(ox_tc_093, places);
  File.print(",");
  File.print(ox_tc_097, places);
  File.print(",");
  File.print(fu_tc_056, places);
  File.print(",");
  File.print(ch_stc_101_a, places);
  File.print(",");
  File.print(ch_stc_101_b, places);
  File.print(",");
  File.print(ch_stc_101_c, places);
  File.print(",");
  File.print(ox_pt_094,places);
  File.print(",");
  File.print(ox_pt_098,places);
  File.print(","); 
  File.print(n2_pt_019,places);
  File.print(","); 
  File.println(ch_pt_100,places);
}

void serial_print_data(){
  Serial.print(ox_lc_a + ox_lc_b + ox_lc_c + ox_lc_d);
  Serial.print(",");
  Serial.print(fu_lc_a + fu_lc_b + fu_lc_c + fu_lc_d);
  Serial.print(",");
  Serial.print(ox_tc_093);
  Serial.print(",");
  Serial.print(ox_tc_097);
  Serial.print(",");
  Serial.print(fu_tc_056);
  Serial.print(",");
  Serial.print(ch_stc_101_a);
  Serial.print(",");
  Serial.print(ch_stc_101_b);
  Serial.print(",");
  Serial.print(ch_stc_101_c);
  File.print(",");
  File.print(ox_pt_094,places);
  File.print(",");
  File.print(ox_pt_098,places);
  File.print(","); 
  File.print(n2_pt_019,places);
  File.print(","); 
  File.println(ch_pt_100,places);
}

// =================================================================================================
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

void do_the_data() {
  if (is_streaming){
    serial_print_data();
  }
  if (is_recording){
    write_data();
  }
}



int init_data_file(){

  // Shitty copy pasta code to itterate the next file name
  const uint8_t BASE_NAME_SIZE = sizeof(FILE_BASE_NAME) - 1;
  char file_name[13] = FILE_BASE_NAME "00.csv";
  if (BASE_NAME_SIZE > 6) {
    Serial.println("ERROR| FILE_BASE_NAME too long");
  }
  while (sd.exists(file_name)) {
    if (file_name[BASE_NAME_SIZE + 1] != "9") {
      file_name[BASE_NAME_SIZE + 1]++;
    } else if (file_name[BASE_NAME_SIZE] != "9") {
      file_name[BASE_NAME_SIZE + 1] = "0";
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
