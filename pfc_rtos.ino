#include "SoftwareSerial.h"
#include "HardwareSerial.h"
#include "Wire.h"
#include "MPU6050.h"
#include "I2Cdev.h"
#include <TinyGPS.h>
#include <elapsedMillis.h>

String buffer2 = "";
int vibracall = 25;
int lembrete = 0;
int lembreteflag = 0;

char* nova_string = "";
String resultado = "";
String myString = "";
String myAnterior = "0";

 #define GPS_RX 4  //RXD
#define GPS_TX 2  //TXD
#define GPS_Serial_Baud 9600
TinyGPS gps;
HardwareSerial gpsSerial(1);  //if using UART1


bool newData = false;
float flat, flon;


#define MPU                     0x68  // Endereço I2C para comunicação com o MPU


MPU6050 mpu(MPU); 

float AccX, AccY, AccZ;   // Armazenar o valor da leitura de aceleração dos eixos X, Y e Z
float TotalAcceleration;  // Armazenar o valor da soma vetorial da aceleração dos eixos X, Y e Z

uint8_t value = 0;
float LSB_Sensitivity = 2048.00;        //Sensibilidade configurada para a escala da medida de aceleração

float listofvalues[50];

int queda = 0;
int cd = 0;

const int buttonPin = 12;
bool resetbutton = 0;
int buttoncount = 0;
int reset = 0;
int cb = 0;
int buttonState = 0;  

String str = "";
String previousMsg = "";

#define rxPin 16
#define txPin 17
// The serial connection to the GSM device
SoftwareSerial gprsSerial(rxPin,txPin);



// Define tasks
void TaskGSM( void *pvParameters );
void TaskAnalogRead( void *pvParameters );
void TaskGPS( void *pvParameters );
void TaskVibra( void *pvParameters );
void TaskLembrete( void *pvParameters );

// The setup function runs once when you press reset or power on the board.
void setup() {
  gprsSerial.begin(9600);               // the GSM baud rate 
  pinMode(buttonPin, INPUT);
  
  Serial.begin(9600);
  
  xTaskCreate(
    TaskGSM
    ,  "Task GSM" // A name just for humans
    ,  3000        // The stack size can be checked by calling `uxHighWaterMark = uxTaskGetStackHighWaterMark(NULL);`
    ,  NULL // Task parameter which can modify the task behavior. This must be passed as pointer to void.
    ,  3  // Priority
    ,  NULL 
    // Task handle is not used here - simply pass NULL
    );

  
  xTaskCreate(
    TaskAnalogRead
    ,  "Analog Read"
    ,  2048  
    ,  NULL  
    ,  4  
    ,  NULL 
    );

  xTaskCreate(
    TaskGPS
    ,  "GPS"
    ,  3000
    ,  NULL
    ,  3  
    ,  NULL );

  
  xTaskCreate(
    TaskVibra
    ,  "Vibração"
    ,  3000 
    ,  NULL
    ,  2  
    ,  NULL );

    xTaskCreate(
    TaskLembrete
    ,  "Lembrete"
    ,  1000 
    ,  NULL
    ,  3  
    ,  NULL );

  // Now the task scheduler, which takes over control of scheduling individual tasks, is automatically started.
}

void loop(){
  vTaskDelay(10);
}

/*--------------------------------------------------*/
/*---------------------- Tasks ---------------------*/
/*--------------------------------------------------*/

void TaskGSM(void *pvParameters){  // This is a task.
  for (;;) 
  {
    Serial.println("Rodando GSM...");
    
  if(reset == 1){
      if (previousMsg == "queda"){
        queda = 1;
      }
      if (previousMsg == "button"){
        buttoncount = 1;
      }
      if(previousMsg == "gps"){
        newData = true;
      }
    }

    if (gprsSerial.available())
    Serial.write(gprsSerial.read());  
 
  sendATcommand("AT", "OK");
  delay(200);
 
  gprsSerial.println("AT+CPIN?");
  delay(200);
 
  gprsSerial.println("AT+CREG?");
  delay(200);
 
  gprsSerial.println("AT+CGATT?");
  delay(200);
 
  gprsSerial.println("AT+CIPSHUT");
  delay(200);
 
  gprsSerial.println("AT+CIPSTATUS");
  delay(500);
 
  gprsSerial.println("AT+CIPMUX=0");
  delay(500);
 
  sendATcommand("AT+CSTT=\"zap.vivo.com.br\",\"vivo\",\"vivo\"", "OK");
  delay(500);
  
  gprsSerial.println("AT+CIICR");
  delay(2000);
 
  gprsSerial.println("AT+CIFSR");
  delay(2000);
 
  gprsSerial.println("AT+CIPSPRT=0");
  delay(5000);
 
  sendATcommand("AT+CIPSTART=\"TCP\",\"api.thingspeak.com\",\"80\"", "OK");
  delay(7000);
 
  sendCIPSENDcommand("AT+CIPSEND");//begin send data to remote server
  delay(2000);
  
    if(newData){  
    str="GET https://api.thingspeak.com/update?api_key=WTKGLIUU9S9GA20X&field1=" + String(flat, 6) +"&field2="+String(flon, 6);
    Serial.println("GET https://api.thingspeak.com/update?api_key=WTKGLIUU9S9GA20X&field1=" + String(flat, 6) +"&field2="+String(flon, 6));
    newData = false;
    previousMsg = "gps";
    lembreteflag = 0;
    delay(200);
    }
    if(lembrete==1){
      lembreteflag = 1;
      str = "GET https://api.thingspeak.com/channels/2423872/fields/1.json?results=1";
      Serial.println("GET https://api.thingspeak.com/channels/2423872/fields/1.json?results=1");
      delay(200);
    }

    if(queda == 1){ 
    queda = 0;
    str="GET https://api.thingspeak.com/update?api_key=ALFQ18LP4X4K9QNB&field1=" + String(cd);
    Serial.println("GET https://api.thingspeak.com/update?api_key=ALFQ18LP4X4K9QNB&field1=" + String(cd));
    delay(200);
    previousMsg = "queda";
    lembreteflag = 0;
    }
    if(buttoncount == 1){ 
    str="GET https://api.thingspeak.com/update?api_key=Z7QYMM34YODC4UAX&field1=" + String(cb);
    Serial.println("GET https://api.thingspeak.com/update?api_key=Z7QYMM34YODC4UAX&field1=" + String(cb));
    previousMsg = "button";
    buttoncount = 0;
    lembreteflag = 0;
    delay(200);
    }
    
    
  
  Serial.println(str);
  gprsSerial.println(str);
  
  delay(1000);
 
  gprsSerial.println((char)26);//sending
  delay(3500);//waitting for reply, important! the time is base on the condition of internet 
  gprsSerial.println();
 
 
  gprsSerial.println("AT+CIPSHUT");//close the connection
  delay(100);
  vTaskDelay(2000);
}
}


void TaskLembrete(void *pvParameters){
  (void) pvParameters;
  for(;;){
    lembrete = 1;
    delay(30000);
    lembrete = 0;
    delay(30000);
  }
}
void TaskGPS(void *pvParameters)  
{
    gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX); 

    (void) pvParameters;
for (;;)
  {
    unsigned long chars;
  
    if(gpsSerial.available())
    {
      
      char c = gpsSerial.read();
      //Serial.write(c); //apague o comentario para mostrar os dados crus
      if (gps.encode(c)) // Atribui true para newData caso novos dados sejam recebidos
        newData = true;
    }

    if (newData)
    {
    //Serial.print("newData == true");
    unsigned long age;
    gps.f_get_position(&flat, &flon, &age);
    Serial.print("LAT=");
    Serial.print(flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6);
    Serial.print(" LON=");
    Serial.print(flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6);
    Serial.print(" SAT=");
    Serial.print(gps.satellites() == TinyGPS::GPS_INVALID_SATELLITES ? 0 : gps.satellites());
    Serial.print(" PREC=");
    Serial.print(gps.hdop() == TinyGPS::GPS_INVALID_HDOP ? 0 : gps.hdop());
    Serial.println();
    vTaskDelay( 5000 ); // wait 
    }
    vTaskDelay( 10 ); 

  }

}

void TaskAnalogRead(void *pvParameters){  
  (void) pvParameters;
  

Wire.begin();

/** Set sleep mode status.
  * @param enabled New sleep mode enabled status
  */
  mpu.setSleepEnabled(false);
  /** Set clock source setting.
  * An internal 8MHz oscillator, gyroscope based clock, or external sources can
  * be selected as the MPU-6050 clock source. When the internal 8 MHz oscillator
  * or an external source is chosen as the clock source, the MPU-6050 can operate
  * in low power modes with the gyroscopes disabled.
  *
  * CLK_SEL | Clock Source
  * --------+--------------------------------------
  * 0       | Internal oscillator
  * 1       | PLL with X Gyro reference
  * 2       | PLL with Y Gyro reference
  * 3       | PLL with Z Gyro reference
  * 4       | PLL with external 32.768kHz reference
  * 5       | PLL with external 19.2MHz reference
  * 6       | Reserved
  * 7       | Stops the clock and keeps the timing generator in reset
  *
  * @param source New clock source setting
  */
  mpu.setClockSource(0);

  /** Set temperature sensor enabled status.
  *
  * @param enabled New temperature sensor enabled status
  */
  mpu.setTempSensorEnabled(false);

  /** Set gyroscope standby enabled status.
  * @param New X-axis standby enabled status
  * @param New Y-axis standby enabled status
  * @param New Z-axis standby enabled status
  */
  mpu.setStandbyXGyroEnabled(true);
  mpu.setStandbyYGyroEnabled(true);
  mpu.setStandbyZGyroEnabled(true);

  /** Set full-scale accelerometer range.
  * The FS_SEL parameter allows setting the full-scale range of the accelerometer
  * sensors, as described in the table below.
  *
  * 0 = +/- 2g
  * 1 = +/- 4g
  * 2 = +/- 8g
  * 3 = +/- 16g
  *
  * @param range New full-scale accelerometer range setting
  */
  mpu.setFullScaleAccelRange(1);

  int cont, aux1;


  for (;;){
    
  cont = 0;
      //Obter a aceleração total dos três eixos
    TotalAcceleration = getTotalAcceleration();
  

  if (TotalAcceleration < 0.4) { 
  //Se a aceleração for menor que 0.4G
    for (int i = 0; i < 50; i++) {
      listofvalues[i] = TotalAcceleration;
      if(TotalAcceleration > 5){
        cont++;
        aux1 = i;
      }
      delay(10);
      TotalAcceleration = getTotalAcceleration();
    }
  

    if(cont > 3) { 
          value++;
          Serial.println(("QUEDA"));
          queda = 1;
          cd++;
    }

  }
    // read the input on analog pin:
    buttonState = digitalRead(buttonPin);
    if(buttonState == 1){
      Serial.println(buttonState);
      cb++;
      buttoncount = 1;
    }
    
    vTaskDelay(10);  

  }
  }




void TaskVibra(void *pvParameters){
  (void) pvParameters;
  pinMode(vibracall, OUTPUT);
  for(;;){
    if (gprsSerial.available() != 0){ // for ignoring the NULLs
        String c = gprsSerial.readString();
        Serial.print(c);
        buffer2.concat(c);
        if(buffer2.indexOf("SEND OK")>0){
          Serial.println("deu certo");
          Serial.println(c);
          if (buffer2.indexOf("field1")>0){
            int index = buffer2.lastIndexOf("field1");
            myString =  buffer2.substring(index+9,index+10);
            Serial.println(myString);
        if (myString.compareTo(myAnterior)!=0 && lembreteflag == 1){
          analogWrite(vibracall, 700);
          delay(2000);
          analogWrite(vibracall, 0);
          delay(2000);
          analogWrite(vibracall, 700);
          delay(2000);
          analogWrite(vibracall, 0);
          delay(2000);
          analogWrite(vibracall, 700);
          delay(2000);
          analogWrite(vibracall, 0);
          myAnterior = myString; 
        }}
        
      }
    }
    else{
      buffer2.clear();
    }
    delay(100);
  }

}
void sendCIPSENDcommand(char* ATcommand){
  String response;
  while( gprsSerial.available() > 0) {      
      gprsSerial.read();
      delay(10);
    }
    if (ATcommand[0] != '\0'){
      //Send the AT command 
      gprsSerial.println(ATcommand);
      //Serial.println(ATcommand);
      
    }
  if(gprsSerial.available() != 0){
    response = gprsSerial.readString();
    Serial.println("response cipsend: ");
    Serial.println(response);
    if(response == "ERROR"){
      reset = 1;
    }
  }
}
int8_t sendATcommand(char* ATcommand, char* expected_answer){

    uint8_t answer=0;
    String response;
    int c = 0;
    
    //Clean the input buffer
    while( gprsSerial.available() > 0) {      
      gprsSerial.read();
      delay(10);
    }
    
    if (ATcommand[0] != '\0'){
      //Send the AT command 
      gprsSerial.println(ATcommand);
      //Serial.println(ATcommand);
      
    }
        if(gprsSerial.available() != 0){
          response = gprsSerial.readString();
          Serial.println("response: ");
          Serial.println(response);
          if(response.indexOf("OK") > 0){
            answer = 1;
            reset = 0;
            Serial.println(answer);
          }else{
              Serial.println("else");
              reset = 1;
              answer = 1;
                
          } 
        //}
      
    }

  //Serial.println(response);
  return answer;
}

float getTotalAcceleration() {
  AccX = mpu.getAccelerationX() / LSB_Sensitivity; // Obtem aceleração do eixo X
  AccY = mpu.getAccelerationY() / LSB_Sensitivity; // Obtem aceleração do eixo Y
  AccZ = mpu.getAccelerationZ() / LSB_Sensitivity; // Obtem aceleração do eixo Z
  //Serial.print(AccX);
  //Serial.print(AccY);
  //Serial.println(AccZ);
  return sqrt(pow(AccX, 2) + pow(AccY, 2) + pow(AccZ, 2));
}

