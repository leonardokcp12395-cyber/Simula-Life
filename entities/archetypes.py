# entities/archetypes.py

"""
This file defines the 'DNA' for all creature archetypes in the simulation.
Each archetype is a dictionary containing all the base data needed to create a creature,
allowing for easy creation of new and diverse beings without changing the core code.
"""

CREATURE_ARCHETYPES = {
    'herbivore_generic': {
        'name': 'Herbivore',
        'diet': {'plants': True, 'meat': False},
        'prey_archetypes': [], # What it hunts
        'predator_archetypes': ['carnivore_generic'], # What it flees from
        'sprite_key': 'herbivore_base', # Key for asset generation
        'nest_sprite_key': 'herbivore_nest',
        'base_attributes': {
            'max_speed': 2.5,
            'vision_radius': 200,
            'max_energy': 1200,
            'energy_per_plant': 250,
            'reproduction_urge_threshold': 800,
            'lifespan': 15000,
        }
    },
    'carnivore_generic': {
        'name': 'Carnivore',
        'diet': {'plants': False, 'meat': True},
        'prey_archetypes': ['herbivore_generic'],
        'predator_archetypes': [],
        'sprite_key': 'carnivore_base',
        'nest_sprite_key': 'carnivore_nest',
        'base_attributes': {
            'max_speed': 3.0,
            'vision_radius': 250,
            'max_energy': 1500,
            'energy_per_kill': 500,
            'reproduction_urge_threshold': 900,
            'lifespan': 20000,
        }
    },
    'human': {
        'name': 'Human',
        'diet': {'plants': True, 'meat': True},
        'prey_archetypes': ['herbivore_generic'],
        'predator_archetypes': ['carnivore_generic'],
        'sprite_key': 'human_base',
        'nest_sprite_key': 'human_nest', # Placeholder, can be a campfire or simple hut
        'base_attributes': {
            'max_speed': 2.8,
            'vision_radius': 220,
            'max_energy': 1300,
            'energy_per_plant': 150,
            'energy_per_kill': 400,
            'reproduction_urge_threshold': 700,
            'lifespan': 30000,
        }
    },
    'feline': {
        'name': 'Feline',
        'diet': {'plants': False, 'meat': True},
        'prey_archetypes': ['herbivore_generic'],
        'predator_archetypes': ['carnivore_generic'], # Felines might be hunted by larger carnivores
        'sprite_key': 'feline_base',
        'nest_sprite_key': 'carnivore_nest', # Can reuse the carnivore den
        'base_attributes': {
            'max_speed': 3.5,
            'vision_radius': 280,
            'max_energy': 1000,
            'energy_per_kill': 450,
            'reproduction_urge_threshold': 850,
            'lifespan': 18000,
        }
    }
}
