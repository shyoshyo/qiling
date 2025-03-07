[FLASH]
type = memory
size = 0x80000
base = 0x8000000

[FLASH OTP]
type = memory
size = 0x400
base = 0x1fff7800

[SRAM]
type = memory
size = 0x20000
base = 0x20000000

[SYSTEM]
type = memory
size = 0x7800
base = 0x1FFF0000

[SRAM BB]
type = bitband
size = 0x100000
base = 0x20000000
alias = 0x22000000

[PERIP]
type = mmio
size = 0x100000
base = 0x40000000

[PERIP BB]
type = bitband
size = 0x100000
base = 0x40000000
alias = 0x42000000

[PPB]
type = mmio
size = 0x10000
base = 0xE0000000

[SYSTICK]
type = core periperal
base = 0xE000E010
class = CortexM4SysTick

[NVIC]
type = core periperal
base = 0xE000E100
class = CortexM4Nvic

[SCB]
type = core periperal
base = 0xE000ED00
class = CortexM4Scb

[TIM2]
type = periperal
base = 0x40000000
class = STM32F4xxTim
intn = 28

[TIM3]
type = periperal
base = 0x40000400
class = STM32F4xxTim
intn = 29

[TIM4]
type = periperal
base = 0x40000800
class = STM32F4xxTim
intn = 30

[TIM5]
type = periperal
base = 0x40000c00
class = STM32F4xxTim
intn = 50

[RTC]
type = periperal
base = 0x40002800
class = STM32F4xxRtc
wkup_intn = 3
alarm_intn = 41

[WWDG]
type = periperal
base = 0x40002c00
class = STM32F4xxWwdg
intn = 0

[IWDG]
type = periperal
base = 0x40003000
class = STM32F4xxIwdg

[I2S2ext]
type = periperal
base = 0x40003400
class = STM32F4xxSpi

[SPI2]
type = periperal
base = 0x40003800
class = STM32F4xxSpi
intn = 36

[SPI3]
type = periperal
base = 0x40003c00
class = STM32F4xxSpi
intn = 51

[I2S3ext]
type = periperal
base = 0x40004000
class = STM32F4xxSpi

[USART2]
type = periperal
base = 0x40004400
class = STM32F4xxUsart
intn = 38

[I2C1]
type = periperal
base = 0x40005400
class = STM32F4xxI2c
ev_intn = 31
er_intn = 32

[I2C2]
type = periperal
base = 0x40005800
class = STM32F4xxI2c
ev_intn = 33
er_intn = 34

[I2C3]
type = periperal
base = 0x40005c00
class = STM32F4xxI2c
ev_intn = 72
er_intn = 73

[PWR]
type = periperal
base = 0x40007000
class = STM32F4xxPwr

[TIM1]
type = periperal
base = 0x40010000
class = STM32F4xxTim
brk_tim9_intn = 24
up_tim10_intn = 25
trg_com_tim11_intn = 26
cc_intn = 27

[USART1]
type = periperal
base = 0x40011000
class = STM32F4xxUsart
intn = 37

[USART6]
type = periperal
base = 0x40011400
class = STM32F4xxUsart
intn = 71

[ADC1]
type = periperal
base = 0x40012000
class = STM32F4xxAdc

[SDIO]
type = periperal
base = 0x40012c00
class = STM32F4xxSdio
intn = 49

[SPI1]
type = periperal
base = 0x40013000
class = STM32F4xxSpi
intn = 35

[SPI4]
type = periperal
base = 0x40013400
class = STM32F4xxSpi
intn = 84

[SYSCFG]
type = periperal
base = 0x40013800
class = STM32F4xxSyscfg

[EXTI]
type = periperal
base = 0x40013c00
class = STM32F4xxExti

[TIM9]
type = periperal
base = 0x40014000
class = STM32F4xxTim

[TIM10]
type = periperal
base = 0x40014400
class = STM32F4xxTim

[TIM11]
type = periperal
base = 0x40014800
class = STM32F4xxTim

[GPIOA]
type = periperal
base = 0x40020000
class = STM32F4xxGpio

[GPIOB]
type = periperal
base = 0x40020400
class = STM32F4xxGpio

[GPIOC]
type = periperal
base = 0x40020800
class = STM32F4xxGpio

[GPIOD]
type = periperal
base = 0x40020c00
class = STM32F4xxGpio

[GPIOE]
type = periperal
base = 0x40021000
class = STM32F4xxGpio

[GPIOH]
type = periperal
base = 0x40021c00
class = STM32F4xxGpio

[CRC]
type = periperal
base = 0x40023000
class = STM32F4xxCrc

[RCC]
type = periperal
base = 0x40023800
class = STM32F4xxRcc
intn = 5

[DMA1]
type = periperal
base = 0x40026000
class = STM32F4xxDma
stream0_intn = 11
stream1_intn = 12
stream2_intn = 13
stream3_intn = 14
stream4_intn = 15
stream5_intn = 16
stream6_intn = 17
stream7_intn = 47

[DMA2]
type = periperal
base = 0x40026400
class = STM32F4xxDma
stream0_intn = 56
stream1_intn = 57
stream2_intn = 58
stream3_intn = 59
stream4_intn = 60
stream5_intn = 68
stream6_intn = 69
stream7_intn = 70

[DBGMCU]
type = periperal
base = 0xe0042000
class = STM32F4xxDbgmcu

