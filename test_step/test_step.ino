#include <AccelStepper.h>

// --- ĐỊNH NGHĨA CHÂN CÔNG TẮC HÀNH TRÌNH CHUẨN CNC SHIELD V3 ---
#define limitSwitch1 9  // Khe X trên Shield
#define limitSwitch2 10 // Khe Y trên Shield
#define limitSwitch4 A3 // Chân A3 (Không dùng khe Z)

// Chân Enable của CNC Shield V3
#define EN_PIN 8 

// Khởi tạo các stepper (Chỉ X, Y và A)
AccelStepper stepper1(1, 2, 5);   // Trục X
AccelStepper stepper2(1, 3, 6);   // Trục Y
AccelStepper stepper4(1, 12, 13); // Trục A

void setup() {
  Serial.begin(115200);

  // Cài đặt chân công tắc hành trình dạng kéo lên (Pull-up)
  pinMode(limitSwitch1, INPUT_PULLUP);
  pinMode(limitSwitch2, INPUT_PULLUP);
  pinMode(limitSwitch4, INPUT_PULLUP);

  // Bật Enable cho driver A4988
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);

  // Cài đặt thông số cơ bản cho Motor
  stepper1.setMaxSpeed(1000);
  stepper2.setMaxSpeed(1000);
  stepper4.setMaxSpeed(1000);

  showMenu();
}

void loop() {
  if (Serial.available() > 0) {
    char choice = Serial.read();
    
    // Bỏ qua ký tự thừa
    if (choice == '\n' || choice == '\r') return; 

    switch (choice) {
      case '0':
        testAllSwitches();
        break;
      case '1':
        // Chạy motor X ngược chiều, tốc độ chậm (-150)
        testSingleMotor(stepper1, limitSwitch1, "Motor 1 (Truc X)", -150);
        break;
      case '2':
        // Chạy motor Y ngược chiều, tốc độ chậm (-150)
        testSingleMotor(stepper2, limitSwitch2, "Motor 2 (Truc Y)", -150);
        break;
      case '4':
        // Chạy motor A ngược chiều, tốc độ chậm (-150)
        testSingleMotor(stepper4, limitSwitch4, "Motor 4 (Truc A)", -150);
        break;
      default:
        Serial.println("Lenh khong hop le!");
        break;
    }
    showMenu();
  }
}

void showMenu() {
  Serial.println("\n===== MENU TEST CNC SHIELD V3 (3 MOTOR) =====");
  Serial.println("Go '0': Kiem tra tin hieu Cong tac (An tay de test)");
  Serial.println("Go '1': Chay cham Motor X (An CT khe X de dung)");
  Serial.println("Go '2': Chay cham Motor Y (An CT khe Y de dung)");
  Serial.println("Go '4': Chay cham Motor A (An CT A3 de dung)");
  Serial.println("=============================================");
}

// Hàm test tín hiệu công tắc
void testAllSwitches() {
  Serial.println("-> Dang doc tin hieu cong tac... (Go 'q' de thoat)");
  int last1 = -1, last2 = -1, last4 = -1;
  
  while (true) {
    if (Serial.available()) {
      if (Serial.read() == 'q') break;
    }

    int s1 = digitalRead(limitSwitch1);
    int s2 = digitalRead(limitSwitch2);
    int s4 = digitalRead(limitSwitch4);

    if (s1 != last1 || s2 != last2 || s4 != last4) {
      Serial.print("Trang thai -> X(Pin 9): "); Serial.print(s1);
      Serial.print(" | Y(Pin 10): "); Serial.print(s2);
      Serial.print(" | A(Pin A3): "); Serial.println(s4);
      
      last1 = s1; last2 = s2; last4 = s4;
    }
    delay(10); 
  }
  Serial.println("-> Da thoat che do test cong tac.");
}

// Hàm chạy motor và chờ công tắc
void testSingleMotor(AccelStepper &stepper, int switchPin, String name, float testSpeed) {
  Serial.println("\n-> Dang chay " + name + "...");
  Serial.println("=> HAY BAM CONG TAC TUONG UNG DE DUNG MOTOR!");
  
  int normalState = digitalRead(switchPin);
  stepper.setSpeed(testSpeed); 

  while (digitalRead(switchPin) == normalState) {
    stepper.runSpeed();
    
    // Cứu hộ khẩn cấp
    if (Serial.available()) {
      if (Serial.read() == 'q') {
        Serial.println("=> DA DUNG KHAN CAP TU BAN PHIM!");
        stepper.stop();
        return;
      }
    }
  }

  Serial.println("=> THANH CONG! Motor da dung vi cham cong tac.");
  stepper.stop(); 
  delay(500); 
}