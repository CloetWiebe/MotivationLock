
/*--------------------------------------------------------------------*/

#define USE_ARDUINO_INTERRUPTS true    // Set-up low-level interrupts for most acurate BPM math.
#include <PulseSensorPlayground.h>     // Includes the PulseSensorPlayground Library.  
#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2
#include<Wire.h>


// Setup a oneWire instance to communicate with any OneWire devices
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);


//  Variables
const int PulseWire = 0;       // PulseSensor PURPLE WIRE connected to ANALOG PIN 0
// The on-board Arduino LED, close to PIN 13.
int Threshold = 550;           // Determine which Signal to "count as a beat" and which to ignore.
// Use the "Gettting Started Project" to fine-tune Threshold Value beyond default setting.
// Otherwise leave the default "550" value.
String bericht;
const int MPU = 0x68; // I2C address of the MPU-6050
int16_t AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ;

int OldAcX, OldAcY, OldAcZ, OldTmp, OldGyX, OldGyY, OldGyZ;

int AcSensitivity = 5000;
boolean moved = false;

PulseSensorPlayground pulseSensor;  // Creates an instance of the PulseSensorPlayground object called "pulseSensor"


void setup() {

  Serial.begin(9600);          // For Serial Monitor
  // Configure the PulseSensor object, by assigning our variables to it.
  pulseSensor.analogInput(PulseWire);     //auto-magically blink Arduino's LED with heartbeat.
  pulseSensor.setThreshold(Threshold);
  sensors.begin();
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  // Double-check the "pulseSensor" object was created and "began" seeing a signal.
  if (pulseSensor.begin()) {
    //This prints one time at Arduino power-up,  or on Arduino reset.
  }
}



void loop() {
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 14, true); // request a total of 14 registers
  AcX = Wire.read() << 8 | Wire.read(); // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  AcY = Wire.read() << 8 | Wire.read(); // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ = Wire.read() << 8 | Wire.read(); // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  Tmp = Wire.read() << 8 | Wire.read(); // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  GyX = Wire.read() << 8 | Wire.read(); // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  GyY = Wire.read() << 8 | Wire.read(); // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  GyZ = Wire.read() << 8 | Wire.read(); // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)

  if (abs(OldAcX - AcX) > AcSensitivity) {
    moved = true;
  }

  if (abs(OldAcY - AcY) > AcSensitivity) {
    moved = true;
  }

  if (abs(OldAcY - AcY) > AcSensitivity) {
    moved = true;
  }

  int myBPM = pulseSensor.getBeatsPerMinute(); // Calls function on our pulseSensor object that returns BPM as an "int".
  // "myBPM" hold this BPM value now.
  sensors.requestTemperatures();              // Send the command to get temperature readings
  if (Serial.available() > 0) {
    bericht = Serial.readString();
    if (bericht == "hartslag") {
      if (pulseSensor.sawStartOfBeat()) {
        // Constantly test to see if "a beat happened".                         // Print phrase "BPM: "
        if (myBPM < 65) {
          myBPM = 90;
          Serial.println(myBPM);
        }
        else if (myBPM > 150) {
          myBPM = myBPM / 2;
          if (myBPM > 150) {
            myBPM = myBPM / 2;
            Serial.println(myBPM);
          }
          else {
            Serial.println(myBPM);

          }
        }
        else {
          Serial.println(myBPM);
        }
      }
    }
    if (bericht == "temp") {
      Serial.println(sensors.getTempCByIndex(0));
    }
    if (bericht == "mpu6050") {
      if (moved == true) {
        Serial.println(1);
      }
      else if (moved == false) {
        Serial.println(0);
      }
    }
  }
  OldAcX = AcX;
  OldAcY = AcY;
  OldAcZ = AcZ;
  moved = false;
}
