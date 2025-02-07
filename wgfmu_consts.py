#*---------------------------------------------------------------------------*#
#* Constants used when interfacing with WGFMU                                *#
#*                                                                           *#
#* Do not modify the contents of this file.                                  *#
#*---------------------------------------------------------------------------*#


# API Return Value - Error Code
WGFMU_NO_ERROR                                    = 0
WGFMU_PARAMETER_OUT_OF_RANGE_ERROR                = -1
WGFMU_ILLEGAL_STRING_ERROR                        = -2
WGFMU_CONTEXT_ERROR                               = -3
WGFMU_FUNCTION_NOT_SUPPORTED_ERROR                = -4
WGFMU_COMMUNICATION_ERROR                         = -5
WGFMU_FW_ERROR                                    = -6
WGFMU_LIBRARY_ERROR                               = -7
WGFMU_ERROR                                       = -8
WGFMU_CHANNEL_NOT_FOUND_ERROR                     = -9
WGFMU_PATTERN_NOT_FOUND_ERROR                     = -10
WGFMU_EVENT_NOT_FOUND_ERROR                       = -11
WGFMU_PATTERN_ALREADY_EXISTS_ERROR                = -12
WGFMU_SEQUENCER_NOT_RUNNING_ERROR                 = -13
WGFMU_RESULT_NOT_READY_ERROR                      = -14
WGFMU_RESULT_OUT_OF_DATE                          = -15

WGFMU_ERROR_CODE_MIN                              = -9999

# WGFMU_doSelfCaliration, WGFMU_doSelfTest
WGFMU_PASS = 0
WGFMU_FAIL = 1

# WGFMU_treatWarningsAsErrors, WGFMU_setWarningLevel
WGFMU_WARNING_LEVEL_OFFSET                        = 1000
WGFMU_WARNING_LEVEL_OFF                           = WGFMU_WARNING_LEVEL_OFFSET + 0
WGFMU_WARNING_LEVEL_SEVERE                        = WGFMU_WARNING_LEVEL_OFFSET + 1
WGFMU_WARNING_LEVEL_NORMAL                        = WGFMU_WARNING_LEVEL_OFFSET + 2
WGFMU_WARNING_LEVEL_INFORMATION                   = WGFMU_WARNING_LEVEL_OFFSET + 3

# WGFMU_setOperationMode
WGFMU_OPERATION_MODE_OFFSET                       = 2000
WGFMU_OPERATION_MODE_DC                           = WGFMU_OPERATION_MODE_OFFSET + 0
WGFMU_OPERATION_MODE_FASTIV                       = WGFMU_OPERATION_MODE_OFFSET + 1
WGFMU_OPERATION_MODE_PG                           = WGFMU_OPERATION_MODE_OFFSET + 2
WGFMU_OPERATION_MODE_SMU                          = WGFMU_OPERATION_MODE_OFFSET + 3

# WGFMU_setForceVoltageRange
WGFMU_FORCE_VOLTAGE_RANGE_OFFSET                  = 3000
WGFMU_FORCE_VOLTAGE_RANGE_AUTO                    = WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 0
WGFMU_FORCE_VOLTAGE_RANGE_3V                      = WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 1
WGFMU_FORCE_VOLTAGE_RANGE_5V                      = WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 2
WGFMU_FORCE_VOLTAGE_RANGE_10V_NEGATIVE            = WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 3
WGFMU_FORCE_VOLTAGE_RANGE_10V_POSITIVE            = WGFMU_FORCE_VOLTAGE_RANGE_OFFSET + 4

# WGFMU_setMeasureMode
WGFMU_MEASURE_MODE_OFFSET                         = 4000
WGFMU_MEASURE_MODE_VOLTAGE                        = WGFMU_MEASURE_MODE_OFFSET + 0
WGFMU_MEASURE_MODE_CURRENT                        = WGFMU_MEASURE_MODE_OFFSET + 1

# WGFMU_setMeasureVoltageRange
WGFMU_MEASURE_VOLTAGE_RANGE_OFFSET                = 5000
WGFMU_MEASURE_VOLTAGE_RANGE_5V                    = WGFMU_MEASURE_VOLTAGE_RANGE_OFFSET + 1
WGFMU_MEASURE_VOLTAGE_RANGE_10V                   = WGFMU_MEASURE_VOLTAGE_RANGE_OFFSET + 2

# WGFMU_setMeasureCurrentRange
WGFMU_MEASURE_CURRENT_RANGE_OFFSET                = 6000
WGFMU_MEASURE_CURRENT_RANGE_1UA                   = WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 1
WGFMU_MEASURE_CURRENT_RANGE_10UA                  = WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 2
WGFMU_MEASURE_CURRENT_RANGE_100UA                 = WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 3
WGFMU_MEASURE_CURRENT_RANGE_1MA                   = WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 4
WGFMU_MEASURE_CURRENT_RANGE_10MA                  = WGFMU_MEASURE_CURRENT_RANGE_OFFSET + 5

# WGFMU_setMeasureEnabled
WGFMU_MEASURE_ENABLED_OFFSET                      = 7000
WGFMU_MEASURE_ENABLED_DISABLE                     = WGFMU_MEASURE_ENABLED_OFFSET + 0
WGFMU_MEASURE_ENABLED_ENABLE                      = WGFMU_MEASURE_ENABLED_OFFSET + 1

# WGFMU_setTriggerOutMode
WGFMU_TRIGGER_OUT_MODE_OFFSET                     = 8000
WGFMU_TRIGGER_OUT_MODE_DISABLE                    = WGFMU_TRIGGER_OUT_MODE_OFFSET + 0
WGFMU_TRIGGER_OUT_MODE_START_EXECUTION            = WGFMU_TRIGGER_OUT_MODE_OFFSET + 1
WGFMU_TRIGGER_OUT_MODE_START_SEQUENCE             = WGFMU_TRIGGER_OUT_MODE_OFFSET + 2
WGFMU_TRIGGER_OUT_MODE_START_PATTERN              = WGFMU_TRIGGER_OUT_MODE_OFFSET + 3
WGFMU_TRIGGER_OUT_MODE_EVENT                      = WGFMU_TRIGGER_OUT_MODE_OFFSET + 4

WGFMU_TRIGGER_OUT_POLARITY_OFFSET                 = 8100
WGFMU_TRIGGER_OUT_POLARITY_POSITIVE               = WGFMU_TRIGGER_OUT_POLARITY_OFFSET+ 0
WGFMU_TRIGGER_OUT_POLARITY_NEGATIVE               = WGFMU_TRIGGER_OUT_POLARITY_OFFSET+ 1

# WGFMU_createMergedPattern
WGFMU_AXIS_OFFSET                                 = 9000
WGFMU_AXIS_TIME                                   = WGFMU_AXIS_OFFSET + 0
WGFMU_AXIS_VOLTAGE                                = WGFMU_AXIS_OFFSET + 1

# WGFMU_getStatus, WGFMU_getChannelStatus
WGFMU_STATUS_OFFSET                               = 10000
WGFMU_STATUS_COMPLETED                            = WGFMU_STATUS_OFFSET + 0
WGFMU_STATUS_DONE                                 = WGFMU_STATUS_OFFSET + 1
WGFMU_STATUS_RUNNING                              = WGFMU_STATUS_OFFSET + 2
WGFMU_STATUS_ABORT_COMPLETED                      = WGFMU_STATUS_OFFSET + 3
WGFMU_STATUS_ABORTED                              = WGFMU_STATUS_OFFSET + 4
WGFMU_STATUS_RUNNING_ILLEGAL                      = WGFMU_STATUS_OFFSET + 5
WGFMU_STATUS_IDLE                                 = WGFMU_STATUS_OFFSET + 6

# WGFMU_isMeasureEventCompleted
WGFMU_MEASURE_EVENT_OFFSET                        = 11000
WGFMU_MEASURE_EVENT_NOT_COMPLETED                 = WGFMU_MEASURE_EVENT_OFFSET + 0
WGFMU_MEASURE_EVENT_COMPLETED                     = WGFMU_MEASURE_EVENT_OFFSET + 1

# WGFMU_setMeasureEvent
WGFMU_MEASURE_EVENT_DATA_OFFSET                   = 12000
WGFMU_MEASURE_EVENT_DATA_AVERAGED                 = WGFMU_MEASURE_EVENT_DATA_OFFSET + 0
WGFMU_MEASURE_EVENT_DATA_RAW                      = WGFMU_MEASURE_EVENT_DATA_OFFSET + 1
