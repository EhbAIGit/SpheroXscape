/*
CONNECT 

Updated :  25/04/2024

servo to pwm channel 0  (red=5V,  black, GND and yellow signal)
Analog out from XARM controller to A0,  GND from XARM controller to GND
green wire to pin 9 on pwm shield (digital pin 2 on arduino)  (This is the switch on 2 sides of gripper.)
white wire to ground

When setting minimal 4V to AO,  gripper will close. Setting less then 2.9V will open gripper
Gripper will stop closing when switch is activated.
*/


#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Switch pinnen
const int switchPin1 = 2;
bool objectCatched = false;
int sensorValue=0;

String status = "OPEN"; 

// Servo instellingen, deze moeten mogelijk aangepast worden aan jouw servo
#define SERVOMIN  150  // minimale pulsbreedte (volledig open)
#define SERVOMAX  380  // maximale pulsbreedte (volledig gesloten)
#define SERVO_FREQ 50  // servo frequentie

void setup() {
  Serial.begin(9600);

  pwm.begin();
  pwm.setOscillatorFrequency(27000000); // Kalibreer de frequentie indien nodig
  pwm.setPWMFreq(SERVO_FREQ);  // Zet de PWM frequentie op 50Hz

  pinMode(switchPin1, INPUT_PULLUP);
  pinMode(9, OUTPUT);

  digitalWrite(9,HIGH);
}

void loop() {

  sensorValue = analogRead(A0);

  // Als sensorwaarde groter is dan 800, open de servo
  if (sensorValue < 600  && status == "CLOSE") {
    digitalWrite(9,LOW);
    delay(100);
     pwm.setPWM(0, 0, SERVOMIN); // Volledig open positie
     Serial.println("OPENED");
     status="OPEN";
    delay(1500);
    digitalWrite(9,HIGH);


  }
  // Als sensorwaarde kleiner is dan 200, en switchPin1 niet geactiveerd is, sluit de servo
  if (sensorValue > 800 && digitalRead(switchPin1) == HIGH  && status == "OPEN") {
    digitalWrite(9,LOW);
    delay(100);
    for (uint16_t pulselen = SERVOMIN; pulselen < SERVOMAX; pulselen++) {
      pwm.setPWM(0, 0, pulselen);
      delay(5); // Langzaam dichtgaan
      // Controleer of switchPin1 is geactiveerd
      if (digitalRead(switchPin1) == LOW) {
        Serial.println("OBJECT_CATCHED");
        objectCatched = true;
        break; // Stop de sluiting als switchPin1 wordt geactiveerd
      }
      status="CLOSE";
    }
    if (!objectCatched) {
      Serial.println("CLOSED");
    }
    delay(250);
    digitalWrite(9,HIGH);

  }

  if (Serial.available() > 0) {
    
    String command = Serial.readString();

    if (command.startsWith("stand")) {
      // Zet de servo op een specifieke hoek
      int angle = command.substring(5).toInt();
      uint16_t pulseLen = map(angle, 0, 180, SERVOMIN, SERVOMAX);
      pwm.setPWM(0, 0, pulseLen);
    }
  }
}
