#include <SD.h>
#include <SPI.h>



const int chipSelect = BUILTIN_SDCARD;
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

void do_the_data() {
  String datastring = String();

  // Assemble data
  datastring += String(time_s, places);
  datastring += ",";
  datastring += String(time_s - relative_time_start_s, places);
  datastring += ",";
  datastring += String(State);
  datastring += ",";
  datastring += String(ox_l1, places);

  if (is_streaming){
    Serial.println(datastring);
  }


  if (is_recording){
    File dataFile = SD.open(("data/"+ data_file_name + ".csv").c_str(), FILE_WRITE);
    if (dataFile){
      dataFile.println(datastring);
      dataFile.close();

    } else {
      Serial.println("ERROR| Opening " + data_file_name + ".txt");
    }
  }
}

int read_data_index(const char *filename) {
  // Open the file for reading
  File file = SD.open(filename, FILE_READ);
  
  // Check if the file was successfully opened
  if (file) {
    Serial.print("Opened: ");
    Serial.println(filename);

    // Read the file until there's nothing left
    String c;
    while (file.available()) {
      // Read a byte and print it to the serial monitor
      c = String(file.read());
    }
    // Close the file
    file.close();
    return c.toInt();

  } else {
    // If the file didn't open, print an error
    Serial.print("ERROR| Can't Open: ");
    Serial.println(filename);
    is_recording = false;
    return 0;
  }
}

void sd_setup() {

  while (!Serial) {
    Serial.print("SD Card is waiting for Serial response");
  }
  Serial.println("\n\n__ SD Card Setup __");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("ERROR| SD Card failed or is not present, can't continue");
    while (1) {
      // !!!!!!!!!!!!!!!!!!!!!!!!!!!!   Can get stuck here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    }
  }
  Serial.println("SD Card intialised Correctly");
}

void init_data_file() {
  // Open the data index file for reading
  File data_index_file = SD.open("__ref__/data_index.txt", FILE_READ);
  int stored_data_index = 0;

  // Check if the file opened successfully
  if (data_index_file) {
    // Read the first line of the file directly
    stored_data_index = data_index_file.parseInt();  // Read the integer value from the first line
    data_index_file.close();
  } else {
    Serial.println("ERROR| Unable to open __ref__/data_index.txt for reading.");
    is_data_recording == False
  }

  // Print the stored data index
  Serial.println("Saved Data Index: " + String(stored_data_index));
  Serial.println("Current Data Index: " + String(data_index));

  // Update and increment data_index if necessary
  if (data_index <= stored_data_index) {
    data_index = stored_data_index + 1;

    // Delete the existing data index file
    if (SD.remove("__ref__/data_index.txt")) {
      Serial.println("Deleted: __ref__/data_index.txt");
    } else {
      Serial.println("ERROR| Unable to delete __ref__/data_index.txt.");
      while (1) {
        // Loop indefinitely
      }
    }

    // Create and write the new data_index
    data_index_file = SD.open("__ref__/data_index.txt", FILE_WRITE);
    if (data_index_file) {
      Serial.println("Created: __ref__/data_index.txt");
      Serial.print("Writing new index: ");
      Serial.println(data_index);
      data_index_file.println(data_index);
      data_index_file.close();
    } else {
      Serial.println("ERROR| Unable to create __ref__/data_index.txt for writing.");
      while (1) {
        // Loop indefinitely
      }
    }

    relative_time_start_s = time_s;
  }

  // Generate the new data file name
  data_file_name = String("log-") + String(data_index);

  // Write the file header for the data
  Serial.println("Writing file header for data");
  File dataFile = SD.open(("data/" + data_file_name + ".csv").c_str(), FILE_WRITE | O_TRUNC);
  if (dataFile) {
    Serial.print("Opened: ");
    Serial.println("data/" + data_file_name + ".csv");
    dataFile.println(header);
    dataFile.close();
  } else {
    Serial.println("ERROR| Can't Open: " + data_file_name + ".csv");
  }

  Serial.println("Data File setup was ay okay!");
}
