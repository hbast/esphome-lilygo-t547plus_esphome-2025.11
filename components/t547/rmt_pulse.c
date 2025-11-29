
/******************************************************************************/
/***        include files                                                   ***/
/******************************************************************************/

#include "rmt_pulse.h"
#include <esp_idf_version.h>

#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
#include <driver/rmt_tx.h>
#include <driver/rmt_encoder.h>
#else
#include <driver/rmt.h>
#endif

#include <esp_check.h>
#include <string.h>

/******************************************************************************/
/***        macro definitions                                               ***/
/******************************************************************************/

/******************************************************************************/
/***        type definitions                                                ***/
/******************************************************************************/

/******************************************************************************/
/***        local function prototypes                                       ***/
/******************************************************************************/

/**
 * @brief Remote peripheral interrupt. Used to signal when transmission is done.
 */
// static void IRAM_ATTR rmt_interrupt_handler(void *arg);

/******************************************************************************/
/***        exported variables                                              ***/
/******************************************************************************/

/******************************************************************************/
/***        local variables                                                 ***/
/******************************************************************************/

#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
/**
 * @brief RMT channel handle
 */
static rmt_channel_handle_t rmt_chan = NULL;

/**
 * @brief RMT transmit configuration
 */
static rmt_transmit_config_t rmt_tx_config = {
    .loop_count = 0,
    .flags.eot_level = 0,
};

/**
 * @brief RMT encoder handle
 */
static rmt_encoder_handle_t rmt_encoder = NULL;
#endif

/******************************************************************************/
/***        exported functions                                              ***/
/******************************************************************************/

void rmt_pulse_init(gpio_num_t pin)
{
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    rmt_tx_channel_config_t tx_chan_config = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .gpio_num = pin,
        .mem_block_symbols = 64,
        .resolution_hz = 10000000, // 10MHz, 0.1us resolution
        .trans_queue_depth = 4,
        .flags.invert_out = false,
        .flags.with_dma = false,
    };
    
    ESP_ERROR_CHECK(rmt_new_tx_channel(&tx_chan_config, &rmt_chan));
    ESP_ERROR_CHECK(rmt_enable(rmt_chan));
    
    // Create copy encoder for simple symbol transmission
    rmt_copy_encoder_config_t copy_encoder_config = {};
    ESP_ERROR_CHECK(rmt_new_copy_encoder(&copy_encoder_config, &rmt_encoder));
#else
    rmt_config_t config = RMT_DEFAULT_CONFIG_TX(pin, RMT_CHANNEL_0);
    config.clk_div = 8; // 80MHz / 8 = 10MHz
    
    ESP_ERROR_CHECK(rmt_config(&config));
    ESP_ERROR_CHECK(rmt_driver_install(config.channel, 0, 0));
#endif
}


void IRAM_ATTR pulse_ckv_ticks(uint16_t high_time_ticks,
                               uint16_t low_time_ticks, bool wait)
{
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    rmt_symbol_word_t rmt_symbol;
    
    if (high_time_ticks > 0)
    {
        rmt_symbol.level0 = 1;
        rmt_symbol.duration0 = high_time_ticks;
        rmt_symbol.level1 = 0;
        rmt_symbol.duration1 = low_time_ticks;
    }
    else
    {
        rmt_symbol.level0 = 1;
        rmt_symbol.duration0 = low_time_ticks;
        rmt_symbol.level1 = 0;
        rmt_symbol.duration1 = 0;
    }
    
    rmt_transmit_config_t tx_config = {
        .loop_count = 0,
    };
    
    ESP_ERROR_CHECK(rmt_transmit(rmt_chan, rmt_encoder, &rmt_symbol, 1, &tx_config));
    if (wait) {
        ESP_ERROR_CHECK(rmt_tx_wait_all_done(rmt_chan, -1));
    }
#else
    rmt_item32_t item;
    if (high_time_ticks > 0) {
        item = (rmt_item32_t){{{high_time_ticks, 1, low_time_ticks, 0}}};
    } else {
        item = (rmt_item32_t){{{low_time_ticks, 1, 0, 0}}};
    }
    
    ESP_ERROR_CHECK(rmt_write_items(RMT_CHANNEL_0, &item, 1, wait));
#endif
}

void pulse_ckv_us(uint16_t high_time_us, uint16_t low_time_us, bool wait)
{
    pulse_ckv_ticks(high_time_us * 10, low_time_us * 10, wait);
}


// bool IRAM_ATTR rmt_busy()
// {
//     return !rmt_tx_done;
// }

/******************************************************************************/
/***        local functions                                                 ***/
/******************************************************************************/

// static void IRAM_ATTR rmt_interrupt_handler(void *arg)
// {
//     rmt_tx_done = true;
//     RMT.int_clr.val = RMT.int_st.val;
// }

/******************************************************************************/
/***        END OF FILE                                                     ***/
/******************************************************************************/