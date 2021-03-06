/** main.c
 * Program for UTSVT BeVolt's Battery Protection System
 * @authors Sijin Woo, Chase Block,Garrett Wong
 * @lastRevised 10/2/2018
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "stm32f4xx.h"
#include "Voltage.h"
#include "Current.h"
#include "Temperature.h"
#include "Contactor.h"
#include "EEPROM.h"
//#include "CANlib.h"
#include "WDTimer.h"
#include "Gyro.h"
#include "Terminal.h"

void initialize(void);
void preliminaryCheck(void);
void faultCondition(void);

int main(){
	__disable_irq();				// Disable all interrupts until initialization is done
	initialize();					// Initialize codes/pins
	preliminaryCheck();		// Wait until all boards are powered on
	__enable_irq();				// Enable interrupts
	
	WDTimer_Start();
	while(1){
		// First update the measurements.
		Voltage_UpdateMeasurements();
		Current_UpdateMeasurements();
		Temperature_UpdateMeasurements();
		
		// Check if everything is safe
		if(Current_IsSafe() && Temperature_IsSafe(Current_IsCharging()) && Voltage_IsSafe()){
			Contactor_On();
		}else{
			break;
		}
		
		// Update necessary
		// CAN_SendMessageStatus()	// Most likely need to put this on a timer if sending too frequently
		//Terminal_CheckInput();
		// Display_UpdateScreen()
		
		WDTimer_Reset();
	}
	
	// BPS has tripped if this line is reached
	faultCondition();
}

/**
 * Initialize system.
 *	1. Initialize device drivers.
 *			- This includes communication protocols, GPIO pins, timers
 *	2. Get EEPROM data that holds all fault conditions.
 *			- By regulations, we are not allowed to be able to set the voltage, current, temperature
 *				limits while the car is moving. To make sure this doesn't happen, the EEPROM needs to be
 *				written and cannot be modified (locked) once programmed.
 *	3. Set the current, voltage, and temperature limits.
 *			- Give wrappers (Voltage, Current, Temperature) the limits
 */
void initialize(void){
	Contactor_Init();
	Contactor_Off();
	EEPROM_Init();
	WDTimer_Init();
	
	Current_Init();
	Voltage_Init();
	Temperature_Init();
}

/** preliminaryCheck
 * Before starting any data monitoring, check if all the boards are powered. If we start the data
 * collection before everything is powered on, then the system will immediately fault and not turn on
 * even though everything is safe.
 */
void preliminaryCheck(void){
	
}

/** faultCondition
 * This block of code will be executed whenever there is a fault.
 * If bps trips, make it spin and impossible to connect the battery to car again
 * until complete reboot is done.
 */
void faultCondition(void){
	while(1){
		// CAN_SendMessageStatus()
		if(!Current_IsSafe()){
			// Toggle Current fault LED
		}
		
		if(!Voltage_IsSafe()){
			// Toggle Voltage fault LED
		}
		
		if(!Temperature_IsSafe(Current_IsCharging())){
			// Toggle Temperature fault LED
		}
	}
}


//****************************************************************************************
// The following code is for testing individual pieces of code.
//****************************************************************************************
// If you want to test an individual test, change the #define NAME to what you want to what
// to use. This is used mainly to save memory for both the microcontroller and Keil.
// Keil has a limit of how much memory you can compile.
// E.g. If you want to run a LTC6811 test, change "#define CHANGE_THIS_TO_TEST_NAME" to the
//		following:
//		#define LTC6811_TEST
#define CHANGE_THIS_TO_TEST_NAME

#ifdef LTC6811_TEST
// LTC6811 Test
#include "SPI.h"
#include "LTC6811.h"
#include "UART.h"
#include "Definition.h"
#include <string.h>
void printCells(cell_asic *mods);
void print_config(cell_asic *bms_ic);
int main(){
	// Local var
	int8_t error = 0;
	
	// Initialize LTC
	__disable_irq();
	cell_asic battMod[NUM_VOLTAGE_BOARDS];
	UART3_Init(9600);
	printf("Testing LTC6811:\n\r");
	LTC6811_Init(battMod);
	LTC6811_wrcfg(NUM_VOLTAGE_BOARDS, battMod);
	print_config(battMod);
	wakeup_sleep(NUM_VOLTAGE_BOARDS);
	error = LTC6811_rdcfg(NUM_VOLTAGE_BOARDS, battMod);
  LTC6811_adcv(ADC_CONVERSION_MODE, ADC_DCP, CELL_CH_TO_CONVERT);
	__enable_irq();
	while(1){
		printf("Waiting...\n\r");
		wakeup_sleep(NUM_VOLTAGE_BOARDS);
		LTC6811_adcv(ADC_CONVERSION_MODE,ADC_DCP,CELL_CH_TO_CONVERT);
    LTC6811_pollAdc();
    error = LTC6811_rdcv(0, NUM_VOLTAGE_BOARDS, battMod); // Set to read back all cell voltage registers
		printCells(battMod);
		for(uint32_t i = 0; i < 10000000; i++);
	}
}

void printCells(cell_asic *mods){
	for (int current_ic = 0 ; current_ic < NUM_VOLTAGE_BOARDS; current_ic++){
		for (int i=0; i<mods[0].ic_reg.cell_channels; i++){
      printf("C%d", i + 1);
      printf(":");
      printf("%4f", mods[current_ic].cells.c_codes[i]*0.0001);
      printf("\n\r");
    }
		printf("\n\r");
  }
}

void print_config(cell_asic *bms_ic)
{
  int cfg_pec;

  printf("Written Configuration: ");
  for (int current_ic = 0; current_ic<NUM_VOLTAGE_BOARDS; current_ic++)
  {
    printf(" IC ");
    printf("%d", current_ic+1);
    printf(": ");
    printf("0x");
    printf("%x", bms_ic[current_ic].config.tx_data[0]);
    printf(", 0x");
    printf("%x", bms_ic[current_ic].config.tx_data[1]);
    printf(", 0x");
    printf("%x", bms_ic[current_ic].config.tx_data[2]);
    printf(", 0x%x", bms_ic[current_ic].config.tx_data[3]);
    printf(", 0x%x", bms_ic[current_ic].config.tx_data[4]);
    printf(", 0x%x", bms_ic[current_ic].config.tx_data[5]);
    cfg_pec = pec15_calc(6,&bms_ic[current_ic].config.tx_data[0]);
		printf(", Calculated PEC: 0x%x",(uint8_t)(cfg_pec>>8));
    printf("%d", (uint8_t)(cfg_pec>>8));
    printf(", 0x%x", (uint8_t)cfg_pec);
    printf("\n\r");
  }
}
#endif

#ifdef SPI_TEST
//****************************************************************************************
// SPI Test
#include "SPI.h"
#include "UART.h"
int SPITestmain(){
	__disable_irq();
	UART3_Init(9600);
	SPI_Init8();
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);	// 1) Initialize GPIO portB clock
	GPIO_InitTypeDef GPIO_InitStruct;
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_6;								// 2) Initialize which pins to use
	GPIO_InitStruct.GPIO_Mode = GPIO_Mode_OUT;						// 3) Set PA8 and PA9 as alternate function
	GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;							// 4) Set the resistor to pull-up
	GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;				// 5) Initialize the speed of communication as 25 MHz
	GPIO_InitStruct.GPIO_OType = GPIO_OType_PP;						// 6) Set to open drain
	GPIO_Init(GPIOB, &GPIO_InitStruct);
	GPIOB->ODR |= GPIO_Pin_6;
	__enable_irq();
	
	char str[30] = "Testing\n\r";
	UART3_Write(str, strlen(str));
	GPIOB->ODR &= ~GPIO_Pin_6;
	SPI_Write8((uint8_t *)str, strlen(str));
	GPIOB->ODR |= GPIO_Pin_6;
	while(1){
		
	}
}
#endif

#ifdef UART_TEST
//****************************************************************************************
// Debug UART Test
int UARTmain(){
	UART3_Init(9600);
	while(1){
		printf("Die world\n");
		for(uint32_t i = 0; i < 100000; i++);
	}
}
#endif

#ifdef GYRO_TEST
//****************************************************************************************
// Gyro test
int gyroTestmain(){
	//FXAS21002CQR1_Init();
	UART3_Init(9600);
	while(1){
		//uint16_t *vals = FXAS21002CQR1_Measure();
		// print or something
	}
}
#endif

#ifdef ADC_TEST
//****************************************************************************************
#include "ADC.h"
#include <stdio.h>
int ADCmain(){
	char str[50];
	UART3_Init(9600);
	ADC_InitHilo();
	while(1){
		sprintf(str,"%d\t%d\n",(int)ADC_ReadHigh(),(int)ADC_ReadLow());
		UART3_Write(str,strlen(str));
	}		
}
#endif
