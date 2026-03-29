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
  digitalWrite(RCLK, LOW);
}

void _srPushIN(){
  digitalWrite(SRCLK, HIGH);
  digitalWrite(SRCLK, LOW);
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
    for(uint8_t i = 0; i < 8; i++) pinMode(13-i, OUTPUT);
  } else {
    for(uint8_t i = 0; i < 8; i++) pinMode(13-i, INPUT);
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
    digitalWrite(13-i, data & 1);
    data = data >> 1;
  }
  _romWriteE();
  _romWriteD();
  _romChipD();
  delay(10);
}

uint8_t romRead(uint16_t address){
  _romOutputD();
  _srClear();
  _romSwitchMode(false);
  srSetAddr(address);
  _romChipE();
  _romOutputE();
  uint8_t ret = 0;
  for (uint8_t i = 0; i < 8; i++){
    ret |= (digitalRead(13-i) << i);
  }
  return ret;
}


void setup() {
  srSetup();
  romSetup();

  Serial.begin(9600);
  Serial.println("----BEGIN----");

  //romWrite(100, 0);

  for (uint16_t i = 0; i < 10; i++){
    romWrite((uint8_t)i*10, i);
  }
  
  for (uint16_t i = 0; i < 10; i++){
    Serial.print("Address ");
    Serial.print(i);
    Serial.print(": ");
    Serial.println(romRead(i));
  }
  
}

void loop() {
  

}
