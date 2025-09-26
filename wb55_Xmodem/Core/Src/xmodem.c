/**
 * @file    xmodem.c
 * @author  Ferenc Nemeth
 * @date    21 Dec 2018
 * @brief   This module is the implementation of the Xmodem protocol.
 *
 *          Copyright (c) 2018 Ferenc Nemeth - https://github.com/ferenc-nemeth
 */

#include "xmodem.h"
#include "flash.h"
#include <stdio.h>
#include "main.h"
#include "stm32wbxx_hal.h"
#include "stm32wbxx_hal_crc.h"

extern CRC_HandleTypeDef hcrc;

/* Global variables. */
static uint8_t xmodem_packet_number = 0u;         /**< Packet number counter. */
static uint32_t xmodem_actual_flash_address = 0u; /**< Address where we have to write. */
static uint8_t x_first_packet_received = false;   /**< First packet or not. */
static uint32_t xmodem_bytes_written = 0u;        /**< Total bytes written for sector management. */

/* Local functions. */
static uint16_t xmodem_calc_crc(uint8_t *data, uint16_t length);
static xmodem_status xmodem_handle_packet(uint8_t size);
static xmodem_status xmodem_error_handler(uint8_t *error_number, uint8_t max_error_number);

/**
 * @brief   This function is the base of the Xmodem protocol.
 *          When we receive a header from UART, it decides what action it shall take.
 * @param   void
 * @return  void
 */
void xmodem_receive(void)
{
  volatile xmodem_status status = X_OK;
  uint8_t error_number = 0u;

  x_first_packet_received = false;
  xmodem_packet_number = 1u;
  xmodem_actual_flash_address = FLASH_APP_START_ADDRESS;
  xmodem_bytes_written = 0u;

  /* Loop until there isn't any error (or until we jump to the user application). */
  while (X_OK == status)
  {
    uint8_t header = 0x00u;

    /* Get the header from UART. */
    uart_status comm_status = uart_receive(&header, 1u);

    /* Spam the host (until we receive something) with ACSII "C", to notify it, we want to use CRC-16. */
    if ((UART_OK != comm_status) && (false == x_first_packet_received))
    {
      (void)uart_transmit_ch(X_C);
    }
    /* Uart timeout or any other errors. */
    else if ((UART_OK != comm_status) && (true == x_first_packet_received))
    {
      status = xmodem_error_handler(&error_number, X_MAX_ERRORS);
    }
    else
    {
      /* Do nothing. */
    }

    /* The header can be: SOH, STX, EOT and CAN. */
    switch(header)
    {
      xmodem_status packet_status = X_ERROR;
      /* 128 or 1024 bytes of data. */
      case X_SOH:
      case X_STX:
        /* If the handling was successful, then send an ACK. */
        packet_status = xmodem_handle_packet(header);
        if (X_OK == packet_status)
        {
          (void)uart_transmit_ch(X_ACK);
        }
        /* If the error was flash related, then immediately set the error counter to max (graceful abort). */
        else if (X_ERROR_FLASH == packet_status)
        {
          error_number = X_MAX_ERRORS;
          status = xmodem_error_handler(&error_number, X_MAX_ERRORS);
        }
        /* Error while processing the packet, either send a NAK or do graceful abort. */
        else
        {
          status = xmodem_error_handler(&error_number, X_MAX_ERRORS);
        }
        break;
      /* End of Transmission. */
      case X_EOT:
        (void)uart_transmit_ch(X_ACK);
        (void)uart_transmit_str((uint8_t*)"\n\rFirmware updated!\n\r");

        // HAL CRC ile hesaplama
        uint8_t *fw_data = (uint8_t*)FLASH_APP_START_ADDRESS;
        size_t total_len = xmodem_bytes_written;

        // Total length bilgisini yazdır
        char len_msg[64];
        snprintf(len_msg, sizeof(len_msg), "Total bytes: %lu\n\r", (unsigned long)total_len);
        uart_transmit_str((uint8_t*)len_msg);

        // Python uyumlu CRC-32 hesaplaması (IEEE 802.3)
        uint32_t crc32 = 0xFFFFFFFF;
        
        for (size_t i = 0; i < total_len; i++) {
            crc32 ^= fw_data[i];
            for (int j = 0; j < 8; j++) {
                if (crc32 & 1) {
                    crc32 = (crc32 >> 1) ^ 0xEDB88320; // Reflected polynomial
                } else {
                    crc32 >>= 1;
                }
            }
        }
        
        crc32 ^= 0xFFFFFFFF; // Final XOR (complement)

        char msg[64];
        snprintf(msg, sizeof(msg), "HAL CRC32: 0x%08lX\n\r", crc32);
        uart_transmit_str((uint8_t*)msg);

        status = X_DONE;
        break;
      /* Abort from host. */
      case X_CAN:
        status = X_ERROR;
        break;
      default:
        /* Wrong header. */
        if (UART_OK == comm_status)
        {
          status = xmodem_error_handler(&error_number, X_MAX_ERRORS);
        }
        break;
    }
  }
}



/**
 * @brief   Calculates the CRC-16 for the input package.
 * @param   *data:  Array of the data which we want to calculate.
 * @param   length: Size of the data, either 128 or 1024 bytes.
 * @return  status: The calculated CRC.
 */
static uint16_t xmodem_calc_crc(uint8_t *data, uint16_t length)
{
    uint16_t crc = 0u;
    while (length)
    {
        length--;
        crc = crc ^ ((uint16_t)*data++ << 8u);
        for (uint8_t i = 0u; i < 8u; i++)
        {
            if (crc & 0x8000u)
            {
                crc = (crc << 1u) ^ 0x1021u;
            }
            else
            {
                crc = crc << 1u;
            }
        }
    }
    return crc;
}

/**
 * @brief   This function handles the data packet we get from the xmodem protocol.
 * @param   header: SOH or STX.
 * @return  status: Report about the packet.
 */
uint8_t received_packet_number[X_PACKET_NUMBER_SIZE];
volatile uint8_t received_packet_data[X_PACKET_1024_SIZE];
uint8_t received_packet_crc[X_PACKET_CRC_SIZE];
static xmodem_status xmodem_handle_packet(uint8_t header)
{
  xmodem_status status = X_OK;
  uint16_t size = 0u;

  /* 2 bytes for packet number, 1024 for data, 2 for CRC*/


  /* Get the size of the data. */
  if (X_SOH == header)
  {
    size = X_PACKET_128_SIZE;
  }
  else if (X_STX == header)
  {
    size = X_PACKET_1024_SIZE;
  }
  else
  {
    /* Wrong header type. This shoudn't be possible... */
    status |= X_ERROR;
  }

  uart_status comm_status = UART_OK;
  /* Get the packet number, data and CRC from UART. */
  comm_status |= uart_receive(&received_packet_number[0u], X_PACKET_NUMBER_SIZE);
  comm_status |= uart_receive(&received_packet_data[0u], size);
  comm_status |= uart_receive(&received_packet_crc[0u], X_PACKET_CRC_SIZE);
  /* Merge the two bytes of CRC. */
  uint16_t crc_received = ((uint16_t)received_packet_crc[X_PACKET_CRC_HIGH_INDEX] << 8u) | ((uint16_t)received_packet_crc[X_PACKET_CRC_LOW_INDEX]);
  /* We calculate it too. */
  uint16_t crc_calculated = xmodem_calc_crc(&received_packet_data[0u], size);

  /* Communication error. */
  if (UART_OK != comm_status)
  {
    status |= X_ERROR_UART;
  }

  /* If it is the first packet, then erase the memory. */
  if ((X_OK == status) && (false == x_first_packet_received))
  {
    if (FLASH_OK == flash_erase(FLASH_APP_START_ADDRESS))
    {
      x_first_packet_received = true;
    }
    else
    {
      status |= X_ERROR_FLASH;
    }
  }

  /* Error handling and flashing. */
  if (X_OK == status)
  {
    if (xmodem_packet_number != received_packet_number[0u])
    {
      /* Packet number counter mismatch. */
      status |= X_ERROR_NUMBER;
    }
    if (255u != (received_packet_number[X_PACKET_NUMBER_INDEX] + received_packet_number[X_PACKET_NUMBER_COMPLEMENT_INDEX]))
    {
      /* The sum of the packet number and packet number complement aren't 255. */
      /* The sum always has to be 255. */
      status |= X_ERROR_NUMBER;
    }
    if (crc_calculated != crc_received)
    {
      /* The calculated and received CRC are different. */
      status |= X_ERROR_CRC;
    }
  }


  /* Check if we need to erase the next sector before writing */
  if (X_OK == status)
  {
    /* Check if we're crossing a 4KB sector boundary */
    uint32_t current_sector = (xmodem_actual_flash_address - FLASH_APP_START_ADDRESS) / FLASH_SECTOR_SIZE;
    uint32_t next_sector = (xmodem_actual_flash_address + size - FLASH_APP_START_ADDRESS) / FLASH_SECTOR_SIZE;
    
    /* If we're writing to a new sector, erase it first */
    if (current_sector != next_sector)
    {
      uint32_t sector_start_address = FLASH_APP_START_ADDRESS + (next_sector * FLASH_SECTOR_SIZE);
      if (FLASH_OK != flash_erase(sector_start_address))
      {
        status |= X_ERROR_FLASH;
      }
    }
  }

  /* Write the data to flash */
  if ((X_OK == status) && (FLASH_OK != flash_write(xmodem_actual_flash_address, (uint32_t*)&received_packet_data[0u], (uint32_t)size/4u)))
  {
    status |= X_ERROR_FLASH;
  }

  /* Raise the packet number and the address counters (if there weren't any errors). */
  if (X_OK == status)
  {
    xmodem_packet_number++;
    xmodem_actual_flash_address += size;
    xmodem_bytes_written += size;
  }

  return status;
}

/**
 * @brief   Handles the xmodem error.
 *          Raises the error counter, then if the number of the errors reached critical, do a graceful abort, otherwise send a NAK.
 * @param   *error_number:    Number of current errors (passed as a pointer).
 * @param   max_error_number: Maximal allowed number of errors.
 * @return  status: X_ERROR in case of too many errors, X_OK otherwise.
 */
static xmodem_status xmodem_error_handler(uint8_t *error_number, uint8_t max_error_number)
{
  xmodem_status status = X_OK;
  /* Raise the error counter. */
  (*error_number)++;
  /* If the counter reached the max value, then abort. */
  if ((*error_number) >= max_error_number)
  {
    /* Graceful abort. */
    (void)uart_transmit_ch(X_CAN);
    (void)uart_transmit_ch(X_CAN);
    status = X_ERROR;
  }
  /* Otherwise send a NAK for a repeat. */
  else
  {
    (void)uart_transmit_ch(X_NAK);
    status = X_OK;
  }
  return status;
}

