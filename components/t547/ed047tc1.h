#ifndef _ED047TC1_H_
#define _ED047TC1_H_

#ifdef __cplusplus
extern "C" {
#endif

/******************************************************************************/
/***        include files                                                   ***/
/******************************************************************************/

#include <driver/gpio.h>

#include <stdint.h>

/******************************************************************************/
/***        macro definitions                                               ***/
/******************************************************************************/

/******************************************************************************/
/***        type definitions                                                ***/
/******************************************************************************/

typedef struct {
    gpio_num_t cfg_data;
    gpio_num_t cfg_clk;
    gpio_num_t cfg_str;
    gpio_num_t ckv;
    gpio_num_t sth;
    gpio_num_t ckh;
    gpio_num_t d7;
    gpio_num_t d6;
    gpio_num_t d5;
    gpio_num_t d4;
    gpio_num_t d3;
    gpio_num_t d2;
    gpio_num_t d1;
    gpio_num_t d0;
} ed047tc1_config_t;

/******************************************************************************/
/***        exported variables                                              ***/
/******************************************************************************/

/******************************************************************************/
/***        exported functions                                              ***/
/******************************************************************************/

void epd_base_init(uint32_t epd_row_width, const ed047tc1_config_t *config);
void epd_poweron();
void epd_poweroff();

/**
 * @brief Start a draw cycle.
 */
void epd_start_frame();

/**
 * @brief End a draw cycle.
 */
void epd_end_frame();

/**
 * @brief output row data
 *
 * @note Waits until all previously submitted data has been written.
 *       Then, the following operations are initiated:
 *
 *           1. Previously submitted data is latched to the output register.
 *           2. The RMT peripheral is set up to pulse the vertical (gate) driver
 *              for `output_time_dus` / 10 microseconds.
 *           3. The I2S peripheral starts transmission of the current buffer to
 *              the source driver.
 *           4. The line buffers are switched.
 *
 *       This sequence of operations allows for pipelining data preparation and
 *       transfer, reducing total refresh times.
 */
void  epd_output_row(uint32_t output_time_dus);

/**
 * @brief Skip a row without writing to it.
 */
void  epd_skip();

/**
 * @brief Get the currently writable line buffer.
 */
uint8_t *  epd_get_current_buffer();

/**
 * @brief Switches front and back line buffer.
 *
 * @note If the switched-to line buffer is currently in use, this function
 *       blocks until transmission is done.
 */
void  epd_switch_buffer();

#ifdef __cplusplus
}
#endif

#endif
/******************************************************************************/
/***        END OF FILE                                                     ***/
/******************************************************************************/