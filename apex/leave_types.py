leave_types = {
    'fr': [
        {
            'name': 'P',
            'desc': 'Jours de présence',
            'type': 'presence',
            'color': 'green',
            'visible': False,
            'position': 0,
        },
        {
            'name': 'CN',
            'desc': 'Congés annuels',
            'type': 'normal_leave',
            'color': 'red',
            'visible': True,
            'position': 1,
        },
        {
            'name': 'JC',
            'desc': 'Jours de crédits',
            'type': 'credit_day',
            'color': 'indigo',
            'visible': True,
            'position': 2,
        },
        {
            'name': 'CV',
            'desc': 'Jours compensatoires',
            'type': 'variable_leave',
            'color': 'yellow',
            'visible': True,
            'position': 3,
        },
        {
            'name': 'CH',
            'desc': 'Congé hebdomadaires',
            'type': 'saturday',
            'color': 'blue',
            'visible': True,
            'position': 4,
        },
        {
            'name': 'RH',
            'desc': 'Repos hebdomadaires',
            'type': 'sunday',
            'color': 'pink',
            'visible': True,
            'position': 5,
        },
        {
            'name': 'RR',
            'desc': 'Jours fériés',
            'type': 'holiday',
            'color': 'orange',
            'visible': True,
            'position': 6,
        },
        {
            'name': 'HS',
            'desc': 'Heures supplémentaire',
            'type': 'hour',
            'color': 'green',
            'visible': True,
            'position': 7,
        },
        {
            'name': 'MM',
            'desc': 'Jours de maladies',
            'type': 'counter_sick',
            'color': 'purple',
            'visible': False,
            'position': 8,
        },
        {
            'name': 'CC',
            'desc': 'Congés de circonstances',
            'type': 'counter_special',
            'color': 'purple',
            'visible': False,
            'position': 9,
        },
        {
            'name': 'AI',
            'desc': 'Absences injustifiées',
            'type': 'counter_unjustified',
            'color': 'purple',
            'visible': False,
            'position': 10,
        },
        {
            'name': 'AG',
            'desc': 'Agent en grève',
            'type': 'counter_strike',
            'color': 'purple',
            'visible': False,
            'position': 11,
        },
        {
            'name': 'BT',
            'desc': 'Blessé au travail',
            'type': 'counter_wounded',
            'color': 'purple',
            'visible': False,
            'position': 12,
        },
        {
            'name': 'OZ',
            'desc': 'Récupération',
            'type': 'recovery',
            'color': 'red',
            'visible': False,
            'position': 13,
        },
        {
            'name': 'AP',
            'desc': 'Temps partiel',
            'type': 'ignore',
            'color': 'red',
            'visible': False,
            'position': 14,
        },
    ]
}