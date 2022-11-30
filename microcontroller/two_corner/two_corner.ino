#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Kampung Bali_EXT";
const char* password = "(//////)";

//“hwid”
//  “two_corner”
//    “front_facing” -> 15 IN
//    “side_facing” -> 2 IN
//    “room_entry” -> 4 IN
//    “reset_trigger” -> 16 OUT
//  “two_entry”
//    “left_sensor” 15 IN
//    “right_sensor” 2 IN
//    “reset_trigger” -> 4 OUT
//  “one_perimeter”
//    “carport_perimeter” 15 IN
//    “large_gate” 2 IN
//    “small_gate” 4 IN
//    “garden_fence” 16 IN
//    “garden_outer_perimeter” 17 IN
//    “reset_trigger” -> 5 OUT
//  “one_main”
//    “parlor_window” 15 IN
//    “main_door_upper” 2 IN
//    “main_door_lower” 4 IN
//    “reset_trigger” -> 16 OUT
//  “one_hallway”
//    “hallway_door” 15 IN
//    “hallway_window” 2 IN
//    “kitchen_lamp_switch” 4 OUT
//    “outdoor_lamp_switch” 16 OUT
//    “parlor_lamp_switch” 17 OUT
//    “reset_trigger” -> 5 OUT

// THINGS NEED TO BE CHANGED:
// hwid (~43 & ~45) 
// pinMode setup according to pin rule (~88)
// ditialRead (~109)
// store input cumulative (~140)
// payload substring in output command (~164)
// relay update (~168)

// two_corner SETUP (IN, IN, IN, OUT)

String hwid = "two_corner";
String key = "431f8a00bb579d4691b19efe332e21d8b61ff25e8a1698d81bf95a756660f3ee";
String input_url = "http://192.168.0.7:5000/input?key=" + key + "&hwid=" + hwid + "&payload=";
String output_url = "http://192.168.0.7:5000/output?key=" + key + "&hwid=" + hwid;

const int pin1 = 32;
const int pin2 = 33;
const int pin3 = 25;
const int pin4 = 26;
const int pin5 = 27;
const int pin6 = 14;

// Unused pins
const int unused_pins [] = {15,2,4,16,17,5,18,19,21,3,1,22,23,13,12,35,34,39};

// Store sensor status
int pin1_status = 0;
int pin1_cumulative = 0;
String pin1_output_status = "";
int pin2_status = 0;
int pin2_cumulative = 0;
String pin2_output_status = "";
int pin3_status = 0;
int pin3_cumulative = 0;
String pin3_output_status = "";
int pin4_status = 0;
int pin4_cumulative = 0;
String pin4_output_status = "";
int pin5_status = 0;
int pin5_cumulative = 0;
String pin5_output_status = "";
int pin6_status = 0;
int pin6_cumulative = 0;
String pin6_output_status = "";
int send_data_every = 1000; // ms
int delay_set = 10; // ms
int counter = 0;
int counter_reference = send_data_every / delay_set;
int wifi_connection = 0;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  // initialize pinout
  pinMode(pin1, INPUT);
  pinMode(pin2, INPUT);
  pinMode(pin3, INPUT);
  pinMode(pin4, OUTPUT);
  pinMode(pin5, OUTPUT);
  pinMode(pin6, OUTPUT);

//   Unused pin configured in output mode to prevent input
  for (int unused_pin : unused_pins) {
      pinMode(unused_pin, OUTPUT);
      digitalWrite(unused_pin, LOW);
    }

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
  wifi_connection = 1;
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // put your main code here, to run repeatedly:
  pin1_status = digitalRead(pin1);
  pin1_cumulative = pin1_cumulative + pin1_status;
  pin2_status = digitalRead(pin2);
  pin2_cumulative = pin2_cumulative + pin2_status;
  pin3_status = digitalRead(pin3);
  pin3_cumulative = pin3_cumulative + pin3_status;
  
  counter = counter + 1;
  if (counter == counter_reference){
    // Post data to server
    if(WiFi.status() == WL_CONNECTED){
       wifi_connection = 1;
      }
    else {
      // Reconnect to WiFi
      wifi_connection = 0;
      WiFi.begin(ssid, password);
      Serial.println("Reconnecting");
      while(WiFi.status() != WL_CONNECTED) {
          delay(500);
          Serial.print(".");
        }
      wifi_connection = 1;
      Serial.println("");
      Serial.print("Reconnected to WiFi network with IP Address: ");
      Serial.println(WiFi.localIP());
      }
    HTTPClient http;

    // Store Input
    String input_url_w_data = input_url + pin1_cumulative + "z" + pin2_cumulative + "z" + pin3_cumulative;
    Serial.println(input_url_w_data);
    http.begin(input_url_w_data.c_str());
    int input_http_response_code = http.GET();

    if (input_http_response_code > 0) {
      Serial.print("Input HTTP Response code: ");
      Serial.println(input_http_response_code);
      }
    else {
      Serial.print("Input error code: ");
      Serial.println(input_http_response_code);
      }
    http.end();

    // Get output params
    http.begin(output_url.c_str());
    int output_http_response_code = http.GET();

    if (output_http_response_code > 0) {
      Serial.print("Output HTTP Response code: ");
      Serial.println(output_http_response_code);
      String payload = http.getString();
      payload = String(payload);
      Serial.println(payload);
      pin4_output_status = payload.substring(0,1);
//      pin5_output_status = payload.substring(2,3);
//      pin6_output_status = payload.substring(4,5);

      // Pin 4 Relay update
      if(pin4_output_status == "0"){
        Serial.println("Pin 4 Low state (OFF)");
        pinMode(pin4, INPUT);
        }
      else {
        Serial.println("Pin 4 High state (ON)");
        pinMode(pin4, OUTPUT);
        }
      }
    else {
      Serial.print("Output error code: ");
      Serial.println(output_http_response_code);
      }
    http.end();


    

    // Reset counter
    counter = 0;
    pin1_cumulative = 0;
    pin2_cumulative = 0;
    pin3_cumulative = 0;
    pin4_cumulative = 0;
    pin5_cumulative = 0;
    pin6_cumulative = 0;
    }
  delay(delay_set);

}
