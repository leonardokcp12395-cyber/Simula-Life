# entities/archetypes.py

"""
This file defines the 'DNA' for all creature archetypes in the simulation.
"""

CREATURE_ARCHETYPES = {
    'herbivore_generic': {
        'name': 'Herbivore',
        'diet': {'plants': True, 'meat': False},
        'prey_archetypes': [],
        'predator_archetypes': ['carnivore_generic', 'feline', 'human'],
        'sprite_key': 'herbivore_base',
        'nest_sprite_key': 'herbivore_nest',
        'base_attributes': {
            'max_speed': 2.5, 'vision_radius': 200, 'max_energy': 1200,
            'energy_per_plant': 250, 'reproduction_urge_threshold': 800, 'lifespan': 15000,
        },
        'behaviors': {'social_group': 'herd'} # This creature will use Boids logic
    },
    'carnivore_generic': {
        'name': 'Carnivore',
        'diet': {'plants': False, 'meat': True},
        'prey_archetypes': ['herbivore_generic', 'human', 'feline'],
        'predator_archetypes': [],
        'sprite_key': 'carnivore_base',
        'nest_sprite_key': 'carnivore_nest',
        'base_attributes': {
            'max_speed': 3.0, 'vision_radius': 250, 'max_energy': 1500,
            'energy_per_kill': 500, 'reproduction_urge_threshold': 900, 'lifespan': 20000,
        },
        'behaviors': {'social_group': 'pack'}
    },
    'human': {
        'name': 'Human',
        'diet': {'plants': True, 'meat': True},
        'prey_archetypes': ['herbivore_generic', 'feline'],
        'predator_archetypes': ['carnivore_generic'],
        'sprite_key': 'human_base',
        'nest_sprite_key': 'human_nest',
        'base_attributes': {
            'max_speed': 2.8, 'vision_radius': 220, 'max_energy': 1300,
            'energy_per_plant': 150, 'energy_per_kill': 400,
            'reproduction_urge_threshold': 700, 'lifespan': 30000,
        },
        'behaviors': {'social_group': 'tribe'}
    },
    'feline': {
        'name': 'Feline',
        'diet': {'plants': False, 'meat': True},
        'prey_archetypes': ['herbivore_generic'],
        'predator_archetypes': ['carnivore_generic'],
        'sprite_key': 'feline_base',
        'nest_sprite_key': 'carnivore_nest',
        'base_attributes': {
            'max_speed': 3.5, 'vision_radius': 280, 'max_energy': 1000,
            'energy_per_kill': 450, 'reproduction_urge_threshold': 850, 'lifespan': 18000,
        },
        'behaviors': {'social_group': 'pack'}
    }
}
