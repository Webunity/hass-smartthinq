import wideq
import logging

# General variables
REQUIREMENTS = ['wideq']
LOGGER = logging.getLogger(__name__)


# Device specific imports
import datetime
from .LGDevice import LGDevice
from wideq import dryer as wideq_dryer
from wideq.util import lookup_enum, lookup_reference

# Device specific dictionaries
# Where applicable extended with my model: https://eic.lgthinq.com:46030/api/webContents/modelJSON?modelName=RC90U2_WW&countryCode=WW&contentsId=JS0611052043415559&authKey=thinq
BIT_STATE = {
    'ON': 'On',
    'OFF': 'Off'
}

DRYER_STATE = {
    'POWER_OFF': 'Power Off',
    'INITIAL': 'Initial',
    'RUNNING': 'Running',
    'PAUSE': 'Paused',
    'COOLING': 'Cooling',
    'END': 'Complete',
    'ERROR': 'Error',
    'DRYING': 'Drying',
    'SMART_DIAGNOSIS': 'Smart diagnosis',
    'TEST1': 'Test 1',
    'TEST2': 'Test 2',
    'RESERVE': 'Reserve',
    'WRINKLE_CARE': 'Wrinkle care'
}

DRYER_ERROR = {
    'NOERROR': 'No error',
    'AE': 'Ae',
    'CE1': 'Ce1',
    'DE4': 'De4',
    'EMPTYWATER': 'Empty water',
    'DE': 'Door',
    'OE': 'Drainmotor',
    'F1': 'F1',
    'LE1': 'Le1',
    'LE2': 'Le2',
    'TE1': 'Te1',
    'TE2': 'Te2',
    'TE5': 'Te5',
    'TE6': 'Te6',
    'NOFILTER': 'No filter',
    'NP_GAS': 'Np',
    'PS': 'High power'
}

DRYER_IS_ON = {
    'YES': 'Yes',
    'NO': 'No'
}

DRYER_DRY_LEVEL = {
    'CUPBOARD': 'Cupboard',
    'DAMP': 'Damp',
    'EXTRA': 'Extra',
    'IRON': 'Iron',
    'LESS': 'Less',
    'MORE': 'More',
    'NORMAL': 'Normal',
    'VERY': 'Very'
}

DRYER_TEMPERATURE_CONTROL = {
    'OFF': 'Off',
    'ULTRA_LOW': 'Ultra low',
    'LOW': 'Low',
    'MEDIUM': 'Medium',
    'MID_HIGH': 'Mid high',
    'HIGH': 'High'
}

DRYER_TIME_DRY = {
    'OFF': 'Off',
    'TWENTY': '20',
    'THIRTY': '30',
    'FOURTY': '40',
    'FIFTY': '50',
    'SIXTY': '60'
}

DRYER_ECO_HYBRID = {
    'ECO': 'Eco',
    'NORMAL': 'Normal',
    'TURBO': 'Turbo'
}

DRYER_COURSE = {
    'COTTON_SOFT': 'Cotton Soft',
    'BULKY_ITEM': 'Bulky Item',
    'EASY_CARE': 'Easy Care',
    'COTTON': 'Cotton',
    'SPORTS_WEAR': 'Sportswear',
    'QUICK_DRY': 'Quick Dry',
    'WOOL': 'Wool',
    'RACK_DRY': 'Rack Dry',
    'COOL_AIR': 'Cool Air',
    'WARM_AIR': 'Warm Air',
    'BEDDING_BRUSH': 'Bedding Brush',
    'STERILIZATION': 'Sterilization',
    'REFRESH': 'Refresh',
    'POWER': 'Power',
    'NORMAL': 'Normal',
    'SPEED_DRY': 'Speed Dry',
    'HEAVY_DUTY': 'Heavy Duty',
    'TOWELS': 'Towels',
    'PERM_PRESS': 'Permenant Press',
    'DELICATES': 'Delicates',
    'BEDDING': 'Bedding',
    'AIR_DRY': 'Air Dry',
    'TIME_DRY': 'Time Dry',
    'ANTI_BACTERIAL': 'Anti Bacterial',
    'STEAM_FRESH': 'Steam Fresh',
    'STEAM_SANITARY': 'Steam Sanitary'
}

DRYER_SMART_COURSE = {
    'BABY_WEAR': 'Baby wear',
    'GYM_CLOTHES': 'Gym clothes',
    'BLANKET': 'Blanket',
    'BLANKET_REFRESH': 'Blanket refresh',
    'RAINY_SEASON': 'Rainy season',
    'SINGLE_GARMENTS': 'Single garments',
    'DEODORIZATION': 'Deodorization',
    'SMALL_LOAD': 'Small load',
    'LINGERIE': 'Lingerie',
    'EASY_IRON': 'Easy iron',
    'SUPER_DRY': 'Super dry',
    'ECONOMIC_DRY': 'Economic dry',
    'BIG_SIZE_ITEM': 'Big size item',
    'MINIMIZE_WRINKLES': 'Minimize wrinkles',
    'SHOES_FABRIC_DOLL': 'Shoes/Fabric Doll',
    'FULL_SIZE_LOAD': 'Full size load',
    'JEANS': 'Jeans'
}

DRYER_PROCESS_STATE = {
    'DETECTING': 'Detecting',
    'STEAM': 'Steam',
    'DRY': 'Dry',
    'COOLING': 'Cooling',
    'ANTI_CREASE': 'Anti-crease',
    'END': 'End',
    'OFF': 'Off'
}

class LGDryerDevice(LGDevice):
    def __init__(self, client, max_retries, device):
        """Initialize an LG Dryer Device."""

        # Call LGDevice constructor
        super().__init__(client, max_retries, device, wideq_dryer.DryerDevice)

        # Overwrite variables
        self._name = "lg_dryer_" + device.id

    def bit_state(self, key, index):
        """Get a state of a bit (ON/OFF) or N/A if not there."""

        key = 'N/A'
        if self._status:
            bit_value = int(self._status.data[key])
            bit_index = 2 ** index
            mode = bin(bit_value & bit_index)
            if mode == bin(0):
                key = 'OFF'
            else:
                key = 'ON'

        # Lookup the readable state representation, but if it fails, return the dryer returned value instead.
        try:
            return BIT_STATE[key]
        except KeyError:
            return key

    def lookup_enum(self, key):
        """Returns the found enum value for this key."""
        
        enum_name = ''
        enum = lookup_enum(key, self._status.data, self._device)
        if (enum):
            enum_name = enum.name;
        return enum_name

    @property
    def state_attributes(self):
        """Returns the state of the dryer for HomeAssistant representation."""

        data = {}
        data['is_on'] = self.is_on
        data['state'] = self.state
        data['error'] = self.error
        data['remaining_time'] = self.remaining_time
        data['remaining_time_in_minutes'] = self.remaining_time_in_minutes
        data['initial_time'] = self.initial_time
        data['initial_time_in_minutes'] = self.initial_time_in_minutes
        data['dry_level'] = self.dry_level
        return data

    @property
    def is_on(self):
        """Returns if the dryer is currently on"""

        key = 'NO'
        if (self._status and self._status.is_on):
            key = 'YES'
        return DRYER_IS_ON[key]

    @property
    def state(self):
        """Returns the current (translated) state of the dryer, taken from the 'DRYER_STATE' enum"""

        key = 'N/A'
        if self._status:
            enum = self.lookup_enum('State')
            if enum.startswith('@WM_STATE_'):
                key = enum[10:-2]

        # If we have a '-' state, it is off
        if key == '-':
            key = 'POWER_OFF'

        # Lookup the readable state representation, but if it fails, return the dryer returned value instead.
        try:
            return DRYER_STATE[key]
        except KeyError:
            return key

    @property
    def error(self):
        """Returns the current (translated) error of the dryer, taken from the 'DRYER_ERROR' enum"""

        key = 'N/A'
        if self._status:
            enum = self.lookup_enum('Error')
            if enum.startswith('ERROR_NOERROR'):
                key = 'NOERROR'
            if enum.startswith('@WM_US_DRYER_ERROR_'):
                key = enum[19:-2]
            if enum.startswith('@WM_WW_FL_ERROR_'):
                key = enum[16:-2]

        # If we have a '-' state, there is no error.
        if key == '-':
            key = 'NOERROR'

        # Lookup the readable state representation, but if it fails, return the dryer returned value instead.
        try:
            return DRYER_ERROR[key]
        except KeyError:
            return key

    @property
    def remaining_time(self):
        """Returns the current remaining time of the dryer or N/A if the dryer is not on."""

        minutes = 'N/A'
        if (self._status and self._status.is_on):
            minutes = self.remaining_time_in_minutes
            minutes = str(datetime.timedelta(minutes=minutes))[:-3]

        return minutes

    @property
    def remaining_time_in_minutes(self):
        """Returns the current remaining time of the dryer or N/A if the dryer is not on."""

        minutes = 'N/A'
        if (self._status and self._status.is_on):
            minutes = self._status.remaining_time

            # The API (indefinitely) returns 1 minute remaining when a cycle is
            # either in state off or complete, or process night-drying. Return 0
            # minutes remaining in these instances, which is more reflective of
            # reality.
            if (self._status.state == wideq_dryer.DryerState.END or
                self._status.state == wideq_dryer.DryerState.COMPLETE):
                minutes = 0

        return minutes

    @property
    def initial_time(self):
        """Returns the initial time of the dryer or N/A if the dryer is not on."""

        minutes = 'N/A'
        if (self._status and self._status.is_on):
            minutes = self.initial_time_in_minutes
            minutes = str(datetime.timedelta(minutes=minutes))[:-3]

        return minutes

    @property
    def initial_time_in_minutes(self):
        """Returns the initial time in minutes of the dryer or N/A if the dryer is not on."""

        minutes = 'N/A'
        if (self._status and self._status.is_on):
            minutes = self._status.initial_time

            # When in state OFF, the dishwasher still returns the initial program
            # length of the previously ran cycle. Instead, return 0 which is more
            # reflective of the dishwasher being off.
            if (self._status.state == wideq_dryer.DryerState.OFF):
                minutes = 0

        return minutes

    @property
    def dry_level(self):
        key = 'N/A'
        if (self._status and self._status.is_on):
            enum = self.lookup_enum('DryLevel')
            if (enum.startswith('@WM_DRY24_DRY_LEVEL_') or
                enum.startswith('@WM_DRY27_DRY_LEVEL_')):
                key = enum[20:-2]

        try:
            return DRYER_DRY_LEVEL[key]
        except KeyError:
            return key

