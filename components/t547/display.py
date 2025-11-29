import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import display
from esphome.core import CORE
from esphome.const import (
    CONF_ID,
    CONF_LAMBDA,
    CONF_PAGES,
)
from esphome.const import __version__ as ESPHOME_VERSION

DEPENDENCIES = ["esp32"]

CONF_GREYSCALE = "greyscale"


t547_ns = cg.esphome_ns.namespace("t547")
T547 = t547_ns.class_(
    "T547", cg.PollingComponent, display.DisplayBuffer
)
ed047tc1_config_t = cg.global_ns.struct("ed047tc1_config_t")

CONFIG_SCHEMA = cv.All(
    display.FULL_DISPLAY_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(T547),
            cv.Optional(CONF_GREYSCALE, default=False): cv.boolean,
        }
    )
    .extend(cv.polling_component_schema("5s")),
    cv.has_at_most_one_key(CONF_PAGES, CONF_LAMBDA),
    cv.only_with_arduino,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])

    if cv.Version.parse(ESPHOME_VERSION) < cv.Version.parse("2023.12.0"):
        await cg.register_component(var, config)
    await display.register_display(var, config)

    if CONF_LAMBDA in config:
        lambda_ = await cg.process_lambda(
            config[CONF_LAMBDA], [(display.DisplayRef, "it")], return_type=cg.void
        )
        cg.add(var.set_writer(lambda_))

    cg.add(var.set_greyscale(config[CONF_GREYSCALE]))

    cg.add_library("Wire", None)

    # Detect board variant and inject pins/flags
    variant = CORE.data["esp32"]["variant"]
    
    if variant == "esp32s3":
        # ESP32-S3 (T5-4.7 Plus)
        pins_config = {
            "cfg_data": 13, "cfg_clk": 12, "cfg_str": 0,
            "ckv": 38, "sth": 40, "ckh": 41,
            "d7": 7, "d6": 6, "d5": 5, "d4": 4,
            "d3": 3, "d2": 2, "d1": 1, "d0": 8
        }
        
        # Inject PlatformIO options for ESP32-S3 T5-4.7 Plus
        cg.add_build_flag("-DBOARD_HAS_PSRAM")
        cg.add_build_flag("-DARDUINO_USB_CDC_ON_BOOT=1")
        cg.add_build_flag("-mfix-esp32-psram-cache-issue")

        cg.add_platformio_option("board_build.arduino.memory_type", "qspi_opi")
        cg.add_platformio_option("board_build.flash_mode", "qio")
        cg.add_platformio_option("board_build.psram_type", "opi")
        cg.add_platformio_option("board_build.memory_type", "qspi_opi")
        cg.add_platformio_option("board_build.boot_freq", "80m")
        
    else:
        # ESP32 (Standard T5-4.7)
        pins_config = {
            "cfg_data": 23, "cfg_clk": 18, "cfg_str": 0,
            "ckv": 25, "sth": 26, "ckh": 5,
            "d7": 22, "d6": 21, "d5": 27, "d4": 2,
            "d3": 19, "d2": 4, "d1": 32, "d0": 33
        }
        # Standard ESP32 might need PSRAM flag too, but usually it's standard
        cg.add_build_flag("-DBOARD_HAS_PSRAM")

    # Initialize the configuration struct with pin assignments.
    # Explicit casting to gpio_num_t ensures type safety across different IDF versions.
    config_struct = cg.StructInitializer(
        ed047tc1_config_t,
        ("cfg_data", cg.RawExpression(f"(gpio_num_t){pins_config['cfg_data']}")),
        ("cfg_clk", cg.RawExpression(f"(gpio_num_t){pins_config['cfg_clk']}")),
        ("cfg_str", cg.RawExpression(f"(gpio_num_t){pins_config['cfg_str']}")),
        ("ckv", cg.RawExpression(f"(gpio_num_t){pins_config['ckv']}")),
        ("sth", cg.RawExpression(f"(gpio_num_t){pins_config['sth']}")),
        ("ckh", cg.RawExpression(f"(gpio_num_t){pins_config['ckh']}")),
        ("d7", cg.RawExpression(f"(gpio_num_t){pins_config['d7']}")),
        ("d6", cg.RawExpression(f"(gpio_num_t){pins_config['d6']}")),
        ("d5", cg.RawExpression(f"(gpio_num_t){pins_config['d5']}")),
        ("d4", cg.RawExpression(f"(gpio_num_t){pins_config['d4']}")),
        ("d3", cg.RawExpression(f"(gpio_num_t){pins_config['d3']}")),
        ("d2", cg.RawExpression(f"(gpio_num_t){pins_config['d2']}")),
        ("d1", cg.RawExpression(f"(gpio_num_t){pins_config['d1']}")),
        ("d0", cg.RawExpression(f"(gpio_num_t){pins_config['d0']}")),
    )
    
    cg.add(var.set_pin_config(config_struct))
