#include "main.h"
#include <stdint.h>
#include "flash.h"
#include "stm32wbxx_hal.h"


/**
 * @brief   This function erases the memory.
 * @param   address: First address to be erased (the last is the end of the flash).
 * @return  status: Report about the success of the erasing.
 */
flash_status flash_erase(uint32_t address)
{
    flash_status status = FLASH_OK;
    HAL_StatusTypeDef hal_status;
    uint32_t pageError = 0;

    __disable_irq();
    HAL_FLASH_Unlock();

    FLASH_EraseInitTypeDef eraseInit;
    eraseInit.TypeErase   = FLASH_TYPEERASE_PAGES;     // Sayfa bazlı silme
    eraseInit.Page        = (address - FLASH_BASE) / FLASH_PAGE_SIZE;
    eraseInit.NbPages     = 1;                         // Sadece 1 sayfa sil
#if defined(FLASH_BANK_1) && defined(FLASH_BANK_2)
    eraseInit.Banks       = FLASH_BANK_1;              // Hangi banktaysa seç
#endif

    hal_status = HAL_FLASHEx_Erase(&eraseInit, &pageError);

    if (hal_status != HAL_OK)
    {
        status |= FLASH_ERROR;
    }

    HAL_FLASH_Lock();
    __enable_irq();

    return status;
}


/**
 * @brief   This function flashes the memory.
 * @param   address: First address to be written to.
 * @param   *data:   Array of the data that we want to write.
 * @param   *length: Size of the array.
 * @return  status: Report about the success of the writing.
 */
flash_status flash_write(uint32_t address, uint32_t *data, uint32_t length)
{
  flash_status status = FLASH_OK;

  __disable_irq();
  HAL_FLASH_Unlock();
  uint32_t adr = address;

  for (uint32_t i = 0u; (i < length) && (FLASH_OK == status); i += 2)
  {
    if (FLASH_APP_END_ADDRESS <= adr)
    {
      status |= FLASH_ERROR_SIZE;
    }
    else
    {
      uint64_t dword = ((uint64_t)data[i+1] << 32) | data[i]; // iki word → 1 doubleword

      if (HAL_OK != HAL_FLASH_Program(FLASH_TYPEPROGRAM_DOUBLEWORD, adr, dword))
      {
        status |= FLASH_ERROR_WRITE;
      }

      FLASH_WaitForLastOperation(2);

      if ( (*(volatile uint64_t*)adr) != dword )
      {
        status |= FLASH_ERROR_READBACK;
      }

      adr += 8u; // doubleword = 8 byte ilerle
    }
  }

  HAL_FLASH_Lock();
  __enable_irq();
  return status;
}

/**
 * @brief   Actually jumps to the user application.
 * @param   void
 * @return  void
 */

typedef void (*fnc_ptr)(void);
void flash_jump_to_app(void)
{
  /* Function pointer to the address of the user application. */
  fnc_ptr jump_to_app;
  jump_to_app = (fnc_ptr)(*(volatile uint32_t*) (FLASH_APP_START_ADDRESS+4u));
  //HAL_RCC_DeInit();
  HAL_DeInit();
  /* Change the main stack pointer. */
  SCB->VTOR = FLASH_APP_START_ADDRESS;
  __set_MSP(*(volatile uint32_t*)FLASH_APP_START_ADDRESS);
  jump_to_app();
}



