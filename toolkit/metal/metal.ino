//-----SR CTL-------
#define SRCLR A0
#define SRCLK A1
#define RCLK A2
#define SROE A3
#define SER A4

//-----ROM CTL------
#define RWE 2
#define ROE 3
#define RCE 4
//13 - 1/0 0; 6 - I/O 7

//----SR HELPERS----
void _srClear(){
  digitalWrite(SRCLR, LOW);
  digitalWrite(SRCLR, HIGH);
}

void _srOutputE(){
  digitalWrite(SROE, LOW);
}
void _srOutputD(){
  digitalWrite(SROE, HIGH);
}

void _srPushPH(){
  digitalWrite(RCLK, HIGH);
  delayMicroseconds(5);
  digitalWrite(RCLK, LOW);
  delayMicroseconds(5);
}

void _srPushIN(){
  digitalWrite(SRCLK, HIGH);
  delayMicroseconds(5);
  digitalWrite(SRCLK, LOW);
  delayMicroseconds(5);
}

//---SR FUNCTIONS----
void srSetup(){
  pinMode(SRCLK, OUTPUT);
  pinMode(SER, OUTPUT);
  pinMode(RCLK, OUTPUT);
  pinMode(SRCLR, OUTPUT);
  pinMode(SROE, OUTPUT);

  _srClear();
  _srOutputE();
  _srPushPH();
}

void srSetAddr(uint16_t addr) {
  for(uint8_t i = 0; i < 16; i++){
    digitalWrite(SER, addr & 0b00000001);
    _srPushIN();
    addr = addr >> 1;
  }
  _srPushPH();
}

void _romOutputE(){
  digitalWrite(ROE, LOW);
}
void _romOutputD(){
  digitalWrite(ROE, HIGH);
}
void _romChipE(){
  digitalWrite(RCE, LOW);
}
void _romChipD(){
  digitalWrite(RCE, HIGH);
}
void _romWriteE(){
  digitalWrite(RWE, LOW);
}
void _romWriteD(){
  digitalWrite(RWE, HIGH);
}

void _romSwitchMode(bool isWrite){
if (isWrite) {
    for(uint8_t i = 0; i < 8; i++) pinMode(12-i, OUTPUT);
  } else {
    for(uint8_t i = 0; i < 8; i++) pinMode(12-i, INPUT);
  }
}

//---ROM FUNCTIONS---
void romSetup(){
  pinMode(ROE, OUTPUT);
  pinMode(RCE, OUTPUT);
  pinMode(RWE, OUTPUT);



  _romWriteD();
  _romChipD();
  _romOutputD();
}

void romWrite(uint8_t data, uint16_t address){
  _srClear();
  _romSwitchMode(true);
  _romOutputD();
  srSetAddr(address);
  _romChipE();
  for(uint8_t i = 0; i < 8; i++){
    digitalWrite(12-i, data & 1);
    data = data >> 1;
  }
  _romWriteE();
  _romWriteD();
  _romChipD();
  delay(10);
}

uint8_t romRead(uint16_t address){
  _romOutputD();
  _romSwitchMode(false);
  srSetAddr(address);
  _romChipE();
  _romOutputE();
  delayMicroseconds(5);
  uint8_t ret = 0;
  for (uint8_t i = 0; i < 8; i++){
    ret |= (digitalRead(12-i) << i);
  }
  _romOutputD(); 
  _romChipD();
  return ret;
}


void setup() {
  randomSeed(analogRead(A5));
  srSetup();
  romSetup();

  Serial.begin(115200);
}

enum SlaveMode {
  WRITE = 0x10,
  READ = 0x11,
  STREAM_WRITE = 0x12
};

uint16_t serAddress = 0;
uint8_t serData = 0;
uint8_t serBuffer[6];
void loop() {
  //wait for instruction
  if (Serial.available() >= 4){
    Serial.readBytes(serBuffer, 4);
    serAddress = 0;
    serAddress |= serBuffer[1];
    serAddress <<= 8;
    serAddress |= serBuffer[2];
    if (serBuffer[0] == WRITE){
      romWrite(serBuffer[3], serAddress);
      Serial.write(0x06);
    } else if (serBuffer[0] == READ){
      Serial.write(romRead(serAddress));
    } else if (serBuffer[0] == STREAM_WRITE) {
      serAddress = (serBuffer[1] << 8) | serBuffer[2];
      uint8_t blockSize = serBuffer[3]; 
      
      for (int i = 0; i < blockSize; i++) {
        while (Serial.available() == 0); 
        uint8_t dataByte = Serial.read();
        
        romWrite(dataByte, serAddress + i);
      }
      Serial.write(0x06); 
    }
  }

}
