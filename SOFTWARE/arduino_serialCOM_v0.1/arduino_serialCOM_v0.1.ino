//#include <lc.h>
//#include <lc-addrlabels.h>
//#include <pt-sem.h>
//#include <lc-switch.h>
//#include <pt.h>

// TODO:
// (1) Figure out how to report distance remaining back to python
// (2) Combine the run and jog functions into a move function
// (3) Then also combine one, few, and all movements into 1 function
// (4) Figure out how to enable/disable steppers without using the jumper that way we can control the enabling via gui

// NOTES:
// (1) All values are reported to the arduino in steps (not mm or any other units!)
// (2) With 32 microstepping, and a 200 step motor, there are effectively 6400 steps per rev
// (3) The reporting the distance left will reutnr "steps remaining"

// WRITE COMMAND: <RUN,DIST,123,F,0.0,0.0,0.0>

// ======================================================
// ACCELSTEPPER FUNCTIONS: returns fncName(argtype arg) [description]
// ======================================================

// SETTINGS
// --------
// void setMaxSpeed(float speed>0)            [run() will accelerate to speed in steps per sec]
// void setAcceleration(float acceleration>0) [sets the accel in steps per sec per sec]
// void setSpeed(float speed)                 [runSpeed() will use this amount. >0 is clockwise, <0 counterclockwise]

// #########I DON'T USE THESE###########
// void setMinPulseWidth(unsignedint minWidth)
// void setEnablePin(uint8_t enablePin=0xff)
// void setPinsInverted(bool directionInvert=false, bool stepInvert=false, bool enableInvert=false)
// void setPinsInverted (bool pin1Invert, bool pin2Invert, bool pin3Invert, bool pin4Invert, bool enableInvert)
// #########I DON'T USE THESE###########

// SET MOVEMENT
// ------------
// void moveTo(long absolute)
// void move(long relative)
// void setCurrentPosition(long position)      [resets the current position of the motor to ZERO. this is the ZERO!! side effect: sets speed=0]

// RUN
// -----------
// void runToPosition()                        [BLOCKING; moves with accel and decell to target (runToNewPosition()) calls this fnc, then this calls run()]
// void runToNewPosition(long position)        [BLOCKING; moves with accel and deccel to target position (absolute position) moves with run()]
// bool run()                                  [move motor one step if a step is due. this implements accel and decell. uses setMaxSpeed]
// bool runSpeed()                             [move motor one step if a step is due. does not implement accel and decell (ie inf accel). uses setSpeed()]
// bool runSpeedToPosition()                   [runs at currently selected speed until target position is reached, does not use accel]
// void stop()                                 [changes target pos s.t. stepper stops as quickly as possible. uses accel and decell]
// void disableOutputs()
// void enableOutputs()

// I am confused how the calls work for these functions. need to review

// GETTERS
// ------------
// long distanceToGo()                         [returns distance in steps from targetPosition. >0 is clockwise from current pos, <0 ccw]
// long targetPosition()                       [the most recently set target pos, >0 is cw from the ZERO and <0 is ccw from current]
// long currentPosition()                      [current motor position >0 cw from the ZERO position
// bool isRunning()
// float maxSpeed()
// float speed()

// =============================== Code starts here ================================================================

#include <AccelStepper.h>

// First we create the constants that we will use throughout our code
#define MOTOR_STEPS 200
#define MICROSTEPS 32
#define TOTAL_STEPS 6400

#define X_SPEED 1000 // X steps per second
#define Y_SPEED 1000 // Y
#define Z_SPEED 1000 // Z

#define X_ACCEL 5000.0 // X steps per second per second
#define Y_ACCEL 5000.0 // Y
#define Z_ACCEL 5000.0 // Z

#define EN        8       // stepper motor enable, low level effective (note put jumper so automatic)

#define X_DIR     5       // X axis, direction pin
#define Y_DIR     6       // Y
#define Z_DIR     7       // Z

#define X_STP     2       // X axis, step pin
#define Y_STP     3       // Y
#define Z_STP     4       // Z

#define BAUD_RATE 230400  // the rate at which data is read

// AccelStepper is the class we use to run all of the motors in a parallel fashion
// Documentation can be found here: http://www.airspayce.com/mikem/arduino/AccelStepper/classAccelStepper.html
AccelStepper stepper1(AccelStepper::DRIVER, X_STP, X_DIR);
AccelStepper stepper2(AccelStepper::DRIVER, Y_STP, Y_DIR);
AccelStepper stepper3(AccelStepper::DRIVER, Z_STP, Z_DIR);


// Now we declare variables we will use throughout our code (That could change!)
const int ledPin = 13;
// The buffer allows us to store bytes as they are read from the python program (64 bytes in size)
const byte buffSize = 64;
char inputBuffer[buffSize];
// We create inputs to this program by <...> where <> represent the startread and endread markers
const char startMarker = '<';
const char endMarker = '>';

byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;

// WRITE COMMAND: <RUN,DIST,123,F,0.0,0.0,0.0>
// The following is data we will read from the PC. Since the USB reads one byte at a time, we have to store a
// string of bytes in an array called messageFromPC. Then we can grab the relevant information from it.
// Note that in this application, a command sent from python takes the form: <mode, setting, motorID, value, direction, optional>
// Where mode is ["RUN", "SETTING", "JOG", "STOP"]
// setting is string ["ALL"", "FEW", "ONE", "ACCEL", "SPEED", "DELTA"]
// motorID is int [1, 2, 3] (can be combo if numbers ie 123 or 12 or 23)
// value is float [any positive floating number]
// direction is ['F', 'B']
// p1_optional is [any floating number]
// p2_optional is [any floating number]
// p3_optional is [any floating number]

char messageFromPC[buffSize] = {0};
char mode[buffSize] = {0};
int motorID = 0;
int motors[3] = {0,0,0};
AccelStepper steppers[3] = {stepper1, stepper2, stepper3};
char setting[buffSize] = {0};
float value = 0.0;
char dir[buffSize] = {0};
float optional = 0.0;

// These are values that we declare to assign as "settings" to each of the steppers
float motorSpeed = 0.0;
float motorAccel = 0.0;
float oldDistanceLeft1;
float oldDistanceLeft2;
float oldDistanceLeft3;
float jog1Delta;
float jog2Delta;
float jog3Delta;
float toMove;
float p1_toMove;
float p2_toMove;
float p3_toMove;
float p1_optional;
float p2_optional;
float p3_optional;
float distances[3];
signed long p1_distance_to_go;
signed long p1_target_position;
signed long p1_distance_left;

signed long p2_distance_to_go;
signed long p2_target_position;
signed long p2_distance_left;

signed long p3_distance_to_go;
signed long p3_target_position;
signed long p3_distance_left;

signed long distances_to_go[3];
signed long targets_position[3];
signed long distances_left[3];

unsigned long curMillis;
unsigned long prevReplyToPCmillis = 0;
unsigned long replyToPCinterval = 1000;

//=============
// Setup is only called once. When we start up the GUI the Arduino initalizes with a BAUD Rate of _________
void setup() {
  Serial.begin(BAUD_RATE);

  // flash LEDs so we know we are alive
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH);
  delay(500); // delay() is OK in setup as it only happens once
  digitalWrite(ledPin, LOW);
  delay(500);

  stepper1.setMaxSpeed(X_SPEED);
  stepper2.setMaxSpeed(Y_SPEED);
  stepper3.setMaxSpeed(Z_SPEED);
  // stepper1.setSpeed(X_SPEED);
  // stepper2.setSpeed(Y_SPEED);
  // stepper3.setSpeed(Z_SPEED);
  stepper1.setAcceleration(X_ACCEL);
  stepper2.setAcceleration(Y_ACCEL);
  stepper3.setAcceleration(Z_ACCEL);
  // tell the PC we are ready
  Serial.println("<Arduino is ready>");


}

//=============
// The loop function is what is always running and refreshes BAUD_RATE times per second
void loop() {
  curMillis = millis();
  getDataFromPC();
  // Now is when we determine which mode we are in which dictates which function to call
  //replyToPC();
  //executeThisFunction();
  //replyToPC();
}

//=============
// Here we get data from the serial port, read it one byte at a time, store each subsequent byte in the buffer (list)
// then read it and declare the values to variables in this code
void getDataFromPC() {

  // If there is data from the serial port
  if (Serial.available() > 0) {
    // turn on the LED to indicate we are receiving
    digitalWrite(ledPin, HIGH);
    // read the a single character
    char x = Serial.read();

    // the order of these IF clauses is significant
    if (x == endMarker) {
      readInProgress = false;
      newDataFromPC = true;
      // clear the buffer
      inputBuffer[bytesRecvd] = 0;
      // and parse the data
      return parseData();
    }

    if (readInProgress) {
      // add the character to the buffer
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) {
      bytesRecvd = 0;
      readInProgress = true;
    }
    digitalWrite(ledPin, LOW);
  }
}


//=============

/*
  # <Mode, Setting, Pump Num, Value>
  # Mode can be SETTING, RUN, JOG, STOP
  # Setting can be SPEED, ACCEL, DELTA, ONE, FEW, ALL, ZERO
  # Pump number can be 1 or 2 or 3 or 12 or 13 or 23. (## indicates two pumps to run)
*/

// Here is where we take the string <...> that we have read from the serial port and parse it
void parseData() {

  // split the data into its parts
  // strtok scans the string inputBuffer until it reaches a "," or a ">"
  // Then we declare the variable associated with that part of the inputBuffer
  // each strtok contiues where the previous call left off

  char * strtokIndx; // this is used by strtok() as an index


  strtokIndx = strtok(inputBuffer, ",");     // get the first part - the mode string
  strcpy(mode, strtokIndx);                  // copy it to messageFromPC

  strtokIndx = strtok(NULL, ",");            // get the second part - the setting string
  strcpy(setting, strtokIndx);               // copy it to messageFromPC


  strtokIndx = strtok(NULL, ",");            // get the third part - the motor ID int
  String motorstr(strtokIndx);

  motorID = atoi(strtokIndx);                // convert to integer and copy it to motorID

  motors[0] = 0;
  motors[1] = 0;
  motors[2] = 0;

  if(motorstr.indexOf("1") >= 0) {
    motors[0] = 1;
  }
  if(motorstr.indexOf("2") >= 0) {
    motors[1] = 1;
  }
  if(motorstr.indexOf("3") >= 0) {
    motors[2] = 1;
  }
  Serial.println("string");
  Serial.println(motorstr);
  Serial.println("Status");
  Serial.println(motors[0]);
  Serial.println(motors[1]);
  Serial.println(motors[2]);

  strtokIndx = strtok(NULL, ",");            // get the fourth part - the value float
  value = atof(strtokIndx);                  // convert to float and copy to value

  strtokIndx = strtok(NULL, ",");            // get the fifth part - the direction character
  strcpy(dir, strtokIndx);                   // copy the character to dire

  strtokIndx = strtok(NULL, ",");            // get the fourth part - the value float
  p1_optional = atof(strtokIndx);            // convert to float and copy to value

  strtokIndx = strtok(NULL, ",");            // get the fourth part - the value float
  p2_optional = atof(strtokIndx);            // convert to float and copy to value

  strtokIndx = strtok(NULL, ",");            // get the fourth part - the value float
  p3_optional = atof(strtokIndx);            // convert to float and copy to value

  distances[0] = p1_optional;
  distances[1] = p2_optional;
  distances[2] = p3_optional;
  if (strcmp(setting, "RUN") == 0) {
    distances[0] = 999999.0;
    distances[1] = 999999.0;
    distances[2] = 999999.0;
  }

  Serial.println("Status Distances");
  Serial.println(distances[0]);
  Serial.println(distances[1]);
  Serial.println(distances[2]);

  newDataFromPC = true;
  replyToPC();

  return executeThisFunction();
  }

void clearVariables() {
  char messageFromPC[buffSize] = {0};
  char mode[buffSize] = {0};
  char setting[buffSize] = {0};
  int motorID = 0;
  float value = 0.0;
  char dir[buffSize] = {0};

  float p1_optional = 0.0;
  float p2_optional = 0.0;
  float p3_optional = 0.0;
}

// =============================
// So we do a string comparison using strcmp(str1, str2) as a condition to determine what to do next
// Here we can add new functions if we like, for example if we wanted to add a "TEST" to the mode
// input we would add a condition if (strcmp(mode, "TEST") == 0 {...}
void executeThisFunction() {

  if (strcmp(mode, "STOP") == 0) {
    return stopAll();
  }

  else if (strcmp(mode, "SETTING") == 0) {
    return udpateSettings();
    //Serial.print("UPDATING SETTINGS\n");
  }

  else if (strcmp(mode, "RUN") == 0) {
    // Check if any stepper is currently running and do not allow execution if that is the case
    //if (!stepper1.isRunning()) {
      if (strcmp(setting, "DIST") == 0) {
        return runFew();
     // }
    }

  }

  else if (strcmp(mode, "PAUSE") == 0) {
    return pauseRun();
  }

  else if (strcmp(mode, "RESUME") == 0) {
    return runFew();
  }
}

//=============

// Here is where we reply to the PC if we find that we have new data from the PC
// This is executed on everyloop if we detect that we have new data from the pc

void replyToPC() {

  if (newDataFromPC) {
    newDataFromPC = false;
    Serial.print("<mode: ");
    Serial.print(mode);
    Serial.print(" ,setting: ");
    Serial.print(setting);
    Serial.print(" ,motorID: ");
    Serial.print(motorID);
    Serial.print(" ,value: ");
    Serial.print(value);
    Serial.print(" ,direction: ");
    Serial.print(dir);
    Serial.print(" ,p1 optional: ");
    Serial.print(p1_optional);
    Serial.print(" ,p2 optional: ");
    Serial.print(p2_optional);
    Serial.print(" ,p3 optional: ");
    Serial.print(p3_optional);
    Serial.print(" ,Time ");
    Serial.print(curMillis >> 9); // divide by 512 is approx = half-seconds
    Serial.println(">");
  }
  //executeThisFunction();
}


// Here we want to send our current distance to the PC
// We send the motor ID and then print out distance left
// This returns the step difference between where we are at now and where we want to be.
// Since the Baud Rate is larger than the speed of rotation for max motor speed
// we return the distance left only if it changes otherwise it would print out the same
// number a million times
void sendDistanceToPC(int mID) {
  switch (mID) {
    case 1:
      if (stepper1.distanceToGo() != oldDistanceLeft1) {
        Serial.print("<DISP1|");
        Serial.print(stepper1.distanceToGo());
        Serial.print(">");
      }
      oldDistanceLeft1 = stepper1.distanceToGo();
      break;
    case 2:
      if (stepper2.distanceToGo() != oldDistanceLeft2) {
        Serial.print("<DISP2|");
        Serial.print(stepper2.distanceToGo());
        Serial.print(">");
      }
      oldDistanceLeft2 = stepper2.distanceToGo();
      break;
    case 3:
      if (stepper3.distanceToGo() != oldDistanceLeft3) {
        Serial.print("<DISP3|");
        Serial.print(stepper3.distanceToGo());
        Serial.print(">");
      }
      oldDistanceLeft3 = stepper3.distanceToGo();
      break;
  }
}
//============
// Update the settings for each stepper. This is run before performing any moving functions
// It sets the speed, accel, and jog delta for each pump

void udpateSettings() {
  stepper1.setCurrentPosition(0.0);
  stepper2.setCurrentPosition(0.0);
  stepper3.setCurrentPosition(0.0);

  switch (motorID) {
    case 1:
      if (strcmp(setting, "SPEED") == 0) {
        stepper1.setMaxSpeed(value);
      }
      else if (strcmp(setting, "ACCEL") == 0) {
        //stepper1.setAcceleration(value);
        stepper1.setAcceleration(value);
      }
      else if (strcmp(setting, "DELTA") == 0) {
        jog1Delta = value;
      }
      break;
    case 2:
      if (strcmp(setting, "SPEED") == 0) {
        stepper2.setMaxSpeed(value);
      }
      else if (strcmp(setting, "ACCEL") == 0) {
        //stepper2.setAcceleration(value);
        stepper2.setAcceleration(value);
      }
      else if (strcmp(setting, "DELTA") == 0) {
        jog2Delta = value;
      }
      break;
    case 3:
      if (strcmp(setting, "SPEED") == 0) {
        stepper3.setMaxSpeed(value);
      }
      else if (strcmp(setting, "ACCEL") == 0) {
        //stepper3.setAcceleration(value);
        stepper3.setAcceleration(value);
      }
      else if (strcmp(setting, "DELTA") == 0) {
        jog3Delta = value;
      }
      break;
  }
  clearVariables();
}

//======================================
// The main function for moving the pumps. Takes in a displacement (in steps) and then moves that much
// For now this is implemented in a constant speed (acceleration is zero except for start and stop where it is max)
// anytime you are running your pumps you should always calll get data from PC in case you want to send a STOP command
// This should be complete!
// Need to add the ability to report distance remaining back to LCD monitor


//===================================
// This function will run few ie if (p1, p2) or (p1, p3) or (p2, p3) are enabled
int array_sum(int * array, int len) {
  int arraySum;

  arraySum = 0;
  for(int index = 0; index < len; index++)
  { arraySum += array[index]; }
  return arraySum;
}

void runFew() {
  // First we determine the direction of movement. If 1, then it's forward, otherwise it's -1.
  // We use 1 and -1 so that we can multiply any number and reverse the math, minimizing lines of code
  AccelStepper steppers[3] = {stepper1, stepper2, stepper3};

  int direction = 1;
  if (strcmp(dir, "B") == 0) {
    direction = -1;
  }
  Serial.print("Direction");
  Serial.println(direction);
  // Second we set the distance to move for each stepper.
  // We use direction and multiply the value saved in the distances array;
  // The distances array is set above to default to 999999 if 'RUN' else, the value set.
  Serial.println("Status Distances");
  Serial.println(distances[0]);
  Serial.println(distances[1]);
  Serial.println(distances[2]);

  for (int i = 0; i < 3; i += 1) {
    if (motors[i] == 1) {
      toMove = direction * distances[i];
      Serial.print("Sedding tomove command: ");
      Serial.println(toMove);
      steppers[i].move(toMove);
    }
  }
  // Finally the main loop where we move and check the steppers status
  // We declare an array to store the status of each stepper
  int stepperStatus[3] = {0, 0, 0};
  // Then we loop until that sum is equal to the number of selected steppers
  // That number is stored in the motors array, 1 for selected, 0 otherwise
  // If we have 1 and 3 for example motors = [1, 0, 1] => sum = 2
  Serial.println("Entering While Loop ");
  Serial.println(array_sum(stepperStatus, 3));

  Serial.println(motors[0]);
  Serial.println(motors[1]);
  Serial.println(motors[2]);

  Serial.println(array_sum(motors, 3));

// 4000 steps == 1 mm


  while (array_sum(stepperStatus, 3) != array_sum(motors, 3)) {
    // We iterate over the 3 possible steppers
    for (int i = 0; i < 3; i += 1) {
      // If this stepper is selected
      if (motors[i] == 1) {
        // Ask the stepper to move to position at constant speed.
        if (stepperStatus[i] == 0 ) {
          steppers[i].run();
        }
        // Check if it reached it's position
        if (steppers[i].distanceToGo() == 0) {
          // If yes then store that value in the stepperStatus array.
          stepperStatus[i] = 1;
        }
      }
    }
    getDataFromPC();
  }
  clearVariables();
}


void stopAll() {
  for (int i = 0; i < 3; i += 1) {
    steppers[i].stop();
  }
}

void pauseRun() {
  for (int i = 0; i < 3; i += 1) {
    distances_to_go[i] = steppers[i].distanceToGo();
    targets_position[i] = steppers[i].targetPosition();
    distances_left[i] = distances_to_go[i] - distances_left[i];
    steppers[i].move(p1_distance_to_go);
  }
  while (strcmp(mode, "RESUME") != 0) {
    // do nothing
    getDataFromPC();
  }
  for (int i = 0; i < 3; i += 1) {
    distances[i] = distances_left[i];
  }

  return runFew();
}
