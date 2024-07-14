void user_inputs(String message){
  if (message == "-r"){
    is_recording = !is_recording;

    if (is_recording){
      init_data_file();
    };

  } else if (message == "--stream"){
    is_streaming = !is_streaming;
  } 
  else {
    Serial.print("WARNING| Can't parse input: ");
    Serial.println(message);
  };
}