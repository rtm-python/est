# -*- coding: utf-8 -*-

"""
Plugin module to handle examination process.
"""

# Standard libraries import


# Application modules import


# Additional libraries import


# Plugin configuration data
data = {
	'default_language': 'en',
	'name': {
		'en': 'Arithmetic',
		'ru': 'Арифметика'
	},
	'description': {
		'en': 'Arithmetic is a branch of mathematics that consists of the study of numbers, especially the properties of the traditional operations on them—addition, subtraction, multiplication, division, exponentiation and extraction of roots.',
		'ru': 'В арифметике рассматриваются измерения, вычислительные операции (сложение, вычитание, умножение, деление) и приёмы вычислений. Изучением свойств отдельных целых чисел занимается высшая арифметика, или теория чисел.'
	},
	'options': {
		'operations': {
			'name': {
				'en': 'Operations on numbers',
				'ru': 'Операции надо числами'
			},
			'multiselect': {
				'add': {
					'name': {
						'en': 'Addition',
						'ru': 'Сложение'
					}
				},
				'subs': {
					'name': {
						'en': 'Substraction',
						'ru': 'Вычитание'
					}
				},
				'mult': {
					'name': {
						'en': 'Multiplication',
						'ru': 'Умножение'
					}
				},
				'div': {
					'name': {
						'en': 'Division',
						'ru': 'Деление'
					}
				}
			}
		},
		'variables': {
			'name': {
				'en': 'Number of variables',
				'ru': 'Количество переменных'
			},
			'range': {
				'min': 2,
				'max': 4
			}
		},
		'result_only': {
			'name': {
				'en': 'Only result is unknown',
				'ru': 'Неизвестным является только результат'
			},
			'value': {
				'type': 'bool'
			}
		}
	}
}
