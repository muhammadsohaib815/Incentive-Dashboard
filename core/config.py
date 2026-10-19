"""
Criteria Configurations for Incentive Website
Contains all criteria definitions for DO, TOUCH, OVERLAPPING, BLISS, TE, ASM, and RSM teams.
"""

# =====================================================================
# SPO (SENIOR POSITION OFFICER / FIELD FORCE) QUALIFYING CRITERIA
# =====================================================================

# DO Team SPOs (5 Criteria, 4 Qualifying Slabs)
CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'do_category',
        'name': 'DO Category Bottom-Line Net Value',
        'short_name': 'DO Category Net Value',
        'groups': ['DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S'],
        'prd_prefix': ['DO'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True
    },
    {
        'id': 2,
        'key': 'do_ultra_thin',
        'name': 'DO Silk Ultra-Thin Units',
        'short_name': 'DO Silk Ultra-Thin',
        'groups': ['DO ULTRA THIN 3S'],
        'prd_prefix': ['DO'],
        'metric': 'E_QTY',
        'target_type': 'unit',
        'is_currency': False
    },
    {
        'id': 3,
        'key': 'sathi_6s',
        'name': 'Sathi 6S Bottom-Line Net Value',
        'short_name': 'Sathi 6S Net Value',
        'groups': ['SATHI 6S'],
        'prd_prefix': ['SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True
    },
    {
        'id': 4,
        'key': 'sathi_performance',
        'name': 'Sathi Performance Category Bottom-Line Net Value',
        'short_name': 'Sathi Performance Net Value',
        'groups': ['SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI DANEDAR 4S', 'SATHI MENTHOL 3S', 'SATHI 4S'],
        'prd_prefix': ['SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True
    },
    {
        'id': 5,
        'key': 'do_sathi_bottom_line',
        'name': 'Bottom-Line Net Value',
        'short_name': 'Bottom-Line Net Value',
        'groups': [
            'DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S',
            'SATHI 6S', 'SATHI MENTHOL 3S', 'SATHI DANEDAR 4S',
            'SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI 4S'
        ],
        'prd_prefix': ['DO', 'SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True
    }
]

# TOUCH Team SPOs (4 Criteria)
TOUCH_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'touch_delay_mix',
        'name': 'Touch Delay + Strawberry + Multi Mix Net Value',
        'short_name': 'Touch Delay Mix',
        'groups': ['TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S'],
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 10000,
        'slab_120': 12500,
        'req_name': 'Touch Delay + Strawberry + Multi Mix Incentive',
        'remark_name': 'Touch Delay, Strawberry & Multi Mix'
    },
    {
        'id': 2,
        'key': 'touch_classic_group',
        'name': 'Touch Dotted + Ribbed + Classic Net Value',
        'short_name': 'Touch Dotted Classic',
        'groups': ['TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S', 'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S'],
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 7500,
        'slab_120': 9500,
        'req_name': 'Touch Dotted + Ribbed + Classic Incentive',
        'remark_name': 'Touch Dotted, Ribbed & Classic'
    },
    {
        'id': 3,
        'key': 'one_brand',
        'name': 'ONE Brand Category Bottom-Line Net Value',
        'short_name': 'ONE Brand Net Value',
        'groups': ['ONE EXTENDED PLEASURE 3S', 'ONE MAXIMUM PLEASURE 3S', 'ONE SUPER STUDS 3S', 'ONE MIXED PLEASURE 3S'],
        'prd_prefix': ['ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 4500,
        'slab_120': 5500,
        'req_name': 'ONE Brand Incentive',
        'remark_name': 'ONE Brand Category'
    },
    {
        'id': 4,
        'key': 'touch_one_bottom_line',
        'name': 'Bottom-Line Net Value',
        'short_name': 'Bottom-Line Net Value',
        'groups': [
            'TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S',
            'TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S',
            'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S',
            'ONE EXTENDED PLEASURE 3S', 'ONE MAXIMUM PLEASURE 3S', 'ONE SUPER STUDS 3S', 'ONE MIXED PLEASURE 3S'
        ],
        'prd_prefix': ['TOUCH', 'ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 5000,
        'slab_120': 6500,
        'req_name': 'Bottom-Line Net Value Incentive',
        'remark_name': 'Bottom-Line Net Value'
    }
]

# OVERLAPPING SPOs (4 Criteria)
OVERLAPPING_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'do_sathi_perf_bottom_line',
        'name': 'DO Category + Sathi Performance Category Bottom-line Net Value',
        'short_name': 'DO + Sathi Perf Net Value',
        'groups': [
            'DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S', 'DO BUNDLE PACK',
            'SATHI 6S', 'SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI DANEDAR 4S', 'SATHI MENTHOL 3S', 'SATHI 4S'
        ],
        'prd_prefix': ['DO', 'SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True
    },
    {
        'id': 2,
        'key': 'overlapping_silk_ultra_thin',
        'name': 'DO Silk Ultra-Thin Units',
        'short_name': 'DO Silk Ultra-Thin',
        'groups': ['DO ULTRA THIN 3S'],
        'prd_prefix': ['DO'],
        'metric': 'E_QTY',
        'target_type': 'unit',
        'is_currency': False
    },
    {
        'id': 3,
        'key': 'touch_bottom_line',
        'name': 'Touch Category Bottom-Line Net Value',
        'short_name': 'Touch Bottom-Line',
        'groups': [
            'TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S',
            'TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S',
            'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S'
        ],
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 10000,
        'slab_120': 12500,
        'req_name': 'Touch Bottom-Line Incentive',
        'remark_name': 'Touch Category Bottom-Line'
    },
    {
        'id': 4,
        'key': 'overlapping_overall_bottom_line',
        'name': 'Overall Bottom-Line Net Value',
        'short_name': 'Overall Bottom-Line',
        'groups': [
            'DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S', 'DO BUNDLE PACK',
            'SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI DANEDAR 4S', 'SATHI MENTHOL 3S', 'SATHI 4S',
            'SATHI 6S',
            'TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S',
            'TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S',
            'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S',
            'ONE EXTENDED PLEASURE 3S', 'ONE MAXIMUM PLEASURE 3S', 'ONE SUPER STUDS 3S', 'ONE MIXED PLEASURE 3S'
        ],
        'prd_prefix': ['DO', 'SATHI', 'TOUCH', 'ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 5000,
        'slab_120': 6500,
        'req_name': 'Overall Bottom-Line Incentive',
        'remark_name': 'Overall Bottom-Line Net Value'
    }
]

# BLISS Team SPOs (1 Criterion)
BLISS_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'bliss_bottom_line',
        'name': 'Bottom-Line Net Value',
        'short_name': 'BLISS Bottom-Line Net Value',
        'groups': [
            'BLISS MAXI THICK L-9S',
            'BLISS MAXI THICK XL-8S',
            'BLISS ULTRA THIN L-8S',
            'BLISS ULTRA THIN XL-7S',
            'BLISS MAXI VALUE PACK 16S',
            'BLISS MAXI VALUE PACK 18S',
            'MAXI STRAIGHT PADS XL'
        ],
        'prd_prefix': ['BLISS', 'MAXI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 30000,
        'slab_120': 35000,
        'req_name': 'Bottom-Line Net Value Incentive',
        'remark_name': 'BLISS Bottom-Line Net Value'
    }
]

# =====================================================================
# ASM (AREA SALES MANAGER) QUALIFYING CRITERIA CONFIGURATIONS
# =====================================================================

# DO Team ASMs (5 Criteria)
ASM_DO_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'do_category',
        'name': 'Target vs Achievement of Do Category bottom-line Net Value',
        'short_name': 'DO Category Net Value',
        'groups': ['DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S'],
        'prd_prefix': ['DO'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True
    },
    {
        'id': 2,
        'key': 'do_ultra_thin',
        'name': 'Target vs Achievement of Do Silk Ultra-Thin Units',
        'short_name': 'DO Silk Ultra-Thin',
        'groups': ['DO ULTRA THIN 3S'],
        'prd_prefix': ['DO'],
        'metric': 'E_QTY',
        'target_type': 'unit',
        'is_currency': False
    },
    {
        'id': 3,
        'key': 'sathi_performance',
        'name': 'Target vs Achievement of Sathi Performance Category Bottom-line Net Value',
        'short_name': 'Sathi Performance Net Value',
        'groups': ['SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI DANEDAR 4S', 'SATHI MENTHOL 3S', 'SATHI 4S'],
        'prd_prefix': ['SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 12500,
        'slab_120': 14000,
        'req_name': 'SATHI Perf. Category Incentive',
        'remark_name': 'Sathi Performance Category'
    },
    {
        'id': 4,
        'key': 'sathi_6s',
        'name': 'Target vs Achievement of Sath Plain Bottom-line Net Value',
        'short_name': 'Sathi Plain Net Value',
        'groups': ['SATHI 6S'],
        'prd_prefix': ['SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 6500,
        'slab_120': 8000,
        'req_name': 'SATHI Plain Bottom-line Incentive',
        'remark_name': 'Sathi Plain Bottom-Line'
    },
    {
        'id': 5,
        'key': 'do_sathi_bottom_line',
        'name': 'Target vs Achievement of Bottom-Line Net Value',
        'short_name': 'Bottom-Line Net Value',
        'groups': [
            'DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S',
            'SATHI 6S', 'SATHI MENTHOL 3S', 'SATHI DANEDAR 4S',
            'SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI 4S'
        ],
        'prd_prefix': ['DO', 'SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 10000,
        'slab_120': 15000,
        'req_name': 'Bottom-Line Net Value Incentive',
        'remark_name': 'Bottom-Line Net Value'
    }
]

# TOUCH Team ASMs (4 Criteria)
ASM_TOUCH_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'touch_delay_mix',
        'name': 'Target vs Achievement of Touch Delay + Touch Strawberry + Touch Multi Mix Category bottom-line Net Value',
        'short_name': 'Touch Delay Mix',
        'groups': ['TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S'],
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 16000,
        'slab_120': 18000,
        'req_name': 'Touch Delay + Strawberry + Multi Mix Incentive',
        'remark_name': 'Touch Delay, Strawberry & Multi Mix'
    },
    {
        'id': 2,
        'key': 'touch_classic_group',
        'name': 'Target vs Achievement of Touch Dotted + Touch Ribbed + Touch Classic Category bottom-line Net Value',
        'short_name': 'Touch Dotted Classic',
        'groups': ['TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S', 'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S'],
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 14000,
        'slab_120': 15500,
        'req_name': 'Touch Dotted + Ribbed + Classic Incentive',
        'remark_name': 'Touch Dotted, Ribbed & Classic'
    },
    {
        'id': 3,
        'key': 'one_brand',
        'name': 'Target vs Achievement of ONE Category bottom-line Net Value',
        'short_name': 'ONE Brand Net Value',
        'groups': ['ONE EXTENDED PLEASURE 3S', 'ONE MAXIMUM PLEASURE 3S', 'ONE SUPER STUDS 3S', 'ONE MIXED PLEASURE 3S'],
        'prd_prefix': ['ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 5000,
        'slab_120': 6500,
        'req_name': 'ONE Category Incentive',
        'remark_name': 'ONE Category'
    },
    {
        'id': 4,
        'key': 'touch_one_bottom_line',
        'name': 'Target vs Achievement of Touch + ONE Bottom-Line Net Value',
        'short_name': 'Touch + ONE Bottom-Line',
        'groups': [
            'TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S',
            'TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S',
            'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S',
            'ONE EXTENDED PLEASURE 3S', 'ONE MAXIMUM PLEASURE 3S', 'ONE SUPER STUDS 3S', 'ONE MIXED PLEASURE 3S'
        ],
        'prd_prefix': ['TOUCH', 'ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 10000,
        'slab_120': 15000,
        'req_name': 'Touch + ONE Bottom-Line Incentive',
        'remark_name': 'Touch + ONE Bottom-Line'
    }
]

# Overlapping ASMs (7 Criteria)
ASM_OVERLAPPING_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'do_category',
        'name': 'Target vs Achievement of Do Category bottom-line Net Value',
        'short_name': 'DO Category Net Value',
        'groups': ['DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S'],
        'prd_prefix': ['DO'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True
    },
    {
        'id': 2,
        'key': 'do_ultra_thin',
        'name': 'Target vs Achievement of Do Silk Ultra-Thin Units',
        'short_name': 'DO Silk Ultra-Thin',
        'groups': ['DO ULTRA THIN 3S'],
        'prd_prefix': ['DO'],
        'metric': 'E_QTY',
        'target_type': 'unit',
        'is_currency': False
    },
    {
        'id': 3,
        'key': 'sathi_category',
        'name': 'Target vs Achievement of Sathi Category bottom-line Net Value',
        'short_name': 'Sathi Category Net Value',
        'groups': [
            'SATHI 6S', 'SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI DANEDAR 4S',
            'SATHI MENTHOL 3S', 'SATHI 4S'
        ],
        'prd_prefix': ['SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 9000,
        'slab_120': 10500,
        'req_name': 'Sathi Category Incentive',
        'remark_name': 'Sathi Category'
    },
    {
        'id': 4,
        'key': 'touch_delay_mix',
        'name': 'Target vs Achievement of Touch Delay + Touch Strawberry + Touch Multi Mix Category bottom-line Net Value',
        'short_name': 'Touch Delay Mix',
        'groups': ['TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S'],
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 7000,
        'slab_120': 9000,
        'req_name': 'Touch Delay + Strawberry + Multi Mix Incentive',
        'remark_name': 'Touch Delay, Strawberry & Multi Mix'
    },
    {
        'id': 5,
        'key': 'touch_classic_group',
        'name': 'Target vs Achievement of Touch Dotted + Touch Ribbed + Touch Classic Category bottom-line Net Value',
        'short_name': 'Touch Dotted Classic',
        'groups': ['TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S', 'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S'],
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 7000,
        'slab_120': 8500,
        'req_name': 'Touch Dotted + Ribbed + Classic Incentive',
        'remark_name': 'Touch Dotted, Ribbed & Classic'
    },
    {
        'id': 6,
        'key': 'one_brand',
        'name': 'Target vs Achievement of ONE Category bottom-line Net Value',
        'short_name': 'ONE Brand Net Value',
        'groups': ['ONE EXTENDED PLEASURE 3S', 'ONE MAXIMUM PLEASURE 3S', 'ONE SUPER STUDS 3S', 'ONE MIXED PLEASURE 3S'],
        'prd_prefix': ['ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 5000,
        'slab_120': 6500,
        'req_name': 'ONE Category Incentive',
        'remark_name': 'ONE Category'
    },
    {
        'id': 7,
        'key': 'bliss_overlap_bottom_line',
        'name': 'Target vs Achievement of BLISS Category bottom-line Net Value',
        'short_name': 'BLISS Bottom-Line Net Value',
        'groups': [
            'BLISS MAXI THICK L-9S',
            'BLISS MAXI THICK XL-8S',
            'BLISS ULTRA THIN L-8S',
            'BLISS ULTRA THIN XL-7S',
            'BLISS MAXI VALUE PACK 16S',
            'BLISS MAXI VALUE PACK 18S',
            'MAXI STRAIGHT PADS XL'
        ],
        'prd_prefix': ['BLISS', 'MAXI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 15000,
        'slab_120': 20000,
        'req_name': 'BLISS Category Incentive',
        'remark_name': 'BLISS Category Bottom-line'
    },
    {
        'id': 8,
        'key': 'overlapping_bottom_line',
        'name': 'Target vs Achievement of bottom-line Net Value targets',
        'short_name': 'Bottom-Line Net Value',
        'groups': [
            'DO 3s', 'DO 5s', 'DO EXTRA DELAY 3S', 'DO ULTRA THIN 3S', 'DO BUNDLE PACK',
            'SATHI PLUS 5S', 'SATHI PLUS 3S', 'SATHI DANEDAR 4S', 'SATHI MENTHOL 3S', 'SATHI 4S', 'SATHI 6S',
            'TOUCH DELAY 5S', 'TOUCH DELAY 3S', 'TOUCH STRAWBERRY 3S', 'TOUCH MULTI MIX 4S',
            'TOUCH DOTTED 5S', 'TOUCH DOTTED 3S', 'TOUCH RIBBED 5S', 'TOUCH RIBBED 3S',
            'TOUCH CLASSIC 5S', 'TOUCH CLASSIC 3S',
            'ONE EXTENDED PLEASURE 3S', 'ONE MAXIMUM PLEASURE 3S', 'ONE SUPER STUDS 3S', 'ONE MIXED PLEASURE 3S'
        ],
        'prd_prefix': ['DO', 'SATHI', 'TOUCH', 'ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 5000,
        'slab_120': 6500,
        'req_name': 'Bottom-Line Net Value Incentive',
        'remark_name': 'Bottom-Line Net Value targets'
    }
]

# Dedicated BLISS Team ASMs (1 Criterion: Rs. 40k / 50k)
ASM_BLISS_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'bliss_bottom_line',
        'name': 'Target vs Achievement of Bottom-Line Net Value',
        'short_name': 'BLISS Bottom-Line Net Value',
        'groups': [
            'BLISS MAXI THICK L-9S',
            'BLISS MAXI THICK XL-8S',
            'BLISS ULTRA THIN L-8S',
            'BLISS ULTRA THIN XL-7S',
            'BLISS MAXI VALUE PACK 16S',
            'BLISS MAXI VALUE PACK 18S',
            'MAXI STRAIGHT PADS XL'
        ],
        'prd_prefix': ['BLISS', 'MAXI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 40000,
        'slab_120': 50000,
        'req_name': 'Bottom-Line Net Value Incentive',
        'remark_name': 'BLISS Bottom-Line Net Value'
    }
]

# Overlap BLISS ASMs (1 Criterion: Rs. 15k / 20k)
ASM_OVERLAP_BLISS_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'bliss_bottom_line',
        'name': 'Target vs Achievement of Bottom-Line Net Value',
        'short_name': 'BLISS Bottom-Line Net Value',
        'groups': [
            'BLISS MAXI THICK L-9S',
            'BLISS MAXI THICK XL-8S',
            'BLISS ULTRA THIN L-8S',
            'BLISS ULTRA THIN XL-7S',
            'BLISS MAXI VALUE PACK 16S',
            'BLISS MAXI VALUE PACK 18S',
            'MAXI STRAIGHT PADS XL'
        ],
        'prd_prefix': ['BLISS', 'MAXI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 15000,
        'slab_120': 20000,
        'req_name': 'Bottom-Line Net Value Incentive',
        'remark_name': 'BLISS Bottom-Line Net Value'
    }
]

# =============================================================
# RSM (REGIONAL SALES MANAGER) QUALIFYING CRITERIA CONFIGURATIONS
# =============================================================
RSM_CRITERIA_CONFIG = [
    {
        'id': 1,
        'key': 'rsm_do_street',
        'name': '100% Target vs Achievement of Do Team bottom-line Net Value (Street)',
        'short_name': 'DO Team (Street)',
        'channel': 'FMCG CONDOM STREET',
        'prd_prefix': ['DO', 'SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 20000,
        'req_name': 'DO Team (Street) Incentive',
        'remark_name': 'DO Team Bottom-line'
    },
    {
        'id': 2,
        'key': 'rsm_touch_street',
        'name': '100% Target vs Achievement of Touch Team bottom-line Net Value (Street)',
        'short_name': 'TOUCH Team (Street)',
        'channel': 'FMCG CONDOM STREET',
        'prd_prefix': ['TOUCH', 'ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 20000,
        'req_name': 'TOUCH Team (Street) Incentive',
        'remark_name': 'TOUCH Team Bottom-line'
    },
    {
        'id': 3,
        'key': 'rsm_trade',
        'name': '100% Target vs Achievement of Trade Bottom-line Value',
        'short_name': 'Trade Bottom-Line',
        'channel': 'FMCG TRADE',
        'prd_prefix': ['DO', 'SATHI', 'TOUCH', 'ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 20000,
        'req_name': 'Trade Bottom-Line Incentive',
        'remark_name': 'TRADE Bottom-line'
    },
    {
        'id': 4,
        'key': 'rsm_ws_sathi',
        'name': 'Target vs Achievement of Wholesale - Sathi 4s Bottom-line Value',
        'short_name': 'WS Sathi 4s Bottom-Line',
        'channel': 'FMCG WHOLESALE',
        'prd_prefix': ['SATHI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 20000,
        'req_name': 'WS Sathi 4s Incentive',
        'remark_name': 'WS SATHI 4s Bottom-line'
    },
    {
        'id': 5,
        'key': 'rsm_ws_touch',
        'name': 'Target vs Achievement of Wholesale - TOUCH Bottom-line Value',
        'short_name': 'WS TOUCH Bottom-Line',
        'channel': 'FMCG WHOLESALE',
        'prd_prefix': ['TOUCH'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 20000,
        'req_name': 'WS TOUCH Incentive',
        'remark_name': 'WS TOUCH Bottom-line'
    },
    {
        'id': 6,
        'key': 'rsm_condom_bottom_line',
        'name': '100% of Target vs Achievement of Bottom-line Value (Street + Trade + Wholesale)',
        'short_name': 'Condom Bottom-Line',
        'channel': 'ALL_CONDOM',
        'prd_prefix': ['DO', 'SATHI', 'TOUCH', 'ONE'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 50000,
        'req_name': 'Condom Bottom-Line Incentive',
        'remark_name': 'RSM CONDOM Bottom-line'
    }
]

RSM_BLISS_CRITERIA_CONFIG = [
    {
        'id': 7,
        'key': 'rsm_bliss_bottom_line',
        'name': 'Target vs Achievement of Bottom-Line Net Value',
        'short_name': 'BLISS Bottom-Line',
        'channel': 'FMCG BLISS',
        'prd_prefix': ['BLISS', 'MAXI'],
        'metric': 'NET_WO_REG_DISC_VALUE',
        'target_type': 'net',
        'is_currency': True,
        'slab_100': 40000,
        'slab_120': 50000,
        'req_name': 'BLISS Bottom-Line Incentive',
        'remark_name': 'RSM BLISS Bottom-line'
    }
]
