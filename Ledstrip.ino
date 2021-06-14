#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif
#define PIN        15
#define NUMPIXELS 14
String bericht;
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
#define DELAYVAL 5

void setup() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  Serial.begin(9600);
  pixels.begin();
}

void loop() {
  pixels.clear();
  if (Serial.available() > 0) {
    bericht = Serial.readString();
    Serial.print("Bericht: ");
    Serial.println(bericht);
    if (bericht == "groen") {
      for (int i = 0; i < NUMPIXELS; i++) {

        pixels.setPixelColor(i, pixels.Color(0, 150, 0));
        pixels.show();
      }
    }
    if (bericht == "rood") {
      for (int i = 0; i < NUMPIXELS; i++) {

        pixels.setPixelColor(i, pixels.Color(150, 0, 0));
        pixels.show();
      }
    }
    if (bericht == "oranje") {
      for (int i = 0; i < NUMPIXELS; i++) {

        pixels.setPixelColor(i, pixels.Color(255, 69, 0));
        pixels.show();
      }
    }
    if (bericht == "uit") {
      for (int i = 0; i < NUMPIXELS; i++) {

        pixels.setPixelColor(i, pixels.Color(0, 0, 0));
        pixels.show();
      }
    }
  }
}
