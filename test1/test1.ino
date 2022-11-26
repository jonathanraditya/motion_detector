// Pin numbers
const int vs1 = 15;

// Store sensor status
int vs1_status = 0;
int vs1_cumulative = 0;
int n = 0;
int reset_every_n = 5000;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  // initialize pinout
  pinMode(vs1, INPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  vs1_status = digitalRead(vs1);
  vs1_cumulative = vs1_cumulative + vs1_status;
  n = n + 1;
  if (n == reset_every_n){
    n = 0;
    vs1_cumulative = 0;
    }
  Serial.println(vs1_cumulative);
  delay(10);

}
