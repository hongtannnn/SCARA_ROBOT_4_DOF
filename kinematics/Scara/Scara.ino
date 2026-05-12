#include <AccelStepper.h>
#include <math.h>

#define limitSwitch1 9
#define limitSwitch2 10
#define EN_PIN 8

AccelStepper stepper1(1, 2, 5);
AccelStepper stepper2(1, 3, 6);
AccelStepper stepperZ(1, 12, 13);

const float STEPS_PER_REV = 200.0;
const float MICROSTEP = 16.0;
const float RATIO_J1 = 5.0;
const float RATIO_J2 = 4.0;

const float L1 = 228.0;
const float L2 = 136.5;

const float theta1AngleToSteps = 4*((STEPS_PER_REV * RATIO_J1 * MICROSTEP) / 360.0);
const float theta2AngleToSteps = 4*((STEPS_PER_REV * RATIO_J2 * MICROSTEP) / 360.0);
const float zMmToSteps = 400.0*4;

const float HOMING_BACKOFF_ANGLE_X = 5.0;
const float HOMING_BACKOFF_ANGLE_Y = 150.0;

bool isHomed = false;
float currentX = 0.0;
float currentY = 0.0;
float currentAngle1 = 0.0;
float currentAngle2 = 0.0;
float currentZ = 0.0;

void setup() {
  Serial.begin(115200);

  pinMode(limitSwitch1, INPUT_PULLUP);
  pinMode(limitSwitch2, INPUT_PULLUP);
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);

  stepper1.setMaxSpeed(6000); stepper1.setAcceleration(2000);
  stepper2.setMaxSpeed(6000); stepper2.setAcceleration(2000);
  stepperZ.setMaxSpeed(10000); stepperZ.setAcceleration(5000);

  Serial.println("\n=== HE THONG DA KHOI DONG (CHE DO 3 JUMP - VI BUOC) ===");
}

void reportStatus() {
  Serial.print("STATUS,");
  Serial.print(currentX); Serial.print(",");
  Serial.print(currentY); Serial.print(",");
  Serial.print(currentZ); Serial.print(",");
  Serial.print(currentAngle1); Serial.print(",");
  Serial.print(currentAngle2);
  Serial.println(); 
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n'); 
    input.trim(); 

    if (input.length() > 0) {
      char firstChar = input.charAt(0);

      if (firstChar == 'H' || firstChar == 'h') {
        homing();
      } 
      else {
        if (!isHomed) {
          Serial.println("\n[!] LOI: Ban phai go 'H' de xet goc truoc.");
          return; 
        }

        if (firstChar == 'J' || firstChar == 'j') {
          int comma1 = input.indexOf(',');
          int comma2 = input.indexOf(',', comma1 + 1);
          if (comma1 > 0 && comma2 > 0) {
            int jointId = input.substring(comma1 + 1, comma2).toInt();
            float value = input.substring(comma2 + 1).toFloat();
            
            if (jointId == 1) {
              moveToAngleWithZ(currentAngle1 + value, currentAngle2, currentZ);
            } else if (jointId == 2) {
              moveToAngleWithZ(currentAngle1, currentAngle2 + value, currentZ);
            } else if (jointId == 3) {
              moveToAngleWithZ(currentAngle1, currentAngle2, currentZ + value);
            }
          }
        }
        
        else if (firstChar == 'A' || firstChar == 'a') {
          int c1 = input.indexOf(',');
          int c2 = input.indexOf(',', c1 + 1);
          int c3 = input.indexOf(',', c2 + 1);
          if (c1 > 0 && c2 > 0 && c3 > 0) {
            float t1 = input.substring(c1 + 1, c2).toFloat();
            float t2 = input.substring(c2 + 1, c3).toFloat();
            float z = input.substring(c3 + 1).toFloat();
            moveToAngleWithZ(t1, t2, z); 
          }
        } 
        
        else if (firstChar == 'P' || firstChar == 'p') {
          int c1 = input.indexOf(',');
          int c2 = input.indexOf(',', c1 + 1);
          
          if (c1 > 0 && c2 > 0) {
            float targetX = input.substring(c1 + 1, c2).toFloat();
            float targetY = input.substring(c2 + 1).toFloat(); 
            
            moveToXYZ(targetX, targetY, currentZ);
          }
        }

        else if (firstChar == 'D' || firstChar == 'd') {
          int c1 = input.indexOf(',');
          int c2 = input.indexOf(',', c1 + 1);
          int c3 = input.indexOf(',', c2 + 1);
          int c4 = input.indexOf(',', c3 + 1);
          int c5 = input.indexOf(',', c4 + 1);
          int c6 = input.indexOf(',', c5 + 1);

          if (c1 > 0 && c2 > 0 && c3 > 0 && c4 > 0 && c5 > 0) {
            float x1 = input.substring(c1 + 1, c2).toFloat();
            float y1 = input.substring(c2 + 1, c3).toFloat();
            float x2 = input.substring(c3 + 1, c4).toFloat();
            float y2 = input.substring(c4 + 1, c5).toFloat();
            float zUp = input.substring(c5 + 1, c6).toFloat();
            float zDown = input.substring(c6 + 1).toFloat();
            
            moveToXYZ(currentX, currentY, zUp);
            moveToXYZ(x1, y1, zUp);
            moveToXYZ(x1, y1, zDown);
            drawLine(x2, y2);
            moveToXYZ(currentX, currentY, zUp);
          }
        }
        
        else if (firstChar == 'C' || firstChar == 'c') {
          int c1 = input.indexOf(',');
          int c2 = input.indexOf(',', c1 + 1);
          int c3 = input.indexOf(',', c2 + 1);
          int c4 = input.indexOf(',', c3 + 1);
          int c5 = input.indexOf(',', c4 + 1);

          if (c1 > 0 && c2 > 0 && c3 > 0 && c4 > 0) {
            float cx = input.substring(c1 + 1, c2).toFloat();
            float cy = input.substring(c2 + 1, c3).toFloat();
            float r = input.substring(c3 + 1, c4).toFloat();
            float zUp = input.substring(c4 + 1, c5).toFloat();
            float zDown = input.substring(c5 + 1).toFloat();

            float startX = cx + r;
            float startY = cy;

            moveToXYZ(currentX, currentY, zUp);
            moveToXYZ(startX, startY, zUp);
            moveToXYZ(startX, startY, zDown);
            drawCircle(cx, cy, r);
            moveToXYZ(currentX, currentY, zUp);
          }
        }

        else if (firstChar == 'Z' || firstChar == 'z') {
          int c1 = input.indexOf(',');
          if (c1 > 0) {
            float targetZ = input.substring(c1 + 1).toFloat();
            moveToXYZ(currentX, currentY, targetZ); 
          }
        }
        
        else if (firstChar == 'L' || firstChar == 'l') {
          int c1 = input.indexOf(',');
          int c2 = input.indexOf(',', c1 + 1);
          
          if (c1 > 0 && c2 > 0) {
            float targetX = input.substring(c1 + 1, c2).toFloat();
            float targetY = input.substring(c2 + 1).toFloat(); 
            
            drawLine(targetX, targetY);
          }
        }
      }
      
      reportStatus();
    }
  }
}

void homing() {
  Serial.println("\n-> Dang tim vi tri goc (Homing) DONG THOI...");
  
  int normalState1 = digitalRead(limitSwitch1);
  int normalState2 = digitalRead(limitSwitch2);

  bool isJ1Homed = false;
  bool isJ2Homed = false;

  stepper1.setSpeed(-2000); 
  stepper2.setSpeed(-2000); 

  while (!isJ1Homed || !isJ2Homed) {
    if (!isJ1Homed) {
      if (digitalRead(limitSwitch1) == normalState1) {
        stepper1.runSpeed();
      } else {
        isJ1Homed = true; 
      }
    }
    if (!isJ2Homed) {
      if (digitalRead(limitSwitch2) == normalState2) {
        stepper2.runSpeed();
      } else {
        isJ2Homed = true; 
      }
    }
  }

  long backoffSteps1 = HOMING_BACKOFF_ANGLE_X * theta1AngleToSteps;
  long backoffSteps2 = HOMING_BACKOFF_ANGLE_Y * theta2AngleToSteps;
  
  stepper1.move(backoffSteps1); 
  stepper2.move(backoffSteps2); 

  while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0) { 
    stepper1.run(); 
    stepper2.run(); 
  }

  stepper1.setCurrentPosition(0); 
  stepper2.setCurrentPosition(0); 
  stepperZ.setCurrentPosition(0);
  
  currentZ = 0.0;
  currentAngle1 = 0;
  currentAngle2 = 0;
  
  currentX = L1 + L2; 
  currentY = 0.0;

  isHomed = true;
  Serial.println("\n--- ROBOT SCARA DA SAN SANG ---");
  
  reportStatus();
}

void moveToAngleWithZ(float theta1_deg, float theta2_deg, float z_mm) {
  stepper1.moveTo(theta1_deg * theta1AngleToSteps);
  stepper2.moveTo(theta2_deg * theta2AngleToSteps);
  stepperZ.moveTo(z_mm * zMmToSteps);

  while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0 || stepperZ.distanceToGo() != 0) {
    stepper1.run(); 
    stepper2.run();
    stepperZ.run(); 
  }
  
  currentAngle1 = theta1_deg;
  currentAngle2 = theta2_deg;
  currentZ = z_mm;
  
  float t1_rad = theta1_deg * PI / 180.0;
  float t2_rad = theta2_deg * PI / 180.0;
  
  currentX = L1 * cos(t1_rad) + L2 * cos(t1_rad + t2_rad);
  currentY = L1 * sin(t1_rad) + L2 * sin(t1_rad + t2_rad);
}

void moveToXYZ(float x, float y, float z) {
  float r_square = (x * x) + (y * y);
  if (r_square > pow(L1 + L2, 2) || r_square < pow(L1 - L2, 2)) return; 

  float cosTheta2 = (r_square - (L1 * L1) - (L2 * L2)) / (2 * L1 * L2);
  cosTheta2 = constrain(cosTheta2, -1.0, 1.0);
  float theta2_rad = acos(cosTheta2); 
  float theta2_deg = theta2_rad * 180.0 / PI;

  float term1 = atan2(y, x); 
  float term2 = atan2(L2 * sin(theta2_rad), L1 + L2 * cosTheta2);
  float theta1_rad = term1 - term2;
  float theta1_deg = theta1_rad * 180.0 / PI;

  moveToAngleWithZ(theta1_deg, theta2_deg, z);
  
  currentX = x; 
  currentY = y;
}

void drawLine(float targetX, float targetY) {
  float dx = targetX - currentX;
  float dy = targetY - currentY;
  float distance = sqrt(dx * dx + dy * dy);

  float stepSize = 0.5;
  int numSegments = max(1, (int)(distance / stepSize));

  stepper1.setAcceleration(8000); stepper2.setAcceleration(8000);
  stepper1.setMaxSpeed(4000); stepper2.setMaxSpeed(4000);

  for (int i = 1; i <= numSegments; i++) {
    float nextX = currentX + dx * ((float)i / numSegments);
    float nextY = currentY + dy * ((float)i / numSegments);
    calculateAndRunIK_Drawing(nextX, nextY);
  }

  stepper1.setAcceleration(2000); stepper2.setAcceleration(2000);
  stepper1.setMaxSpeed(6000); stepper2.setMaxSpeed(6000);

  currentX = targetX; currentY = targetY;
}

void drawCircle(float cx, float cy, float r) {
  int numSegments = max(10, (int)(2 * PI * r / 0.5)); 
  
  stepper1.setAcceleration(8000); stepper2.setAcceleration(8000);
  stepper1.setMaxSpeed(4000); stepper2.setMaxSpeed(4000);

  for (int i = 1; i <= numSegments; i++) {
    float angle = 2.0 * PI * i / numSegments; 
    float nextX = cx + r * cos(angle);
    float nextY = cy + r * sin(angle);
    calculateAndRunIK_Drawing(nextX, nextY);
  }

  stepper1.setAcceleration(2000); stepper2.setAcceleration(2000);
  stepper1.setMaxSpeed(6000); stepper2.setMaxSpeed(6000);
  
  currentX = cx + r; 
  currentY = cy;
}

void calculateAndRunIK_Drawing(float x, float y) {
  float r_square = (x * x) + (y * y);
  if (r_square > pow(L1 + L2, 2) || r_square < pow(L1 - L2, 2)) return; 

  float cosTheta2 = (r_square - (L1 * L1) - (L2 * L2)) / (2 * L1 * L2);
  cosTheta2 = constrain(cosTheta2, -1.0, 1.0);
  float theta2_rad = acos(cosTheta2); 
  float theta2_deg = theta2_rad * 180.0 / PI;

  float term1 = atan2(y, x); 
  float term2 = atan2(L2 * sin(theta2_rad), L1 + L2 * cosTheta2);
  float theta1_rad = term1 - term2;
  float theta1_deg = theta1_rad * 180.0 / PI;

  stepper1.moveTo(theta1_deg * theta1AngleToSteps);
  stepper2.moveTo(theta2_deg * theta2AngleToSteps);

  while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0) {
    stepper1.run();
    stepper2.run();
  }

  currentAngle1 = theta1_deg;
  currentAngle2 = theta2_deg;
}