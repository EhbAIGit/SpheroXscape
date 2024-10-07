#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Switch pinnen
const int switchPin1 = 2;
bool objectCatched = false;
int sensorValue = 0;
// Servo instellingen, deze moeten mogelijk aangepast worden aan jouw servo
#define SERVOMIN  150  // minimale pulsbreedte
#define SERVOMAX  350  // maximale pulsbreedte
#define SERVO_FREQ 50  // servo frequentie

void setup() {
  Serial.begin(9600);

  pwm.begin();
  pwm.setOscillatorFrequency(27000000); // Kalibreer de frequentie indien nodig
  pwm.setPWMFreq(SERVO_FREQ);  // Zet de PWM frequentie op 50Hz

  Serial.println("gripper online");

  pinMode(switchPin1, INPUT_PULLUP);
}

void loop() {

  sensorValue = analogRead(A0);
  if (sensorValue > 100 ) {
     map(sensorValue, 100, 1023, SERVOMIN, SERVOMAX);
     uint16_t pulseLen = map(sensorValue, 100, 1023, SERVOMIN, SERVOMAX);
     Serial.println(sensorValue);
     delay(500);
     pwm.setPWM(0, 0, pulseLen);    
  }


  if (Serial.available() > 0) {
    String command = Serial.readString();


    if (command.startsWith("open")) {
      // Beweeg de servo naar de open positie
      pwm.setPWM(0, 0, SERVOMIN); // Verander naar de juiste pulslengte voor open
      Serial.println("OPENED");

    } 
    else if (command.startsWith("close")) {
      // Beweeg de servo langzaam tot een switch wordt geactiveerd
      for (uint16_t pulselen = SERVOMIN; pulselen < SERVOMAX; pulselen++) {
        pwm.setPWM(0, 0, pulselen);
        if (digitalRead(switchPin1) == LOW) {
          Serial.println("OBJECT_CATCHED");
          objectCatched = true;
          break; // Stop als een van de switches wordt geactiveerd
        }
        delay(1); // Aanpassen voor een soepele beweging
      }
      if (objectCatched == false) {
        Serial.println("CLOSED_NO_OBJECT");
      }
    }
    else if (command.startsWith("stand")) {
      // Zet de servo op een specifieke hoek
      int angle = command.substring(5).toInt();
      uint16_t pulseLen = map(angle, 0, 180, SERVOMIN, SERVOMAX);
      pwm.setPWM(0, 0, pulseLen);
    }
  }
}
